import { test as setup, expect } from "@playwright/test";
import path from "path";

const authFile = path.join(__dirname, ".auth", "user.json");

setup("authenticate", async ({ page }) => {
  // 1. 로그인 페이지로 이동
  await page.goto("/login");

  // 로그인 폼이 렌더링될 때까지 대기
  await expect(page.locator("form")).toBeVisible();

  // 2. 이메일/비밀번호 입력
  await page.getByLabel("이메일").fill("test@example.com");
  await page.getByLabel("비밀번호").fill("Test1234!");

  // 3. 로그인 버튼 클릭
  await page.getByRole("button", { name: "로그인" }).click();

  // 4. 로그인 성공 확인 - 대시보드로 리다이렉트되는지 검증
  await page.waitForURL("/dashboard", { timeout: 10_000 });
  await expect(page).toHaveURL(/\/dashboard/);

  // 5. 인증 상태 저장 (쿠키, localStorage 등)
  await page.context().storageState({ path: authFile });
});
