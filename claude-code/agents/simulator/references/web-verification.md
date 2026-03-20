# Web App Verification Reference

## Playwright CLI Commands

```bash
# Check Playwright installation
npx playwright --version

# Install specific browser
npx playwright install chromium --with-deps

# Install all browsers
npx playwright install --with-deps
```

## Playwright Script Patterns

All web verification is done by writing a temporary Node.js script and executing it with `node`. Scripts are saved to `/tmp/simulator-web/` and deleted after execution unless the user requests otherwise.

### Basic Page Navigation and Screenshot

```javascript
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 }
  });
  const page = await context.newPage();

  await page.goto('http://localhost:3000', { waitUntil: 'networkidle' });
  await page.screenshot({
    path: '/tmp/simulator-screenshots/page-initial.png',
    fullPage: true
  });

  console.log('Title:', await page.title());
  console.log('URL:', page.url());

  await browser.close();
})();
```

### Click, Type, and Form Interaction

```javascript
// Click a button
await page.click('button:has-text("Submit")');
await page.click('[data-testid="login-button"]');
await page.click('a[href="/dashboard"]');

// Fill form fields
await page.fill('input[name="email"]', 'test@example.com');
await page.fill('input[name="password"]', 'testpass123');
await page.fill('[data-testid="search-input"]', 'search query');

// Select dropdown
await page.selectOption('select[name="country"]', 'KR');

// Check/uncheck checkbox
await page.check('input[type="checkbox"]#terms');
await page.uncheck('input[type="checkbox"]#newsletter');

// Upload file
await page.setInputFiles('input[type="file"]', '/path/to/file.pdf');
```

### Waiting Strategies

```javascript
// Wait for element to appear
await page.waitForSelector('.dashboard-content', { state: 'visible' });

// Wait for URL change
await page.waitForURL('**/dashboard');

// Wait for network response
const response = await page.waitForResponse(
  resp => resp.url().includes('/api/users') && resp.status() === 200
);

// Wait for navigation
await Promise.all([
  page.waitForNavigation(),
  page.click('a[href="/next-page"]')
]);

// Wait for load state
await page.waitForLoadState('networkidle');
```

### Assertions (Manual Verification)

```javascript
// Check if element is visible
const isVisible = await page.isVisible('[data-testid="success-message"]');
console.log('Success message visible:', isVisible);

// Get element text
const text = await page.textContent('.result-message');
console.log('Result text:', text);

// Count elements
const count = await page.locator('.list-item').count();
console.log('List items:', count);

// Check element attribute
const href = await page.getAttribute('a.next-link', 'href');
console.log('Next link href:', href);

// Check input value
const value = await page.inputValue('input[name="email"]');
console.log('Email value:', value);
```

### Screenshot Variants

```javascript
// Full page screenshot
await page.screenshot({
  path: '/tmp/simulator-screenshots/full-page.png',
  fullPage: true
});

// Viewport-only screenshot
await page.screenshot({
  path: '/tmp/simulator-screenshots/viewport.png'
});

// Element-specific screenshot
await page.locator('.hero-section').screenshot({
  path: '/tmp/simulator-screenshots/hero.png'
});

// Screenshot with clip region
await page.screenshot({
  path: '/tmp/simulator-screenshots/region.png',
  clip: { x: 0, y: 0, width: 800, height: 600 }
});
```

### Multi-Step Flow Verification

```javascript
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
  const screenshotDir = '/tmp/simulator-screenshots';
  let stepNum = 0;

  const capture = async (name) => {
    stepNum++;
    const path = `${screenshotDir}/step-${String(stepNum).padStart(2, '0')}-${name}.png`;
    await page.screenshot({ path, fullPage: true });
    console.log(`Step ${stepNum} [${name}]: ${path}`);
    return path;
  };

  // Step 1: Navigate to login
  await page.goto('http://localhost:3000/login', { waitUntil: 'networkidle' });
  await capture('login-page');

  // Step 2: Fill credentials
  await page.fill('input[name="email"]', 'test@example.com');
  await page.fill('input[name="password"]', 'password123');
  await capture('credentials-filled');

  // Step 3: Submit and wait for redirect
  await Promise.all([
    page.waitForURL('**/dashboard'),
    page.click('button[type="submit"]')
  ]);
  await capture('dashboard-loaded');

  // Step 4: Verify dashboard content
  const welcomeText = await page.textContent('.welcome-message');
  console.log('Welcome:', welcomeText);
  const isVisible = await page.isVisible('.user-avatar');
  console.log('Avatar visible:', isVisible);
  await capture('verification-complete');

  await browser.close();
})();
```

### Authentication Handling

```javascript
// Cookie-based auth: set cookies before navigation
await context.addCookies([
  {
    name: 'session',
    value: 'session-token-here',
    domain: 'localhost',
    path: '/'
  }
]);

// Local storage: set after navigation to the domain
await page.goto('http://localhost:3000');
await page.evaluate(() => {
  localStorage.setItem('auth_token', 'bearer-token-here');
});
await page.reload();

// Save and restore session state
await context.storageState({ path: '/tmp/simulator-web/auth-state.json' });
// Later: restore
const context2 = await browser.newContext({
  storageState: '/tmp/simulator-web/auth-state.json'
});
```

### Responsive Viewport Testing

```javascript
const viewports = [
  { name: 'mobile', width: 375, height: 812 },
  { name: 'tablet', width: 768, height: 1024 },
  { name: 'desktop', width: 1280, height: 720 },
  { name: 'wide', width: 1920, height: 1080 }
];

for (const vp of viewports) {
  await page.setViewportSize({ width: vp.width, height: vp.height });
  await page.screenshot({
    path: `/tmp/simulator-screenshots/responsive-${vp.name}.png`,
    fullPage: true
  });
  console.log(`${vp.name} (${vp.width}x${vp.height}): captured`);
}
```

### Network Interception (Read-Only Monitoring)

```javascript
// Log all API requests
page.on('request', req => {
  if (req.url().includes('/api/')) {
    console.log(`→ ${req.method()} ${req.url()}`);
  }
});

page.on('response', resp => {
  if (resp.url().includes('/api/')) {
    console.log(`← ${resp.status()} ${resp.url()}`);
  }
});

// Log console errors
page.on('console', msg => {
  if (msg.type() === 'error') {
    console.log('CONSOLE ERROR:', msg.text());
  }
});

// Log page errors (uncaught exceptions)
page.on('pageerror', err => {
  console.log('PAGE ERROR:', err.message);
});
```

## Common Selectors Priority

Use selectors in this priority order:

1. `[data-testid="..."]` — most stable
2. `role=button[name="Submit"]` — accessible role selectors
3. `text="Button Text"` or `:has-text("...")` — visible text
4. `#element-id` — HTML id
5. `.class-name` — CSS class (least stable, avoid if possible)
