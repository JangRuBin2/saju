# Per-Reading Ticket Payment System - Implementation Guide

## Overview

구독 모델(월 9,900원) -> 건당 결제 모델로 전환.
1결제 = 1회 사용. reading_type별로 별도 결제.

---

## Current Status

### Backend (saju) - Phase 1 COMPLETE

| File | Status | Change |
|------|--------|--------|
| `app/config.py` | DONE | `require_service_token = True` |
| `app/middleware/token_validator.py` | DONE | `tier` -> `reading_type` |
| `app/middleware/rate_limiter.py` | DONE | tier 기반 -> 균일 per-user (30 req/min) |
| `app/llm/prompts/reading_types.py` | DONE | 5개 타입별 프롬프트 + `get_prompt_for_type()` |
| `app/services/saju_service.py` | DONE | `reading(birth, reading_type)` 파라미터 추가 |
| `app/routers/saju.py` | DONE | `request.state.reading_type` 전달 |
| `tests/test_reading_types.py` | DONE | 13개 테스트 (프롬프트 선택 + 토큰 검증) |

### Frontend (saju-front) - TODO

아래 Phase 2~4 전부 미구현.

---

## Phase 2: Frontend DB Schema Changes

### File: `prisma/schema.prisma`

#### 2-1. ReadingType 모델 추가 (상품 카탈로그)

```prisma
model ReadingType {
  id          String    @id @default(cuid())
  code        String    @unique
  name        String
  description String?
  price       Int
  endpoint    String
  isActive    Boolean   @default(true)
  createdAt   DateTime  @default(now())
  payments    Payment[]
}
```

#### 2-2. Payment 모델 변경

제거할 필드:
- `plan` (구독 플랜 구분 불필요)
- `startDate` (구독 시작일 불필요)
- `endDate` (구독 만료일 불필요)

추가할 필드:
- `readingTypeId` (FK -> ReadingType)
- `usedAt` (사용 시점, nullable)

변경할 필드:
- `status`: "pending" -> "paid" -> "used" 또는 "refunded"

```prisma
model Payment {
  id            String      @id @default(cuid())
  userId        String
  orderId       String      @unique
  paymentKey    String?     @unique
  amount        Int
  status        String      @default("pending")
  readingTypeId String
  readingType   ReadingType @relation(fields: [readingTypeId], references: [id])
  usedAt        DateTime?
  createdAt     DateTime    @default(now())
  updatedAt     DateTime    @updatedAt
  user          User        @relation(fields: [userId], references: [id])

  @@index([userId, status])
  @@index([userId, readingTypeId, status])
}
```

#### 2-3. UsageLog 모델 - 유지 또는 제거

건당 결제에서는 Payment.status로 사용 여부를 추적하므로 UsageLog가 불필요할 수 있음.
단, 통계/분석 목적으로 유지해도 무방.

#### 2-4. Seed Data

migration 후 seed script로 삽입:

| code | name | price (KRW) | endpoint |
|------|------|-------------|----------|
| `saju_reading` | 종합 사주 | 5000 | saju_reading |
| `love_reading` | 연애운 | 3000 | saju_reading |
| `friendship_reading` | 우정운 | 3000 | saju_reading |
| `marriage_reading` | 결혼운 | 3000 | saju_reading |
| `sinsal` | 신살 분석 | 5000 | sinsal |
| `compatibility` | 궁합 분석 | 8000 | compatibility |
| `monthly_fortune` | 월간 운세 | 3000 | monthly_fortune |
| `daily_fortune` | 일일 운세 | 1000 | daily_fortune |

#### 2-5. 실행

```bash
cd C:\workspace\saju-front\saju-front
npx prisma migrate dev --name per-reading-ticket
npx prisma db seed   # seed script 작성 필요
```

---

## Phase 3: Frontend Logic Changes

### 3-1. `src/lib/server/service-token.ts`

**현재:**
```typescript
interface ServiceTokenPayload {
  user_id: string;
  tier: "free" | "premium";
  timestamp: number;
  nonce: string;
}
generateServiceToken(userId, tier)
```

**변경:**
```typescript
interface ServiceTokenPayload {
  user_id: string;
  reading_type: string;    // "love_reading", "saju_reading", etc.
  timestamp: number;
  nonce: string;
}
generateServiceToken(userId, readingType)
```

- `tier` 필드 제거, `reading_type` 필드 추가
- HMAC 서명 대상 payload가 바뀌므로 Python API의 token_validator와 정확히 일치해야 함

### 3-2. `src/lib/server/user-tier.ts`

**제거 또는 단순화.**

구독 모델이 없으므로 `getUserTier()` 함수 불필요.
이 함수를 참조하는 모든 곳에서 제거.

참조하는 파일:
- `actions.ts` (withUsageCheck 내부)
- `api/saju/reading/route.ts`

### 3-3. `src/lib/server/payment-service.ts`

**현재 함수:**
- `createPaymentOrder(userId, plan, amount)` - plan 기반
- `confirmPayment(paymentKey, orderId, amount)` - startDate/endDate 설정

**변경/추가할 함수:**

```typescript
// plan -> readingTypeId
createPaymentOrder(userId: string, readingTypeId: string, amount: number): Promise<string>

// startDate/endDate 제거, status만 "paid"로
confirmPayment(paymentKey: string, orderId: string, amount: number): Promise<{success: boolean}>

// NEW: 미사용 결제(티켓) 조회
findUnusedPayment(userId: string, readingTypeCode: string): Promise<Payment | null>
// -> status === "paid" && usedAt === null && readingType.code === readingTypeCode

// NEW: 결제 소비 (사용 처리)
consumePayment(paymentId: string): Promise<void>
// -> status = "used", usedAt = new Date()
```

### 3-4. `src/lib/server/usage-limiter.ts`

**현재:** tier 기반 일일 횟수 제한 (FREE_LIMITS, PREMIUM_ONLY_ACTIONS)

**변경:** 결제 티켓 존재 여부 확인으로 전환

```typescript
// Before
checkUsageLimit(userId, sessionId, action, tier) -> { allowed, remaining }

// After
checkTicket(userId: string, readingTypeCode: string): Promise<{
  allowed: boolean;
  paymentId: string | null;
  readingType: ReadingType | null;
}>
```

- `findUnusedPayment(userId, readingTypeCode)` 호출
- 미사용 결제가 있으면 `{ allowed: true, paymentId }` 반환
- 없으면 `{ allowed: false, paymentId: null }` 반환
- `recordUsage()` 함수는 `consumePayment()`로 대체

### 3-5. `src/lib/server/api-server-client.ts`

**현재:** 모든 함수가 `tier` 파라미터를 받아 서비스 토큰에 전달

```typescript
// Before
calculateSaju(birthInfo, userId, tier)
streamSajuReading(request, userId, tier)
getSinsal(birthInfo, userId, tier)
// ...

function serverRequest(path, body, userId, tier) {
  const token = generateServiceToken(userId, tier);
  // ...
}
```

**변경:** `tier` -> `readingTypeCode`

```typescript
// After
calculateSaju(birthInfo, userId, readingTypeCode)
streamSajuReading(request, userId, readingTypeCode)
getSinsal(birthInfo, userId, readingTypeCode)
// ...

function serverRequest(path, body, userId, readingTypeCode) {
  const token = generateServiceToken(userId, readingTypeCode);
  // ...
}
```

### 3-6. `src/lib/server/actions.ts`

**현재:**
```typescript
withUsageCheck(action, fn):
  1. getSession
  2. getUserTier(userId)
  3. checkUsageLimit(userId, sessionId, action, tier)
  4. fn(userId, tier)
  5. recordUsage(userId, sessionId, action)
```

**변경:**
```typescript
withTicketCheck(readingTypeCode, fn):
  1. getSession (로그인 필수)
  2. checkTicket(userId, readingTypeCode) -> { paymentId }
  3. fn(userId, readingTypeCode)
  4. consumePayment(paymentId)  // 성공 시에만
```

각 action에 readingTypeCode 전달:
- `calculateSajuAction(birth)` -> `calculateSajuAction(birth, readingTypeCode)`
- 또는 readingTypeCode를 request body에 포함

### 3-7. `src/app/api/saju/reading/route.ts`

**현재:**
```
1. getSession
2. getUserTier(userId)
3. checkUsageLimit(userId, sessionId, "saju_reading", tier)
4. streamSajuReading(body, userId, tier)
5. recordUsage()
```

**변경:**
```
1. getSession (로그인 필수 - 비로그인은 결제 불가)
2. body에서 readingTypeCode 추출
3. checkTicket(userId, readingTypeCode) -> { paymentId }
4. streamSajuReading(body, userId, readingTypeCode)
5. consumePayment(paymentId)  // 스트림 성공 시
```

비로그인 사용자는 무조건 로그인 유도.

---

## Phase 4: Frontend UI Changes

### 4-1. 결제 페이지 (`src/app/[locale]/payment/page.tsx`)

**현재:** 구독 플랜 (9,900원/월) 단일 상품

**변경:** 개별 reading type 상품 목록

- DB에서 `ReadingType` 목록 조회 (isActive === true)
- 카드 형태로 각 상품 표시 (name, description, price)
- 상품 선택 -> Toss Payments 결제 요청
- `orderId` 생성 시 `readingTypeId` 포함

### 4-2. PremiumGate -> PaymentGate (`src/components/ui/PremiumGate.tsx`)

**현재:**
- `premium_required`: "프리미엄 구독이 필요합니다" -> `/payment`
- `usage_limit`: "일일 한도 초과" -> 로그인 또는 구독 유도

**변경:**
- `ticket_required`: "이 운세를 보려면 결제가 필요합니다"
- 해당 reading type의 가격 표시
- "결제하기" 버튼 -> `/payment?type={readingTypeCode}`
- `auth_required`: 로그인 유도 (유지)

### 4-3. 사주 결과 요청 전 티켓 확인

SajuForm 또는 result 페이지에서:
1. 사용자가 reading type 선택 (연애운, 우정운, 결혼운 등)
2. 미사용 결제 확인 API 호출
3. 결제가 있으면 -> 바로 요청
4. 결제가 없으면 -> PaymentGate 표시

### 4-4. 마이페이지 변경

**구독 페이지 (`mypage/subscription`):**
- 제거하거나 "결제 내역"으로 통합

**결제 내역 (`mypage/payments`):**
- 각 결제의 status 표시: pending / paid (미사용) / used / refunded
- "미사용 티켓" 섹션 분리 표시

### 4-5. 홈/메뉴 변경 (`[locale]/page.tsx`)

- 기존 메뉴 카드에 가격 표시 추가 가능
- 또는 상세 페이지에서 reading type 선택 후 결제 유도

---

## Phase 5: API Route for Reading Types

### 새 API Route: `src/app/api/reading-types/route.ts`

프론트엔드에서 상품 목록을 조회하기 위한 엔드포인트:

```typescript
// GET /api/reading-types
export async function GET() {
  const types = await prisma.readingType.findMany({
    where: { isActive: true },
    orderBy: { price: "asc" },
  });
  return Response.json(types);
}
```

### 새 API Route: `src/app/api/tickets/route.ts`

미사용 티켓 조회:

```typescript
// GET /api/tickets?type=love_reading
export async function GET(request: Request) {
  const session = await auth();
  if (!session?.user?.id) return Response.json({ error: "Unauthorized" }, { status: 401 });

  const url = new URL(request.url);
  const typeCode = url.searchParams.get("type");

  const ticket = await findUnusedPayment(session.user.id, typeCode);
  return Response.json({ hasTicket: !!ticket, ticket });
}
```

---

## Phase 6: Tests

### Backend (saju) - DONE

- `tests/test_reading_types.py`: 프롬프트 선택 8개 + 토큰 검증 5개
- 기존 65개 테스트 전부 통과

### Frontend (saju-front) - TODO

작성 필요한 테스트:
- `service-token.test.ts`: reading_type 포함 토큰 생성/검증
- `payment-service.test.ts`: createPaymentOrder, confirmPayment, consumePayment, findUnusedPayment
- `usage-limiter.test.ts` (or `ticket-checker.test.ts`): checkTicket 로직
- E2E: 결제 -> 사용 -> 재사용 불가 flow

---

## Migration Checklist

### Backend 배포 시

1. `.env`에 `REQUIRE_SERVICE_TOKEN=true` 확인
2. `.env`에 `API_SECRET_KEY` 설정 확인 (프론트와 동일한 값)
3. 기존 프론트가 `tier` 기반 토큰을 보내고 있으므로, 프론트 배포 전에 백엔드를 먼저 배포하면 기존 요청이 실패함
4. **프론트와 백엔드를 동시에 배포하거나, 백엔드에 일시적으로 하위 호환 로직 추가**

### 하위 호환 전략 (선택)

token_validator.py에서 `tier`와 `reading_type` 둘 다 허용하는 임시 로직:

```python
reading_type = token_data.get("reading_type")
tier = token_data.get("tier")  # legacy fallback

if not reading_type and tier:
    reading_type = "saju_reading"  # 기존 구독 유저 -> 기본 reading

if not user_id or (reading_type is None and tier is None) or timestamp is None:
    return _json_error(401, "Incomplete token payload")

request.state.reading_type = reading_type or "saju_reading"
```

프론트 배포 완료 후 이 fallback 제거.

---

## File Change Summary

### Backend (saju) - COMPLETE

| File | Change |
|------|--------|
| `app/config.py` | `require_service_token = True` |
| `app/middleware/token_validator.py` | `tier` -> `reading_type` |
| `app/middleware/rate_limiter.py` | tier 기반 -> 균일 rate limit |
| `app/llm/prompts/reading_types.py` | NEW: 타입별 프롬프트 |
| `app/services/saju_service.py` | `reading_type` 파라미터 |
| `app/routers/saju.py` | `request.state.reading_type` 전달 |
| `tests/test_reading_types.py` | NEW: 13개 테스트 |

### Frontend (saju-front) - TODO

| File | Change | Phase |
|------|--------|-------|
| `prisma/schema.prisma` | ReadingType 추가, Payment 변경 | 2 |
| `prisma/seed.ts` | NEW: seed data | 2 |
| `src/lib/server/service-token.ts` | `tier` -> `reading_type` | 3 |
| `src/lib/server/user-tier.ts` | 제거 | 3 |
| `src/lib/server/payment-service.ts` | 건당 결제 + consumePayment + findUnusedPayment | 3 |
| `src/lib/server/usage-limiter.ts` | tier 기반 -> ticket 기반 (checkTicket) | 3 |
| `src/lib/server/api-server-client.ts` | `tier` -> `readingTypeCode` | 3 |
| `src/lib/server/actions.ts` | `withUsageCheck` -> `withTicketCheck` | 3 |
| `src/app/api/saju/reading/route.ts` | 티켓 검증 + 소비 | 3 |
| `src/app/api/reading-types/route.ts` | NEW: 상품 목록 API | 5 |
| `src/app/api/tickets/route.ts` | NEW: 티켓 조회 API | 5 |
| `src/app/[locale]/payment/page.tsx` | 구독 -> 개별 상품 결제 | 4 |
| `src/components/ui/PremiumGate.tsx` | -> PaymentGate | 4 |
| `src/app/[locale]/mypage/subscription/page.tsx` | 제거 또는 통합 | 4 |
| `src/app/[locale]/mypage/payments/page.tsx` | 미사용 티켓 표시 | 4 |

---

## Implementation Order (Recommended)

```
Phase 2: Schema  ──> Phase 3: Logic  ──> Phase 4: UI  ──> Phase 5: API  ──> Phase 6: Tests
  (1일)               (2일)               (2일)             (0.5일)          (1일)
```

Phase 3는 의존 관계가 있으므로 순서 준수:
1. `service-token.ts` (다른 모듈이 의존)
2. `user-tier.ts` 제거 (참조 제거)
3. `payment-service.ts` (새 함수 추가)
4. `usage-limiter.ts` -> ticket checker
5. `api-server-client.ts` (token 변경 반영)
6. `actions.ts` (withTicketCheck)
7. `api/saju/reading/route.ts`

---

## Known Issues to Fix (Existing Bugs)

1. **`/api/payments/confirm` GET handler 불완전**: mypage/subscription과 mypage/payments에서 `?tier=true`, `?list=true` 쿼리를 보내지만 핸들러가 처리하지 않음
2. **Anonymous sessionId 공유**: 모든 비로그인 사용자가 `"anonymous"` sessionId를 공유 -> 건당 결제에서는 로그인 필수로 해결
3. **SSE usage recording**: 스트림 시작 시 사용 기록 -> 실패해도 소비됨. consumePayment는 성공 후 호출로 해결
4. **Webhook 서명 미검증**: `api/payments/webhook/route.ts`에서 Toss HMAC 서명 검증 없음
