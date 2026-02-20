# Architecture Rules

## System Architecture

```
[사용자] -> [Next.js Frontend (향후)]
                |
                v
         [Python API Server (FastAPI)]
                |
        +-------+-------+
        v       v       v
     [Redis]  [PostgreSQL]  [LLM API]
     (캐시)   (영구저장)     (사주해석)
```

## Core Principle: Python API가 모든 비즈니스 로직 담당

- Next.js는 순수 프론트엔드 역할만 수행 (DB 직접 접근 없음)
- Python API가 캐싱, DB, LLM 호출, 만세력 계산 전부 담당
- 모바일 앱(React Native) 추가 시 API 재사용 가능

## 요청 흐름

```
1. 사용자가 생년월일시 + 질문유형 입력
2. Frontend -> Python API 호출
3. Python API 내부 처리:
   a. 캐시 키 생성 (해시 기반)
   b. Redis 캐시 조회 -> HIT이면 즉시 반환
   c. PostgreSQL 조회 (Redis 만료 후에도 영구 데이터 존재 가능)
   d. 만세력 계산 (lunar-python, 순수 연산)
   e. LLM API 호출 (만세력 데이터 + 프롬프트)
   f. 결과를 Redis + PostgreSQL 양쪽에 저장
   g. 응답 반환
```

## 레이어 구조

| 레이어 | 디렉토리 | 역할 | I/O |
|--------|----------|------|-----|
| Engine | app/engine/ | 순수 만세력 계산 | 동기, 외부 I/O 없음 |
| LLM | app/llm/ | Claude API 호출, 프롬프트 관리 | 비동기 |
| Services | app/services/ | 계산+해석 오케스트레이션, 캐싱 | 비동기 |
| Routers | app/routers/ | HTTP 요청/응답 처리 | 비동기 |
| Models | app/models/ | Pydantic 스키마 | 없음 |
| Middleware | app/middleware/ | 에러 핸들링 | 없음 |

## 의존성 방향 (위에서 아래로만)

```
Routers -> Services -> Engine
                    -> LLM
                    -> Cache
```

- Router는 Service만 호출
- Service는 Engine, LLM, Cache를 조합
- Engine은 다른 레이어에 의존하지 않음 (순수 계산)
- LLM은 Engine에 의존하지 않음

## 캐시 키 설계

```python
# 기본 사주: 해시 기반 (PII 보호)
"saju:reading:a1b2c3d4e5f6g7h8"

# 궁합: 두 사람 키를 정렬하여 일관성 유지
"saju:compat:sorted_hash"

# 운세: 대상 날짜 포함
"saju:daily:hash_with_target_date"
```

## Redis TTL 전략

| 데이터 | TTL | 이유 |
|--------|-----|------|
| 사주 계산 결과 | 30일 | 동일 입력 = 동일 결과 (결정적) |
| LLM 해석 결과 | 1시간 | 같은 사주라도 해석 다양성 허용 |
| 일일 운세 | 24시간 | 매일 갱신 |
| 월간 운세 | 7일 | 주 1회 갱신 |

## DB 스키마 (PostgreSQL, 향후 구현)

```sql
-- 사주 결과 영구 캐시
saju_results (cache_key, saju_data JSONB, result_text, model_used, created_at)

-- 사용자
users (id, email, nickname, created_at)

-- 조회 기록
user_queries (user_id, saju_result_id, queried_at)

-- 결제
payments (user_id, amount, payment_type, status, created_at)
```

## LLM 비용 최적화

1. 동일 사주 + 동일 질문유형은 캐시에서 서빙 (LLM 호출 0회)
2. 시스템 프롬프트에 `cache_control: {"type": "ephemeral"}` (비용 90% 절감)
3. 시스템 프롬프트를 짧고 정확하게 유지 (입력 토큰 절약)
4. `max_tokens` 제한 설정 (불필요하게 긴 응답 방지)
5. 만세력 계산은 Python으로 직접 (LLM에 절대 위임하지 않음)

## Rate Limiting (향후)

```python
# 무료 사용자: 하루 3회
# 유료 사용자: 무제한
rate_limit_key = f"rate_limit:{user_id}:{today}"
```

## 스트리밍 응답

```python
# 캐시 HIT -> 즉시 전체 응답
# 캐시 MISS -> SSE 스트리밍
#   1. 계산 결과 먼저 전송 (event: calculation)
#   2. LLM 해석 스트리밍 (event: interpretation)
#   3. 완료 (event: done)
```

## 향후 확장

- Next.js 프론트엔드 추가
- PostgreSQL 영구 저장소
- 모바일 앱 (React Native) - API 재사용
- 관리자 대시보드
- A/B 테스트 (프롬프트 비교)
- 다국어 지원
