# Saju API 코드베이스 아키텍처 레퍼런스

> 신규 기능 추가 시 이 문서를 참고하여 기존 패턴을 따를 것.

---

## 1. 파일 위치 맵

```
app/
  config.py              -- Pydantic Settings (env vars)
  dependencies.py        -- DI 컨테이너 (싱글톤 초기화, Depends 함수)
  main.py                -- FastAPI app, 미들웨어, 라우터 등록

  engine/
    models.py            -- frozen dataclass: PillarInfo, DaYunInfo, SajuData
    calculator.py        -- SajuCalculator (순수 동기, I/O 없음)
    constants.py         -- 오행/천간/지지 매핑 상수
    night_zi.py          -- 야자시 처리
    summer_time.py       -- 서머타임 보정
    true_solar_time.py   -- 진태양시 보정

  models/
    common.py            -- Enum: Gender, CalendarType, RelationshipType, SituationType
    request.py           -- 모든 요청 Pydantic 모델
    response.py          -- 모든 응답 Pydantic 모델

  llm/
    client.py            -- LLMClient: generate(), generate_stream()
    formatter.py         -- format_saju_for_prompt(saju) -> markdown
    model_router.py      -- get_model_for_type() (premium->Sonnet, else->Haiku)
    prompts/
      system.py          -- 공통 시스템 프롬프트
      reading_types.py   -- READING_TYPE_PROMPTS dict (프롬프트 디스패처)
      saju_reading.py    -- 종합 사주 감정
      compatibility.py   -- 궁합
      relationship.py    -- 관계별 리딩 (lover, boss, child, friend)
      situation.py       -- 상황별 리딩 (career_change, wealth_flow 등)
      fortune.py         -- 일일/월간 운세
      timing.py          -- 시간별 운세
      celebrity_compatibility.py -- 연예인 궁합

  services/
    saju_service.py      -- 핵심 오케스트레이터
    compatibility_service.py -- 2인 비교 분석
    celebrity_service.py -- 연예인 궁합 (CompatibilityService 위임)
    fortune_service.py   -- 시간 기반 운세
    cache_service.py     -- Redis 캐시 추상화

  routers/
    health.py            -- GET /health
    saju.py              -- POST /api/v1/saju/{calculate,reading,sinsal}
    compatibility.py     -- POST /api/v1/compatibility/analyze
    celebrity.py         -- GET/POST /api/v1/celebrity/{search,compatibility}
    fortune.py           -- POST /api/v1/fortune/{monthly,daily}
    relationship.py      -- POST /api/v1/relationship/reading
    timing.py            -- POST /api/v1/timing/{now,best-hours,dday}

  middleware/
    error_handler.py     -- SajuError 계층, 에러 핸들러
```

---

## 2. 핵심 모델

### 2.1 요청 모델 (request.py)

```python
class BirthInput(BaseModel):
    year: int = Field(..., ge=1900, le=2100)
    month: int = Field(..., ge=1, le=12)
    day: int = Field(..., ge=1, le=31)
    hour: int | None = None
    minute: int | None = None
    gender: Gender
    calendar_type: CalendarType = CalendarType.SOLAR
    is_leap_month: bool = False
    use_night_zi: bool = True
    use_true_solar_time: bool = False
```

모든 요청 모델은 `birth: BirthInput` + `language: str = "ko"` 패턴.

### 2.2 응답 모델 (response.py)

```python
class SajuCalculateResponse(BaseModel):
    solar_date: str
    lunar_date: str
    year_pillar: PillarResponse
    month_pillar: PillarResponse
    day_pillar: PillarResponse
    time_pillar: PillarResponse | None
    day_master: str
    # ... element_counts, da_yun_list 등

class SajuReadingResponse(BaseModel):
    calculation: SajuCalculateResponse
    interpretation: str

class CompatibilityResponse(BaseModel):
    person1_calculation: SajuCalculateResponse
    person2_calculation: SajuCalculateResponse
    interpretation: str
```

### 2.3 엔진 모델 (engine/models.py)

```python
@dataclass(frozen=True)
class SajuData:
    solar_year, solar_month, solar_day, solar_hour, solar_minute
    lunar_year, lunar_month, lunar_day, is_leap_month
    year_pillar, month_pillar, day_pillar, time_pillar  # PillarInfo | None
    day_master, day_master_kor, day_master_element, day_master_yin_yang
    element_counts: dict[str, int]
    da_yun_start_age, da_yun_list: list[DaYunInfo]
    # ... tai_yuan, ming_gong, shen_gong 등
```

---

## 3. 신규 기능 추가 패턴

### 패턴 A: 단일 사주 LLM 리딩 (가장 단순)

```python
# 1. 프롬프트 추가: app/llm/prompts/my_feature.py
MY_PROMPT = """...\n{saju_data}\n..."""

# 2. reading_types.py의 READING_TYPE_PROMPTS에 등록
"my_reading_type": MY_PROMPT

# 3. 라우터 추가: app/routers/my_feature.py
@router.post("/endpoint", response_model=SajuReadingResponse)
async def endpoint(
    request_body: MyRequest,
    service: SajuService = Depends(get_saju_service),
) -> SajuReadingResponse:
    saju, interpretation = await service.reading(
        request_body.birth, "my_reading_type", language=request_body.language,
    )
    return SajuReadingResponse(
        calculation=SajuCalculateResponse(**service.saju_to_dict(saju)),
        interpretation=interpretation,
    )

# 4. main.py에 라우터 등록
app.include_router(my_feature.router)
```

### 패턴 B: 2인 비교 (궁합 계열)

```python
# CompatibilityService.analyze()에 커스텀 프롬프트 전달
saju1, saju2, interp = await compat_service.analyze(
    person1_birth, person2_birth,
    reading_type="my_compat_type",
    prompt_template=MY_COMPAT_PROMPT,
    prompt_kwargs={"extra_key": "extra_value"},
    language=language,
)
```

### 패턴 C: 시간 기반 운세

```python
# FortuneService의 _get_target_period_info() 활용
# 캐시 키에 target_year/month/day 포함
# TTL: cache_ttl_fortune (24시간)
```

---

## 4. 서비스 레이어 핵심

### SajuService

```python
def calculate(birth: BirthInput) -> SajuData          # 순수 계산
async def reading(birth, reading_type, language) -> tuple[SajuData, str]  # 계산+LLM
async def reading_stream(birth, reading_type, language) -> tuple[SajuData, AsyncIterator[str]]
def saju_to_dict(saju: SajuData) -> dict               # 응답 변환
```

### CompatibilityService

```python
async def analyze(person1, person2, reading_type, prompt_template, prompt_kwargs, language)
    -> tuple[SajuData, SajuData, str]
# 캐시 키: 두 사람 정보를 정렬하여 일관성 유지
```

### FortuneService

```python
async def monthly(birth, target_year, target_month, language)
async def daily(birth, target_year, target_month, target_day, language)
async def timing_now(birth, target_year, target_month, target_day, target_hour, language)
# 모두 tuple[SajuData, str, datetime] 반환
```

### CacheService

```python
CacheService.make_key("prefix", y=year, m=month, d=day, ...)
# -> "saju:prefix:a1b2c3d4e5f6g7h8" (SHA256 해시)
```

---

## 5. LLM 레이어 핵심

### 모델 라우팅 (model_router.py)

```python
_PREMIUM_TYPES = {"saju_reading", "compatibility", "celebrity_compatibility", "situation_career_change"}
# Premium -> settings.llm_model (Sonnet)
# 나머지 -> Haiku
```

### 프롬프트 디스패치 (reading_types.py)

```python
READING_TYPE_PROMPTS: dict[str, str] = {
    "saju_reading": SAJU_READING_PROMPT,
    "compatibility": COMPATIBILITY_PROMPT,
    "relationship_lover": RELATIONSHIP_LOVER_PROMPT,
    "situation_career_change": SITUATION_CAREER_CHANGE_PROMPT,
    "monthly_fortune": MONTHLY_FORTUNE_PROMPT,
    # ... 새 타입은 여기에 추가
}

def get_prompt_for_type(reading_type: str) -> str:
    return READING_TYPE_PROMPTS[reading_type]
```

### 포매터 (formatter.py)

```python
format_saju_for_prompt(saju: SajuData) -> str
# 사주 데이터를 마크다운 테이블 형태로 변환
# 사주 + 오행 + 십성 + 지장간 + 12운성 + 대운 포함
```

---

## 6. DI 초기화 (dependencies.py)

```python
# 전역 싱글톤
_saju_service: SajuService | None = None
_compatibility_service: CompatibilityService | None = None
_fortune_service: FortuneService | None = None
_celebrity_service: CelebrityService | None = None

async def init_dependencies():
    # 1. SajuCalculator (동기)
    # 2. AsyncAnthropic -> LLMClient (비동기)
    # 3. Redis -> CacheService (비동기, 선택)
    # 4. 서비스 싱글톤 생성

# 신규 서비스 추가 시:
# 1. 전역 변수 추가
# 2. init_dependencies()에서 생성
# 3. get_xxx_service() Depends 함수 추가
```

---

## 7. main.py 라우터 등록

```python
app.include_router(health.router)
app.include_router(saju.router)
app.include_router(compatibility.router)
app.include_router(celebrity.router)
app.include_router(fortune.router)
app.include_router(relationship.router)
app.include_router(timing.router)
# 신규 라우터는 여기에 추가
```

---

## 8. 에러 처리 (middleware/error_handler.py)

```python
class SajuError(Exception):        # base, status_code=400
class InvalidBirthDateError        # 422
class LunarConversionError         # 422
class LLMError                     # 502
class CelebrityNotFoundError       # 404
```

---

## 9. 신규 기능 추가 체크리스트

1. [ ] 프롬프트 파일 생성: `app/llm/prompts/{feature}.py`
2. [ ] `reading_types.py`의 `READING_TYPE_PROMPTS`에 등록
3. [ ] `model_router.py`의 `_PREMIUM_TYPES`에 추가 (프리미엄이면)
4. [ ] 요청 모델 추가: `app/models/request.py`
5. [ ] 응답 모델 추가 (필요 시): `app/models/response.py`
6. [ ] Enum 추가 (필요 시): `app/models/common.py`
7. [ ] 서비스 추가 (필요 시): `app/services/{feature}_service.py`
8. [ ] DI 등록 (신규 서비스 시): `app/dependencies.py`
9. [ ] 라우터 추가: `app/routers/{feature}.py`
10. [ ] `app/main.py`에 라우터 등록
11. [ ] 테스트 추가: `tests/test_routers/test_{feature}.py`
