"""
api/actions/exceptions.py
--------------------------
Custom exceptions for the Actions domain with structured payloads suitable for API responses.
"""

from __future__ import annotations

from typing import Any


class ActionValidationError(Exception):
    """Raised when business validation fails while executing an Action.

    Attributes:
        code: Stable machine-readable error code (e.g., "invalid_parameters").
        message: Human-friendly summary.
        details: Optional structured payload with extra context (e.g., field errors).
        http_status: Suggested HTTP status code (default 400).
    """

    def __init__(
        self,
        code: str,
        message: str,
        details: Any | None = None,
        *,
        http_status: int = 400,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details
        self.http_status = http_status

    def to_http_detail(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"code": self.code, "message": self.message}
        if self.details is not None:
            payload["details"] = self.details
        return payload
