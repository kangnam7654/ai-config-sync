# UI Figma Reference

Figma MCP를 사용하는 UI 디자인 모드. 화면, 컴포넌트, 디자인 토큰, 슬라이드 생성에 사용.

## 언제 이 모드를 사용하나

- CTO tech-stack의 `design_tool`이 `figma`인 경우
- Figma UI 화면/컴포넌트 디자인 요청
- 디자인 토큰/변수 설정 요청
- 슬라이드/발표자료 디자인 요청 (Figma Slides)
- UX 산출물을 Figma에 시각화하는 경우 (ux-research.md와 조합)

---

## NEVER Rules (Figma 전용)

1. NEVER Figma에 요소를 빈 캔버스에 직접 배치하지 마라. 반드시 Section 또는 Frame 안에 배치한다.
2. NEVER 컴포넌트를 인스턴스화하기 전에 `figma_search_components`를 건너뛰지 마라. 기존 컴포넌트가 있을 수 있다.
3. NEVER 스크린샷 없이 디자인 완료를 선언하지 마라. 반드시 Visual Validation을 수행한다.
4. NEVER 이전 세션의 nodeId를 재사용하지 마라. 매 세션 시작 시 `figma_search_components`로 새로 조회한다.
5. NEVER "hug contents"를 기본으로 사용하지 마라. 레이아웃 컨테이너는 "fill container"를 우선 사용한다.
6. NEVER Visual Validation 루프를 3회 초과 반복하지 마라. 3회 후에도 문제가 있으면 현재 상태를 스크린샷과 함께 사용자에게 보고한다.
7. NEVER 색상을 하드코딩하지 마라. 디자인 토큰/변수가 존재하면 변수를 바인딩한다.
8. NEVER SLIDE 노드에 직접 요소를 배치하지 마라. 반드시 SLIDE 안에 Frame을 먼저 생성하고 그 Frame 안에 모든 요소를 배치한다.
9. NEVER `figma.getNodeById()`를 사용하지 마라. Figma Slides는 dynamic-page 접근 모드이므로 반드시 `await figma.getNodeByIdAsync()`를 사용한다.
10. NEVER `createSlide()` 후 내부 Frame의 좌표를 확인하지 않고 진행하지 마라. Frame의 x, y가 자동으로 offset될 수 있으므로 반드시 `frame.x = 0; frame.y = 0;`으로 보정한다.

## ALWAYS Rules (Figma 전용)

1. ALWAYS 세션 시작 시 `figma_search_components`를 실행하여 사용 가능한 컴포넌트를 파악한다.
2. ALWAYS 요소 생성 후 `figma_take_screenshot`으로 결과를 확인한다.
3. ALWAYS Section 또는 Frame을 먼저 생성하고 그 안에 디자인 요소를 배치한다.
4. ALWAYS Auto Layout을 사용하여 요소를 정렬한다 (수동 좌표 배치 최소화).
5. ALWAYS 디자인 완료 시 전체 화면 스크린샷을 찍어 사용자에게 보여준다.

---

## Figma 환경 준비

```
1. figma_get_status — Figma 연결 상태 확인
2. figma_search_components — 사용 가능한 컴포넌트 목록 조회
3. figma_list_open_files — 현재 열린 파일 확인
4. 페이지 확인 또는 생성
```

### 페이지 중복 방지 코드

```javascript
await figma.loadAllPagesAsync();
const existing = figma.root.children.find(p => p.name === 'Design Name');
if (!existing) {
  const page = figma.createPage();
  page.name = 'Design Name';
  figma.currentPage = page;
}
```

---

## 구조 생성

### Section 생성 (최상위 컨테이너)

```javascript
const section = figma.createSection();
section.name = 'Screen Name';
section.x = 0;
section.y = 0;
```

### 메인 Frame 생성

```javascript
const frame = figma.createFrame();
frame.name = 'Screen Name';
frame.resize(1440, 900); // 웹 기본값
frame.layoutMode = 'VERTICAL';
frame.primaryAxisAlignItems = 'CENTER';
frame.counterAxisAlignItems = 'CENTER';
frame.paddingTop = 24;
frame.paddingBottom = 24;
frame.paddingLeft = 24;
frame.paddingRight = 24;
frame.itemSpacing = 16;
section.appendChild(frame);
```

플랫폼별 Frame 크기:
- 웹: 1440x900px
- 모바일: 390x844px
- 태블릿: 768x1024px

---

## 디자인 요소 배치

각 요소 생성 시 사용하는 Figma MCP 도구:
- `figma_create_child` — 요소 생성
- `figma_set_fills` — 색상 적용
- `figma_set_text` — 텍스트 설정
- `figma_resize_node` — 크기 조정
- `figma_instantiate_component` — 기존 컴포넌트 인스턴스화
- Auto Layout 속성으로 정렬

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

### 디자인 토큰/변수 생성

```
figma_setup_design_tokens — 일괄 토큰 생성
또는
figma_create_variable_collection + figma_batch_create_variables — 단계별 생성
```

---

## Visual Validation 루프 (필수)

생성 → 스크린샷 → 분석 → 수정 반복:

1. `figma_take_screenshot` — 현재 상태 캡처
2. 스크린샷 분석 체크리스트:
   - [ ] 요소가 정렬되어 있는가 (좌우 대칭, 균등 간격)
   - [ ] 텍스트가 잘리지 않는가
   - [ ] 색상 대비가 충분한가 (가독성)
   - [ ] 빈 공간이 과도하거나 요소가 겹치지 않는가
   - [ ] "hug contents" 대신 "fill container"를 사용했는가
   - [ ] 모든 요소가 Section/Frame 안에 있는가
3. 문제 발견 시 수정 후 다시 스크린샷
4. **최대 3회 반복**. 3회 후에도 문제가 있으면 현재 상태를 사용자에게 보고.

---

## 컴포넌트 생성 가이드

### 버튼
- Variants: Primary, Secondary, Outline, Ghost
- States: Default, Hover, Disabled
- Sizes: Small (32px), Medium (40px), Large (48px)

### 입력 필드
- States: Default, Focus, Error, Disabled
- Types: Text, Password, Search, Textarea

### 카드
- Variants: Default, Elevated, Outlined
- 구조: Image (optional) + Title + Description + Actions

컴포넌트 생성 후 `figma_arrange_component_set`으로 variant grid 정렬.

---

## UX 산출물 Figma 시각화

ux-research.md의 산출물을 Figma에 생성할 때:

### 유저 페르소나
- 페르소나 카드: 320x400px Frame
- 별도 Figma 페이지 또는 섹션에 배치

### 유저 저니맵
- 프레임 크기: 1920x600px
- 수평 타임라인 레이아웃

### 정보 구조 (IA)
- 별도 페이지 "IA / Sitemap"에 배치
- Figma Connector 도구로 연결선

### 유저 플로우
- 별도 섹션 "User Flow"에 배치
- 노드: 사각형(화면), 다이아몬드(분기), 원(시작/끝)
- Figma Connector로 화살표 연결

### 와이어프레임
- 별도 페이지 "Wireframes"에 배치
- 그레이스케일 색상만 사용 (#F3F4F6, #6B7280, #D1D5DB)

---

## 슬라이드/발표자료 모드 (Figma Slides)

"발표자료", "슬라이드", "피치덱", "프레젠테이션" 키워드 → 슬라이드 모드.

### 슬라이드 기본 설정

| 항목 | 값 |
|------|-----|
| 프레임 크기 | 1920 x 1080 (16:9) |
| 배경색 | #FFFFFF (라이트) 또는 #0F172A (다크) |
| 마진 | 상하좌우 80px |
| 제목 폰트 | Inter Bold, 48px |
| 본문 폰트 | Inter Regular, 24px |
| 부제목 폰트 | Inter Medium, 32px |
| 캡션 폰트 | Inter Regular, 16px, Text Secondary 색상 |
| 슬라이드 간격 | 프레임 간 X축 100px 간격으로 수평 배치 |

### Figma Slides API 주의사항

Figma Slides 파일(`/slides/` URL)에서는 일반 Design 파일과 API 동작이 다르다:

| 항목 | 일반 Design 파일 | Figma Slides 파일 |
|------|----------------|-----------------|
| 최상위 구조 | Page → Section → Frame | Page → SLIDE_GRID → SLIDE_ROW → SLIDE |
| 슬라이드 생성 | `figma.createFrame()` | `figma.createSlide()` |
| 노드 조회 | `figma.getNodeById()` | `await figma.getNodeByIdAsync()` (필수) |
| 좌표 | Frame x,y 그대로 적용 | SLIDE 내부 Frame의 x,y가 자동 offset될 수 있음 — 반드시 0,0으로 보정 |

### 슬라이드 생성 워크플로우

1. `figma.createSlide()`로 SLIDE 노드 생성
2. SLIDE 안에 Auto Layout Frame 생성:

```javascript
const slide = figma.createSlide();
slide.name = `${n} - ${slideTitle}`;

const frame = figma.createFrame();
frame.name = "Content";
frame.resize(1920, 1080);
frame.x = 0;  // 반드시 0으로 설정 — 자동 offset 보정
frame.y = 0;  // 반드시 0으로 설정
frame.fills = [{type: 'SOLID', color: {r: 1, g: 1, b: 1}}];
frame.layoutMode = 'VERTICAL';
frame.primaryAxisAlignItems = 'MIN';
frame.counterAxisAlignItems = 'MIN';
frame.paddingTop = 100;
frame.paddingBottom = 100;
frame.paddingLeft = 120;
frame.paddingRight = 120;
frame.itemSpacing = 48;
frame.layoutSizingHorizontal = 'FIXED';
frame.layoutSizingVertical = 'FIXED';
slide.appendChild(frame);
```

3. Frame 안에 콘텐츠 추가 — 절대 좌표가 아닌 Auto Layout으로 배치
4. 생성 후 Frame 좌표 검증: `frame.x === 0 && frame.y === 0` 확인. 아니면 보정.
5. Visual Validation: `figma_capture_screenshot` with nodeId

### 슬라이드 순서 변경

```javascript
const grid = await figma.getNodeByIdAsync('0:3');
const row = grid.children[0];
const slideToMove = await figma.getNodeByIdAsync(slideId);
row.appendChild(slideToMove); // 맨 뒤로 이동
```

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

### 슬라이드 콘텐츠 생성

- 주제만 제공: 구성안 먼저 제안 → 사용자 승인 후 생성
- 주제 + 내용 제공: 바로 생성
- "N장으로": 지정된 장수에 맞춰 구성

### Figma 프레젠테이션 모드 안내

슬라이드 완성 후:
"Figma에서 첫 번째 슬라이드 프레임을 선택한 뒤 오른쪽 상단 ▶ (Present) 버튼을 누르면 전체화면 프레젠테이션이 시작됩니다. 화살표 키로 슬라이드를 넘길 수 있습니다."

---

## Edge Cases (Figma 전용)

| 상황 | 처리 |
|------|------|
| **Figma 연결 안 됨** | `figma_reconnect` 시도. 실패 시 "Figma 플러그인이 실행 중인지 확인해주세요." 보고. 작업 중단. |
| **컴포넌트 검색 결과 0건** | 처음부터 생성. "기존 디자인 시스템이 없어 기본 토큰으로 생성합니다." 알림. |
| **페이지가 이미 존재** | 기존 페이지에 새 Section 추가. 기존 디자인 덮어쓰지 않는다. |
| **사용자가 브랜드 가이드 제공** | `figma_setup_design_tokens`로 사용자 제공 값 적용. |
| **figma_execute 실행 에러** | `figma_get_console_logs`로 에러 확인. 코드 수정 후 재시도. 3회 실패 시 사용자에게 보고. |
| **SLIDE 내 Frame 좌표 offset 발생** | `frame.x = 0; frame.y = 0;` 보정. 보정 후 스크린샷으로 확인. |
| **`getNodeById()` 에러** ("Cannot call with documentAccess: dynamic-page") | Figma Slides 파일. 모든 조회를 `await figma.getNodeByIdAsync()`로 변경. |
| **Figma Design vs Figma Slides 구분** | URL에 `/slides/` → Figma Slides. `/design/` → 일반 Design 파일. |
