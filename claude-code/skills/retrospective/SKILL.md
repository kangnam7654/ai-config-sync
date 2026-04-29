---
name: retrospective
description: >
  4L 회고 기법(Liked/Learned/Lacked/Longed For)으로 git 커밋 히스토리와 위키 작성 기록을 분석해
  구조화된 회고를 생성하고 ~/wiki/에 저장하는 스킬. 두 가지 모드: (1) 통합 retro — 기간별,
  여러 프로젝트, milestone retro와 이전 retro의 Action Items를 1차 입력으로 사용, 마지막에 Rule 업데이트 후보 제시.
  (2) 마일스톤 retro — 특정 프로젝트의 milestone 완료 시점, raw git log 직접 분석.
  사용자가 "retro", "회고", "retrospective", "/retrospective", "지난 작업 돌아보자",
  "최근 작업 정리해줘", "이번 주/달 회고 해줘", "milestone retro", "마일스톤 회고" 등을
  언급할 때 반드시 이 스킬을 사용하세요.
---

# Retrospective Skill

회고는 **4L 기법** 사용. 카테고리 정의(Liked/Learned/Lacked/Longed For)와 구분 기준은 항상
`~/wiki/Concepts/4L-Retrospective.md`를 읽어 적용. 정의를 이 스킬에 인라인하지 않음 — 단일 출처 유지.

두 가지 모드:
- **통합 retro**: 기간 기반 → `~/wiki/Retro/regular/`
- **마일스톤 retro**: 특정 프로젝트의 milestone 완료 → `~/wiki/Retro/milestones/<프로젝트>/`

모드가 불분명하면 사용자에게 질문.

---

## 공통 1단계: 위키 pull + 4L 정의 로드

```bash
git -C ~/wiki pull --rebase
```

`~/wiki/Concepts/4L-Retrospective.md`를 읽어 4L 카테고리 정의 확인. 특히 Lacked vs Longed For,
Liked vs Learned 구분 기준을 적용해야 회고가 4L의 의도대로 작동.

---

## 모드 A: 통합 Retro

### 2단계: 기간 결정

사용자가 명시한 기간 그대로. 미명시 시:

```bash
ls ~/wiki/Retro/regular/ 2>/dev/null | sort | tail -1
```

- 파일이 있으면 해당 날짜 이후 ~ 오늘
- 없으면 최근 2주

### 3단계: 데이터 수집 (계층적 입력)

통합 retro는 raw 커밋에서 직접 도출하지 않는다. 정제된 입력을 우선 사용.

**3-A. 기간 내 작성된 milestone retro 읽기 (1차 입력)**

```bash
git -C ~/wiki log --since="<start_date>" --diff-filter=A --name-only --pretty=format: \
  | grep '^Retro/milestones/' | sort -u
```

해당 파일들을 모두 읽고, 각 파일의 Liked/Learned/Lacked/Longed For를 통합 retro의 출발점으로 사용.

**3-B. 직전 통합 retro의 Action Items 추적 (1차 입력)**

```bash
ls ~/wiki/Retro/regular/ | sort | tail -2
```

직전 통합 retro의 `## Action Items` 섹션을 읽고, 이번 기간에 실제로 처리됐는지 git 히스토리로 확인.

- 처리됐으면 → Liked / Learned에 반영
- 안 됐으면 → Lacked에 반영 ("지난 회고 액션이 진행 안 됨")

**3-C. milestone retro가 없는 영역의 raw git log (보조 입력)**

milestone retro가 커버하지 않은 프로젝트나 기간이 있으면 직접 분석:

```bash
git -C ~/wiki log --since="<start_date>" --oneline --no-merges
git log --since="<start_date>" --oneline --no-merges
git -C ~/wiki log --since="<start_date>" --name-only --pretty=format: | sort -u | grep '\.md$'
```

변경된 위키 `.md` 중 의미있는 파일은 직접 읽기.

### 4단계: 통합 retro 작성

프로젝트별 섹션 + 전체 인사이트 + Action Items:

```markdown
# Retrospective: <start_date> ~ <end_date>

## <프로젝트명>

### Liked (좋았던 것)
### Learned (배운 것)
### Lacked (아쉬웠던 것)
### Longed For (바랐던 것)

## <또 다른 프로젝트>

### Liked / Learned / Lacked / Longed For

## 전체 인사이트

- 기간을 관통하는 패턴이나 교훈
- 시간 배분, 집중도, 습관 관련 관찰
- (있다면) 직전 회고 Action Items 처리 현황 요약

## Action Items

- Lacked / Longed For에서 도출한 구체적·측정 가능한 다음 행동
- 막연한 다짐("더 꼼꼼하게") 금지
```

각 항목은 실제 사실(커밋, 변경 파일, 이전 retro 인용)에 기반.

**4L 카테고리 적용 시 주의:** Lacked는 _이번에 부족했던 것_ (회고적), Longed For는 _있었으면 하는 것_ (미래지향). 같은 문제의 두 측면이면 둘 다 기록.

### 5단계: Rule 업데이트 _후보_ 제시 (자동 수정 금지)

Action Items 중 **반복될 가능성이 있는 원칙**을 `~/wiki/Rules/`에 반영할 _후보_ 로 제시.

```bash
ls ~/wiki/Rules/
cat ~/wiki/Rules/MAP.md
```

회고 파일 안에 다음 섹션을 추가:

```markdown
## Rule 업데이트 제안

> 이 섹션은 _제안_입니다. 실제 Rule 파일 수정은 사용자 승인 후 별도 작업으로 처리.

- **대상 파일:** `~/wiki/Rules/Refactoring.md` (또는 신규)
- **추가/수정 내용:**
  ```
  (제안하는 rule 텍스트)
  ```
- **근거:** 이번 회고의 어떤 항목에서 도출됐는지 (Lacked/Longed For 인용)
```

판단 기준:
- "다음에 또 같은 실수를 할 것 같다" → Rule 후보
- 한두 번 우연은 후보로 만들지 않음 — 패턴이 보일 때만

**중요: `~/wiki/Rules/` 파일을 직접 수정하지 않는다.** 사용자가 회고를 검토 후 별도로 Rule 파일을 수정/커밋해야 함. 회고 스킬은 후보만 제시.

### 6단계: 저장 및 커밋

```bash
mkdir -p ~/wiki/Retro/regular

# 종료 날짜 기준
~/wiki/Retro/regular/YYYY-MM-DD.md

git -C ~/wiki add Retro/regular/YYYY-MM-DD.md
git -C ~/wiki commit -m "retro: <start_date> ~ <end_date>"
```

`Rules/`는 add하지 않음 (5단계는 제안만). push 안 함 (NEVER #2).

저장 경로 + Rule 업데이트 제안 개수 + 회고 요약 출력.

---

## 모드 B: 마일스톤 Retro

특정 프로젝트의 milestone(기능 완성, 버전 릴리즈, 큰 리팩터 등) 완료 시점 회고.
입력은 raw git log 직접 분석.

### 2단계: 정보 수집

사용자에게 확인:
- 프로젝트명
- 마일스톤 설명 (예: "v0.2 — Windows pull-only 지원 완료")
- 기간 (마일스톤 시작 ~ 오늘, 또는 명시된 기간)

### 3단계: 데이터 수집

```bash
git -C <project_path> log --since="<start_date>" --oneline --no-merges
git -C <project_path> diff <start_commit>..HEAD --stat
```

해당 프로젝트의 위키 문서가 있으면 함께 참조.

### 4단계: 마일스톤 retro 작성

```markdown
# Milestone Retro: <프로젝트명> — <마일스톤 설명>

_<start_date> ~ <end_date>_

## 마일스톤 개요

- 핵심 커밋 흐름
- 무엇을 달성했는가

## Liked (좋았던 것)
## Learned (배운 것)
## Lacked (아쉬웠던 것)
## Longed For (바랐던 것)

## 다음 마일스톤 메모

- 이 프로젝트를 계속한다면 다음엔 뭘 다르게 할지
- Longed For 중 다음 마일스톤에서 우선 처리할 것
```

### 5단계: 저장 및 커밋

```bash
mkdir -p ~/wiki/Retro/milestones/<프로젝트명>

# 파일명: <마일스톤 슬러그>-<날짜>.md
~/wiki/Retro/milestones/ai-config-sync/v0.2-2026-04-29.md

git -C ~/wiki add Retro/milestones/
git -C ~/wiki commit -m "retro(milestone): <프로젝트> <마일스톤>"
```
