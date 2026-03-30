---
name: Dalgyeol 4.3(b) Repositioning Plan
description: 달결 앱 "운세 앱" -> "AI 상담 앱" 리포지셔닝 계획. Apple 4.3(b) Spam 리젝 극복 목적. 백엔드 변경 없이 iOS UI 동선 변경 + 5.1.2(i) 준수 + 메타데이터 변경.
type: project
---

달결 앱이 Apple 4.3(b) Spam으로 리젝됨. 리포지셔닝 계획 수립 완료.

**Why:** 운세 앱이 App Store에서 스팸으로 분류되는 경향이 있어, AI 상담을 메인 CTA로 전환하여 차별화 필요.

**How to apply:**
- 플랜 경로: `/Users/kangnam/projects/lunawave/docs/PLAN_REPOSITIONING_AI_CONSULT.md`
- 핵심 변경: HomeView에 AI 상담 히어로 카드 최상단 배치, 탭바 순서 AI상담/홈/리포트/마이로 변경
- 5.1.2(i) 동의 바텀시트 필수 (AIDisclosureSheet.swift)
- AI 프로바이더명은 "Anthropic Claude AI"로 하드코딩 (백엔드 변경 최소화 제약)
- 백엔드 변경 0건, 신규 Swift 파일 2개, 수정 파일 7개
- 2순위 카테고리는 CEO 확인 필요 (건강및피트니스 vs 엔터테인먼트)
