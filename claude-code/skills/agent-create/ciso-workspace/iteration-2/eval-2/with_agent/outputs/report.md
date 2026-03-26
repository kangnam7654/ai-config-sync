## Security Posture Report

### Application Security Profile
- Application type: CLI (shell scripts + Python script for config file synchronization across devices)
- Tech stack: Bash, Python 3.10+, Git, pathlib, JSON (no database, no cache, no message queue)
- Authentication: none (relies on Git SSH key and `gh auth token` for GitHub access; no application-level auth)
- Deployment: Local machines (macOS, Ubuntu, Windows) via cron/Task Scheduler every 30 minutes; GitHub Actions CI for tests; no cloud hosting, not containerized, not serverless
- External services: 3 services (GitHub - send/receive via git push/pull, Notion API - send/receive via `cal_sync.py`, Google Calendar - send/receive via `gog` CLI)
- Existing security controls: `.gitignore` excludes `credentials/`, `auth-profiles.json`, `.env`, `openclaw/openclaw.json`; `CLAUDE_INCLUDES` whitelist limits claude-code sync scope; `EXCLUDES` dict blocks sensitive patterns; `validate_filepath()` prevents path traversal (`..`, null bytes, absolute paths); `validate_timestamp()` rejects negative and far-future values; `validate_hostname()` enforces RFC 952/1123; `umask 077` on generated `openclaw.json`; symlink removal in claude-code section

### Data Classification

| Data Field | Location | Sensitivity | Current Control | Required Control | Gap |
|---|---|---|---|---|---|
| 실명: "Kangnam Kim (김강남)" | `openclaw/workspace/USER.md:3` | CONFIDENTIAL (PII, PIPA Art. 2) | None -- committed to PUBLIC repo | Removal from public repo; if needed, store in local-only file excluded from sync | YES - CRITICAL |
| 이메일: `kangnam7653@gmail.com` | `openclaw/workspace/cal_sync.py:13`, `openclaw/workspace/notion_to_gcal_sync.sh:3,5`, `openclaw/workspace/memory/2026-02-23.md:13`, `openclaw/workspace/memory/2026-03-07.md:36` | CONFIDENTIAL (PII, PIPA Art. 2) | None -- committed to PUBLIC repo | Replace with environment variable; remove from memory files; purge from git history | YES - CRITICAL |
| Telegram ID: `REDACTED` | `openclaw/workspace/USER.md:8`, `openclaw/workspace/memory/2026-02-23.md:44` | CONFIDENTIAL (PII, PIPA Art. 2) | None -- committed to PUBLIC repo | Remove from synced files; store in local-only config | YES - CRITICAL |
| 제3자 실명 + 직함 + 휴대폰 번호: "REDACTED" | `openclaw/workspace/memory/2026-02-23.md:7` | CONFIDENTIAL - **THIRD-PARTY PII** (PIPA Art. 17, GDPR Art. 6) | None -- committed to PUBLIC repo | Immediate deletion from repo and git history | YES - CRITICAL |
| 연봉: "REDACTED" | `openclaw/workspace/memory/2026-02-23.md:8` | CONFIDENTIAL (sensitive personal financial data) | None -- committed to PUBLIC repo | Remove from synced files | YES - CRITICAL |
| 부서/직급: "미르5프로그램실 미르5서버팀, 전임 팀원" | `openclaw/workspace/memory/2026-02-23.md:8` | CONFIDENTIAL (employment PII) | None -- committed to PUBLIC repo | Remove from synced files | YES - CRITICAL |
| 입사처/입사일: "위메이드넥스트 2026-02-24" | `openclaw/workspace/memory/2026-02-23.md:5-6` | CONFIDENTIAL (employment PII) | None -- committed to PUBLIC repo | Remove from synced files | YES - CRITICAL |
| 자택 주소: "올림픽파크 포레온 1단지 104동 206호", "상도로 54길 54 이에스하임 12차 1동 401호" | `openclaw/workspace/notion_to_gcal_sync.sh:76,83` | RESTRICTED (precise residential address) | None -- committed to PUBLIC repo | Immediate deletion from repo and git history | YES - CRITICAL |
| 경력 이력 (회사명, 입사/퇴사일, 면접일): 크레버스, 메타버스월드, 아임클라우드 등 | `openclaw/workspace/notion_to_gcal_sync.sh:72-122` | CONFIDENTIAL (employment history) | None -- committed to PUBLIC repo | Remove or generalize | YES |
| GitHub token (runtime): `gh auth token` embedded in URL | `openclaw/workspace/sync-openclaw.sh:41-42` | RESTRICTED (credential) | Token fetched at runtime, not hardcoded; BUT URL pattern `https://user:${TOKEN}@github.com` leaks to shell history/process table/.git/config | Use SSH remote or git credential helper; never embed tokens in URLs | YES |
| Notion API key reference: `NOTION_API_KEY` env var | `openclaw/workspace/cal_sync.py:11` | RESTRICTED (API credential) | Loaded from environment variable (not hardcoded) | Meets requirement | NO |
| Notion DB ID: `b53115d0-3307-4f56-a76b-2ea22dae80a0` | `openclaw/workspace/cal_sync.py:12` | INTERNAL | Hardcoded in source | Move to environment variable (leaks internal resource identifier) | YES |
| Hostname / OS version | `state/*.md` | INTERNAL | Committed to repo | Acceptable for sync purpose | NO |
| Cron schedule / sync logs path | `state/*.md` | INTERNAL | Committed to repo | Acceptable | NO |
| 제3자 실명: "김재우 팀장님", "경식이형" | `openclaw/workspace/notion_to_gcal_sync.sh:104,95` | CONFIDENTIAL - **THIRD-PARTY PII** | None -- committed to PUBLIC repo | Remove names from synced files | YES |
| Agent/skill definitions, config files | `claude-code/agents/`, `claude-code/skills/`, `claude-code/settings.json` | INTERNAL | Whitelisted sync with CLAUDE_INCLUDES | Acceptable | NO |
| Timestamp JSON files | `timestamps/*.json` | PUBLIC | Committed to repo | Integrity protection adequate via git | NO |

### Compliance Matrix

| Framework | Requirement | Article | Status | Evidence |
|---|---|---|---|---|
| PIPA | 동의 수집 및 목적 명시 | Art. 15 | FAIL | 개인정보(실명, 이메일, Telegram ID, 제3자 성명+전화번호) 수집 및 공개 저장소 게시에 대한 동의 절차 부재. 프라이버시 정책 문서 없음. |
| PIPA | 목적 제한 | Art. 3 | FAIL | 설정 동기화 목적이나, `USER.md`의 실명/Telegram ID, `memory/` 내 연봉/부서 정보, `notion_to_gcal_sync.sh` 내 주소는 동기화에 불필요. 수집 목적 대비 과잉 수집. |
| PIPA | 목적 달성 후 파기 | Art. 21 | FAIL | 보유기간 정책 없음. `notion_to_gcal_sync.sh`의 2022년 이력 데이터가 영구 보존 중. 삭제 로직 부재. |
| PIPA | 주민등록번호 등 고유식별정보 암호화 | Art. 24 | UNVERIFIED | 주민등록번호는 발견되지 않음. 해당 항목 검증 불필요. |
| PIPA | 개인정보 처리방침 공개 | Art. 30 | FAIL | 개인정보 처리방침 문서 없음. |
| PIPA | 제3자 제공 시 동의 | Art. 17 | FAIL | 제3자 PII ("REDACTED", "김재우 팀장님")가 PUBLIC 저장소에 게시됨. 해당 제3자의 동의 없이 공개. **개인정보보호법 Art. 17 중대 위반.** |
| PIPA | 국외 이전 시 동의 | Art. 17 | FAIL | 개인정보가 GitHub(미국 서버)에 저장됨. 국외 이전에 대한 동의 절차 부재. |
| GDPR | Encryption of personal data | Art. 32(1)(a) | FAIL | PII가 PUBLIC GitHub 저장소에 평문으로 저장됨. Git transfer는 SSH(암호화)이나, 데이터 자체가 공개 접근 가능. 저장 시(at rest) 암호화 없음. |
| GDPR | Data minimization | Art. 5(1)(c) | FAIL | 설정 동기화에 불필요한 실명, Telegram ID, 연봉, 자택 주소, 경력 이력이 저장소에 포함됨. |
| GDPR | Right to erasure | Art. 17 | FAIL | 데이터 삭제 엔드포인트/프로세스 없음. git history에 영구 보존. |
| GDPR | Data processing records | Art. 30 | FAIL | 데이터 처리 기록 문서 없음. |
| GDPR | Breach notification process | Art. 33 | FAIL | Incident response plan 부재. |
| GDPR | Lawful basis documented | Art. 6 | FAIL | 처리 근거 문서 없음. |

### Threat Register

| ID | STRIDE | Threat | Likelihood | Impact | Risk Score | Current Control | Recommended Control |
|---|---|---|---|---|---|---|---|
| T-01 | Information Disclosure | PII (실명, 이메일, Telegram ID, 제3자 성명+전화번호, 연봉, 자택 주소)가 PUBLIC GitHub 저장소에 평문 노출 -- 전 세계 누구나 접근 가능 | 5 | 5 | 25 (CRITICAL) | None | 즉시 저장소를 PRIVATE으로 전환 + PII 포함 파일을 삭제 + `git filter-repo`로 git history에서 PII 제거 |
| T-02 | Information Disclosure | `sync-openclaw.sh`에서 `gh auth token`을 HTTPS URL에 삽입 -- 프로세스 테이블, shell history, `.git/config`에 GitHub 토큰 노출 가능 | 3 | 4 | 12 (HIGH) | Token은 런타임에 가져옴 (하드코딩 아님) | SSH remote (`git@github.com:...`) 사용 또는 `git credential helper` 사용. URL에 토큰 포함 금지. |
| T-03 | Tampering | `sync.sh`에서 `git reset --hard origin/main` (Windows pull-only 모드) -- 로컬 변경 무조건 덮어쓰기 | 2 | 3 | 6 (MEDIUM) | Windows pull-only 모드에만 적용 | 로컬 변경 감지 시 백업 생성 후 reset 수행. 또는 `git stash` 후 rebase. |
| T-04 | Spoofing | 피어 타임스탬프 조작으로 악의적 파일 내용 주입 -- 공격자가 GitHub repo에 push 권한 있으면 `timestamps/*.json`에 미래 타임스탬프를 삽입하여 피어 파일이 항상 "최신"으로 판정되도록 유도 | 2 | 4 | 8 (MEDIUM) | `validate_timestamp()`로 미래 24시간 이상 차단; `validate_filepath()`로 path traversal 차단 | GitHub branch protection rule 활성화 (main branch에 push 가능 계정 제한). 파일 내용 무결성 검증(해시) 추가. |
| T-05 | Repudiation | 자동 커밋 (`sync [$HOSTNAME]: 날짜`)에 상세 변경 로그 부재 -- 어떤 파일이 변경되었는지 추적 어려움 | 2 | 2 | 4 (LOW) | Git diff로 사후 확인 가능 | 커밋 메시지에 변경 파일 목록 포함. 또는 별도 sync log 파일 유지. |
| T-06 | Elevation of Privilege | `setup-mac.sh`에서 `openclaw.json`을 `umask 077`로 생성하나, 이후 `sync-openclaw.sh:33`에서 `cp` 명령으로 복사 시 권한이 기본값으로 리셋될 수 있음 | 2 | 3 | 6 (MEDIUM) | `umask 077` 적용 | `cp`후 `chmod 600` 명시적 적용. 또는 `install -m 600` 사용. |
| T-07 | Denial of Service | `sync.sh` 실패 시 30분마다 반복 실패 -- 로그가 `/tmp/ai-config-sync.log`에 무한 누적 가능 | 2 | 1 | 2 (LOW) | None | 로그 로테이션 적용 (`logrotate` 또는 스크립트 내 크기 제한). |
| T-08 | Information Disclosure | `state/*.md`에 hostname, OS 버전, cron 일정 노출 -- 공격 표면 정보 수집에 활용 가능 | 3 | 2 | 6 (MEDIUM) | None | 저장소를 PRIVATE으로 전환하면 완화됨 |

### Domain Scores

| Domain | Score | Key Finding |
|---|---|---|
| 1. Policy & Governance | 2/10 | 보안 정책, 개인정보 처리방침, incident response plan 모두 부재. README에 "보안 주의" 안내만 있으나 정식 정책 문서 아님. |
| 2. Data Protection | 0/10 | RESTRICTED/CONFIDENTIAL 데이터(실명, 이메일, 전화번호, 자택 주소, 연봉, 제3자 PII)가 PUBLIC GitHub 저장소에 평문으로 노출됨. 암호화 없음. 데이터 분류 없음. 보유기간 정책 없음. Git 이력에 영구 보존. |
| 3. Access Control | 3/10 | GitHub SSH key 기반 인증 존재. 그러나 저장소가 PUBLIC이므로 읽기 접근제어가 전무함. `sync-openclaw.sh`에 토큰-in-URL 패턴. 앱 레벨 인증/인가 없음. |
| 4. Threat & Vulnerability Mgmt | 3/10 | GitHub Actions CI로 자동 테스트 실행 (3 OS x 2 Python 버전). `validate_filepath()`/`validate_timestamp()` 검증 로직 존재. 그러나 정식 threat model 부재, dependency scanning 미설정, 보안 테스트 미포함. |
| 5. Incident Response Readiness | 0/10 | Incident response playbook 없음. 모니터링 없음. 연락 체계 없음. 침해 감지 수단 없음. |
| 6. Third-Party Risk | 2/10 | GitHub, Notion API, Google Calendar 사용. 어떤 서비스에 대해서도 보안 평가 미수행. DPA(Data Processing Agreement) 없음. Notion API key는 환경변수로 관리(양호). 데이터 흐름 문서 없음. |
| **Security Posture Score (SPS)** | **1.6/10** | |

SPS 계산: (2 x 0.15) + (0 x 0.20) + (3 x 0.20) + (3 x 0.20) + (0 x 0.10) + (2 x 0.15) = 0.30 + 0.00 + 0.60 + 0.60 + 0.00 + 0.30 = **1.80**

수정: (2 x 0.15) + (0 x 0.20) + (3 x 0.20) + (3 x 0.20) + (0 x 0.10) + (2 x 0.15) = 0.3 + 0.0 + 0.6 + 0.6 + 0.0 + 0.3 = **1.8/10**

### Verdict

**CRITICAL** (SPS 1.8 < 4.0): 보안 상태가 운영에 부적합합니다. 즉각적인 조치가 필요한 항목이 8개입니다.

가장 심각한 문제: **개인정보(실명, 이메일, 제3자 성명+전화번호, 자택 상세 주소, 연봉, 경력 이력)가 PUBLIC GitHub 저장소에 평문으로 노출**되어 있어, 개인정보보호법(PIPA) Art. 17 및 GDPR Art. 32(1)(a)를 중대하게 위반하고 있습니다. 특히 **제3자("현정화 과장")의 실명+전화번호가 동의 없이 공개**되어 있어 PIPA Art. 17(제3자 제공) 위반이 확정적입니다. 이 저장소는 전 세계 누구나 접근할 수 있는 상태입니다.

### Remediation Roadmap

| Priority | Finding | Risk Score | Remediation | Effort | Impact on Operations |
|---|---|---|---|---|---|
| 1 | T-01: PII가 PUBLIC 저장소에 노출 (실명, 이메일, 제3자 전화번호, 자택 주소, 연봉) | 25 (CRITICAL) | **즉시 실행 (24시간 이내)**: (1) `gh repo edit kangnam7654/ai-config-sync --visibility private` 로 저장소를 PRIVATE으로 전환. (2) PII 포함 파일(`openclaw/workspace/memory/2026-02-23.md`, `openclaw/workspace/USER.md`, `openclaw/workspace/notion_to_gcal_sync.sh`, `openclaw/workspace/memory/2026-03-07.md`, `openclaw/workspace/cal_sync.py`)에서 PII 제거. (3) `git filter-repo`로 git history에서 PII 완전 삭제. (4) GitHub Support에 캐시 삭제 요청. | 4시간 | 저장소 PRIVATE 전환 시 CI/CD, cron push/pull 영향 없음 (SSH key 인증 유지). 외부 공유 링크 차단됨. |
| 2 | PIPA Art. 17 위반: 제3자 PII ("REDACTED", "김재우 팀장님") 무단 공개 | 25 (CRITICAL) | `openclaw/workspace/memory/2026-02-23.md:7`에서 "REDACTED" 삭제. `notion_to_gcal_sync.sh:104`에서 "김재우 팀장님" 등 제3자 실명 제거. `git filter-repo`로 이력에서도 삭제. | 1시간 (Priority 1과 병행) | 없음 |
| 3 | PIPA Art. 3 / GDPR Art. 5(1)(c): 자택 상세 주소 공개 ("올림픽파크 포레온 1단지 104동 206호" 등) | 25 (CRITICAL) | `openclaw/workspace/notion_to_gcal_sync.sh:76,83`에서 상세 주소 삭제. `git filter-repo`로 이력에서도 삭제. | 30분 (Priority 1과 병행) | 없음 |
| 4 | T-02: `sync-openclaw.sh`에서 GitHub 토큰이 URL에 삽입 | 12 (HIGH) | `openclaw/workspace/sync-openclaw.sh:42`의 `REMOTE_URL` 패턴을 SSH (`git@github.com:kangnam7654/openclaw-config-sync.git`)로 변경. 또는 `git credential helper` 사용. | 30분 | 없음 |
| 5 | PIPA Art. 30 / GDPR Art. 30: 개인정보 처리방침 부재 | - | 개인정보 처리방침 문서 작성: 수집 항목(hostname, OS 버전), 수집 목적(설정 동기화), 보유기간, 파기 절차 명시. 저장소 README 또는 별도 `PRIVACY.md`에 게시. | 2시간 | 없음 |
| 6 | PIPA Art. 3 / GDPR Art. 5(1)(c): 동기화에 불필요한 PII 과잉 수집 | - | `USER.md`에서 실명, Telegram ID 제거 (동기화에 불필요). `cal_sync.py`의 이메일(`kangnam7653@gmail.com`)과 Notion DB ID를 환경변수(`CALENDAR_ID`, `NOTION_DB`)로 대체. `memory/*.md`를 동기화 제외 대상에 추가 (EXCLUDES에 `memory` 패턴 추가하거나 CLAUDE_INCLUDES에서 제외). | 2시간 | `cal_sync.py` 실행 시 환경변수 설정 필요. memory 파일의 cross-device 동기화 중단. |
| 7 | Domain 1: 보안 정책 부재 | - | 최소한의 보안 정책 문서 작성: (1) 동기화 대상 데이터 분류 기준, (2) PII 취급 금지 규칙, (3) 민감 파일 `.gitignore` 기준. `docs/security-policy.md`에 저장. | 2시간 | 없음 |
| 8 | Domain 5: Incident response 부재 | - | 경량 IR 플레이북 작성: (1) PII 유출 감지 시 저장소 PRIVATE 전환, (2) `git filter-repo`로 이력 삭제, (3) 영향받는 개인에게 통지. `docs/incident-response.md`에 저장. | 2시간 | 없음 |
| 9 | T-04: 피어 타임스탬프 조작 위험 | 8 (MEDIUM) | GitHub main branch protection rule 활성화: require pull request, restrict push to owner only. | 30분 | 자동 push 방식 변경 필요 (direct push -> PR 기반 또는 bot account 사용). |
| 10 | T-03: Windows `git reset --hard` 데이터 손실 위험 | 6 (MEDIUM) | `sync.sh`의 Windows 경로에서 `git reset --hard` 전 `git stash`로 로컬 변경 백업. | 30분 | 없음 |
| 11 | T-08: `state/*.md`에 시스템 정보 노출 | 6 (MEDIUM) | Priority 1에서 저장소를 PRIVATE으로 전환하면 자동 완화. | 0시간 (Priority 1로 해결) | 없음 |
| 12 | T-06: `openclaw.json` 파일 권한 리셋 가능성 | 6 (MEDIUM) | `sync-openclaw.sh`에서 `cp` 후 `chmod 600 $CONFIG_FILE` 추가. | 15분 | 없음 |
| 13 | Domain 6: 제3자 서비스 보안 평가 미수행 | - | GitHub, Notion, Google Calendar의 보안 인증(SOC 2) 확인 및 기록. 해당 서비스별 DPA 존재 확인. | 3시간 | 없음 |
