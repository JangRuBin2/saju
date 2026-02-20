from __future__ import annotations

import pytest

from app.engine.true_solar_time import (
    adjust_for_true_solar_time,
    calculate_solar_time_offset_minutes,
)


class TestCalculateSolarTimeOffsetMinutes:
    """Test the offset calculation formula."""

    def test_seoul_longitude_offset(self):
        """Seoul (127.0E) should have ~32 min offset from KST (135E)."""
        offset = calculate_solar_time_offset_minutes(127.0)
        assert offset == pytest.approx(32.0)

    def test_kst_standard_longitude_zero_offset(self):
        """KST standard meridian (135E) should have 0 offset."""
        offset = calculate_solar_time_offset_minutes(135.0)
        assert offset == pytest.approx(0.0)

    def test_east_of_standard_negative_offset(self):
        """Longitude east of 135E should produce negative offset (add time)."""
        offset = calculate_solar_time_offset_minutes(137.0)
        assert offset == pytest.approx(-8.0)

    def test_incheon_longitude(self):
        """Incheon (~126.7E) should have slightly larger offset than Seoul."""
        offset = calculate_solar_time_offset_minutes(126.7)
        assert offset == pytest.approx(33.2)

    def test_busan_longitude(self):
        """Busan (~129.0E) should have smaller offset than Seoul."""
        offset = calculate_solar_time_offset_minutes(129.0)
        assert offset == pytest.approx(24.0)


class TestAdjustForTrueSolarTime:
    """Test time adjustment including boundary crossings."""

    def test_simple_subtraction_no_boundary(self):
        """09:32 - 32min = 09:00, no boundary crossing."""
        y, m, d, h, mi = adjust_for_true_solar_time(2000, 6, 15, 9, 32)
        assert (y, m, d, h, mi) == (2000, 6, 15, 9, 0)

    def test_minute_underflow_crosses_hour(self):
        """09:10 - 32min = 08:38, crosses hour boundary."""
        y, m, d, h, mi = adjust_for_true_solar_time(2000, 6, 15, 9, 10)
        assert (y, m, d, h, mi) == (2000, 6, 15, 8, 38)

    def test_crosses_midnight_backward(self):
        """00:20 - 32min = previous day 23:48."""
        y, m, d, h, mi = adjust_for_true_solar_time(2000, 6, 15, 0, 20)
        assert (y, m, d, h, mi) == (2000, 6, 14, 23, 48)

    def test_crosses_month_boundary(self):
        """March 1st 00:10 - 32min = Feb 28/29."""
        # 2000 is a leap year
        y, m, d, h, mi = adjust_for_true_solar_time(2000, 3, 1, 0, 10)
        assert (y, m, d, h, mi) == (2000, 2, 29, 23, 38)

        # 2001 is not a leap year
        y, m, d, h, mi = adjust_for_true_solar_time(2001, 3, 1, 0, 10)
        assert (y, m, d, h, mi) == (2001, 2, 28, 23, 38)

    def test_crosses_year_boundary(self):
        """Jan 1st 00:10 - 32min = previous year Dec 31 23:38."""
        y, m, d, h, mi = adjust_for_true_solar_time(2000, 1, 1, 0, 10)
        assert (y, m, d, h, mi) == (1999, 12, 31, 23, 38)

    def test_custom_longitude(self):
        """Custom longitude should produce different offset."""
        # 129E: offset = (135-129)*4 = 24 min
        y, m, d, h, mi = adjust_for_true_solar_time(
            2000, 6, 15, 9, 30, longitude=129.0,
        )
        assert (y, m, d, h, mi) == (2000, 6, 15, 9, 6)

    def test_no_change_at_standard_meridian(self):
        """At 135E, no adjustment should be made."""
        y, m, d, h, mi = adjust_for_true_solar_time(
            2000, 6, 15, 9, 30, longitude=135.0,
        )
        assert (y, m, d, h, mi) == (2000, 6, 15, 9, 30)

    def test_shi_chen_boundary_change(self):
        """09:05 Seoul -> 08:33 true solar, crosses si-shi(巳時 9-11) to jin-shi(辰時 7-9).

        This is the classic case where true solar time changes the time pillar.
        """
        y, m, d, h, mi = adjust_for_true_solar_time(1997, 1, 5, 9, 5)
        assert h == 8
        assert mi == 33
        # 8:33 is in jin-shi (辰時, 7-9), not si-shi (巳時, 9-11)

    def test_default_longitude_is_seoul(self):
        """Default longitude should be 127.0 (Seoul)."""
        result_default = adjust_for_true_solar_time(2000, 6, 15, 10, 0)
        result_explicit = adjust_for_true_solar_time(
            2000, 6, 15, 10, 0, longitude=127.0,
        )
        assert result_default == result_explicit
