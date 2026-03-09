## Session Start Protocol

- 세션 시작 시 `git status` + `git pull` 없이 작업을 시작하지 마라
- remote가 없는 프로젝트에서 push를 시도하지 마라 — 먼저 사용자에게 GitHub repo 연결을 요청
- push 실패 시 HTTPS remote를 그대로 두지 마라 — `git@github.com:` 형식으로 변환 후 재시도

## Design-First Development

- 설계문서 없이 구현 코드를 작성하지 마라
- 설계문서를 `{project}/docs/{feature-or-topic}/` 외의 위치에 두지 마라
- 목적, 아키텍처, 데이터 흐름, API 설계, 파일 구조, 의사결정 근거를 빠뜨리지 마라
- DB가 필요한 프로젝트에서 DB 스키마 설계를 나중으로 미루지 마라 — 가장 먼저 수행 (ERD, 테이블, 관계, 인덱스)
- 사용자 확인 없이 설계에서 구현으로 넘어가지 마라
- 다이어그램을 Mermaid(`.mmd`) 외의 형식으로 작성하지 마라
  - `mmdc -i input.mmd -o output.png -b transparent -s 4` (4x 고해상도)
  - `.mmd` 원본과 `.png` 결과를 `docs/` 밖에 두지 마라
  - Markdown 문서에서는 `![설명](./diagram.png)` 로 참조

## Testing

- 코드 변경 후 테스트를 건너뛰지 마라 — `uv run python -m pytest tests/ -q`로 전체 통과 확인
- 커버리지 80% 미만인 상태로 두지 마라 — `uv run python -m pytest --cov --cov-fail-under=80`
- 새 기능/모듈을 테스트 없이 추가하지 마라 — Unit + 통합 테스트 함께 작성
- Unit 테스트에서 외부 의존성을 Mock 없이 호출하지 마라
- 통합 테스트에서 모듈 간 호출을 Mock하지 마라 — 외부 I/O(API, 파일시스템, DB)만 Mock

## Development Environment

### Python
- 시스템 python을 직접 호출하지 마라 — 반드시 `uv run python` 사용
  - 예: `uv run python -m pytest`, `uv run python script.py`
- 패키지를 pip으로 직접 설치하지 마라 — `uv add <pkg>` 또는 `uv pip install <pkg>` 사용

### CLI Tools
- **mmdc** (mermaid-cli): Mermaid 다이어그램 → PNG 렌더링
- **agent-browser** (v0.10.0): 로그인/동적 SPA/브라우저 조작이 필요한 경우에만 사용
  - 일반 검색/페이지 읽기에 agent-browser를 쓰지 마라 — WebSearch/WebFetch가 더 빠르다
  - 명령어: `agent-browser open <url>`, `snapshot`, `screenshot`, `click`, `fill`, `text`, `close`
