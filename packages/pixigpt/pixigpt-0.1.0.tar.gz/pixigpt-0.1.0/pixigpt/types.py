"""Type definitions for PixiGPT API."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class Message:
    """Chat message."""
    role: str
    content: str


@dataclass
class ChatCompletionRequest:
    """Request for chat completion."""
    assistant_id: str
    messages: List[Message]
    temperature: float = 0.7
    max_tokens: int = 2000
    enable_thinking: Optional[bool] = None


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


@dataclass
class Assistant:
    """AI assistant."""
    id: str
    object: str
    created_at: int
    name: str
    instructions: str
    tools_config: Optional[str] = None
