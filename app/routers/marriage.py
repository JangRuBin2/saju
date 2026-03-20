from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends

from app.dependencies import get_compatibility_service, get_fortune_service, get_saju_service
from app.llm.parser import parse_interpretation
from app.llm.prompts.marriage import (
    MARRIAGE_AUSPICIOUS_DATES_PROMPT,
    MARRIAGE_FINANCE_PROMPT,
    MARRIAGE_LIFE_FORECAST_PROMPT,
    MARRIAGE_TIMING_PROMPT,
)
from app.models.request import (
    MarriageAuspiciousDatesRequest,
    MarriageFinanceRequest,
    MarriageLifeForecastRequest,
    MarriageTimingRequest,
    RelationshipInfoInput,
)
from app.models.response import MarriageTimingResponse, SajuCalculateResponse
from app.services.compatibility_service import CompatibilityService
from app.services.fortune_service import FortuneService
from app.services.saju_service import SajuService

router = APIRouter(prefix="/api/v1/marriage", tags=["marriage"])


def _format_relationship_info(info: RelationshipInfoInput | None, marriage_year: int | None = None) -> str:
    """Format relationship metadata for prompt context."""
    lines = []
    if info is not None:
        if info.dating_start_year:
            lines.append(f"교제 시작 연도: {info.dating_start_year}년")
        if info.dating_years is not None:
            lines.append(f"교제 기간: {info.dating_years}년")
        if info.target_marriage_year:
            lines.append(f"결혼 희망 연도: {info.target_marriage_year}년")
        if info.concern_type:
            concern_labels = {
                "when": "결혼 시기",
                "readiness": "결혼 준비도",
                "compatibility": "결혼 후 궁합",
                "family": "양가 관계",
                "finance": "결혼 후 재물운",
                "children": "자녀운",
            }
            lines.append(f"주요 고민: {concern_labels.get(info.concern_type.value, info.concern_type.value)}")
        if info.living_together is not None:
            lines.append(f"동거 여부: {'예' if info.living_together else '아니오'}")
    if marriage_year:
        lines.append(f"결혼 예정 연도: {marriage_year}년")
    return "\n".join(lines) if lines else "관계 정보: 제공되지 않음"


@router.post("/timing", response_model=MarriageTimingResponse)
async def marriage_timing(
    request_body: MarriageTimingRequest,
    compat_service: CompatibilityService = Depends(get_compatibility_service),
    saju_service: SajuService = Depends(get_saju_service),
) -> MarriageTimingResponse:
    """Analyze optimal marriage timing for a couple."""
    rel_info = _format_relationship_info(request_body.relationship_info)

    saju1, saju2, interpretation = await compat_service.analyze(
        request_body.person1,
        request_body.person2,
        reading_type="marriage_timing",
        prompt_template=MARRIAGE_TIMING_PROMPT,
        prompt_kwargs={"relationship_info": rel_info},
        language=request_body.language,
    )

    return MarriageTimingResponse(
        person1=SajuCalculateResponse(**saju_service.saju_to_dict(saju1)),
        person2=SajuCalculateResponse(**saju_service.saju_to_dict(saju2)),
        interpretation=parse_interpretation(interpretation),
    )


@router.post("/life-forecast", response_model=MarriageTimingResponse)
async def marriage_life_forecast(
    request_body: MarriageLifeForecastRequest,
    compat_service: CompatibilityService = Depends(get_compatibility_service),
    saju_service: SajuService = Depends(get_saju_service),
) -> MarriageTimingResponse:
    """Analyze post-marriage life compatibility in depth."""
    rel_info = _format_relationship_info(None, marriage_year=request_body.marriage_year)

    saju1, saju2, interpretation = await compat_service.analyze(
        request_body.person1,
        request_body.person2,
        reading_type="marriage_life_forecast",
        prompt_template=MARRIAGE_LIFE_FORECAST_PROMPT,
        prompt_kwargs={"relationship_info": rel_info},
        language=request_body.language,
    )

    return MarriageTimingResponse(
        person1=SajuCalculateResponse(**saju_service.saju_to_dict(saju1)),
        person2=SajuCalculateResponse(**saju_service.saju_to_dict(saju2)),
        interpretation=parse_interpretation(interpretation),
    )


@router.post("/finance", response_model=MarriageTimingResponse)
async def marriage_finance(
    request_body: MarriageFinanceRequest,
    compat_service: CompatibilityService = Depends(get_compatibility_service),
    saju_service: SajuService = Depends(get_saju_service),
) -> MarriageTimingResponse:
    """Analyze couple's financial fortune after marriage."""
    rel_info = _format_relationship_info(None, marriage_year=request_body.marriage_year)

    saju1, saju2, interpretation = await compat_service.analyze(
        request_body.person1,
        request_body.person2,
        reading_type="marriage_finance",
        prompt_template=MARRIAGE_FINANCE_PROMPT,
        prompt_kwargs={"relationship_info": rel_info},
        language=request_body.language,
    )

    return MarriageTimingResponse(
        person1=SajuCalculateResponse(**saju_service.saju_to_dict(saju1)),
        person2=SajuCalculateResponse(**saju_service.saju_to_dict(saju2)),
        interpretation=parse_interpretation(interpretation),
    )


@router.post("/auspicious-dates", response_model=MarriageTimingResponse)
async def marriage_auspicious_dates(
    request_body: MarriageAuspiciousDatesRequest,
    compat_service: CompatibilityService = Depends(get_compatibility_service),
    saju_service: SajuService = Depends(get_saju_service),
    fortune_service: FortuneService = Depends(get_fortune_service),
) -> MarriageTimingResponse:
    """Analyze auspicious dates for marriage."""
    target_year = request_body.target_year or date.today().year
    period_info = fortune_service._get_target_period_info(target_year, 6)
    if request_body.target_months:
        months_str = ", ".join(str(m) for m in request_body.target_months)
        period_info += f"\n분석 대상 월: {months_str}월"

    saju1, saju2, interpretation = await compat_service.analyze(
        request_body.person1,
        request_body.person2,
        reading_type="marriage_auspicious_dates",
        prompt_template=MARRIAGE_AUSPICIOUS_DATES_PROMPT,
        prompt_kwargs={"target_period": period_info},
        language=request_body.language,
    )

    return MarriageTimingResponse(
        person1=SajuCalculateResponse(**saju_service.saju_to_dict(saju1)),
        person2=SajuCalculateResponse(**saju_service.saju_to_dict(saju2)),
        interpretation=parse_interpretation(interpretation),
    )
