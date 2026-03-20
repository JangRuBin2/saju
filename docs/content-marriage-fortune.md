# 연애 상대와 결혼운 컨텐츠 기획

## 1. 컨텐츠 개요

### 1.1 컨셉

"우리의 결혼 시계" - 연애 중인 두 사람의 사주를 분석하여 결혼 적기, 결혼 후 궁합,
피해야 할 시기, 결혼 생활에서 주의할 점을 종합 분석하는 프리미엄 컨텐츠.

### 1.2 기존 컨텐츠와의 차별화

| 기존 컨텐츠 | 신규 컨텐츠 |
|------------|------------|
| 궁합 분석: 두 사람의 오행 조화 (정적 분석) | 결혼운: 시기별 운세 흐름 포함 (동적 분석) |
| 결혼운 (reading): 본인 사주만 분석 | 두 사람의 사주를 동시에 분석 |
| 단순 "잘 맞다/안 맞다" | 구체적 시기 + 행동 가이드 |

### 1.3 타겟 사용자

- 결혼을 구체적으로 고려 중인 커플
- 결혼 시기를 고민하는 장기 연애 커플
- 양가 상견례/결혼 날짜를 잡으려는 커플
- 결혼에 대한 막연한 불안이 있는 사람

---

## 2. 사용자 입력 설계

### 2.1 기본 정보 (필수)

| 입력 항목 | 필수 | 설명 |
|----------|------|------|
| 본인 생년월일시 | 필수 | 사주 원국 계산 |
| 본인 성별 | 필수 | 대운 방향 |
| 상대방 생년월일시 | 필수 | 사주 원국 계산 |
| 상대방 성별 | 필수 | 대운 방향 |

### 2.2 관계 정보 (선택이지만 분석 품질 향상)

| 입력 항목 | 필수 | 용도 |
|----------|------|------|
| 교제 시작 연도 | 선택 | 만남 시점의 운세 역추적 |
| 교제 기간 (년) | 선택 | 관계 단계 판단 |
| 결혼 희망 시기 | 선택 | 해당 시기 집중 분석 |
| 고민 유형 | 선택 | 분석 초점 결정 |
| 동거 여부 | 선택 | 관계 단계 보조 정보 |

### 2.3 고민 유형 (택1)

```
marriage_concern:
  - when: "언제 결혼하는 게 가장 좋을까"
  - readiness: "우리가 결혼할 준비가 되었는지"
  - compatibility: "결혼 후에도 잘 살 수 있을지"
  - family: "양가 관계가 걱정된다"
  - finance: "결혼 후 재물운이 궁금하다"
  - children: "결혼 후 자녀운이 궁금하다"
```

---

## 3. 분석 프레임워크

### 3.1 결혼 적기 판단 기준 (사주 역학)

```
결혼 유리 신호:
- 남성: 재성(財星)이 강해지는 대운/세운 (정재=정실, 편재=인연)
- 여성: 관성(官星)이 강해지는 대운/세운 (정관=정배우자, 편관=인연)
- 공통: 일지(日支)와 합(合)이 되는 세운
- 공통: 도화살(桃花殺)이 동(動)하는 시기
- 공통: 천을귀인(天乙貴人)이 오는 시기

결혼 주의 신호:
- 형충파해(刑沖破害)가 겹치는 해 -> 변동이 큰 시기
- 공망(空亡)에 해당하는 시기 -> 허무한 기운
- 역마살(驛馬殺)이 강한 시기 -> 이동/불안정
- 대운 교체기 (전후 1년) -> 큰 변화기
```

### 3.2 결혼 궁합 심화 분석

기존 궁합 분석(오행 조화)에 추가:

```
1. 일주(日柱) 궁합 - 가장 중요
   - 일간(日干) 합: 갑기합(甲己合), 을경합(乙庚合) 등 -> 천생연분
   - 일지(日支) 합: 자축합(子丑合), 인해합(寅亥合) 등 -> 생활 조화
   - 일지 충: 자오충(子午沖), 묘유충(卯酉沖) 등 -> 갈등 요소

2. 궁성(宮星) 분석
   - 배우자궁(日支)의 상태: 길신이면 좋은 배우자 인연
   - 배우자성(財星/官星)의 위치와 강도

3. 결혼 후 대운 동조 분석
   - 두 사람의 대운이 같은 방향으로 흐르는지
   - 한 쪽이 좋을 때 다른 쪽은 어떤지
   - 가장 시너지가 나는 시기/갈등 가능 시기

4. 재물운 동조 분석
   - 결혼 후 공동 재물운 흐름
   - 재성(財星) 방향이 일치하는지
```

### 3.3 결혼 생활 단계별 분석

```
1단계: 신혼기 (결혼 후 1~3년)
  - 적응 궁합: 생활 습관 충돌 가능성
  - 재물: 결혼 초기 재정 안정도

2단계: 정착기 (결혼 후 3~7년)
  - 자녀운: 출산 적기 (시주+세운 분석)
  - 커리어: 결혼 후 직업 변화 가능성
  - 위기: 권태기 가능 시점

3단계: 성숙기 (결혼 후 7~15년)
  - 대운 흐름 변화에 따른 관계 변화
  - 재물 축적 패턴
  - 건강 주의 시기
```

---

## 4. 세부 컨텐츠 구성

### 4.1 결혼 타이밍 분석 (핵심)

**컨텐츠명:** "우리의 결혼 골든타임"

출력 구성:
```
1. 두 사람의 결혼 인연 분석
   - 일주 궁합 (천간합/지지합 여부)
   - 배우자궁/배우자성 상태
   - 만남 시점의 운세 역추적 (교제 시작 연도 입력 시)

2. 결혼 적기 판단
   - 두 사람의 운세가 동시에 좋은 시기 (교집합)
   - 향후 36개월 중 결혼 유리 시기 TOP 3
   - 피해야 할 시기와 이유
   - 대운 교체기 주의사항

3. 결혼 날짜 참고
   - 사주적으로 유리한 월 (택일 참고)
   - 피해야 할 월
   - "정확한 택일은 전문 역술인 상담을 권장합니다" 안내

4. 결혼 전 준비 조언
   - 사주 기반 관계 강화 포인트
   - 주의해야 할 갈등 요소 (오행 상극 기반)
   - 양가 관계 운세 (간략)
```

### 4.2 결혼 후 궁합 심화

**컨텐츠명:** "우리의 결혼 생활 예보"

출력 구성:
```
1. 결혼 생활 종합 궁합
   - 소통 궁합 (일간 관계)
   - 생활 궁합 (일지 관계)
   - 재물 궁합 (재성 비교)
   - 가정 궁합 (인성 비교)
   - 종합 점수

2. 결혼 후 10년 흐름 예보
   - 연도별 핵심 키워드 (1줄씩)
   - 특히 좋은 해 / 주의할 해
   - 대운 교체에 따른 관계 변화 포인트

3. 갈등 예방 가이드
   - 두 사람의 오행 상극 포인트
   - 갈등이 심화될 수 있는 시기
   - 갈등 해소에 도움이 되는 오행 활동

4. 자녀운 (간략)
   - 자녀 인연의 강도 (시주 기반)
   - 출산에 유리한 시기 (세운 기반)
```

### 4.3 결혼 재물운

**컨텐츠명:** "우리 부부의 돈 지도"

출력 구성:
```
1. 개인별 재물 패턴
   - 각자의 재성 구조 분석
   - 재물 축적 성향 (저축형 vs 투자형 vs 소비형)

2. 부부 공동 재물운
   - 합산 재물 패턴 시너지 분석
   - 누가 재물 관리를 맡으면 좋은지
   - 공동 투자 적기

3. 연도별 재물 흐름 (5년)
   - 수입 증가 예상 시기
   - 큰 지출 주의 시기 (이사, 차량 등)
   - 재산 형성 황금기
```

### 4.4 결혼 날짜 길일 분석

**컨텐츠명:** "우리만의 좋은 날"

출력 구성:
```
1. 두 사람 사주 기반 길월(吉月) 분석
   - 올해/내년 중 결혼에 좋은 달 TOP 3
   - 피해야 할 달과 이유

2. 월별 길일 경향
   - 선택한 달 내에서 좋은 날의 특성
   - 요일/시간대 참고 (간지 기반)

3. 주의사항
   - "본 분석은 사주 역학 기반 참고 정보입니다"
   - "정확한 택일은 전문 역술인 상담을 권장합니다"
   - 손 없는 날 등 전통 택일 기본 정보 안내
```

---

## 5. API 설계

### 5.1 결혼 타이밍 분석

```
POST /api/v1/marriage/timing
Body: {
  "person1": {
    "year": 1992, "month": 8, "day": 15,
    "hour": 10, "gender": "male"
  },
  "person2": {
    "year": 1994, "month": 3, "day": 22,
    "hour": 16, "gender": "female"
  },
  "relationship_info": {
    "dating_start_year": 2022,     // 선택
    "dating_years": 4,             // 선택
    "target_marriage_year": 2027,  // 선택
    "concern_type": "when",        // 선택
    "living_together": false       // 선택
  },
  "language": "ko"
}
Response: {
  "person1_calculation": { ... },
  "person2_calculation": { ... },
  "marriage_affinity": {
    "day_stem_harmony": "갑기합 - 천생연분의 조합",
    "day_branch_harmony": "...",
    "spouse_palace_status": "...",
    "overall_affinity": 88
  },
  "timing": {
    "best_periods": [
      {
        "year": 2027, "months": [3, 4, 9],
        "score": 92,
        "reason": "두 사람 모두 재성/관성이 강해지는 시기"
      }
    ],
    "caution_periods": [
      {
        "year": 2026, "months": [7, 8],
        "reason": "형충이 겹치는 변동기"
      }
    ],
    "dayun_change_alert": "..."
  },
  "interpretation": "...",
  "preparation_tips": "..."
}
```

### 5.2 결혼 생활 궁합 심화

```
POST /api/v1/marriage/life-forecast
Body: {
  "person1": {
    "year": 1992, "month": 8, "day": 15,
    "hour": 10, "gender": "male"
  },
  "person2": {
    "year": 1994, "month": 3, "day": 22,
    "hour": 16, "gender": "female"
  },
  "marriage_year": 2027,  // 선택: 결혼 예정 연도
  "language": "ko"
}
Response: {
  "person1_calculation": { ... },
  "person2_calculation": { ... },
  "compatibility_scores": {
    "communication": 85,
    "lifestyle": 78,
    "finance": 82,
    "family": 90,
    "intimacy": 76,
    "overall": 82
  },
  "decade_forecast": [
    { "year": 2027, "keyword": "설렘과 적응", "tone": "positive" },
    { "year": 2028, "keyword": "안정의 시작", "tone": "positive" },
    { "year": 2029, "keyword": "재물 성장기", "tone": "positive" },
    ...
  ],
  "conflict_prevention": {
    "clash_points": ["..."],
    "risk_periods": ["..."],
    "resolution_activities": ["..."]
  },
  "children_fortune": {
    "affinity_strength": "strong",
    "favorable_years": [2028, 2030],
    "brief_analysis": "..."
  },
  "interpretation": "..."
}
```

### 5.3 결혼 재물운

```
POST /api/v1/marriage/finance
Body: {
  "person1": {
    "year": 1992, "month": 8, "day": 15,
    "hour": 10, "gender": "male"
  },
  "person2": {
    "year": 1994, "month": 3, "day": 22,
    "hour": 16, "gender": "female"
  },
  "marriage_year": 2027,
  "language": "ko"
}
Response: {
  "person1_calculation": { ... },
  "person2_calculation": { ... },
  "individual_finance": {
    "person1": { "pattern": "투자형", "strengths": "...", "cautions": "..." },
    "person2": { "pattern": "저축형", "strengths": "...", "cautions": "..." }
  },
  "combined_finance": {
    "synergy": "...",
    "money_manager_recommendation": "person2",
    "investment_timing": "..."
  },
  "five_year_forecast": [
    { "year": 2027, "trend": "안정", "event": "신혼 정착 비용" },
    { "year": 2028, "trend": "상승", "event": "수입 증가 기대" },
    ...
  ],
  "interpretation": "..."
}
```

### 5.4 결혼 길일 분석

```
POST /api/v1/marriage/auspicious-dates
Body: {
  "person1": {
    "year": 1992, "month": 8, "day": 15,
    "hour": 10, "gender": "male"
  },
  "person2": {
    "year": 1994, "month": 3, "day": 22,
    "hour": 16, "gender": "female"
  },
  "target_year": 2027,
  "target_months": [3, 4, 9, 10],  // 선택: 특정 월만 분석
  "language": "ko"
}
Response: {
  "person1_calculation": { ... },
  "person2_calculation": { ... },
  "auspicious_months": [
    { "month": 4, "score": 95, "reason": "두 사람 모두에게 길한 달" },
    { "month": 9, "score": 88, "reason": "재물운과 가정운이 동시에 좋음" }
  ],
  "avoid_months": [
    { "month": 7, "reason": "충(沖)이 겹치는 시기" }
  ],
  "general_guidelines": "...",
  "disclaimer": "정확한 택일은 전문 역술인 상담을 권장합니다",
  "interpretation": "..."
}
```

---

## 6. 프롬프트 설계 원칙

### 6.1 핵심 원칙

```
1. 두 사람 모두를 존중하는 톤 - 한쪽을 폄하하지 않음
2. 궁합이 안 좋아도 해결책 중심으로 프레이밍
3. "안 맞으니 헤어지세요" 류의 조언 절대 금지
4. 결혼은 개인의 선택임을 전제 - 사주는 참고 정보
5. 구체적 시기 제시 시 근거(어떤 간지, 어떤 신살)를 함께 설명
6. 자녀운은 민감 주제 -> 간략하게만, 단정 금지
```

### 6.2 금지 사항

```
- "이 사람과 결혼하면 안 됩니다" (결혼 반대 금지)
- "이혼할 수 있습니다" (이혼 예측 금지)
- "자녀가 없을 수 있습니다" (무자녀 단정 금지)
- "바람을 피울 수 있습니다" (외도 예측 금지)
- "시댁/처가와 안 맞습니다" (가족 갈등 단정 금지)
- 구체적 건강 문제 예측 금지
- 특정 종교/문화적 관행 강요 금지
```

### 6.3 부정적 결과 리프레이밍 가이드

| 원래 해석 | 리프레이밍 |
|----------|----------|
| 일지 충(沖): 성격 충돌 | "서로 다른 에너지로 균형을 이루는 관계. 차이를 인정하면 더 깊은 이해로" |
| 관성 약함: 결혼 인연 약함 | "자유로운 영혼의 소유자. 형식보다 진심이 중요한 관계 스타일" |
| 재성 충돌: 재물 갈등 | "재물에 대한 가치관이 달라 서로 배울 점이 많은 조합" |
| 도화살 강함: 이성 문제 | "매력적이고 사교적인 성향. 파트너에게 집중하면 큰 에너지" |

### 6.4 면책조항

```
본 분석은 전통 역학에 기반한 참고 정보이며,
결혼에 대한 최종 결정은 두 사람의 대화와 합의가 가장 중요합니다.
택일(결혼 날짜 선정)은 참고용이며, 정확한 택일이 필요하시면
전문 역술인 상담을 권장합니다.
건강, 재정, 법률 관련 중요한 결정은 각 분야 전문가와 상의하세요.
```

---

## 7. 수익 모델

| 컨텐츠 | 판매가 (VAT 포함) | 모델 | API 비용 | max_tokens |
|---------|-------------------|------|----------|------------|
| 결혼 타이밍 분석 | 8,800원 | Sonnet | ~67원 | 3,000 |
| 결혼 생활 궁합 심화 | 8,800원 | Sonnet | ~67원 | 3,000 |
| 결혼 재물운 | 5,500원 | Sonnet | ~46원 | 2,000 |
| 결혼 길일 분석 | 5,500원 | Sonnet | ~46원 | 2,000 |
| 결혼 종합 패키지 (전체) | 22,000원 | Sonnet | ~180원 | 8,000 |

### 가격 근거

- 기존 "부부 궁합 심화" 8,800원과 동일 가격대
- 결혼 관련 의사결정은 인생에서 가장 큰 결정 중 하나 -> 프리미엄 가격 수용도 매우 높음
- 오프라인 궁합/택일 상담: 10~30만원 -> 온라인 AI 분석은 1/10 수준
- 종합 패키지 22,000원: 개별 구매 대비 24% 할인 효과

---

## 8. 구현 우선순위

```
Phase 1 (핵심):
  1. 결혼 타이밍 분석 - 가장 높은 수요, 핵심 차별화
  2. 결혼 생활 궁합 심화 - 기존 궁합의 프리미엄 업그레이드

Phase 2 (확장):
  3. 결혼 길일 분석 - 결혼 준비 단계 수요
  4. 결혼 재물운 - 현실적 관심사

Phase 3 (프리미엄):
  5. 결혼 종합 패키지 - Phase 1~2 통합 상품
```

---

## 9. 기술 구현 사항

### 9.1 모델 레이어

```python
class MarriageConcernType(str, Enum):
    WHEN = "when"
    READINESS = "readiness"
    COMPATIBILITY = "compatibility"
    FAMILY = "family"
    FINANCE = "finance"
    CHILDREN = "children"

class RelationshipInfo(BaseModel):
    dating_start_year: int | None = Field(None, ge=2000, le=2030)
    dating_years: int | None = Field(None, ge=0, le=30)
    target_marriage_year: int | None = Field(None, ge=2024, le=2035)
    concern_type: MarriageConcernType | None = None
    living_together: bool | None = None

class MarriageTimingRequest(BaseModel):
    person1: BirthInput
    person2: BirthInput
    relationship_info: RelationshipInfo | None = None
    language: Language = Language.KO

class MarriageLifeForecastRequest(BaseModel):
    person1: BirthInput
    person2: BirthInput
    marriage_year: int | None = None
    language: Language = Language.KO
```

### 9.2 서비스 레이어

- `MarriageService`: 결혼 전용 서비스
- 두 사람의 사주를 동시에 계산하고 교차 분석
- 기존 `CompatibilityService`의 궁합 로직을 확장
- 대운/세운 교차 분석: 두 사람의 운세가 동시에 좋은 시기 탐색

### 9.3 엔진 레이어 확장

```
신규 계산 필요:
- 일간합(日干合) 판정: 갑기합, 을경합, 병신합, 정임합, 무계합
- 일지합(日支合) 판정: 자축합, 인해합, 묘술합, 진유합, 사신합, 오미합
- 일지충(日支沖) 판정: 자오충, 축미충, 인신충, 묘유충, 진술충, 사해충
- 배우자궁(日支) 분석: 길신/흉신 판정
- 도화살(桃花殺) 동(動) 여부: 세운 지지와 도화살 관계
- 두 사람 대운/세운 교집합 산출
```

### 9.4 기존 컴포넌트 재활용

| 기존 컴포넌트 | 재활용 방식 |
|-------------|------------|
| SajuCalculator | 두 사람 사주 각각 계산 |
| CompatibilityService | 기본 궁합 로직 위임 |
| FortuneService | 세운/월운 계산 로직 |
| DaYun 계산 | 대운 흐름 분석 |
