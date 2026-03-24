from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field

from app.models.common import (
    CalendarType,
    CareerConcernType,
    Gender,
    MarriageConcernType,
    PetSize,
)


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
    counselor_id: str | None = Field(None, description="Virtual counselor ID (e.g. 'master-yoon')")
    custom_system_prompt: str | None = Field(None, description="Custom system prompt from admin DB (overrides default)")


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


# --- Pet fortune ---

class PetBirthInput(BaseModel):
    name: str | None = Field(None, description="Pet name")
    year: int = Field(..., ge=1990, le=2030, description="Pet birth year")
    month: int | None = Field(None, ge=1, le=12, description="Pet birth month (None if unknown)")
    day: int | None = Field(None, ge=1, le=31, description="Pet birth day (None if unknown)")
    hour: int | None = Field(None, ge=0, le=23, description="Pet birth hour (None if unknown)")
    gender: Gender
    breed: str | None = Field(None, description="Dog breed (e.g. 'poodle', 'golden_retriever')")
    size: PetSize | None = Field(None, description="Pet size category")


class PetReadingRequest(BaseModel):
    pet: PetBirthInput
    language: str = Field("ko", description="Response language")


class PetCompatibilityRequest(BaseModel):
    owner: BirthInput
    pet: PetBirthInput
    language: str = Field("ko", description="Response language")


class PetYearlyFortuneRequest(BaseModel):
    pet: PetBirthInput
    target_year: int | None = None
    language: str = Field("ko", description="Response language")


class PetAdoptionTimingRequest(BaseModel):
    owner: BirthInput
    target_year: int | None = None
    language: str = Field("ko", description="Response language")


# --- Career transition ---

class CareerInfo(BaseModel):
    current_industry: str | None = Field(None, description="Current industry (e.g. 'IT', 'finance')")
    current_role: str | None = Field(None, description="Current role/position")
    years_at_company: int | None = Field(None, ge=0, le=50, description="Years at current company")
    join_year: int | None = Field(None, ge=1970, le=2030, description="Year joined current company")
    total_experience: int | None = Field(None, ge=0, le=50, description="Total career years")
    concern_type: CareerConcernType | None = Field(None, description="Primary concern type")
    target_period: str | None = Field(None, description="Target period (e.g. '2026-H2')")


class CareerTransitionRequest(BaseModel):
    birth: BirthInput
    career_info: CareerInfo | None = None
    language: str = Field("ko", description="Response language")


class CareerStayOrGoRequest(BaseModel):
    birth: BirthInput
    career_info: CareerInfo | None = None
    language: str = Field("ko", description="Response language")


class CareerStartupRequest(BaseModel):
    birth: BirthInput
    career_info: CareerInfo | None = None
    target_industry: str | None = Field(None, description="Target startup industry")
    language: str = Field("ko", description="Response language")


class CareerBurnoutRequest(BaseModel):
    birth: BirthInput
    career_info: CareerInfo | None = None
    language: str = Field("ko", description="Response language")


# --- Marriage fortune ---

class RelationshipInfoInput(BaseModel):
    dating_start_year: int | None = Field(None, ge=2000, le=2030, description="Year dating started")
    dating_years: int | None = Field(None, ge=0, le=30, description="Years of dating")
    target_marriage_year: int | None = Field(None, ge=2024, le=2035, description="Target marriage year")
    concern_type: MarriageConcernType | None = Field(None, description="Primary concern")
    living_together: bool | None = Field(None, description="Currently living together")


class MarriageTimingRequest(BaseModel):
    person1: BirthInput
    person2: BirthInput
    relationship_info: RelationshipInfoInput | None = None
    language: str = Field("ko", description="Response language")


class MarriageLifeForecastRequest(BaseModel):
    person1: BirthInput
    person2: BirthInput
    marriage_year: int | None = Field(None, description="Planned marriage year")
    language: str = Field("ko", description="Response language")


class MarriageFinanceRequest(BaseModel):
    person1: BirthInput
    person2: BirthInput
    marriage_year: int | None = Field(None, description="Planned marriage year")
    language: str = Field("ko", description="Response language")


class MarriageAuspiciousDatesRequest(BaseModel):
    person1: BirthInput
    person2: BirthInput
    target_year: int | None = None
    target_months: list[int] | None = Field(None, description="Specific months to analyze")
    language: str = Field("ko", description="Response language")
