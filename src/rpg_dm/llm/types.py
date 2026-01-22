"""Type definitions for LLM interactions."""

from enum import Enum
from typing import Any, Optional, Union

from pydantic import BaseModel, Field


class ChatRole(str, Enum):
    """Chat message roles."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class ChatMessage(BaseModel):
    """A chat message in the conversation."""

    role: ChatRole
    content: Optional[str] = None
    name: Optional[str] = None
    tool_call_id: Optional[str] = None
    tool_calls: Optional[list[dict[str, Any]]] = None


class Tool(BaseModel):
    """A tool that can be called by the LLM."""

    type: str = "function"
    function: dict[str, Any]


class FunctionCall(BaseModel):
    """A function call within a tool call."""

    name: str
    arguments: dict[str, Any]


class ToolCall(BaseModel):
    """A tool call made by the LLM."""

    id: str
    type: str
    function: FunctionCall


class LLMResponse(BaseModel):
    """Response from the LLM."""

    content: Optional[str] = None
    tool_calls: Optional[list[ToolCall]] = None
    finish_reason: Optional[str] = None
    usage: dict[str, int] = Field(default_factory=dict)


class StreamChunk(BaseModel):
    """A chunk from a streaming LLM response."""

    content: Optional[str] = None
    tool_calls: Optional[list[ToolCall]] = None
    finish_reason: Optional[str] = None
