from __future__ import annotations

import pytest

from app.engine.calculator import SajuCalculator
from app.middleware.error_handler import InvalidBirthDateError


@pytest.fixture
def calc() -> SajuCalculator:
    return SajuCalculator()


class TestSajuCalculator:
    """Test core saju calculation against known reference values."""

    def test_basic_calculation_solar(self, calc: SajuCalculator):
        """1990-05-15 14:30 male solar - cross-verify with known values."""
        result = calc.calculate(
            year=1990, month=5, day=15, hour=14, minute=30,
            gender_male=True, calendar_type="solar",
        )

        # Year pillar: 庚午
        assert result.year_pillar.gan == "庚"
        assert result.year_pillar.zhi == "午"

        # Month pillar: 辛巳
        assert result.month_pillar.gan == "辛"
        assert result.month_pillar.zhi == "巳"

        # Day pillar: 庚辰
        assert result.day_pillar.gan == "庚"
        assert result.day_pillar.zhi == "辰"

        # Time pillar: 癸未
        assert result.time_pillar is not None
        assert result.time_pillar.gan == "癸"
        assert result.time_pillar.zhi == "未"

        # Day master
        assert result.day_master == "庚"
        assert result.day_master_element == "金"
        assert result.day_master_yin_yang == "양"

    def test_birth_time_unknown(self, calc: SajuCalculator):
        """Time pillar should be None when hour is not provided."""
        result = calc.calculate(
            year=1990, month=5, day=15, hour=None,
            gender_male=True, calendar_type="solar",
        )
        assert result.time_pillar is None
        assert result.birth_time_unknown is True

    def test_lunar_calendar_input(self, calc: SajuCalculator):
        """Lunar date 1990-04-21 should convert to solar 1990-05-15."""
        result = calc.calculate(
            year=1990, month=4, day=21, hour=14, minute=30,
            gender_male=True, calendar_type="lunar",
        )
        assert result.solar_year == 1990
        assert result.solar_month == 5
        assert result.solar_day == 15

    def test_element_counts(self, calc: SajuCalculator):
        """Element counts should sum to 6 (3 stems + 3 branches) when time unknown."""
        result = calc.calculate(
            year=1990, month=5, day=15, hour=None,
            gender_male=True, calendar_type="solar",
        )
        total = sum(result.element_counts.values())
        assert total == 6  # 3 stems + 3 branches (no time pillar)

    def test_element_counts_with_time(self, calc: SajuCalculator):
        """Element counts should sum to 8 (4 stems + 4 branches) with time."""
        result = calc.calculate(
            year=1990, month=5, day=15, hour=14,
            gender_male=True, calendar_type="solar",
        )
        total = sum(result.element_counts.values())
        assert total == 8

    def test_da_yun_list(self, calc: SajuCalculator):
        """Da Yun list should contain major luck periods."""
        result = calc.calculate(
            year=1990, month=5, day=15, hour=14,
            gender_male=True, calendar_type="solar",
        )
        assert len(result.da_yun_list) > 0
        # First da yun for male 庚 (yang stem) should be forward
        assert result.da_yun_list[0].gan_zhi == "壬午"

    def test_female_calculation(self, calc: SajuCalculator):
        """Female calculation should produce valid results with different da yun direction."""
        result = calc.calculate(
            year=1990, month=5, day=15, hour=14,
            gender_male=False, calendar_type="solar",
        )
        assert result.day_master == "庚"
        assert len(result.da_yun_list) > 0
        # Female with yang stem -> reverse direction
        assert result.da_yun_list[0].gan_zhi == "庚辰"

    def test_night_zi_hour(self, calc: SajuCalculator):
        """Test night zi (23:00) with different sect settings."""
        # use_night_zi=True (sect=2): day pillar stays same
        result_night = calc.calculate(
            year=1990, month=5, day=15, hour=23,
            gender_male=True, calendar_type="solar", use_night_zi=True,
        )

        # use_night_zi=False (sect=1): day pillar advances
        result_normal = calc.calculate(
            year=1990, month=5, day=15, hour=23,
            gender_male=True, calendar_type="solar", use_night_zi=False,
        )

        # Day pillars should be different
        assert result_night.day_pillar.gan != result_normal.day_pillar.gan

    def test_invalid_date(self, calc: SajuCalculator):
        """Invalid date should raise InvalidBirthDateError."""
        with pytest.raises(InvalidBirthDateError):
            calc.calculate(
                year=1990, month=13, day=15, hour=14,
                gender_male=True, calendar_type="solar",
            )

    def test_korean_reading_in_pillars(self, calc: SajuCalculator):
        """Korean reading should be present in pillar info."""
        result = calc.calculate(
            year=1990, month=5, day=15, hour=14,
            gender_male=True, calendar_type="solar",
        )
        assert result.year_pillar.gan_kor == "경"
        assert result.year_pillar.zhi_kor == "오"
        assert result.day_master_kor == "경"

    def test_true_solar_time_default_false(self, calc: SajuCalculator):
        """By default, true solar time should not be used."""
        result = calc.calculate(
            year=1990, month=5, day=15, hour=14, minute=30,
            gender_male=True, calendar_type="solar",
        )
        assert result.used_true_solar_time is False

    def test_true_solar_time_changes_time_pillar(self, calc: SajuCalculator):
        """1997-01-05 09:05 with true solar time should shift to 08:33 (jin-shi).

        Without true solar time: 09:05 -> si-shi (巳時, 9-11)
        With true solar time: 08:33 -> jin-shi (辰時, 7-9)
        """
        result_normal = calc.calculate(
            year=1997, month=1, day=5, hour=9, minute=5,
            gender_male=True, calendar_type="solar",
            use_true_solar_time=False,
        )
        result_tst = calc.calculate(
            year=1997, month=1, day=5, hour=9, minute=5,
            gender_male=True, calendar_type="solar",
            use_true_solar_time=True,
        )

        # Time pillars should differ
        assert result_normal.time_pillar.zhi != result_tst.time_pillar.zhi
        assert result_tst.used_true_solar_time is True

    def test_true_solar_time_no_change_far_from_boundary(self, calc: SajuCalculator):
        """14:30 - 32min = 13:58, both in mi-shi (未時, 13-15). Pillars unchanged."""
        result_normal = calc.calculate(
            year=1990, month=5, day=15, hour=14, minute=30,
            gender_male=True, calendar_type="solar",
        )
        result_tst = calc.calculate(
            year=1990, month=5, day=15, hour=14, minute=30,
            gender_male=True, calendar_type="solar",
            use_true_solar_time=True,
        )

        # Same shi-chen, so time pillar should be the same
        assert result_normal.time_pillar.gan == result_tst.time_pillar.gan
        assert result_normal.time_pillar.zhi == result_tst.time_pillar.zhi
        assert result_tst.used_true_solar_time is True

    def test_extra_info_present(self, calc: SajuCalculator):
        """TaiYuan, MingGong, ShenGong should be present."""
        result = calc.calculate(
            year=1990, month=5, day=15, hour=14,
            gender_male=True, calendar_type="solar",
        )
        assert result.tai_yuan != ""
        assert result.ming_gong != ""
        assert result.shen_gong != ""
        assert result.tai_yuan_na_yin != ""
