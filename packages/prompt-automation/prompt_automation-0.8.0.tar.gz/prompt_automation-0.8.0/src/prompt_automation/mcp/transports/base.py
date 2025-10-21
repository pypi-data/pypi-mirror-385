"""Transport abstractions for MCP clients."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Optional

from ..protocol.models import Notification, Request, Response


class TransportError(RuntimeError):
    """Raised when the transport encounters a fatal error."""


class Transport(ABC):
    """Abstract transport used by the MCP client."""

    @abstractmethod
    def send_request(self, request: Request) -> None:  # pragma: no cover - interface only
        raise NotImplementedError

    @abstractmethod
    def send_notification(self, notification: Notification) -> None:  # pragma: no cover
        raise NotImplementedError

    @abstractmethod
    def receive(self, timeout: Optional[float] = None) -> Iterable[Response]:  # pragma: no cover
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:  # pragma: no cover
        raise NotImplementedError


