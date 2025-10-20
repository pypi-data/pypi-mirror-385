# PixiGPT Python Client

Production-grade Python client for the [PixiGPT API](https://pixigpt.com).

## Features

- 🚀 **High Performance**: Connection pooling with 100 connections
- 🔄 **Smart Retries**: Exponential backoff (0.1s → 0.8s)
- ⏱️ **Timeouts**: 30s default, fully configurable
- 🎯 **Type Hints**: Full typing support for modern Python
- 📦 **Minimal Dependencies**: Just `requests` + `urllib3`
- 🔧 **OpenAI Compatible**: Familiar API surface
- 🧠 **Reasoning Extraction**: Automatic CoT reasoning extraction

## Installation

```bash
pip install pixigpt
```

## Quick Start

```python
from pixigpt import Client, ChatCompletionRequest, Message

client = Client("sk-proj-YOUR_API_KEY", "https://pixigpt.com/v1")

response = client.create_chat_completion(
    ChatCompletionRequest(
        assistant_id="your-assistant-id",
        messages=[Message(role="user", content="Hello!")],
    )
)

print(response.choices[0].message.content)

# Access chain of thought reasoning (if present)
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

response = client.create_chat_completion(
    ChatCompletionRequest(
        assistant_id=assistant_id,
        messages=[
            Message(role="user", content="What's the weather?"),
        ],
        temperature=0.7,
        max_tokens=2000,
        enable_thinking=True,  # Enable chain of thought
    )
)

# Access response
print(response.choices[0].message.content)
print(f"Tokens: {response.usage.total_tokens}")

# Access reasoning (if enable_thinking=True)
if response.choices[0].reasoning_content:
    print(f"Reasoning: {response.choices[0].reasoning_content}")
```

### Threads (Async with Memory)

```python
# Create thread
thread = client.create_thread()

# Add message
msg = client.create_message(thread.id, "user", "Hello!")

# Run assistant
run = client.create_run(thread.id, assistant_id, enable_thinking=True)

# Wait for completion
completed_run = client.wait_for_run(thread.id, run.id)

# Get messages
messages = client.list_messages(thread.id, limit=10)

for msg in messages:
    content = msg.content[0].text["value"]
    print(f"{msg.role}: {content}")

    # Access reasoning
    if msg.reasoning_content:
        print(f"Reasoning: {msg.reasoning_content}")
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

The client automatically extracts chain of thought reasoning from `<think>` or `<thinking>` tags:

```python
response = client.create_chat_completion(
    ChatCompletionRequest(
        assistant_id=assistant_id,
        messages=[Message(role="user", content="Explain quantum physics")],
        enable_thinking=True,
    )
)

# Main response (thinking tags removed)
print(response.choices[0].message.content)

# Reasoning content (extracted from <think> tags)
if response.choices[0].reasoning_content:
    print(f"Chain of thought: {response.choices[0].reasoning_content}")
```

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
