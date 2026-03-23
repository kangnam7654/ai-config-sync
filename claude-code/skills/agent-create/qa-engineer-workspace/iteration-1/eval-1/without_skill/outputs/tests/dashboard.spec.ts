import { test, expect } from "@playwright/test";

test.describe("대시보드 접근 및 핵심 기능 검증", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/dashboard");
  });

  // ── 페이지 접근 및 렌더링 ──────────────────────────────────────

  test("인증된 사용자가 대시보드에 정상 접근할 수 있다", async ({ page }) => {
    await expect(page).toHaveURL(/\/dashboard/);
    await expect(page).toHaveTitle(/대시보드|Dashboard/i);
  });

  test("대시보드 헤더에 사용자 정보가 표시된다", async ({ page }) => {
    const userProfile = page.getByTestId("user-profile");
    await expect(userProfile).toBeVisible();
    await expect(userProfile).toContainText("test@example.com");
  });

  // ── 동기화 상태 위젯 ──────────────────────────────────────────

  test("동기화 상태 카드가 렌더링된다", async ({ page }) => {
    const syncStatusCard = page.getByTestId("sync-status-card");
    await expect(syncStatusCard).toBeVisible();

    // 마지막 동기화 시간이 표시되는지 확인
    const lastSyncTime = syncStatusCard.getByTestId("last-sync-time");
    await expect(lastSyncTime).toBeVisible();
    await expect(lastSyncTime).not.toHaveText("");
  });

  test("동기화 상태 카드에 연결된 기기 목록이 표시된다", async ({ page }) => {
    const deviceList = page.getByTestId("connected-devices");
    await expect(deviceList).toBeVisible();

    // 최소 1개 이상의 기기가 표시되어야 함
    const devices = deviceList.getByRole("listitem");
    await expect(devices).toHaveCount(1, { timeout: 5_000 });
  });

  // ── 파일 동기화 현황 테이블 ────────────────────────────────────

  test("파일 동기화 현황 테이블이 표시된다", async ({ page }) => {
    const fileTable = page.getByTestId("sync-files-table");
    await expect(fileTable).toBeVisible();

    // 테이블 헤더 검증
    const headers = fileTable.getByRole("columnheader");
    await expect(headers.nth(0)).toContainText(/파일명|File/i);
    await expect(headers.nth(1)).toContainText(/상태|Status/i);
    await expect(headers.nth(2)).toContainText(/최종 수정|Last Modified/i);
  });

  test("동기화 파일 목록에 섹션별 필터가 동작한다", async ({ page }) => {
    // workspace 필터 클릭
    const workspaceFilter = page.getByRole("button", { name: /workspace/i });
    await workspaceFilter.click();

    const fileTable = page.getByTestId("sync-files-table");
    const rows = fileTable.getByRole("row");
    // 헤더 행을 제외하고 최소 1개 행이 있어야 함
    expect(await rows.count()).toBeGreaterThan(1);

    // claude-code 필터 클릭
    const claudeFilter = page.getByRole("button", { name: /claude-code/i });
    await claudeFilter.click();

    // 필터 전환 후에도 테이블이 유지되는지 확인
    await expect(fileTable).toBeVisible();
  });

  // ── 네비게이션 ─────────────────────────────────────────────────

  test("사이드바 네비게이션이 정상 동작한다", async ({ page }) => {
    const sidebar = page.getByRole("navigation");
    await expect(sidebar).toBeVisible();

    // 설정 페이지로 이동
    await sidebar.getByRole("link", { name: /설정|Settings/i }).click();
    await expect(page).toHaveURL(/\/settings/);

    // 대시보드로 복귀
    await sidebar.getByRole("link", { name: /대시보드|Dashboard/i }).click();
    await expect(page).toHaveURL(/\/dashboard/);
  });

  // ── 로그아웃 ───────────────────────────────────────────────────

  test("로그아웃 후 로그인 페이지로 리다이렉트된다", async ({ page }) => {
    // 사용자 메뉴 열기
    const userMenu = page.getByTestId("user-menu-trigger");
    await userMenu.click();

    // 로그아웃 클릭
    await page.getByRole("menuitem", { name: /로그아웃|Logout/i }).click();

    // 로그인 페이지로 리다이렉트 확인
    await expect(page).toHaveURL(/\/login/);

    // 대시보드 직접 접근 시 로그인 페이지로 리다이렉트되는지 확인
    await page.goto("/dashboard");
    await expect(page).toHaveURL(/\/login/);
  });
});

test.describe("미인증 사용자 접근 제어", () => {
  // 이 describe 블록은 storageState를 비워서 미인증 상태로 테스트
  test.use({ storageState: { cookies: [], origins: [] } });

  test("미인증 사용자가 대시보드 접근 시 로그인 페이지로 리다이렉트된다", async ({
    page,
  }) => {
    await page.goto("/dashboard");
    await expect(page).toHaveURL(/\/login/);
  });

  test("미인증 사용자가 설정 페이지 접근 시 로그인 페이지로 리다이렉트된다", async ({
    page,
  }) => {
    await page.goto("/settings");
    await expect(page).toHaveURL(/\/login/);
  });
});
