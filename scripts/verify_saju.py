"""Saju calculation cross-verification script.

Compares API results against known reference values from manselyeok sites.
Usage: python scripts/verify_saju.py [--url URL]
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from dataclasses import dataclass


@dataclass(frozen=True)
class ExpectedPillar:
    gan: str
    zhi: str
    gan_kor: str
    zhi_kor: str


@dataclass(frozen=True)
class TestCase:
    label: str
    year: int
    month: int
    day: int
    hour: int
    minute: int
    gender: str
    year_pillar: ExpectedPillar
    month_pillar: ExpectedPillar
    day_pillar: ExpectedPillar
    time_pillar: ExpectedPillar
    note: str = ""


TEST_CASES: list[TestCase] = [
    TestCase(
        label="Case 1: 2000-01-01 00:00 (New Millennium, before ipchun)",
        year=2000, month=1, day=1, hour=0, minute=0, gender="male",
        year_pillar=ExpectedPillar("己", "卯", "기", "묘"),
        month_pillar=ExpectedPillar("丙", "子", "병", "자"),
        day_pillar=ExpectedPillar("戊", "午", "무", "오"),
        time_pillar=ExpectedPillar("壬", "子", "임", "자"),
        note="2000 but before ipchun -> 1999 己卯year",
    ),
    TestCase(
        label="Case 2: 1990-05-15 14:00",
        year=1990, month=5, day=15, hour=14, minute=0, gender="male",
        year_pillar=ExpectedPillar("庚", "午", "경", "오"),
        month_pillar=ExpectedPillar("辛", "巳", "신", "사"),
        day_pillar=ExpectedPillar("庚", "辰", "경", "진"),
        time_pillar=ExpectedPillar("癸", "未", "계", "미"),
    ),
    TestCase(
        label="Case 3: 1985-08-20 06:30",
        year=1985, month=8, day=20, hour=6, minute=30, gender="female",
        year_pillar=ExpectedPillar("乙", "丑", "을", "축"),
        month_pillar=ExpectedPillar("甲", "申", "갑", "신"),
        day_pillar=ExpectedPillar("辛", "卯", "신", "묘"),
        time_pillar=ExpectedPillar("辛", "卯", "신", "묘"),
        note="Day pillar and time pillar are identical",
    ),
    TestCase(
        label="Case 4: 1970-03-10 22:00",
        year=1970, month=3, day=10, hour=22, minute=0, gender="male",
        year_pillar=ExpectedPillar("庚", "戌", "경", "술"),
        month_pillar=ExpectedPillar("己", "卯", "기", "묘"),
        day_pillar=ExpectedPillar("己", "丑", "기", "축"),
        time_pillar=ExpectedPillar("乙", "亥", "을", "해"),
    ),
    TestCase(
        label="Case 5: 2000-06-15 12:00",
        year=2000, month=6, day=15, hour=12, minute=0, gender="female",
        year_pillar=ExpectedPillar("庚", "辰", "경", "진"),
        month_pillar=ExpectedPillar("壬", "午", "임", "오"),
        day_pillar=ExpectedPillar("甲", "辰", "갑", "진"),
        time_pillar=ExpectedPillar("庚", "午", "경", "오"),
    ),
    TestCase(
        label="Case 6: 1988-02-04 03:00 (ipchun boundary)",
        year=1988, month=2, day=4, hour=3, minute=0, gender="male",
        year_pillar=ExpectedPillar("丁", "卯", "정", "묘"),
        month_pillar=ExpectedPillar("癸", "丑", "계", "축"),
        day_pillar=ExpectedPillar("己", "丑", "기", "축"),
        time_pillar=ExpectedPillar("丙", "寅", "병", "인"),
        note="1988-02-04 is still before ipchun -> 丁卯year 癸丑month",
    ),
    TestCase(
        label="Case 7: 1960-07-30 23:30 (DST + night zi)",
        year=1960, month=7, day=30, hour=23, minute=30, gender="male",
        year_pillar=ExpectedPillar("庚", "子", "경", "자"),
        month_pillar=ExpectedPillar("癸", "未", "계", "미"),
        day_pillar=ExpectedPillar("己", "未", "기", "미"),
        time_pillar=ExpectedPillar("乙", "亥", "을", "해"),
        note="DST applied: 23:30 -> 22:30 -> hai-shi, not zi-shi",
    ),
    TestCase(
        label="Case 8: 1995-12-25 09:00",
        year=1995, month=12, day=25, hour=9, minute=0, gender="female",
        year_pillar=ExpectedPillar("乙", "亥", "을", "해"),
        month_pillar=ExpectedPillar("戊", "子", "무", "자"),
        day_pillar=ExpectedPillar("庚", "寅", "경", "인"),
        time_pillar=ExpectedPillar("辛", "巳", "신", "사"),
    ),
    TestCase(
        label="Case 9: 2010-10-10 10:00",
        year=2010, month=10, day=10, hour=10, minute=0, gender="male",
        year_pillar=ExpectedPillar("庚", "寅", "경", "인"),
        month_pillar=ExpectedPillar("丙", "戌", "병", "술"),
        day_pillar=ExpectedPillar("癸", "巳", "계", "사"),
        time_pillar=ExpectedPillar("丁", "巳", "정", "사"),
    ),
    TestCase(
        label="Case 10: 1975-01-01 00:00 (before ipchun)",
        year=1975, month=1, day=1, hour=0, minute=0, gender="male",
        year_pillar=ExpectedPillar("甲", "寅", "갑", "인"),
        month_pillar=ExpectedPillar("丙", "子", "병", "자"),
        day_pillar=ExpectedPillar("丁", "未", "정", "미"),
        time_pillar=ExpectedPillar("庚", "子", "경", "자"),
        note="1975 but before ipchun -> 1974 甲寅year",
    ),
]


def call_api(base_url: str, case: TestCase) -> dict:
    payload = {
        "birth": {
            "year": case.year,
            "month": case.month,
            "day": case.day,
            "hour": case.hour,
            "minute": case.minute,
            "gender": case.gender,
            "calendar_type": "solar",
            "use_night_zi": True,
        }
    }
    req = urllib.request.Request(
        f"{base_url}/api/v1/saju/calculate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    resp = urllib.request.urlopen(req, timeout=10)
    return json.loads(resp.read().decode("utf-8"))


def compare_pillar(
    name: str, expected: ExpectedPillar, actual: dict
) -> list[str]:
    errors = []
    if actual["gan"] != expected.gan:
        errors.append(f"  {name} gan: expected {expected.gan}, got {actual['gan']}")
    if actual["zhi"] != expected.zhi:
        errors.append(f"  {name} zhi: expected {expected.zhi}, got {actual['zhi']}")
    if actual["gan_kor"] != expected.gan_kor:
        errors.append(
            f"  {name} gan_kor: expected {expected.gan_kor}, got {actual['gan_kor']}"
        )
    if actual["zhi_kor"] != expected.zhi_kor:
        errors.append(
            f"  {name} zhi_kor: expected {expected.zhi_kor}, got {actual['zhi_kor']}"
        )
    return errors


def run_verification(base_url: str) -> int:
    print(f"Saju Calculation Verification")
    print(f"API: {base_url}")
    print("=" * 60)

    passed = 0
    failed = 0
    errors_all: list[tuple[str, list[str]]] = []

    for case in TEST_CASES:
        try:
            result = call_api(base_url, case)
        except Exception as exc:
            print(f"FAIL  {case.label}")
            print(f"  API error: {exc}")
            failed += 1
            continue

        errors = []
        errors.extend(compare_pillar("year", case.year_pillar, result["year_pillar"]))
        errors.extend(
            compare_pillar("month", case.month_pillar, result["month_pillar"])
        )
        errors.extend(compare_pillar("day", case.day_pillar, result["day_pillar"]))
        errors.extend(compare_pillar("time", case.time_pillar, result["time_pillar"]))

        if errors:
            failed += 1
            errors_all.append((case.label, errors))
            print(f"FAIL  {case.label}")
            for e in errors:
                print(e)
            if case.note:
                print(f"  note: {case.note}")
        else:
            passed += 1
            print(f"PASS  {case.label}")

    print("=" * 60)
    print(f"Result: {passed} passed, {failed} failed / {len(TEST_CASES)} total")

    if errors_all:
        print("\nFailed cases summary:")
        for label, errs in errors_all:
            print(f"\n  {label}")
            for e in errs:
                print(f"  {e}")

    return 0 if failed == 0 else 1


def main():
    parser = argparse.ArgumentParser(description="Verify saju calculation API")
    parser.add_argument(
        "--url",
        default="http://13.124.36.79",
        help="API base URL (default: http://13.124.36.79)",
    )
    args = parser.parse_args()
    sys.exit(run_verification(args.url))


if __name__ == "__main__":
    main()
