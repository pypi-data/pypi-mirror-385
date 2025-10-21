"""StdIO transport for MCP clients."""
from __future__ import annotations

import json
import queue
import threading
from dataclasses import asdict
from typing import Iterable, Optional, TextIO

from .base import Transport, TransportError
from ..protocol.models import Notification, Request, Response


class StdioTransport(Transport):
    """Transport that communicates using JSON lines over stdio."""

    def __init__(self, reader: TextIO, writer: TextIO) -> None:
        self._reader = reader
        self._writer = writer
        self._responses: "queue.Queue[Response]" = queue.Queue()
        self._closed = threading.Event()
        self._thread = threading.Thread(target=self._pump, name="mcp-stdio-reader", daemon=True)
        self._thread.start()

    def _pump(self) -> None:
        while not self._closed.is_set():
            line = self._reader.readline()
            if not line:
                break
            try:
                payload = json.loads(line)
                response = Response(**payload)
            except Exception as exc:  # pragma: no cover - defensive
                raise TransportError(f"Failed to decode response: {exc}") from exc
            self._responses.put(response)

    def send_request(self, request: Request) -> None:
        self._send(asdict(request))

    def send_notification(self, notification: Notification) -> None:
        self._send(asdict(notification))

    def _send(self, payload: dict) -> None:
        if self._closed.is_set():
            raise TransportError("transport is closed")
        data = json.dumps(payload, separators=(",", ":")) + "\n"
        self._writer.write(data)
        self._writer.flush()

    def receive(self, timeout: Optional[float] = None) -> Iterable[Response]:
        items: list[Response] = []
        try:
            response = self._responses.get(timeout=timeout)
        except queue.Empty:
            return items
        items.append(response)
        while True:
            try:
                items.append(self._responses.get_nowait())
            except queue.Empty:
                break
        return items

    def close(self) -> None:
        self._closed.set()
        close = getattr(self._reader, "close", None)
        if callable(close):  # pragma: no cover - depends on IO type
            try:
                close()
            except Exception:  # pragma: no cover - defensive
                pass
        self._thread.join(timeout=1)


