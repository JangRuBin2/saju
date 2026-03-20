from __future__ import annotations

import json

from fastapi import APIRouter, Depends, Request
from sse_starlette.sse import EventSourceResponse

from app.dependencies import get_saju_service
from app.llm.parser import parse_interpretation
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
    request_body: SajuReadingRequest,
    request: Request,
    service: SajuService = Depends(get_saju_service),
):
    """Full saju reading with LLM interpretation. Supports SSE streaming."""
    reading_type = getattr(request.state, "reading_type", "saju_reading")

    if request_body.stream:
        return await _streaming_reading(request_body, service, reading_type)

    saju, raw_text = await service.reading(
        request_body.birth, reading_type, language=request_body.language,
    )
    return SajuReadingResponse(
        calculation=SajuCalculateResponse(**service.saju_to_dict(saju)),
        interpretation=parse_interpretation(raw_text),
    )


async def _streaming_reading(
    request: SajuReadingRequest,
    service: SajuService,
    reading_type: str = "saju_reading",
) -> EventSourceResponse:
    saju, text_stream = await service.reading_stream(
        request.birth, reading_type, language=request.language,
    )

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
    request_body: SinsalRequest,
    request: Request,
    service: SajuService = Depends(get_saju_service),
) -> SajuReadingResponse:
    """Sinsal (신살) analysis."""
    reading_type = getattr(request.state, "reading_type", "sinsal")
    saju, raw_text = await service.reading(
        request_body.birth, reading_type, language=request_body.language,
    )
    return SajuReadingResponse(
        calculation=SajuCalculateResponse(**service.saju_to_dict(saju)),
        interpretation=parse_interpretation(raw_text),
    )
