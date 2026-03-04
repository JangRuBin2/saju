from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field

from app.models.common import CalendarType, Gender


class RelationshipType(str, Enum):
    LOVER = "lover"
    BOSS = "boss"
    CHILD = "child"
    FRIEND = "friend"


class SituationType(str, Enum):
    CAREER_CHANGE = "career_change"
    WEALTH_FLOW = "wealth_flow"
    HIDDEN_TALENT = "hidden_talent"
    PAST_LIFE = "past_life"


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
    use_true_solar_time: bool = Field(False, description="Use true solar time (진태양시) correction")


class SajuCalculateRequest(BaseModel):
    birth: BirthInput


class SajuReadingRequest(BaseModel):
    birth: BirthInput
    stream: bool = Field(False, description="Enable SSE streaming")
    language: str = Field("ko", description="Response language (e.g. 'ko', 'en', 'ja', 'English')")


class SinsalRequest(BaseModel):
    birth: BirthInput
    language: str = Field("ko", description="Response language (e.g. 'ko', 'en', 'ja', 'English')")


class CompatibilityRequest(BaseModel):
    person1: BirthInput
    person2: BirthInput
    language: str = Field("ko", description="Response language (e.g. 'ko', 'en', 'ja', 'English')")


class FortuneRequest(BaseModel):
    birth: BirthInput
    target_year: int | None = None
    target_month: int | None = None
    target_day: int | None = None
    language: str = Field("ko", description="Response language (e.g. 'ko', 'en', 'ja', 'English')")


class CelebrityCompatibilityRequest(BaseModel):
    birth: BirthInput
    celebrity_id: str = Field(..., description="Celebrity unique ID (e.g. 'karina-aespa')")
    language: str = Field("ko", description="Response language (e.g. 'ko', 'en', 'ja', 'English')")


class RelationshipReadingRequest(BaseModel):
    target_birth: BirthInput
    relationship_type: RelationshipType
    language: str = Field("ko", description="Response language (e.g. 'ko', 'en', 'ja', 'English')")


class SituationReadingRequest(BaseModel):
    birth: BirthInput
    situation_type: SituationType
    language: str = Field("ko", description="Response language (e.g. 'ko', 'en', 'ja', 'English')")


class TimingRequest(BaseModel):
    birth: BirthInput
    target_year: int | None = None
    target_month: int | None = None
    target_day: int | None = None
    target_hour: int | None = Field(None, ge=0, le=23, description="Target hour (0-23)")
    language: str = Field("ko", description="Response language (e.g. 'ko', 'en', 'ja', 'English')")
