import { test, expect } from '@playwright/test';

test.describe('Human Decision Workspace & Gate', () => {
  test('user can view approvals workspace and legal attestation input', async ({ page }) => {
    await page.goto('/approvals');
    await expect(page.getByText('Human Decision Workspace')).toBeVisible();
    await expect(page.getByText('Human Approver Attestation')).toBeVisible();
    await expect(page.getByRole('button', { name: /APPROVE RECOMMENDATION/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /REJECT RECOMMENDATION/i })).toBeVisible();
  });
});
