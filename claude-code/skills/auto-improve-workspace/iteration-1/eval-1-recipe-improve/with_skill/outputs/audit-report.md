# Audit Report: Recipick (Recipe SNS)

## 프로젝트 개요

- **스택**: FastAPI (Python 3.14) + React 18 (TypeScript) + PostgreSQL 16
- **아키텍처**: 3-tier SPA → REST API → PostgreSQL (SQLAlchemy async)
- **규모**: 백엔드 30개 소스 파일, 프런트엔드 25개 소스 파일, 테스트 19건
- **기능**: JWT 인증, 레시피 CRUD, 좋아요/댓글/북마크, 팔로우, 피드(팔로우+인기), 검색

## 베이스라인 점수

| 영역 | 점수 (0~10) |
|------|------------|
| Code Quality | 5 |
| Security | 4 |
| Architecture | 6 |
| Test Coverage | 5 |
| UX/UI | 5 |

## 개선 항목 (우선순위별)

### P0 (Critical) - 즉시 수정 필수

| # | 영역 | 파일 | 문제 | 영향 |
|---|------|------|------|------|
| 1 | Code Quality | `services/feed.py` | `_to_list_items()`에서 레시피당 Like, Bookmark SELECT 2회 → N+1 | 피드 20건 로드 시 40+개 추가 쿼리 |
| 2 | Code Quality | `services/social.py` | `get_comments()`에서 댓글당 User SELECT → N+1 | 댓글 20건 로드 시 20개 추가 쿼리 |
| 3 | Code Quality | `services/social.py` | `get_followers()`/`get_following()`에서 팔로우당 User SELECT → N+1 | 목록 20건 시 20개 추가 쿼리 |
| 4 | Code Quality | `services/feed.py` 외 | UUID 기반 cursor 페이지네이션: UUID는 순차 정렬 불가, `< uuid.UUID(cursor)` 비교 무의미 | 페이지네이션 작동 불량, 데이터 누락/중복 |
| 5 | Code Quality | `pages/RecipeDetailPage.tsx:46` | FollowButton에 `recipe.is_liked` 전달 → 팔로우 상태가 아닌 좋아요 상태로 초기화 | 팔로우 버튼 상태 표시 오류 |

### P1 (High) - 기능/보안에 직접 영향

| # | 영역 | 파일 | 문제 |
|---|------|------|------|
| 6 | Security | `schemas/auth.py` | 비밀번호 최소 길이/복잡성 검증 없음 |
| 7 | Security | `schemas/recipe.py` | ingredients/steps/tags 리스트 최대 길이 제한 없음 |
| 8 | UX/UI | `pages/SearchPage.tsx` | 카테고리 칩 클릭 시 자동 검색 안 됨 |
| 9 | Code Quality | 프런트엔드 전체 | API 에러를 console.error로만 처리, 사용자 피드백 없음 |
| 10 | Code Quality | `services/feed.py:112` | ILIKE `%{q}%`에서 사용자 입력의 `%`, `_` 와일드카드 미이스케이프 |

### P2 (Medium) - 인프라/유지보수

| # | 영역 | 파일 | 문제 |
|---|------|------|------|
| 11 | Architecture | 프로젝트 루트 | .gitignore 파일 없음 |
| 12 | Architecture | backend/ | Alembic 마이그레이션 디렉토리/파일 없음 |
| 13 | Architecture | `app/main.py` | /health 엔드포인트가 DB 연결 확인 안 함 |
| 14 | Test | backend/tests/ | 사용자 프로필, 에러 케이스, 페이지네이션 테스트 부재 |

### P3 (Low) - 품질 향상

| # | 영역 | 파일 | 문제 |
|---|------|------|------|
| 15 | UX/UI | 프런트엔드 전체 | 로딩 상태에 스피너/스켈레톤 없음 |
| 16 | Security | `app/main.py` | CORS allow_methods/allow_headers 와일드카드 |
| 17 | Architecture | backend/ | 구조화된 로깅 없음 |

## 개선 범위 결정

**이번 라운드 개선 대상**: P0 전체 (5건) + P1 전체 (5건) + P2 부분 (3건: .gitignore, 헬스체크, 테스트 추가)

**제외**: Alembic 마이그레이션 (별도 작업), Rate limiting (인프라 의존), 로딩 UI 개선 (P3)

**총 개선 항목 수**: 13건
