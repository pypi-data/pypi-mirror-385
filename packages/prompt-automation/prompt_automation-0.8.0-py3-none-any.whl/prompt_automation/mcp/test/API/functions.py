"""Hard-coded testing APIs used for MCP smoke tests."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List


def echo(payload: Dict[str, str]) -> Dict[str, str]:
    """Return the payload unchanged."""

    return dict(payload)


def time(_: Dict[str, str] | None = None) -> Dict[str, str]:
    """Return the current UTC timestamp."""

    return {"timestamp": datetime.now(timezone.utc).isoformat()}


def add(numbers: Dict[str, List[int]]) -> Dict[str, int]:
    """Return the sum of an integer list."""

    total = sum(int(value) for value in numbers.get("values", []))
    return {"sum": total}


__all__ = ["echo", "time", "add"]


