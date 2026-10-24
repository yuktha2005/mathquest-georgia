import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '../stores/auth'

// Mocking route middleware navigation decision function
function evaluateAuthRoute(
  authStore: any,
  to: { path: string; fullPath?: string; query?: Record<string, string> }
) {
  const publicRoutes = ['/login', '/signup', '/forgot', '/eval']
  const isPublicRoute = publicRoutes.includes(to.path)

  // 1. If signed in, prevent visiting login/signup
  if (authStore.isAuthenticated) {
    if (to.path === '/login' || to.path === '/signup') {
      const redirectTarget = (to.query?.redirect as string) || '/dashboard'
      return { action: 'redirect', to: redirectTarget }
    }

    if (authStore.needsSetup && to.path !== '/onboarding') {
      return { action: 'redirect', to: '/onboarding' }
    }

    return { action: 'allow' }
  }

  // 2. Guest mode: allows all learning and quiz routes
  if (authStore.isGuest) {
    return { action: 'allow' }
  }

  // 3. Unauthenticated non-guest: redirect to login
  if (!isPublicRoute) {
    return {
      action: 'redirect',
      to: {
        path: '/login',
        query: {
          redirect: to.fullPath && to.fullPath !== '/' ? to.fullPath : undefined,
        },
      },
    }
  }

  return { action: 'allow' }
}

describe('Route Middleware (auth.global.ts)', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    vi.clearAllMocks()
  })

  it('redirects unauthenticated non-guest from protected /dashboard to /login', () => {
    const auth = useAuthStore()
    const decision = evaluateAuthRoute(auth, { path: '/dashboard', fullPath: '/dashboard' })

    expect(decision.action).toBe('redirect')
    expect(decision.to).toEqual({
      path: '/login',
      query: { redirect: '/dashboard' },
    })
  })

  it('redirects unauthenticated non-guest from /quiz to /login with deep-link redirect', () => {
    const auth = useAuthStore()
    const decision = evaluateAuthRoute(auth, {
      path: '/quiz',
      fullPath: '/quiz?board=georgia&grade=5&topic=fractions',
    })

    expect(decision.action).toBe('redirect')
    expect(decision.to).toEqual({
      path: '/login',
      query: { redirect: '/quiz?board=georgia&grade=5&topic=fractions' },
    })
  })

  it('allows unauthenticated access to public routes (/login, /signup, /forgot, /eval)', () => {
    const auth = useAuthStore()
    expect(evaluateAuthRoute(auth, { path: '/login' }).action).toBe('allow')
    expect(evaluateAuthRoute(auth, { path: '/signup' }).action).toBe('allow')
    expect(evaluateAuthRoute(auth, { path: '/forgot' }).action).toBe('allow')
    expect(evaluateAuthRoute(auth, { path: '/eval' }).action).toBe('allow')
  })

  it('allows guests to access all learning routes without redirection', () => {
    const auth = useAuthStore()
    auth.continueAsGuest()
    expect(auth.isGuest).toBe(true)

    expect(evaluateAuthRoute(auth, { path: '/' }).action).toBe('allow')
    expect(evaluateAuthRoute(auth, { path: '/learn/5/fractions' }).action).toBe('allow')
    expect(evaluateAuthRoute(auth, { path: '/quiz' }).action).toBe('allow')
    expect(evaluateAuthRoute(auth, { path: '/results' }).action).toBe('allow')
    expect(evaluateAuthRoute(auth, { path: '/dashboard' }).action).toBe('allow')
    expect(evaluateAuthRoute(auth, { path: '/progress' }).action).toBe('allow')
  })

  it('redirects signed-in user away from /login to /dashboard', () => {
    const auth = useAuthStore()
    auth.user = { id: 'test-user-123', email: 'adventurer@mathquest.org' } as any

    const decision = evaluateAuthRoute(auth, { path: '/login' })
    expect(decision.action).toBe('redirect')
    expect(decision.to).toBe('/dashboard')
  })

  it('preserves return redirect query after login', () => {
    const auth = useAuthStore()
    auth.user = { id: 'test-user-123', email: 'adventurer@mathquest.org' } as any

    const decision = evaluateAuthRoute(auth, {
      path: '/login',
      query: { redirect: '/learn/6/geometry' },
    })
    expect(decision.action).toBe('redirect')
    expect(decision.to).toBe('/learn/6/geometry')
  })

  it('diverts newly registered user needing setup to /onboarding', () => {
    const auth = useAuthStore()
    auth.user = { id: 'new-user-456', email: 'fresh@mathquest.org' } as any
    auth.needsSetup = true

    const decision = evaluateAuthRoute(auth, { path: '/dashboard' })
    expect(decision.action).toBe('redirect')
    expect(decision.to).toBe('/onboarding')
  })
})
