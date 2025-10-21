"""MCP session manager."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Optional

from ..protocol.models import (
    Capability,
    Request,
    Response,
    ServerDiscovery,
    ToolDescription,
)
from ..transports.base import Transport, TransportError


def _to_capability(payload: dict) -> Capability:
    return Capability(
        name=str(payload.get("name", "")),
        version=str(payload.get("version", "")),
        description=payload.get("description"),
    )


def _to_tool(payload: dict) -> ToolDescription:
    return ToolDescription(
        name=str(payload.get("name", "")),
        description=str(payload.get("description", "")),
        input_schema=dict(payload.get("input_schema", {})),
    )


@dataclass
class Session:
    """High level session for interacting with an MCP server."""

    transport: Transport
    _next_id: int = 0
    _discovery: Optional[ServerDiscovery] = None
    _tools: Dict[str, ToolDescription] = None

    def __post_init__(self) -> None:
        self._tools = {}

    def _allocate_id(self) -> int:
        self._next_id += 1
        return self._next_id

    def initialize(self) -> ServerDiscovery:
        request_id = self._allocate_id()
        request = Request(id=request_id, method="initialize")
        self.transport.send_request(request)
        for response in self._drain():
            if response.id == request_id:
                response.raise_for_error()
                payload = response.result or {}
                discovery = ServerDiscovery(
                    name=str(payload.get("name", "")),
                    version=str(payload.get("version", "")),
                    capabilities=[_to_capability(item) for item in payload.get("capabilities", [])],
                    tools=[_to_tool(item) for item in payload.get("tools", [])],
                )
                self._tools = {tool.name: tool for tool in discovery.tools}
                self._discovery = discovery
                return discovery
        raise TransportError("Server did not respond to initialize request")

    def call_tool(self, name: str, arguments: dict | None = None) -> dict:
        if not self._discovery:
            raise TransportError("session is not initialized")
        if name not in self._tools:
            raise KeyError(name)
        arguments = arguments or {}
        request_id = self._allocate_id()
        request = Request(id=request_id, method="callTool", params={"name": name, "arguments": arguments})
        self.transport.send_request(request)
        for response in self._drain():
            if response.id == request_id:
                response.raise_for_error()
                return dict(response.result or {})
        raise TransportError("Server did not respond to callTool request")

    def _drain(self) -> Iterable[Response]:
        return self.transport.receive(timeout=1)

    def close(self) -> None:
        self.transport.close()


