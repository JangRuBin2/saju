# 이직/커리어 전환 사주 컨텐츠 기획

## 1. 컨텐츠 개요

### 1.1 컨셉

"사주로 보는 나의 커리어 전환 타이밍" - 현재 직장 상황, 경력 정보를 종합하여
이직 적기, 방향성, 주의사항을 사주 기반으로 분석하는 프리미엄 컨텐츠.

### 1.2 타겟 사용자

- 현 직장에서 이직을 고민 중인 직장인 (3~7년차 핵심)
- 경력 전환(업종 변경)을 고려하는 사람
- 승진 vs 이직을 저울질하는 중간관리자
- 퇴사 후 창업을 고민하는 사람

### 1.3 차별화 포인트

기존 사주 서비스의 "취업운/직업운"은 단순히 사주 원국만 분석.
본 컨텐츠는 **현재 직장 정보 + 대운/세운 흐름 + 사용자 상황**을 종합하여
실질적이고 구체적인 타이밍 조언을 제공.

---

## 2. 사용자 입력 설계

### 2.1 기본 정보 (필수)

| 입력 항목 | 필수 | 용도 |
|----------|------|------|
| 생년월일시 | 필수 | 사주 원국 계산 |
| 성별 | 필수 | 대운 방향 |

### 2.2 직장/경력 정보 (선택이지만 입력 시 분석 품질 향상)

| 입력 항목 | 필수 | 용도 |
|----------|------|------|
| 현재 업종 | 선택 | 업종-오행 매핑으로 적합도 분석 |
| 현재 직무 | 선택 | 직무 성향과 사주 비교 |
| 현 직장 근속 연수 | 선택 | 이직 주기 분석, 대운 흐름과 매칭 |
| 입사 연도 | 선택 | 입사 시점의 운세 흐름 역추적 |
| 연차 (총 경력) | 선택 | 경력 단계별 맞춤 조언 |
| 현재 고민 유형 | 선택 | 분석 초점 결정 |
| 희망 이직 시기 | 선택 | 해당 시기의 운세 집중 분석 |

### 2.3 고민 유형 (택1)

```
career_concern:
  - timing: "지금이 이직할 때인지 알고 싶다"
  - direction: "어떤 업종/직무로 가야 할지 모르겠다"
  - promotion_vs_move: "승진을 기다릴지 이직할지 고민이다"
  - startup: "퇴사 후 창업을 고려 중이다"
  - burnout: "번아웃이 왔는데 쉬어야 할지 옮겨야 할지"
  - salary: "연봉 협상 vs 이직, 어떤 게 나을지"
```

---

## 3. 분석 프레임워크

### 3.1 업종-오행 매핑

사주의 오행과 업종의 오행 속성을 매칭하여 적합도 분석:

| 오행 | 관련 업종 | 키워드 |
|------|----------|--------|
| 木 (목) | 교육, 출판, 패션, 의류, 가구, 농업, 환경 | 성장, 발전, 창의 |
| 火 (화) | IT, 미디어, 엔터테인먼트, 요식업, 에너지, 전자 | 확산, 표현, 기술 |
| 土 (토) | 부동산, 건설, 농업, 중개, 컨설팅, 유통 | 안정, 중재, 저장 |
| 金 (금) | 금융, 법률, 군/경, 기계, 자동차, 보석, 의료기기 | 결단, 정밀, 규율 |
| 水 (수) | 무역, 물류, 수산, 관광, 서비스, 연구, 제약 | 유동, 지혜, 소통 |

### 3.2 십성 기반 직무 적합도

| 십성 | 직무 성향 | 적합 직무 |
|------|----------|----------|
| 비견/겁재 | 독립적, 경쟁적 | 영업, 프리랜서, 창업, 스포츠 |
| 식신/상관 | 창의적, 표현적 | 기획, 디자인, 마케팅, 연구개발 |
| 편재/정재 | 실용적, 재물 지향 | 재무, 경영, 투자, 유통 |
| 편관/정관 | 체계적, 관리 지향 | 관리직, 공무원, 법률, 인사 |
| 편인/정인 | 학습적, 분석적 | 연구, 교육, 컨설팅, 기술직 |

### 3.3 대운/세운 기반 타이밍 분석

```
분석 요소:
1. 현재 대운 (10년 주기) - 전체 커리어 방향성
2. 올해 세운 - 올해의 직업 운세
3. 향후 2~3년 세운 흐름 - 이직 적기 판단
4. 대운 교체 시기 - 큰 변화가 오는 시점
5. 월운 (이직 실행 최적 월) - 구체적 행동 시기

핵심 판단 기준:
- 관성(官星)이 강해지는 시기 = 직장 내 변화/승진 가능성
- 식상(食傷)이 강해지는 시기 = 새로운 시도/창업 유리
- 재성(財星)이 강해지는 시기 = 연봉 상승/재물 증가
- 인성(印星)이 강해지는 시기 = 학습/자격증/역량 강화
- 비겁(比劫)이 강해지는 시기 = 경쟁 심화/독립 욕구
```

---

## 4. 세부 컨텐츠 구성

### 4.1 이직 타이밍 분석 (핵심 컨텐츠)

**컨텐츠명:** "나의 이직 골든타임"

출력 구성:
```
1. 현재 커리어 운세 진단
   - 현재 대운이 직업에 미치는 영향
   - 올해 세운과 직업 운세의 관계
   - 지금 느끼는 불만족의 사주적 원인 해석

2. 이직 적기 판단
   - 향후 24개월 중 이직 유리한 시기 (월 단위)
   - 피해야 할 시기와 이유
   - 대운 교체 전후 주의사항

3. 이직 방향 제안
   - 사주에 맞는 업종 (오행 기반)
   - 직무 적합도 (십성 기반)
   - 현재 업종과의 시너지 분석

4. 실행 조언
   - 이력서 제출/면접에 좋은 날
   - 연봉 협상에 유리한 시기
   - 이직 전 준비해야 할 것 (사주 기반)
```

### 4.2 승진 vs 이직 분석

**컨텐츠명:** "머물 것인가, 떠날 것인가"

출력 구성:
```
1. 현 직장에서의 성장 가능성
   - 관성(官星) 흐름으로 본 승진 가능성
   - 현 직장 입사 시점의 운세 vs 현재 비교
   - 조직 내 인간관계 운세

2. 이직 시 기대 효과
   - 새로운 환경에서의 적응력 (식상 흐름)
   - 연봉 상승 가능성 (재성 흐름)
   - 새로운 인간관계 운세

3. 종합 판단
   - 승진 유리 지표 vs 이직 유리 지표 비교
   - 시기별 추천 액션 (분기별)
```

### 4.3 창업 적기 분석

**컨텐츠명:** "내 사주에 사장 기운이 있을까"

출력 구성:
```
1. 창업 적합도 진단
   - 비겁/식상/편재 구성으로 본 창업 기질
   - 리더십 성향 (비견 vs 겁재)
   - 리스크 감수 성향 (편재 vs 정재)

2. 창업 타이밍
   - 식상이 강해지는 시기 = 아이디어 폭발기
   - 재성이 뒷받침되는 시기 = 수익화 가능기
   - 관성이 약해지는 시기 = 조직 이탈 충동기

3. 적합 업종 추천
   - 사주 오행 기반 업종
   - 동업 vs 단독 창업 추천
   - 초기 자금 운용 시기
```

### 4.4 번아웃 회복 분석

**컨텐츠명:** "지금, 쉬어야 할 때인가"

출력 구성:
```
1. 번아웃의 사주적 원인
   - 현재 운세 흐름에서 에너지 소모 요인
   - 일간(日干)과 현재 운세의 충돌 지점

2. 회복 시기 전망
   - 에너지가 회복되는 시기
   - 인성(印星) 흐름으로 본 재충전 기간

3. 회복 후 커리어 방향
   - 쉰 후 복귀 vs 새로운 시작 판단
   - 최적 복귀/이직 시기
```

---

## 5. API 설계

### 5.1 이직 종합 분석

```
POST /api/v1/career/transition
Body: {
  "birth": {
    "year": 1992, "month": 8, "day": 15,
    "hour": 10, "gender": "male"
  },
  "career_info": {
    "current_industry": "IT",       // 선택
    "current_role": "backend_dev",  // 선택
    "years_at_company": 4,          // 선택
    "join_year": 2022,              // 선택
    "total_experience": 7,          // 선택
    "concern_type": "timing",       // 선택: timing, direction, promotion_vs_move, startup, burnout, salary
    "target_period": "2026-H2"      // 선택: 희망 이직 시기
  },
  "language": "ko"
}
Response: {
  "calculation": { ... },
  "current_career_fortune": {
    "current_dayun": "...",
    "current_year_fortune": "...",
    "career_energy": "rising" | "stable" | "declining" | "transitioning"
  },
  "transition_timing": {
    "best_months": [
      { "year": 2026, "month": 9, "score": 92, "reason": "..." },
      { "year": 2026, "month": 11, "score": 85, "reason": "..." }
    ],
    "caution_months": [
      { "year": 2026, "month": 7, "score": 35, "reason": "..." }
    ],
    "next_dayun_change": { "year": 2028, "impact": "..." }
  },
  "direction": {
    "suitable_industries": ["금융", "컨설팅"],
    "suitable_roles": ["기획", "전략"],
    "element_alignment": "..."
  },
  "interpretation": "...",
  "action_plan": {
    "immediate": "...",
    "short_term": "...",
    "long_term": "..."
  }
}
```

### 5.2 승진 vs 이직 분석

```
POST /api/v1/career/stay-or-go
Body: {
  "birth": {
    "year": 1990, "month": 3, "day": 20,
    "hour": 14, "gender": "female"
  },
  "career_info": {
    "years_at_company": 5,
    "join_year": 2021,
    "current_role": "team_lead",
    "total_experience": 10
  },
  "language": "ko"
}
Response: {
  "calculation": { ... },
  "stay_analysis": {
    "promotion_probability_trend": "...",
    "relationship_fortune": "...",
    "growth_potential": "..."
  },
  "go_analysis": {
    "adaptation_fortune": "...",
    "salary_growth_trend": "...",
    "new_relationship_fortune": "..."
  },
  "recommendation": "stay" | "go" | "wait",
  "recommended_timing": "...",
  "interpretation": "..."
}
```

### 5.3 창업 적합도 분석

```
POST /api/v1/career/startup
Body: {
  "birth": {
    "year": 1988, "month": 11, "day": 5,
    "hour": 22, "gender": "male"
  },
  "career_info": {
    "total_experience": 12,
    "current_industry": "marketing",
    "target_industry": "F&B"   // 선택: 희망 창업 업종
  },
  "language": "ko"
}
Response: {
  "calculation": { ... },
  "startup_aptitude": {
    "leadership_score": 78,
    "risk_tolerance": 65,
    "creativity_score": 88,
    "financial_sense": 72,
    "overall": 76
  },
  "timing": {
    "best_period": "2027년 상반기",
    "reason": "..."
  },
  "suitable_types": {
    "solo_vs_partnership": "partnership",
    "industries": ["F&B", "교육"],
    "scale": "소규모 시작 추천"
  },
  "interpretation": "..."
}
```

---

## 6. 프롬프트 설계 원칙

### 6.1 핵심 원칙

```
1. 구체적 시기 제시: "좋다/나쁘다"가 아닌 "2026년 9~10월이 유리하다"
2. 행동 가능한 조언: "준비하세요"가 아닌 "이력서를 9월 초에 제출하세요"
3. 양면 제시: 이직이 무조건 좋다/나쁘다가 아닌 장단점 모두 분석
4. 현실적 톤: 사주 해석이지만 현실적 커리어 조언과 결합
5. 결정은 사용자 몫: "반드시 이직하세요"가 아닌 "이 시기에 기회가 열립니다"
```

### 6.2 금지 사항

```
- "이 직장은 당신과 안 맞습니다" (현 직장 폄하 금지)
- "반드시 OO하세요" (단정적 조언 금지)
- "실패할 것입니다" (부정적 예측 금지)
- 구체적 회사명 언급 금지
- 연봉 금액 직접 예측 금지
```

### 6.3 면책조항

```
본 분석은 전통 역학에 기반한 참고 정보이며,
실제 커리어 의사결정을 대체하지 않습니다.
중요한 이직/퇴사 결정은 전문 커리어 상담사,
헤드헌터, 또는 신뢰할 수 있는 멘토와 상의하세요.
```

---

## 7. 수익 모델

| 컨텐츠 | 판매가 (VAT 포함) | 모델 | API 비용 | max_tokens |
|---------|-------------------|------|----------|------------|
| 이직 타이밍 분석 | 8,800원 | Sonnet | ~67원 | 3,000 |
| 승진 vs 이직 분석 | 8,800원 | Sonnet | ~67원 | 3,000 |
| 창업 적합도 분석 | 8,800원 | Sonnet | ~67원 | 3,000 |
| 번아웃 회복 분석 | 5,500원 | Sonnet | ~46원 | 2,000 |
| 커리어 종합 리포트 (전체 포함) | 16,500원 | Sonnet | ~90원 | 4,000 |

### 가격 근거

- 기존 가격표에서 "취업/이직 분석"이 8,800원으로 설정되어 있어 동일 가격대 유지
- 커리어 관련 의사결정은 고가치 -> 프리미엄 가격 수용도 높음
- 오프라인 사주 상담 (이직 관련): 5~15만원 -> 온라인 AI 분석 8,800~16,500원은 합리적
- 헤드헌터 커리어 상담: 무료~30만원 -> 사주 기반 보완재로 포지셔닝

---

## 8. 구현 우선순위

```
Phase 1 (핵심):
  1. 이직 타이밍 분석 - 가장 높은 수요
  2. 승진 vs 이직 분석 - 직장인 핵심 고민

Phase 2 (확장):
  3. 창업 적합도 분석
  4. 번아웃 회복 분석

Phase 3 (프리미엄):
  5. 커리어 종합 리포트 (1~4 통합)
```

---

## 9. 기술 구현 사항

### 9.1 모델 레이어

```python
class CareerConcernType(str, Enum):
    TIMING = "timing"
    DIRECTION = "direction"
    PROMOTION_VS_MOVE = "promotion_vs_move"
    STARTUP = "startup"
    BURNOUT = "burnout"
    SALARY = "salary"

class CareerInfo(BaseModel):
    current_industry: str | None = None
    current_role: str | None = None
    years_at_company: int | None = Field(None, ge=0, le=50)
    join_year: int | None = Field(None, ge=1970, le=2030)
    total_experience: int | None = Field(None, ge=0, le=50)
    concern_type: CareerConcernType | None = None
    target_period: str | None = None

class CareerTransitionRequest(BaseModel):
    birth: BirthInput
    career_info: CareerInfo | None = None
    language: Language = Language.KO
```

### 9.2 서비스 레이어

- `CareerService`: 커리어 전용 서비스
- `SajuService`에서 사주 계산 + 대운/세운 데이터 가져옴
- career_info를 프롬프트 컨텍스트로 전달하여 맞춤 해석
- 입사 연도 기반 역행 분석: 입사 당시의 운세 흐름과 현재 비교

### 9.3 엔진 레이어

- 기존 대운(Da Yun) 계산 활용
- 세운(年運) 계산: target_year의 간지 산출 (기존 구현)
- 월운(月運) 계산: 향후 24개월의 월간지 산출 (신규)
- 입사 시점 세운 역추적: join_year의 간지로 당시 운세 분석
