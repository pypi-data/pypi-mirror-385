"""Configuration helpers for MCP integrations."""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List

logger = logging.getLogger(__name__)

MAX_PROVIDERS = 16
MAX_COMMAND_LENGTH = 8


@dataclass(slots=True)
class ProviderConfig:
    identifier: str
    transport: str
    command: List[str]
    consent_required: bool = False
    metadata: Dict[str, str] = field(default_factory=dict)

    def needs_consent(self, accepted: Iterable[str]) -> bool:
        accepted_set = set(accepted)
        return self.consent_required and self.identifier not in accepted_set


@dataclass(slots=True)
class RegistryConfig:
    providers: List[ProviderConfig]


def _redact(value: str) -> str:
    if not value:
        return value
    if len(value) <= 4:
        return "***"
    return value[:2] + "***" + value[-2:]


def _redact_mapping(mapping: Dict[str, str]) -> Dict[str, str]:
    return {key: _redact(value) for key, value in mapping.items()}


def load_registry(path: Path) -> RegistryConfig:
    data = json.loads(path.read_text("utf-8"))
    providers = data.get("providers", [])
    if not isinstance(providers, list):
        raise ValueError("registry providers must be a list")
    if len(providers) > MAX_PROVIDERS:
        raise ValueError("registry exceeds provider limit")

    parsed: List[ProviderConfig] = []
    for item in providers:
        identifier = str(item.get("id", "")).strip()
        if not identifier:
            raise ValueError("provider missing id")
        command = item.get("command", [])
        if not isinstance(command, list) or not command:
            raise ValueError(f"provider {identifier} has invalid command")
        if len(command) > MAX_COMMAND_LENGTH:
            raise ValueError(f"provider {identifier} command exceeds limit")
        consent = bool(item.get("consent_required", False))
        transport = str(item.get("transport", "stdio"))
        metadata = {str(k): str(v) for k, v in (item.get("metadata") or {}).items()}
        parsed.append(
            ProviderConfig(
                identifier=identifier,
                transport=transport,
                command=[str(part) for part in command],
                consent_required=consent,
                metadata=metadata,
            )
        )
        logger.debug("Registered MCP provider %s", identifier)
    return RegistryConfig(providers=parsed)


def load_credentials(path: Path) -> Dict[str, Dict[str, str]]:
    data = json.loads(path.read_text("utf-8"))
    sanitized = {name: _redact_mapping(values) for name, values in data.items()}
    logger.debug("Loaded MCP credentials: %s", sanitized)
    return data


