## Session Start Protocol

세션 시작 시 반드시 수행:
1. **Git repo 동기화**: 작업 대상 프로젝트(들)에서 `git status` + `git pull`로 최신 상태 확인
2. **Remote 연결 확인**: remote가 없으면 사용자에게 GitHub repo 연결을 요청
3. **SSH remote 선호**: push 실패 시 `git@github.com:` 형식으로 변환 후 재시도

## Design-First Development

구현 전에 반드시 설계문서를 먼저 작성:
1. **위치**: `{project}/docs/{feature-or-topic}/` 디렉토리에 생성
2. **내용**: 목적, 아키텍처, 데이터 흐름, API 설계, 파일 구조, 의사결정 근거 등을 최대한 자세히 기술
3. **순서**: 설계문서 작성 → 사용자 확인 → 설계에 맞춰 구현
4. **DB 우선**: DB가 필요한 프로젝트는 DB 스키마 설계를 가장 먼저 수행 (ERD, 테이블 정의, 관계, 인덱스 등)
4. **형식**: Markdown 기본. 필요 시 다이어그램, 테이블 등 활용
5. **다이어그램**: 아키텍처, 시퀀스, ERD 등은 Mermaid로 작성 후 이미지로 렌더링하여 보관
   - `.mmd` 파일 작성 → `mmdc -i input.mmd -o output.png -b transparent` 로 PNG 생성
   - `.mmd` 원본과 `.png` 렌더링 결과 모두 `docs/` 안에 보관
   - Markdown 문서에서는 `![설명](./diagram.png)` 로 참조

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
