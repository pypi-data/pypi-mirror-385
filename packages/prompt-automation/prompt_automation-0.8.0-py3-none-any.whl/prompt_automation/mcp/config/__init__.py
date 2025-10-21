"""Public configuration helpers for MCP integrations."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .loader import (  # re-exported for convenience
    MAX_COMMAND_LENGTH,
    MAX_PROVIDERS,
    ProviderConfig,
    RegistryConfig,
    load_credentials,
    load_registry,
)


@dataclass(slots=True)
class RetryPolicy:
    """Retry/backoff policy applied to MCP endpoint invocations."""

    base_delay: float = 0.25
    """Base delay in seconds applied after the first failure."""

    max_delay: float = 0.5
    """Maximum delay in seconds between attempts (clamps exponential growth)."""

    jitter: float = 0.0
    """Fractional jitter (0-1) applied symmetrically to computed delays."""

    max_attempts: int | None = None
    """Optional cap on the total number of attempts across all endpoints."""

    max_duration: float | None = None
    """Optional wall-clock budget in seconds for the aggregate retry loop."""

    def delay_for_attempt(self, attempt: int, *, jitter_fn: Callable[[float, float], float] | None = None) -> float:
        """Return the sleep duration for the given ``attempt`` index."""

        if attempt <= 0:
            return 0.0
        delay = max(0.0, self.base_delay * attempt)
        if self.max_delay > 0:
            delay = min(delay, self.max_delay)
        if self.jitter > 0 and delay > 0:
            apply = jitter_fn or (lambda low, high: low)
            jitter_span = delay * self.jitter
            low = max(0.0, delay - jitter_span)
            high = delay + jitter_span
            delay = apply(low, high)
        return delay


__all__ = [
    "RetryPolicy",
    "MAX_PROVIDERS",
    "MAX_COMMAND_LENGTH",
    "ProviderConfig",
    "RegistryConfig",
    "load_registry",
    "load_credentials",
]
