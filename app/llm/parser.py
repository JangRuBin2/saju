"""Parse LLM markdown output into structured sections."""
from __future__ import annotations

import re

from app.models.response import InterpretationResponse, SectionResponse

# Matches ### with optional numbering: "### 1. Title", "### Title", "### 2. Title text"
_SECTION_HEADER_RE = re.compile(r"^###\s+(?:\d+\.\s*)?(.+)$", re.MULTILINE)

# Common disclaimer prefixes found in LLM output
_DISCLAIMER_PREFIXES = (
    "본 분석은",
    "본 서비스의",
    "이 해석은",
    "본 해석은",
    "(본 분석은",
    "(이 해석은",
    "(본 해석은",
)


def parse_interpretation(raw_text: str) -> InterpretationResponse:
    """Parse raw LLM markdown text into structured interpretation.

    Expected LLM output format:
        [summary line(s) before first ### header]

        ### 1. Section Title
        Section content...

        ### 2. Another Section
        More content...

        (disclaimer text at the end)

    Returns:
        InterpretationResponse with summary, sections, and disclaimer.
    """
    raw_text = raw_text.strip()

    # Split by ### headers
    headers = list(_SECTION_HEADER_RE.finditer(raw_text))

    if not headers:
        # No sections found - return entire text as summary
        summary, disclaimer = _extract_disclaimer(raw_text)
        return InterpretationResponse(
            summary=summary.strip(),
            sections=[],
            disclaimer=disclaimer,
        )

    # Everything before first ### is summary
    summary_text = raw_text[: headers[0].start()].strip()
    # Clean summary: remove leading ## header if present
    summary_text = re.sub(r"^##\s+.+\n*", "", summary_text).strip()

    # Parse sections
    sections: list[SectionResponse] = []
    for i, header in enumerate(headers):
        title = header.group(1).strip()
        start = header.end()
        end = headers[i + 1].start() if i + 1 < len(headers) else len(raw_text)
        content = raw_text[start:end].strip()
        sections.append(SectionResponse(title=title, content=content))

    # Extract disclaimer from last section's content
    disclaimer: str | None = None
    if sections:
        last_content = sections[-1].content
        cleaned, found_disclaimer = _extract_disclaimer(last_content)
        if found_disclaimer:
            sections = [
                *sections[:-1],
                SectionResponse(title=sections[-1].title, content=cleaned.strip()),
            ]
            disclaimer = found_disclaimer

    # If no disclaimer found in sections, check if summary_text is empty
    # and disclaimer might be standalone
    if not disclaimer and not sections:
        summary_text, disclaimer = _extract_disclaimer(summary_text)

    # If summary is empty, use first section's first sentence
    if not summary_text and sections:
        first_sentence = _first_sentence(sections[0].content)
        summary_text = first_sentence

    return InterpretationResponse(
        summary=summary_text.strip(),
        sections=sections,
        disclaimer=disclaimer,
    )


def _extract_disclaimer(text: str) -> tuple[str, str | None]:
    """Extract disclaimer from the end of text.

    Returns (text_without_disclaimer, disclaimer_or_none).
    """
    lines = text.strip().split("\n")

    # Search from the end for disclaimer
    disclaimer_start = -1
    for i in range(len(lines) - 1, max(len(lines) - 6, -1), -1):
        stripped = lines[i].strip().lstrip("(").lstrip("*").lstrip("_")
        if any(stripped.startswith(prefix) for prefix in _DISCLAIMER_PREFIXES):
            disclaimer_start = i
            break

    if disclaimer_start == -1:
        return text, None

    disclaimer = "\n".join(lines[disclaimer_start:]).strip()
    # Clean markdown formatting from disclaimer
    disclaimer = disclaimer.strip("()").strip("*").strip("_").strip()
    remaining = "\n".join(lines[:disclaimer_start]).strip()
    return remaining, disclaimer


def _first_sentence(text: str) -> str:
    """Extract first meaningful sentence from text."""
    # Remove markdown formatting
    clean = re.sub(r"^[-*]\s+", "", text.strip())
    clean = re.sub(r"\*\*(.+?)\*\*", r"\1", clean)

    # Find first sentence end
    for delimiter in (".", "다.", "니다.", "\n"):
        idx = clean.find(delimiter)
        if 0 < idx < 150:
            return clean[: idx + len(delimiter)].strip()

    # Fallback: first 100 chars
    return clean[:100].strip() if len(clean) > 100 else clean.strip()
