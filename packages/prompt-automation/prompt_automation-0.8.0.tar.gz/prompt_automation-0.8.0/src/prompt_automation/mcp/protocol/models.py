"""Typed models for MCP JSON-RPC interactions."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Generic, List, Literal, Optional, TypeVar, Union

JsonValue = Union[None, bool, int, float, str, List["JsonValue"], Dict[str, "JsonValue"]]

TParams = TypeVar("TParams", bound=Optional[JsonValue])
TResult = TypeVar("TResult", bound=Optional[JsonValue])


@dataclass(slots=True)
class Request(Generic[TParams]):
    """Represents a JSON-RPC request."""

    id: Union[int, str]
    method: str
    params: TParams = None
    jsonrpc: Literal["2.0"] = "2.0"


@dataclass(slots=True)
class Notification(Generic[TParams]):
    """Represents a JSON-RPC notification."""

    method: str
    params: TParams = None
    jsonrpc: Literal["2.0"] = "2.0"


@dataclass(slots=True)
class ErrorData:
    """Represents an error object according to JSON-RPC."""

    code: int
    message: str
    data: Optional[JsonValue] = None


@dataclass(slots=True)
class Response(Generic[TResult]):
    """Represents a JSON-RPC response."""

    id: Union[int, str, None]
    result: Optional[TResult] = None
    error: Optional[ErrorData] = None
    jsonrpc: Literal["2.0"] = "2.0"

    def raise_for_error(self) -> None:
        if self.error is not None:
            raise RuntimeError(f"RPC error {self.error.code}: {self.error.message}")


@dataclass(slots=True)
class Capability:
    name: str
    version: str
    description: Optional[str] = None


@dataclass(slots=True)
class ToolDescription:
    name: str
    description: str
    input_schema: Dict[str, JsonValue] = field(default_factory=dict)


@dataclass(slots=True)
class ServerDiscovery:
    name: str
    version: str
    capabilities: List[Capability] = field(default_factory=list)
    tools: List[ToolDescription] = field(default_factory=list)


