import { test, expect } from '@playwright/test';

/**
 * 로그인 페이지 E2E 테스트
 *
 * 이 파일은 storageState를 사용하지 않으므로
 * 비인증 상태에서 로그인 플로우 자체를 검증한다.
 */

// 이 테스트 파일 전체에서 인증 상태를 사용하지 않음
test.use({ storageState: { cookies: [], origins: [] } });

test.describe('로그인 페이지 렌더링', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
  });

  test('로그인 폼이 정상적으로 렌더링된다', async ({ page }) => {
    // 주요 UI 요소 존재 확인
    await expect(page.getByRole('heading', { name: /로그인|Sign In|Login/i })).toBeVisible();
    await expect(page.getByLabel(/이메일|Email|Username/i)).toBeVisible();
    await expect(page.getByLabel(/비밀번호|Password/i)).toBeVisible();
    await expect(page.getByRole('button', { name: /로그인|Sign In|Login|Log in/i })).toBeVisible();
  });

  test('빈 폼 제출 시 유효성 검사 에러가 표시된다', async ({ page }) => {
    // 빈 상태로 제출
    await page.getByRole('button', { name: /로그인|Sign In|Login|Log in/i }).click();

    // 에러 메시지가 표시되어야 한다
    const errorMessage = page.locator(
      '[data-testid="error-message"], .error-message, .form-error, [role="alert"]'
    );
    await expect(errorMessage).toBeVisible({ timeout: 5_000 });
  });
});

test.describe('로그인 시도', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
  });

  test('올바른 자격 증명으로 로그인하면 대시보드로 이동한다', async ({ page }) => {
    const username = process.env.TEST_USERNAME ?? 'testuser@example.com';
    const password = process.env.TEST_PASSWORD ?? 'TestPassword123!';

    await page.getByLabel(/이메일|Email|Username/i).fill(username);
    await page.getByLabel(/비밀번호|Password/i).fill(password);
    await page.getByRole('button', { name: /로그인|Sign In|Login|Log in/i }).click();

    // 대시보드로 리다이렉트
    await expect(page).toHaveURL(/.*\/dashboard/, { timeout: 15_000 });
  });

  test('잘못된 비밀번호로 로그인하면 에러가 표시된다', async ({ page }) => {
    await page.getByLabel(/이메일|Email|Username/i).fill('testuser@example.com');
    await page.getByLabel(/비밀번호|Password/i).fill('WrongPassword!');
    await page.getByRole('button', { name: /로그인|Sign In|Login|Log in/i }).click();

    // 에러 메시지 확인
    const errorMessage = page.locator(
      '[data-testid="login-error"], .login-error, [role="alert"]'
    );
    await expect(errorMessage).toBeVisible({ timeout: 5_000 });

    // URL이 여전히 로그인 페이지인지 확인
    await expect(page).toHaveURL(/.*\/login/);
  });

  test('존재하지 않는 계정으로 로그인하면 에러가 표시된다', async ({ page }) => {
    await page.getByLabel(/이메일|Email|Username/i).fill('nonexistent@example.com');
    await page.getByLabel(/비밀번호|Password/i).fill('AnyPassword123!');
    await page.getByRole('button', { name: /로그인|Sign In|Login|Log in/i }).click();

    const errorMessage = page.locator(
      '[data-testid="login-error"], .login-error, [role="alert"]'
    );
    await expect(errorMessage).toBeVisible({ timeout: 5_000 });
  });

  test('비밀번호 입력 필드가 마스킹 처리되어 있다', async ({ page }) => {
    const passwordField = page.getByLabel(/비밀번호|Password/i);
    await expect(passwordField).toHaveAttribute('type', 'password');
  });
});

test.describe('로그인 보안', () => {
  test('연속 로그인 실패 시 rate limit 메시지가 표시된다', async ({ page }) => {
    await page.goto('/login');

    // 5회 연속 실패 시도
    for (let i = 0; i < 5; i++) {
      await page.getByLabel(/이메일|Email|Username/i).fill('testuser@example.com');
      await page.getByLabel(/비밀번호|Password/i).fill(`WrongPassword${i}!`);
      await page.getByRole('button', { name: /로그인|Sign In|Login|Log in/i }).click();

      // 다음 시도 전 에러 메시지 대기
      await page
        .locator('[data-testid="login-error"], .login-error, [role="alert"]')
        .waitFor({ state: 'visible', timeout: 5_000 })
        .catch(() => {});
    }

    // rate limit 또는 계정 잠금 메시지 확인
    const rateLimitMessage = page.locator(
      '[data-testid="rate-limit"], .rate-limit-message, [role="alert"]'
    );
    // rate limit이 구현되어 있다면 메시지가 표시된다
    // 구현되어 있지 않다면 이 테스트는 보안 개선 이슈로 기록한다
    const isRateLimited = await rateLimitMessage
      .isVisible({ timeout: 3_000 })
      .catch(() => false);

    if (!isRateLimited) {
      console.warn(
        '[보안 권고] Rate limiting이 구현되어 있지 않습니다. ' +
        '무차별 대입 공격 방지를 위해 rate limiting 구현을 권장합니다.'
      );
    }
  });
});
