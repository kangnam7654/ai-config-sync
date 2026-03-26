### Policies

#### Incident Response Playbook

- **Scope**: KangNam Dev 조직의 모든 개발 환경 설정 파일(IDE 설정, CLI 설정, API 키 참조)을 동기화하는 ai-config-sync 프로젝트에서 발생하는 보안 인시던트에 적용한다. 1인 개발자 환경이므로 모든 역할을 단일 담당자가 수행한다.
- **Classification**: CONFIDENTIAL (API 키 참조 포함), INTERNAL (IDE/CLI 설정)
- **Requirements**:

  **1. 인시던트 분류 기준**

  | 심각도 | 정의 | 예시 | 대응 시한 |
  |---|---|---|---|
  | SEV-1 (Critical) | API 키 또는 시크릿이 공개 저장소에 노출됨 | `.env` 파일, API 키가 포함된 설정 파일이 public repo에 push됨 | 즉시 (발견 후 15분 이내 초기 대응) |
  | SEV-2 (High) | 동기화 경로를 통해 인가되지 않은 설정 변경이 전파됨 | 악성 설정이 sync를 통해 다른 기기로 전파, `.claude/CLAUDE.md` 변조 | 1시간 이내 초기 대응 |
  | SEV-3 (Medium) | 동기화 실패로 설정 불일치 발생, 데이터 무결성 의심 | `sync-timestamps.py` 오류로 파일 덮어쓰기, 타임스탬프 충돌 | 4시간 이내 확인 |
  | SEV-4 (Low) | 비민감 설정 파일의 동기화 지연 또는 누락 | cron job 미실행, 네트워크 오류로 git push 실패 | 다음 업무일 내 확인 |

  **2. 탐지 (Detection)**

  2.1. 다음 이벤트를 모니터링하라:
    - git log에서 예상치 못한 커밋 (자신이 아닌 author, 비정상 시간대)
    - `sync.sh` 실행 로그에서 에러 발생 (cron 로그: `grep CRON /var/log/syslog` 또는 macOS `log show --predicate 'eventMessage contains "sync.sh"'`)
    - `timestamps/` 디렉토리의 비정상적 변경 (미래 타임스탬프, 알 수 없는 호스트명)
    - `.gitignore`에 포함되어야 할 파일이 추적되는 경우 (`openclaw.json` 등)

  2.2. 주 1회 아래 점검을 수행하라:
    - `git log --all --oneline -20`으로 최근 커밋 이력 검토
    - `git remote -v`로 remote URL이 변조되지 않았는지 확인
    - 동기화 대상 파일 목록(`CLAUDE_INCLUDES`, `sections` dict)이 의도한 범위인지 확인

  **3. 초기 대응 (Initial Response)**

  3.1. **SEV-1: API 키/시크릿 노출 시**
    - 단계 1 (0-15분): 노출된 키를 즉시 폐기(revoke)하라. 해당 서비스 대시보드에서 키를 무효화하고 새 키를 발급하라.
    - 단계 2 (15-30분): `git filter-branch` 또는 `git-filter-repo`로 git 히스토리에서 시크릿을 제거하라. public repo인 경우 GitHub Support에 캐시 삭제를 요청하라.
    - 단계 3 (30-60분): 새 키를 안전한 경로에 설정하라. 노출 경로를 `.gitignore`와 `EXCLUDES` 딕셔너리에 추가하라.
    - 단계 4 (1-4시간): 노출된 키로 발생한 비인가 사용 이력을 확인하라 (서비스 제공자의 API 사용 로그, 청구 내역 확인).

  3.2. **SEV-2: 인가되지 않은 설정 변경 전파 시**
    - 단계 1: 동기화를 즉시 중단하라 (`sync.sh`의 cron job을 비활성화: `crontab -e`에서 해당 라인 주석 처리).
    - 단계 2: `git log --diff-filter=M -- openclaw/ claude-code/ timestamps/`로 변경된 파일을 식별하라.
    - 단계 3: `git diff <안전한_커밋>..HEAD`로 변경 내용을 검토하라.
    - 단계 4: 안전한 상태의 커밋으로 롤백하라: `git revert <악성_커밋>` 또는 필요시 `git reset --hard <안전한_커밋>`.
    - 단계 5: 모든 동기화 대상 기기(macOS, Ubuntu, Windows)에서 로컬 설정 파일을 검증하라.
    - 단계 6: 원인 파악 후 동기화를 재개하라.

  3.3. **SEV-3: 동기화 실패/무결성 의심 시**
    - 단계 1: `python3 sync-timestamps.py . $(hostname -s)`를 수동 실행하여 에러 메시지를 확인하라.
    - 단계 2: `timestamps/` 디렉토리의 각 기기별 타임스탬프 파일을 비교하라.
    - 단계 3: 로컬 파일의 mtime과 repo 내 타임스탬프가 일치하는지 확인하라.
    - 단계 4: 불일치가 있으면 신뢰할 수 있는 소스(가장 최근에 수동 확인한 기기)를 기준으로 수동 동기화하라.

  3.4. **SEV-4: 동기화 지연/누락 시**
    - 단계 1: cron job 상태를 확인하라 (`crontab -l`).
    - 단계 2: 네트워크 연결 및 git remote 접근 가능 여부를 확인하라 (`git fetch --dry-run origin main`).
    - 단계 3: 원인 해소 후 `bash sync.sh`를 수동 실행하여 동기화를 복구하라.

  **4. 봉쇄 (Containment)**

  4.1. 즉시 봉쇄: 영향받는 기기의 `sync.sh` cron job을 비활성화하라.
  4.2. 네트워크 봉쇄: 필요시 git remote 접근을 차단하라 (`git remote set-url origin DISABLED`).
  4.3. 범위 확인: `state/` 디렉토리의 기기별 상태 파일을 확인하여 영향받는 기기 목록을 파악하라.
  4.4. 증거 보존: 현재 상태를 별도 브랜치에 보존하라 (`git checkout -b incident-evidence-YYYYMMDD`).

  **5. 근절 (Eradication)**

  5.1. 인시던트 원인을 식별하고 제거하라:
    - 노출된 시크릿: 키 폐기 + git 히스토리 정리 + `.gitignore`/`EXCLUDES` 업데이트
    - 악성 설정 전파: 악성 커밋 revert + 동기화 대상 파일 화이트리스트(`CLAUDE_INCLUDES`) 검토
    - 동기화 로직 버그: `sync-timestamps.py` 수정 + 수동 테스트 확인
  5.2. 수정 사항을 모든 동기화 대상 기기에 배포하라 (`sync.sh`의 `git pull --rebase`로 자동 반영됨을 확인).

  **6. 복구 (Recovery)**

  6.1. 봉쇄 해제: cron job을 재활성화하고 remote URL을 복원하라.
  6.2. 검증: `bash sync.sh`를 수동 실행하여 정상 동기화를 확인하라.
  6.3. 모니터링 강화: 인시던트 후 1주간 매일 `git log`와 `sync.sh` 로그를 검토하라.

  **7. 사후 분석 (Post-Mortem)**

  7.1. 인시던트 종료 후 48시간 이내에 아래 항목을 기록하라:
    - 타임라인: 발생 시각, 탐지 시각, 대응 시작 시각, 봉쇄 완료 시각, 복구 완료 시각
    - 근본 원인 (Root Cause): 인시던트가 발생한 기술적/프로세스적 원인
    - 영향 범위: 영향받은 기기, 파일, 서비스
    - 대응 효과성: 플레이북 절차 중 잘 작동한 부분과 개선이 필요한 부분
    - 재발 방지 조치: 구체적 조치 항목 + 완료 기한 + 담당자 (1인 개발자이므로 본인)
  7.2. 사후 분석 문서를 `docs/incidents/YYYY-MM-DD-제목.md`에 저장하라.
  7.3. 재발 방지 조치 중 이 플레이북에 반영할 사항이 있으면 플레이북을 업데이트하라.

  **8. 커뮤니케이션 계획**

  8.1. 1인 개발자 환경이므로 외부 커뮤니케이션은 다음 경우에만 필요하다:
    - API 키 노출로 인해 서비스 제공자에 키 폐기를 요청하는 경우
    - public repo에 시크릿이 노출되어 GitHub Support에 캐시 삭제를 요청하는 경우
    - 노출된 키를 통해 제3자 데이터가 영향받은 경우 (해당 제3자에게 통보)
  8.2. 커뮤니케이션 템플릿:

  ```
  [서비스 제공자]에게:
  제목: API 키 노출 - 즉시 폐기 요청
  본문:
  - 노출된 키 식별자: [키 ID 또는 접두사]
  - 노출 경로: [public git repository / 기타]
  - 노출 시점 (추정): [YYYY-MM-DD HH:MM UTC]
  - 조치 완료 사항: 키 폐기 완료, git 히스토리 정리 완료
  - 요청 사항: [비인가 사용 이력 확인 / 캐시 삭제 / 기타]
  ```

  **9. 도구 및 명령어 참조**

  | 용도 | 명령어 |
  |---|---|
  | 동기화 중단 | `crontab -e` 후 sync.sh 라인 주석 처리 |
  | git 히스토리에서 파일 제거 | `git filter-repo --path <파일경로> --invert-paths` |
  | 최근 변경 확인 | `git log --oneline -20 --all` |
  | 특정 커밋의 변경 확인 | `git show <commit_hash>` |
  | 안전한 커밋으로 롤백 | `git revert <악성_커밋>` |
  | 동기화 수동 실행 | `bash sync.sh` |
  | 타임스탬프 디버깅 | `python3 sync-timestamps.py . $(hostname -s)` |
  | cron job 상태 확인 | `crontab -l` |
  | 증거 보존 브랜치 생성 | `git checkout -b incident-evidence-$(date +%Y%m%d)` |

- **Exceptions**: 이 플레이북의 절차를 건너뛰어야 하는 경우, 사후 분석 문서에 건너뛴 단계와 사유를 반드시 기록하라. SEV-1의 "키 즉시 폐기" 단계는 어떤 경우에도 건너뛸 수 없다.
- **Review cycle**: 6개월 (매년 1월, 7월). 인시던트 발생 시 사후 분석 완료 후 즉시 추가 검토.
- **Effective date**: 2026-03-26
