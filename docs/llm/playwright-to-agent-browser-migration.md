# Playwright → agent-browser 마이그레이션 설계문서

## 목적

simulator 에이전트, webapp-testing 스킬, ui-review 스킬에서 ad-hoc 브라우저 조작에 사용하는 Playwright를 agent-browser CLI로 교체하라. 완료 조건: 교체 대상 파일에서 Playwright 참조가 모두 agent-browser로 대체되고, 교체하지 않는 파일(qa-engineer E2E, cto tech-stack 등)에는 영향이 없다.

## 교체 범위 판단 기준

| 용도 | 교체 여부 | 이유 |
|---|---|---|
| ad-hoc 브라우저 조작 (스크린샷, 클릭, 폼 입력 등) | **교체** | 임시 스크립트 작성 → CLI 한 줄 명령으로 토큰 효율 향상 |
| E2E 테스트 프레임워크 (`npx playwright test`, `.spec.ts`) | **유지** | CI용 재사용 테스트 스위트는 agent-browser가 대체 불가 |
| Agent SDK의 MCP 서버 설정 예시 | **유지** | `@playwright/mcp`는 별도 MCP 서버 — agent-browser와 무관 |
| eval 산출물 (과거 생성된 파일) | **유지** | 과거 평가 결과는 히스토리이므로 수정 불필요 |
| agent-memory 기록 | **유지** | 과거 관찰 기록이므로 수정 불필요 |
| plugins 캐시 | **유지** | 자동 생성 캐시 |

## 파일 변경 목록

### 교체 대상 (12개 파일)

| # | 파일 경로 | 변경 유형 | 변경 내용 요약 |
|---|---|---|---|
| 1 | `claude-code/agents/simulator.md` | 수정 | description + 본문에서 "Playwright" → "agent-browser" 교체 (참조 경로, 스코프 설명, 워크플로우) |
| 2 | `claude-code/agents/simulator/references/web-verification.md` | 전면 재작성 | Playwright JS 스크립트 패턴 → agent-browser CLI 명령 패턴으로 전환 |
| 3 | `claude-code/skills/webapp-testing/SKILL.md` | 전면 재작성 | Python Playwright 패턴 → agent-browser CLI 워크플로우로 전환 |
| 4 | `claude-code/skills/webapp-testing/examples/static_html_automation.py` | 삭제 후 .sh 생성 | Python Playwright → shell script (agent-browser CLI) |
| 5 | `claude-code/skills/webapp-testing/examples/element_discovery.py` | 삭제 후 .sh 생성 | Python Playwright → shell script (agent-browser CLI) |
| 6 | `claude-code/skills/webapp-testing/examples/console_logging.py` | 삭제 후 .sh 생성 | Python Playwright → shell script (agent-browser CLI) |
| 7 | `claude-code/skills/ui-review/SKILL.md` | 수정 | `npx playwright screenshot` → `agent-browser screenshot` (2곳) + edge case 메시지 변경 |
| 8 | `claude-code/skills/simulator-workspace/evals.json` | 수정 | eval 기준에서 "Playwright" → "agent-browser" 교체 |
| 9 | `openclaw/workspace/skills/webapp-testing/SKILL.md` | 전면 재작성 | claude-code 버전과 동일하게 교체 |
| 10 | `openclaw/workspace/skills/webapp-testing/examples/static_html_automation.py` | 삭제 후 .sh 생성 | claude-code 버전과 동일 |
| 11 | `openclaw/workspace/skills/webapp-testing/examples/element_discovery.py` | 삭제 후 .sh 생성 | claude-code 버전과 동일 |
| 12 | `openclaw/workspace/skills/webapp-testing/examples/console_logging.py` | 삭제 후 .sh 생성 | claude-code 버전과 동일 |

### 추가 교체 대상 (openclaw 구버전)

| # | 파일 경로 | 변경 유형 | 변경 내용 요약 |
|---|---|---|---|
| 13 | `openclaw/workspace/skills/frontend-review/SKILL.md` | 수정 | `npx playwright screenshot` → `agent-browser screenshot` (ui-review의 구버전) |

### 교체하지 않는 파일 (확인 완료)

| 파일 | 유지 이유 |
|---|---|
| `claude-code/agents/qa-engineer.md` | E2E 테스트 프레임워크로서 Playwright 사용 |
| `claude-code/agents/qa-engineer/references/e2e-playwright.md` | E2E 테스트 패턴 레퍼런스 |
| `claude-code/agents/cto/refs/tech-stack-guide.md` | E2E 테스트 도구 매핑 (CI용) |
| `claude-code/agents/cto.md` | tech-stack-guide 참조만 |
| `openclaw/workspace/agents/e2e-runner.md` | E2E 전용 에이전트 |
| `claude-code/skills/agent-create/qa-engineer-workspace/**` | 과거 eval 산출물 (히스토리) |
| `claude-code/agent-memory/qa-engineer/**` | 과거 관찰 기록 |
| `claude-code/skills/claude-api/**/patterns.md` | Agent SDK MCP 설정 예시 (`@playwright/mcp`) |
| `claude-code/skills/claude-api/**/README.md` | 동일 |
| `claude-code/skills/web-artifacts-builder/SKILL.md` | 간접 참조만 ("Playwright or Puppeteer") |
| `claude-code/plugins/install-counts-cache.json` | 자동 생성 캐시 |
| `claude-code/skills/simulator-workspace/iteration-*/**` | 과거 eval 결과 (히스토리) |
| `openclaw/workspace/agents/tdd-guide.md` | TDD 가이드 (E2E 문맥) |
| `openclaw/workspace/skills/claude-api/**` | claude-code 버전과 동일 (MCP 설정) |
| `openclaw/workspace/skills/web-artifacts-builder/SKILL.md` | 간접 참조만 |

## 구현 순서

### 1단계: simulator 에이전트 (2파일)

1-1. `claude-code/agents/simulator.md` 수정
  - description 문자열에서 "via Playwright browser automation" → "via agent-browser CLI"
  - Line 11: "run web apps in browsers via Playwright" → "run web apps in browsers via agent-browser"
  - Line 19: reference 파일 설명 유지 (파일명은 동일)
  - Line 29-36: IN scope 설명에서 "via Playwright" → "via agent-browser"
  - Line 72: 의존성 체크 `npx playwright --version` → `agent-browser --version`
  - Line 99-103: 웹 환경 체크 명령 → `agent-browser --version`
  - Line 118-122: 환경 준비 명령 → `agent-browser install` (Chromium 설치)
  - Line 138: 임시 Playwright 스크립트 언급 → agent-browser CLI 명령으로 대체
  - Line 153-154: 웹 액션 설명 → agent-browser CLI 참조로 변경
  - Line 210-211: Playwright 미설치 edge case → agent-browser 미설치로 변경
  - Line 217: Playwright script throws error → agent-browser 명령 실패로 변경

1-2. `claude-code/agents/simulator/references/web-verification.md` 전면 재작성
  - 기존: Playwright Node.js 스크립트 패턴 (270줄)
  - 신규: agent-browser CLI 명령 레퍼런스
  - 섹션 구성: 설치/확인, 기본 네비게이션, 요소 조작, 정보 추출, 스크린샷, 대기, 인증, 반응형 테스트, 네트워크 모니터링, 셀렉터 우선순위

### 2단계: webapp-testing 스킬 (4파일)

2-1. `claude-code/skills/webapp-testing/SKILL.md` 전면 재작성
  - description: "using Playwright" → "using agent-browser"
  - 핵심 패턴: Python `sync_playwright()` → `agent-browser` CLI 명령
  - Decision Tree: Playwright 스크립트 작성 → agent-browser 명령 실행
  - `with_server.py` helper 연동 방식 유지 (서버 관리 후 agent-browser 명령 실행)
  - Edge Cases: Playwright 설치 → agent-browser 설치로 변경
  - Best Practices: Playwright 패턴 → agent-browser 패턴

2-2~2-4. examples/ 디렉토리 파일 교체
  - `static_html_automation.py` → `static_html_automation.sh`
  - `element_discovery.py` → `element_discovery.sh`
  - `console_logging.py` → `console_logging.sh`
  - 각 파일에 동일 기능의 agent-browser CLI 명령 시퀀스 작성

### 3단계: ui-review 스킬 (1파일)

3-1. `claude-code/skills/ui-review/SKILL.md` 수정
  - Line 39: `npx playwright screenshot --full-page {url} /tmp/ui-review-$(date +%s).png` → `agent-browser open {url} && agent-browser screenshot --full /tmp/ui-review-$(date +%s).png && agent-browser close`
  - Line 40: localhost 버전도 동일하게 변경
  - Line 209 (edge case): "Playwright가 설치되어 있지 않습니다. `npx playwright install chromium`을 실행하세요." → "agent-browser가 설치되어 있지 않습니다. `npm install -g agent-browser && agent-browser install`을 실행하세요."

### 4단계: simulator-workspace evals (1파일)

4-1. `claude-code/skills/simulator-workspace/evals.json` 수정
  - "Playwright dependency checked" → "agent-browser dependency checked"
  - "npx playwright --version" → "agent-browser --version"
  - "writes a Playwright script" → "runs agent-browser commands"

### 5단계: openclaw 동기화 대상 (5파일)

5-1~5-4. `openclaw/workspace/skills/webapp-testing/` — claude-code 버전과 동일한 내용으로 교체
5-5. `openclaw/workspace/skills/frontend-review/SKILL.md` — ui-review와 동일하게 playwright screenshot → agent-browser screenshot 교체

## 명령어 매핑 테이블

| Playwright 패턴 | agent-browser 대체 |
|---|---|
| `npx playwright --version` | `agent-browser --version` |
| `npx playwright install chromium --with-deps` | `agent-browser install` |
| `npx playwright screenshot --full-page {url} {path}` | `agent-browser open {url} && agent-browser screenshot --full {path}` |
| JS: `await page.goto(url)` | `agent-browser open {url}` |
| JS: `await page.screenshot({path, fullPage: true})` | `agent-browser screenshot --full {path}` |
| JS: `await page.screenshot({path})` | `agent-browser screenshot {path}` |
| JS: `await page.click(selector)` | `agent-browser click {ref}` (snapshot으로 ref 확인 후) |
| JS: `await page.fill(selector, text)` | `agent-browser fill {ref} "{text}"` |
| JS: `await page.textContent(selector)` | `agent-browser get text {ref}` |
| JS: `await page.isVisible(selector)` | `agent-browser snapshot -i` (요소 존재 확인) |
| JS: `await page.waitForSelector(sel)` | `agent-browser wait {ref}` |
| JS: `await page.waitForURL(pattern)` | `agent-browser wait --url "{pattern}"` |
| JS: `await page.waitForLoadState('networkidle')` | `agent-browser wait --load networkidle` |
| JS: `await page.setViewportSize({w, h})` | `agent-browser open {url}` 시 `--viewport {w}x{h}` 옵션 |
| JS: `await browser.close()` | `agent-browser close` |
| Python: `from playwright.sync_api import sync_playwright` | (불필요 — CLI 직접 호출) |
| Python: `p.chromium.launch(headless=True)` | (불필요 — agent-browser 기본 헤드리스) |

## agent-browser 핵심 워크플로우 패턴

기존 Playwright 방식은 "스크립트 작성 → 실행 → 결과 확인" 3단계였으나, agent-browser는 "명령 실행 → 결과 확인" 2단계다.

```bash
# 1. 페이지 열기
agent-browser open http://localhost:3000

# 2. 접근성 트리 확인 (요소 ref 획득)
agent-browser snapshot -i          # 인터랙티브 요소만
# 출력: @e1 button "Login", @e2 input "Email", @e3 input "Password", ...

# 3. 요소 조작
agent-browser fill @e2 "test@example.com"
agent-browser fill @e3 "password123"
agent-browser click @e1

# 4. 결과 확인
agent-browser wait --url "**/dashboard"
agent-browser screenshot /tmp/simulator-screenshots/dashboard.png

# 5. 종료
agent-browser close
```

## 제약 조건

1. `agent-browser` 명령어는 v0.22+ 기준으로 작성하라. CLAUDE.md의 v0.10.0 기재는 구버전이므로 최신 명령어를 사용한다.
2. 셀렉터 → ref 전환: Playwright의 CSS 셀렉터(`[data-testid="..."]`, `button:has-text("...")`) 대신 agent-browser의 `snapshot`으로 획득한 ref(`@e1`, `@e2`)를 사용한다. 시맨틱 로케이터(`agent-browser find role button --name "Submit"`)도 사용 가능하다.
3. qa-engineer, e2e-runner, cto 파일은 절대 수정하지 마라.
4. eval 산출물(`iteration-*/eval-*/outputs/`)은 과거 히스토리이므로 수정하지 마라.
5. agent-memory 파일은 수정하지 마라.
6. openclaw 파일은 claude-code 파일과 정확히 동일한 내용으로 동기화하라.

## 의사결정

- **채택**: ad-hoc 브라우저 조작만 agent-browser로 교체, E2E 테스트 프레임워크는 Playwright 유지
- **기각**: 전체 Playwright 참조를 agent-browser로 교체 — agent-browser는 테스트 프레임워크가 아니므로 CI용 `.spec.ts` 테스트 스위트를 대체할 수 없음
