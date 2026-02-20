from __future__ import annotations

from datetime import datetime

# Korea Summer Time (Daylight Saving Time) periods: 1948-1961
# During these periods, clocks were set forward by 1 hour.
# For saju calculation, we need to subtract 1 hour from the recorded birth time.
_KOREA_DST_PERIODS: list[tuple[datetime, datetime]] = [
    (datetime(1948, 6, 1), datetime(1948, 9, 13)),
    (datetime(1949, 4, 3), datetime(1949, 9, 11)),
    (datetime(1950, 4, 1), datetime(1950, 9, 10)),
    (datetime(1951, 5, 6), datetime(1951, 9, 9)),
    (datetime(1954, 3, 21), datetime(1954, 9, 22)),
    (datetime(1955, 5, 5), datetime(1955, 9, 9)),
    (datetime(1956, 5, 20), datetime(1956, 9, 30)),
    (datetime(1957, 5, 5), datetime(1957, 9, 22)),
    (datetime(1958, 5, 4), datetime(1958, 9, 21)),
    (datetime(1959, 5, 3), datetime(1959, 9, 20)),
    (datetime(1960, 5, 1), datetime(1960, 9, 18)),
    (datetime(1961, 8, 10), datetime(1961, 9, 18)),
]


def is_korea_dst(year: int, month: int, day: int) -> bool:
    """Check if the given date falls within Korean summer time period."""
    if year < 1948 or year > 1961:
        return False

    dt = datetime(year, month, day)
    return any(start <= dt < end for start, end in _KOREA_DST_PERIODS)


def adjust_for_dst(
    year: int, month: int, day: int, hour: int, minute: int
) -> tuple[int, int, int, int, int]:
    """Adjust birth time by subtracting 1 hour if born during Korean DST.

    Returns the corrected (year, month, day, hour, minute).
    """
    if not is_korea_dst(year, month, day):
        return year, month, day, hour, minute

    dt = datetime(year, month, day, hour, minute)
    from datetime import timedelta

    corrected = dt - timedelta(hours=1)
    return (
        corrected.year,
        corrected.month,
        corrected.day,
        corrected.hour,
        corrected.minute,
    )
