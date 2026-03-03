"""Reading-type-specific prompt templates and lookup."""
from __future__ import annotations

from app.llm.prompts.saju_reading import SAJU_READING_PROMPT

LOVE_READING_PROMPT = """아래 사주 데이터를 분석하여 연애운에 특화된 해석을 제공해주세요.

## 사주 데이터
{saju_data}

## 요청 해석 항목
다음 항목을 순서대로 해석해주세요:

### 1. 연애 사주 개요
- 일간의 특성과 연애 성향
- 사주 내 관성(정관/편관)과 재성(정재/편재)의 배치 분석

### 2. 연애 스타일
- 일간과 십신 구조로 본 연애 패턴
- 이상형의 특성과 끌리는 유형

### 3. 연애운 시기
- 현재 대운과 연운에서의 연애 에너지
- 좋은 만남이 예상되는 시기와 조건

### 4. 관계에서의 강점과 약점
- 연인 관계에서 빛나는 장점
- 주의해야 할 관계 패턴

### 5. 연애 실천 조언
- 좋은 인연을 만들기 위한 구체적 행동 가이드
- 관계를 발전시키기 위한 방향
"""

FRIENDSHIP_READING_PROMPT = """아래 사주 데이터를 분석하여 우정운과 대인관계에 특화된 해석을 제공해주세요.

## 사주 데이터
{saju_data}

## 요청 해석 항목
다음 항목을 순서대로 해석해주세요:

### 1. 대인관계 사주 개요
- 일간의 특성과 사교 성향
- 비겁(비견/겁재)과 인성(정인/편인)의 배치 분석

### 2. 교우 스타일
- 친구 관계에서의 역할과 패턴
- 잘 맞는 친구 유형과 갈등이 생기기 쉬운 유형

### 3. 사회적 관계
- 직장/학교 등 조직 내 대인관계 특성
- 리더십과 협동 능력 분석

### 4. 우정운 시기
- 현재 대운에서의 인간관계 에너지
- 좋은 인연이 예상되는 시기

### 5. 대인관계 실천 조언
- 관계를 깊게 만들기 위한 구체적 행동 가이드
- 주의해야 할 관계 습관
"""

MARRIAGE_READING_PROMPT = """아래 사주 데이터를 분석하여 결혼운에 특화된 해석을 제공해주세요.

## 사주 데이터
{saju_data}

## 요청 해석 항목
다음 항목을 순서대로 해석해주세요:

### 1. 결혼 사주 개요
- 일간의 특성과 결혼 적성
- 배우자궁(일지)과 관성/재성 분석

### 2. 배우자 성향
- 사주로 본 배우자의 특성과 성격
- 배우자와의 관계 패턴 예측

### 3. 결혼 시기
- 결혼 적기 분석 (대운/연운)
- 결혼에 유리한 조건과 환경

### 4. 결혼 생활 전망
- 부부 관계의 강점과 도전 과제
- 가정 운영 스타일과 재물 관리

### 5. 결혼 실천 조언
- 좋은 배우자를 만나기 위한 방향
- 행복한 결혼 생활을 위한 구체적 조언
"""

SINSAL_READING_PROMPT = """아래 사주 데이터를 분석하여 신살(神殺) 분석에 특화된 해석을 제공해주세요.

## 사주 데이터
{saju_data}

## 요청 해석 항목
다음 항목을 순서대로 해석해주세요:

### 1. 주요 길신(吉神) 분석
- 천을귀인, 문창귀인, 천덕귀인 등 사주 내 길신 확인
- 각 길신의 의미와 발현 조건

### 2. 주요 흉신(凶神) 분석
- 양인, 공망, 원진 등 사주 내 흉신 확인
- 흉신의 영향과 대처 방향 (불필요한 공포 조성 없이)

### 3. 특수 신살
- 도화살, 역마살, 화개살 등 특수 신살 분석
- 현대적 관점에서의 재해석

### 4. 신살의 대운별 영향
- 현재 대운에서 활성화되는 신살
- 향후 주의해야 할 시기

### 5. 종합 조언
- 길신을 활용하는 방법
- 흉신의 에너지를 긍정적으로 전환하는 실천 방안
"""


READING_TYPE_PROMPTS: dict[str, str] = {
    "saju_reading": SAJU_READING_PROMPT,
    "love_reading": LOVE_READING_PROMPT,
    "friendship_reading": FRIENDSHIP_READING_PROMPT,
    "marriage_reading": MARRIAGE_READING_PROMPT,
    "sinsal": SINSAL_READING_PROMPT,
}


def get_prompt_for_type(reading_type: str) -> str:
    """Return the prompt template for the given reading type.

    Falls back to the general saju reading prompt for unknown types.
    """
    return READING_TYPE_PROMPTS.get(reading_type, SAJU_READING_PROMPT)
