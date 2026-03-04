# LLM 비용 최적화 전략

## 현재 비용 구조

### 요청 1건당 토큰/비용 (Claude Sonnet 기준)

| 구분 | 토큰 수 | 비용 |
|------|---------|------|
| System prompt (캐시 HIT) | ~300 | $0.00009 |
| 사주 데이터 + 프롬프트 (입력) | ~1,100 | $0.0033 |
| 해석 출력 (평균) | ~1,500 | $0.0225 |
| **합계 (1건)** | **~2,900** | **~$0.026** |

- 출력 토큰이 전체 비용의 86%
- 현재 20개 읽기 유형이 모두 Sonnet 사용
- Redis 캐시(해석 1시간, 운세 24시간)로 중복 호출 절감 중

---

## Phase 1: 멀티모델 라우팅 (즉시 적용 가능)

### 개요

모든 해석을 Sonnet에 보내지 않고, 컨텐츠 품질 요구 수준에 따라 모델을 분리한다.

### 모델 티어링

| 티어 | 모델 | 건당 비용 | 대상 컨텐츠 |
|------|------|-----------|-------------|
| Premium | Claude Sonnet | ~$0.026 | 종합 사주, 궁합, 연예인 궁합, 이직 타이밍 |
| Standard | Claude Haiku / Gemini Pro | ~$0.005 | 관계 사주(4종), 재물운, 숨은 재능, 월운, 신살 |
| Light | Gemini Flash | ~$0.001 | 일운, 시간 운세(3종), 전생 사주 |

### 타입별 모델 매핑

```python
MODEL_TIER: dict[str, str] = {
    # Premium - Claude Sonnet (높은 품질 필요)
    "saju_reading": "claude-sonnet-4-5-20250514",
    "compatibility": "claude-sonnet-4-5-20250514",
    "celebrity_compatibility": "claude-sonnet-4-5-20250514",
    "situation_career_change": "claude-sonnet-4-5-20250514",

    # Standard - Claude Haiku (적절한 품질)
    "love_reading": "claude-haiku-4-5-20251001",
    "friendship_reading": "claude-haiku-4-5-20251001",
    "marriage_reading": "claude-haiku-4-5-20251001",
    "sinsal": "claude-haiku-4-5-20251001",
    "relationship_lover": "claude-haiku-4-5-20251001",
    "relationship_boss": "claude-haiku-4-5-20251001",
    "relationship_child": "claude-haiku-4-5-20251001",
    "relationship_friend": "claude-haiku-4-5-20251001",
    "situation_wealth_flow": "claude-haiku-4-5-20251001",
    "situation_hidden_talent": "claude-haiku-4-5-20251001",
    "monthly": "claude-haiku-4-5-20251001",

    # Light - Gemini Flash (간단한 컨텐츠)
    "daily": "gemini-2.0-flash",
    "timing_now": "gemini-2.0-flash",
    "timing_best_hours": "gemini-2.0-flash",
    "timing_dday": "gemini-2.0-flash",
    "situation_past_life": "gemini-2.0-flash",
}
```

### 예상 비용 절감

트래픽 비율 가정: Light 60% / Standard 30% / Premium 10%

| 지표 | 현재 (전부 Sonnet) | Phase 1 적용 후 |
|------|-------------------|----------------|
| 건당 평균 비용 | $0.026 | $0.005 |
| 절감율 | - | **~80%** |
| 1,000건/일 월비용 | $780 | $150 |
| 5,000건/일 월비용 | $3,900 | $750 |

### 구현 범위

1. `app/llm/client.py` - Gemini client 추가 (google-generativeai SDK)
2. `app/llm/client.py` - `generate(prompt, model_override=None)` 파라미터 추가
3. `app/llm/model_router.py` - 읽기 유형별 모델 매핑 딕셔너리
4. `app/config.py` - `GEMINI_API_KEY` 설정 추가
5. 각 서비스에서 reading_type을 model_router에 전달

---

## Phase 2: 사주 지식 베이스 + RAG (MAU 1만+)

### 개요

LLM에게 "사주 전문가가 되어라"라고 시키는 대신, 사주 해석 규칙을 구조화된 지식으로 분리하고
LLM에게는 "이 규칙을 바탕으로 글을 써라"만 시키는 방식.

```
현재:  사주 데이터 → [LLM이 사주 지식 + 문장 생성 모두 담당] → 해석
개선:  사주 데이터 → [룰엔진이 해석 요소 추출] → [저가 LLM이 문장 생성] → 해석
```

### 사주 지식 베이스 구축 범위

| 항목 | 조합 수 | 내용 |
|------|---------|------|
| 일간별 기본 성격 | 10 | 갑목, 을목, 병화... 각각의 특성 |
| 십신 해석 | 10 x 4(위치) | 정관이 연주/월주/일주/시주에 있을 때 |
| 오행 균형 패턴 | ~20 | 목다, 화다, 수부족 등 불균형 해석 |
| 상생/상극 관계 | 25 | 오행 간 관계별 영향 |
| 12운성 해석 | 12 | 건록, 제왕, 묘 등 |
| 대운 해석 규칙 | ~20 | 대운 천간/지지와 일간 관계 |
| 신살 해석 | ~30 | 주요 신살별 의미 |
| **합계** | **~500항목** | |

### 효과

- LLM의 사주 지식 의존도 제거
- 해석 일관성 향상 (같은 사주 = 같은 규칙 적용)
- Standard 티어도 Gemini Flash + RAG로 전환 가능
- Sonnet 사용을 궁합/종합 사주만으로 축소

### 구현 범위

1. `app/engine/knowledge/` - 사주 해석 규칙 데이터 (JSON/Python)
2. `app/engine/interpreter.py` - 규칙 기반 해석 요소 추출
3. `app/llm/prompts/` - RAG용 프롬프트 (규칙 주입 형식)
4. 초기 구축: 1-2주 예상

---

## Phase 3: 파인튜닝 / 자체 모델 (DAU 1천+)

### 개요

Claude로 생성한 고품질 사주 해석 데이터를 학습 데이터로 활용하여
오픈소스 모델(Llama 3 8B/70B)을 파인튜닝한다.

### 비용 비교

| 항목 | 비용 |
|------|------|
| 학습 데이터 생성 (Claude Sonnet 5,000건) | ~$130 (1회) |
| 파인튜닝 (Llama 3 8B, 클라우드) | ~$50-100 (1회) |
| GPU 호스팅 (추론 서버) | **$150-300/월** (고정비) |

### 손익분기 분석

| 일일 요청 수 | Sonnet 월비용 | 멀티모델(P1) 월비용 | 파인튜닝 월비용 |
|-------------|-------------|-------------------|---------------|
| 100건/일 | $78 | $15 | $150-300 |
| 1,000건/일 | $780 | $150 | $150-300 |
| 5,000건/일 | $3,900 | $750 | $150-300 |
| 10,000건/일 | $7,800 | $1,500 | $300-500 |

- **P1 대비 손익분기: 일 1,000건 이상**
- 서비스 초기에는 P1(멀티모델)이 유리
- 트래픽 증가 시 P3 전환 검토

### 파인튜닝 옵션

| 옵션 | 모델 | 플랫폼 | 장단점 |
|------|------|--------|--------|
| A | Llama 3.1 8B | RunPod/Modal | 저렴, 품질 제한적 |
| B | Llama 3.1 70B | AWS/GCP | 고품질, 고비용 |
| C | GPT-4o-mini (OpenAI FT) | OpenAI API | 관리 편함, 종속성 |
| D | Gemini (Google FT) | Google AI Studio | Gemini 생태계 활용 |

---

## 실행 로드맵

```
Phase 1 (지금)     ─── 멀티모델 라우팅 도입
                       Light 컨텐츠를 Gemini Flash로 전환
                       → 즉시 50-80% 비용 절감

Phase 2 (MAU 1만+) ─── 사주 지식 베이스 구축
                       Standard 티어도 Flash + RAG로 전환
                       → Sonnet 사용을 최소화

Phase 3 (DAU 1천+) ─── 파인튜닝 검토
                       축적된 해석 데이터로 자체 모델 학습
                       → 고정비 구조로 전환
```

### 우선순위

1. **Phase 1 즉시 실행** - ROI 가장 높음, 구현 최소(1-2일)
2. Phase 2는 서비스 안정화 후 - 지식 베이스 품질이 핵심
3. Phase 3는 트래픽 데이터 확보 후 판단
