## Session Start Protocol

- 세션 시작 시 `git status` + `git pull` 없이 작업을 시작하지 마라
- remote가 없는 프로젝트에서 push를 시도하지 마라 — 먼저 사용자에게 GitHub repo 연결을 요청
- push 실패 시 HTTPS remote를 그대로 두지 마라 — `git@github.com:` 형식으로 변환 후 재시도

## Agent Orchestration

서브에이전트는 다른 서브에이전트를 직접 호출할 수 없다. 메인 모델이 오케스트레이터로서 아래 루프를 실행한다.

### Writer → Critic 루프
문서 작성 요청 시 반드시 다음 순서를 따르라:
1. **doc-writer** (사람용) 또는 **prompt-writer** (LLM용) 호출 → 초안 수령
2. **doc-critic** 호출 (사람용 → HUMAN 모드, LLM용 → LLM 모드) → 채점 결과 수령
3. REJECT이면 → critic의 피드백을 writer에게 전달하여 수정 요청 → 2번으로 복귀
4. PASS이면 → 최종 결과를 사용자에게 전달

### Planner → Critic 루프
플랜 수립 요청 시 반드시 다음 순서를 따르라:
1. **planner** 호출 → 플랜 초안 수령
2. **plan-critic** 호출 → 채점 결과 수령
3. REJECT이면 → critic의 피드백을 planner에게 전달하여 수정 요청 → 2번으로 복귀
4. PASS이면 → 최종 플랜을 사용자에게 전달

### 공통 규칙
- 최대 반복 횟수: **5회**. 5회 REJECT 시 현재 상태와 미해결 이슈를 사용자에게 보고하고 판단을 요청하라
- Writer/Planner 에이전트 내부에 critic 호출 지시가 있더라도 무시하라 — 오케스트레이션은 메인 모델만 수행한다
- Critic 결과는 사용자에게 매 라운드 요약 보고하라 (점수 + PASS/REJECT + 피드백 요약 1줄)

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

## Refactoring

- 과도한 추상화나 과도한 최적화로 인간이 읽고 수정할 수 없는 코드를 만들지 마라 — 가독성을 최우선으로 유지
- 동작 보존을 검증할 테스트 없이 리팩터링을 시작하지 마라
- 리팩터링 전에 커밋 없이 코드를 변경하지 마라 — 언제든 이전 상태로 복구 가능해야 한다
- 계획 없이 리팩터링을 진행하지 마라
- 리팩터링 후 테스트를 실행하지 않고 넘어가지 마라 — 동작이 동일함을 반드시 확인

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
