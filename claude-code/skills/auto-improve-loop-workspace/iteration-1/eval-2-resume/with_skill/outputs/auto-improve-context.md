# auto-improve Round 2 Context

auto-improve를 실행하라.
코드베이스 경로: /tmp/mock-webapp
집중 영역: 전체

[이전 라운드 컨텍스트]
improve-progress.yaml 경로: /tmp/mock-webapp/docs/llm/improve-progress.yaml

이 파일을 읽고 아래 규칙을 적용하라:

1. Audit Phase: 이전 라운드에서 이미 해결된 항목(items_addressed)은 재진단하지 마라.
   대신 해당 영역의 회귀 여부만 확인하라.
   - 해결 완료 항목:
     - SEC-001: SQL injection in user search (security, P0) — Round 1에서 해결

2. Audit Phase: 이전 라운드의 items_remaining을 우선 진단 대상으로 삼아라.
   새로 발견된 항목도 포함하되, 기존 remaining 항목이 우선순위가 높다.
   - 우선 진단 대상 (P1, 즉시 착수):
     - ARCH-001: Circular dependency in core modules (architecture, P1)
     - TEST-001: No integration tests for payment flow (test, P1)
   - 추가 진단: 위 항목 처리 후 새 발견 항목도 보고하라. 특히 아래 영역은 target(8.0) 대비 gap이 큰 순서대로 주목하라:
     - test_coverage: 5.0 (gap: 3.0) — 가장 큰 gap
     - security: 6.0 (gap: 2.0)
     - repo_health: 6.0 (gap: 2.0)
     - architecture: 6.5 (gap: 1.5)
     - code_quality: 6.5 (gap: 1.5)
     - ux_ui: 6.5 (gap: 1.5)
     - db: 7.5 (gap: 0.5)

3. Design Phase: 이전 라운드의 learnings를 참고하여 동일한 시행착오를 반복하지 마라.
   - Round 1 Learnings:
     - payment 모듈 테스트 시 mock DB 필요 (TEST-001 작업 시 반드시 mock DB를 사전 구성하라)
     - user search API 시그니처가 변경됨 (SEC-001 수정의 부작용. user search를 호출하는 코드가 새 시그니처를 사용하는지 확인하라)

4. Build Phase: 이전 라운드에서 수정한 코드에 대한 회귀 테스트를 포함하라.
   - Round 1에서 수정된 영역:
     - user search의 SQL injection fix (security) — 회귀 테스트 필수
     - user search API 시그니처 변경 — 호출부 정합성 테스트 필수

5. Verify Phase: 이전 라운드 final_scores와 현재 라운드 final_scores를 비교하여
   점수가 하락한 영역이 있으면 반드시 보고하라.
   - Round 1 final_scores (비교 기준선):
     - code_quality: 6.5
     - security: 6.0
     - architecture: 6.5
     - db: 7.5
     - test_coverage: 5.0
     - repo_health: 6.0
     - ux_ui: 6.5
