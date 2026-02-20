# Saju API Server - Project CLAUDE.md

## Project Overview

사주(四柱) 만세력 계산 + LLM 해석 API 서버. Python 3.11+ / FastAPI / lunar-python / Anthropic Claude.
핵심 원칙: **계산(만세력)과 해석(LLM)의 완전 분리**

## Modular Rules

상세 가이드라인은 `.claude/rules/`에 있습니다:

| Rule File | Contents |
|-----------|----------|
| architecture.md | 시스템 아키텍처, 요청 흐름, 캐시/DB 전략 |
| coding-style.md | 불변성, 파일 구조, 에러 처리 |
| security.md | 보안 체크, 시크릿/PII 관리 |
| testing.md | TDD 워크플로우, 80% 커버리지 |
| git-workflow.md | 커밋 포맷, PR 워크플로우 |
| agents.md | 에이전트 오케스트레이션 |
| patterns.md | API 응답, 서비스 패턴, 캐시 키 |
| performance.md | 모델 선택, 컨텍스트 관리, 비용 최적화 |

## Critical Rules

### 1. Code Organization

- Many small files over few large files
- High cohesion, low coupling
- 200-400 lines typical, 800 max per file
- Organize by feature/domain (engine, llm, services, routers)

### 2. Code Style

- No emojis in code, comments, or documentation
- Immutability: frozen dataclass, never mutate dicts/lists in place
- No print() in production code (use logging)
- Type hints on all public functions
- `from __future__ import annotations` in every module

### 3. Testing

- TDD: Write tests first
- 80% minimum coverage
- Unit tests for engine calculations
- Integration tests for API endpoints
- Cross-verify calculations against reference saju sites

### 4. Security

- No hardcoded secrets (API keys in .env only)
- .env is gitignored, .env.example has dummy values
- Validate all user inputs via Pydantic models
- Error messages must not leak internal details

### 5. Architecture

- Engine layer: Pure calculation, no I/O, no async
- LLM layer: Async Anthropic client, prompt caching
- Service layer: Orchestration between engine and LLM
- Router layer: HTTP concerns only, delegates to services
- Dependencies injected via FastAPI Depends

## File Structure

```
app/
|-- engine/          # Pure saju calculation (lunar-python wrapping)
|-- llm/             # Anthropic client, prompts, formatter
|-- services/        # Business logic orchestration
|-- routers/         # FastAPI route handlers
|-- middleware/       # Error handlers
|-- models/          # Pydantic request/response schemas
|-- config.py        # Pydantic Settings
|-- dependencies.py  # DI container
|-- main.py          # FastAPI app entry
tests/
|-- test_engine/     # Calculator, summer time, night zi tests
|-- test_routers/    # API endpoint tests
```

## Key Patterns

### API Response (Calculation)

```python
class SajuCalculateResponse(BaseModel):
    solar_date: str
    lunar_date: str
    year_pillar: PillarResponse
    month_pillar: PillarResponse
    day_pillar: PillarResponse
    time_pillar: PillarResponse | None
    day_master: str
    element_counts: dict[str, int]
    da_yun_list: list[DaYunResponse]
```

### Error Handling

```python
class SajuError(Exception):
    def __init__(self, message: str, status_code: int = 400): ...

class InvalidBirthDateError(SajuError): ...
class LunarConversionError(SajuError): ...
class LLMError(SajuError): ...
```

## Environment Variables

```bash
# Required for LLM features
ANTHROPIC_API_KEY=sk-ant-xxxxx

# Optional
REDIS_URL=redis://localhost:6379/0
LLM_MODEL=claude-sonnet-4-5-20250514
LLM_TEMPERATURE=0.4
LLM_MAX_TOKENS=3000
```

## Available Commands

- `/plan` - Create implementation plan before coding
- `/tdd` - Test-driven development workflow
- `/code-review` - Code quality and security review
- `/build-fix` - Fix build/import errors

## Git Workflow

- Conventional commits: `feat:`, `fix:`, `refactor:`, `docs:`, `test:`
- Test locally before commit
- Small, focused commits
- All tests must pass before merge

## Running

```bash
# Install
pip install -e ".[dev]"

# Dev server
uvicorn app.main:app --reload

# Tests
pytest tests/ -v

# Single test file
pytest tests/test_engine/test_calculator.py -v
```
