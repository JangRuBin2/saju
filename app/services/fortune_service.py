from __future__ import annotations

from datetime import date

from lunar_python import Solar

from app.config import settings
from app.engine.calculator import SajuCalculator
from app.engine.models import SajuData
from app.llm.client import LLMClient
from app.llm.formatter import format_saju_for_prompt
from app.llm.prompts.fortune import DAILY_FORTUNE_PROMPT, MONTHLY_FORTUNE_PROMPT
from app.models.request import BirthInput
from app.services.cache_service import CacheService


class FortuneService:
    """Handles monthly and daily fortune analysis."""

    def __init__(
        self,
        calculator: SajuCalculator,
        llm_client: LLMClient,
        cache: CacheService,
    ):
        self._calculator = calculator
        self._llm = llm_client
        self._cache = cache

    def _calculate_person(self, birth: BirthInput) -> SajuData:
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
        )

    def _get_target_period_info(
        self, target_year: int, target_month: int, target_day: int | None = None
    ) -> str:
        """Get the Gan-Zhi info for a target date/month."""
        day = target_day if target_day else 15  # mid-month for monthly
        solar = Solar(target_year, target_month, day, 12, 0, 0)
        lunar = solar.getLunar()
        ec = lunar.getEightChar()

        lines = [f"대상 연도: {target_year}년"]
        lines.append(f"연간지: {ec.getYear()}")
        lines.append(f"월간지: {ec.getMonth()}")
        if target_day:
            lines.append(f"대상 날짜: {target_year}년 {target_month}월 {target_day}일")
            lines.append(f"일간지: {ec.getDay()}")
        else:
            lines.append(f"대상 월: {target_year}년 {target_month}월")

        return "\n".join(lines)

    async def monthly(
        self, birth: BirthInput, target_year: int, target_month: int
    ) -> tuple[SajuData, str, str]:
        """Generate monthly fortune."""
        saju = self._calculate_person(birth)
        target_date_str = f"{target_year}-{target_month:02d}"

        cache_key = CacheService.make_key(
            "monthly",
            y=saju.solar_year, m=saju.solar_month, d=saju.solar_day,
            h=saju.solar_hour, g=birth.gender.value,
            ty=target_year, tm=target_month,
        )

        cached = await self._cache.get(cache_key)
        if cached:
            return saju, cached, target_date_str

        period_info = self._get_target_period_info(target_year, target_month)
        prompt = MONTHLY_FORTUNE_PROMPT.format(
            saju_data=format_saju_for_prompt(saju),
            target_period=period_info,
        )
        interpretation = await self._llm.generate(prompt)

        await self._cache.set(cache_key, interpretation, ttl=settings.cache_ttl_fortune)
        return saju, interpretation, target_date_str

    async def daily(
        self, birth: BirthInput, target_year: int, target_month: int, target_day: int
    ) -> tuple[SajuData, str, str]:
        """Generate daily fortune."""
        saju = self._calculate_person(birth)
        target_date_str = f"{target_year}-{target_month:02d}-{target_day:02d}"

        cache_key = CacheService.make_key(
            "daily",
            y=saju.solar_year, m=saju.solar_month, d=saju.solar_day,
            h=saju.solar_hour, g=birth.gender.value,
            ty=target_year, tm=target_month, td=target_day,
        )

        cached = await self._cache.get(cache_key)
        if cached:
            return saju, cached, target_date_str

        period_info = self._get_target_period_info(target_year, target_month, target_day)
        prompt = DAILY_FORTUNE_PROMPT.format(
            saju_data=format_saju_for_prompt(saju),
            target_period=period_info,
        )
        interpretation = await self._llm.generate(prompt)

        # Daily fortune cache until end of day
        await self._cache.set(cache_key, interpretation, ttl=settings.cache_ttl_fortune)
        return saju, interpretation, target_date_str
