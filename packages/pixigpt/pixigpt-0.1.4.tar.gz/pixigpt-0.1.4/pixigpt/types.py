"""Type definitions for PixiGPT API."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class ToolCallFunction:
    """Function details within a tool call."""
    name: str
    arguments: str  # JSON string


@dataclass
class ToolCall:
    """Tool call made by the assistant."""
    id: str
    type: str
    function: ToolCallFunction


@dataclass
class Message:
    """Chat message."""
    role: str
    content: str
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None  # For role="tool" messages


@dataclass
class ChatCompletionRequest:
    """Request for chat completion.

    assistant_id is optional - if omitted, messages[0] must be a system message.
    tools can be provided to override assistant's configured tools.
    """
    messages: List[Message]
    assistant_id: Optional[str] = None
    temperature: float = 0.0  # Server defaults to 0.6 if 0
    max_tokens: int = 0       # Server omits if 0 (vLLM default)
    enable_thinking: Optional[bool] = None
    tools: Optional[List[Dict[str, Any]]] = None  # OpenAI-format tool definitions


@dataclass
class Usage:
    """Token usage statistics."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass
class ChatCompletionChoice:
    """Chat completion choice."""
    index: int
    message: Message
    finish_reason: str
    reasoning_content: Optional[str] = None  # Chain of thought reasoning


@dataclass
class ChatCompletionResponse:
    """Response from chat completion."""
    id: str
    object: str
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: Usage


@dataclass
class Thread:
    """Conversation thread."""
    id: str
    object: str
    created_at: int
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass
class MessageContent:
    """Message content block."""
    type: str
    text: Dict[str, Any]


@dataclass
class ThreadMessage:
    """Message in a thread."""
    id: str
    object: str
    created_at: int
    thread_id: str
    role: str
    content: List[MessageContent]
    reasoning_content: Optional[str] = None  # Chain of thought reasoning


@dataclass
class Run:
    """Async run."""
    id: str
    object: str
    created_at: int
    thread_id: str
    assistant_id: str
    status: str  # queued, in_progress, completed, failed
    model: str
    message: Optional[ThreadMessage] = None  # Populated when completed


@dataclass
class Assistant:
    """AI assistant."""
    id: str
    object: str
    created_at: int
    name: str
    instructions: str
    tools_config: Optional[str] = None
