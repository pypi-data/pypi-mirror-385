"""Helpers for launching prompt-automation across install variants."""

from .windows import (
    iter_windows_launch_commands,
    maybe_handoff_to_preferred_installation,
    resolve_windows_launcher,
)

__all__ = [
    "iter_windows_launch_commands",
    "maybe_handoff_to_preferred_installation",
    "resolve_windows_launcher",
]
