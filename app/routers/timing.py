from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends

from app.dependencies import get_fortune_service, get_saju_service
from app.llm.parser import parse_interpretation
from app.models.request import TimingRequest
from app.models.response import SajuCalculateResponse, TimingResponse
from app.services.fortune_service import FortuneService
from app.services.saju_service import SajuService

router = APIRouter(prefix="/api/v1/timing", tags=["timing"])


@router.post("/now", response_model=TimingResponse)
async def timing_now(
    request: TimingRequest,
    service: FortuneService = Depends(get_fortune_service),
    saju_service: SajuService = Depends(get_saju_service),
) -> TimingResponse:
    """Real-time fortune for the current hour."""
    now = datetime.now()
    target_year = request.target_year or now.year
    target_month = request.target_month or now.month
    target_day = request.target_day or now.day
    target_hour = request.target_hour if request.target_hour is not None else now.hour

    saju, interpretation, target_dt = await service.timing_now(
        request.birth, target_year, target_month, target_day, target_hour,
        language=request.language,
    )
    return TimingResponse(
        calculation=SajuCalculateResponse(**saju_service.saju_to_dict(saju)),
        interpretation=parse_interpretation(interpretation),
        target_datetime=target_dt,
    )


@router.post("/best-hours", response_model=TimingResponse)
async def timing_best_hours(
    request: TimingRequest,
    service: FortuneService = Depends(get_fortune_service),
    saju_service: SajuService = Depends(get_saju_service),
) -> TimingResponse:
    """Best hours analysis for today (or target date)."""
    now = datetime.now()
    target_year = request.target_year or now.year
    target_month = request.target_month or now.month
    target_day = request.target_day or now.day

    saju, interpretation, target_date = await service.timing_best_hours(
        request.birth, target_year, target_month, target_day,
        language=request.language,
    )
    return TimingResponse(
        calculation=SajuCalculateResponse(**saju_service.saju_to_dict(saju)),
        interpretation=parse_interpretation(interpretation),
        target_datetime=target_date,
    )


@router.post("/dday", response_model=TimingResponse)
async def timing_dday(
    request: TimingRequest,
    service: FortuneService = Depends(get_fortune_service),
    saju_service: SajuService = Depends(get_saju_service),
) -> TimingResponse:
    """D-day fortune for a specific date."""
    now = datetime.now()
    target_year = request.target_year or now.year
    target_month = request.target_month or now.month
    target_day = request.target_day or now.day

    saju, interpretation, target_date = await service.timing_dday(
        request.birth, target_year, target_month, target_day,
        language=request.language,
    )
    return TimingResponse(
        calculation=SajuCalculateResponse(**saju_service.saju_to_dict(saju)),
        interpretation=parse_interpretation(interpretation),
        target_datetime=target_date,
    )
