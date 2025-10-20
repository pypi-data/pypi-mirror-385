"""Error types for PixiGPT API."""


class APIError(Exception):
    """Error returned by the PixiGPT API."""

    def __init__(self, error_data: dict, status_code: int):
        self.error_data = error_data
        self.status_code = status_code
        self.type = error_data.get("type", "unknown")
        self.message = error_data.get("message", "Unknown error")
        self.code = error_data.get("code")

        if self.code:
            super().__init__(f"[{self.code}] {self.type}: {self.message}")
        else:
            super().__init__(f"[{self.type}] {self.message}")


def is_auth_error(error: Exception) -> bool:
    """Check if error is an authentication error."""
    return isinstance(error, APIError) and error.type == "authentication_error"


def is_rate_limit_error(error: Exception) -> bool:
    """Check if error is a rate limit error."""
    return isinstance(error, APIError) and error.type == "rate_limit_error"
