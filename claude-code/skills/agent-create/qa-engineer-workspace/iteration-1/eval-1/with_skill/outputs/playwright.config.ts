import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright 설정 파일
 * - localhost:3000에서 실행되는 웹앱 대상
 * - 로그인 → 대시보드 접근 E2E 테스트용
 */
export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: false, // 로그인 상태 의존성이 있으므로 순차 실행
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: 1,
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['list'],
  ],
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    actionTimeout: 10_000,
    navigationTimeout: 15_000,
  },

  projects: [
    // 인증 상태를 생성하는 setup 프로젝트
    {
      name: 'setup',
      testMatch: /.*\.setup\.ts/,
    },
    // 인증 상태를 사용하는 메인 테스트
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        storageState: 'tests/e2e/.auth/user.json',
      },
      dependencies: ['setup'],
    },
    {
      name: 'firefox',
      use: {
        ...devices['Desktop Firefox'],
        storageState: 'tests/e2e/.auth/user.json',
      },
      dependencies: ['setup'],
    },
    {
      name: 'webkit',
      use: {
        ...devices['Desktop Safari'],
        storageState: 'tests/e2e/.auth/user.json',
      },
      dependencies: ['setup'],
    },
  ],
});
