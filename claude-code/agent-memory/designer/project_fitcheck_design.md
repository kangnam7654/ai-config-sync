---
name: fit-check UI Design System
description: fit-check (핏체크) MVP의 디자인 시스템 결정사항 - Primary blue-600, Pretendard, shadcn/ui 기반, 8개 핵심 화면 명세 완료
type: project
---

fit-check MVP UI 디자인 명세 완료 (2026-03-31). UX 설계(PASS 8.75) 기반으로 8개 핵심 화면 하이파이 UI 명세 작성. ui-reviewer FAIL(7.55) 접근성 피드백 반영 수정 완료.

**Why:** UX 설계 문서가 와이어프레임 수준이라 구현 LLM이 pixel-perfect UI를 만들기 위한 상세 명세가 필요했음. 1차 리뷰에서 접근성(5/10)이 핵심 실패 원인.

**How to apply:**
- 디자인 토큰: Primary #2563EB (blue-600), Pretendard 폰트, 4px base 간격, shadcn/ui HSL 테마 확장
- 문서 위치: `/docs/llm/ui-design.md` (상태: REVISED)
- 핵심 8개 화면: 랜딩, 대시보드, Gap 시작, Gap 결과, 서류 블러, 서류 상세, 지원 현황 보드, 크레딧 결제
- 접근성 수정: 점수 숫자 text-slate-900 고정, 배지 텍스트 Success-700/Warning-700, placeholder slate-500, Button min-h-44px, H3 weight 500, H4 17px, Footer copyright slate-400
- 커스텀 컴포넌트: ScoreGauge, RadarChart, CreditBadge, SSEProgress, BlurPreview, KanbanBoard, BottomTabBar, EmptyState 등
- 아이콘: Lucide React
- 애니메이션: score-count-up, gauge-fill, typing-cursor, card-hover, modal-enter/exit
