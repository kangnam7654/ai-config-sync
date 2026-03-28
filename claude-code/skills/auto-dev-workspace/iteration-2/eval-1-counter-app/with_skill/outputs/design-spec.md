# Design Specification: Counter App

이 문서는 idea-brief.md, arch-spec.md, ux-ui-spec.md를 흡수한 통합 설계 문서이다. Build Phase와 Verify Phase에서 "기대 동작"의 기준 문서로 사용한다.

---

## 1. 프로젝트 개요

- **앱명**: Counter App
- **한 문장 요약**: 버튼으로 숫자를 증가/감소시키는 React 카운터 웹앱
- **타겟 사용자**: React 학습자 및 간단한 카운터 기능이 필요한 사용자
- **핵심 기능**:
  1. 숫자 증가 (Increment) 버튼
  2. 숫자 감소 (Decrement) 버튼
  3. 현재 카운트 값 표시 (초기값 0)
  4. 리셋 버튼 (0으로 복귀)
- **앱 유형**: Web SPA
- **복잡도**: Simple (기능 3개, 트랙 1개, DB 없음)

## 2. 기술 스택

| 레이어 | 기술 | 근거 |
|--------|------|------|
| Frontend | React 19 + Vite 6 + TypeScript | SPA 전용, SSR 불필요. Trade-Off 4.40 vs Next.js 4.00 |
| Backend | N/A | 서버 로직 없음 |
| Database | N/A | 영속 데이터 없음 |
| Test | Vitest + React Testing Library | Vite 네이티브 테스트, 컴포넌트 테스트 |
| App Verification | Playwright | 브라우저 기반 E2E 검증 |

## 3. 디자인 시스템

### 3.1 색상
| 토큰 | 값 | 용도 |
|------|-----|------|
| --color-primary | #2563EB | 증가 버튼, 포커스 링 |
| --color-primary-hover | #1D4ED8 | 증가 버튼 hover |
| --color-background | #FFFFFF | 카드 배경 |
| --color-surface | #F8FAFC | 페이지 배경 |
| --color-text-primary | #0F172A | 카운트 값 |
| --color-text-secondary | #64748B | 제목 |
| --color-border | #E2E8F0 | 리셋 버튼 테두리 |
| --color-error | #DC2626 | 감소 버튼 |
| --color-error-hover | #B91C1C | 감소 버튼 hover |

### 3.2 타이포그래피
| 토큰 | 값 |
|------|-----|
| font-family | Inter, system-ui, sans-serif |
| display (카운트) | 4rem / font-weight 700 |
| h1 (제목) | 1.5rem / font-weight 600 |
| body | 0.875rem / font-weight 400 |

### 3.3 간격
xs=8px, sm=16px, md=24px, lg=32px, xl=48px

### 3.4 Border Radius
default=8px, lg=16px (카드)

## 4. 화면 설계

### 4.1 메인 화면 (카운터)

**레이아웃**: 중앙 정렬 카드. 세로 스택:
```
┌─────────────────────┐
│      COUNTER        │  ← 제목 (text-secondary, uppercase)
│                     │
│        0            │  ← 카운트 값 (display, aria-live)
│                     │
│    [ - ]  [ + ]     │  ← 감소/증가 버튼
│                     │
│      [Reset]        │  ← 리셋 버튼 (outlined)
└─────────────────────┘
```

**목업 경로**: `mockups/counter.html`

### 4.2 반응형
| 뷰포트 | 동작 |
|---------|------|
| <375px | 카드 패딩 32px, 숫자 3rem |
| 375~767px | 카드 너비 90%, 숫자 4rem |
| 768~1439px | 카드 최소 400px, 숫자 5rem |
| 1440px+ | 카드 최소 440px |

## 5. 페르소나

- **지민** (25세, 주니어 프론트엔드 개발자): React 기초 실습, 직관적 UI 선호, 복잡한 설정 회피

## 6. 유저 플로우

1. 앱 로드 -> 카운터 값 0 표시
2. "+" 버튼 클릭 -> 카운트 +1
3. "-" 버튼 클릭 -> 카운트 -1
4. "Reset" 버튼 클릭 -> 카운트 0 복귀

## 7. 접근성 요구사항

- `aria-live="polite"` + `aria-atomic="true"`: 카운트 변경 시 스크린리더 알림
- `aria-label`: 모든 버튼 ("증가", "감소", "리셋")
- `focus-visible`: 3px solid var(--color-primary) 아웃라인
- `prefers-reduced-motion`: 트랜지션 비활성화
- 버튼 최소 터치 타겟: 48x48px
- 색상 대비: 4.5:1 이상

## 8. 실행 계획

### Step 1: 프로젝트 초기화
- Vite + React + TypeScript 프로젝트 생성
- 파일: package.json, vite.config.ts, tsconfig.json, tsconfig.app.json, tsconfig.node.json, index.html

### Step 2: Counter 컴포넌트 구현
- useState로 count 상태 관리
- increment(), decrement(), reset() 핸들러
- aria-live 적용
- 파일: src/components/Counter.tsx, src/components/Counter.css

### Step 3: App 컴포넌트 조립
- Counter 컴포넌트를 App에 마운트
- 글로벌 스타일 적용
- 파일: src/App.tsx, src/App.css, src/main.tsx

### Step 4: 테스트 작성
- Vitest + React Testing Library
- 테스트 케이스: 초기값 0, 증가, 감소, 리셋
- 파일: src/components/__tests__/Counter.test.tsx

## 9. 파일 구조

```
/tmp/auto-dev-eval-counter/
  ├── docs/llm/design-spec.md
  ├── mockups/counter.html
  ├── package.json
  ├── vite.config.ts
  ├── tsconfig.json
  ├── tsconfig.app.json
  ├── tsconfig.node.json
  ├── index.html
  ├── src/
  │   ├── main.tsx
  │   ├── App.tsx
  │   ├── App.css
  │   ├── components/
  │   │   ├── Counter.tsx
  │   │   ├── Counter.css
  │   │   └── __tests__/
  │   │       └── Counter.test.tsx
  └── vitest.config.ts (or in vite.config.ts)
```

## 10. CTO Design Gate

- **판정**: PASS
- **근거**: 아키텍처, UX/UI, 실행 계획 모두 검증 완료
- **루프 횟수**: 1
