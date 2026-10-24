/**
 * Playwright Smoke Test Suite: MathQuest
 * 
 * Covers all 6 primary user and navigation flows:
 * 1. Guest → topics → learn → quiz → results
 * 2. Signup → setup (onboarding) → dashboard
 * 3. Login → dashboard
 * 4. Logout
 * 5. Protected-route redirect and return (deep-linking)
 * 6. Invalid deep link → custom 404 page
 * 
 * Execution:
 * npx playwright test tests/smoke.playwright.spec.ts --headed
 */

import { test, expect } from '@playwright/test'

const BASE_URL = process.env.PLAYWRIGHT_TEST_BASE_URL || 'http://localhost:3000'

test.describe('MathQuest E2E Smoke Tests', () => {
  test.beforeEach(async ({ page, context }) => {
    // Clear storage for clean session state
    await context.clearCookies()
    await page.goto(BASE_URL)
    await page.evaluate(() => localStorage.clear())
  })

  test('Flow 1: Guest → Topics → Learn → Quiz → Results', async ({ page }) => {
    // 1. Visit Login page and continue as guest
    await page.goto(`${BASE_URL}/login`)
    await page.click('button:has-text("Continue as Guest")')

    // 2. Navigates to territory map (Topics)
    await expect(page).toHaveURL(new RegExp(`${BASE_URL}/?$`))
    await expect(page.locator('h1')).toContainText(/Georgia|Territory Map/)

    // 3. Navigate into Learn lesson (e.g. Fractions)
    await page.click('a[href*="/learn/5/fractions"]')
    await expect(page).toHaveURL(/.*\/learn\/5\/fractions/)
    await expect(page.locator('h1')).toContainText(/Fractions/)

    // 4. Click "Practice Now" to enter Focus Layout Quiz
    await page.click('a:has-text("Practice Now")')
    await expect(page).toHaveURL(/.*\/quiz.*/)

    // Verify Quiz Question Card renders
    await expect(page.locator('text=Question 1 of 10')).toBeVisible({ timeout: 10000 })
    await expect(page.locator('button:has-text("Option A")')).toBeVisible()

    // 5. Select Option A and confirm
    await page.click('button:has-text("Option A")')
    await page.click('button:has-text("Confirm Answer")')

    // Verify feedback panel appears
    await expect(page.locator('text=Next Question')).toBeVisible()
  })

  test('Flow 2: Signup → Setup (Onboarding) → Dashboard', async ({ page }) => {
    const randomEmail = `adventurer_${Date.now()}@mathquest-test.org`
    const testPassword = 'Password123!'

    // 1. Visit signup page
    await page.goto(`${BASE_URL}/signup`)
    await page.fill('input#email', randomEmail)
    await page.fill('input#password', testPassword)
    await page.fill('input#confirmPassword', testPassword)
    await page.click('button[type="submit"]')

    // 2. Diverts to onboarding setup
    await expect(page).toHaveURL(/.*\/onboarding/, { timeout: 10000 })
    await page.fill('input#displayName', 'Speedy Solver')
    await page.click('button:has-text("Grade 6")')
    await page.click('button:has-text("Georgia Standards (GSE)")')
    await page.click('button:has-text("Launch My Adventure!")')

    // 3. Arrives on dashboard with customized greeting
    await expect(page).toHaveURL(/.*\/dashboard/, { timeout: 10000 })
    await expect(page.locator('h1')).toContainText('Welcome back, Speedy Solver!')
    await expect(page.locator('text=Grade 6')).toBeVisible()
  })

  test('Flow 3: Login → Dashboard', async ({ page }) => {
    // Test with demo credentials
    await page.goto(`${BASE_URL}/login`)
    await page.fill('input#email', 'demo@mathquest.org')
    await page.fill('input#password', 'MathQuest2026!')
    await page.click('button[type="submit"]')

    // Successful login redirects to dashboard
    await expect(page).toHaveURL(/.*\/dashboard/, { timeout: 10000 })
    await expect(page.locator('text=Explorer Account')).toBeVisible()
  })

  test('Flow 4: Logout', async ({ page }) => {
    // 1. In guest mode or authenticated
    await page.goto(`${BASE_URL}/profile`)
    await expect(page.locator('button:has-text("Exit Guest Mode"), button:has-text("Sign Out")')).toBeVisible()

    // 2. Click sign out / exit
    await page.click('button:has-text("Exit Guest Mode"), button:has-text("Sign Out")')

    // 3. Redirected to /login
    await expect(page).toHaveURL(/.*\/login/)
  })

  test('Flow 5: Protected Route Redirect and Return', async ({ page }) => {
    // 1. Try to visit protected deep link while logged out & non-guest
    await page.goto(`${BASE_URL}/progress`)

    // 2. Middleware redirects to /login with redirect query param
    await expect(page).toHaveURL(new RegExp(`${BASE_URL}/login\\?redirect=%2Fprogress`))

    // 3. Click "Continue as Guest" or sign in
    await page.click('button:has-text("Continue as Guest")')

    // 4. Arrives at originally requested page (/progress)
    await expect(page).toHaveURL(/.*\/progress/)
    await expect(page.locator('h1')).toContainText(/Mastery & Learning Progress/)
  })

  test('Flow 6: Invalid Deep Link → Custom 404 Page', async ({ page }) => {
    // 1. First enable guest mode
    await page.goto(`${BASE_URL}/login`)
    await page.click('button:has-text("Continue as Guest")')

    // 2. Navigate to non-existent route
    await page.goto(`${BASE_URL}/non-existent-secret-realm`)

    // 3. Renders custom error 404 page
    await expect(page.locator('text=404')).toBeVisible()
    await expect(page.locator('h1')).toContainText('Lost in the Mathematical Wilderness')
    await expect(page.locator('a:has-text("Return to Dashboard")')).toBeVisible()

    // 4. Clicking recovery button brings user back
    await page.click('a:has-text("Return to Dashboard")')
    await expect(page).toHaveURL(/.*\/dashboard/)
  })
})
