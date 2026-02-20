from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PillarInfo:
    """Single pillar (column) of the four pillars."""

    gan: str  # Heavenly Stem (hanja)
    zhi: str  # Earthly Branch (hanja)
    gan_kor: str  # Korean reading
    zhi_kor: str  # Korean reading
    wu_xing: str  # Five elements pair (e.g. "金火")
    na_yin: str  # Na-yin (납음)
    shi_shen_gan: str  # Ten god of the stem
    shi_shen_zhi: list[str]  # Ten gods of the branch (hidden stems)
    di_shi: str  # Twelve fate position (12운성)
    hide_gan: list[str]  # Hidden stems in branch (지장간)


@dataclass(frozen=True)
class DaYunInfo:
    """Single major luck period (대운)."""

    start_age: int
    start_year: int
    gan_zhi: str  # e.g. "壬午"


@dataclass(frozen=True)
class SajuData:
    """Complete saju calculation result."""

    # Birth info
    solar_year: int
    solar_month: int
    solar_day: int
    solar_hour: int | None
    solar_minute: int | None
    lunar_year: int
    lunar_month: int
    lunar_day: int
    is_leap_month: bool

    # Four pillars
    year_pillar: PillarInfo
    month_pillar: PillarInfo
    day_pillar: PillarInfo
    time_pillar: PillarInfo | None  # None when birth time unknown

    # Day master
    day_master: str  # Day stem (일간) - hanja
    day_master_kor: str
    day_master_element: str  # Element of day master
    day_master_yin_yang: str  # 음/양

    # Extra
    tai_yuan: str  # Conception pillar (태원)
    tai_yuan_na_yin: str
    ming_gong: str  # Destiny palace (명궁)
    ming_gong_na_yin: str
    shen_gong: str  # Body palace (신궁)
    shen_gong_na_yin: str

    # Major luck periods (대운)
    da_yun_start_age: int
    da_yun_list: list[DaYunInfo]

    # Five element counts
    element_counts: dict[str, int]

    # Options used
    used_night_zi: bool
    used_true_solar_time: bool
    birth_time_unknown: bool
