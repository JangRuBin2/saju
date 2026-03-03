from __future__ import annotations

from app.data.celebrities import (
    CELEBRITIES,
    Celebrity,
    get_celebrity_by_id,
    search_celebrities,
)


class TestCelebrityData:
    """Tests for celebrity database integrity."""

    def test_all_entries_are_celebrity_instances(self):
        for c in CELEBRITIES:
            assert isinstance(c, Celebrity)

    def test_no_duplicate_ids(self):
        ids = [c.id for c in CELEBRITIES]
        assert len(ids) == len(set(ids)), "Duplicate celebrity IDs found"

    def test_all_ids_are_non_empty_strings(self):
        for c in CELEBRITIES:
            assert isinstance(c.id, str)
            assert len(c.id) > 0

    def test_all_genders_valid(self):
        for c in CELEBRITIES:
            assert c.gender in ("male", "female"), f"Invalid gender for {c.id}"

    def test_year_in_reasonable_range(self):
        for c in CELEBRITIES:
            assert 1970 <= c.year <= 2015, f"Year out of range for {c.id}"

    def test_month_in_range(self):
        for c in CELEBRITIES:
            assert 1 <= c.month <= 12, f"Month out of range for {c.id}"

    def test_day_in_range(self):
        for c in CELEBRITIES:
            assert 1 <= c.day <= 31, f"Day out of range for {c.id}"

    def test_minimum_celebrity_count(self):
        assert len(CELEBRITIES) >= 20, "Expected at least 20 celebrities"

    def test_celebrities_is_immutable_tuple(self):
        assert isinstance(CELEBRITIES, tuple)

    def test_celebrity_is_frozen(self):
        c = CELEBRITIES[0]
        try:
            c.name_ko = "changed"
            assert False, "Should have raised FrozenInstanceError"
        except AttributeError:
            pass


class TestGetCelebrityById:
    """Tests for O(1) ID lookup."""

    def test_valid_id_returns_celebrity(self):
        result = get_celebrity_by_id("karina-aespa")
        assert result is not None
        assert result.name_ko == "카리나"
        assert result.group == "aespa"

    def test_invalid_id_returns_none(self):
        result = get_celebrity_by_id("nonexistent-idol")
        assert result is None

    def test_empty_id_returns_none(self):
        result = get_celebrity_by_id("")
        assert result is None


class TestSearchCelebrities:
    """Tests for celebrity search functionality."""

    def test_search_by_korean_name(self):
        results = search_celebrities("카리나")
        assert len(results) == 1
        assert results[0].id == "karina-aespa"

    def test_search_by_english_name(self):
        results = search_celebrities("Karina")
        assert len(results) == 1
        assert results[0].id == "karina-aespa"

    def test_search_by_english_name_case_insensitive(self):
        results = search_celebrities("karina")
        assert len(results) == 1

    def test_search_by_group_name(self):
        results = search_celebrities("BTS")
        assert len(results) >= 7

    def test_search_by_group_name_case_insensitive(self):
        results = search_celebrities("bts")
        assert len(results) >= 7

    def test_partial_match(self):
        results = search_celebrities("지")
        # Should match at least jisoo (지수), giselle (지젤), jimin (지민)
        assert len(results) >= 3

    def test_empty_query_returns_empty(self):
        results = search_celebrities("")
        assert len(results) == 0

    def test_whitespace_query_returns_empty(self):
        results = search_celebrities("   ")
        assert len(results) == 0

    def test_no_match_returns_empty(self):
        results = search_celebrities("zzzzzzz")
        assert len(results) == 0

    def test_results_are_immutable_tuple(self):
        results = search_celebrities("aespa")
        assert isinstance(results, tuple)
