import { test, expect } from '@playwright/test';

test.describe('Pre-Approved Trade Execution Safety Gate', () => {
  test('user can access execution controls workspace', async ({ page }) => {
    await page.goto('/login');
    await page.getByRole('button', { name: /Sign In/i }).click();
    await page.goto('/execution');
    await expect(page.getByText('Pre-Approved Trade Execution Control')).toBeVisible();
  });
});
