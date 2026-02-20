from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import asdict

from app.config import settings
from app.engine.calculator import SajuCalculator
from app.engine.models import SajuData
from app.llm.client import LLMClient
from app.llm.formatter import format_saju_for_prompt
from app.llm.prompts.saju_reading import SAJU_READING_PROMPT
from app.models.request import BirthInput
from app.services.cache_service import CacheService


class SajuService:
    """Orchestrates saju calculation and LLM interpretation."""

    def __init__(
        self,
        calculator: SajuCalculator,
        llm_client: LLMClient,
        cache: CacheService,
    ):
        self._calculator = calculator
        self._llm = llm_client
        self._cache = cache

    def calculate(self, birth: BirthInput) -> SajuData:
        """Pure calculation, no LLM."""
        return self._calculator.calculate(
            year=birth.year,
            month=birth.month,
            day=birth.day,
            hour=birth.hour,
            minute=birth.minute,
            gender_male=birth.gender == "male",
            calendar_type=birth.calendar_type.value,
            is_leap_month=birth.is_leap_month,
            use_night_zi=birth.use_night_zi,
            use_true_solar_time=birth.use_true_solar_time,
        )

    async def reading(self, birth: BirthInput) -> tuple[SajuData, str]:
        """Calculate and generate full interpretation."""
        saju = self.calculate(birth)

        cache_key = CacheService.make_key(
            "reading",
            year=saju.solar_year, month=saju.solar_month, day=saju.solar_day,
            hour=saju.solar_hour, minute=saju.solar_minute,
            gender=birth.gender.value, night_zi=birth.use_night_zi,
            true_solar_time=birth.use_true_solar_time,
        )

        cached = await self._cache.get(cache_key)
        if cached:
            return saju, cached

        prompt = SAJU_READING_PROMPT.format(saju_data=format_saju_for_prompt(saju))
        interpretation = await self._llm.generate(prompt)

        await self._cache.set(cache_key, interpretation, ttl=settings.cache_ttl_interpretation)
        return saju, interpretation

    async def reading_stream(self, birth: BirthInput) -> tuple[SajuData, AsyncIterator[str]]:
        """Calculate and stream interpretation."""
        saju = self.calculate(birth)
        prompt = SAJU_READING_PROMPT.format(saju_data=format_saju_for_prompt(saju))
        return saju, self._llm.generate_stream(prompt)

    def saju_to_dict(self, saju: SajuData) -> dict:
        """Convert SajuData to a serializable dict matching SajuCalculateResponse."""
        d = asdict(saju)
        d["solar_date"] = f"{saju.solar_year}-{saju.solar_month:02d}-{saju.solar_day:02d}"
        d["lunar_date"] = f"{saju.lunar_year}-{abs(saju.lunar_month):02d}-{saju.lunar_day:02d}"

        # Remove raw fields not in response
        for key in (
            "solar_year", "solar_month", "solar_day",
            "solar_hour", "solar_minute",
            "lunar_year", "lunar_month", "lunar_day",
        ):
            d.pop(key, None)

        return d
