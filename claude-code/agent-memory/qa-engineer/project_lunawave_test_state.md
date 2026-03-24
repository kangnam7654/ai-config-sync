---
name: lunawave_test_state
description: lunawave 프로젝트의 테스트 인프라 상태 스냅샷 (2026-03-24 기준)
type: project
---

lunawave 프로젝트 테스트 현황 진단 완료.

**Why:** QA 진단 요청에 따라 전체 테스트 스택 파악.

**How to apply:** 향후 테스트 작성 시 이 현황을 기준으로 우선순위 결정.

## 백엔드 (Rust)

- 단위 테스트: 90개 (#[test] + #[tokio::test], src/ 내 14개 파일)
  - 커버리지 있는 모듈: fortune_engine (saju/pillars, saju/branches, saju/daeun, saju/daily, saju/monthly, saju/ten_gods), tarot_engine, tarot/draw, tarot/interpreter, ai_advisor/mod, ai_advisor/safety, redaction, jwt, crypto
  - 단위 테스트 없는 서비스: auth_service, point_service, reading_service, profile_service, checkin_service, ad_reward_service, advisor_service, apple_iap_service, calendar_service, consult_service, payment_service, product_service, settlement_service, wallet_service, llm_config_service (총 15개 서비스 파일)
- 통합 테스트: 11개 (tests/integration_test.rs, 995줄)
  - 커버된 플로우: health, auth(register/login/refresh/logout), profile CRUD, reading 생성, oauth exchange, consult session E2E, refund/settlement, webhook idempotency, AI WebSocket E2E, AI safety filter, AI 메시지 크기 제한
  - 미커버 플로우: checkin, rewards/ad-watch, Apple IAP 검증, subscription, consents, admin/llm, 유료 reading(daily_detail/weekly/compatibility_detail 등), 포인트 402 에러, compatibility reading
- CI/CD: .github/workflows 없음 (CI 미설정)
- 커버리지 도구: tarpaulin/llvm-cov 미설정
- test isolation: DB를 공유하므로 병렬 실행 시 오염 위험. --test-threads=1 미설정.
- flakiness risk: 3곳에서 tokio::time::sleep(100ms) 사용 (WebSocket 테스트)

## iOS (Swift/XCTest)

- APIClientTests: 4개 테스트, Keychain 저장/로드/삭제 + 미인증 요청 실패 경로
  - testRequestWithoutTokenThrowsUnauthorized / testRefreshFailureClearsTokens: 서버 없이 실행하므로 error path 검증이 불완전 (catch 블록에 assertion 없음)
- ViewScreenshotTests: 21개 테스트 (모두 PNG 저장용). XCTAssert 4개뿐. 의미있는 behavioral assertion 없음.
- ViewModels 10개 모두 테스트 없음: AuthViewModel, CheckinViewModel, ConsultViewModel, FortuneCalendarViewModel, ProfileViewModel, ReadingViewModel, RewardViewModel, StoreViewModel, TarotPreviewViewModel, WalletViewModel
- StoreKitManager, WebSocketService, AdManager 테스트 없음

## Maestro E2E

- maestro/login-tap.yaml 1개 파일: appId + tapOn("테스트 로그인") + waitForAnimationToEnd
- assertion 전무 — 탭 후 어떤 상태인지 검증하지 않음
- 루트 maestro/ 디렉토리는 비어있음

## 인프라

- Makefile에 `make test` 타겟 있음 (docker-compose up + cargo test)
- dev-dependencies: tokio-tungstenite만 있음 (reqwest는 [dependencies]에 이미 포함)
- 커버리지 측정 명령 없음
