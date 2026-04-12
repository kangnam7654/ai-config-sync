# Web Mockup (HTML/CSS) Reference

웹앱 HTML/CSS 목업 모드에서 사용하는 패턴 및 규칙.

## 언제 이 모드를 사용하나

- CTO tech-stack의 `design_tool`이 `html` 또는 미지정이고 앱 유형이 웹(SPA/SSR/SSG)인 경우
- Figma MCP를 사용할 수 없는 경우 폴백

---

## 파일 출력 규칙

| 항목 | 규칙 |
|------|------|
| 화면 파일 경로 | `mockups/{screen-name}.html` |
| 토큰 파일 경로 | `mockups/tokens.css` |
| 슬라이드 파일 경로 | `mockups/slides/slide-{N}.html` |
| 파일 형식 | Self-contained HTML (인라인 CSS 또는 tokens.css import) |
| 기존 파일 | 덮어쓰지 않는다. 새 화면은 새 파일명으로 추가. |

---

## 디렉토리 초기화

```bash
mkdir -p mockups
```

---

## tokens.css 구조

```css
:root {
  /* Colors */
  --color-primary: #2563EB;
  --color-bg: #FFFFFF;
  --color-surface: #F8FAFC;
  --color-text-primary: #0F172A;
  --color-text-secondary: #64748B;
  --color-border: #E2E8F0;
  --color-error: #DC2626;
  --color-success: #16A34A;

  /* Typography */
  --font-family: Inter, system-ui, -apple-system, sans-serif;
  --font-heading-h1: 24px;
  --font-heading-h2: 20px;
  --font-heading-h3: 16px;
  --font-body: 14px;
  --font-caption: 12px;

  /* Spacing */
  --spacing-xs: 8px;
  --spacing-sm: 12px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;

  /* Border */
  --border-radius: 8px;
  --border-color: var(--color-border);
  --border-width: 1px;
}
```

---

## 반응형 브레이크포인트

모든 화면 파일에 반드시 포함:

```css
/* Mobile */
@media (max-width: 375px) { ... }

/* Tablet */
@media (max-width: 768px) { ... }

/* Desktop */
@media (min-width: 1440px) { ... }
```

---

## 화면 유형별 레이아웃 패턴

### 로그인

```html
<div class="login-container">
  <div class="login-card">
    <div class="logo">...</div>
    <form class="login-form">
      <input type="email" placeholder="이메일" />
      <input type="password" placeholder="비밀번호" />
      <button type="submit" class="btn-primary">로그인</button>
    </form>
    <a href="#" class="link-secondary">비밀번호를 잊으셨나요?</a>
  </div>
</div>
```

CSS: 중앙 정렬 카드 (max-width: 400px, margin: auto, padding: 32px)

### 대시보드

```html
<div class="dashboard-layout">
  <aside class="sidebar" style="width: 240px;">네비게이션</aside>
  <main class="main-content">
    <header class="page-header">...</header>
    <div class="card-grid">...</div>
  </main>
</div>
```

CSS: `display: flex`, sidebar `flex-shrink: 0`

### 리스트

```html
<div class="list-layout">
  <div class="list-header">
    <input type="search" />
    <div class="filters">...</div>
  </div>
  <table class="data-table">...</table>
  <div class="pagination">...</div>
</div>
```

### 상세 페이지

```html
<div class="detail-layout">
  <header class="detail-header">제목 + 액션 버튼</header>
  <div class="detail-content">이미지/텍스트 영역</div>
  <footer class="detail-actions">버튼 그룹</footer>
</div>
```

### 설정

```html
<div class="settings-layout">
  <nav class="settings-nav">섹션 리스트</nav>
  <div class="settings-content">
    <section class="form-group">...</section>
  </div>
</div>
```

### 모달

```html
<div class="modal-overlay">
  <div class="modal-card">
    <h2 class="modal-title">제목</h2>
    <div class="modal-body">콘텐츠</div>
    <div class="modal-actions">
      <button class="btn-secondary">취소</button>
      <button class="btn-primary">확인</button>
    </div>
  </div>
</div>
```

CSS: `position: fixed; inset: 0; background: rgba(0,0,0,0.5);` + 중앙 카드

---

## 기본 디자인 토큰 (사용자 제공 없는 경우)

| 토큰 | 값 |
|------|-----|
| Primary | #2563EB (blue-600) |
| Background | #FFFFFF |
| Surface | #F8FAFC (slate-50) |
| Text Primary | #0F172A (slate-900) |
| Text Secondary | #64748B (slate-500) |
| Border | #E2E8F0 (slate-200) |
| Error | #DC2626 (red-600) |
| Success | #16A34A (green-600) |
| Border Radius | 8px |
| Font | Inter (없으면 시스템 기본) |
| Heading Size | 24/20/16px (H1/H2/H3) |
| Body Size | 14px |
| Spacing | 8/16/24/32px |

---

## HTML/CSS 코딩 원칙

1. **시맨틱 HTML**: `<header>`, `<main>`, `<nav>`, `<section>`, `<article>`, `<footer>` 사용
2. **CSS 변수**: 색상, 폰트, 간격 모두 CSS 변수 사용. 하드코딩 금지.
3. **Flexbox/Grid**: 레이아웃은 Flexbox 또는 CSS Grid. float/absolute 배치 최소화.
4. **Hover/Focus 상태**: 버튼, 링크, 입력 필드에 반드시 포함.
5. **접근성**: `aria-label`, `role`, `tabindex` 기본 적용. 색상 대비 최소 4.5:1.

---

## 검증 절차

```bash
# 브라우저에서 열어 시각적 확인
open mockups/{screen-name}.html
```

체크리스트:
- [ ] 정렬 (좌우 대칭, 균등 간격)
- [ ] 텍스트 가독성 (색상 대비)
- [ ] 반응형 동작 (375/768/1440px)
- [ ] CSS 변수 사용 (하드코딩 없음)
- [ ] Hover/Focus 상태 작동

문제 발견 시 수정 후 재확인. 최대 3회.

---

## 슬라이드 모드 (HTML/CSS)

"발표자료", "슬라이드", "피치덱", "프레젠테이션" 키워드 → 슬라이드 모드.

### 슬라이드 기본 설정

| 항목 | 값 |
|------|-----|
| 슬라이드 크기 | 1920 x 1080 (16:9) |
| 배경색 | #FFFFFF (라이트) 또는 #0F172A (다크) |
| 마진 | 상하좌우 80px |
| 제목 폰트 | Inter Bold, 48px |
| 본문 폰트 | Inter Regular, 24px |
| 부제목 폰트 | Inter Medium, 32px |
| 캡션 폰트 | Inter Regular, 16px, Text Secondary 색상 |

### 슬라이드 파일 경로
- `mockups/slides/slide-{N}.html`
- `mkdir -p mockups/slides`

### 슬라이드 유형별 레이아웃

| 유형 | 구조 | 사용 시점 |
|------|------|----------|
| **타이틀** | 중앙 정렬: 제목 (48px) + 부제목 (32px) + 발표자 (16px) | 첫 슬라이드 |
| **섹션 구분** | 중앙 정렬: 섹션 번호 (120px, Primary) + 섹션 제목 (48px) | 챕터 전환 |
| **텍스트 + 불릿** | 좌측: 제목 (36px) + 불릿 리스트 (24px, 줄간격 48px) | 핵심 포인트 |
| **2단 분할** | 좌측 50%: 텍스트, 우측 50%: 이미지/차트 | 비교, 설명 + 시각자료 |
| **3단 카드** | 상단: 제목, 하단: 3개 카드 (560px 너비, 40px 간격) | 3개 항목 비교 |
| **큰 숫자** | 중앙: 핵심 수치 (120px, Primary) + 설명 (24px) | KPI, 통계 강조 |
| **인용** | 중앙: 큰따옴표 (80px) + 인용문 (32px, 이탤릭) + 출처 (16px) | 고객 후기, 명언 |
| **마무리** | 중앙: "감사합니다" / CTA (48px) + 연락처 (24px) | 마지막 슬라이드 |

### 슬라이드 디자인 규칙

1. 한 슬라이드 텍스트 최대 6줄. 초과 시 2개 슬라이드로 분할.
2. 불릿 포인트 슬라이드당 최대 5개. 초과 시 분할.
3. 제목은 모든 슬라이드에 포함 (타이틀/마무리 제외).
4. 슬라이드 번호 우하단 표시 (16px, Text Secondary, 타이틀 제외).
5. 일관된 색상 팔레트 전 슬라이드 적용.
6. 텍스트-배경 명암비 최소 4.5:1.

### 슬라이드 장수 기본값
- 미지정 시: 5~8장 (타이틀 1 + 본문 3~5 + 마무리 1)
- 구성안을 사용자에게 먼저 제안하고 승인 후 생성
