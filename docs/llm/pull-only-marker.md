---
type: design-spec
target: pull-only 마커 + 대화형 setup 스크립트
---

# Pull-Only 마커 + 대화형 Setup

## 목적

대화형 `setup.sh`로 플랫폼/모드/크론을 한 번에 설정하라. 완료 조건: `bash setup.sh` 실행 시 pull-only 여부와 크론 설정을 물어보고 자동 구성.

## 파일 변경 목록

| 파일 | 변경 내용 |
|------|----------|
| `setup.sh` | **신규** — 대화형 통합 셋업 스크립트 |
| `sync.sh` | pull-only 판단을 `is_pull_only` 함수로 통합 |
| `.gitignore` | `.pull-only` 추가 |
| `setup-mac.sh` | 유지 (OpenClaw 전용 복원, 기존 사용자 호환) |
| `setup-windows.sh` | 유지 (기존 사용자 호환) |

## 구현 순서

### 1. `sync.sh` — `is_pull_only` 함수 추가

대상: `sync.sh` L15 부근 (detect_platform 다음)

```bash
is_pull_only() {
  [ "$PLATFORM" = "windows" ] || [ -f "$SYNC_DIR/.pull-only" ]
}
```

L116, L136의 `[ "$PLATFORM" = "windows" ]`를 `is_pull_only`로 교체.

### 2. `.gitignore` — `.pull-only` 추가

파일 끝에 `.pull-only` 한 줄 추가.

### 3. `setup.sh` — 대화형 통합 셋업

플로우:

```
1. 플랫폼 자동 감지 (macos/linux/windows)
2. 질문: "동기화 모드를 선택하세요"
   - [1] 양방향 (기본) — 내 설정도 공유
   - [2] 수신 전용 (pull-only) — 다른 기기 설정만 받기
   → pull-only 선택 시 .pull-only 파일 생성
3. 질문: "자동 동기화(크론)를 설정할까요? (y/n)"
   → y: 플랫폼별 크론/Task Scheduler 등록 (30분)
   → n: 스킵 ("bash sync.sh로 수동 실행하세요" 안내)
4. Claude Code 설정 복원 (claude-code/ → ~/.claude/)
5. OpenClaw 워크스페이스가 있으면 복원 여부 질문
6. 첫 동기화 실행 (bash sync.sh)
```

## 함수/API 시그니처

```bash
# setup.sh
ask_sync_mode()    # → .pull-only 생성 여부 결정
ask_cron_setup()   # → 크론 등록 여부 결정
restore_claude()   # → claude-code/ → ~/.claude/ 복사
restore_openclaw() # → openclaw/ → ~/.openclaw/ 복사 (선택)

# sync.sh
is_pull_only() -> exit code 0 (true) or 1 (false)
```

## 제약 조건

- `read -p` 로 사용자 입력 받기 (비대화형 환경 대비 기본값 제공)
- 기존 `setup-mac.sh`, `setup-windows.sh`는 삭제하지 않는다 (호환)
- `.pull-only`는 gitignore 처리
- 크론 등록 시 기존 ai-config-sync 크론이 있으면 덮어쓰기 확인

## 의사결정

- 통합 `setup.sh` 채택 — 플랫폼별 스크립트 분리 대신 하나로 관리, 대화형으로 모드 선택
- 플랫폼별 스크립트 유지 — 기존 사용자 호환 + OpenClaw 전용 복원용
- `.pull-only` 마커 파일 방식 — hostname 기반 설정 파일 기각 (새 머신마다 커밋 필요)
