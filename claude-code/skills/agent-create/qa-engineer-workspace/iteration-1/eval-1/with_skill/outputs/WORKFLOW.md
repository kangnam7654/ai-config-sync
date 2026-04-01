# Playwright E2E 테스트 워크플로우

## 1. 목표

localhost:3000에서 동작하는 웹앱의 **로그인 -> 대시보드 접근** 플로우를 Playwright로 E2E 테스트한다.

## 2. 설계 결정

### 2.1 인증 전략: Project Dependencies 패턴

Playwright의 `setup` 프로젝트를 활용하여 인증 상태를 `storageState`로 파일에 저장하고, 이후 테스트에서 재사용한다. 이 패턴을 선택한 이유:

- **테스트 격리**: 각 테스트가 독립적으로 인증 상태를 소비
- **실행 속도**: 로그인을 1회만 수행하고 모든 테스트에서 재사용
- **Playwright 공식 권장 패턴** (https://playwright.dev/docs/auth)

기각한 대안:
- `globalSetup`으로 로그인: 브라우저 컨텍스트를 직접 관리해야 하고, 디버깅이 어려움
- 매 테스트마다 로그인: 느리고 불필요한 중복

### 2.2 파일 구조

```
outputs/
├── package.json              # 프로젝트 설정 및 npm scripts
├── playwright.config.ts       # Playwright 설정 (baseURL, projects, reporters)
├── .env.example               # 테스트 환경 변수 템플릿
├── .gitignore                 # 인증 파일, 리포트, 결과물 제외
├── WORKFLOW.md                # 이 문서
└── tests/
    └── e2e/
        ├── auth.setup.ts      # 인증 setup (로그인 -> storageState 저장)
        ├── login.spec.ts      # 로그인 페이지 테스트 (비인증 상태)
        └── dashboard.spec.ts  # 대시보드 테스트 (인증 상태 사용)
```

### 2.3 테스트 분류

| 파일 | 인증 상태 | 테스트 수 | 검증 항목 |
|------|-----------|-----------|-----------|
| auth.setup.ts | 직접 로그인 | 1 | 로그인 -> storageState 저장 |
| login.spec.ts | 비인증 (빈 storageState) | 6 | 폼 렌더링, 유효성 검사, 성공/실패 로그인, 비밀번호 마스킹, rate limit |
| dashboard.spec.ts | 인증 (storageState 사용) | 6 | 대시보드 접근, 사용자 정보, 네비게이션, 데이터 로드, 미인증 접근 차단, 로그아웃 |

## 3. 설치 및 실행 워크플로우

### 3.1 사전 준비

```bash
# Node.js 18+ 필요
node --version

# 프로젝트 디렉토리로 이동
cd outputs/
```

### 3.2 설치

```bash
# 1. 의존성 설치
npm install

# 2. Playwright 브라우저 설치
npx playwright install --with-deps
```

### 3.3 환경 변수 설정

```bash
# .env.example을 복사하여 .env 생성
cp .env.example .env

# .env 파일을 편집하여 실제 테스트 계정 정보 입력
# TEST_USERNAME=testuser@example.com
# TEST_PASSWORD=TestPassword123!
```

### 3.4 테스트 실행

```bash
# 전체 테스트 실행 (3개 브라우저: Chromium, Firefox, WebKit)
npm run test:e2e

# 특정 브라우저만 실행
npm run test:e2e:chromium

# UI 모드 (브라우저에서 테스트 과정 시각화)
npm run test:e2e:ui

# 디버그 모드 (step-by-step 실행)
npm run test:e2e:debug

# headed 모드 (브라우저 창 표시)
npm run test:e2e:headed
```

### 3.5 리포트 확인

```bash
# HTML 리포트 확인
npm run test:e2e:report
```

## 4. 실행 순서 (Playwright 내부)

```
1. [setup] auth.setup.ts::authenticate
   ├── /login 페이지 이동
   ├── 이메일/비밀번호 입력
   ├── 로그인 버튼 클릭
   ├── /dashboard 리다이렉트 대기
   └── storageState → tests/e2e/.auth/user.json 저장

2. [chromium/firefox/webkit] login.spec.ts (storageState 사용 안 함)
   ├── 로그인 폼 렌더링 확인
   ├── 빈 폼 제출 유효성 검사
   ├── 올바른 자격 증명 로그인 성공
   ├── 잘못된 비밀번호 에러 표시
   ├── 존재하지 않는 계정 에러 표시
   ├── 비밀번호 마스킹 확인
   └── rate limit 보안 검증

3. [chromium/firefox/webkit] dashboard.spec.ts (storageState 사용)
   ├── 인증된 사용자 대시보드 접근
   ├── 사용자 정보 표시 확인
   ├── 네비게이션 메뉴 동작
   ├── 대시보드 데이터 로드 (API 응답 확인)
   ├── 미인증 사용자 접근 차단 (리다이렉트)
   ├── 미인증 API 호출 401 확인
   └── 로그아웃 기능
```

## 5. CI 통합 가이드

### GitHub Actions 예시

```yaml
name: E2E Tests
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - name: Install dependencies
        run: npm ci
      - name: Install Playwright browsers
        run: npx playwright install --with-deps
      - name: Run E2E tests
        run: npx playwright test
        env:
          TEST_USERNAME: ${{ secrets.TEST_USERNAME }}
          TEST_PASSWORD: ${{ secrets.TEST_PASSWORD }}
      - uses: actions/upload-artifact@v4
        if: ${{ !cancelled() }}
        with:
          name: playwright-report
          path: playwright-report/
          retention-days: 30
```

## 6. 트러블슈팅

| 문제 | 원인 | 해결 |
|------|------|------|
| 타임아웃 에러 | 앱이 localhost:3000에서 실행되지 않음 | 앱을 먼저 시작하거나, `playwright.config.ts`에 `webServer` 설정 추가 |
| 인증 실패 | 테스트 계정이 없음 | `.env` 파일에 유효한 계정 정보 설정 |
| storageState 에러 | `.auth/` 디렉토리 없음 | `mkdir -p tests/e2e/.auth` 실행 |
| 브라우저 미설치 | Playwright 브라우저 미다운로드 | `npx playwright install --with-deps` 실행 |

## 7. 확장 포인트

- **webServer 설정**: `playwright.config.ts`에 `webServer` 블록을 추가하면 테스트 실행 시 자동으로 앱을 시작/종료할 수 있다.
- **Page Object Model**: 테스트가 많아지면 `tests/e2e/pages/` 디렉토리에 POM 클래스를 추가하여 로케이터를 중앙 관리한다.
- **Visual regression**: `expect(page).toHaveScreenshot()` 을 활용하여 UI 회귀 감지를 추가할 수 있다.
