# Stitch MCP Reference

네이티브/React Native 앱 디자인을 위한 Google Stitch MCP 도구 및 워크플로우.

## 언제 이 모드를 사용하나

- CTO tech-stack의 `design_tool`이 `stitch` 또는 미지정이고 앱 유형이 네이티브/React Native인 경우
- Figma MCP를 사용할 수 없는 네이티브 앱 디자인

---

## Stitch MCP 도구 목록

| 도구 | 설명 |
|------|------|
| `mcp__stitch__create_project` | 새 Stitch 프로젝트 생성 |
| `mcp__stitch__list_projects` | 기존 프로젝트 목록 조회 |
| `mcp__stitch__get_project` | 특정 프로젝트 상세 조회 |
| `mcp__stitch__generate_screen_from_text` | 텍스트 설명으로 스크린 생성 |
| `mcp__stitch__edit_screens` | 기존 스크린 수정 |
| `mcp__stitch__generate_variants` | 디자인 변형 생성 (다크 모드, 다른 레이아웃 등) |
| `mcp__stitch__get_screen` | 스크린 상세 조회 |
| `mcp__stitch__list_screens` | 프로젝트 내 스크린 목록 조회 |
| `mcp__stitch__create_design_system` | 디자인 시스템 생성 |
| `mcp__stitch__list_design_systems` | 디자인 시스템 목록 조회 |
| `mcp__stitch__apply_design_system` | 스크린에 디자인 시스템 적용 |
| `mcp__stitch__update_design_system` | 디자인 시스템 업데이트 |

---

## 워크플로우

### Step 1: 프로젝트 준비

```
1. mcp__stitch__list_projects 로 기존 프로젝트 확인
2. 적합한 프로젝트가 없으면 mcp__stitch__create_project 로 생성
3. mcp__stitch__list_screens 로 기존 스크린 확인
```

### Step 2: 디자인 시스템 설정

디자인 토큰 적용:
```
1. mcp__stitch__list_design_systems 로 기존 시스템 확인
2. 없으면 mcp__stitch__create_design_system 으로 색상/타이포/간격 정의
3. mcp__stitch__apply_design_system 으로 스크린에 적용
```

기본 디자인 토큰 (사용자 제공 없는 경우):

| 토큰 | 값 |
|------|-----|
| Primary | #2563EB (blue-600) |
| Background | #FFFFFF |
| Surface | #F8FAFC (slate-50) |
| Text Primary | #0F172A (slate-900) |
| Text Secondary | #64748B (slate-500) |
| Error | #DC2626 (red-600) |
| Success | #16A34A (green-600) |
| Border Radius | 8px |
| Font | System default (iOS: SF Pro, Android: Roboto) |

### Step 3: 스크린 생성

```
mcp__stitch__generate_screen_from_text 로 텍스트 설명 → 스크린 생성
```

텍스트 설명 작성 원칙:
- 화면 유형 명시 (로그인, 홈, 리스트, 상세, 설정)
- 플랫폼 명시 (iOS: 390x844, Android: 360x800)
- 주요 요소 나열 (네비게이션 바, 버튼 위치, 카드 개수 등)
- 스타일 키워드 (미니멀, 모던, 다크 등)

### Step 4: 세부 조정

```
mcp__stitch__edit_screens 로 생성된 스크린 수정
```

수정 가능 요소:
- 색상, 폰트, 간격
- 레이아웃 구조
- 컴포넌트 추가/제거
- 텍스트 내용

### Step 5: 변형 생성

```
mcp__stitch__generate_variants 로 디자인 변형 생성
```

변형 활용:
- 다크 모드 버전
- 다른 레이아웃 옵션 (탭 바 vs 드로어)
- 컬러 테마 변형

### Step 6: 검증

```
mcp__stitch__get_screen 으로 스크린 상세 확인
```

체크리스트:
- [ ] 레이아웃이 화면 크기에 맞는가
- [ ] 디자인 토큰이 일관되게 적용되었는가
- [ ] Safe Area (노치, 홈바) 고려했는가
- [ ] 터치 타겟 최소 44px 이상인가

---

## 네이티브 앱 디자인 원칙

### iOS 가이드라인 준수
- 탭 바: 하단 고정, 아이콘 + 레이블
- 네비게이션 바: 상단 고정, 타이틀 + 백 버튼
- Safe Area: 상단 44px(상태바+네비바), 하단 34px(홈 인디케이터) 여백
- 최소 터치 타겟: 44x44pt

### Android 가이드라인 준수
- 바텀 네비게이션: 하단 고정
- 앱 바: 상단 고정
- 상태 바: 시스템 영역 24px
- 최소 터치 타겟: 48x48dp

### 공통 모바일 원칙
- 단일 열 레이아웃 우선
- 스크롤 방향: 수직 스크롤 기본
- 폰트 크기 최소: 본문 14sp/pt, 캡션 12sp/pt
- 색상 대비: 최소 4.5:1 (접근성)

---

## Stitch MCP 연결 실패 처리

1. 1회 재시도
2. 재시도 후에도 실패 시: "Stitch MCP 연결 불가. HTML/CSS 모드로 전환합니다."
3. HTML/CSS 모드로 폴백하여 모바일 화면 크기(390x844px)로 목업 생성

---

## 화면 유형별 텍스트 설명 템플릿

### 로그인
```
iOS 로그인 화면 (390x844). 상단 앱 로고, 중앙 폼(이메일+비밀번호 입력, 로그인 버튼), 하단 소셜 로그인 버튼들. 미니멀 화이트 디자인.
```

### 홈/피드
```
iOS 홈 피드 (390x844). 상단 검색바+프로필 아이콘, 중앙 카드 피드 (무한 스크롤), 하단 탭 바 5개. 모던 카드 디자인.
```

### 리스트
```
iOS 리스트 화면 (390x844). 상단 네비게이션 바(제목+필터), 검색바, 아이템 리스트 (이미지+제목+부제목+화살표), 하단 탭 바. 미니멀.
```

### 상세
```
iOS 상세 화면 (390x844). 상단 네비게이션(뒤로+공유 버튼), 히어로 이미지(1:1 비율), 제목+설명 텍스트, 액션 버튼(CTA). 클린 디자인.
```
