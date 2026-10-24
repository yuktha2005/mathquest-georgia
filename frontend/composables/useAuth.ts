import { computed } from 'vue'
import { useAuthStore } from '~/stores/auth'

/**
 * Composable wrapper around the Pinia auth store for convenient component usage.
 */
export function useAuth() {
  const authStore = useAuthStore()

  return {
    user: computed(() => authStore.user),
    profile: computed(() => authStore.profile),
    isGuest: computed(() => authStore.isGuest),
    isLoading: computed(() => authStore.isLoading),
    isInitialized: computed(() => authStore.isInitialized),
    needsSetup: computed(() => authStore.needsSetup),
    authError: computed(() => authStore.authError),
    displayName: computed(() => authStore.displayName),
    isAuthenticated: computed(() => authStore.isAuthenticated),
    hasAccess: computed(() => authStore.hasAccess),
    userGrade: computed(() => authStore.userGrade),
    userBoard: computed(() => authStore.userBoard),

    // Actions
    signIn: (email: string, pass: string) => authStore.signIn(email, pass),
    signUp: (email: string, pass: string, meta?: Record<string, any>) => authStore.signUp(email, pass, meta),
    signOut: () => authStore.signOut(),
    continueAsGuest: () => authStore.continueAsGuest(),
    saveSetupProfile: (data: { displayName: string; grade: 5 | 6; board: string }) => authStore.saveSetupProfile(data),
    resetPassword: (email: string) => authStore.resetPassword(email),
    init: () => authStore.init(),
  }
}
