from __future__ import annotations

from datetime import datetime, timedelta

# KST is based on 135 degrees East longitude
_KST_STANDARD_LONGITUDE = 135.0

# Each degree of longitude corresponds to 4 minutes of time
_MINUTES_PER_DEGREE = 4.0


def calculate_solar_time_offset_minutes(longitude: float = 127.0) -> float:
    """Calculate the offset in minutes between KST and true solar time.

    Args:
        longitude: Observer's longitude in degrees East.
                   Seoul default: 127.0E.

    Returns:
        Offset in minutes to subtract from KST.
        Positive means KST is ahead (west of standard meridian).
        Negative means KST is behind (east of standard meridian).
    """
    return (_KST_STANDARD_LONGITUDE - longitude) * _MINUTES_PER_DEGREE


def adjust_for_true_solar_time(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    longitude: float = 127.0,
) -> tuple[int, int, int, int, int]:
    """Adjust birth time from KST to true solar time.

    Args:
        year: Birth year
        month: Birth month
        day: Birth day
        hour: Birth hour (0-23)
        minute: Birth minute (0-59)
        longitude: Observer's longitude (default: 127.0E for Seoul)

    Returns:
        Corrected (year, month, day, hour, minute).
    """
    offset = calculate_solar_time_offset_minutes(longitude)
    if offset == 0.0:
        return year, month, day, hour, minute

    dt = datetime(year, month, day, hour, minute)
    corrected = dt - timedelta(minutes=offset)
    return (
        corrected.year,
        corrected.month,
        corrected.day,
        corrected.hour,
        corrected.minute,
    )
