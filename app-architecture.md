# 사주 앱 아키텍처 & 최적화 전략

## 프로젝트 개요

한국 사주(四柱) 풀이 웹 서비스. 사용자가 생년월일시를 입력하면 만세력 기반 사주 분석 결과를 제공한다.

---

## 기술 스택

| 레이어     | 기술                  | 역할                                        |
| ---------- | --------------------- | ------------------------------------------- |
| Frontend   | Next.js (App Router)  | UI, SSR/SSG, 사용자 인터랙션                |
| API Server | Python (FastAPI 권장) | 사주 연산, LLM 호출, 캐싱, DB 관리          |
| Cache      | Redis                 | 사주 결과 캐시, 세션, Rate Limiting         |
| Database   | PostgreSQL            | 사용자 정보, 사주 결과 영구 저장, 결제 내역 |
| LLM        | Claude API / GPT API  | 사주 해석 텍스트 생성                       |

---

## 아키텍처 구조

```
[사용자] → [Next.js Frontend]
                │
                ▼
         [Python API Server]
                │
        ┌───────┼───────┐
        ▼       ▼       ▼
     [Redis]  [PostgreSQL]  [LLM API]
     (캐시)   (영구저장)    (사주해석)
```

### 요청 흐름

```
1. 사용자가 생년월일시 + 질문유형 입력
2. Next.js → Python API 호출 (항상)
3. Python API 내부 처리:
   a. 캐시 키 생성: "saju:{년}:{월}:{일}:{시}:{성별}:{질문유형}"
   b. Redis에서 캐시 조회
      - HIT  → 즉시 응답 반환
      - MISS → 다음 단계로
   c. PostgreSQL에서 조회 (Redis 만료 후에도 영구 데이터 존재 가능)
      - HIT  → Redis에 다시 캐싱 + 응답 반환
      - MISS → 다음 단계로
   d. 만세력 계산 (Python 라이브러리 활용)
   e. LLM API 호출 (만세력 데이터 + 프롬프트)
   f. 결과를 Redis + PostgreSQL 양쪽에 저장
   g. 응답 반환
```

### 설계 원칙

- **Next.js는 순수 프론트엔드 역할만 수행**: DB 직접 접근 없음, Prisma 사용 안 함
- **Python API가 모든 비즈니스 로직 담당**: 캐싱, DB, LLM 호출, 만세력 계산
- **이 구조의 장점**: 나중에 모바일 앱(React Native 등)을 추가할 때 Python API를 그대로 재사용 가능

---

## 캐시 키 설계

```python
# 기본 사주 결과 캐시
cache_key = f"saju:{year}:{month}:{day}:{hour}:{gender}:{question_type}"

# 예시
"saju:1997:03:15:14:M:overall"      # 종합운세
"saju:1997:03:15:14:M:wealth"       # 재물운
"saju:1997:03:15:14:M:love"         # 애정운
"saju:1997:03:15:14:M:career"       # 직업운

# 궁합 캐시 (두 사람의 키를 정렬하여 일관성 유지)
person_a = f"{year_a}:{month_a}:{day_a}:{hour_a}:{gender_a}"
person_b = f"{year_b}:{month_b}:{day_b}:{hour_b}:{gender_b}"
sorted_keys = sorted([person_a, person_b])
cache_key = f"saju:compatibility:{sorted_keys[0]}:{sorted_keys[1]}"
```

### Redis TTL 전략

```python
# 기본 사주 풀이: 동일 입력이면 결과가 변하지 않으므로 장기 캐싱
SAJU_RESULT_TTL = 60 * 60 * 24 * 30  # 30일

# 오늘의 운세: 매일 갱신
DAILY_FORTUNE_TTL = 60 * 60 * 24  # 24시간

# 월간/연간 운세
MONTHLY_FORTUNE_TTL = 60 * 60 * 24 * 7  # 7일
```

---

## DB 스키마 설계 (PostgreSQL)

```sql
-- 사주 결과 캐시 테이블
CREATE TABLE saju_results (
    id            SERIAL PRIMARY KEY,
    cache_key     VARCHAR(255) UNIQUE NOT NULL,  -- 캐시 키 (조회용)
    birth_year    INT NOT NULL,
    birth_month   INT NOT NULL,
    birth_day     INT NOT NULL,
    birth_hour    INT NOT NULL,
    gender        VARCHAR(1),
    question_type VARCHAR(50) NOT NULL,

    -- 만세력 데이터 (구조화)
    saju_data     JSONB NOT NULL,  -- 사주 원국 (천간, 지지, 오행 등)

    -- LLM 응답
    result_text   TEXT NOT NULL,   -- 사주 해석 결과
    model_used    VARCHAR(50),     -- 사용한 LLM 모델명

    created_at    TIMESTAMP DEFAULT NOW(),
    updated_at    TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_saju_cache_key ON saju_results(cache_key);

-- 사용자 테이블
CREATE TABLE users (
    id            SERIAL PRIMARY KEY,
    email         VARCHAR(255) UNIQUE,
    nickname      VARCHAR(100),
    created_at    TIMESTAMP DEFAULT NOW()
);

-- 사용자 조회 기록 (히스토리 + 통계용)
CREATE TABLE user_queries (
    id              SERIAL PRIMARY KEY,
    user_id         INT REFERENCES users(id),
    saju_result_id  INT REFERENCES saju_results(id),
    queried_at      TIMESTAMP DEFAULT NOW()
);

-- 결제 내역
CREATE TABLE payments (
    id            SERIAL PRIMARY KEY,
    user_id       INT REFERENCES users(id),
    amount        INT NOT NULL,
    payment_type  VARCHAR(50),  -- 'premium_saju', 'compatibility', etc.
    status        VARCHAR(20),  -- 'pending', 'completed', 'refunded'
    created_at    TIMESTAMP DEFAULT NOW()
);
```

---

## 최적화 전략

### 1. LLM 호출 비용 최적화

```python
# 프롬프트 템플릿화: 시스템 프롬프트는 고정, 사주 데이터만 변수로
SYSTEM_PROMPT = """
당신은 전문 사주 역학가입니다.
주어진 사주 원국 데이터를 기반으로 정확하고 구체적인 해석을 제공합니다.
...
"""

# 사주 데이터를 구조화하여 전달 → 토큰 절약
user_prompt = f"""
[사주 원국]
- 연주: {year_pillar}
- 월주: {month_pillar}
- 일주: {day_pillar}
- 시주: {hour_pillar}
- 오행 분포: {five_elements}
- 용신: {yong_sin}

[질문]: {question_type}에 대해 해석해주세요.
"""
```

**비용 절감 포인트:**

- 동일 사주 + 동일 질문유형은 캐시에서 서빙 → LLM 호출 0회
- 시스템 프롬프트를 짧고 정확하게 유지 → 입력 토큰 절약
- 응답 max_tokens 제한 설정 → 불필요하게 긴 응답 방지
- Claude의 prompt caching 기능 활용: 시스템 프롬프트 캐싱으로 반복 호출 시 비용 절감

### 2. 만세력 계산 최적화

```python
# 만세력은 순수 연산이므로 LLM 호출 없이 Python으로 직접 계산
# 추천 라이브러리: lunarcalendar, korean-lunar-calendar
# 만세력 결과도 캐싱 가능 (동일 생년월일시 → 동일 사주)

from functools import lru_cache

@lru_cache(maxsize=10000)
def calculate_saju(year: int, month: int, day: int, hour: int) -> dict:
    """만세력 기반 사주 원국 계산 (메모리 캐시)"""
    # 천간, 지지, 오행 계산 로직
    ...
    return {
        "year_pillar": {...},
        "month_pillar": {...},
        "day_pillar": {...},
        "hour_pillar": {...},
        "five_elements": {...},
    }
```

### 3. API 응답 속도 최적화

```python
# Streaming 응답: LLM 결과를 실시간으로 프론트에 전달
from fastapi.responses import StreamingResponse

@app.post("/api/saju/interpret")
async def interpret_saju(request: SajuRequest):
    # 캐시 HIT → 즉시 전체 응답
    cached = await get_cached_result(request)
    if cached:
        return {"result": cached, "cached": True}

    # 캐시 MISS → LLM 스트리밍 응답
    return StreamingResponse(
        stream_llm_response(request),
        media_type="text/event-stream"
    )
```

### 4. Rate Limiting (Redis 활용)

```python
# 무료 사용자: 하루 3회 제한
# 유료 사용자: 무제한

async def check_rate_limit(user_id: str, is_premium: bool) -> bool:
    if is_premium:
        return True

    key = f"rate_limit:{user_id}:{today}"
    count = await redis.incr(key)
    if count == 1:
        await redis.expire(key, 86400)  # 24시간 TTL

    return count <= 3
```

### 5. 프론트엔드 최적화 (Next.js)

```
- SSG로 정적 페이지 (홈, 소개, 가격 페이지 등) 사전 렌더링
- 사주 입력 폼 → Client Component
- 사주 결과 페이지 → Server Component + Suspense로 로딩 처리
- 결과 페이지 URL에 해시값 포함하여 공유/북마크 가능하게
  예: /result?key=abc123 → 해당 키로 API 조회
```

### 6. SEO & 마케팅 최적화

```
- /saju/[type] 형태로 운세 종류별 랜딩 페이지 SSG 생성
  예: /saju/overall, /saju/love, /saju/career
- 메타 태그, OG 이미지 동적 생성 (사주 결과 공유 시)
- 블로그 섹션: 사주 관련 콘텐츠 (오행이란?, 용신이란?) → 검색 유입
```

### 7. 모니터링 & 분석

```python
# 캐시 히트율 추적
async def track_cache_metrics(hit: bool, source: str):
    """source: 'redis', 'postgres', 'llm'"""
    key = f"metrics:cache:{today}:{source}"
    await redis.incr(key)

# 인기 질문 유형 추적 → 프롬프트 최적화에 활용
async def track_query_type(question_type: str):
    key = f"metrics:query_type:{today}"
    await redis.hincrby(key, question_type, 1)
```

---

## 디렉토리 구조 (참고)

```
saju-app/
├── frontend/                  # Next.js
│   ├── app/
│   │   ├── page.tsx          # 홈
│   │   ├── saju/
│   │   │   ├── page.tsx      # 사주 입력 폼
│   │   │   └── result/
│   │   │       └── page.tsx  # 결과 페이지
│   │   └── api/              # 사용하지 않음 (Python API로 위임)
│   └── lib/
│       └── api-client.ts     # Python API 호출 래퍼
│
├── backend/                   # Python API
│   ├── main.py               # FastAPI 엔트리포인트
│   ├── routers/
│   │   ├── saju.py           # 사주 관련 엔드포인트
│   │   ├── auth.py           # 인증
│   │   └── payment.py        # 결제
│   ├── services/
│   │   ├── saju_calculator.py    # 만세력 계산
│   │   ├── llm_service.py        # LLM API 호출
│   │   └── cache_service.py      # Redis + DB 캐싱 로직
│   ├── models/                   # SQLAlchemy 모델
│   └── config.py
│
└── docker-compose.yml         # Redis + PostgreSQL + API + Frontend
```

---

## 향후 확장 고려사항

- **모바일 앱**: Python API를 그대로 사용 (프론트만 React Native로 추가)
- **관리자 대시보드**: Python API에 admin 라우터 추가
- **A/B 테스트**: 다른 프롬프트로 생성한 결과 비교 → 사용자 만족도 높은 프롬프트 채택
- **다국어 지원**: 프롬프트에 언어 파라미터 추가, 캐시 키에도 언어 포함
