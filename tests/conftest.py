from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from app.engine.calculator import SajuCalculator
from app.llm.client import LLMClient
from app.services.cache_service import CacheService
from app.services.saju_service import SajuService


@pytest.fixture
def calculator() -> SajuCalculator:
    return SajuCalculator()


@pytest.fixture
def saju_service(calculator: SajuCalculator) -> SajuService:
    return SajuService(calculator, LLMClient(None), CacheService(None))


@pytest.fixture
async def client():
    from app.main import app
    from app import dependencies

    # Initialize minimal dependencies without Redis/Anthropic
    dependencies._calculator = SajuCalculator()
    dependencies._llm_client = LLMClient(None)
    dependencies._cache_service = CacheService(None)
    dependencies._saju_service = SajuService(
        dependencies._calculator,
        dependencies._llm_client,
        dependencies._cache_service,
    )
    from app.services.compatibility_service import CompatibilityService
    from app.services.fortune_service import FortuneService

    dependencies._compatibility_service = CompatibilityService(
        dependencies._calculator,
        dependencies._llm_client,
        dependencies._cache_service,
    )
    dependencies._fortune_service = FortuneService(
        dependencies._calculator,
        dependencies._llm_client,
        dependencies._cache_service,
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
