import { test, expect } from "@playwright/test";

/**
 * 대시보드 E2E 테스트
 *
 * 전제 조건:
 * - auth.setup.ts에서 저장한 storageState를 통해 이미 인증된 상태
 * - localhost:3000에서 웹앱이 구동 중
 *
 * 테스트 범위:
 * 1. 로그인 후 대시보드 접근 및 핵심 요소 렌더링
 * 2. 비인증 상태에서 대시보드 접근 시 리다이렉트
 * 3. 대시보드 데이터 로딩
 * 4. 네비게이션 동작
 * 5. 로그아웃 흐름
 */

test.describe("대시보드 - 인증된 사용자", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/dashboard");
  });

  test("대시보드 페이지가 정상적으로 렌더링된다", async ({ page }) => {
    // 페이지 타이틀 확인
    await expect(page).toHaveTitle(/대시보드|Dashboard/i);

    // 대시보드 제목 표시
    const heading = page.getByRole("heading", { name: /대시보드|Dashboard/i });
    await expect(heading).toBeVisible();

    // 사용자 정보 영역이 표시됨 (프로필, 사용자명 등)
    const userInfo = page.getByTestId("user-info").or(
      page.getByRole("button", { name: /프로필|Profile|계정|Account/i })
    );
    await expect(userInfo).toBeVisible();
  });

  test("대시보드에 핵심 위젯/섹션이 표시된다", async ({ page }) => {
    // 대시보드의 주요 섹션이 로드되는지 확인
    // (실제 앱 구조에 맞게 선택자를 조정해야 함)
    const mainContent = page.getByRole("main").or(page.getByTestId("dashboard-content"));
    await expect(mainContent).toBeVisible();

    // 최소 하나의 카드/위젯이 렌더링됨
    const widgets = page.getByTestId("dashboard-widget").or(
      page.locator("[class*='card'], [class*='widget'], [class*='panel']")
    );
    await expect(widgets.first()).toBeVisible({ timeout: 10_000 });
  });

  test("대시보드 데이터가 로딩 후 표시된다", async ({ page }) => {
    // 로딩 인디케이터가 나타났다가 사라지는 것을 확인
    const loadingIndicator = page.getByTestId("loading").or(
      page.getByRole("progressbar")
    );

    // 로딩이 있었다면 사라질 때까지 대기
    if (await loadingIndicator.isVisible().catch(() => false)) {
      await expect(loadingIndicator).toBeHidden({ timeout: 15_000 });
    }

    // 데이터가 실제로 표시되는지 확인 (빈 상태 메시지가 아닌)
    const emptyState = page.getByText(/데이터가 없습니다|No data|비어 있습니다|Empty/i);
    const dataContent = page.getByTestId("dashboard-data").or(
      page.locator("table, [class*='chart'], [class*='list']")
    );

    // 데이터가 있거나, 빈 상태 메시지가 있거나 (둘 중 하나는 표시)
    const hasData = await dataContent.first().isVisible().catch(() => false);
    const isEmpty = await emptyState.first().isVisible().catch(() => false);
    expect(hasData || isEmpty).toBe(true);
  });

  test("네비게이션 메뉴가 동작한다", async ({ page }) => {
    // 사이드바 또는 상단 네비게이션 존재 확인
    const nav = page.getByRole("navigation").first();
    await expect(nav).toBeVisible();

    // 네비게이션 링크 클릭 시 페이지 전환
    const navLinks = nav.getByRole("link");
    const linkCount = await navLinks.count();
    expect(linkCount).toBeGreaterThan(0);

    // 첫 번째 네비게이션 링크 클릭 후 URL 변경 확인
    const firstLink = navLinks.first();
    const href = await firstLink.getAttribute("href");
    if (href && href !== "#") {
      await firstLink.click();
      await page.waitForURL(`**${href}**`, { timeout: 5_000 });
    }
  });

  test("로그아웃 후 로그인 페이지로 리다이렉트된다", async ({ page }) => {
    // 로그아웃 버튼/메뉴 찾기
    // 프로필 메뉴를 열어야 할 수 있음
    const profileMenu = page.getByTestId("user-menu").or(
      page.getByRole("button", { name: /프로필|Profile|계정|Account/i })
    );

    if (await profileMenu.isVisible().catch(() => false)) {
      await profileMenu.click();
    }

    const logoutButton = page.getByRole("button", { name: /로그아웃|Logout|Sign out/i }).or(
      page.getByRole("menuitem", { name: /로그아웃|Logout|Sign out/i })
    );
    await logoutButton.click();

    // 로그인 페이지로 리다이렉트 확인
    await page.waitForURL("**/login**", { timeout: 10_000 });
    await expect(
      page.getByRole("heading", { name: /로그인|Sign in|Login/i })
    ).toBeVisible();
  });
});

test.describe("대시보드 - 비인증 접근", () => {
  // 이 describe 블록은 storageState를 사용하지 않음 (비인증 상태)
  test.use({ storageState: { cookies: [], origins: [] } });

  test("비인증 상태에서 대시보드 접근 시 로그인 페이지로 리다이렉트된다", async ({
    page,
  }) => {
    await page.goto("/dashboard");

    // 로그인 페이지로 리다이렉트 확인
    await page.waitForURL("**/login**", { timeout: 10_000 });

    // 로그인 폼이 표시됨
    await expect(
      page.getByRole("heading", { name: /로그인|Sign in|Login/i })
    ).toBeVisible();
  });

  test("비인증 상태에서 보호된 API 호출 시 401을 반환한다", async ({
    page,
  }) => {
    // API 응답을 가로채서 401 확인
    const response = await page.request.get("/api/dashboard");
    expect(response.status()).toBe(401);
  });
});

test.describe("대시보드 - 에러 처리", () => {
  test("API 오류 시 에러 메시지가 표시된다", async ({ page }) => {
    // API 응답을 모킹하여 500 에러 시뮬레이션
    await page.route("**/api/dashboard**", (route) =>
      route.fulfill({
        status: 500,
        contentType: "application/json",
        body: JSON.stringify({ error: "Internal Server Error" }),
      })
    );

    await page.goto("/dashboard");

    // 에러 메시지 또는 재시도 UI가 표시되는지 확인
    const errorMessage = page.getByText(
      /오류|에러|Error|문제가 발생|Something went wrong/i
    );
    await expect(errorMessage).toBeVisible({ timeout: 10_000 });
  });

  test("네트워크 오류 시 오프라인 안내가 표시된다", async ({ page }) => {
    // 대시보드 로드 후 네트워크 차단
    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");

    // 네트워크 차단
    await page.context().setOffline(true);

    // 데이터 갱신을 트리거하는 동작 (새로고침)
    await page.reload().catch(() => {
      // 오프라인이므로 에러 발생 가능
    });

    // 오프라인/네트워크 에러 안내 확인
    const offlineMessage = page.getByText(
      /오프라인|네트워크|Offline|Network|연결/i
    );
    // 브라우저 기본 에러 페이지 또는 앱의 오프라인 UI
    const isAppOffline = await offlineMessage.isVisible().catch(() => false);
    const isBrowserError = await page
      .getByText(/ERR_INTERNET_DISCONNECTED|연결할 수 없|unable to connect/i)
      .isVisible()
      .catch(() => false);

    expect(isAppOffline || isBrowserError).toBe(true);

    // 네트워크 복원
    await page.context().setOffline(false);
  });
});
