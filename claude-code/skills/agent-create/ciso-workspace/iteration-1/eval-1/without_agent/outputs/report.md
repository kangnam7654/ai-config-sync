# ai-config-sync 보안 평가 보고서

> 평가일: 2026-03-26
> 대상: `git@github.com:kangnam7654/ai-config-sync.git` (main 브랜치)
> 저장소 가시성: **PUBLIC**
> 평가자: Claude (자동 보안 평가)

---

## 종합 등급: C (주의 필요)

기본적인 보안 설계(민감값 분리, 경로 검증, 화이트리스트 동기화)는 갖춰져 있으나, 공개 저장소에 민감 정보가 노출되어 있고, 동시 실행 보호가 없으며, 셸 스크립트에서의 인젝션 벡터가 존재한다. 아래 CRITICAL 항목은 즉시 조치가 필요하다.

---

## 1. CRITICAL 발견 사항

### 1-1. 공개 저장소에 Google OAuth client_secret 노출

- **파일**: `claude-code/agent-memory/security-reviewer/project_kangnam_credentials.md`
- **상태**: 현재 HEAD에 존재하며, 공개 저장소에서 누구나 열람 가능
- **내용**: Google OAuth `client_secret` 2건이 평문으로 기록됨
  - `<REDACTED>` (Gemini provider)
  - `<REDACTED>` (Antigravity provider)
- **위험**: 이 시크릿은 다른 프로젝트(kangnam-client)의 것이지만, 공격자가 해당 OAuth 클라이언트를 사칭하여 사용자 대신 토큰 교환을 수행할 수 있다.
- **권장 조치**:
  1. 즉시 해당 파일을 삭제하고 커밋
  2. `git filter-branch` 또는 `git-filter-repo`로 git 이력에서도 제거
  3. Google Cloud Console에서 해당 client_secret 2건을 즉시 재발급/폐기
  4. 보안 감사 메모는 비공개 채널(Notion, 사내 문서)로 이동

### 1-2. 자동 동기화가 민감 에이전트 메모리를 공개 저장소에 Push

- **메커니즘**: `sync.sh`가 30분마다 `git add -A ... claude-code ...`를 실행하여 `claude-code/agent-memory/` 전체를 커밋
- **결과**: 보안 감사 결과, 다른 프로젝트의 감사 메모, 아키텍처 설계 문서 등이 모두 공개됨
- **노출된 민감 콘텐츠 예시**:
  - `project_kangnam_credentials.md` (OAuth 시크릿)
  - `project_dearant_audit_2026_03_25.md` (타 프로젝트 보안 감사)
  - `project_kangnam_full_audit_2026_03_25.md` (전체 감사 보고서)
  - `project_moneyprinter_prerelease_audit.md` (타 프로젝트 사전 공개 감사)
  - `multi-provider-oauth-architecture.md` (인증 아키텍처 상세)
- **권장 조치**:
  1. `agent-memory/security-reviewer/` 경로를 `.gitignore`에 추가하거나, `CLAUDE_INCLUDES`에서 `agent-memory`를 제외
  2. 또는 저장소를 **private**으로 전환

### 1-3. `skipDangerousModePermissionPrompt: true` 동기화

- **파일**: `claude-code/settings.json` (line 41)
- **의미**: Claude Code의 위험 모드 확인 프롬프트를 비활성화. 이 설정이 모든 기기에 동기화됨.
- **위험**: 파일시스템 쓰기, 셸 명령 실행 등 위험 작업에 대한 사용자 확인 절차가 생략된다. 특히 Windows(회사 기기)에도 동기화될 수 있다.
- **권장 조치**: 이 설정을 기기별 로컬 설정으로 분리하거나, `settings.json`에서 제거

---

## 2. HIGH 발견 사항

### 2-1. 동시 실행 보호 없음 (Race Condition)

- **문제**: `sync.sh`에 lockfile 메커니즘이 없다. 크론(30분)과 수동 실행이 동시에 발생하면 git 작업이 충돌할 수 있다.
- **영향**: 동시 `git commit`/`git push`로 인한 데이터 손실 또는 상태 불일치
- **권장 조치**: `flock` (Linux) 또는 lockfile 패턴으로 동시 실행 방지
  ```bash
  LOCKFILE="/tmp/ai-config-sync.lock"
  exec 200>"$LOCKFILE"
  flock -n 200 || { echo "Already running"; exit 0; }
  ```

### 2-2. hostname 기반 신뢰 모델의 약점

- **문제**: 피어 인증이 없다. `timestamps/{hostname}.json`을 조작하면 누구든 피어로 위장할 수 있다.
- **시나리오**: 저장소가 public이므로, 공격자가 fork한 뒤 악의적인 타임스탬프 파일과 설정 파일을 push하고, 원본 repo에 PR을 보내면 merge 시 피어 설정이 주입될 수 있다.
- **완화 요소**: `sync.sh`는 `origin main`만 fetch하므로 PR 자체는 직접 반영되지 않음. 단, main 브랜치에 직접 push 권한이 있는 협력자가 악의적이라면 위험.
- **권장 조치**: 저장소를 private으로 전환. 또는 allowed_peers 목록을 설정 파일로 관리.

### 2-3. `state/{hostname}.md`에 인프라 정보 노출

- **노출 정보**: OS 버전, 호스트명, 크론탭 전체 내용, 최근 작업 파일명 목록
- **위험**: 공격자가 대상 환경을 프로파일링하는 데 활용 가능 (OS 버전 기반 취약점 탐색, 파일 구조 파악)
- **권장 조치**: `crontab -l` 출력과 최근 파일 목록을 state에서 제거하거나, state 자체를 .gitignore에 추가

### 2-4. 로그 파일 경로의 디렉토리 트래버설 가능성

- **위치**: `setup.sh` line 68, `setup-windows.sh` line 38
- **문제**: 로그 출력 경로 `$HOME/.local/share/ai-config-sync/sync.log`에 `$HOME`이 사용됨. `$HOME`이 비정상적인 값일 경우 예상치 못한 경로에 기록될 수 있다.
- **실제 위험도**: 낮음 (공격자가 $HOME을 조작하려면 이미 셸 접근 필요)
- **권장 조치**: 로그 디렉토리 생성 시 `chmod 700` 적용 (setup.sh에는 있으나 setup-windows.sh에는 없음)

---

## 3. MEDIUM 발견 사항

### 3-1. `sync-timestamps.py`의 JSON 파싱 시 크기 제한 없음

- **문제**: `json.loads()`에 크기 제한이 없다. 공격자가 거대한 타임스탬프 JSON을 push하면 OOM을 유발할 수 있다.
- **영향**: 동기화 프로세스 중단 (DoS)
- **권장 조치**: JSON 파일 크기를 확인하고 임계값(예: 10MB) 초과 시 건너뛰기

### 3-2. `.gitignore` 불완전

- **현재 누락 항목**:
  - `claude-code/plugins/marketplaces/` 는 gitignore에 포함되어 있으나, 실제로 `claude-code/plugins/marketplaces/` 디렉토리가 추적되고 있음 (`.git` 하위 디렉토리 포함)
  - `claude-code/plugins/install-counts-cache.json` (plugin 사용 통계)
  - `claude-code/plugins/blocklist.json` (외부 서비스와의 동기화 메타데이터)
- **위험**: 불필요한 메타데이터 노출
- **권장 조치**: `.gitignore`에 추가하고 `CLAUDE_INCLUDES`에서 plugins 범위를 세분화

### 3-3. 셸 변수 인용 부재

- **위치**: `sync.sh` 곳곳, `setup-mac.sh`, `setup-windows.sh`
- **예시**: `$HOSTNAME` 변수가 따옴표 없이 사용됨 (line 130: `git commit -m "sync [$HOSTNAME]..."`)
- **위험**: 호스트명에 특수문자가 포함된 경우 셸 인젝션 가능 (실질적으로 `validate_hostname`이 Python 측에서 방어하지만 셸 스크립트 측은 무방비)
- **권장 조치**: 모든 변수를 큰따옴표로 감싸기

### 3-4. `setup-mac.sh`의 토큰 생성 경쟁 조건

- **위치**: `setup-mac.sh` lines 33-38
- **문제**: `$CONFIG_FILE.tmp` 중간 파일을 사용하지만, 동일 사용자의 다른 프로세스가 같은 `.tmp` 파일을 쓸 수 있다.
- **권장 조치**: `mktemp`를 사용하여 고유한 임시 파일 생성

### 3-5. Windows pull-only 모드의 `git reset --hard`

- **위치**: `sync.sh` line 153
- **문제**: `git reset --hard origin/main`은 추적 파일의 로컬 변경을 무조건 폐기한다. Windows에서 사용자가 수동으로 수정한 설정이 경고 없이 사라진다.
- **권장 조치**: reset 전 `git stash`를 실행하거나, 변경 있을 시 사용자에게 경고

---

## 4. LOW 발견 사항

### 4-1. `__pycache__/` 디렉토리가 프로젝트 루트에 존재

- `.gitignore`에 의해 추적되지 않지만, 파일 시스템에 잔존. `sync-timestamps.py` 직접 실행 시 생성됨.
- 보안 영향: 없음. 위생 문제.

### 4-2. `.coverage` 파일이 프로젝트 루트에 존재

- `.gitignore`에 의해 추적되지 않지만, 테스트 실행 시 잔존.
- 보안 영향: 없음.

### 4-3. 커밋 메시지에 호스트명 노출

- 모든 자동 커밋이 `sync [Kangnamui-MacBookPro]: 2026-03-26 14:30` 형식으로 호스트명을 포함.
- public repo에서 기기 식별 정보로 활용 가능.
- **권장 조치**: 호스트명 대신 해시나 익명 식별자 사용 검토

### 4-4. 이메일 주소 노출 (git author)

- git log에 `kangnam@192.168.nate.com`, `kangnam@Kangnamui-MacBookPro.local` 등 로컬 이메일이 노출됨.
- **권장 조치**: GitHub noreply 이메일 사용 (`kangnam7654@users.noreply.github.com`)

---

## 5. 긍정적 보안 설계 사항

다음 항목들은 보안 관점에서 올바르게 설계되어 있다.

| 항목 | 설명 |
|------|------|
| 민감 설정 분리 | `openclaw.json`은 `.gitignore`로 추적 금지, 템플릿만 관리 |
| 경로 트래버설 방어 | `validate_filepath()`에서 `..`, 절대경로, null byte 차단 |
| 타임스탬프 검증 | `validate_timestamp()`에서 음수, 비숫자, 24시간 초과 미래값 거부 |
| 호스트명 검증 | `validate_hostname()`에서 RFC 952/1123 준수 검증 |
| 화이트리스트 동기화 | `CLAUDE_INCLUDES`로 claude-code 동기화 대상을 명시적으로 제한 |
| 섹션별 제외 패턴 | `EXCLUDES` dict로 민감 파일 패턴 제외 |
| 심볼릭 링크 제거 | claude-code 섹션에서 symlink를 명시적으로 삭제 (심링크 공격 방어) |
| 토큰 생성 시 umask | `setup-mac.sh`/`setup.sh`에서 `umask 077`로 설정 파일 생성 |
| 게이트웨이 loopback 바인딩 | 템플릿에서 `"bind": "loopback"`으로 외부 접근 차단 |
| 위험 명령 차단 | `denyCommands` 목록으로 camera/calendar/contacts 명령 차단 |
| CI 테스트 | GitHub Actions에서 3 OS x 2 Python 버전으로 테스트 + 80% 커버리지 요구 |
| 피어 JSON 구조 검증 | `load_peer_timestamps()`에서 known sections만 허용, 파일명 정규식 검증 |

---

## 6. 즉시 조치 권장 사항 (우선순위 순)

| 순위 | 심각도 | 조치 내용 | 예상 소요 |
|------|--------|----------|----------|
| 1 | CRITICAL | `project_kangnam_credentials.md` 삭제 + git 이력 정리 + Google OAuth secret 재발급 | 30분 |
| 2 | CRITICAL | 저장소를 private으로 전환하거나, `agent-memory/security-reviewer/`를 동기화 대상에서 제외 | 5분 |
| 3 | CRITICAL | `settings.json`에서 `skipDangerousModePermissionPrompt` 제거 또는 기기별 분리 | 5분 |
| 4 | HIGH | `sync.sh`에 lockfile 추가 (동시 실행 방지) | 15분 |
| 5 | HIGH | `state/` 파일에서 crontab 내용과 파일 목록 제거 | 10분 |
| 6 | MEDIUM | `.gitignore` 보완 (plugins 메타데이터, agent-memory 민감 경로) | 10분 |
| 7 | MEDIUM | 셸 변수 인용 처리 전면 점검 | 20분 |
| 8 | LOW | git author 이메일을 noreply로 변경 | 5분 |

---

## 7. 장기 개선 권장 사항

1. **저장소 가시성 재검토**: 개인 설정 동기화 저장소는 private이 적합하다. 공개할 기술적 이유가 없다면 private 전환을 권장한다.
2. **시크릿 스캐닝 활성화**: GitHub의 secret scanning 기능을 활성화하여 향후 시크릿 커밋을 자동 감지하라.
3. **pre-commit hook**: `pre-commit` 프레임워크로 시크릿 패턴 (`GOCSPX-`, `sk-ant-`, `ghp_` 등)을 커밋 전에 차단하라.
4. **CLAUDE_INCLUDES 세분화**: `agent-memory`, `memory` 전체를 동기화하는 대신, 비민감 하위 경로만 선택적으로 포함하라.
5. **동기화 대상 감사 자동화**: CI에서 `git diff --cached`를 분석하여 민감 파일 패턴이 포함된 커밋을 차단하는 GitHub Actions workflow를 추가하라.
