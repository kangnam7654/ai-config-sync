---
name: ai-config-sync architecture health baseline
description: Architecture health of ai-config-sync (Python+Bash config sync), 5-domain composite 5.045/10, arch-spec drafted for P0-P2 (16 items), as of 2026-03-25
type: project
---

ai-config-sync: Python3+Bash 설정 파일 동기화 도구 (Ubuntu/Mac/Windows). Git을 전송 계층으로 사용, newest-wins 병합. 크론 30분 주기.

**Why:** 5개 진단(코드 품질/보안/아키텍처/테스트/Repo Health) 종합 분석으로 개선 우선순위 수립. PARTIAL 판정 -- P0+P1+P2 해소 시 8.0 달성 가능.

**How to apply:** 이 프로젝트 변경 시 아래 점수표와 arch-spec를 참조. docs/llm/arch-spec.md에 구현 순서와 함수 시그니처 상세 기술됨.

## Composite Scores (2026-03-25)
- 가중 총점: 5.045/10 (FAIL -- target 8.0)
- 코드 품질: 5.4 (w=0.25)
- 보안: 7.0 (w=0.20)
- 아키텍처: 6.85 (w=0.20)
- 테스트: 1.3 (w=0.25, PRIMARY -- target 7.0 FAIL)
- Repo Health: 6.0 (w=0.10)

## Architecture Decisions (2026-03-25)
- ADR-001: CLAUDE_INCLUDES 단일소스화 -- Python --list-includes 커맨드 (scored 4.45 vs 3.45/2.30)
- ADR-002: main() 분리 -- 4개 함수 추출 (load_timestamps, load_peer_timestamps, sync_section, save_timestamps)
- ADR-003: 테스트 인프라 -- pytest+pytest-cov dev dep, monkeypatch git_cmd/git_bytes, tmp_path 실제 I/O, CI paths filter

## Implementation Plan
- 5 phases, 의존관계 기반
- Phase 1: infra (pyproject.toml, __pycache__ rm, type annotations)
- Phase 2: validation functions + unit tests (SEC-001/002/004, CODE-001/002/004)
- Phase 3: main() split (CODE-005) -- HIGH risk, requires Phase 2 tests first
- Phase 4: Bash scripts (ARCH-001, CODE-003, SEC-003/005, CODE-006)
- Phase 5: CI + final verification

## Key Files
- docs/llm/arch-spec.md: 전체 아키텍처 설계서
- docs/llm/audit-report.md: 감사 보고서
- docs/adr/ADR-001~003: 기술 결정 기록
- docs/arch-dependency-graph.mmd: 구현 의존관계 그래프
- docs/arch-data-flow.mmd: 리팩터링 후 데이터 흐름
