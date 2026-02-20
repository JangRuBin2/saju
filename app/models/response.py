from __future__ import annotations

from pydantic import BaseModel


class PillarResponse(BaseModel):
    gan: str
    zhi: str
    gan_kor: str
    zhi_kor: str
    wu_xing: str
    na_yin: str
    shi_shen_gan: str
    shi_shen_zhi: list[str]
    di_shi: str
    hide_gan: list[str]


class DaYunResponse(BaseModel):
    start_age: int
    start_year: int
    gan_zhi: str


class SajuCalculateResponse(BaseModel):
    solar_date: str
    lunar_date: str
    is_leap_month: bool
    year_pillar: PillarResponse
    month_pillar: PillarResponse
    day_pillar: PillarResponse
    time_pillar: PillarResponse | None
    day_master: str
    day_master_kor: str
    day_master_element: str
    day_master_yin_yang: str
    tai_yuan: str
    tai_yuan_na_yin: str
    ming_gong: str
    ming_gong_na_yin: str
    shen_gong: str
    shen_gong_na_yin: str
    da_yun_start_age: int
    da_yun_list: list[DaYunResponse]
    element_counts: dict[str, int]
    used_night_zi: bool
    used_true_solar_time: bool
    birth_time_unknown: bool


class SajuReadingResponse(BaseModel):
    calculation: SajuCalculateResponse
    interpretation: str


class CompatibilityResponse(BaseModel):
    person1: SajuCalculateResponse
    person2: SajuCalculateResponse
    interpretation: str


class FortuneResponse(BaseModel):
    calculation: SajuCalculateResponse
    interpretation: str
    target_date: str


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"


class ErrorResponse(BaseModel):
    error: str
    message: str
