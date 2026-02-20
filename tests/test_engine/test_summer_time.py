from __future__ import annotations

import pytest

from app.engine.summer_time import adjust_for_dst, is_korea_dst


class TestKoreaDST:
    """Test Korean summer time (1948-1961) detection and correction."""

    def test_dst_period_1948(self):
        assert is_korea_dst(1948, 7, 1) is True
        assert is_korea_dst(1948, 5, 1) is False
        assert is_korea_dst(1948, 10, 1) is False

    def test_dst_period_1955(self):
        assert is_korea_dst(1955, 6, 1) is True
        assert is_korea_dst(1955, 4, 1) is False

    def test_no_dst_before_1948(self):
        assert is_korea_dst(1947, 7, 1) is False

    def test_no_dst_after_1961(self):
        assert is_korea_dst(1962, 7, 1) is False

    def test_no_dst_modern(self):
        assert is_korea_dst(1990, 7, 1) is False

    def test_dst_boundary_start(self):
        # 1949: Apr 3 start
        assert is_korea_dst(1949, 4, 2) is False
        assert is_korea_dst(1949, 4, 3) is True

    def test_dst_boundary_end(self):
        # 1949: Sep 11 end (exclusive)
        assert is_korea_dst(1949, 9, 10) is True
        assert is_korea_dst(1949, 9, 11) is False

    def test_no_dst_1952_1953(self):
        """1952-1953 had no DST in Korea."""
        assert is_korea_dst(1952, 7, 1) is False
        assert is_korea_dst(1953, 7, 1) is False


class TestAdjustForDST:
    def test_adjust_during_dst(self):
        """Birth at 15:00 during DST should become 14:00."""
        y, m, d, h, mi = adjust_for_dst(1955, 7, 15, 15, 30)
        assert h == 14
        assert mi == 30

    def test_no_adjust_outside_dst(self):
        """Birth outside DST period should not be adjusted."""
        y, m, d, h, mi = adjust_for_dst(1990, 7, 15, 15, 30)
        assert h == 15
        assert mi == 30

    def test_adjust_midnight_crossing(self):
        """Birth at 00:30 during DST should go back to previous day 23:30."""
        y, m, d, h, mi = adjust_for_dst(1955, 7, 15, 0, 30)
        assert d == 14
        assert h == 23
        assert mi == 30
