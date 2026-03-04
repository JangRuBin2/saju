from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies import get_saju_service
from app.models.request import RelationshipReadingRequest
from app.models.response import SajuCalculateResponse, SajuReadingResponse
from app.services.saju_service import SajuService

router = APIRouter(prefix="/api/v1/relationship", tags=["relationship"])


@router.post("/reading", response_model=SajuReadingResponse)
async def relationship_reading(
    request: RelationshipReadingRequest,
    service: SajuService = Depends(get_saju_service),
) -> SajuReadingResponse:
    """Analyze a person's saju from a relationship perspective."""
    reading_type = f"relationship_{request.relationship_type.value}"
    saju, interpretation = await service.reading(
        request.target_birth, reading_type, language=request.language,
    )
    return SajuReadingResponse(
        calculation=SajuCalculateResponse(**service.saju_to_dict(saju)),
        interpretation=interpretation,
    )
