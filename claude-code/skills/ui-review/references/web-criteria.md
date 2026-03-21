# Web UI Review Criteria

ui-review 스킬이 웹 앱/사이트를 평가할 때 참조하는 플랫폼별 기준.

---

## 1. 반응형 Breakpoint 정의

웹 UI는 아래 4개 주요 breakpoint에서 레이아웃이 자연스럽게 전환되어야 한다.

| Breakpoint | 너비 | 대상 기기 | 핵심 체크 |
|------------|------|-----------|-----------|
| Mobile | 320–767px | 스마트폰 | 단일 컬럼, 터치 타겟 44x44px 이상, 햄버거 메뉴 |
| Tablet | 768–1023px | 태블릿 (가로/세로) | 2컬럼 허용, 사이드바 접힘, 터치+마우스 겸용 |
| Desktop | 1024–1439px | 랩탑/모니터 | 다중 컬럼, hover 상태 필수, 키보드 탐색 |
| Wide | 1440px+ | 대형 모니터/울트라와이드 | max-width 제한 (1200–1440px), 중앙 정렬 |

### 평가 기준
- 각 breakpoint에서 콘텐츠 잘림, 오버플로우, 수평 스크롤이 없어야 한다
- 이미지/미디어가 컨테이너에 맞게 스케일링 (`max-width: 100%`)
- 폰트 사이즈가 breakpoint별로 적절히 조정 (mobile: 14–16px body, desktop: 16–18px body)
- 터치 타겟은 모든 인터랙티브 요소에서 최소 44x44px (WCAG 2.5.5)

---

## 2. WCAG 2.1 AA 접근성 체크리스트

### 색상 대비 (1.4.3, 1.4.11)
- **본문 텍스트**: 배경 대비 최소 4.5:1
- **대형 텍스트** (18pt+ 또는 14pt+ bold): 최소 3:1
- **UI 컴포넌트/아이콘**: 인접 색상과 최소 3:1
- **비활성 상태**: 대비 요구사항 면제, 단 시각적으로 비활성임이 명확해야 함

### 포커스 인디케이터 (2.4.7, 2.4.11)
- 모든 인터랙티브 요소에 가시적 포커스 링 필수
- 포커스 링 최소 2px 두께, 배경 대비 3:1 이상
- `outline: none` 사용 시 대체 시각 피드백 필수 (`box-shadow`, `border` 등)
- 포커스 순서가 논리적 (좌→우, 상→하)

### 대체 텍스트 (1.1.1)
- 모든 의미 있는 이미지에 `alt` 속성
- 장식용 이미지는 `alt=""` 또는 `role="presentation"`
- 복잡한 이미지(차트, 인포그래픽)에 상세 설명 (`aria-describedby`)

### 키보드 탐색 (2.1.1, 2.1.2)
- 모든 기능이 키보드만으로 접근 가능
- 키보드 트랩 없음 (모달 제외, 모달은 Esc로 닫기 가능)
- Skip link 제공 (반복 네비게이션 건너뛰기)
- 드롭다운, 탭, 아코디언 등에 적절한 ARIA 패턴

### 기타 필수 항목
- 페이지 제목 (`<title>`) 의미 있고 고유
- 랜드마크 역할 (`<main>`, `<nav>`, `<header>`, `<footer>`)
- 폼 레이블 (`<label>` 또는 `aria-label`)
- 에러 메시지가 입력 필드와 연결 (`aria-describedby`)

---

## 3. 2025–2026 웹 UI 트렌드 키워드

리뷰 시 아래 트렌드 적용 여부를 Trend Alignment 차원에서 평가:

### 비주얼 트렌드
- **Glassmorphism**: `backdrop-filter: blur(10-20px)`, 반투명 배경 (`rgba` + 0.1-0.3 opacity), 미묘한 border
- **Bento Grid**: 불균등 그리드 셀로 콘텐츠 카드 배치, `grid-template-columns` 활용, Apple 스타일 레이아웃
- **Micro-interactions**: 버튼 호버 스케일 (1.02–1.05x), 페이지 전환 애니메이션 (300–500ms), 스크롤 기반 요소 등장
- **Dark Mode**: 시스템 설정 연동 (`prefers-color-scheme`), 순수 검정(#000) 대신 진한 회색 (#121212–#1a1a1a)
- **Variable Fonts**: `font-variation-settings`로 단일 폰트 파일에서 weight/width 조절, 성능 최적화

### 인터랙션 트렌드
- **Scroll-driven Animations**: CSS `animation-timeline: scroll()`, parallax 효과
- **View Transitions API**: SPA 내 페이지 전환 시 부드러운 크로스페이드
- **Skeleton Loading**: 콘텐츠 로딩 시 회색 플레이스홀더 블록, 펄스 애니메이션
- **Progressive Disclosure**: 초기에 핵심 정보만 표시, 상세는 클릭/확장으로

### 레이아웃 트렌드
- **Full-bleed Hero**: 뷰포트 너비 이미지/비디오 히어로 섹션
- **Asymmetric Layouts**: 의도적 비대칭으로 시선 유도
- **Oversized Typography**: 히어로 헤딩 48–120px, 임팩트 연출

---

## 4. Navigation & Affordance 가중치 조정 가이드

웹 UI 평가 시 Navigation & Affordance 차원의 세부 가중치:

### Hover 상태 (웹 전용, 30%)
- 모든 클릭 가능 요소에 `cursor: pointer`
- 호버 시 시각적 변화: 색상 변경, 밑줄, 배경색, 그림자
- 호버→클릭 전환 시간 150–200ms (너무 빠르면 깜빡임, 너무 느리면 답답)
- 카드/리스트 아이템 호버 시 전체 영역 하이라이트

### Breadcrumb & 네비게이션 (25%)
- 3단계 이상 depth에서 breadcrumb 필수
- 현재 위치 시각적 강조 (네비게이션 바 active state)
- 모바일에서 breadcrumb → 뒤로가기 또는 축약 표시
- 메가메뉴 사용 시: 열림/닫힘 명확, 카테고리 구분, 키보드 탐색

### Infinite Scroll & 페이지네이션 (20%)
- Infinite scroll 사용 시: 로딩 인디케이터, footer 접근 가능, "맨 위로" 버튼
- 페이지네이션 사용 시: 현재 페이지 강조, 이전/다음 화살표, 총 페이지 수
- 하이브리드: "더 보기" 버튼 + 자동 로딩 조합

### 기타 Affordance (25%)
- 링크: 본문 텍스트와 구별 (색상 + 밑줄 중 최소 하나)
- 버튼: 배경색 또는 border로 명확히 구분, 텍스트 링크와 혼동 불가
- 폼 입력: 포커스 시 border 변경 + 레이블 위치 변화 (floating label 등)
- 드래그 가능 요소: grab cursor + 시각적 핸들
