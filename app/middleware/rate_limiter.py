"""Per-user rate limiting middleware using Redis."""
from __future__ import annotations

import logging
import time
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.config import settings

logger = logging.getLogger(__name__)

_SKIP_PATHS: frozenset[str] = frozenset({"/health"})

_DEFAULT_LIMIT = 30
_WINDOW_SECONDS = 60


class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self._redis = None
        self._redis_checked = False

    async def _get_redis(self):
        if not self._redis_checked:
            self._redis_checked = True
            try:
                import redis.asyncio as aioredis

                client = aioredis.from_url(settings.redis_url)
                await client.ping()
                self._redis = client
            except Exception:
                logger.warning("Rate limiter: Redis unavailable, rate limiting disabled")
                self._redis = None
        return self._redis

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path in _SKIP_PATHS:
            return await call_next(request)

        if not settings.require_service_token:
            return await call_next(request)

        user_id = getattr(request.state, "user_id", None)

        if not user_id:
            return await call_next(request)

        redis = await self._get_redis()
        if redis is None:
            return await call_next(request)

        current_minute = int(time.time()) // _WINDOW_SECONDS
        rate_key = f"rate:{user_id}:{current_minute}"

        try:
            current_count = await redis.incr(rate_key)
            if current_count == 1:
                await redis.expire(rate_key, _WINDOW_SECONDS)

            if current_count > _DEFAULT_LIMIT:
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "RateLimitExceeded",
                        "message": f"Rate limit exceeded. {_DEFAULT_LIMIT} requests per minute allowed.",
                    },
                )
        except Exception:
            logger.warning("Rate limiter: Redis error, allowing request", exc_info=True)

        return await call_next(request)
