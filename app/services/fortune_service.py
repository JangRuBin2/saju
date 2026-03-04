from __future__ import annotations

from datetime import date

from lunar_python import Solar

from app.config import settings
from app.engine.calculator import SajuCalculator
from app.engine.models import SajuData
from app.llm.client import LLMClient
from app.llm.formatter import format_saju_for_prompt
from app.llm.prompts.fortune import DAILY_FORTUNE_PROMPT, MONTHLY_FORTUNE_PROMPT
from app.llm.prompts.timing import (
    TIMING_BEST_HOURS_PROMPT,
    TIMING_DDAY_PROMPT,
    TIMING_NOW_PROMPT,
)
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
            use_true_solar_time=birth.use_true_solar_time,
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
        self,
        birth: BirthInput,
        target_year: int,
        target_month: int,
        *,
        language: str = "ko",
    ) -> tuple[SajuData, str, str]:
        """Generate monthly fortune."""
        saju = self._calculate_person(birth)
        target_date_str = f"{target_year}-{target_month:02d}"

        cache_key = CacheService.make_key(
            "monthly",
            y=saju.solar_year, m=saju.solar_month, d=saju.solar_day,
            h=saju.solar_hour, g=birth.gender.value,
            ty=target_year, tm=target_month,
            lang=language,
        )

        cached = await self._cache.get(cache_key)
        if cached:
            return saju, cached, target_date_str

        period_info = self._get_target_period_info(target_year, target_month)
        prompt = MONTHLY_FORTUNE_PROMPT.format(
            saju_data=format_saju_for_prompt(saju),
            target_period=period_info,
        )
        interpretation = await self._llm.generate(prompt, language=language)

        await self._cache.set(cache_key, interpretation, ttl=settings.cache_ttl_fortune)
        return saju, interpretation, target_date_str

    async def daily(
        self,
        birth: BirthInput,
        target_year: int,
        target_month: int,
        target_day: int,
        *,
        language: str = "ko",
    ) -> tuple[SajuData, str, str]:
        """Generate daily fortune."""
        saju = self._calculate_person(birth)
        target_date_str = f"{target_year}-{target_month:02d}-{target_day:02d}"

        cache_key = CacheService.make_key(
            "daily",
            y=saju.solar_year, m=saju.solar_month, d=saju.solar_day,
            h=saju.solar_hour, g=birth.gender.value,
            ty=target_year, tm=target_month, td=target_day,
            lang=language,
        )

        cached = await self._cache.get(cache_key)
        if cached:
            return saju, cached, target_date_str

        period_info = self._get_target_period_info(target_year, target_month, target_day)
        prompt = DAILY_FORTUNE_PROMPT.format(
            saju_data=format_saju_for_prompt(saju),
            target_period=period_info,
        )
        interpretation = await self._llm.generate(prompt, language=language)

        # Daily fortune cache until end of day
        await self._cache.set(cache_key, interpretation, ttl=settings.cache_ttl_fortune)
        return saju, interpretation, target_date_str

    def _get_target_time_info(
        self,
        target_year: int,
        target_month: int,
        target_day: int,
        target_hour: int | None = None,
    ) -> str:
        """Get Gan-Zhi info for a target date/time including hour pillar."""
        hour = target_hour if target_hour is not None else 12
        solar = Solar(target_year, target_month, target_day, hour, 0, 0)
        lunar = solar.getLunar()
        ec = lunar.getEightChar()

        lines = [
            f"대상 날짜: {target_year}년 {target_month}월 {target_day}일",
            f"연간지: {ec.getYear()}",
            f"월간지: {ec.getMonth()}",
            f"일간지: {ec.getDay()}",
        ]
        if target_hour is not None:
            shi_chen = _hour_to_shi_chen(target_hour)
            lines.append(f"대상 시간: {target_hour}시 ({shi_chen})")
            lines.append(f"시간지: {ec.getTime()}")

        return "\n".join(lines)

    def _get_all_hours_info(
        self, target_year: int, target_month: int, target_day: int
    ) -> str:
        """Get Gan-Zhi info for all 12 shi-chen of a target date."""
        solar_mid = Solar(target_year, target_month, target_day, 12, 0, 0)
        lunar_mid = solar_mid.getLunar()
        ec_mid = lunar_mid.getEightChar()

        lines = [
            f"대상 날짜: {target_year}년 {target_month}월 {target_day}일",
            f"일간지: {ec_mid.getDay()}",
            "",
            "## 12시진 간지",
        ]

        hours_info = [
            (0, "자시(子時) 23:00-01:00"),
            (2, "축시(丑時) 01:00-03:00"),
            (4, "인시(寅時) 03:00-05:00"),
            (6, "묘시(卯時) 05:00-07:00"),
            (8, "진시(辰時) 07:00-09:00"),
            (10, "사시(巳時) 09:00-11:00"),
            (12, "오시(午時) 11:00-13:00"),
            (14, "미시(未時) 13:00-15:00"),
            (16, "신시(申時) 15:00-17:00"),
            (18, "유시(酉時) 17:00-19:00"),
            (20, "술시(戌時) 19:00-21:00"),
            (22, "해시(亥時) 21:00-23:00"),
        ]

        for hour, name in hours_info:
            solar = Solar(target_year, target_month, target_day, hour, 0, 0)
            lunar = solar.getLunar()
            ec = lunar.getEightChar()
            lines.append(f"- {name}: {ec.getTime()}")

        return "\n".join(lines)

    async def timing_now(
        self,
        birth: BirthInput,
        target_year: int,
        target_month: int,
        target_day: int,
        target_hour: int,
        *,
        language: str = "ko",
    ) -> tuple[SajuData, str, str]:
        """Generate real-time fortune for current hour."""
        saju = self._calculate_person(birth)
        shi_chen = _hour_to_shi_chen(target_hour)
        target_dt_str = f"{target_year}-{target_month:02d}-{target_day:02d} {target_hour:02d}:00 ({shi_chen})"

        cache_key = CacheService.make_key(
            "timing_now",
            y=saju.solar_year, m=saju.solar_month, d=saju.solar_day,
            h=saju.solar_hour, g=birth.gender.value,
            ty=target_year, tm=target_month, td=target_day, th=target_hour,
            lang=language,
        )

        cached = await self._cache.get(cache_key)
        if cached:
            return saju, cached, target_dt_str

        time_info = self._get_target_time_info(
            target_year, target_month, target_day, target_hour,
        )
        prompt = TIMING_NOW_PROMPT.format(
            saju_data=format_saju_for_prompt(saju),
            target_time=time_info,
        )
        interpretation = await self._llm.generate(prompt, language=language)

        await self._cache.set(cache_key, interpretation, ttl=settings.cache_ttl_interpretation)
        return saju, interpretation, target_dt_str

    async def timing_best_hours(
        self,
        birth: BirthInput,
        target_year: int,
        target_month: int,
        target_day: int,
        *,
        language: str = "ko",
    ) -> tuple[SajuData, str, str]:
        """Generate best hours analysis for a target date."""
        saju = self._calculate_person(birth)
        target_date_str = f"{target_year}-{target_month:02d}-{target_day:02d}"

        cache_key = CacheService.make_key(
            "timing_best_hours",
            y=saju.solar_year, m=saju.solar_month, d=saju.solar_day,
            h=saju.solar_hour, g=birth.gender.value,
            ty=target_year, tm=target_month, td=target_day,
            lang=language,
        )

        cached = await self._cache.get(cache_key)
        if cached:
            return saju, cached, target_date_str

        hours_info = self._get_all_hours_info(target_year, target_month, target_day)
        prompt = TIMING_BEST_HOURS_PROMPT.format(
            saju_data=format_saju_for_prompt(saju),
            target_time=hours_info,
        )
        interpretation = await self._llm.generate(prompt, language=language)

        await self._cache.set(cache_key, interpretation, ttl=settings.cache_ttl_fortune)
        return saju, interpretation, target_date_str

    async def timing_dday(
        self,
        birth: BirthInput,
        target_year: int,
        target_month: int,
        target_day: int,
        *,
        language: str = "ko",
    ) -> tuple[SajuData, str, str]:
        """Generate D-day fortune for a specific date."""
        saju = self._calculate_person(birth)
        target_date_str = f"{target_year}-{target_month:02d}-{target_day:02d}"

        cache_key = CacheService.make_key(
            "timing_dday",
            y=saju.solar_year, m=saju.solar_month, d=saju.solar_day,
            h=saju.solar_hour, g=birth.gender.value,
            ty=target_year, tm=target_month, td=target_day,
            lang=language,
        )

        cached = await self._cache.get(cache_key)
        if cached:
            return saju, cached, target_date_str

        time_info = self._get_target_time_info(target_year, target_month, target_day)
        prompt = TIMING_DDAY_PROMPT.format(
            saju_data=format_saju_for_prompt(saju),
            target_time=time_info,
        )
        interpretation = await self._llm.generate(prompt, language=language)

        await self._cache.set(cache_key, interpretation, ttl=settings.cache_ttl_fortune)
        return saju, interpretation, target_date_str


_SHI_CHEN_NAMES = (
    "자시(子)", "축시(丑)", "인시(寅)", "묘시(卯)",
    "진시(辰)", "사시(巳)", "오시(午)", "미시(未)",
    "신시(申)", "유시(酉)", "술시(戌)", "해시(亥)",
)


def _hour_to_shi_chen(hour: int) -> str:
    """Convert a 24-hour value to its shi-chen name."""
    # 23-01: 자, 01-03: 축, ..., 21-23: 해
    index = ((hour + 1) % 24) // 2
    return _SHI_CHEN_NAMES[index]
