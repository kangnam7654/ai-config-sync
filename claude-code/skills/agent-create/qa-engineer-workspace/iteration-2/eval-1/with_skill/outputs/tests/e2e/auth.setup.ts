import { test as setup, expect } from "@playwright/test";
import path from "path";

/**
 * 인증 Setup 스크립트
 * - 로그인 페이지에서 자격 증명을 입력하고 대시보드 진입을 확인
 * - 인증된 브라우저 상태를 storageState 파일로 저장
 * - 다른 테스트 프로젝트가 이 상태를 재사용하여 로그인 반복을 회피
 */

const AUTH_FILE = path.join(__dirname, ".auth", "user.json");

setup("로그인하여 인증 상태 저장", async ({ page }) => {
  // ── 1. 로그인 페이지 접근 ────────────────────────────────────
  await page.goto("/login");

  // 로그인 폼이 렌더링될 때까지 대기
  await expect(page.getByRole("heading", { name: /로그인|Sign in|Login/i })).toBeVisible();

  // ── 2. 자격 증명 입력 ────────────────────────────────────────
  // 환경변수에서 테스트 계정 정보를 읽음 (CI/로컬 모두 대응)
  const username = process.env.TEST_USERNAME ?? "testuser@example.com";
  const password = process.env.TEST_PASSWORD ?? "Test1234!";

  await page.getByLabel(/이메일|Email|Username/i).fill(username);
  await page.getByLabel(/비밀번호|Password/i).fill(password);

  // ── 3. 로그인 버튼 클릭 ──────────────────────────────────────
  await page.getByRole("button", { name: /로그인|Sign in|Log in/i }).click();

  // ── 4. 대시보드 도달 확인 ────────────────────────────────────
  // 로그인 성공 후 대시보드로 리다이렉트되는 것을 URL과 요소로 이중 확인
  await page.waitForURL("**/dashboard**", { timeout: 10_000 });
  await expect(page.getByRole("heading", { name: /대시보드|Dashboard/i })).toBeVisible();

  // ── 5. 인증 상태 저장 ────────────────────────────────────────
  await page.context().storageState({ path: AUTH_FILE });
});
