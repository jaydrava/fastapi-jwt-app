import { test, expect } from '@playwright/test';

test.describe('Auth E2E Tests', () => {
  test('Register with valid data', async ({ page }) => {
    await page.goto('http://localhost:8000/register');
    await page.fill('input[name="username"]', 'testuser');
    await page.fill('input[name="email"]', 'testuser@example.com');
    await page.fill('input[name="password"]', 'TestPassword123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/login/);
  });

  test('Login with valid credentials', async ({ page }) => {
    await page.goto('http://localhost:8000/login');
    await page.fill('input[name="username"]', 'testuser');
    await page.fill('input[name="password"]', 'TestPassword123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/dashboard|\/$/); // adjust based on your redirect
  });

  test('Register with short password (negative)', async ({ page }) => {
    await page.goto('http://localhost:8000/register');
    await page.fill('input[name="username"]', 'baduser');
    await page.fill('input[name="email"]', 'baduser@example.com');
    await page.fill('input[name="password"]', '123'); // too short
    await page.click('button[type="submit"]');
    // expect some error message
    await expect(page.locator('.error-message')).toBeVisible();
  });

  test('Login with wrong password (negative)', async ({ page }) => {
    await page.goto('http://localhost:8000/login');
    await page.fill('input[name="username"]', 'testuser');
    await page.fill('input[name="password"]', 'WrongPassword');
    await page.click('button[type="submit"]');
    await expect(page.locator('.error-message')).toBeVisible();
  });
});
