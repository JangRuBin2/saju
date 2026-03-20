from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends

from app.dependencies import get_fortune_service, get_saju_service
from app.llm.parser import parse_interpretation
from app.models.request import FortuneRequest
from app.models.response import FortuneResponse, SajuCalculateResponse
from app.services.fortune_service import FortuneService
from app.services.saju_service import SajuService

router = APIRouter(prefix="/api/v1/fortune", tags=["fortune"])


@router.post("/monthly", response_model=FortuneResponse)
async def monthly_fortune(
    request: FortuneRequest,
    service: FortuneService = Depends(get_fortune_service),
    saju_service: SajuService = Depends(get_saju_service),
) -> FortuneResponse:
    """Monthly fortune analysis."""
    today = date.today()
    target_year = request.target_year or today.year
    target_month = request.target_month or today.month

    saju, raw_text, target_date = await service.monthly(
        request.birth, target_year, target_month, language=request.language,
    )
    return FortuneResponse(
        calculation=SajuCalculateResponse(**saju_service.saju_to_dict(saju)),
        interpretation=parse_interpretation(raw_text),
        target_date=target_date,
    )


@router.post("/daily", response_model=FortuneResponse)
async def daily_fortune(
    request: FortuneRequest,
    service: FortuneService = Depends(get_fortune_service),
    saju_service: SajuService = Depends(get_saju_service),
) -> FortuneResponse:
    """Daily fortune analysis."""
    today = date.today()
    target_year = request.target_year or today.year
    target_month = request.target_month or today.month
    target_day = request.target_day or today.day

    saju, raw_text, target_date = await service.daily(
        request.birth, target_year, target_month, target_day, language=request.language,
    )
    return FortuneResponse(
        calculation=SajuCalculateResponse(**saju_service.saju_to_dict(saju)),
        interpretation=parse_interpretation(raw_text),
        target_date=target_date,
    )
