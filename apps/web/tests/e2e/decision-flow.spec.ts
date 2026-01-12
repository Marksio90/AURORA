import { test, expect } from '@playwright/test';

test.describe('Decision Flow', () => {
  test('should display landing page with form', async ({ page }) => {
    await page.goto('/');

    // Check heading
    await expect(page.getByRole('heading', { level: 1 })).toContainText(
      'Podejmuj spokojniejsze decyzje'
    );

    // Check form fields exist
    await expect(page.getByLabelText(/What decision are you facing/i)).toBeVisible();
    await expect(page.getByLabelText(/What options are you considering/i)).toBeVisible();
    await expect(page.getByLabelText(/How stressed do you feel/i)).toBeVisible();

    // Check submit button
    await expect(page.getByRole('button', { name: /Get Your Decision Brief/i })).toBeVisible();
  });

  test('should validate required fields', async ({ page }) => {
    await page.goto('/');

    const submitButton = page.getByRole('button', { name: /Get Your Decision Brief/i });

    // Button should be disabled when fields are empty
    await expect(submitButton).toBeDisabled();
  });

  test('should enable submit when all fields are filled', async ({ page }) => {
    await page.goto('/');

    // Fill form
    await page.getByLabelText(/What decision are you facing/i).fill(
      'Should I change careers? I have been in tech for 10 years but feeling burnt out.'
    );

    await page.getByLabelText(/What options are you considering/i).fill(
      'Stay in current role, Switch to management, Take a sabbatical, Change careers entirely'
    );

    // Set stress level
    await page.getByLabelText(/How stressed do you feel/i).fill('7');

    // Submit button should be enabled
    const submitButton = page.getByRole('button', { name: /Get Your Decision Brief/i });
    await expect(submitButton).toBeEnabled();
  });

  test('should navigate to history page', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('link', { name: /History/i }).click();

    await expect(page).toHaveURL('/history');
    await expect(page.getByRole('heading', { level: 1 })).toContainText('Decision History');
  });
});
