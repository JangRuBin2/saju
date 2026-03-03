from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.data.celebrities import search_celebrities
from app.dependencies import get_celebrity_service, get_saju_service
from app.llm.prompts.celebrity_compatibility import CELEBRITY_DISCLAIMER
from app.models.request import CelebrityCompatibilityRequest
from app.models.response import (
    CelebrityCompatibilityResponse,
    CelebrityInfo,
    CelebritySearchResponse,
    SajuCalculateResponse,
)
from app.services.celebrity_service import CelebrityService
from app.services.saju_service import SajuService

router = APIRouter(prefix="/api/v1/celebrity", tags=["celebrity"])


@router.get("/search", response_model=CelebritySearchResponse)
async def celebrity_search(
    q: str = Query(..., min_length=1, max_length=50, description="Search query"),
) -> CelebritySearchResponse:
    """Search celebrities by name (Korean/English) or group name."""
    results = search_celebrities(q)
    items = [
        CelebrityInfo(
            id=c.id,
            name_ko=c.name_ko,
            name_en=c.name_en,
            group=c.group,
        )
        for c in results
    ]
    return CelebritySearchResponse(results=items, count=len(items))


@router.post("/compatibility", response_model=CelebrityCompatibilityResponse)
async def celebrity_compatibility(
    request: CelebrityCompatibilityRequest,
    service: CelebrityService = Depends(get_celebrity_service),
    saju_service: SajuService = Depends(get_saju_service),
) -> CelebrityCompatibilityResponse:
    """Analyze saju compatibility between user and a celebrity."""
    user_saju, celeb_saju, celebrity, interpretation = (
        await service.analyze_compatibility(
            request.birth, request.celebrity_id, language=request.language,
        )
    )
    return CelebrityCompatibilityResponse(
        user=SajuCalculateResponse(**saju_service.saju_to_dict(user_saju)),
        celebrity=SajuCalculateResponse(**saju_service.saju_to_dict(celeb_saju)),
        celebrity_info=CelebrityInfo(
            id=celebrity.id,
            name_ko=celebrity.name_ko,
            name_en=celebrity.name_en,
            group=celebrity.group,
        ),
        interpretation=interpretation,
        disclaimer=CELEBRITY_DISCLAIMER,
    )
