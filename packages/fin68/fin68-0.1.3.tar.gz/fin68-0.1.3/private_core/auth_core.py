from __future__ import annotations

import logging
from typing import Optional

from pydantic import ValidationError

from fin68.exceptions import ApiKeyValidationError, HttpError
from fin68.types import ApiKeyValidationResponse

from .http_core import HttpSession

logger = logging.getLogger(__name__)

VALIDATION_ENDPOINT = "/auth/validate"


def validate_api_key(
    session: HttpSession,
    *,
    client_version: str,
    include_messages: bool = True,
    extra_context: Optional[dict] = None,
) -> ApiKeyValidationResponse:
    """Validate the provided API key with the backend."""

    payload = {
        "apiKey": session.api_key,
        "clientVersion": client_version,
        "includeMessages": include_messages,
    }
    if extra_context:
        payload["context"] = extra_context

    try:
        response = session.post(VALIDATION_ENDPOINT, json_body=payload)
        response = session.post(VALIDATION_ENDPOINT, json_body=payload)
    except HttpError as exc: 
        logger.error(
            "Backend rejected API key validation (status=%s, payload=%s)",
            exc.status_code,
            exc.payload,
        )
        detail: Optional[str] = None
        if isinstance(exc.payload, dict):
            detail = exc.payload.get("detail") or exc.payload.get("message")
        elif isinstance(exc.payload, str):
            detail = exc.payload.strip() or None
        message = detail or f"Backend rejected API key validation (HTTP {exc.status_code})"
        raise ApiKeyValidationError(message) from exc
    except Exception as exc:  # pragma: no cover - network failure
        logger.exception("Failed to validate API key with Fin68 backend")
        raise ApiKeyValidationError("Unable to validate API key") from exc

    try:
        json_payload = response.json()
    except ValueError as exc:
        raise ApiKeyValidationError("Backend returned invalid JSON payload") from exc

    try:
        result = ApiKeyValidationResponse.model_validate(json_payload)
    except ValidationError as exc:
        raise ApiKeyValidationError("Backend response did not match expected schema") from exc

    logger.debug("API key validated successfully for version %s", client_version)
    return result
