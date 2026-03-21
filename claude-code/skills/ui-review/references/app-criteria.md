# App UI Review Criteria

ui-review 스킬이 모바일 앱(iOS/Android)을 평가할 때 참조하는 플랫폼별 기준.

---

## 1. Apple Human Interface Guidelines (HIG) 핵심

### Safe Area
- **상단**: Dynamic Island / 노치 영역 침범 금지 (약 59pt, 기기별 상이)
- **하단**: Home Indicator 영역 (34pt) 위에 인터랙티브 요소 배치 금지
- **좌우**: 최소 16pt 여백 (standard margin)
- `safeAreaInsets` 준수 여부를 스크린샷에서 확인: 콘텐츠가 잘리거나 시스템 UI와 겹치면 감점

### Navigation Bar (44pt)
- 높이: 44pt (Large Title 모드 시 최대 96pt)
- Back 버튼: 왼쪽 정렬, chevron + 이전 화면 제목 (또는 "Back")
- 제목: 중앙 정렬 (standard) 또는 좌측 대형 (large title)
- 우측: 최대 2개 액션 버튼

### Tab Bar (49pt)
- 높이: 49pt (Home Indicator 포함 시 83pt)
- 최소 3개, 최대 5개 탭
- 각 탭: 아이콘 (25x25pt) + 텍스트 레이블 (10pt)
- 선택된 탭: 틴트 컬러로 강조, 비선택: 시스템 그레이
- 스크롤 시 Tab Bar 숨김 가능하나 쉽게 복원 가능해야 함

### 터치 타겟
- 최소 44x44pt (실제 시각적 크기는 더 작을 수 있으나 히트 영역은 44pt 이상)
- 인접 터치 타겟 간 최소 8pt 간격
- 버튼 내 텍스트: 최소 15pt (SF Pro 기준)

---

## 2. Material Design 3 (M3) 핵심

### Color Roles
- **Primary**: 주요 CTA 버튼, FAB, 선택된 상태
- **Secondary**: 필터 칩, 토글, 보조 버튼
- **Tertiary**: 대비를 위한 보조 색상 (선택적)
- **Surface**: 배경, 카드, 시트
- **Error**: 에러 상태, 유효성 검사 실패
- **On-[Color]**: 해당 색상 위의 텍스트/아이콘 색상 (대비 보장)
- 다이나믹 컬러: Android 12+ 벽지 기반 자동 팔레트 생성

### Shape System
- **Small** (4dp radius): 칩, 스낵바, 텍스트 필드
- **Medium** (12dp radius): 카드, 다이얼로그
- **Large** (16dp radius): 모달 바텀 시트, 네비게이션 드로어
- **Extra Large** (28dp radius): FAB, 풀스크린 시트
- 일관성: 같은 계층의 요소는 같은 radius 사용

### Typography Scale
- **Display** (Large/Medium/Small): 57/45/36sp — 히어로 텍스트, 대형 숫자
- **Headline** (Large/Medium/Small): 32/28/24sp — 섹션 제목
- **Title** (Large/Medium/Small): 22/16/14sp — 카드/리스트 제목
- **Body** (Large/Medium/Small): 16/14/12sp — 본문 텍스트
- **Label** (Large/Medium/Small): 14/12/11sp — 버튼, 탭, 칩

---

## 3. iOS vs Android 비교표

| 항목 | iOS (HIG) | Android (M3) | 리뷰 포인트 |
|------|-----------|--------------|-------------|
| **Back Navigation** | 좌측 상단 chevron + edge swipe | 시스템 back 버튼/gesture + 앱 내 arrow | 플랫폼 관습 준수 여부 |
| **Status Bar** | 밝은/어두운 콘텐츠, Dynamic Island 대응 | 시스템 색상 또는 투명 + edge-to-edge | 상태 바 콘텐츠와 충돌 여부 |
| **Bottom Sheet** | UISheetPresentationController detents (.medium, .large) | BottomSheetBehavior (collapsed, expanded, half-expanded) | 드래그 핸들 존재, 스냅 포인트 |
| **Pull to Refresh** | UIRefreshControl (네이티브 스피너) | SwipeRefreshLayout (원형 프로그레스) | 일관된 위치와 애니메이션 |
| **Typography** | SF Pro (시스템), Dynamic Type 지원 | Roboto (시스템) 또는 커스텀 + sp 단위 | 접근성 텍스트 크기 대응 |
| **색상 시스템** | 시스템 컬러 (systemBlue 등), 다크모드 자동 | Material Theme, 다이나믹 컬러 | 다크모드 대응 일관성 |
| **아이콘** | SF Symbols (weight/scale 매칭) | Material Icons (filled/outlined 선택) | 아이콘 스타일 일관성 |
| **알림/토스트** | 시스템 알림, 인앱 배너 | Snackbar (하단), Toast (비권장) | 위치와 지속시간 적절성 |
| **제스처** | swipe back, long press, 3D/Haptic Touch | swipe, long press, edge gesture | 플랫폼 네이티브 제스처 지원 |

---

## 4. 모바일 전용 가중치 조정

앱 UI 평가 시 아래 항목에 추가 가중치를 부여:

### Gesture 지원 (가중치 +1.0)
- 스와이프 삭제/아카이브 (리스트 아이템)
- 핀치 줌 (이미지/지도)
- 스와이프 네비게이션 (탭 간 이동)
- 풀 다운 리프레시
- 제스처와 버튼 동시 제공 (제스처 발견성 보장)

### Haptic Feedback (가중치 +0.5)
- 토글 전환 시 촉각 피드백
- 삭제/중요 액션 시 경고 촉각
- 스크롤 끝 도달 시 바운스 피드백 (iOS)
- 길게 누르기 성공 시 피드백
- 스크린샷에서 관찰 불가 → N/O 처리, 단 관련 UI 패턴 존재 시 추론 가능

### Safe Area 준수 (가중치 +1.5)
- 콘텐츠가 노치/Dynamic Island/Home Indicator와 겹치지 않음
- 가로 모드에서 좌우 safe area 준수
- 키보드 표시 시 입력 필드 가림 방지 (keyboard avoidance)
- 모달/시트에서도 safe area 존중

### 모바일 성능 지표 (관찰 가능 시)
- 스크롤 부드러움: 끊김 없이 60fps
- 이미지 로딩: 점진적 로딩 또는 placeholder
- 전환 애니메이션: 300ms 이내, 자연스러운 이징
- 로딩 상태: 스켈레톤 또는 인디케이터

### 차원별 가중치 조정 요약

| 차원 | 웹 기본 가중치 | 앱 조정 가중치 | 이유 |
|------|---------------|---------------|------|
| Visual Hierarchy | 1.0 | 1.0 | 동일 |
| Color & Contrast | 1.0 | 1.0 | 동일 |
| Typography | 1.0 | 1.2 | Dynamic Type/sp 대응 중요 |
| Spacing & Alignment | 1.0 | 1.3 | Safe area 준수 필수 |
| Layout & Composition | 1.0 | 1.0 | 동일 |
| Navigation & Affordance | 1.0 | 1.5 | 제스처, 탭바, 네이티브 패턴 |
| Consistency | 1.0 | 1.2 | 플랫폼 가이드라인 준수 |
| Trend Alignment | 1.0 | 0.8 | 모바일은 트렌드보다 표준 준수 우선 |
