# AI Config Sync

Ubuntu ↔ MacBook ↔ Windows 간 OpenClaw + Claude Code 설정을 양방향 동기화하는 프로젝트.

## 프로젝트 구조

- `openclaw/` - OpenClaw 워크스페이스 및 설정 (Mac/Ubuntu만 사용)
- `claude-code/` - Claude Code 설정 (~/.claude/ 동기화, 전 플랫폼)
- `sync.sh` - 동기화 진입점 (bash, 전 플랫폼)
- `sync-timestamps.py` - 핵심 동기화 로직 (newest-wins 파일별 병합)
- `setup-mac.sh` - macOS/Ubuntu 초기 설정
- `setup-windows.sh` - Windows 초기 설정 (Claude Code만)
- `timestamps/` - 기기별 파일 타임스탬프 JSON
- `state/` - 기기별 환경 상태 기록

## 동기화 방식

- **newest-wins**: 파일 단위로 타임스탬프가 더 최신인 쪽이 우선
- `sync-timestamps.py`의 `sections` dict에서 section key와 repo 경로를 분리 관리 (tuple)
- `CLAUDE_INCLUDES` 화이트리스트로 claude-code 동기화 대상을 제한
- `TS_KEY_MIGRATIONS`로 과거 키 이름 자동 마이그레이션 지원
- 삭제 전파: local/peer/기존 timestamps/repo 파일을 합쳐 stale 파일 정리
- workspace에서 `tools/flutter`는 동기화 제외 (대용량/노이즈 방지)

## 플랫폼별 동기화 범위

| 플랫폼 | OpenClaw | Claude Code |
|---|---|---|
| macOS (개인) | O | O |
| Ubuntu (개인) | O | O |
| Windows (회사) | X (보안) | O (pull-only) |

- `~/.openclaw`이 없으면 OpenClaw 섹션은 자동 스킵됨
- Windows는 pull-only: 피어 설정을 수신만 하고 push하지 않음

## 코드 수정 시 주의사항

- `sync-timestamps.py` 수정 시: 모든 플랫폼에서 동작 확인 (pathlib 사용, `as_posix()`로 경로 통일, 인코딩은 반드시 `encoding="utf-8"` 명시)
- Windows CP949 주의: `read_text()`/`write_text()`/`subprocess(text=True)` 에 `encoding="utf-8"` 필수
- 새 동기화 대상 추가 시: `CLAUDE_INCLUDES` 또는 `sections` dict 수정
- 크론/Task Scheduler가 30분마다 `sync.sh`를 실행 중 — 스크립트 오류 시 동기화 중단됨
- `sync.sh` 마지막에 `git pull`이 있어 코드 변경이 다음 실행 시 자동 반영됨
- `sync.sh`는 `git add .`를 쓰지 않고 동기화 산출물 경로만 add함
- 민감값이 포함된 `openclaw/openclaw.json`은 추적 금지 (`openclaw.template.json`만 관리)
