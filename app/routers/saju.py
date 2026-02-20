from __future__ import annotations

import json

from fastapi import APIRouter, Depends
from sse_starlette.sse import EventSourceResponse

from app.dependencies import get_saju_service
from app.models.request import SajuCalculateRequest, SajuReadingRequest, SinsalRequest
from app.models.response import SajuCalculateResponse, SajuReadingResponse
from app.services.saju_service import SajuService

router = APIRouter(prefix="/api/v1/saju", tags=["saju"])


@router.post("/calculate", response_model=SajuCalculateResponse)
async def calculate(
    request: SajuCalculateRequest,
    service: SajuService = Depends(get_saju_service),
) -> SajuCalculateResponse:
    """Calculate saju (four pillars) without LLM interpretation."""
    saju = service.calculate(request.birth)
    return SajuCalculateResponse(**service.saju_to_dict(saju))


@router.post("/reading")
async def reading(
    request: SajuReadingRequest,
    service: SajuService = Depends(get_saju_service),
):
    """Full saju reading with LLM interpretation. Supports SSE streaming."""
    if request.stream:
        return await _streaming_reading(request, service)

    saju, interpretation = await service.reading(request.birth)
    return SajuReadingResponse(
        calculation=SajuCalculateResponse(**service.saju_to_dict(saju)),
        interpretation=interpretation,
    )


async def _streaming_reading(
    request: SajuReadingRequest,
    service: SajuService,
) -> EventSourceResponse:
    saju, text_stream = await service.reading_stream(request.birth)

    async def event_generator():
        # First event: calculation result
        calc_data = service.saju_to_dict(saju)
        yield {
            "event": "calculation",
            "data": json.dumps(calc_data, ensure_ascii=False),
        }

        # Stream interpretation chunks
        async for chunk in text_stream:
            yield {
                "event": "interpretation",
                "data": chunk,
            }

        yield {"event": "done", "data": ""}

    return EventSourceResponse(event_generator())


@router.post("/sinsal", response_model=SajuReadingResponse)
async def sinsal(
    request: SinsalRequest,
    service: SajuService = Depends(get_saju_service),
) -> SajuReadingResponse:
    """Sinsal (신살) analysis."""
    saju, interpretation = await service.reading(request.birth)
    return SajuReadingResponse(
        calculation=SajuCalculateResponse(**service.saju_to_dict(saju)),
        interpretation=interpretation,
    )
