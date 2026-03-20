from __future__ import annotations

from app.llm.parser import parse_interpretation


class TestParseInterpretation:
    def test_basic_sections(self):
        raw = """핵심 요약 문장입니다.

### 1. 첫 번째 섹션
첫 번째 내용입니다.

### 2. 두 번째 섹션
두 번째 내용입니다.
"""
        result = parse_interpretation(raw)
        assert result.summary == "핵심 요약 문장입니다."
        assert len(result.sections) == 2
        assert result.sections[0].title == "첫 번째 섹션"
        assert "첫 번째 내용" in result.sections[0].content
        assert result.sections[1].title == "두 번째 섹션"
        assert result.disclaimer is None

    def test_with_disclaimer(self):
        raw = """요약입니다.

### 1. 분석
분석 내용

### 2. 조언
조언 내용

본 분석은 전통 역학에 기반한 참고 정보입니다.
"""
        result = parse_interpretation(raw)
        assert result.summary == "요약입니다."
        assert len(result.sections) == 2
        assert result.disclaimer is not None
        assert "전통 역학" in result.disclaimer

    def test_no_sections(self):
        raw = "섹션 없이 텍스트만 있는 경우입니다."
        result = parse_interpretation(raw)
        assert result.summary == "섹션 없이 텍스트만 있는 경우입니다."
        assert result.sections == []

    def test_no_summary_before_first_section(self):
        raw = """### 1. 바로 시작하는 섹션
내용이 여기 있습니다.

### 2. 두 번째
두 번째 내용
"""
        result = parse_interpretation(raw)
        assert result.summary != ""
        assert len(result.sections) == 2

    def test_section_title_without_numbering(self):
        raw = """요약

### 연애운 분석
연애 관련 내용

### 직업운 분석
직업 관련 내용
"""
        result = parse_interpretation(raw)
        assert result.sections[0].title == "연애운 분석"
        assert result.sections[1].title == "직업운 분석"

    def test_disclaimer_in_parentheses(self):
        raw = """요약

### 1. 분석
내용

(본 분석은 전통 역학에 기반한 참고 정보입니다.)
"""
        result = parse_interpretation(raw)
        assert result.disclaimer is not None
        assert "전통 역학" in result.disclaimer

    def test_empty_input(self):
        result = parse_interpretation("")
        assert result.summary == ""
        assert result.sections == []

    def test_response_is_serializable(self):
        raw = """요약

### 1. 섹션
내용
"""
        result = parse_interpretation(raw)
        d = result.model_dump()
        assert d["summary"] == "요약"
        assert len(d["sections"]) == 1
        assert d["sections"][0]["title"] == "섹션"
        assert d["sections"][0]["content"] == "내용"
