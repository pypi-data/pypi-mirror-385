"""Integration tests for PixiGPT client."""

import os
import time
import pytest
from dotenv import load_dotenv

from pixigpt import (
    Client,
    ChatCompletionRequest,
    Message,
    APIError,
)

# Load test environment
load_dotenv()

API_KEY = os.getenv("PIXIGPT_API_KEY")
BASE_URL = os.getenv("PIXIGPT_BASE_URL")
ASSISTANT_ID = os.getenv("DEFAULT_ASSISTANT_ID")

if not all([API_KEY, BASE_URL, ASSISTANT_ID]):
    pytest.skip(
        "Missing test environment variables",
        allow_module_level=True,
    )


@pytest.fixture
def client():
    """Create test client."""
    return Client(API_KEY, BASE_URL)


def test_chat_completion(client):
    """Test basic chat completion."""
    response = client.create_chat_completion(
        ChatCompletionRequest(
            assistant_id=ASSISTANT_ID,
            messages=[Message(role="user", content="Say only 'TEST PASS' and nothing else.")],
            temperature=0.1,
            max_tokens=50,
        )
    )

    assert response.id
    assert response.object == "chat.completion"
    assert len(response.choices) > 0

    choice = response.choices[0]
    assert choice.message.content
    assert response.usage.total_tokens > 0

    print(f"\nResponse: {choice.message.content}")
    print(f"Tokens: {response.usage.total_tokens}")

    # Check if reasoning was extracted
    if choice.reasoning_content:
        print(f"Reasoning: {choice.reasoning_content[:200]}...")


def test_chat_completion_thinking_disabled(client):
    """Test chat completion with thinking disabled."""
    response = client.create_chat_completion(
        ChatCompletionRequest(
            assistant_id=ASSISTANT_ID,
            messages=[Message(role="user", content="What is 2+2?")],
            enable_thinking=False,
            max_tokens=100,
        )
    )

    assert response.choices[0].message.content
    print(f"\nResponse (no thinking): {response.choices[0].message.content}")
    print(f"Reasoning extracted: {response.choices[0].reasoning_content is not None}")


def test_thread_workflow(client):
    """Test full thread workflow."""
    # 1. Create thread
    thread = client.create_thread()
    assert thread.id
    assert thread.object == "thread"
    print(f"\nCreated thread: {thread.id}")

    # 2. Add message
    msg = client.create_message(thread.id, "user", "What is the capital of France? Answer in one word.")
    assert msg.id
    assert msg.role == "user"
    print(f"Created message: {msg.id}")

    # 3. Create run
    run = client.create_run(thread.id, ASSISTANT_ID, enable_thinking=True)
    assert run.id
    assert run.status in ["queued", "in_progress"]
    print(f"Created run: {run.id} (status: {run.status})")

    # 4. Wait for completion
    completed_run = client.wait_for_run(thread.id, run.id)
    assert completed_run.status == "completed"
    print(f"Run completed: {completed_run.status}")

    # 5. List messages
    messages = client.list_messages(thread.id, limit=10)
    assert len(messages) >= 2

    print("\n=== Conversation ===")
    for msg in reversed(messages):
        if msg.content:
            content = msg.content[0].text["value"]
            print(f"{msg.role}: {content}")

            if msg.reasoning_content:
                print(f"  [Reasoning: {msg.reasoning_content[:100]}...]")

    # Verify assistant response
    assistant_msgs = [m for m in messages if m.role == "assistant"]
    assert len(assistant_msgs) > 0
    assert assistant_msgs[0].content[0].text["value"]


def test_get_thread(client):
    """Test thread retrieval."""
    thread = client.create_thread()
    retrieved = client.get_thread(thread.id)

    assert retrieved.id == thread.id
    assert retrieved.object == "thread"


def test_error_handling(client):
    """Test API error handling."""
    with pytest.raises(APIError) as exc_info:
        client.create_chat_completion(
            ChatCompletionRequest(
                assistant_id="invalid-uuid",
                messages=[Message(role="user", content="test")],
            )
        )

    error = exc_info.value
    assert error.type == "invalid_request_error"
    print(f"\nExpected error: {error}")


def test_context_manager():
    """Test context manager usage."""
    with Client(API_KEY, BASE_URL) as client:
        response = client.create_chat_completion(
            ChatCompletionRequest(
                assistant_id=ASSISTANT_ID,
                messages=[Message(role="user", content="Hello")],
                max_tokens=50,
            )
        )
        assert response.choices[0].message.content
