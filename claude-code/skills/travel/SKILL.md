---
name: travel
description: "Real-time transport search and travel planning. Searches flights, trains, buses, ferries with price comparison. Plans full itineraries with weather, events, budget. Use for any travel-related request including '항공권', 'KTX', '여행 계획', '일정'."
---

# Travel

교통편 검색과 여행 계획을 통합한 스킬.

## Step 1: Mode Detection

| Request pattern | Mode | Load Reference |
|---|---|---|
| 항공권, KTX, 기차, 버스, 페리, 교통편, 가격 비교, "how to get to" | Transport Search | `travel/references/transport.md` |
| 여행 계획, 일정, 숙박, 날씨, 예산, 관광지, "plan a trip" | Travel Planning | `travel/references/planning.md` |
| 둘 다 포함 (예: "제주도 3박4일 + 항공권") | Combined | Load both references |

Read the matched reference(s) before proceeding.

## Shared Tool Requirements

- `WebSearch` — 일반 검색
- `WebFetch` — 페이지 내용 읽기
- `agent-browser` — 로그인 필요 페이지, 동적 SPA, 실시간 가격 조회 (JS 렌더링 페이지)
  - 명령어: `agent-browser open <url>`, `snapshot`, `screenshot`, `click <selector>`, `fill <selector> <value>`, `text <selector>`, `close`
  - agent-browser가 설치되어 있지 않으면 사용자에게 설치를 요청하고 스킬 실행을 중단하라

## Shared Output Rules

- 가격은 실시간 변동 → 캡처 시점 기준임을 고지
- 정보가 불확실하면 추정치임을 명시
- 모든 금액은 한화(원) 기준. 현지 통화는 괄호로 병기. 예: `약 15만원 (¥15,000)`
