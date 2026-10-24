import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '../stores/auth'

describe('Auth Store (useAuthStore)', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    vi.clearAllMocks()
  })

  it('initializes in unauthenticated state by default when no storage exists', () => {
    const auth = useAuthStore()
    expect(auth.user).toBeNull()
    expect(auth.isGuest).toBe(false)
    expect(auth.isAuthenticated).toBe(false)
    expect(auth.displayName).toBe('Math Adventurer')
  })

  it('continueAsGuest sets isGuest to true and writes flag to localStorage', () => {
    const auth = useAuthStore()
    auth.continueAsGuest()

    expect(auth.isGuest).toBe(true)
    expect(auth.isAuthenticated).toBe(false)
    expect(auth.user).toBeNull()
    expect(localStorage.getItem('mathquest_is_guest')).toBe('true')
  })

  it('restores guest mode on init() when localStorage flag is set', async () => {
    localStorage.setItem('mathquest_is_guest', 'true')
    const auth = useAuthStore()
    await auth.init()

    expect(auth.isGuest).toBe(true)
    expect(auth.isInitialized).toBe(true)
  })

  it('signOut clears user, profile, guest mode and removes storage keys', async () => {
    const auth = useAuthStore()
    auth.continueAsGuest()
    expect(auth.isGuest).toBe(true)

    await auth.signOut()

    expect(auth.user).toBeNull()
    expect(auth.profile).toBeNull()
    expect(auth.isGuest).toBe(false)
    expect(auth.isAuthenticated).toBe(false)
    expect(localStorage.getItem('mathquest_guest_mode')).toBeNull()
  })

  it('saveSetupProfile updates user profile, grade, board, and displayName', async () => {
    const auth = useAuthStore()
    auth.continueAsGuest()

    const result = await auth.saveSetupProfile({
      displayName: 'Falcon Hero',
      grade: 6,
      board: 'cbse',
    })

    expect(result).toBe(true)
    expect(auth.needsSetup).toBe(false)
  })

  it('handles signIn error and sets authError', async () => {
    const auth = useAuthStore()
    await expect(auth.signIn('invalid@mathquest.org', 'short')).rejects.toThrow()
    expect(auth.authError).toBeTruthy()
  })
})
