# Saju API Reference

## Overview

사주(四柱) 만세력 계산 + LLM 해석 API 서버.
총 **17개 엔드포인트** (16개 기능 + 1개 헬스체크)

---

## Authentication & Middleware

| Middleware | Description |
|------------|-------------|
| TokenValidatorMiddleware | 서비스 토큰 검증 (`.env`의 `require_service_token`으로 on/off) |
| RateLimiterMiddleware | Rate limiting |
| CORSMiddleware | CORS 정책 (현재 all origins 허용) |

---

## Endpoints

### Health Check

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | 서버 상태 확인 |

---

### Saju (사주) - `/api/v1/saju`

| Method | Path | Description | LLM |
|--------|------|-------------|-----|
| POST | `/api/v1/saju/calculate` | 사주 사주팔자 계산 (순수 만세력) | No |
| POST | `/api/v1/saju/reading` | 사주 해석 (SSE 스트리밍 지원, `stream: bool`) | Yes |
| POST | `/api/v1/saju/sinsal` | 신살(神煞) 분석 | Yes |

---

### Compatibility (궁합) - `/api/v1/compatibility`

| Method | Path | Description | LLM |
|--------|------|-------------|-----|
| POST | `/api/v1/compatibility/analyze` | 두 사람 간 궁합 분석 | Yes |

---

### Celebrity (연예인) - `/api/v1/celebrity`

| Method | Path | Description | LLM |
|--------|------|-------------|-----|
| GET | `/api/v1/celebrity/search?q={query}` | 연예인 이름/그룹명 검색 (한국어/영어) | No |
| POST | `/api/v1/celebrity/compatibility` | 사용자-연예인 궁합 분석 | Yes |

---

### Fortune (운세) - `/api/v1/fortune`

| Method | Path | Description | LLM |
|--------|------|-------------|-----|
| POST | `/api/v1/fortune/monthly` | 월간 운세 분석 (기본: 이번 달) | Yes |
| POST | `/api/v1/fortune/daily` | 일간 운세 분석 (기본: 오늘) | Yes |

---

### Relationship (관계) - `/api/v1/relationship`

| Method | Path | Description | LLM |
|--------|------|-------------|-----|
| POST | `/api/v1/relationship/reading` | 관계 관점 사주 해석 (`lover`, `boss`, `child`, `friend`) | Yes |

---

### Timing (시간 운세) - `/api/v1/timing`

| Method | Path | Description | LLM |
|--------|------|-------------|-----|
| POST | `/api/v1/timing/now` | 현재 시간(시진) 실시간 운세 | Yes |
| POST | `/api/v1/timing/best-hours` | 오늘(또는 지정일) 최적 시간대 분석 | Yes |
| POST | `/api/v1/timing/dday` | 특정 날짜 D-day 운세 | Yes |

---

## Internationalization (i18n) - 다국어 지원

### 구현 방식

별도의 번역 파일(JSON/YAML) 없이 **Claude LLM의 다국어 능력**을 활용하는 prompt-based 방식.

### Language 파라미터

LLM 해석이 포함된 모든 엔드포인트는 요청 body에 `language` 필드를 지원합니다.

```json
{
  "year": 1990,
  "month": 5,
  "day": 15,
  "hour": 14,
  "gender": "male",
  "language": "en"
}
```

### 지원 언어

| Code | Language | Status |
|------|----------|--------|
| `ko` | Korean (한국어) | **Default** |
| `en` | English | Supported |
| `ja` | Japanese (日本語) | Supported |
| `zh` | Chinese (中文) | Supported |
| `es` | Spanish (Espanol) | Supported |
| `fr` | French (Francais) | Supported |
| 기타 | Claude가 지원하는 모든 언어 | Supported |

- ISO 코드(`"ko"`, `"en"`, `"ja"`) 또는 전체 이름(`"English"`, `"Japanese"`) 모두 사용 가능
- 비한국어 요청 시 LLM 프롬프트에 `[IMPORTANT: You MUST respond entirely in {language}.]` 지시문 자동 추가
- 언어별 캐시 키 분리 (같은 사주 데이터라도 언어가 다르면 별도 캐싱)

### Language 파라미터 지원 모델

| Request Model | Endpoint |
|---------------|----------|
| SajuReadingRequest | `/api/v1/saju/reading` |
| SinsalRequest | `/api/v1/saju/sinsal` |
| CompatibilityRequest | `/api/v1/compatibility/analyze` |
| CelebrityCompatibilityRequest | `/api/v1/celebrity/compatibility` |
| FortuneRequest | `/api/v1/fortune/monthly`, `/api/v1/fortune/daily` |
| RelationshipReadingRequest | `/api/v1/relationship/reading` |
| TimingRequest | `/api/v1/timing/now`, `/api/v1/timing/best-hours`, `/api/v1/timing/dday` |

> **Note**: `POST /api/v1/saju/calculate`와 `GET /api/v1/celebrity/search`는 LLM을 사용하지 않으므로 `language` 파라미터가 없습니다.

---

## Endpoint Summary

| Category | Count | LLM | Streaming |
|----------|-------|-----|-----------|
| Health | 1 | - | - |
| Saju 계산 | 1 | No | No |
| Saju 해석 | 2 | Yes | Yes (reading) |
| 궁합 | 1 | Yes | No |
| 연예인 | 2 | 1 Yes / 1 No | No |
| 운세 | 2 | Yes | No |
| 관계 | 1 | Yes | No |
| 시간 운세 | 3 | Yes | No |
| **Total** | **17** | **12 Yes** | **1** |

---

## Router Files

```
app/routers/
  health.py          # GET /health
  saju.py            # POST /api/v1/saju/*
  compatibility.py   # POST /api/v1/compatibility/*
  celebrity.py       # GET/POST /api/v1/celebrity/*
  fortune.py         # POST /api/v1/fortune/*
  relationship.py    # POST /api/v1/relationship/*
  timing.py          # POST /api/v1/timing/*
```
