"""Simple observability toggles for MCP integrations."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

from ...features import is_mcp_observability_enabled


@dataclass(slots=True)
class ObservabilityState:
    metrics_enabled: bool = False
    tracing_enabled: bool = False
    logger: Optional[Callable[[str], None]] = None
    metrics_hook: Optional[Callable[[str, Dict[str, Any]], None]] = None

    def log(self, message: str) -> None:
        if self.logger:
            self.logger(message)

    def emit_metric(self, name: str, payload: Dict[str, Any]) -> None:
        if not self.metrics_enabled:
            return
        if self.metrics_hook is None:
            return
        self.metrics_hook(name, payload)


def _default_logger(message: str) -> None:  # pragma: no cover - fallback logging only
    print(message)


def _initial_enabled() -> bool:
    try:
        return is_mcp_observability_enabled()
    except Exception:  # pragma: no cover - defensive
        return False


_DEFAULT_OBSERVABILITY = _initial_enabled()

global_state = ObservabilityState(
    metrics_enabled=_DEFAULT_OBSERVABILITY,
    tracing_enabled=_DEFAULT_OBSERVABILITY,
    logger=_default_logger,
)


def configure(
    metrics: Optional[bool] = None,
    tracing: Optional[bool] = None,
    logger: Optional[Callable[[str], None]] = None,
    metrics_hook: Optional[Callable[[str, Dict[str, Any]], None]] = None,
) -> None:
    """Update the observability state atomically."""

    if metrics is not None:
        global_state.metrics_enabled = metrics
    if tracing is not None:
        global_state.tracing_enabled = tracing
    if logger is not None:
        global_state.logger = logger
    if metrics_hook is not None:
        global_state.metrics_hook = metrics_hook


class ObservabilityToggle:
    """Context manager used to temporarily override observability."""

    def __init__(self, metrics: Optional[bool] = None, tracing: Optional[bool] = None) -> None:
        self.metrics = metrics
        self.tracing = tracing
        self._previous = ObservabilityState(
            metrics_enabled=global_state.metrics_enabled,
            tracing_enabled=global_state.tracing_enabled,
            logger=global_state.logger,
            metrics_hook=global_state.metrics_hook,
        )

    def __enter__(self) -> ObservabilityState:
        configure(metrics=self.metrics, tracing=self.tracing)
        return global_state

    def __exit__(self, exc_type, exc, tb) -> None:
        configure(
            metrics=self._previous.metrics_enabled,
            tracing=self._previous.tracing_enabled,
            logger=self._previous.logger,
            metrics_hook=self._previous.metrics_hook,
        )


def sync_with_features() -> ObservabilityState:
    """Refresh the global observability state from feature resolution."""

    enabled = is_mcp_observability_enabled()
    configure(metrics=enabled, tracing=enabled)
    return global_state


def record_project_call_metric(
    event: str,
    *,
    duration_ms: float,
    attempt_index: int,
    attempt_count: int,
    next_delay_ms: float | None = None,
) -> None:
    """Emit lightweight metrics describing MCP project call attempts."""

    payload: Dict[str, Any] = {
        "duration_ms": float(duration_ms),
        "attempt_index": int(attempt_index),
        "attempt_count": int(attempt_count),
    }
    if next_delay_ms is not None:
        payload["next_delay_ms"] = float(next_delay_ms)
    global_state.emit_metric(event, payload)


sync_with_features()


__all__ = [
    "ObservabilityState",
    "ObservabilityToggle",
    "configure",
    "global_state",
    "record_project_call_metric",
    "sync_with_features",
]


