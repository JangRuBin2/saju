from __future__ import annotations

import hashlib
import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


class CacheService:
    """Redis cache abstraction with graceful degradation."""

    def __init__(self, redis_client=None):
        self._redis = redis_client

    @property
    def available(self) -> bool:
        return self._redis is not None

    async def get(self, key: str) -> Any | None:
        if not self.available:
            return None
        try:
            data = await self._redis.get(key)
            if data is None:
                return None
            return json.loads(data)
        except Exception:
            logger.warning("Cache get failed for key=%s", key, exc_info=True)
            return None

    async def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        if not self.available:
            return
        try:
            await self._redis.set(key, json.dumps(value, ensure_ascii=False), ex=ttl)
        except Exception:
            logger.warning("Cache set failed for key=%s", key, exc_info=True)

    async def delete(self, key: str) -> None:
        if not self.available:
            return
        try:
            await self._redis.delete(key)
        except Exception:
            logger.warning("Cache delete failed for key=%s", key, exc_info=True)

    @staticmethod
    def make_key(prefix: str, **kwargs) -> str:
        """Create a deterministic cache key from parameters."""
        raw = json.dumps(kwargs, sort_keys=True)
        digest = hashlib.sha256(raw.encode()).hexdigest()[:16]
        return f"saju:{prefix}:{digest}"
