import { test, expect } from "@playwright/test";

// 로그인 테스트는 인증되지 않은 상태에서 실행
test.use({ storageState: { cookies: [], origins: [] } });

test.describe("로그인 페이지 E2E", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/login");
  });

  // ── 페이지 렌더링 ──────────────────────────────────────────────

  test("로그인 폼이 정상 렌더링된다", async ({ page }) => {
    await expect(page).toHaveTitle(/로그인|Login/i);

    const emailInput = page.getByLabel("이메일");
    const passwordInput = page.getByLabel("비밀번호");
    const submitButton = page.getByRole("button", { name: "로그인" });

    await expect(emailInput).toBeVisible();
    await expect(passwordInput).toBeVisible();
    await expect(submitButton).toBeVisible();
    await expect(submitButton).toBeEnabled();
  });

  // ── 유효성 검사 ────────────────────────────────────────────────

  test("이메일 미입력 시 유효성 검사 에러가 표시된다", async ({ page }) => {
    await page.getByLabel("비밀번호").fill("Test1234!");
    await page.getByRole("button", { name: "로그인" }).click();

    const emailError = page.getByText(/이메일.*필수|이메일.*입력/i);
    await expect(emailError).toBeVisible();
  });

  test("비밀번호 미입력 시 유효성 검사 에러가 표시된다", async ({ page }) => {
    await page.getByLabel("이메일").fill("test@example.com");
    await page.getByRole("button", { name: "로그인" }).click();

    const passwordError = page.getByText(/비밀번호.*필수|비밀번호.*입력/i);
    await expect(passwordError).toBeVisible();
  });

  test("잘못된 이메일 형식 입력 시 유효성 검사 에러가 표시된다", async ({
    page,
  }) => {
    await page.getByLabel("이메일").fill("invalid-email");
    await page.getByLabel("비밀번호").fill("Test1234!");
    await page.getByRole("button", { name: "로그인" }).click();

    const formatError = page.getByText(/유효.*이메일|이메일.*형식/i);
    await expect(formatError).toBeVisible();
  });

  // ── 로그인 실패 ────────────────────────────────────────────────

  test("잘못된 자격증명으로 로그인 시 에러 메시지가 표시된다", async ({
    page,
  }) => {
    await page.getByLabel("이메일").fill("wrong@example.com");
    await page.getByLabel("비밀번호").fill("WrongPassword!");
    await page.getByRole("button", { name: "로그인" }).click();

    const errorAlert = page.getByRole("alert");
    await expect(errorAlert).toBeVisible({ timeout: 5_000 });
    await expect(errorAlert).toContainText(
      /이메일.*비밀번호.*확인|로그인.*실패|인증.*실패/i
    );
  });

  test("로그인 실패 후 비밀번호 필드가 초기화된다", async ({ page }) => {
    await page.getByLabel("이메일").fill("wrong@example.com");
    await page.getByLabel("비밀번호").fill("WrongPassword!");
    await page.getByRole("button", { name: "로그인" }).click();

    // 에러 표시 대기
    await expect(page.getByRole("alert")).toBeVisible({ timeout: 5_000 });

    // 비밀번호 필드가 비어있는지 확인
    await expect(page.getByLabel("비밀번호")).toHaveValue("");
    // 이메일은 유지되어야 함
    await expect(page.getByLabel("이메일")).toHaveValue("wrong@example.com");
  });

  // ── 로그인 성공 ────────────────────────────────────────────────

  test("올바른 자격증명으로 로그인 시 대시보드로 리다이렉트된다", async ({
    page,
  }) => {
    await page.getByLabel("이메일").fill("test@example.com");
    await page.getByLabel("비밀번호").fill("Test1234!");
    await page.getByRole("button", { name: "로그인" }).click();

    await page.waitForURL("/dashboard", { timeout: 10_000 });
    await expect(page).toHaveURL(/\/dashboard/);
  });

  // ── 로그인 중 상태 ────────────────────────────────────────────

  test("로그인 요청 중 버튼이 비활성화되고 로딩 상태가 표시된다", async ({
    page,
  }) => {
    await page.getByLabel("이메일").fill("test@example.com");
    await page.getByLabel("비밀번호").fill("Test1234!");

    // 네트워크 요청을 지연시켜 로딩 상태를 확인
    await page.route("**/api/auth/login", async (route) => {
      await new Promise((resolve) => setTimeout(resolve, 1_000));
      await route.continue();
    });

    await page.getByRole("button", { name: "로그인" }).click();

    // 버튼이 비활성화 상태인지 확인
    const submitButton = page.getByRole("button", { name: /로그인|로딩/i });
    await expect(submitButton).toBeDisabled();
  });

  // ── 비밀번호 표시/숨김 토글 ────────────────────────────────────

  test("비밀번호 표시/숨김 토글이 동작한다", async ({ page }) => {
    const passwordInput = page.getByLabel("비밀번호");
    await passwordInput.fill("Test1234!");

    // 초기 상태: password 타입
    await expect(passwordInput).toHaveAttribute("type", "password");

    // 표시 토글 클릭
    const toggleButton = page.getByTestId("password-visibility-toggle");
    // 토글 버튼이 존재하는 경우에만 테스트 (선택적 UI)
    if (await toggleButton.isVisible()) {
      await toggleButton.click();
      await expect(passwordInput).toHaveAttribute("type", "text");

      await toggleButton.click();
      await expect(passwordInput).toHaveAttribute("type", "password");
    }
  });

  // ── 키보드 접근성 ──────────────────────────────────────────────

  test("Enter 키로 로그인 폼을 제출할 수 있다", async ({ page }) => {
    await page.getByLabel("이메일").fill("test@example.com");
    await page.getByLabel("비밀번호").fill("Test1234!");
    await page.getByLabel("비밀번호").press("Enter");

    await page.waitForURL("/dashboard", { timeout: 10_000 });
    await expect(page).toHaveURL(/\/dashboard/);
  });

  test("Tab 키로 폼 요소 간 이동이 가능하다", async ({ page }) => {
    // 이메일 필드에 포커스
    await page.getByLabel("이메일").focus();
    await expect(page.getByLabel("이메일")).toBeFocused();

    // Tab으로 비밀번호 필드로 이동
    await page.keyboard.press("Tab");
    await expect(page.getByLabel("비밀번호")).toBeFocused();

    // Tab으로 로그인 버튼으로 이동
    await page.keyboard.press("Tab");
    await expect(page.getByRole("button", { name: "로그인" })).toBeFocused();
  });
});
