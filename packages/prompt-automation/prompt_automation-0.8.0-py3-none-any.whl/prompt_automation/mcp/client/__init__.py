"""High-level utilities for interacting with MCP providers."""
from __future__ import annotations

from dataclasses import asdict
from contextlib import contextmanager
import logging
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, Mapping, MutableMapping, Tuple, cast, IO

from ...features import is_mcp_enabled, is_mcp_observability_enabled
from ..config.loader import ProviderConfig, RegistryConfig
from ..config import loader as _config_loader
from ..protocol.models import ServerDiscovery
from ..transports.base import TransportError
from ..transports.stdio import StdioTransport
from .session import Session

# Import validation for cross-platform safety
try:
    from ...platform_utils import validate_subprocess_stdio, detect_environment
    _HAS_VALIDATION = True
except ImportError:  # pragma: no cover
    _HAS_VALIDATION = False

_log = logging.getLogger(__name__)

PathType = Path | str

_REGISTRY_CACHE: Dict[Path, Tuple[float, RegistryConfig]] = {}
_CREDENTIALS_CACHE: Dict[Path, Tuple[float, Dict[str, Dict[str, str]]]] = {}
_DISCOVERY_CACHE: Dict[Tuple[str, Tuple[str, ...], Tuple[Tuple[str, str], ...]], ServerDiscovery] = {}


def _require_mcp_enabled() -> None:
    if not is_mcp_enabled():
        raise RuntimeError("MCP feature disabled")


def clear_caches() -> None:
    """Reset in-memory caches used for configuration and discovery."""

    _REGISTRY_CACHE.clear()
    _CREDENTIALS_CACHE.clear()
    _DISCOVERY_CACHE.clear()


def _coerce_path(path: PathType) -> Path:
    raw = Path(path)
    return raw.expanduser().resolve()


def _load_registry(path: Path) -> RegistryConfig:
    return _config_loader.load_registry(path)


def _load_credentials(path: Path) -> Dict[str, Dict[str, str]]:
    return _config_loader.load_credentials(path)


def load_registry_cached(path: PathType) -> RegistryConfig:
    """Load and cache the registry configuration from disk."""

    _require_mcp_enabled()
    resolved = _coerce_path(path)
    mtime = resolved.stat().st_mtime
    cached = _REGISTRY_CACHE.get(resolved)
    if cached and cached[0] == mtime:
        return cached[1]
    registry = _load_registry(resolved)
    _REGISTRY_CACHE[resolved] = (mtime, registry)
    return registry


def load_credentials_cached(path: PathType) -> Dict[str, Dict[str, str]]:
    """Load and cache provider credentials from disk."""

    _require_mcp_enabled()
    resolved = _coerce_path(path)
    mtime = resolved.stat().st_mtime
    cached = _CREDENTIALS_CACHE.get(resolved)
    if cached and cached[0] == mtime:
        return cached[1]
    data = _load_credentials(resolved)
    _CREDENTIALS_CACHE[resolved] = (mtime, data)
    return data


def _find_provider(registry: RegistryConfig, identifier: str) -> ProviderConfig:
    for provider in registry.providers:
        if provider.identifier == identifier:
            return provider
    raise KeyError(identifier)


def _ensure_consent(provider: ProviderConfig, accepted: Iterable[str] | None) -> None:
    accepted_set = set(accepted or ())
    if provider.needs_consent(accepted_set):
        raise PermissionError(f"consent required for provider '{provider.identifier}'")


def _load_provider_credentials(
    identifier: str, credentials_path: PathType | None
) -> Dict[str, str]:
    if not credentials_path:
        return {}
    data = load_credentials_cached(credentials_path)
    raw = data.get(identifier) or {}
    if not isinstance(raw, Mapping):
        raise ValueError(f"credentials for provider '{identifier}' must be a mapping")
    return {str(key): str(value) for key, value in raw.items()}


def _merge_env(
    provider: ProviderConfig,
    base_env: Mapping[str, str] | None,
    credentials: Mapping[str, str],
) -> Dict[str, str]:
    merged: Dict[str, str] = {}
    if base_env:
        merged.update({str(key): str(value) for key, value in base_env.items()})
    merged.setdefault("MCP_PROVIDER_ID", provider.identifier)
    for key, value in credentials.items():
        merged[f"MCP_CREDENTIAL_{key.upper()}"] = value
    if "PROMPT_AUTOMATION_MCP_OBSERVABILITY" not in merged:
        merged["PROMPT_AUTOMATION_MCP_OBSERVABILITY"] = (
            "1" if is_mcp_observability_enabled() else "0"
        )
    return merged


def _discovery_cache_key(
    provider: ProviderConfig, credentials: Mapping[str, str]
) -> Tuple[str, Tuple[str, ...], Tuple[Tuple[str, str], ...]]:
    return (
        provider.identifier,
        tuple(provider.command),
        tuple(sorted((str(key), str(value)) for key, value in credentials.items())),
    )


@contextmanager
def _open_session(
    provider: ProviderConfig, env_overrides: Mapping[str, str] | None = None
) -> Iterator[Session]:
    """Open an MCP session with stdio transport.
    
    Validates subprocess stdio before opening on WSL2→Windows to prevent hangs.
    
    Args:
        provider: MCP provider configuration
        env_overrides: Environment variables to merge
        
    Yields:
        Active MCP session
        
    Raises:
        TransportError: If stdio validation fails or pipes are unavailable
    """
    # Validate subprocess stdio on cross-platform boundaries (WSL2→Windows)
    if _HAS_VALIDATION:
        result = validate_subprocess_stdio(provider.command)  # type: ignore
        if not result.success:
            env = detect_environment()  # type: ignore
            error_msg = (
                f"MCP stdio validation failed: {result.error}\n"
                f"Current environment: {env}\n"
                f"Command: {provider.command}\n"
                f"Suggestion: {result.message}\n"
                f"Hint: Use HTTP transport instead of stdio for cross-VM operations"
            )
            _log.error(error_msg)
            raise TransportError(error_msg)
    
    env = os.environ.copy()
    if env_overrides:
        env.update({str(key): str(value) for key, value in env_overrides.items()})
    proc = subprocess.Popen(  # noqa: S603 - command comes from trusted config
        provider.command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=None,
        text=True,
        bufsize=1,
        env=env,
    )
    if proc.stdin is None or proc.stdout is None:
        proc.terminate()
        raise TransportError("provider is missing stdio pipes")
    
    # Cast to satisfy type checker (subprocess.PIPE guarantees TextIO in text mode)
    transport = StdioTransport(
        cast(Any, proc.stdout),  # type: ignore - Popen text=True returns TextIO
        cast(Any, proc.stdin)    # type: ignore - Popen text=True returns TextIO
    )
    session = Session(transport)
    try:
        yield session
    finally:
        try:
            session.close()
        finally:
            for stream in (proc.stdin, proc.stdout):
                if stream:
                    try:
                        stream.close()
                    except Exception:  # pragma: no cover - defensive cleanup
                        pass
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=2)
                except subprocess.TimeoutExpired:  # pragma: no cover - defensive
                    proc.kill()
                    proc.kill()


def discover_provider(
    provider_id: str,
    *,
    registry_path: PathType,
    credentials_path: PathType | None = None,
    accepted: Iterable[str] | None = None,
    refresh: bool = False,
    env: Mapping[str, str] | None = None,
) -> ServerDiscovery:
    """Initialize a provider and return its discovery payload."""

    _require_mcp_enabled()
    registry = load_registry_cached(registry_path)
    provider = _find_provider(registry, provider_id)
    _ensure_consent(provider, accepted)
    credentials = _load_provider_credentials(provider.identifier, credentials_path)
    cache_key = _discovery_cache_key(provider, credentials)
    if not refresh and cache_key in _DISCOVERY_CACHE:
        return _DISCOVERY_CACHE[cache_key]
    env_overrides = _merge_env(provider, env, credentials)
    with _open_session(provider, env_overrides=env_overrides) as session:
        discovery = session.initialize()
    _DISCOVERY_CACHE[cache_key] = discovery
    return discovery


def call_tool(
    provider_id: str,
    tool_name: str,
    arguments: MutableMapping[str, Any] | None,
    *,
    registry_path: PathType,
    credentials_path: PathType | None = None,
    accepted: Iterable[str] | None = None,
    env: Mapping[str, str] | None = None,
) -> Dict[str, Any]:
    """Invoke a tool exposed by an MCP provider."""

    _require_mcp_enabled()
    registry = load_registry_cached(registry_path)
    provider = _find_provider(registry, provider_id)
    _ensure_consent(provider, accepted)
    credentials = _load_provider_credentials(provider.identifier, credentials_path)
    env_overrides = _merge_env(provider, env, credentials)
    with _open_session(provider, env_overrides=env_overrides) as session:
        discovery = session.initialize()
        _DISCOVERY_CACHE[_discovery_cache_key(provider, credentials)] = discovery
        payload = session.call_tool(tool_name, dict(arguments or {}))
    return payload


def provider_to_dict(provider: ProviderConfig) -> Dict[str, Any]:
    """Serialize a provider configuration into a JSON-friendly mapping."""

    return {
        "id": provider.identifier,
        "transport": provider.transport,
        "command": list(provider.command),
        "consent_required": provider.consent_required,
        "metadata": dict(provider.metadata),
    }


def discovery_to_dict(discovery: ServerDiscovery) -> Dict[str, Any]:
    """Serialize discovery metadata into primitives suitable for JSON."""

    return asdict(discovery)


__all__ = [
    "clear_caches",
    "load_registry_cached",
    "load_credentials_cached",
    "discover_provider",
    "call_tool",
    "provider_to_dict",
    "discovery_to_dict",
]
