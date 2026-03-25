---
name: ai-config-sync architecture health baseline
description: Architecture health of ai-config-sync (Python+Bash config sync), 5-domain composite 5.045/10, improvement plan P0-P3 with 24 items, as of 2026-03-25
type: project
---

ai-config-sync: Python3+Bash 설정 파일 동기화 도구 (Ubuntu/Mac/Windows). Git을 전송 계층으로 사용, newest-wins 병합. 크론 30분 주기.

**Why:** 5개 진단(코드 품질/보안/아키텍처/테스트/Repo Health) 종합 분석으로 개선 우선순위 수립. PARTIAL 판정 — 운영 중단 불필요하나 P0+P1 해소 필수.

**How to apply:** 이 프로젝트 변경 시 아래 점수표와 P0-P3 항목을 참조. P0 4건 최우선 해소 후 재진단.

## Composite Scores (2026-03-25)
- 가중 총점: 5.045/10 (FAIL — target 8.0)
- 코드 품질: 5.4 (w=0.25)
- 보안: 7.0 (w=0.20)
- 아키텍처: 6.85 (w=0.20)
- 테스트: 1.3 (w=0.25, PRIMARY — target 7.0 FAIL)
- Repo Health: 6.0 (w=0.10)

## Priority Items (24건)
- P0 (즉시, 4건): 테스트 인프라+핵심 테스트, bare except 제거, sys.argv 검증, hostname 검증
- P1 (1주, 5건): 경로 트래버설 차단, 크론 로그 권한, push 에러 핸들링, 타임스탬프 sanity, unlink 로깅
- P2 (2주, 7건): CLAUDE_INCLUDES 단일소스화, main() 분리, pycache 추적 제거, CI/CD, setup 중복 제거, 타입어노테이션, 토큰 임시파일
- P3 (백로그, 8건): Git LFS, 중첩 .git, walk 통합, TS pruning, find 가드, 커밋 경량화, set-e 정리, pre-commit

## Gate Decision
- PARTIAL: P0+P1 해소 후 재진단 필요. 예상 P0 1-2일, P1 2-3일.
- P0+P1 해소 후 예상: ~6.5-7.0. P2 완료 시 8.0 도달 가능.

## Strengths (유지)
- Bash(orchestration) / Python(merge) 계층 분리 명확
- newest-wins 병합 전략이 도메인에 적합
- 보안 설계 기본 양호 (whitelist, .gitignore, template)
- 크로스 플랫폼 일관성 (pathlib, encoding)
