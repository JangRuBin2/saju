from __future__ import annotations

from app.engine.night_zi import get_sect_value, is_night_zi_hour


class TestNightZi:
    def test_is_night_zi_hour(self):
        assert is_night_zi_hour(23) is True
        assert is_night_zi_hour(0) is False
        assert is_night_zi_hour(22) is False
        assert is_night_zi_hour(1) is False

    def test_get_sect_value_night_zi(self):
        """use_night_zi=True -> sect=2 (day pillar stays same)."""
        assert get_sect_value(True) == 2

    def test_get_sect_value_normal(self):
        """use_night_zi=False -> sect=1 (day pillar advances)."""
        assert get_sect_value(False) == 1
