# Saju Project - 작업 현황

## 완료된 작업

### 1. 프로젝트 스캐폴딩
- [x] pyproject.toml, .env.example, .gitignore
- [x] 전체 디렉토리 구조 및 __init__.py

### 2. 엔진 레이어
- [x] constants.py - 천간지지, 오행, 십신, 12운성 매핑 (한자/한글)
- [x] models.py - PillarInfo, DaYunInfo, SajuData (frozen dataclass)
- [x] calculator.py - lunar-python 래핑, 사주 계산 핵심 로직
- [x] summer_time.py - 한국 서머타임 보정 (1948-1961)
- [x] night_zi.py - 야자시 처리

### 3. 설정/모델/에러
- [x] config.py - Pydantic Settings (.env 기반)
- [x] models/common.py - Gender, CalendarType enums
- [x] models/request.py - 모든 요청 스키마
- [x] models/response.py - 모든 응답 스키마
- [x] middleware/error_handler.py - SajuError 계층 + 글로벌 핸들러

### 4. LLM/캐시 레이어
- [x] llm/client.py - AsyncAnthropic wrapper (스트리밍 지원)
- [x] llm/formatter.py - SajuData -> 프롬프트 텍스트 변환
- [x] llm/prompts/system.py - 30년 전문가 시스템 프롬프트
- [x] llm/prompts/saju_reading.py - 종합해석 프롬프트
- [x] llm/prompts/compatibility.py - 궁합 프롬프트
- [x] llm/prompts/fortune.py - 월운/일운 프롬프트
- [x] services/cache_service.py - Redis 캐싱 추상화

### 5. 서비스/라우터/DI
- [x] services/saju_service.py - 계산 + 해석 오케스트레이션
- [x] services/compatibility_service.py - 궁합
- [x] services/fortune_service.py - 월운/일운
- [x] routers/health.py - GET /health
- [x] routers/saju.py - POST /api/v1/saju/calculate, /reading, /sinsal
- [x] routers/compatibility.py - POST /api/v1/compatibility/analyze
- [x] routers/fortune.py - POST /api/v1/fortune/monthly, /daily
- [x] dependencies.py - DI 연결
- [x] main.py - FastAPI app, lifespan, CORS

### 6. 테스트 (32/32 통과)
- [x] test_calculator.py - 11개 (만세력 계산 교차검증)
- [x] test_summer_time.py - 10개 (DST 보정)
- [x] test_night_zi.py - 3개 (야자시 처리)
- [x] test_saju_router.py - 8개 (API 엔드포인트)

---

## 미완료 작업

### 필수
- [ ] Anthropic API 크레딧 충전 (LLM 해석 기능 사용 위해)
- [ ] 만세력 사이트와 교차 검증 (최소 100개 사례 권장)
- [ ] .env 파일에 API 키 설정 완료 (키는 입력됨, 크레딧 미충전)

### 기능 보완
- [ ] 신살(sinsal) 전용 프롬프트 작성 (현재 reading 프롬프트 공유)
- [ ] Rate limiting 구현
- [ ] 인증/인가 구현
- [ ] 요청/응답 로깅

### 인프라/배포
- [ ] Dockerfile 작성
- [ ] CI/CD 파이프라인
- [ ] 프로덕션 환경 설정

### 법률/운영
- [ ] 개인정보처리방침 작성
- [ ] 면책 조항 작성
- [ ] 사업자 등록 / 통신판매업 신고 (유료 서비스 시)
