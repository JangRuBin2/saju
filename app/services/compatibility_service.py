from __future__ import annotations

from app.config import settings
from app.engine.calculator import SajuCalculator
from app.engine.models import SajuData
from app.llm.client import LLMClient
from app.llm.formatter import format_saju_for_prompt
from app.llm.prompts.compatibility import COMPATIBILITY_PROMPT
from app.models.request import BirthInput
from app.services.cache_service import CacheService


class CompatibilityService:
    """Handles compatibility (궁합) analysis."""

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

    async def analyze(
        self,
        person1: BirthInput,
        person2: BirthInput,
        *,
        prompt_template: str | None = None,
        prompt_kwargs: dict[str, str] | None = None,
        language: str = "ko",
    ) -> tuple[SajuData, SajuData, str]:
        """Analyze compatibility between two people.

        Args:
            person1: First person's birth input.
            person2: Second person's birth input.
            prompt_template: Custom prompt template. Falls back to COMPATIBILITY_PROMPT.
            prompt_kwargs: Extra format kwargs merged into the prompt template.
            language: Response language code (e.g. 'ko', 'en', 'ja').
        """
        saju1 = self._calculate_person(person1)
        saju2 = self._calculate_person(person2)

        cache_key = CacheService.make_key(
            "compat",
            p1_y=saju1.solar_year, p1_m=saju1.solar_month, p1_d=saju1.solar_day,
            p1_h=saju1.solar_hour, p1_g=person1.gender.value,
            p2_y=saju2.solar_year, p2_m=saju2.solar_month, p2_d=saju2.solar_day,
            p2_h=saju2.solar_hour, p2_g=person2.gender.value,
            lang=language,
        )

        cached = await self._cache.get(cache_key)
        if cached:
            return saju1, saju2, cached

        template = prompt_template if prompt_template is not None else COMPATIBILITY_PROMPT
        format_args: dict[str, str] = {
            "person1_data": format_saju_for_prompt(saju1),
            "person2_data": format_saju_for_prompt(saju2),
        }
        if prompt_kwargs:
            format_args = {**format_args, **prompt_kwargs}
        prompt = template.format(**format_args)
        interpretation = await self._llm.generate(prompt, language=language)

        await self._cache.set(cache_key, interpretation, ttl=settings.cache_ttl_interpretation)
        return saju1, saju2, interpretation
