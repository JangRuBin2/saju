from __future__ import annotations


def is_night_zi_hour(hour: int) -> bool:
    """Check if the given hour falls in the night zi (23:00-00:00) range.

    In saju, the zi hour (子時) spans 23:00-01:00. The period 23:00-00:00
    is called "night zi" (야자시). Different schools treat this differently:

    - sect 1: 23:00 is treated as the next day's zi hour (day pillar advances)
    - sect 2: 23:00 stays as the current day's zi hour (day pillar does NOT advance)
      This is the "night zi" (야자시) approach.
    """
    return hour == 23


def get_sect_value(use_night_zi: bool) -> int:
    """Convert the use_night_zi flag to lunar-python's sect parameter.

    sect=1: Early zi approach - 23:00 advances day pillar (not night zi)
    sect=2: Night zi approach - 23:00 keeps current day pillar (야자시)
    """
    return 2 if use_night_zi else 1
