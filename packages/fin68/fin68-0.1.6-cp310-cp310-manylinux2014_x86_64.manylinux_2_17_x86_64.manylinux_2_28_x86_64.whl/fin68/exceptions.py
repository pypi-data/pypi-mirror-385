from __future__ import annotations

from typing import Any, Optional


class Fin68Error(Exception):
    """Base exception for all Fin68 client errors."""


class ConfigurationError(Fin68Error):
    """Raised when the client is misconfigured."""


class HttpError(Fin68Error):
    """Raised when an HTTP call returns an unexpected status code."""

    def __init__(self, message: str, *, status_code: Optional[int] = None, payload: Any = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload


class ApiKeyValidationError(Fin68Error):
    """Raised when the backend rejects or cannot validate the API key."""


class DataDecodingError(Fin68Error):
    """Raised when raw API data cannot be transformed into the expected format."""
