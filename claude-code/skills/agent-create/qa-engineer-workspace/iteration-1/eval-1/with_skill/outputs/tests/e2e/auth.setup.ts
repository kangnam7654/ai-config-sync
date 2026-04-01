import { test as setup, expect } from '@playwright/test';
import path from 'path';

const authFile = path.join(__dirname, '.auth', 'user.json');

/**
 * 인증 Setup
 *
 * Playwright의 "project dependencies" 패턴을 사용하여
 * 로그인 상태를 파일로 저장하고, 이후 테스트에서 재사용한다.
 *
 * 이 setup은 다른 모든 테스트 프로젝트(chromium, firefox, webkit)보다
 * 먼저 실행되며, storageState를 .auth/user.json에 저장한다.
 */
setup('authenticate', async ({ page }) => {
  // 1. 로그인 페이지로 이동
  await page.goto('/login');

  // 2. 로그인 페이지가 정상 로드되었는지 확인
  await expect(page).toHaveURL(/.*\/login/);
  await expect(page.getByRole('heading', { name: /로그인|Sign In|Login/i })).toBeVisible();

  // 3. 자격 증명 입력
  //    환경 변수에서 테스트 계정 정보를 읽어온다.
  //    CI에서는 시크릿으로, 로컬에서는 .env 파일로 관리한다.
  const username = process.env.TEST_USERNAME ?? 'testuser@example.com';
  const password = process.env.TEST_PASSWORD ?? 'TestPassword123!';

  await page.getByLabel(/이메일|Email|Username/i).fill(username);
  await page.getByLabel(/비밀번호|Password/i).fill(password);

  // 4. 로그인 버튼 클릭
  await page.getByRole('button', { name: /로그인|Sign In|Login|Log in/i }).click();

  // 5. 로그인 성공 후 대시보드로 리다이렉트되는지 확인
  //    네트워크 응답까지 기다린다.
  await page.waitForURL('**/dashboard', { timeout: 15_000 });
  await expect(page).toHaveURL(/.*\/dashboard/);

  // 6. 인증 상태를 파일로 저장 (쿠키 + localStorage)
  await page.context().storageState({ path: authFile });
});
