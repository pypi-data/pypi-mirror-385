# PixiGPT Python Client

Production-grade Python client for the [PixiGPT API](https://pixigpt.com).

## Features

- 🚀 **High Performance**: Connection pooling with 100 connections
- 🔄 **Smart Retries**: Exponential backoff (0.1s → 0.8s)
- ⏱️ **Timeouts**: 30s default, fully configurable
- 🎯 **Type Hints**: Full typing support for modern Python
- 📦 **Minimal Dependencies**: Just `requests` + `urllib3`
- 🔧 **OpenAI Compatible**: Familiar API surface
- 🧠 **Chain of Thought**: Server-extracted CoT reasoning in `reasoning_content`
- 🛠️ **Tool Calling**: Full OpenAI-compatible function calling support

## Installation

```bash
pip install pixigpt
```

## Quick Start

```python
from pixigpt import Client, ChatCompletionRequest, Message

client = Client("sk-proj-YOUR_API_KEY", "https://pixigpt.com/v1")

# Option 1: With assistant personality
response = client.create_chat_completion(
    ChatCompletionRequest(
        assistant_id="your-assistant-id",  # Optional
        messages=[Message(role="user", content="Hello!")],
    )
)

# Option 2: Pure OpenAI mode (no assistant)
response = client.create_chat_completion(
    ChatCompletionRequest(
        messages=[
            Message(role="system", content="You are helpful"),
            Message(role="user", content="Hello!"),
        ],
    )
)

print(response.choices[0].message.content)

# Access chain of thought reasoning (if enable_thinking=true)
if response.choices[0].reasoning_content:
    print(f"Reasoning: {response.choices[0].reasoning_content}")
```

## Configuration

```python
from pixigpt import Client

# Custom timeout and retries
client = Client(
    api_key="sk-proj-...",
    base_url="https://pixigpt.com/v1",
    timeout=60,        # 60 second timeout
    max_retries=5,     # Retry up to 5 times
)

# Custom session
import requests
session = requests.Session()
session.proxies = {"http": "http://proxy:8080"}

client = Client(
    api_key="sk-proj-...",
    base_url="https://pixigpt.com/v1",
    session=session,
)
```

## API Methods

### Chat Completions (Stateless)

```python
from pixigpt import ChatCompletionRequest, Message

# Basic completion
response = client.create_chat_completion(
    ChatCompletionRequest(
        assistant_id=assistant_id,  # Optional - omit for pure OpenAI mode
        messages=[
            Message(role="user", content="What's the weather?"),
        ],
        temperature=0.7,
        max_tokens=2000,
        enable_thinking=True,  # Enable chain of thought (default: True)
    )
)

# Access response
print(response.choices[0].message.content)
print(f"Tokens: {response.usage.total_tokens}")

# Access reasoning (server-provided, automatically extracted from <think> tags)
if response.choices[0].reasoning_content:
    print(f"Reasoning: {response.choices[0].reasoning_content}")
```

### Tool Calling (Function Calling)

```python
from pixigpt import ChatCompletionRequest, Message

# Define tools (OpenAI format)
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name"}
                },
                "required": ["location"]
            }
        }
    }
]

# Request with tools
response = client.create_chat_completion(
    ChatCompletionRequest(
        messages=[
            Message(role="system", content="You are helpful"),
            Message(role="user", content="What's the weather in Paris?"),
        ],
        tools=tools,
    )
)

# Check if model wants to call a tool
if response.choices[0].finish_reason == "tool_calls":
    for tool_call in response.choices[0].message.tool_calls:
        print(f"Tool: {tool_call.function.name}")
        print(f"Args: {tool_call.function.arguments}")

        # Execute tool, then send result back
        result = {"temperature": 18, "conditions": "cloudy"}

        response = client.create_chat_completion(
            ChatCompletionRequest(
                messages=[
                    Message(role="system", content="You are helpful"),
                    Message(role="user", content="What's the weather in Paris?"),
                    response.choices[0].message,  # Assistant's tool call
                    Message(
                        role="tool",
                        content=json.dumps(result),
                        tool_call_id=tool_call.id,
                    ),
                ],
                tools=tools,
            )
        )
```

### Threads (Async with Memory)

```python
# Create thread
thread = client.create_thread()

# Add message
msg = client.create_message(thread.id, "user", "Hello!")

# Run assistant
run = client.create_run(thread.id, assistant_id, enable_thinking=True)

# Wait for completion (message included in response!)
completed_run = client.wait_for_run(thread.id, run.id)

# Access the assistant's response directly
content = completed_run.message.content[0].text["value"]
print(f"assistant: {content}")

# Access reasoning if available
if completed_run.message.reasoning_content:
    print(f"Reasoning: {completed_run.message.reasoning_content}")
```

### Assistants

```python
# List
assistants = client.list_assistants()

# Create
assistant = client.create_assistant(
    name="My Assistant",
    instructions="You are a helpful assistant.",
    tools_config=None,
)

# Update
assistant = client.update_assistant(
    assistant_id=assistant.id,
    name="Updated Name",
    instructions="New instructions",
)

# Delete
client.delete_assistant(assistant.id)
```

## Context Manager

```python
with Client(api_key, base_url) as client:
    response = client.create_chat_completion(...)
# Session automatically closed
```

## Error Handling

```python
from pixigpt import APIError, is_auth_error, is_rate_limit_error

try:
    response = client.create_chat_completion(request)
except APIError as e:
    if is_auth_error(e):
        print("Invalid API key")
    elif is_rate_limit_error(e):
        print("Rate limit exceeded")
    else:
        print(f"API error: {e}")
```

## Chain of Thought Reasoning

When `enable_thinking=True` (default), the server automatically extracts reasoning from `<think>` tags:

```python
response = client.create_chat_completion(
    ChatCompletionRequest(
        messages=[
            Message(role="system", content="You are helpful"),
            Message(role="user", content="Explain quantum physics"),
        ],
        enable_thinking=True,  # Default: true
    )
)

# Main response (thinking tags removed by server)
print(response.choices[0].message.content)

# Reasoning content (automatically extracted by vLLM, provided in separate field)
if response.choices[0].reasoning_content:
    print(f"Chain of thought: {response.choices[0].reasoning_content}")
```

**Note:** `reasoning_content` is provided directly by the server (vLLM extracts it). Both `content` and `reasoning_content` are automatically trimmed of whitespace. When thinking is enabled and `max_tokens` < 3000, it's automatically bumped to 3000 (CoT needs space).

## Examples

See [examples/](examples/) directory:
- [`chat.py`](examples/chat.py) - Simple chat completion
- [`thread.py`](examples/thread.py) - Multi-turn conversation

```bash
# Install dev dependencies
pip install pixigpt[dev]

# Run examples
python examples/chat.py
```

## Testing

```bash
pip install pixigpt[dev]
pytest
```

## Publishing to PyPI

```bash
# Update version in pyproject.toml
./publish.sh
```

## License

MIT
