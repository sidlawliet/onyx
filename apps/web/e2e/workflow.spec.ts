import { test, expect } from '@playwright/test';

test.describe('Institutional Workflow Engine', () => {
  test('user can view workflows and navigate control plane stages', async ({ page }) => {
    // 1. Visit Login Page
    await page.goto('/login');
    await expect(page.getByRole('main').getByRole('heading', { name: 'Onyx Operations' })).toBeVisible();

    // 2. Authenticate
    await page.getByRole('button', { name: /Sign In/i }).click();
    await page.goto('/workflow');

    // 3. Verify Sidebar and Workflows Dashboard
    await expect(page.getByRole('heading', { name: 'Active Workflow Pipelines' })).toBeVisible();
    await expect(page.getByRole('link', { name: /Workflows/i })).toBeVisible();
    await expect(page.getByRole('link', { name: /Intelligence/i })).toBeVisible();
    await expect(page.getByRole('link', { name: /Strategy/i })).toBeVisible();
    await expect(page.getByRole('link', { name: /Approvals/i })).toBeVisible();
    await expect(page.getByRole('link', { name: /Execution/i })).toBeVisible();
    await expect(page.getByRole('link', { name: /Monitoring/i })).toBeVisible();
    await expect(page.getByRole('link', { name: /Audit/i })).toBeVisible();
  });

  test('user can navigate to intelligence and audit pages', async ({ page }) => {
    await page.goto('/login');
    await page.getByRole('button', { name: /Sign In/i }).click();
    await page.goto('/workflow');

    // Navigate to Market Intelligence
    await page.click('a[href="/intelligence"]');
    await expect(page.getByText('Market Intelligence Workspace')).toBeVisible();

    // Navigate to Audit Trail
    await page.click('a[href="/audit"]');
    await expect(page.getByText('Institutional Audit Trail & Evidence Log')).toBeVisible();
  });
});
