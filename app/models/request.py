from __future__ import annotations

from pydantic import BaseModel, Field

from app.models.common import CalendarType, Gender


class BirthInput(BaseModel):
    year: int = Field(..., ge=1900, le=2100, description="Birth year")
    month: int = Field(..., ge=1, le=12, description="Birth month")
    day: int = Field(..., ge=1, le=31, description="Birth day")
    hour: int | None = Field(None, ge=0, le=23, description="Birth hour (None if unknown)")
    minute: int | None = Field(None, ge=0, le=59, description="Birth minute")
    gender: Gender
    calendar_type: CalendarType = CalendarType.SOLAR
    is_leap_month: bool = Field(False, description="Leap month flag (lunar calendar only)")
    use_night_zi: bool = Field(True, description="Use night zi (야자시) approach")


class SajuCalculateRequest(BaseModel):
    birth: BirthInput


class SajuReadingRequest(BaseModel):
    birth: BirthInput
    stream: bool = Field(False, description="Enable SSE streaming")


class SinsalRequest(BaseModel):
    birth: BirthInput


class CompatibilityRequest(BaseModel):
    person1: BirthInput
    person2: BirthInput


class FortuneRequest(BaseModel):
    birth: BirthInput
    target_year: int | None = None
    target_month: int | None = None
    target_day: int | None = None
