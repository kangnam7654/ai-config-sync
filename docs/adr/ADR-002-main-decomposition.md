# ADR-002: main() 함수 분리 전략

- Status: ACCEPTED
- Date: 2026-03-25
- Context: CODE-005 (audit-report P2)

## 문제

main()이 140행 모놀리스로, 타임스탬프 로드/피어 감지/섹션별 병합/저장이 한 함수에 집중. 테스트 불가, 중첩 5단계.

## 결정

4개 함수로 추출한다: `load_timestamps`, `load_peer_timestamps`, `sync_section`, `save_timestamps`. main()은 오케스트레이션만 담당하여 약 25행으로 축소.

## 기각 대안

- 클래스 기반 리팩터링: 메서드 수가 5개 이하이고 호출처가 1곳. 추상화 기준(메서드 2개 이하 시 클래스 금지)에 의해 기각.
- 별도 모듈 분리 (sync_lib.py): 프로젝트 내 파일 1곳에서만 호출. 모듈 분리 기준(1곳 호출 시 추출 금지)에 의해 기각.

## 결과

- sync-timestamps.py 단일 파일 내에서 함수 추출
- 각 함수는 독립 테스트 가능 (git_cmd/git_bytes Mock으로)
- main()은 의존성 주입 패턴 (함수 인수로 데이터 전달)
- 하위호환 리스크 HIGH: Phase 2 테스트 완비 후에만 Phase 3 진행
