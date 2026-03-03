"""HMAC-SHA256 service token validation middleware."""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
import time
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.config import settings

logger = logging.getLogger(__name__)

_SKIP_PATHS: frozenset[str] = frozenset({
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
})

_TOKEN_MAX_AGE_SECONDS = 300


def _json_error(status_code: int, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": "Unauthorized", "message": message},
    )


class TokenValidatorMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not settings.require_service_token:
            return await call_next(request)

        if request.url.path in _SKIP_PATHS:
            return await call_next(request)

        token = request.headers.get("X-Service-Token")
        if not token:
            return _json_error(401, "Missing service token")

        try:
            decoded_bytes = base64.b64decode(token)
            token_data: dict = json.loads(decoded_bytes)
        except Exception:
            return _json_error(401, "Invalid token encoding")

        signature = token_data.pop("signature", None)
        if not signature:
            return _json_error(401, "Missing signature in token")

        user_id = token_data.get("user_id")
        reading_type = token_data.get("reading_type")
        timestamp = token_data.get("timestamp")

        if not user_id or reading_type is None or timestamp is None:
            return _json_error(401, "Incomplete token payload")

        now = int(time.time())
        if abs(now - timestamp) > _TOKEN_MAX_AGE_SECONDS:
            return _json_error(401, "Token expired")

        # JSON.stringify() produces compact JSON with no spaces
        message = json.dumps(token_data, separators=(",", ":"), ensure_ascii=False)
        expected_signature = hmac.new(
            settings.api_secret_key.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(expected_signature, signature):
            return _json_error(401, "Invalid token signature")

        request.state.user_id = user_id
        request.state.reading_type = reading_type

        return await call_next(request)
