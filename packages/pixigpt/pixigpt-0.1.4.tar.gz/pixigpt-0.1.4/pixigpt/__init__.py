"""PixiGPT Python Client - Production-grade API client."""

from .client import Client
from .types import (
    Message,
    ChatCompletionRequest,
    ChatCompletionResponse,
    Thread,
    ThreadMessage,
    Run,
    Assistant,
)
from .errors import APIError, is_auth_error, is_rate_limit_error

__version__ = "0.1.0"
__all__ = [
    "Client",
    "Message",
    "ChatCompletionRequest",
    "ChatCompletionResponse",
    "Thread",
    "ThreadMessage",
    "Run",
    "Assistant",
    "APIError",
    "is_auth_error",
    "is_rate_limit_error",
]
