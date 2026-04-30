# Claude Code Bootstrap

> 이 파일은 **얇은 부트스트랩**입니다. 상세 운영 규칙은 `~/wiki/Rules/`에 있습니다. 도구 불문(Claude Code / Codex / Gemini CLI) 공유 규칙이므로 wiki에서 관리합니다.

## Bootstrap (세션 첫 작업 전 필수)

1. `git -C ~/wiki pull --rebase` — wiki를 최신 상태로 (NEVER #10)
2. Read `~/wiki/Rules/MAP.md` — 라우팅 테이블 로드
3. 현재 작업에 매칭되는 Rule 파일을 Read로 로드 후 그 규칙을 따름

upstream 미설정이면 pull은 no-op. wiki 없는 새 기기는 아래 NEVER 룰만 적용되고 상세 규칙은 wiki 클론 후부터 적용.

## Priority Rules

충돌 시 우선순위 (높음 → 낮음):

1. **NEVER rules** (이 파일 내. 오버라이드는 명시적 사용자 확인 필요)
2. **Project `CLAUDE.md`** (프로젝트 루트 또는 하위 디렉토리)
3. **This global `CLAUDE.md`** (부트스트랩 + NEVER) / **`~/wiki/Rules/*.md`** (상세 규칙)
4. **Superpowers skills** (`superpowers:test-driven-development`, `superpowers:brainstorming`, `superpowers:writing-plans` 등)
5. **Default system prompt behavior**

## NEVER Rules

이 규칙들은 예외 없음. 위반 처리 방식:

- **암묵적 위반** — 사용자 요청이 명시 오버라이드 없이 규칙 위반(예: "git pull 해줘"): 안전 변형 자동 적용(`--rebase` 추가). 경고 불필요.
- **명시적 오버라이드** — 사용자가 명시적으로 우회 요청 ("이번엔 그냥 해", "`--no-verify` 써도 돼" 등): 아래 경고 출력 + 사용자 "yes" 확인 후에만 진행.

```
⚠️ Warning: Attempting to override NEVER rule #N: "{rule}". This may cause {specific risk}. Continue? (yes/no)
```

1. NEVER run `git pull` without `--rebase`. Use `git pull --rebase` (현재 브랜치 기본) 또는 `git pull --rebase <remote> <branch>` 명시 인자. `origin main` 하드코딩 금지 — 브랜치/리모트는 프로젝트 컨텍스트에 따라 다름.
2. NEVER `git push` without explicit user request. 모든 push 변형에 적용 (`--force`, `--force-with-lease`, amended-commit push 포함).
3. NEVER call system `python`/`python3` directly in personal projects — `uv run python` 사용. Third-party 프로젝트의 비-uv 도구(poetry/pipenv/conda/rye)는 해당 관례 따름.
4. NEVER install Python packages with `pip install` in personal projects — `uv add <pkg>` 또는 `uv pip install <pkg>` 사용. Third-party는 해당 도구 따름.
5. NEVER commit new feature code without tests. **예외**: documentation-only commits, 설정 파일 변경, 테스트-only commits, 인프라 스크립트(shell/Dockerfile/CI), 테스트 프레임워크 미설정 프로젝트(프로젝트 CLAUDE.md에 명시 필요).
6. NEVER use a non-Mermaid diagram format without explicit user approval (Mermaid 기본).
7. NEVER place diagram files (Mermaid `.mmd` 소스와 렌더 `.png`) outside `docs/`. 다른 이미지 자산(로고, 스크린샷, UI 리소스, 테스트 fixture)은 제약 없음.
8. NEVER use agent-browser when WebSearch/WebFetch suffices. 로그인 필요 페이지, 동적 SPA, 멀티스텝 상호작용 플로우 전용.
9. NEVER design workflows where subagents call other subagents. Main model만 orchestrate; subagent는 leaf node.
10. NEVER read or write `~/wiki/` (personal second-brain wiki) without having pulled in the current session. 첫 wiki 접근 시 `git -C ~/wiki pull --rebase` 1회 실행. Upstream 미설정이면 no-op이고 진행 가능. 기기 간 stale read와 merge conflict 방지.

## Rule Routing (상세 규칙은 wiki에 있음)

| 트리거 조건 | 파일 |
| :--- | :--- |
| Python 코드/실행/패키지 설치 | `~/wiki/Rules/Languages/Python.md` |
| Rust / TypeScript / Go 등 언어별 룰 | `~/wiki/Rules/Languages/MAP.md` |
| 새 기능, 큰 리팩터, 디자인 독 작성 | `~/wiki/Rules/DesignFirst.md` |
| Wiki 자체 읽기/쓰기 | `~/wiki/Rules/Wiki.md` |
| 테스트 작성/커버리지 | `~/wiki/Rules/Testing.md` |
| 리팩터링 | `~/wiki/Rules/Refactoring.md` |
| Auto memory (user/feedback/project/reference/temp) | `~/wiki/Rules/Memory.md` |
| 의미있는 commit(feat/fix/refactor), 트랙·기능 시작/완료 | `~/wiki/Rules/Kanban.md` |
| Subagent 선택, 에이전트 orchestration | `~/wiki/Rules/AgentOrchestration.md` |
| Mermaid/mmdc/agent-browser | `~/wiki/Rules/CliTools.md` |
| 멀티 프로세스 dev 환경, 셸 스크립트, 포트 컨벤션, env var 함정 | `~/wiki/Rules/LocalDev.md` |
| UI 디자인 (브랜드 스타일 요청) | `~/wiki/Rules/DesignSystems.md` |

## Tool-agnostic 설정

이 파일은 Codex(`~/.codex/AGENTS.md`)와 Gemini CLI(`~/.gemini/GEMINI.md`)에서도 동일 내용으로 사용됩니다. 심볼릭 링크로 단일화 가능:

```sh
ln -sf ~/.claude/CLAUDE.md ~/.codex/AGENTS.md
ln -sf ~/.claude/CLAUDE.md ~/.gemini/GEMINI.md
```

(각 도구가 심볼릭 링크를 따라가지 않으면 복사본 유지 + 수동 동기화)
