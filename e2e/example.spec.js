import { test, expect } from '@playwright/test';

const randomEmail = `user_${Date.now()}@example.com`;
const testPassword = 'StrongPass123!';

test.describe('Authentication Tests', () => {
  test('User can register successfully', async ({ page }) => {
    await page.goto('http://localhost:8000/register');

    await page.fill('input[name="email"]', randomEmail);
    await page.fill('input[name="password"]', testPassword);
    await page.click('button[type="submit"]');

    const messageLocator = page.locator('#message');
    await expect(messageLocator).toBeVisible({ timeout: 10000 });

    const messageText = (await messageLocator.textContent())?.toLowerCase() ?? '';
    expect(
      messageText.includes('registration successful') ||
      messageText.includes('email already registered')
    ).toBeTruthy();
  });

  test('User can login successfully with registered credentials', async ({ page }) => {
    await page.goto('http://localhost:8000/login');

    await page.fill('input[name="email"]', randomEmail);
    await page.fill('input[name="password"]', testPassword);
    await page.click('button[type="submit"]');

    const messageLocator = page.locator('#message');
    await expect(messageLocator).toBeVisible({ timeout: 10000 });

    const messageText = (await messageLocator.textContent())?.toLowerCase() ?? '';
    expect(messageText).toContain('login successful');
  });
});
