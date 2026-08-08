import { test, expect } from '@playwright/test';

test.describe('Human Decision Workspace & Gate', () => {
  test('user can view approvals workspace page', async ({ page }) => {
    await page.goto('/login');
    await page.getByRole('button', { name: /Sign In/i }).click();
    await page.goto('/approvals');
    await expect(page.getByText('Human Decision Workspace')).toBeVisible();
  });
});
