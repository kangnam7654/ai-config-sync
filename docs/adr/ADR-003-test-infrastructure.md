# ADR-003: 테스트 인프라 기술 선택

- Status: ACCEPTED
- Date: 2026-03-25
- Context: TEST-001, REPO-002 (audit-report P0, P2)

## 문제

테스트 커버리지 0%. 테스트 프레임워크, CI 모두 부재.

## 결정

- 프레임워크: pytest + pytest-cov (dev dependency-group, uv managed)
- Mock 전략: git_cmd/git_bytes 함수 레벨 monkeypatch. 파일시스템은 tmp_path로 실제 I/O.
- CI: GitHub Actions, 3 OS matrix (ubuntu/macos/windows), paths 필터로 sync 데이터 변경 시 미트리거

## 기각 대안

- unittest: tmp_path fixture 부재, monkeypatch 부재. 이 프로젝트의 Mock 전략에 pytest가 더 적합.
- subprocess.run 직접 Mock: git_cmd/git_bytes 래퍼가 이미 존재. 상위 레벨 Mock이 더 안정적이고 테스트 가독성 향상.
- CI paths 필터 없음: 30분마다 sync 커밋 발생. 필터 없으면 하루 48회 불필요한 CI 실행.

## 결과

- pyproject.toml에 dev dependency-group으로 pytest, pytest-cov 추가
- tests/ 디렉토리에 9개 테스트 모듈, 최소 53개 테스트 케이스
- 목표 커버리지 80% 이상
- .github/workflows/test.yml에 paths 필터 설정
