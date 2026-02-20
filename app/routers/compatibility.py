from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies import get_compatibility_service, get_saju_service
from app.models.request import CompatibilityRequest
from app.models.response import CompatibilityResponse, SajuCalculateResponse
from app.services.compatibility_service import CompatibilityService
from app.services.saju_service import SajuService

router = APIRouter(prefix="/api/v1/compatibility", tags=["compatibility"])


@router.post("/analyze", response_model=CompatibilityResponse)
async def analyze(
    request: CompatibilityRequest,
    service: CompatibilityService = Depends(get_compatibility_service),
    saju_service: SajuService = Depends(get_saju_service),
) -> CompatibilityResponse:
    """Analyze compatibility between two people."""
    saju1, saju2, interpretation = await service.analyze(request.person1, request.person2)
    return CompatibilityResponse(
        person1=SajuCalculateResponse(**saju_service.saju_to_dict(saju1)),
        person2=SajuCalculateResponse(**saju_service.saju_to_dict(saju2)),
        interpretation=interpretation,
    )
