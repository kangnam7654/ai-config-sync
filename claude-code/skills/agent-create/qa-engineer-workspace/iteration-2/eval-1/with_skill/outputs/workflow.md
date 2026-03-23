# Playwright E2E 테스트 워크플로우

## 1. 환경 설정

### 1.1 Playwright 설치

```bash
# 프로젝트 루트에서 실행
npm init -y  # package.json이 없는 경우
npm install -D @playwright/test
npx playwright install  # 브라우저 바이너리(Chromium, Firefox, WebKit) 다운로드
```

### 1.2 디렉토리 구조

```
ai-config-sync/
├── playwright.config.ts       # Playwright 설정 (baseURL, 프로젝트, webServer)
├── tests/
│   └── e2e/
│       ├── .auth/
│       │   └── user.json      # 인증 상태 저장 (자동 생성, .gitignore에 추가)
│       ├── auth.setup.ts      # 인증 Setup 스크립트
│       └── dashboard.spec.ts  # 대시보드 E2E 테스트
├── package.json
└── .gitignore                 # tests/e2e/.auth/ 추가 필요
```

### 1.3 .gitignore 추가

```
# Playwright
tests/e2e/.auth/
test-results/
playwright-report/
```

### 1.4 환경변수 설정

테스트 계정 자격 증명을 환경변수로 관리:

```bash
# .env.test (로컬)
TEST_USERNAME=testuser@example.com
TEST_PASSWORD=Test1234!

# CI 환경에서는 시크릿으로 설정
# GitHub Actions: Settings > Secrets > TEST_USERNAME, TEST_PASSWORD
```

## 2. 테스트 실행

### 2.1 전체 테스트 실행

```bash
npx playwright test
```

### 2.2 특정 파일만 실행

```bash
npx playwright test tests/e2e/dashboard.spec.ts
```

### 2.3 특정 브라우저만 실행

```bash
npx playwright test --project=chromium
```

### 2.4 디버그 모드 (브라우저 UI 표시)

```bash
npx playwright test --headed --debug
```

### 2.5 UI 모드 (인터랙티브)

```bash
npx playwright test --ui
```

## 3. 테스트 구조 설명

### 3.1 인증 흐름 (auth.setup.ts)

```
[auth-setup 프로젝트]
    │
    ├─ /login 페이지 접근
    ├─ 이메일/비밀번호 입력
    ├─ 로그인 버튼 클릭
    ├─ /dashboard 리다이렉트 확인
    └─ storageState → tests/e2e/.auth/user.json 저장
         │
         ▼
[chromium/firefox/webkit 프로젝트]
    │ (storageState 재사용 → 로그인 불필요)
    ├─ dashboard.spec.ts 실행
    └─ 기타 인증 필요 테스트 실행
```

- `auth-setup`은 독립 프로젝트로 정의되어 다른 프로젝트의 `dependencies`로 참조됨
- 로그인은 전체 테스트 스위트에서 1번만 수행되고, 쿠키/세션이 파일로 저장됨
- 각 브라우저 프로젝트는 저장된 상태를 로드하여 즉시 인증된 상태로 시작

### 3.2 대시보드 테스트 (dashboard.spec.ts)

| describe 블록 | 테스트 | 검증 내용 |
|---|---|---|
| 인증된 사용자 | 페이지 렌더링 | 타이틀, 헤딩, 사용자 정보 영역 표시 |
| 인증된 사용자 | 핵심 위젯 표시 | 메인 컨텐츠 영역과 위젯/카드 렌더링 |
| 인증된 사용자 | 데이터 로딩 | 로딩 → 데이터 표시 (또는 빈 상태) 전환 |
| 인증된 사용자 | 네비게이션 동작 | 메뉴 링크 클릭 시 페이지 전환 |
| 인증된 사용자 | 로그아웃 흐름 | 로그아웃 후 로그인 페이지 리다이렉트 |
| 비인증 접근 | 대시보드 가드 | storageState 없이 접근 시 /login으로 리다이렉트 |
| 비인증 접근 | API 보호 | /api/dashboard 호출 시 401 반환 |
| 에러 처리 | API 500 에러 | 서버 에러 시 에러 메시지 UI 표시 |
| 에러 처리 | 네트워크 오류 | 오프라인 시 안내 메시지 표시 |

### 3.3 핵심 설계 결정

1. **storageState 패턴**: 로그인을 setup 프로젝트로 분리하여 테스트 속도를 최적화. 모든 테스트가 인증을 반복하지 않음.
2. **다국어 선택자**: `getByRole` + 정규식(`/로그인|Sign in|Login/i`)으로 한/영 UI 모두 대응.
3. **유연한 선택자**: `getByTestId`를 1차로 사용하되, `getByRole`/`getByText`로 fallback하여 data-testid가 없는 앱에서도 동작.
4. **네트워크 모킹**: `page.route()`로 API 응답을 가로채 에러 시나리오를 안정적으로 재현.
5. **비인증 테스트**: `test.use({ storageState: { cookies: [], origins: [] } })`로 describe 블록 단위 인증 해제.

## 4. CI/CD 통합 (GitHub Actions 예시)

```yaml
name: Playwright E2E Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  e2e:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 20

      - name: Install dependencies
        run: npm ci

      - name: Install Playwright browsers
        run: npx playwright install --with-deps

      - name: Start application
        run: npm run dev &
        env:
          NODE_ENV: test

      - name: Wait for app to be ready
        run: npx wait-on http://localhost:3000 --timeout 60000

      - name: Run Playwright tests
        run: npx playwright test
        env:
          TEST_USERNAME: ${{ secrets.TEST_USERNAME }}
          TEST_PASSWORD: ${{ secrets.TEST_PASSWORD }}

      - name: Upload test report
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: playwright-report
          path: playwright-report/
          retention-days: 7

      - name: Upload test results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-results
          path: test-results/
          retention-days: 7
```

## 5. 실행 전 체크리스트

- [ ] Node.js 18+ 설치 확인
- [ ] `npm install -D @playwright/test` 완료
- [ ] `npx playwright install` 완료 (브라우저 바이너리 다운로드)
- [ ] localhost:3000에서 웹앱 구동 확인
- [ ] 테스트 계정 생성 및 환경변수 설정
- [ ] `.gitignore`에 `tests/e2e/.auth/` 추가
- [ ] `npx playwright test --project=auth-setup` 으로 인증 setup만 먼저 검증
- [ ] `npx playwright test` 전체 실행

## 6. 트러블슈팅

| 증상 | 원인 | 해결 |
|---|---|---|
| `browserType.launch: Executable doesn't exist` | 브라우저 미설치 | `npx playwright install` |
| auth.setup 타임아웃 | 로그인 폼 선택자 불일치 | `--debug` 모드로 실제 DOM 확인 후 선택자 수정 |
| storageState 파일 없음 | auth-setup 실패 | auth.setup.ts를 단독 실행하여 디버깅 |
| 비인증 테스트에서 대시보드 접근 성공 | 인증 가드 미구현 | 앱 측 미들웨어/라우트 가드 확인 |
| CI에서만 실패 | 화면 크기/폰트 차이 | `devices` 설정 확인, 스크린샷 비교 |
