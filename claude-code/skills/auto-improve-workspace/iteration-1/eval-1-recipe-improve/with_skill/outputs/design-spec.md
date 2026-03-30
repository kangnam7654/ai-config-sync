# Design Spec: Recipick Improvement

## 목적

Audit Report에서 식별된 P0~P2 13건의 개선 항목을 구현하여 코드 품질, 보안, 아키텍처, 테스트 커버리지를 향상시킨다.

**완료 조건**: 19건 기존 테스트 전체 PASS + 신규 테스트 추가 + N+1 쿼리 제거 + 페이지네이션 정상 작동 + 프런트엔드 버그 수정

## 파일 변경 목록

### 백엔드

| 파일 | 변경 유형 | 내용 |
|------|----------|------|
| `backend/app/services/feed.py` | 수정 | N+1 쿼리 제거 (배치 조회), cursor 페이지네이션을 created_at 기반으로 변경, ILIKE 와일드카드 이스케이프 |
| `backend/app/services/social.py` | 수정 | get_comments N+1 제거 (joinedload), get_followers/get_following N+1 제거 (joinedload), cursor 페이지네이션 수정 |
| `backend/app/services/recipe.py` | 수정 | get_recipe_detail의 Like/Bookmark 조회 최적화 |
| `backend/app/schemas/auth.py` | 수정 | 비밀번호 최소 8자 검증 추가 |
| `backend/app/schemas/recipe.py` | 수정 | ingredients max 50, steps max 30, tags max 20 제한 추가 |
| `backend/app/main.py` | 수정 | /health 엔드포인트 DB 연결 확인 추가 |
| `backend/app/routers/social.py` | 수정 | list_comments 반환 타입 수정 (next_cursor 포함) |
| `backend/app/schemas/social.py` | 수정 | PaginatedComments 스키마 추가 |
| `backend/tests/test_user_profile.py` | 생성 | 사용자 프로필 테스트 |
| `backend/tests/test_edge_cases.py` | 생성 | 에러 케이스 테스트 (권한 없는 수정/삭제, 잘못된 입력 등) |

### 프런트엔드

| 파일 | 변경 유형 | 내용 |
|------|----------|------|
| `frontend/src/pages/RecipeDetailPage.tsx` | 수정 | FollowButton initialFollowing 버그 수정 |
| `frontend/src/pages/SearchPage.tsx` | 수정 | 카테고리 칩 클릭 시 자동 검색 |

### 인프라

| 파일 | 변경 유형 | 내용 |
|------|----------|------|
| `.gitignore` | 생성 | Python, Node.js, IDE 패턴 추가 |

## 구현 순서

### Step 1: N+1 쿼리 제거 (P0 #1~#3)

**대상 파일**: `backend/app/services/feed.py`, `backend/app/services/social.py`

1-A. `feed.py::_to_list_items()`: 레시피 ID 목록으로 Like/Bookmark를 한 번에 조회하는 배치 쿼리로 교체
1-B. `social.py::get_comments()`: Comment 조회 시 `selectinload(Comment.user)` 적용. Comment 모델에 user relationship 이미 존재.
1-C. `social.py::get_followers()`, `get_following()`: Follow 조회 후 user ID 목록으로 User를 한 번에 조회

### Step 2: Cursor 페이지네이션 수정 (P0 #4)

**대상 파일**: `backend/app/services/feed.py`, `backend/app/services/social.py`

- cursor를 `created_at` ISO 타임스탬프 기반으로 변경
- `created_at < cursor_datetime` 조건으로 페이지네이션
- next_cursor는 마지막 항목의 `created_at` ISO 문자열

### Step 3: FollowButton 버그 수정 (P0 #5)

**대상 파일**: `frontend/src/pages/RecipeDetailPage.tsx`

- line 46: `recipe.is_liked` → 별도 follow 상태 API 호출 또는 initialFollowing={false}로 변경 (follow 상태는 recipe detail에 포함되지 않으므로 기본값 false)

### Step 4: 입력 검증 강화 (P1 #6~#7)

**대상 파일**: `backend/app/schemas/auth.py`, `backend/app/schemas/recipe.py`

- RegisterRequest.password: `min_length=8` 추가
- RecipeCreateRequest.ingredients: `max_length=50` 제한
- RecipeCreateRequest.steps: `max_length=30` 제한
- RecipeCreateRequest.tags: `max_length=20` 제한
- RecipeCreateRequest.title: `min_length=1, max_length=200`

### Step 5: 검색 개선 (P1 #8, #10)

**대상 파일**: `frontend/src/pages/SearchPage.tsx`, `backend/app/services/feed.py`

- SearchPage: 카테고리 변경 시 useEffect로 자동 검색 트리거
- feed.py::search_recipes(): `%`와 `_` 문자 이스케이프 처리

### Step 6: 헬스체크 + .gitignore (P2)

**대상 파일**: `backend/app/main.py`, `.gitignore`

- /health 엔드포인트에서 `SELECT 1` 실행하여 DB 연결 확인
- .gitignore 생성

### Step 7: 테스트 추가 (P2 #14)

**대상 파일**: 신규 테스트 파일

- test_user_profile.py: 프로필 조회, 프로필 수정 테스트
- test_edge_cases.py: 다른 사용자의 레시피 수정/삭제 시도, 존재하지 않는 리소스 접근

## 함수/API 시그니처

### feed.py 변경

```python
# 기존 (삭제)
async def _to_list_items(db, recipes, current_user_id=None) -> list[RecipeListItem]:
    # 레시피마다 개별 Like/Bookmark 조회 (N+1)

# 변경 후
async def _to_list_items(db: AsyncSession, recipes: list[Recipe], current_user_id: uuid.UUID | None = None) -> list[RecipeListItem]:
    # 배치로 liked_ids, bookmarked_ids를 한 번에 조회
```

### social.py 변경

```python
# get_comments: Comment 조회 시 user를 joinedload
# get_followers/get_following: Follow 조회 후 user_ids로 배치 조회

# cursor 파라미터 타입은 str (ISO datetime) 유지, 내부에서 datetime 파싱
```

### schemas/auth.py 변경

```python
class RegisterRequest(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=8)
    display_name: str = Field(..., min_length=1, max_length=100)
```

### schemas/recipe.py 변경

```python
class RecipeCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    # ...
    ingredients: list[IngredientInput] = Field(..., max_length=50)
    steps: list[StepInput] = Field(..., max_length=30)
    tags: list[str] = Field(default=[], max_length=20)
```

## 제약 조건

1. 기존 19건 테스트가 모두 통과해야 한다 (회귀 테스트).
2. API 응답 스키마의 하위호환성을 유지한다. 기존 필드를 삭제하거나 타입을 변경하지 않는다.
3. cursor 형식 변경은 하위호환 불가하므로, 새 cursor가 UUID 형식이면 기존 방식으로 폴백한다.
4. 프런트엔드 변경은 기존 동작을 깨뜨리지 않는다.

## 의사결정

| 결정 | 채택 | 기각 대안 | 기각 이유 |
|------|------|----------|----------|
| N+1 해결 방식 | 배치 조회 (IN 절) | DataLoader 패턴 | 현재 규모에 과도한 추상화 |
| Cursor 형식 | created_at ISO 문자열 | offset 기반 | 대용량 데이터에서 offset 성능 저하 |
| Follow 상태 해결 | 기본값 false + 별도 API 불필요 | recipe detail에 follow 상태 추가 | API 스키마 변경 범위 최소화 |
