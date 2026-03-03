from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Celebrity:
    id: str
    name_ko: str
    name_en: str
    group: str
    year: int
    month: int
    day: int
    gender: str  # "male" | "female"


# K-pop idol database (public birth dates only, no birth times)
# Sources: official profiles, publicly available information
CELEBRITIES: tuple[Celebrity, ...] = (
    # aespa
    Celebrity("karina-aespa", "카리나", "Karina", "aespa", 2000, 4, 11, "female"),
    Celebrity("winter-aespa", "윈터", "Winter", "aespa", 2001, 1, 1, "female"),
    Celebrity("giselle-aespa", "지젤", "Giselle", "aespa", 2000, 10, 30, "female"),
    Celebrity("ningning-aespa", "닝닝", "Ningning", "aespa", 2002, 10, 23, "female"),
    # BLACKPINK
    Celebrity("jisoo-blackpink", "지수", "Jisoo", "BLACKPINK", 1995, 1, 3, "female"),
    Celebrity("jennie-blackpink", "제니", "Jennie", "BLACKPINK", 1996, 1, 16, "female"),
    Celebrity("rose-blackpink", "로제", "Rose", "BLACKPINK", 1997, 2, 11, "female"),
    Celebrity("lisa-blackpink", "리사", "Lisa", "BLACKPINK", 1997, 3, 27, "female"),
    # BTS
    Celebrity("rm-bts", "RM", "RM", "BTS", 1994, 9, 12, "male"),
    Celebrity("jin-bts", "진", "Jin", "BTS", 1992, 12, 4, "male"),
    Celebrity("suga-bts", "슈가", "Suga", "BTS", 1993, 3, 9, "male"),
    Celebrity("jhope-bts", "제이홉", "J-Hope", "BTS", 1994, 2, 18, "male"),
    Celebrity("jimin-bts", "지민", "Jimin", "BTS", 1995, 10, 13, "male"),
    Celebrity("v-bts", "뷔", "V", "BTS", 1995, 12, 30, "male"),
    Celebrity("jungkook-bts", "정국", "Jungkook", "BTS", 1997, 9, 1, "male"),
    # NewJeans
    Celebrity("minji-newjeans", "민지", "Minji", "NewJeans", 2004, 5, 7, "female"),
    Celebrity("hanni-newjeans", "하니", "Hanni", "NewJeans", 2004, 10, 6, "female"),
    Celebrity("danielle-newjeans", "다니엘", "Danielle", "NewJeans", 2005, 4, 11, "female"),
    Celebrity("haerin-newjeans", "해린", "Haerin", "NewJeans", 2006, 5, 15, "female"),
    Celebrity("hyein-newjeans", "혜인", "Hyein", "NewJeans", 2008, 4, 21, "female"),
    # IVE
    Celebrity("yujin-ive", "유진", "Yujin", "IVE", 2003, 9, 1, "female"),
    Celebrity("wonyoung-ive", "원영", "Wonyoung", "IVE", 2004, 8, 31, "female"),
    Celebrity("gaeul-ive", "가을", "Gaeul", "IVE", 2002, 9, 24, "female"),
    Celebrity("rei-ive", "레이", "Rei", "IVE", 2004, 2, 3, "female"),
    Celebrity("liz-ive", "리즈", "Liz", "IVE", 2004, 11, 21, "female"),
    Celebrity("leeseo-ive", "이서", "Leeseo", "IVE", 2007, 2, 21, "female"),
    # SEVENTEEN
    Celebrity("scoups-seventeen", "에스쿱스", "S.Coups", "SEVENTEEN", 1995, 8, 8, "male"),
    Celebrity("mingyu-seventeen", "민규", "Mingyu", "SEVENTEEN", 1997, 4, 6, "male"),
    Celebrity("wonwoo-seventeen", "원우", "Wonwoo", "SEVENTEEN", 1996, 7, 17, "male"),
    # Stray Kids
    Celebrity("bangchan-straykids", "방찬", "Bang Chan", "Stray Kids", 1997, 10, 3, "male"),
    Celebrity("hyunjin-straykids", "현진", "Hyunjin", "Stray Kids", 2000, 3, 20, "male"),
    Celebrity("felix-straykids", "필릭스", "Felix", "Stray Kids", 2000, 9, 15, "male"),
)

# O(1) lookup by ID
_CELEBRITY_BY_ID: dict[str, Celebrity] = {c.id: c for c in CELEBRITIES}


def get_celebrity_by_id(celebrity_id: str) -> Celebrity | None:
    """Get a celebrity by their unique ID. Returns None if not found."""
    return _CELEBRITY_BY_ID.get(celebrity_id)


def search_celebrities(query: str) -> tuple[Celebrity, ...]:
    """Search celebrities by Korean name, English name, or group name.

    Case-insensitive partial matching.
    Returns matching celebrities as an immutable tuple.
    """
    if not query or not query.strip():
        return ()

    q = query.strip().lower()
    return tuple(
        c for c in CELEBRITIES
        if q in c.name_ko.lower()
        or q in c.name_en.lower()
        or q in c.group.lower()
    )
