import { useAuthStore } from '~/stores/auth'

export default defineNuxtRouteMiddleware(async (to) => {
  // Only execute on client side where localStorage and Supabase session exist
  if (!import.meta.client) return

  const authStore = useAuthStore()

  // Ensure auth is initialized from localStorage/Supabase before checking routes
  if (!authStore.isInitialized) {
    await authStore.init()
  }

  const publicRoutes = ['/login', '/signup', '/forgot', '/eval']
  const isPublicRoute = publicRoutes.includes(to.path)

  // 1. If signed-in user tries to visit /login or /signup, redirect them to dashboard
  if (authStore.isAuthenticated) {
    if (to.path === '/login' || to.path === '/signup') {
      const redirectTarget = (to.query.redirect as string) || '/dashboard'
      return navigateTo(redirectTarget)
    }

    // If new user still needs first-time setup, divert them to onboarding
    if (authStore.needsSetup && to.path !== '/onboarding') {
      return navigateTo('/onboarding')
    }

    return
  }

  // 2. Unauthenticated: protect all internal routes, redirecting to /signup
  if (!isPublicRoute) {
    return navigateTo({
      path: '/signup',
      query: {
        redirect: to.fullPath !== '/' ? to.fullPath : undefined,
      },
    })
  }
})
