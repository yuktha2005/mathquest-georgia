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

  // 2. Unauthenticated: protect all internal routes, redirecting to /signup
  if (!isPublicRoute) {
    return {
      action: 'redirect',
      to: {
        path: '/signup',
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

  it('redirects unauthenticated user from protected /dashboard to /signup', () => {
    const auth = useAuthStore()
    const decision = evaluateAuthRoute(auth, { path: '/dashboard', fullPath: '/dashboard' })

    expect(decision.action).toBe('redirect')
    expect(decision.to).toEqual({
      path: '/signup',
      query: { redirect: '/dashboard' },
    })
  })

  it('redirects unauthenticated user from /quiz to /signup with deep-link redirect', () => {
    const auth = useAuthStore()
    const decision = evaluateAuthRoute(auth, {
      path: '/quiz',
      fullPath: '/quiz?board=georgia&grade=5&topic=fractions',
    })

    expect(decision.action).toBe('redirect')
    expect(decision.to).toEqual({
      path: '/signup',
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

  it('redirects unauthenticated user attempting to access learning routes to /signup', () => {
    const auth = useAuthStore()
    expect(evaluateAuthRoute(auth, { path: '/' }).action).toBe('redirect')
    expect(evaluateAuthRoute(auth, { path: '/' }).to).toEqual({ path: '/signup', query: { redirect: undefined } })
    expect(evaluateAuthRoute(auth, { path: '/learn/5/fractions', fullPath: '/learn/5/fractions' }).action).toBe('redirect')
    expect(evaluateAuthRoute(auth, { path: '/quiz', fullPath: '/quiz' }).action).toBe('redirect')
    expect(evaluateAuthRoute(auth, { path: '/results', fullPath: '/results' }).action).toBe('redirect')
    expect(evaluateAuthRoute(auth, { path: '/dashboard', fullPath: '/dashboard' }).action).toBe('redirect')
    expect(evaluateAuthRoute(auth, { path: '/progress', fullPath: '/progress' }).action).toBe('redirect')
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
