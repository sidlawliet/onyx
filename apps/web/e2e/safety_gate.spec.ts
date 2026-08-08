import { test, expect } from '@playwright/test';

test.describe('Pre-Approved Trade Execution Safety Gate', () => {
  test('user can access execution controls and test safety gate rejection', async ({ page }) => {
    await page.goto('/execution');
    await expect(page.getByText('Pre-Approved Trade Execution Control')).toBeVisible();
    await expect(page.getByText('Execution Safety Gate Controls')).toBeVisible();
    await expect(page.getByRole('button', { name: /RELEASE PRE-APPROVED TRADE ORDERS/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /Test Safety Gate/i })).toBeVisible();
  });
});
