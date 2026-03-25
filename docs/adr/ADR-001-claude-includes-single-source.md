# ADR-001: CLAUDE_INCLUDES 단일 소스화 방안

- Status: ACCEPTED
- Date: 2026-03-25
- Context: ARCH-001 (audit-report P2)

## 문제

CLAUDE_INCLUDES 목록이 3곳에 하드코딩되어 있다:
1. sync-timestamps.py L27-30 (Python set)
2. setup.sh L75 (Bash for loop)
3. setup-windows.sh L17 (Bash for loop)

항목 추가/제거 시 3곳을 동시에 수정해야 하며, 불일치 시 setup에서 복원한 파일이 sync에서 무시되거나 그 반대가 발생한다.

## 결정

sync-timestamps.py에 `--list-includes` 서브커맨드를 추가한다. Bash 스크립트는 이 커맨드의 stdout 출력을 사용한다.

## 비교 옵션

| 옵션 | 가중 총점 | 비고 |
|------|----------|------|
| A: sync-config.json | 3.45 | Bash에서 JSON 파싱에 jq 필요 (외부 의존성 금지) |
| B: Python export + eval | 2.30 | eval 보안 리스크, 모듈 구조 변경 과대 |
| **C: --list-includes 커맨드** | **4.45** | 채택 |

## 결과

- sync-timestamps.py가 CLAUDE_INCLUDES의 유일한 정의 소스
- Bash 스크립트는 `$($PYTHON_CMD sync-timestamps.py --list-includes)` 로 동적 참조
- fallback 하드코딩을 Bash에 유지하여 Python 실행 실패 시 방어
- 영향 파일: sync-timestamps.py, setup.sh, setup-windows.sh (3개)
