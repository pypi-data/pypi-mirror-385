"""
Lightweight error hierarchy used by the Stateset SDK.

The goal of this module is to expose a predictable set of exceptions that map
directly to the responses returned by the HTTP client while staying small
enough to be understood at a glance.
"""

from __future__ import annotations

from http import HTTPStatus
from typing import Any, Dict, Optional, Type


class StatesetError(Exception):
    """Base exception type for all SDK related failures."""

    def __init__(
        self,
        message: str,
        error_type: str,
        code: Optional[str] = None,
        detail: Optional[str] = None,
        path: Optional[str] = None,
        status_code: Optional[int] = None,
        raw_response: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.type = error_type
        self.code = code
        self.detail = detail
        self.path = path
        self.status_code = status_code
        self.raw_response = raw_response or {}

    def __str__(self) -> str:  # pragma: no cover - human readable formatting
        parts: list[str] = [f"[{self.type}] {super().__str__()}"]
        if self.status_code is not None:
            parts.append(f"status={self.status_code}")
        if self.code:
            parts.append(f"code={self.code}")
        if self.path:
            parts.append(f"path={self.path}")
        return " ".join(parts)

    @classmethod
    def from_response(
        cls,
        response_content: bytes,
        status_code: Optional[int] = None,
    ) -> "StatesetError":
        """Parse an API error payload into the appropriate error subclass."""
        import json

        try:
            data = json.loads(response_content)
        except (json.JSONDecodeError, UnicodeDecodeError):
            data = {
                "message": response_content.decode("utf-8", errors="replace"),
                "type": "api_error",
            }

        error_type = data.get("type", "api_error")
        message = data.get("message", "Unknown error")

        error_class = ERROR_TYPE_MAPPING.get(error_type, cls)
        return error_class(
            message=message,
            error_type=error_type,
            code=data.get("code"),
            detail=data.get("detail"),
            path=data.get("path"),
            status_code=status_code,
            raw_response=data,
        )


class StatesetInvalidRequestError(StatesetError):
    def __init__(self, message: str = "Invalid request", **kwargs: Any) -> None:
        super().__init__(message=message, error_type="invalid_request_error", **kwargs)


class StatesetAPIError(StatesetError):
    def __init__(self, message: str = "API error occurred", **kwargs: Any) -> None:
        super().__init__(message=message, error_type="api_error", **kwargs)


class StatesetAuthenticationError(StatesetError):
    def __init__(self, message: str = "Authentication failed", **kwargs: Any) -> None:
        super().__init__(message=message, error_type="authentication_error", **kwargs)


class StatesetPermissionError(StatesetError):
    def __init__(self, message: str = "Permission denied", **kwargs: Any) -> None:
        super().__init__(message=message, error_type="permission_error", **kwargs)


class StatesetNotFoundError(StatesetError):
    def __init__(
        self,
        message: str = "Resource not found",
        *,
        resource_type: str = "resource",
        resource_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        if resource_id:
            message = f"{resource_type} not found: {resource_id}"
        super().__init__(
            message=message,
            error_type="not_found_error",
            **kwargs,
        )
        self.resource_type = resource_type
        self.resource_id = resource_id


class StatesetConnectionError(StatesetError):
    def __init__(self, message: str = "Connection error", **kwargs: Any) -> None:
        super().__init__(message=message, error_type="connection_error", **kwargs)


class StatesetRateLimitError(StatesetError):
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        *,
        retry_after: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        if retry_after:
            message = f"{message}. Retry after {retry_after} seconds"
        super().__init__(message=message, error_type="rate_limit_error", **kwargs)
        self.retry_after = retry_after


ERROR_TYPE_MAPPING: Dict[str, Type[StatesetError]] = {
    "invalid_request_error": StatesetInvalidRequestError,
    "api_error": StatesetAPIError,
    "authentication_error": StatesetAuthenticationError,
    "permission_error": StatesetPermissionError,
    "not_found_error": StatesetNotFoundError,
    "connection_error": StatesetConnectionError,
    "rate_limit_error": StatesetRateLimitError,
}


def raise_for_status_code(
    status_code: int,
    content: bytes,
    expected_codes: Optional[set[int]] = None,
) -> None:
    """Raise an appropriate error given a non-success HTTP response."""
    if expected_codes and status_code in expected_codes:
        return
    if 200 <= status_code < 300:
        return

    try:
        error = StatesetError.from_response(content, status_code=status_code)
    except Exception:
        status_desc = "HTTP error"
        try:
            status_desc = HTTPStatus(status_code).phrase
        except ValueError:
            pass
        error = StatesetAPIError(
            message=f"HTTP {status_code} {status_desc}",
            status_code=status_code,
        )

    raise error
