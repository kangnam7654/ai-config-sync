## Session Start Protocol

세션 시작 시 반드시 수행:
1. **Git repo 동기화**: 작업 대상 프로젝트(들)에서 `git status` + `git pull`로 최신 상태 확인
2. **Remote 연결 확인**: remote가 없으면 사용자에게 GitHub repo 연결을 요청
3. **SSH remote 선호**: push 실패 시 `git@github.com:` 형식으로 변환 후 재시도

## Python 실행

- Python 실행 시 반드시 `uv run python` 사용 (시스템 python 직접 호출 금지)
- 예: `uv run python -m pytest`, `uv run python script.py`
- 패키지 설치: `uv add <pkg>` 또는 `uv pip install <pkg>`

## User Tools

- **agent-browser** (v0.10.0) 전역 설치됨
  - 용도: 로그인 필요한 사이트, 동적 SPA 페이지, 브라우저 조작(클릭/폼입력) 필요 시 사용
  - 일반 검색/페이지 읽기는 WebSearch/WebFetch 우선 사용 (더 빠름)
  - agent-browser는 브라우저 조작이 꼭 필요한 경우에만 사용할 것
  - 명령어: `agent-browser open <url>`, `snapshot`, `screenshot`, `click`, `fill`, `text`, `close`
