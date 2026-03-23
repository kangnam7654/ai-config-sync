import { test, expect } from '@playwright/test';

/**
 * 대시보드 E2E 테스트
 *
 * 전제조건: auth.setup.ts에서 로그인이 완료되어
 * storageState가 .auth/user.json에 저장된 상태.
 * playwright.config.ts의 dependencies 설정으로 자동 보장됨.
 */

test.describe('대시보드 접근 및 기본 기능', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/dashboard');
  });

  test('로그인된 사용자가 대시보드에 접근할 수 있다', async ({ page }) => {
    // URL 확인
    await expect(page).toHaveURL(/.*\/dashboard/);

    // 대시보드 주요 요소가 렌더링되었는지 확인
    await expect(page.getByRole('heading', { name: /대시보드|Dashboard/i })).toBeVisible();
  });

  test('대시보드에 사용자 정보가 표시된다', async ({ page }) => {
    // 사용자 이름 또는 아바타가 네비게이션에 표시되는지 확인
    const userInfo = page.locator('[data-testid="user-info"], .user-profile, nav .username');
    await expect(userInfo).toBeVisible({ timeout: 10_000 });
  });

  test('대시보드 네비게이션 메뉴가 정상 작동한다', async ({ page }) => {
    // 주요 네비게이션 항목이 존재하는지 확인
    const nav = page.getByRole('navigation');
    await expect(nav).toBeVisible();

    // 네비게이션 링크 클릭 시 해당 페이지로 이동하는지 확인
    const settingsLink = nav.getByRole('link', { name: /설정|Settings/i });
    if (await settingsLink.isVisible()) {
      await settingsLink.click();
      await expect(page).toHaveURL(/.*\/settings/);

      // 뒤로 돌아가기
      await page.goto('/dashboard');
      await expect(page).toHaveURL(/.*\/dashboard/);
    }
  });

  test('대시보드 데이터가 로드된다', async ({ page }) => {
    // API 응답을 기다린다
    const responsePromise = page.waitForResponse(
      (response) =>
        response.url().includes('/api/') &&
        response.status() === 200,
      { timeout: 15_000 }
    );

    // 페이지 새로고침으로 API 호출 트리거
    await page.reload();
    const response = await responsePromise;

    expect(response.status()).toBe(200);

    // 로딩 스피너가 사라지고 콘텐츠가 표시되는지 확인
    const loadingSpinner = page.locator('[data-testid="loading"], .loading-spinner, .skeleton');
    if (await loadingSpinner.isVisible({ timeout: 1_000 }).catch(() => false)) {
      await expect(loadingSpinner).toBeHidden({ timeout: 15_000 });
    }
  });
});

test.describe('인증되지 않은 사용자 접근 제어', () => {
  // 이 describe 블록은 storageState를 사용하지 않는다
  test.use({ storageState: { cookies: [], origins: [] } });

  test('미인증 사용자가 대시보드 접근 시 로그인 페이지로 리다이렉트된다', async ({ page }) => {
    await page.goto('/dashboard');

    // 로그인 페이지로 리다이렉트되어야 한다
    await expect(page).toHaveURL(/.*\/login/);
  });

  test('미인증 사용자가 보호된 API 호출 시 401을 받는다', async ({ page }) => {
    const response = await page.request.get('/api/dashboard/data');
    expect(response.status()).toBe(401);
  });
});

test.describe('로그아웃 기능', () => {
  test('로그아웃 버튼 클릭 시 로그인 페이지로 이동한다', async ({ page }) => {
    await page.goto('/dashboard');

    // 로그아웃 버튼을 찾아 클릭
    // 유저 메뉴 드롭다운을 열어야 할 수 있음
    const userMenu = page.locator('[data-testid="user-menu"], .user-menu, .avatar-button');
    if (await userMenu.isVisible({ timeout: 3_000 }).catch(() => false)) {
      await userMenu.click();
    }

    const logoutButton = page.getByRole('button', { name: /로그아웃|Logout|Sign Out|Log out/i });
    await expect(logoutButton).toBeVisible();
    await logoutButton.click();

    // 로그인 페이지로 이동되어야 한다
    await expect(page).toHaveURL(/.*\/login/, { timeout: 10_000 });
  });
});
