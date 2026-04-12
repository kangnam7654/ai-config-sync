# Paperclip Company Sync

## Purpose

Paperclip company 데이터(agents, skills)를 Mac mini ↔ MacBook 간 자동 동기화.
완료 기준: `sync.sh` 실행 시 paperclip company export/import가 자동으로 수행되어 양쪽 머신의 agent/skill 설정이 동일해진다.

## File changes

| File | Change |
|---|---|
| `sync.sh` | paperclip export/import 단계 추가, git add 경로에 `paperclip` 추가 |
| `sync-timestamps.py` | `walk_files`에 `followlinks=True` 추가 (symlink skill sync 해결) |
| `CLAUDE.md` | paperclip sync 관련 설명 추가 |

## Implementation order

1. `sync-timestamps.py`: `walk_files` 함수의 `os.walk`에 `followlinks=True` 추가
2. `sync.sh`: `paperclip_export` 함수 추가 — sync-timestamps.py 실행 후, git add 전에 호출
3. `sync.sh`: `paperclip_import` 함수 추가 — git pull 후에 호출
4. `sync.sh`: git add 경로에 `paperclip` 추가
5. `CLAUDE.md`: architecture 섹션에 paperclip sync 설명 추가

## Function/API signatures

### sync.sh

```bash
paperclip_export() -> void
# - `paperclipai company list --json`으로 active company ID 자동 감지
# - `paperclipai company export <id> --include company,agents,skills --expand-referenced-skills --out ./paperclip/company`
# - paperclipai CLI 미설치 시 skip (경고 출력)
# - Paperclip 미실행 시 skip (경고 출력)

paperclip_import() -> void
# - `./paperclip/company` 디렉토리 존재 확인
# - `paperclipai company import ./paperclip/company --target existing --collision replace --yes`
# - active company가 없으면 `--target new`로 생성
# - paperclipai CLI 미설치 시 skip
```

### sync-timestamps.py

```python
def walk_files(base: Path, section: str) -> dict[str, float]:
    # 기존과 동일하되 os.walk(base, followlinks=True)로 변경
```

## Constraints

- paperclipai CLI가 없는 환경(Windows 등)에서는 graceful skip
- Paperclip 서버가 꺼져있을 때도 graceful skip (export/import 실패 시 non-fatal)
- export 실패가 전체 sync를 중단하면 안 됨 (`set -e` 주의 → 개별 에러 핸들링)
- company ID 하드코딩 금지 — `company list --json`으로 동적 감지
- pull-only 모드에서는 import만 수행 (export skip)

## Decisions

- **CLI export/import 사용** — DB 직접 접근이나 API 호출 대비 공식 지원 도구이므로 안정적
- **timestamp 기반 sync 미적용** — company 데이터는 단일 단위로 export/import되므로 파일별 newest-wins 부적합. 대신 "마지막으로 export한 쪽이 우선" 방식
- **`followlinks=True`로 symlink 해결** — symlink를 resolve하여 복사하는 별도 로직 대비 단순함. 순환 symlink 위험은 `~/.claude/` 구조상 무시 가능
