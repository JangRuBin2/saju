from __future__ import annotations

from fastapi import APIRouter, Depends

from app.config import settings
from app.dependencies import get_saju_service
from app.llm.formatter import format_saju_for_prompt
from app.llm.prompts.career import (
    CAREER_BURNOUT_PROMPT,
    CAREER_STARTUP_PROMPT,
    CAREER_STAY_OR_GO_PROMPT,
    CAREER_TRANSITION_PROMPT,
)
from app.models.request import (
    CareerBurnoutRequest,
    CareerInfo,
    CareerStartupRequest,
    CareerStayOrGoRequest,
    CareerTransitionRequest,
)
from app.models.response import SajuCalculateResponse, SajuReadingResponse
from app.services.cache_service import CacheService
from app.services.saju_service import SajuService

router = APIRouter(prefix="/api/v1/career", tags=["career"])


def _format_career_info(info: CareerInfo | None) -> str:
    """Format career metadata for prompt context."""
    if info is None:
        return "직장/경력 정보: 제공되지 않음"
    lines = []
    if info.current_industry:
        lines.append(f"현재 업종: {info.current_industry}")
    if info.current_role:
        lines.append(f"현재 직무: {info.current_role}")
    if info.years_at_company is not None:
        lines.append(f"현 직장 근속 연수: {info.years_at_company}년")
    if info.join_year is not None:
        lines.append(f"입사 연도: {info.join_year}년")
    if info.total_experience is not None:
        lines.append(f"총 경력: {info.total_experience}년")
    if info.concern_type:
        concern_labels = {
            "timing": "이직 타이밍",
            "direction": "이직 방향",
            "promotion_vs_move": "승진 vs 이직",
            "startup": "창업",
            "burnout": "번아웃",
            "salary": "연봉",
        }
        lines.append(f"주요 고민: {concern_labels.get(info.concern_type.value, info.concern_type.value)}")
    if info.target_period:
        lines.append(f"희망 이직 시기: {info.target_period}")
    return "\n".join(lines) if lines else "직장/경력 정보: 제공되지 않음"


async def _career_reading(
    service: SajuService,
    request_body: CareerTransitionRequest | CareerStayOrGoRequest | CareerStartupRequest | CareerBurnoutRequest,
    prompt_template: str,
    reading_type: str,
    cache_prefix: str,
    career_info: CareerInfo | None = None,
    extra_prompt_kwargs: dict[str, str] | None = None,
) -> SajuReadingResponse:
    """Shared logic for all career reading endpoints."""
    saju = service.calculate(request_body.birth)

    cache_key = CacheService.make_key(
        cache_prefix,
        y=saju.solar_year, m=saju.solar_month, d=saju.solar_day,
        h=saju.solar_hour, g=request_body.birth.gender.value,
        rt=reading_type, lang=request_body.language,
    )
    cached = await service._cache.get(cache_key)
    if cached:
        return SajuReadingResponse(
            calculation=SajuCalculateResponse(**service.saju_to_dict(saju)),
            interpretation=cached,
        )

    format_args: dict[str, str] = {
        "saju_data": format_saju_for_prompt(saju),
        "career_info": _format_career_info(career_info),
    }
    if extra_prompt_kwargs:
        format_args = {**format_args, **extra_prompt_kwargs}
    prompt = prompt_template.format(**format_args)

    interpretation = await service._llm.generate(
        prompt, reading_type=reading_type, language=request_body.language,
    )
    await service._cache.set(cache_key, interpretation, ttl=settings.cache_ttl_interpretation)

    return SajuReadingResponse(
        calculation=SajuCalculateResponse(**service.saju_to_dict(saju)),
        interpretation=interpretation,
    )


@router.post("/transition", response_model=SajuReadingResponse)
async def career_transition(
    request_body: CareerTransitionRequest,
    service: SajuService = Depends(get_saju_service),
) -> SajuReadingResponse:
    """Analyze career transition timing and direction."""
    return await _career_reading(
        service, request_body,
        prompt_template=CAREER_TRANSITION_PROMPT,
        reading_type="career_transition",
        cache_prefix="career_transition",
        career_info=request_body.career_info,
    )


@router.post("/stay-or-go", response_model=SajuReadingResponse)
async def career_stay_or_go(
    request_body: CareerStayOrGoRequest,
    service: SajuService = Depends(get_saju_service),
) -> SajuReadingResponse:
    """Analyze whether to stay at current job or move."""
    return await _career_reading(
        service, request_body,
        prompt_template=CAREER_STAY_OR_GO_PROMPT,
        reading_type="career_stay_or_go",
        cache_prefix="career_stay_or_go",
        career_info=request_body.career_info,
    )


@router.post("/startup", response_model=SajuReadingResponse)
async def career_startup(
    request_body: CareerStartupRequest,
    service: SajuService = Depends(get_saju_service),
) -> SajuReadingResponse:
    """Analyze startup aptitude and timing."""
    career_info = request_body.career_info
    extra_kwargs = {}
    if request_body.target_industry:
        extra_kwargs["target_industry"] = request_body.target_industry
    return await _career_reading(
        service, request_body,
        prompt_template=CAREER_STARTUP_PROMPT,
        reading_type="career_startup",
        cache_prefix="career_startup",
        career_info=career_info,
    )


@router.post("/burnout", response_model=SajuReadingResponse)
async def career_burnout(
    request_body: CareerBurnoutRequest,
    service: SajuService = Depends(get_saju_service),
) -> SajuReadingResponse:
    """Analyze burnout recovery timing and direction."""
    return await _career_reading(
        service, request_body,
        prompt_template=CAREER_BURNOUT_PROMPT,
        reading_type="career_burnout",
        cache_prefix="career_burnout",
        career_info=request_body.career_info,
    )
