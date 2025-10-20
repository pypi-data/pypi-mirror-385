"""PixiGPT API client with production-grade HTTP handling."""

import time
import re
from typing import List, Optional, Tuple
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .types import (
    Message,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionChoice,
    Usage,
    Thread,
    ThreadMessage,
    MessageContent,
    Run,
    Assistant,
)
from .errors import APIError


class Client:
    """
    PixiGPT API client with production-grade defaults.

    Features:
    - Connection pooling (100 connections)
    - Smart retries with exponential backoff
    - 30s timeout
    - Keep-alive enabled
    """

    def __init__(
        self,
        api_key: str,
        base_url: str,
        timeout: int = 30,
        max_retries: int = 3,
        session: Optional[requests.Session] = None,
    ):
        """
        Create a new PixiGPT client.

        Args:
            api_key: PixiGPT API key
            base_url: Base URL for API (e.g., https://pixigpt.com/v1)
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum retry attempts (default: 3)
            session: Custom requests.Session (optional)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        if session:
            self.session = session
        else:
            # Create session with connection pooling and retries
            self.session = requests.Session()

            # Connection pooling
            adapter = HTTPAdapter(
                pool_connections=100,
                pool_maxsize=100,
                max_retries=Retry(
                    total=max_retries,
                    backoff_factor=0.1,  # 0.1s, 0.2s, 0.4s, 0.8s...
                    status_forcelist=[500, 502, 503, 504],  # Retry on server errors
                    allowed_methods=["GET", "POST", "PUT", "DELETE"],
                ),
            )
            self.session.mount("http://", adapter)
            self.session.mount("https://", adapter)

            # Default headers
            self.session.headers.update(
                {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                }
            )

    def _request(self, method: str, path: str, json: Optional[dict] = None) -> dict:
        """Execute HTTP request with error handling."""
        url = urljoin(self.base_url + "/", path.lstrip("/"))

        try:
            response = self.session.request(
                method=method,
                url=url,
                json=json,
                timeout=self.timeout,
            )

            # Handle HTTP errors
            if response.status_code >= 400:
                try:
                    error_data = response.json().get("error", {})
                except Exception:
                    error_data = {"message": response.text, "type": "unknown"}

                raise APIError(error_data, response.status_code)

            return response.json() if response.text else {}

        except requests.RequestException as e:
            raise APIError(
                {"message": str(e), "type": "request_error"}, 0
            ) from e

    @staticmethod
    def _extract_reasoning(content: str) -> Tuple[str, Optional[str]]:
        """
        Extract chain of thought reasoning from content.

        Returns:
            (main_content, reasoning_content)
        """
        # Match <think>...</think> or <thinking>...</thinking>
        think_pattern = r"<think(?:ing)?>(.*?)</think(?:ing)?>"
        match = re.search(think_pattern, content, re.DOTALL | re.IGNORECASE)

        if match:
            reasoning = match.group(1).strip()
            # Remove thinking tags from main content
            main_content = re.sub(think_pattern, "", content, flags=re.DOTALL | re.IGNORECASE).strip()
            return main_content, reasoning

        return content, None

    def create_chat_completion(
        self, request: ChatCompletionRequest
    ) -> ChatCompletionResponse:
        """
        Create a stateless chat completion.

        Example:
            >>> client = Client(api_key, base_url)
            >>> response = client.create_chat_completion(
            ...     ChatCompletionRequest(
            ...         assistant_id="...",
            ...         messages=[Message(role="user", content="Hello!")],
            ...     )
            ... )
            >>> print(response.choices[0].message.content)
        """
        data = {
            "assistant_id": request.assistant_id,
            "messages": [{"role": m.role, "content": m.content} for m in request.messages],
        }

        # Only include if non-zero (server handles defaults)
        if request.temperature > 0:
            data["temperature"] = request.temperature
        if request.max_tokens > 0:
            data["max_tokens"] = request.max_tokens
        if request.enable_thinking is not None:
            data["enable_thinking"] = request.enable_thinking

        resp = self._request("POST", "/chat/completions", json=data)

        # Parse response and extract reasoning
        choices = []
        for choice_data in resp["choices"]:
            msg_data = choice_data["message"]
            content, reasoning = self._extract_reasoning(msg_data["content"])

            choices.append(
                ChatCompletionChoice(
                    index=choice_data["index"],
                    message=Message(role=msg_data["role"], content=content),
                    finish_reason=choice_data["finish_reason"],
                    reasoning_content=reasoning,
                )
            )

        return ChatCompletionResponse(
            id=resp["id"],
            object=resp["object"],
            created=resp["created"],
            model=resp["model"],
            choices=choices,
            usage=Usage(**resp["usage"]),
        )

    def create_thread(self) -> Thread:
        """Create a new conversation thread."""
        resp = self._request("POST", "/threads", json={})
        return Thread(**resp)

    def get_thread(self, thread_id: str) -> Thread:
        """Retrieve a thread by ID."""
        resp = self._request("GET", f"/threads/{thread_id}")
        return Thread(**resp)

    def list_threads(self) -> List[Thread]:
        """List all API threads for the authenticated user."""
        resp = self._request("GET", "/threads")
        return [Thread(**t) for t in resp["data"]]

    def delete_thread(self, thread_id: str) -> None:
        """Delete a thread and all its messages."""
        self._request("DELETE", f"/threads/{thread_id}")

    def create_message(self, thread_id: str, role: str, content: str) -> ThreadMessage:
        """Add a message to a thread."""
        resp = self._request(
            "POST",
            f"/threads/{thread_id}/messages",
            json={"role": role, "content": content},
        )

        # Extract reasoning if present
        reasoning_content = None
        if resp.get("content") and len(resp["content"]) > 0:
            text_value = resp["content"][0].get("text", {}).get("value", "")
            _, reasoning_content = self._extract_reasoning(text_value)

        return ThreadMessage(
            id=resp["id"],
            object=resp["object"],
            created_at=resp["created_at"],
            thread_id=resp["thread_id"],
            role=resp["role"],
            content=[MessageContent(**c) for c in resp["content"]],
            reasoning_content=reasoning_content,
        )

    def list_messages(self, thread_id: str, limit: int = 20) -> List[ThreadMessage]:
        """List messages from a thread."""
        resp = self._request("GET", f"/threads/{thread_id}/messages?limit={limit}")

        messages = []
        for msg_data in resp["data"]:
            # Extract reasoning if present
            reasoning_content = None
            if msg_data.get("content") and len(msg_data["content"]) > 0:
                text_value = msg_data["content"][0].get("text", {}).get("value", "")
                _, reasoning_content = self._extract_reasoning(text_value)

            messages.append(
                ThreadMessage(
                    id=msg_data["id"],
                    object=msg_data["object"],
                    created_at=msg_data["created_at"],
                    thread_id=msg_data["thread_id"],
                    role=msg_data["role"],
                    content=[MessageContent(**c) for c in msg_data["content"]],
                    reasoning_content=reasoning_content,
                )
            )

        return messages

    def create_run(
        self,
        thread_id: str,
        assistant_id: str,
        temperature: float = 0.0,
        max_tokens: int = 0,
        enable_thinking: bool = True,
    ) -> Run:
        """
        Create an async run.

        Args:
            thread_id: Thread ID
            assistant_id: Assistant ID
            temperature: Temperature (0 = server default of 0.6)
            max_tokens: Max tokens (0 = vLLM default)
            enable_thinking: Enable chain of thought (default: True)
        """
        data = {
            "assistant_id": assistant_id,
            "enable_thinking": enable_thinking,
        }

        # Only include if > 0 (server handles defaults)
        if temperature > 0:
            data["temperature"] = temperature
        if max_tokens > 0:
            data["max_tokens"] = max_tokens

        resp = self._request("POST", f"/threads/{thread_id}/runs", json=data)
        return Run(**resp)

    def get_run(self, thread_id: str, run_id: str) -> Run:
        """Get run status."""
        resp = self._request("GET", f"/threads/{thread_id}/runs/{run_id}")
        return Run(**resp)

    def wait_for_run(
        self, thread_id: str, run_id: str, poll_interval: float = 0.5
    ) -> Run:
        """
        Poll until run completes.

        Args:
            thread_id: Thread ID
            run_id: Run ID
            poll_interval: Polling interval in seconds (default: 0.5)

        Returns:
            Completed run

        Raises:
            RuntimeError: If run fails or is cancelled
        """
        while True:
            run = self.get_run(thread_id, run_id)

            if run.status == "completed":
                return run
            elif run.status == "failed":
                raise RuntimeError("Run failed")
            elif run.status == "cancelled":
                raise RuntimeError("Run cancelled")

            time.sleep(poll_interval)

    def list_assistants(self) -> List[Assistant]:
        """List all assistants."""
        resp = self._request("GET", "/assistants")
        return [Assistant(**a) for a in resp["data"]]

    def get_assistant(self, assistant_id: str) -> Assistant:
        """Get assistant by ID."""
        resp = self._request("GET", f"/assistants/{assistant_id}")
        return Assistant(**resp)

    def create_assistant(
        self, name: str, instructions: str, tools_config: Optional[str] = None
    ) -> Assistant:
        """Create a new assistant."""
        data = {"name": name, "instructions": instructions}
        if tools_config:
            data["tools_config"] = tools_config

        resp = self._request("POST", "/assistants", json=data)
        return Assistant(**resp)

    def update_assistant(
        self,
        assistant_id: str,
        name: str,
        instructions: str,
        tools_config: Optional[str] = None,
    ) -> Assistant:
        """Update an assistant."""
        data = {"name": name, "instructions": instructions}
        if tools_config:
            data["tools_config"] = tools_config

        resp = self._request("PUT", f"/assistants/{assistant_id}", json=data)
        return Assistant(**resp)

    def delete_assistant(self, assistant_id: str) -> None:
        """Delete an assistant."""
        self._request("DELETE", f"/assistants/{assistant_id}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close session."""
        self.session.close()
