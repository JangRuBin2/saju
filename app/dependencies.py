from __future__ import annotations

import logging

from anthropic import AsyncAnthropic

from app.config import settings
from app.engine.calculator import SajuCalculator
from app.llm.client import LLMClient
from app.services.cache_service import CacheService
from app.services.compatibility_service import CompatibilityService
from app.services.fortune_service import FortuneService
from app.services.saju_service import SajuService

logger = logging.getLogger(__name__)

# Singletons
_calculator: SajuCalculator | None = None
_llm_client: LLMClient | None = None
_cache_service: CacheService | None = None
_saju_service: SajuService | None = None
_compatibility_service: CompatibilityService | None = None
_fortune_service: FortuneService | None = None


async def init_dependencies() -> None:
    """Initialize all dependencies on app startup."""
    global _calculator, _llm_client, _cache_service
    global _saju_service, _compatibility_service, _fortune_service

    _calculator = SajuCalculator()

    # LLM client
    anthropic_client = None
    if settings.anthropic_api_key:
        anthropic_client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        logger.info("Anthropic client initialized")
    else:
        logger.warning("ANTHROPIC_API_KEY not set. LLM features will be unavailable.")
    _llm_client = LLMClient(anthropic_client)

    # Redis (optional)
    redis_client = None
    try:
        import redis.asyncio as aioredis

        redis_client = aioredis.from_url(settings.redis_url)
        await redis_client.ping()
        logger.info("Redis connected: %s", settings.redis_url)
    except Exception:
        logger.warning("Redis unavailable. Running without cache.")
        redis_client = None

    _cache_service = CacheService(redis_client)

    # Services
    _saju_service = SajuService(_calculator, _llm_client, _cache_service)
    _compatibility_service = CompatibilityService(_calculator, _llm_client, _cache_service)
    _fortune_service = FortuneService(_calculator, _llm_client, _cache_service)



async def shutdown_dependencies() -> None:
    """Cleanup on shutdown."""
    if _cache_service and _cache_service.available and _cache_service._redis:
        await _cache_service._redis.aclose()
        logger.info("Redis connection closed")


def get_saju_service() -> SajuService:
    assert _saju_service is not None
    return _saju_service


def get_compatibility_service() -> CompatibilityService:
    assert _compatibility_service is not None
    return _compatibility_service


def get_fortune_service() -> FortuneService:
    assert _fortune_service is not None
    return _fortune_service
