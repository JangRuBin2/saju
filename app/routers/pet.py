from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends

from app.config import settings
from app.dependencies import get_compatibility_service, get_fortune_service, get_saju_service
from app.llm.formatter import format_saju_for_prompt
from app.llm.parser import parse_interpretation
from app.llm.prompts.pet import (
    PET_ADOPTION_TIMING_PROMPT,
    PET_COMPATIBILITY_PROMPT,
    PET_READING_PROMPT,
    PET_YEARLY_FORTUNE_PROMPT,
)
from app.models.request import (
    BirthInput,
    PetAdoptionTimingRequest,
    PetBirthInput,
    PetCompatibilityRequest,
    PetReadingRequest,
    PetYearlyFortuneRequest,
)
from app.models.response import (
    PetCompatibilityResponse,
    PetReadingResponse,
    SajuCalculateResponse,
    SajuReadingResponse,
)
from app.services.cache_service import CacheService
from app.services.compatibility_service import CompatibilityService
from app.services.fortune_service import FortuneService
from app.services.saju_service import SajuService

router = APIRouter(prefix="/api/v1/pet", tags=["pet"])


def _pet_to_birth_input(pet: PetBirthInput) -> BirthInput:
    """Convert PetBirthInput to BirthInput for engine calculation."""
    return BirthInput(
        year=pet.year,
        month=pet.month or 6,
        day=pet.day or 15,
        hour=pet.hour,
        gender=pet.gender,
    )


def _format_pet_info(pet: PetBirthInput) -> str:
    """Format pet metadata for prompt context."""
    lines = []
    if pet.name:
        lines.append(f"이름: {pet.name}")
    lines.append(f"출생 연도: {pet.year}년")
    if pet.month:
        lines.append(f"출생 월: {pet.month}월")
    if pet.day:
        lines.append(f"출생 일: {pet.day}일")
    if pet.hour is not None:
        lines.append(f"출생 시: {pet.hour}시")
    lines.append(f"성별: {'수컷' if pet.gender == 'male' else '암컷'}")
    if pet.breed:
        lines.append(f"견종: {pet.breed}")
    if pet.size:
        lines.append(f"크기: {pet.size.value}")

    known_count = sum([
        True,
        pet.month is not None,
        pet.day is not None,
        pet.hour is not None,
    ])
    lines.append(f"알려진 주(柱) 수: {known_count}주")
    return "\n".join(lines)


def _count_pillars(pet: PetBirthInput) -> int:
    """Count how many pillars can be calculated."""
    count = 1  # year pillar always available
    if pet.month is not None:
        count += 1
    if pet.day is not None:
        count += 1
    if pet.hour is not None:
        count += 1
    return count


@router.post("/reading", response_model=PetReadingResponse)
async def pet_reading(
    request_body: PetReadingRequest,
    service: SajuService = Depends(get_saju_service),
) -> PetReadingResponse:
    """Analyze a pet's innate temperament and tendencies based on saju."""
    birth = _pet_to_birth_input(request_body.pet)
    pet_info = _format_pet_info(request_body.pet)

    saju = service.calculate(birth)

    cache_key = CacheService.make_key(
        "pet_reading",
        y=birth.year, m=birth.month, d=birth.day, h=birth.hour,
        g=birth.gender.value, lang=request_body.language,
    )
    cached = await service._cache.get(cache_key)
    if cached:
        raw_text = cached
    else:
        prompt = PET_READING_PROMPT.format(
            saju_data=format_saju_for_prompt(saju),
            pet_info=pet_info,
        )
        raw_text = await service._llm.generate(
            prompt, reading_type="pet_reading", language=request_body.language,
        )
        await service._cache.set(cache_key, raw_text, ttl=settings.cache_ttl_interpretation)

    return PetReadingResponse(
        calculation=SajuCalculateResponse(**service.saju_to_dict(saju)),
        interpretation=parse_interpretation(raw_text),
        pillars_used=_count_pillars(request_body.pet),
    )


@router.post("/compatibility", response_model=PetCompatibilityResponse)
async def pet_compatibility(
    request_body: PetCompatibilityRequest,
    compat_service: CompatibilityService = Depends(get_compatibility_service),
    saju_service: SajuService = Depends(get_saju_service),
) -> PetCompatibilityResponse:
    """Analyze compatibility between owner and pet."""
    pet_birth = _pet_to_birth_input(request_body.pet)
    pet_info = _format_pet_info(request_body.pet)

    saju1, saju2, raw_text = await compat_service.analyze(
        request_body.owner,
        pet_birth,
        reading_type="pet_compatibility",
        prompt_template=PET_COMPATIBILITY_PROMPT,
        prompt_kwargs={"pet_info": pet_info},
        language=request_body.language,
    )

    return PetCompatibilityResponse(
        owner=SajuCalculateResponse(**saju_service.saju_to_dict(saju1)),
        pet=SajuCalculateResponse(**saju_service.saju_to_dict(saju2)),
        interpretation=parse_interpretation(raw_text),
        pillars_used=_count_pillars(request_body.pet),
    )


@router.post("/fortune/yearly", response_model=PetReadingResponse)
async def pet_yearly_fortune(
    request_body: PetYearlyFortuneRequest,
    service: SajuService = Depends(get_saju_service),
    fortune_service: FortuneService = Depends(get_fortune_service),
) -> PetReadingResponse:
    """Analyze pet's yearly fortune."""
    birth = _pet_to_birth_input(request_body.pet)
    pet_info = _format_pet_info(request_body.pet)
    target_year = request_body.target_year or date.today().year

    saju = service.calculate(birth)
    period_info = fortune_service._get_target_period_info(target_year, 6)

    cache_key = CacheService.make_key(
        "pet_yearly",
        y=birth.year, m=birth.month, d=birth.day, h=birth.hour,
        g=birth.gender.value, ty=target_year, lang=request_body.language,
    )
    cached = await service._cache.get(cache_key)
    if cached:
        raw_text = cached
    else:
        prompt = PET_YEARLY_FORTUNE_PROMPT.format(
            saju_data=format_saju_for_prompt(saju),
            pet_info=pet_info,
            target_period=period_info,
        )
        raw_text = await service._llm.generate(
            prompt, reading_type="pet_yearly_fortune", language=request_body.language,
        )
        await service._cache.set(cache_key, raw_text, ttl=settings.cache_ttl_fortune)

    return PetReadingResponse(
        calculation=SajuCalculateResponse(**service.saju_to_dict(saju)),
        interpretation=parse_interpretation(raw_text),
        pillars_used=_count_pillars(request_body.pet),
    )


@router.post("/adoption-timing", response_model=SajuReadingResponse)
async def pet_adoption_timing(
    request_body: PetAdoptionTimingRequest,
    service: SajuService = Depends(get_saju_service),
    fortune_service: FortuneService = Depends(get_fortune_service),
) -> SajuReadingResponse:
    """Analyze best timing for pet adoption based on owner's saju."""
    target_year = request_body.target_year or date.today().year

    saju = service.calculate(request_body.owner)
    period_info = fortune_service._get_target_period_info(target_year, 6)

    cache_key = CacheService.make_key(
        "pet_adoption",
        y=request_body.owner.year, m=request_body.owner.month,
        d=request_body.owner.day, h=request_body.owner.hour,
        g=request_body.owner.gender.value, ty=target_year,
        lang=request_body.language,
    )
    cached = await service._cache.get(cache_key)
    if cached:
        raw_text = cached
    else:
        prompt = PET_ADOPTION_TIMING_PROMPT.format(
            saju_data=format_saju_for_prompt(saju),
            target_period=period_info,
        )
        raw_text = await service._llm.generate(
            prompt, reading_type="pet_adoption_timing", language=request_body.language,
        )
        await service._cache.set(cache_key, raw_text, ttl=settings.cache_ttl_fortune)

    return SajuReadingResponse(
        calculation=SajuCalculateResponse(**service.saju_to_dict(saju)),
        interpretation=parse_interpretation(raw_text),
    )
