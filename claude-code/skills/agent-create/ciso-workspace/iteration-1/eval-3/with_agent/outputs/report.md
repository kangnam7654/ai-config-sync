## Security Posture Report

> **Edge Case Applied**: "User requests policy only (no audit)" — Steps 1-5 skipped. Incident Response Playbook drafted using industry-standard requirements customized for the provided context.

### Application Security Profile
- Application type: CLI (설정 동기화 도구)
- Tech stack: Python, Bash, Git
- Authentication: Git SSH key / HTTPS credentials
- Deployment: 로컬 실행 (cron/Task Scheduler), GitHub 원격 저장소
- External services: 1 service (GitHub — send/receive)
- Existing security controls: `.gitignore`로 민감 파일 제외, 화이트리스트 기반 동기화 대상 제한 (`CLAUDE_INCLUDES`), 템플릿 분리 (`openclaw.template.json`)

### Data Classification

| Data Field | Location | Sensitivity | Current Control | Required Control | Gap |
|---|---|---|---|---|---|
| API 키 참조 경로 | claude-code/, openclaw/ | CONFIDENTIAL | 화이트리스트 필터링 | + 암호화 저장, 접근 로깅 | YES |
| IDE 설정 파일 | openclaw/workspace/ | INTERNAL | Git 저장소 접근 제한 | 접근 제어 | NO |
| CLI 설정 파일 | claude-code/ | INTERNAL | Git 저장소 접근 제한 | 접근 제어 | NO |
| Git 자격증명 | 시스템 키체인/자격증명 관리자 | RESTRICTED | OS 수준 보호 | OS 수준 보호 유지 | NO |
| openclaw.json (민감값 포함) | 로컬 전용 | CONFIDENTIAL | .gitignore 제외, 템플릿만 추적 | 현행 유지 | NO |

### Compliance Matrix

No compliance frameworks applicable — application does not process regulated data. 1인 개발자의 개인 개발 환경 설정 동기화 도구로, 제3자 개인정보를 처리하지 않음.

### Threat Register

| ID | STRIDE | Threat | Likelihood | Impact | Risk Score | Current Control | Recommended Control |
|---|---|---|---|---|---|---|---|
| T-01 | Information Disclosure | API 키 참조가 포함된 설정 파일이 공개 저장소에 노출 | 2 | 4 | 8 (MEDIUM) | private repo, CLAUDE_INCLUDES 화이트리스트, openclaw.json 제외 | pre-commit hook으로 시크릿 패턴 스캔 + git-secrets 도구 도입 |
| T-02 | Tampering | 악의적 피어가 동기화를 통해 악성 설정 주입 | 1 | 3 | 3 (LOW) | 1인 개발자 (피어 없음), newest-wins 병합 | 동기화 전 변경 diff 로깅 |
| T-03 | Spoofing | Git SSH 키 탈취로 저장소 무단 접근 | 2 | 3 | 6 (MEDIUM) | SSH 키 기반 인증 | SSH 키에 패스프레이즈 설정, GitHub에서 IP 제한 활성화 |
| T-04 | Repudiation | 동기화 변경사항의 감사 추적 부재 | 2 | 2 | 4 (LOW) | Git commit 히스토리 | 현행 Git 히스토리로 충분 (1인 개발) |
| T-05 | Denial of Service | cron 스크립트 오류로 동기화 중단 | 3 | 2 | 6 (MEDIUM) | 없음 | sync.sh에 에러 알림 추가 (실패 시 로컬 알림) |

### Domain Scores

| Domain | Score | Key Finding |
|---|---|---|
| 1. Policy & Governance | 3/10 | 보안 정책 문서 부재, 인시던트 대응 계획 없음 (이 플레이북으로 개선 예정) |
| 2. Data Protection | 6/10 | 민감 파일 제외 패턴 존재하나 암호화 미적용, 데이터 분류 비공식적 |
| 3. Access Control | 6/10 | SSH 키 기반 인증 사용, 단 MFA 미강제 상태 |
| 4. Threat & Vulnerability Mgmt | 3/10 | 위협 모델 부재, 의존성 스캐닝 없음 |
| 5. Incident Response Readiness | 2/10 | 인시던트 프로세스 없음, 모니터링 없음 (이 플레이북으로 개선 예정) |
| 6. Third-Party Risk | 5/10 | GitHub 단일 외부 서비스, 보안 평가 비공식적이나 인지하고 있음 |
| **Security Posture Score (SPS)** | **4.3/10** | |

### Verdict

**AT RISK** (SPS 4.3): Significant security gaps exist. 2 CRITICAL-area items (Policy & Governance, Incident Response) must be remediated. 이 인시던트 대응 플레이북 적용으로 Domain 1과 Domain 5가 각각 +2~3점 개선 가능하여 SPS 5.5~6.0 달성 예상.

### Remediation Roadmap

| Priority | Finding | Risk Score | Remediation | Effort | Impact on Operations |
|---|---|---|---|---|---|
| 1 | T-01: API 키 참조 노출 위험 | 8 (MEDIUM) | pre-commit hook에 git-secrets 또는 detect-secrets 도입. `uv add detect-secrets` 후 `.pre-commit-config.yaml` 구성 | 2시간 | 커밋 시 ~1초 지연 추가 |
| 2 | D5: 인시던트 대응 계획 부재 | - | 아래 인시던트 대응 플레이북 적용 | 1시간 (읽기 + 연락처 설정) | 없음 |
| 3 | T-05: 동기화 실패 감지 없음 | 6 (MEDIUM) | sync.sh에 실패 시 `osascript -e 'display notification'` (macOS) 또는 로그 파일 기록 추가 | 1시간 | 없음 |
| 4 | T-03: SSH 키 보안 강화 | 6 (MEDIUM) | SSH 키에 패스프레이즈 설정 확인, GitHub 계정에 2FA 활성화 확인 | 30분 | SSH 사용 시 패스프레이즈 입력 (키체인으로 완화 가능) |
| 5 | D1: 보안 정책 문서화 | - | 데이터 분류 정책 + 접근 제어 정책을 docs/에 문서화 | 2시간 | 없음 |
| 6 | D4: 의존성 스캐닝 도입 | - | GitHub Dependabot 활성화 또는 `uv audit` 정기 실행 | 1시간 | PR 생성 시 자동 스캐닝 알림 |

### Policies

---

#### Incident Response Playbook Policy

- **Scope**: KangNam Dev 조직의 ai-config-sync 프로젝트 및 동기화되는 모든 개발 환경 설정 (IDE 설정, CLI 설정, API 키 참조)을 대상으로 한다. 1인 개발자 환경에 최적화되어 있으며, 팀 확장 시 역할 배정 섹션을 갱신하라.
- **Classification**: CONFIDENTIAL 이상의 데이터가 관련된 모든 보안 사건에 적용한다.
- **Effective date**: 2026-03-26
- **Review cycle**: 6개월마다 검토 (다음 검토: 2026-09-26)

---

##### 1. 인시던트 분류 체계

| 심각도 | 정의 | 예시 | 대응 시간 |
|---|---|---|---|
| SEV-1 (Critical) | RESTRICTED/CONFIDENTIAL 데이터의 외부 노출이 확인된 경우 | API 키가 공개 저장소에 push됨, Git 자격증명 탈취 확인 | 즉시 (15분 이내 대응 시작) |
| SEV-2 (High) | 인가되지 않은 접근 시도가 감지되었으나 데이터 유출이 확인되지 않은 경우 | GitHub 계정에 알 수 없는 로그인 시도, SSH 키 무단 사용 의심 | 1시간 이내 대응 시작 |
| SEV-3 (Medium) | 동기화 시스템 무결성이 훼손되었으나 민감 데이터 노출은 없는 경우 | sync.sh 오류로 잘못된 설정 배포, timestamps 충돌 | 4시간 이내 대응 시작 |
| SEV-4 (Low) | 보안 정책 위반이 감지되었으나 즉각적 위험이 없는 경우 | .gitignore 누락 파일 발견 (민감값 미포함), 동기화 지연 | 24시간 이내 대응 시작 |

---

##### 2. 인시던트 유형별 플레이북

###### 2.1 Playbook A: API 키 / 시크릿 노출 (SEV-1)

**트리거**: API 키, 토큰, 비밀번호 등이 Git 히스토리 또는 공개 저장소에 노출된 경우

**즉시 조치 (15분 이내)**:

1. 노출된 키/토큰을 해당 서비스 대시보드에서 즉시 무효화(revoke)하라.
2. 새 키를 생성하고 로컬 설정에만 저장하라 (저장소에 push하지 마라).
3. GitHub 저장소가 public인 경우: 즉시 private으로 전환하라.

**억제 (1시간 이내)**:

4. `git log --all --oneline -- <노출된 파일>` 로 노출 범위를 파악하라.
5. 노출된 커밋이 remote에 push되었는지 확인하라: `git log origin/main --oneline -- <파일>`.
6. push된 경우: `git filter-branch` 또는 `git filter-repo`로 히스토리에서 해당 파일을 제거하라.
7. GitHub에 캐시 삭제를 요청하라: https://support.github.com/contact (private repo 전환만으로는 캐시된 커밋에 접근 가능).

**복구 (4시간 이내)**:

8. 모든 동기화 대상 기기에서 `git fetch --all && git reset --hard origin/main`을 실행하라.
9. 노출된 키를 사용하는 모든 서비스의 접근 로그를 확인하라: 비정상 접근 여부 판별.
10. `.gitignore`와 `CLAUDE_INCLUDES` 화이트리스트를 검토하여 해당 파일 유형이 포함되지 않도록 하라.
11. detect-secrets 또는 git-secrets의 패턴 목록에 해당 키 형식을 추가하라.

**사후 조치**:

12. 포스트모템 기록을 작성하라 (섹션 4 템플릿 참조).
13. pre-commit hook에 시크릿 스캐너가 동작하는지 확인하라.

---

###### 2.2 Playbook B: Git 자격증명 / SSH 키 탈취 의심 (SEV-1)

**트리거**: GitHub로부터 알 수 없는 활동 알림 수신, 또는 인가하지 않은 push/설정 변경 감지

**즉시 조치 (15분 이내)**:

1. GitHub > Settings > Sessions 에서 모든 활성 세션을 종료하라.
2. GitHub 비밀번호를 변경하라.
3. GitHub > Settings > SSH and GPG keys 에서 인식하지 못하는 키를 삭제하라.
4. GitHub > Settings > Developer settings > Personal access tokens 에서 모든 PAT를 무효화하라.

**억제 (1시간 이내)**:

5. 새 SSH 키를 생성하라: `ssh-keygen -t ed25519 -C "kangnam@device" -f ~/.ssh/id_ed25519_new`.
6. 새 키에 강력한 패스프레이즈를 설정하라.
7. GitHub에 새 SSH 키를 등록하고, 이전 키를 삭제하라.
8. GitHub > Settings > Security log 에서 최근 활동을 검토하라: 인가하지 않은 repo 생성, 삭제, 설정 변경 여부.

**복구 (4시간 이내)**:

9. 모든 기기(macOS, Ubuntu, Windows)에서 SSH 키를 갱신하라.
10. ai-config-sync 저장소의 최근 커밋을 검토하라: 악의적 변경이 주입되지 않았는지 확인.
11. 2FA가 활성화되어 있지 않다면 즉시 활성화하라.
12. 다른 서비스에서 동일 비밀번호를 사용하고 있다면 모두 변경하라.

**사후 조치**:

13. 포스트모템 기록 작성.
14. SSH 키 패스프레이즈 정책 재검토.

---

###### 2.3 Playbook C: 동기화 무결성 훼손 (SEV-3)

**트리거**: sync.sh 오류로 잘못된 설정이 기기에 배포됨, 또는 timestamps 충돌로 구 설정이 신 설정을 덮어씀

**조치 (4시간 이내)**:

1. 모든 기기에서 cron/Task Scheduler의 sync.sh 실행을 임시 중지하라.
   - macOS/Linux: `crontab -e` 에서 해당 줄 주석 처리.
   - Windows: Task Scheduler에서 작업 비활성화.
2. `git log --oneline -20` 으로 최근 동기화 커밋을 확인하라.
3. 문제가 된 커밋을 식별하고 `git diff <이전커밋>..<문제커밋>` 으로 변경 내용을 분석하라.
4. 정상 상태로 복원하라:
   - 로컬 설정이 정상인 경우: `sync-timestamps.py`를 수동 실행하여 타임스탬프를 재동기화.
   - 로컬 설정도 손상된 경우: `git show <정상커밋>:<파일경로>` 로 정상 파일을 복원.
5. `sync-timestamps.py`의 `sections`, `EXCLUDES`, `CLAUDE_INCLUDES` 설정을 검토하라.
6. 수정 후 `uv run python sync-timestamps.py . $(hostname -s)` 로 직접 실행하여 확인하라.
7. cron/Task Scheduler를 재활성화하라.

**사후 조치**:

8. 포스트모템 기록 작성.
9. 필요시 sync.sh에 검증 단계(동기화 전/후 diff 로깅) 추가.

---

###### 2.4 Playbook D: GitHub 서비스 장애 (SEV-3)

**트리거**: `git fetch` 또는 `git push`가 반복 실패, GitHub Status (https://www.githubstatus.com/) 에서 장애 확인

**조치**:

1. https://www.githubstatus.com/ 에서 장애 상태를 확인하라.
2. sync.sh의 cron 실행을 일시 중지할 필요는 없다 (다음 실행에서 자동 재시도).
3. 로컬 설정 변경은 정상적으로 계속하라 (로컬 Git 커밋은 가능).
4. GitHub 복구 후 `git push origin main && git pull --rebase origin main` 을 수동 실행하여 동기화를 확인하라.

---

##### 3. 커뮤니케이션 계획

| 대상 | 방법 | 시점 | 내용 |
|---|---|---|---|
| 본인 (1인 개발자) | macOS 알림 / 터미널 로그 | 인시던트 감지 즉시 | 인시던트 유형, 심각도, 즉시 조치 사항 |
| 영향받는 서비스 제공자 | 해당 서비스 지원 채널 | SEV-1 발생 시 키 무효화 직후 | 노출된 키 정보, 무효화 시각, 비정상 사용 확인 요청 |
| GitHub Support | support.github.com/contact | 히스토리 정리가 필요한 경우 | 캐시 삭제 요청, 영향받는 커밋 SHA |

> 1인 개발자 환경에서는 외부 커뮤니케이션이 최소화된다. 팀 확장 시 이 테이블에 팀원, 경영진, 법무 담당을 추가하라.

---

##### 4. 포스트모템 템플릿

모든 SEV-1, SEV-2 인시던트와 반복 발생하는 SEV-3 인시던트에 대해 포스트모템을 작성하라. 파일 위치: `docs/postmortems/YYYY-MM-DD-<간략설명>.md`

```markdown
# 포스트모템: [인시던트 제목]

## 요약
- 발생 시각: YYYY-MM-DD HH:MM (KST)
- 감지 시각: YYYY-MM-DD HH:MM (KST)
- 해결 시각: YYYY-MM-DD HH:MM (KST)
- 심각도: SEV-N
- 영향 범위: [영향받은 기기, 서비스, 데이터]

## 타임라인
| 시각 | 행동 |
|---|---|
| HH:MM | [무엇을 했는지] |

## 근본 원인
[기술적 근본 원인을 1-3문장으로 기술]

## 영향
- 노출된 데이터: [구체적 데이터 항목]
- 영향 기간: [시간]
- 비정상 접근 여부: [확인됨 / 미확인 / 해당 없음]

## 조치 완료 사항
1. [완료한 조치]

## 재발 방지 대책
| 대책 | 담당 | 기한 | 상태 |
|---|---|---|---|
| [대책] | kangnam | YYYY-MM-DD | [ ] 미완료 |

## 교훈
- [이번 인시던트에서 배운 점]
```

---

##### 5. 예방적 모니터링 체크리스트

아래 항목을 주 1회 수동 점검하라 (1인 개발자 환경에서 자동화 대비 비용 효율적):

| # | 점검 항목 | 방법 | 소요 시간 |
|---|---|---|---|
| 1 | GitHub 보안 로그 확인 | GitHub > Settings > Security log | 2분 |
| 2 | SSH 키 목록 확인 | GitHub > Settings > SSH and GPG keys — 인식하지 못하는 키 없는지 | 1분 |
| 3 | PAT 목록 확인 | GitHub > Settings > Developer settings > Personal access tokens | 1분 |
| 4 | sync.sh 최근 실행 로그 확인 | `git log --oneline -10` 에서 30분 간격 커밋이 정상적으로 생성되는지 | 2분 |
| 5 | .gitignore 무결성 확인 | `git status` 에서 추적되지 않아야 할 파일이 노출되지 않는지 | 1분 |
| 6 | detect-secrets 기준선 갱신 | `detect-secrets scan --baseline .secrets.baseline` (도입 후) | 2분 |

총 소요: 약 9분/주

---

##### 6. 플레이북 유지 관리

- **Requirements**:
  1. 이 플레이북을 6개월마다 검토하고 날짜를 갱신하라.
  2. SEV-1 또는 SEV-2 인시던트 발생 후 7일 이내에 플레이북을 재검토하고, 포스트모템의 재발 방지 대책을 반영하라.
  3. 새로운 동기화 대상 (sections dict에 추가)이 생기면 해당 데이터의 인시던트 시나리오를 추가하라.
  4. 팀 규모가 2인 이상으로 확장되면 역할 배정 (인시던트 커맨더, 커뮤니케이션 담당)을 정의하라.
- **Exceptions**: 긴급 상황에서 플레이북 단계를 건너뛰어야 하는 경우, 포스트모템에 건너뛴 이유를 기록하라.
- **Review cycle**: 6개월 (다음 검토: 2026-09-26)
- **Effective date**: 2026-03-26
