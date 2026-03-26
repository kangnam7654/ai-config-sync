## Security Posture Report

### Application Security Profile
- Application type: CLI (shell script + Python script for cross-device config synchronization)
- Tech stack: Python 3.10+, Bash, Git (no database, no cache, no message queue)
- Authentication: Git SSH key / HTTPS token (GitHub repository access only, no application-level auth)
- Deployment: Self-hosted on personal devices (macOS, Ubuntu, Windows), cron/Task Scheduler 30-minute intervals, not containerized, not serverless
- External services: 2 services (GitHub - send/receive via git push/pull; Notion API - receive via `cal_sync.py`)
- Existing security controls: `.gitignore` excludes `openclaw/openclaw.json`, `credentials/`, `.env`; `umask 077` on generated config files; `EXCLUDES` dict filters sensitive Claude Code directories (history, cache, telemetry); `CLAUDE_INCLUDES` whitelist limits sync scope; `validate_filepath()` blocks path traversal (`..`, null bytes, absolute paths); `validate_hostname()` enforces RFC 952/1123; `validate_timestamp()` rejects negative/future values; `openclaw.template.json` uses placeholders instead of real tokens

### Data Classification

| Data Field | Location | Sensitivity | Current Control | Required Control | Gap |
|---|---|---|---|---|---|
| 실명 (김강남) | `openclaw/workspace/USER.md` (line 3) | CONFIDENTIAL (PII under PIPA Art. 2) | None - committed to PUBLIC repo | Encryption at rest, access control, removal from public repo | YES - CRITICAL |
| 이메일 (kangnam7653@gmail.com) | `openclaw/workspace/cal_sync.py` (line 13), `openclaw/workspace/notion_to_gcal_sync.sh`, `openclaw/workspace/memory/` | CONFIDENTIAL (PII under PIPA Art. 2) | None - committed to PUBLIC repo | Encryption at rest, access control, removal from public repo | YES - CRITICAL |
| Telegram ID (5512922109) | `openclaw/workspace/USER.md` (line 8) | CONFIDENTIAL (PII under PIPA Art. 2) | None - committed to PUBLIC repo | Removal from public repo, access control | YES - CRITICAL |
| GitHub username (kangnam7654) | `openclaw/workspace/sync-openclaw.sh` (line 42), `README.md` | INTERNAL | None | Acceptable for public profile | NO |
| Notion DB ID | `openclaw/workspace/cal_sync.py` (line 12) | CONFIDENTIAL (internal resource identifier) | None - committed to PUBLIC repo | Removal from public repo | YES |
| Hostname/OS info (Kangnamui-MacBookPro, kangnam-Desktop-Ubuntu, etc.) | `state/*.md`, `timestamps/*.json` | INTERNAL | None | Acceptable for public profile | NO |
| Device file paths (/Users/kangnam/..., /home/kangnam/...) | `openclaw/workspace/memory/*.md`, `state/*.md` | INTERNAL | None | Low risk | NO |
| Gateway auth token (template placeholder) | `openclaw/openclaw.template.json` | PUBLIC (placeholder only) | `.gitignore` excludes real `openclaw.json`; template uses `<REPLACE_WITH_NEW_TOKEN>` | Meets requirement | NO |
| Anthropic API key pattern | `setup-mac.sh`, `README.md` | PUBLIC (example string `sk-ant-...` only) | Only placeholder shown | Meets requirement | NO |
| GitHub auth token (runtime) | `openclaw/workspace/sync-openclaw.sh` (line 41-42) | RESTRICTED | Token fetched at runtime via `gh auth token`, not hardcoded; BUT URL pattern `https://user:${TOKEN}@github.com` may leak token into shell history/process table | Token should use credential helper, not URL embedding | YES |
| Claude Code agent/skill definitions | `claude-code/agents/`, `claude-code/skills/` | INTERNAL | Whitelist sync (`CLAUDE_INCLUDES`) | Acceptable | NO |
| Claude Code settings | `claude-code/settings.json` | INTERNAL | `skipDangerousModePermissionPrompt: true` is a security-relevant config | Document the risk implication | YES (minor) |
| Cron schedule & log paths | `state/*.md` | INTERNAL | None | Acceptable for public profile | NO |

### Compliance Matrix

| Framework | Requirement | Article | Status | Evidence |
|---|---|---|---|---|
| PIPA | 동의 수집 및 목적 명시 | Art. 15 | FAIL | 개인정보(실명, 이메일, Telegram ID) 수집 및 공개 저장소 게시에 대한 동의 절차 부재. 프라이버시 정책 문서 없음. |
| PIPA | 목적 제한 | Art. 3 | FAIL | 설정 동기화 목적이나, `USER.md`의 실명/Telegram ID는 동기화에 불필요한 개인정보. 수집 목적 대비 과잉 수집. |
| PIPA | 목적 달성 후 파기 | Art. 21 | FAIL | 보유기간 정책 없음. Git 이력에 개인정보가 영구 보존됨. 삭제 로직 부재. |
| PIPA | 주민등록번호 암호화 | Art. 24 | N/A | 주민등록번호 수집하지 않음. |
| PIPA | 개인정보처리방침 공개 | Art. 30 | FAIL | 개인정보처리방침 문서 없음. 공개 저장소에 개인정보 포함 상태. |
| PIPA | 국외이전 동의 | Art. 17 | FAIL | 데이터가 GitHub (미국 서버)에 저장됨. PUBLIC 저장소이므로 전 세계에서 접근 가능. 국외이전 동의 절차 없음. |
| GDPR | Encryption of personal data | Art. 32(1)(a) | FAIL | PII (name, email, Telegram ID) stored in plain text in a PUBLIC GitHub repository. No encryption at rest. Git transfer uses SSH (encrypted in transit), but data is publicly readable. |
| GDPR | Data minimization | Art. 5(1)(c) | FAIL | `USER.md` contains real name, Telegram ID -- not required for config sync functionality. `cal_sync.py` hardcodes email address. |
| GDPR | Right to erasure | Art. 17 | FAIL | No deletion endpoint/mechanism. Git history retains data permanently. Removing from HEAD does not remove from history. |
| GDPR | Data processing records | Art. 30 | FAIL | No data processing documentation exists. |
| GDPR | Breach notification process | Art. 33 | FAIL | No incident response plan. |
| GDPR | Lawful basis documented | Art. 6 | UNVERIFIED | No privacy policy. This is a personal project, but PII is publicly exposed on a public repo accessible to anyone. |
| GDPR | DPO designated | Art. 37 | N/A | Personal project, DPO not required. |

### Threat Register

| ID | STRIDE | Threat | Likelihood | Impact | Risk Score | Current Control | Recommended Control |
|---|---|---|---|---|---|---|---|
| T-01 | Information Disclosure | PII (실명, 이메일, Telegram ID) 공개 저장소에 노출 -- 누구나 접근 가능 | 5 | 4 | 20 (CRITICAL) | None - PUBLIC repo | 즉시 저장소를 PRIVATE으로 전환하거나 PII가 포함된 파일을 제거하고 git history에서도 `git filter-repo`로 삭제 |
| T-02 | Information Disclosure | Git history에 PII가 영구 보존되어 있어 HEAD에서 삭제해도 이전 커밋에서 복원 가능 | 5 | 4 | 20 (CRITICAL) | None | `git filter-repo`로 PII 포함 파일의 전체 이력 제거 후 force push. 또는 저장소를 PRIVATE으로 전환 |
| T-03 | Information Disclosure | `sync-openclaw.sh`에서 `gh auth token`을 HTTPS URL에 삽입 -- 프로세스 테이블/shell history에 토큰 노출 가능 | 3 | 4 | 12 (HIGH) | Token은 런타임에 가져옴 (하드코딩 아님) | `git credential helper` 또는 SSH remote 사용으로 URL에 토큰 포함 방지 |
| T-04 | Tampering | 30분 크론에서 `git pull --rebase`/`git reset --hard origin/main` 실행 -- 원격 저장소 변조 시 로컬 설정이 자동으로 덮어씌워짐 | 2 | 4 | 8 (MEDIUM) | SSH key 인증으로 push 권한 제한 | Branch protection rule 추가 (main branch에 직접 push 방지), signed commit 검증 |
| T-05 | Spoofing | 피어 타임스탬프 파일 조작으로 가짜 최신 상태 주입 가능 -- `newest-wins` 로직 악용 | 2 | 3 | 6 (MEDIUM) | `validate_filepath()`, `validate_timestamp()` 검증 존재 | Git signed commit 검증 추가. 피어 타임스탬프에 HMAC 서명 추가 |
| T-06 | Elevation of Privilege | `sync.sh`의 `git reset --hard origin/main` (Windows pull-only 모드)은 로컬 파일을 원격 상태로 강제 리셋 -- 공격자가 repo에 악성 스크립트 주입 시 다음 크론에서 자동 실행 | 2 | 5 | 10 (MEDIUM) | SSH key로 push 권한 제한 | 동기화 스크립트에 무결성 검증 추가. 스크립트 파일 변경 시 경고/중단 로직 |
| T-07 | Repudiation | 동기화 로그가 `/tmp/` 또는 `~/.local/share/` 에만 저장 -- 변조/삭제 용이. 감사 추적 불가 | 3 | 2 | 6 (MEDIUM) | 기본 stdout 로그만 존재 | 변조 방지 로그 저장소 사용 (append-only). 동기화 이벤트별 hash chain 기록 |
| T-08 | Denial of Service | 크론이 30분마다 실행되므로, git fetch/push 실패 시 반복 실패 로그 누적. 하지만 서비스 자체는 개인용이므로 DoS 영향 제한적 | 2 | 1 | 2 (LOW) | `set -e`로 에러 시 조기 종료 | 현 수준 적절 |
| T-09 | Information Disclosure | `claude-code/settings.json`의 `skipDangerousModePermissionPrompt: true`가 공개 -- 공격자에게 Claude Code 보안 설정 노출 | 4 | 2 | 8 (MEDIUM) | None | 보안 관련 설정은 동기화 대상에서 제외하거나 저장소를 PRIVATE으로 전환 |

### Domain Scores

| Domain | Score | Key Finding |
|---|---|---|
| 1. Policy & Governance | 2/10 | 보안 정책 문서 없음. 개인정보처리방침 없음. 인시던트 대응 계획 없음. `.gitignore`와 `README.md`에 보안 주의사항 일부 기술되어 있으나 정식 정책이 아님. |
| 2. Data Protection | 1/10 | PII(실명, 이메일, Telegram ID)가 PUBLIC GitHub 저장소에 평문으로 노출됨. 암호화 없음. 데이터 분류 없음. 보유기간 정책 없음. Git 이력에 영구 보존. |
| 3. Access Control | 3/10 | Git SSH key로 push 권한 제한. 하지만 저장소가 PUBLIC이므로 read 접근에 제한 없음. MFA 미확인. 개인 프로젝트로 RBAC 불필요하나, 공개 저장소에 PII가 있어 접근 제어 실패. |
| 4. Threat & Vulnerability Mgmt | 4/10 | `validate_filepath()`, `validate_timestamp()`, `validate_hostname()` 등 입력 검증 존재. GitHub Actions CI/CD에서 자동 테스트 실행. 하지만 정식 위협 모델 없음. 의존성 스캔 없음. |
| 5. Incident Response Readiness | 1/10 | 인시던트 대응 계획 없음. 모니터링 없음 (로그 파일만 존재). 에스컬레이션 경로 없음. 동기화 실패 시 "다음 실행에서 재시도" 수준. |
| 6. Third-Party Risk | 3/10 | GitHub(외부 서비스) 사용 중이나 보안 평가 없음. Notion API 연동 존재(`cal_sync.py`). DPA 없음. 서드파티 서비스 목록은 식별 가능하나 정식 평가 미수행. |
| **Security Posture Score (SPS)** | **2.35/10** | |

SPS 계산: (2 x 0.15) + (1 x 0.20) + (3 x 0.20) + (4 x 0.20) + (1 x 0.10) + (3 x 0.15) = 0.30 + 0.20 + 0.60 + 0.80 + 0.10 + 0.45 = **2.45/10**

수정: (2 x 0.15) + (1 x 0.20) + (3 x 0.20) + (4 x 0.20) + (1 x 0.10) + (3 x 0.15) = 0.30 + 0.20 + 0.60 + 0.80 + 0.10 + 0.45 = **2.45/10**

### Verdict

**CRITICAL** (SPS 2.45 < 4.0): 보안 수준이 운영에 불충분합니다. 즉각적인 조치가 필요한 항목이 6개 있습니다.

가장 심각한 문제: **개인정보(실명, 이메일, Telegram ID)가 PUBLIC GitHub 저장소에 평문으로 노출**되어 있어, 개인정보보호법(PIPA) 및 GDPR을 중대하게 위반하고 있습니다. 이 저장소는 전 세계 누구나 접근할 수 있는 상태입니다.

### Remediation Roadmap

| Priority | Finding | Risk Score | Remediation | Effort | Impact on Operations |
|---|---|---|---|---|---|
| 1 | T-01: PII 공개 저장소 노출 (실명, 이메일, Telegram ID) | 20 (CRITICAL) | **즉시** 다음 중 하나 실행: (A) `gh repo edit --visibility private` 로 저장소 PRIVATE 전환, 또는 (B) PII 포함 파일(`openclaw/workspace/USER.md`, `openclaw/workspace/cal_sync.py`, `openclaw/workspace/notion_to_gcal_sync.sh`, `openclaw/workspace/memory/*.md`)을 `.gitignore`에 추가하고 `git rm --cached`로 제거. `USER.md`에서 실명/Telegram ID 삭제. `cal_sync.py`에서 이메일을 환경변수로 대체. | 1시간 | 저장소 접근 방식 변경 없음 (SSH key 사용 중). PRIVATE 전환 시 다른 기기에서 clone 시 인증 필요. |
| 2 | T-02: Git history에 PII 영구 보존 | 20 (CRITICAL) | `git filter-repo` 또는 `BFG Repo-Cleaner`로 PII 포함 파일의 전체 이력 제거. 이후 `git push --force`. 모든 기기에서 re-clone 필요. | 2시간 + 모든 기기 re-clone 30분/기기 | Force push로 인해 모든 기기에서 re-clone 필요. 크론 실행 중 충돌 방지를 위해 모든 기기의 크론을 임시 중지 후 작업. |
| 3 | T-03: HTTPS URL에 GitHub token 삽입 | 12 (HIGH) | `openclaw/workspace/sync-openclaw.sh`에서 `REMOTE_URL` 구성을 SSH (`git@github.com:...`) 방식으로 변경. 또는 `git credential helper` 사용. | 30분 | 없음 |
| 4 | PIPA Art. 15, 30 / GDPR Art. 6, 30: 개인정보처리방침 부재 | - | 개인정보처리방침 문서 작성: 수집 항목, 수집 목적, 보유기간, 파기 절차, 제3자 제공(GitHub), 국외이전 고지. 개인 프로젝트라도 PII를 공개 처리하므로 필요. | 2시간 | 없음 |
| 5 | PIPA Art. 3 / GDPR Art. 5(1)(c): 목적 대비 과잉 수집 | - | `USER.md`에서 실명, Telegram ID 제거 (동기화에 불필요). `cal_sync.py`의 이메일을 `CALENDAR_ID` 환경변수로 대체. `Notion DB ID`도 환경변수로 이동. | 1시간 | `cal_sync.py` 실행 시 환경변수 설정 필요 |
| 6 | T-06: Windows pull-only의 `git reset --hard` 원격 코드 자동 실행 위험 | 10 (MEDIUM) | 동기화 대상 경로에 실행 파일(.sh, .py)이 포함되지 않도록 EXCLUDES에 추가하거나, 스크립트 파일 변경 감지 시 자동 적용을 중단하는 안전장치 추가. | 2시간 | 스크립트 업데이트 시 수동 확인 단계 추가 |
| 7 | T-09: 보안 설정 공개 노출 (`skipDangerousModePermissionPrompt`) | 8 (MEDIUM) | `settings.json`을 동기화 대상에서 제외하거나, 보안 관련 키를 별도 로컬 파일로 분리. 또는 저장소 PRIVATE 전환으로 해결. | 30분 | settings.json 수동 동기화 필요 |
| 8 | T-04, T-05: 원격 변조 시 자동 적용 + 피어 스푸핑 | 8/6 (MEDIUM) | GitHub repo에 branch protection rule 추가. 선택적으로 signed commit 검증 추가. | 1시간 | commit 시 GPG/SSH signing 설정 필요 |
| 9 | Domain 5: 인시던트 대응 계획 없음 | - | 최소한의 인시던트 대응 문서 작성: (1) 토큰/키 노출 시 재발급 절차, (2) PII 노출 시 대응 절차, (3) 동기화 장애 시 복구 절차. | 1시간 | 없음 |

### Policies (if requested)

[사용자가 정책 작성을 요청하지 않았으므로 생략]
