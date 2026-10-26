import { defineStore } from 'pinia'
import type { User } from '@supabase/supabase-js'
import { useSupabase } from '~/composables/useSupabase'
import { useSessionStore } from '~/stores/session'

export interface UserProfile {
  id: string
  user_id: string
  email: string | null
  display_name: string
  avatar_url?: string | null
  grade: 5 | 6
  curriculum_board: 'georgia' | 'cbse' | string
  total_score: number
}

export interface AuthState {
  user: User | null
  profile: UserProfile | null
  isGuest: boolean
  isLoading: boolean
  isInitialized: boolean
  needsSetup: boolean
  authError: string | null
}

const GUEST_STORAGE_KEY = 'mathquest_is_guest'
const LOCAL_SESSION_KEY = 'mathquest_local_session'
const LOCAL_ACCOUNTS_KEY = 'mathquest_local_accounts'

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: null,
    profile: null,
    isGuest: false,
    isLoading: false,
    isInitialized: false,
    needsSetup: false,
    authError: null,
  }),

  getters: {
    isAuthenticated: (state): boolean => !!state.user,
    hasAccess: (state): boolean => !!state.user || state.isGuest,
    displayName: (state): string => {
      if (state.profile?.display_name) return state.profile.display_name
      if (state.user?.user_metadata?.display_name) return state.user.user_metadata.display_name
      if (state.user?.email) return state.user.email.split('@')[0]
      if (state.isGuest) return 'Guest Adventurer'
      return 'Math Adventurer'
    },
    userGrade: (state): 5 | 6 => (state.profile?.grade === 6 ? 6 : 5),
    userBoard: (state): string => state.profile?.curriculum_board || 'georgia',
  },

  actions: {
    /**
     * Initializes authentication state on application load.
     * Checks client-side localStorage for local session and Supabase session.
     */
    async init() {
      if (this.isInitialized) return
      this.isLoading = true

      try {
        if (import.meta.client) {
          const guestSaved = localStorage.getItem(GUEST_STORAGE_KEY)
          if (guestSaved === 'true') {
            this.isGuest = true
          }

          // Restore local storage session if exists
          const localSession = localStorage.getItem(LOCAL_SESSION_KEY)
          if (localSession) {
            try {
              const parsedUser = JSON.parse(localSession)
              if (parsedUser && parsedUser.id) {
                this.user = parsedUser
                this.isGuest = false
                const accounts = JSON.parse(localStorage.getItem(LOCAL_ACCOUNTS_KEY) || '{}')
                const account = Object.values(accounts).find((acc: any) => acc.id === parsedUser.id) as any
                if (account) {
                  this.profile = {
                    id: account.id,
                    user_id: account.id,
                    email: account.email,
                    display_name: account.displayName,
                    grade: account.grade,
                    curriculum_board: account.board,
                    total_score: account.totalScore || 0,
                  }
                  const sessionStore = useSessionStore()
                  if (account.grade) sessionStore.setGrade(account.grade as 5 | 6)
                  if (account.board) sessionStore.setBoard(account.board)
                }
              }
            } catch (e) {
              console.warn('[MathQuest Auth] Failed to restore local session:', e)
            }
          }
        }

        const supabase = useSupabase()
        if (supabase) {
          const { data, error } = await supabase.auth.getSession()
          if (!error && data?.session?.user) {
            this.user = data.session.user
            this.isGuest = false
            await this.fetchProfile(data.session.user.id)
            try {
              const { loadUserCloudProgress } = useProgressSync()
              await loadUserCloudProgress()
            } catch (e) {
              console.warn('[MathQuest Auth] Cloud progress load warning:', e)
            }
          }

          // Subscribe to auth state updates
          supabase.auth.onAuthStateChange(async (event, session) => {
            if (session?.user) {
              this.user = session.user
              this.isGuest = false
              await this.fetchProfile(session.user.id)
              if (event === 'SIGNED_IN') {
                try {
                  const { loadUserCloudProgress } = useProgressSync()
                  await loadUserCloudProgress()
                } catch (e) {
                  console.warn('[MathQuest Auth] Cloud progress load warning:', e)
                }
              }
            } else if (!this.isGuest && !localStorage.getItem(LOCAL_SESSION_KEY)) {
              this.user = null
              this.profile = null
            }
          })
        }
      } catch (err) {
        console.warn('[MathQuest Auth] Initialization notice:', err)
      } finally {
        this.isLoading = false
        this.isInitialized = true
      }
    },

    /**
     * Fetches user profile from Supabase profiles table.
     */
    async fetchProfile(userId: string) {
      const supabase = useSupabase()
      if (!supabase) return

      try {
        const { data, error } = await supabase
          .from('profiles')
          .select('*')
          .eq('id', userId)
          .maybeSingle()

        if (!error && data) {
          this.profile = data as UserProfile
          // If display name or grade is not set, flag for setup
          if (!data.display_name || data.display_name === 'Student' || !data.grade) {
            this.needsSetup = true
          } else {
            this.needsSetup = false
            // Sync with session store
            const sessionStore = useSessionStore()
            if (data.grade) sessionStore.setGrade(data.grade as 5 | 6)
            if (data.curriculum_board) sessionStore.setBoard(data.curriculum_board)
          }
        } else {
          // Profile row not found yet (trigger might be delayed or table fresh)
          this.needsSetup = true
        }
      } catch (err) {
        console.error('[MathQuest Auth] Error fetching profile:', err)
      }
    },

    /**
     * Sign in with Email and Password.
     */
    async signIn(email: string, password: string): Promise<boolean> {
      this.isLoading = true
      this.authError = null

      const supabase = useSupabase()

      if (supabase) {
        try {
          const { data, error } = await supabase.auth.signInWithPassword({
            email: email.trim(),
            password,
          })

          if (!error && data.user) {
            this.user = data.user
            this.isGuest = false
            if (import.meta.client) {
              localStorage.removeItem(GUEST_STORAGE_KEY)
            }
            await this.fetchProfile(data.user.id)
            try {
              const { loadUserCloudProgress } = useProgressSync()
              await loadUserCloudProgress()
            } catch (e) {
              console.warn('[MathQuest Auth] Cloud progress load warning:', e)
            }
            return true
          }

          if (error) {
            let friendly = error.message
            const lower = error.message.toLowerCase()
            if (lower.includes('invalid login credentials') || lower.includes('invalid grant')) {
              friendly = 'Incorrect email or password. Please verify your details or use "Forgot password".'
            } else if (lower.includes('email not confirmed')) {
              friendly = 'Your email is not confirmed yet. Check your inbox or disable email confirmation in Supabase.'
            } else if (lower.includes('network') || lower.includes('failed to fetch')) {
              friendly = 'Network connection error. Could not reach authentication server. Please check your internet connection.'
            } else if (lower.includes('rate limit') || lower.includes('too many requests')) {
              friendly = 'Too many attempts. Please wait a few moments before trying again.'
            }
            this.authError = friendly
            throw new Error(friendly)
          }
        } catch (supabaseErr: any) {
          // If Supabase failed or local accounts exist, check local accounts
          if (import.meta.client) {
            const accounts = JSON.parse(localStorage.getItem(LOCAL_ACCOUNTS_KEY) || '{}')
            const account = accounts[email.trim().toLowerCase()]
            if (account && account.password === password) {
              const localUser: any = {
                id: account.id,
                email: account.email,
                user_metadata: { display_name: account.displayName },
                app_metadata: {},
                aud: 'authenticated',
                created_at: new Date().toISOString(),
              }
              localStorage.setItem(LOCAL_SESSION_KEY, JSON.stringify(localUser))
              this.user = localUser
              this.isGuest = false
              this.profile = {
                id: account.id,
                user_id: account.id,
                email: account.email,
                display_name: account.displayName,
                grade: account.grade,
                curriculum_board: account.board,
                total_score: account.totalScore || 0,
              }
              const sessionStore = useSessionStore()
              if (account.grade) sessionStore.setGrade(account.grade as 5 | 6)
              if (account.board) sessionStore.setBoard(account.board)
              return true
            }
          }
          this.authError = supabaseErr.message
          throw supabaseErr
        } finally {
          this.isLoading = false
        }
      }

      // Supabase is not configured: authenticate against local storage accounts
      try {
        if (import.meta.client) {
          const accounts = JSON.parse(localStorage.getItem(LOCAL_ACCOUNTS_KEY) || '{}')
          const account = accounts[email.trim().toLowerCase()]

          if (!account || account.password !== password) {
            const friendly = 'Incorrect email or password. Please verify your details or create a new account.'
            this.authError = friendly
            throw new Error(friendly)
          }

          const localUser: any = {
            id: account.id,
            email: account.email,
            user_metadata: { display_name: account.displayName },
            app_metadata: {},
            aud: 'authenticated',
            created_at: new Date().toISOString(),
          }

          localStorage.setItem(LOCAL_SESSION_KEY, JSON.stringify(localUser))
          this.user = localUser
          this.isGuest = false
          this.profile = {
            id: account.id,
            user_id: account.id,
            email: account.email,
            display_name: account.displayName,
            grade: account.grade,
            curriculum_board: account.board,
            total_score: account.totalScore || 0,
          }
          this.needsSetup = false
          const sessionStore = useSessionStore()
          if (account.grade) sessionStore.setGrade(account.grade as 5 | 6)
          if (account.board) sessionStore.setBoard(account.board)
          return true
        }

        const friendly = 'Incorrect email or password. Please verify your details.'
        this.authError = friendly
        throw new Error(friendly)
      } finally {
        this.isLoading = false
      }
    },

    /**
     * Sign up with Email and Password.
     */
    async signUp(email: string, password: string, metadata: Record<string, any> = {}): Promise<boolean> {
      this.isLoading = true
      this.authError = null

      const supabase = useSupabase()

      if (supabase) {
        try {
          const { data, error } = await supabase.auth.signUp({
            email: email.trim(),
            password,
            options: {
              data: metadata,
            },
          })

          if (error) {
            let friendly = error.message
            const lower = error.message.toLowerCase()
            if (lower.includes('already registered') || lower.includes('user already exists')) {
              friendly = 'An account with this email already exists. Try signing in instead.'
            } else if (lower.includes('at least 6 characters') || lower.includes('password should be')) {
              friendly = 'Password must be at least 6 characters long.'
            } else if (lower.includes('network') || lower.includes('failed to fetch')) {
              friendly = 'Network connection error. Please check your internet connection.'
            }
            this.authError = friendly
            throw new Error(friendly)
          }

          if (data.user) {
            this.user = data.user
            this.isGuest = false
            this.needsSetup = true
            if (import.meta.client) {
              const existingSession = localStorage.getItem('mathquest_multi_curriculum_session_v2')
              if (existingSession) {
                localStorage.setItem('mathquest_guest_backup_before_auth', existingSession)
              }
              localStorage.removeItem(GUEST_STORAGE_KEY)
            }
            return true
          }
        } catch (supabaseErr: any) {
          this.authError = supabaseErr.message
          throw supabaseErr
        } finally {
          this.isLoading = false
        }
      }

      // Supabase not configured: create local account
      try {
        if (import.meta.client) {
          const accounts = JSON.parse(localStorage.getItem(LOCAL_ACCOUNTS_KEY) || '{}')
          const normalizedEmail = email.trim().toLowerCase()

          if (accounts[normalizedEmail]) {
            const friendly = 'An account with this email already exists. Try signing in instead.'
            this.authError = friendly
            throw new Error(friendly)
          }

          const localId = 'local_' + Date.now() + '_' + Math.random().toString(36).substring(2, 8)
          const localUser: any = {
            id: localId,
            email: email.trim(),
            user_metadata: { display_name: email.trim().split('@')[0], ...metadata },
            app_metadata: {},
            aud: 'authenticated',
            created_at: new Date().toISOString(),
          }

          accounts[normalizedEmail] = {
            id: localId,
            email: email.trim(),
            password: password,
            displayName: email.trim().split('@')[0],
            grade: 5,
            board: 'georgia',
            totalScore: 0,
          }

          localStorage.setItem(LOCAL_ACCOUNTS_KEY, JSON.stringify(accounts))
          localStorage.setItem(LOCAL_SESSION_KEY, JSON.stringify(localUser))

          this.user = localUser
          this.isGuest = false
          this.needsSetup = true
          return true
        }

        return false
      } finally {
        this.isLoading = false
      }
    },

    /**
     * Save the first-time setup onboarding data to Supabase profiles.
     */
    async saveSetupProfile(data: { displayName: string; grade: 5 | 6; board: string }): Promise<boolean> {
      if (!this.user) {
        // If guest, apply to local session
        const sessionStore = useSessionStore()
        sessionStore.setGrade(data.grade)
        sessionStore.setBoard(data.board)
        this.needsSetup = false
        return true
      }

      this.isLoading = true
      const supabase = useSupabase()

      if (!supabase || this.user.id.startsWith('local_')) {
        this.profile = {
          ...(this.profile || { id: this.user.id, user_id: this.user.id, email: this.user.email, total_score: 0 }),
          display_name: data.displayName.trim() || 'Student',
          grade: data.grade,
          curriculum_board: data.board,
        }
        if (import.meta.client) {
          const accounts = JSON.parse(localStorage.getItem(LOCAL_ACCOUNTS_KEY) || '{}')
          const normalizedEmail = (this.user.email || '').trim().toLowerCase()
          if (accounts[normalizedEmail]) {
            accounts[normalizedEmail].displayName = data.displayName.trim() || 'Student'
            accounts[normalizedEmail].grade = data.grade
            accounts[normalizedEmail].board = data.board
            localStorage.setItem(LOCAL_ACCOUNTS_KEY, JSON.stringify(accounts))
          }
        }
        this.needsSetup = false
        const sessionStore = useSessionStore()
        sessionStore.setGrade(data.grade)
        sessionStore.setBoard(data.board)
        this.isLoading = false
        return true
      }

      try {
        const payload = {
          id: this.user.id,
          user_id: this.user.id,
          email: this.user.email,
          display_name: data.displayName.trim() || 'Student',
          grade: data.grade,
          curriculum_board: data.board,
          updated_at: new Date().toISOString(),
        }

        const { error } = await supabase
          .from('profiles')
          .upsert(payload, { onConflict: 'id' })

        if (error) {
          console.error('[MathQuest Auth] Error updating profile:', error)
          throw new Error(error.message)
        }

        this.profile = {
          ...(this.profile || { id: this.user.id, user_id: this.user.id, email: this.user.email, total_score: 0 }),
          display_name: data.displayName.trim() || 'Student',
          grade: data.grade,
          curriculum_board: data.board,
        }

        this.needsSetup = false

        // Sync with session store
        const sessionStore = useSessionStore()
        sessionStore.setGrade(data.grade)
        sessionStore.setBoard(data.board)
        return true
      } finally {
        this.isLoading = false
      }
    },

    /**
     * Continue as a Guest (no Supabase account required).
     * Maintains all gamified learning and quiz features without friction.
     */
    continueAsGuest() {
      this.isGuest = true
      this.user = null
      this.profile = null
      this.needsSetup = false
      this.authError = null
      if (import.meta.client) {
        localStorage.setItem(GUEST_STORAGE_KEY, 'true')
      }
    },

    /**
     * Sign out current user and clear sessions.
     */
    async signOut() {
      this.isLoading = true
      try {
        const supabase = useSupabase()
        if (supabase) {
          await supabase.auth.signOut()
        }
      } catch (err) {
        console.warn('[MathQuest Auth] Sign out notice:', err)
      } finally {
        this.user = null
        this.profile = null
        this.isGuest = false
        this.needsSetup = false
        this.authError = null
        if (import.meta.client) {
          localStorage.removeItem(LOCAL_SESSION_KEY)
          localStorage.removeItem(GUEST_STORAGE_KEY)
        }
        if (typeof useRouter === 'function') {
          try {
            const router = useRouter()
            router.push('/login')
          } catch {
            // Nuxt context not active
          }
        }
      }
    },

    /**
     * Send password reset email.
     */
    async resetPassword(email: string): Promise<boolean> {
      this.isLoading = true
      this.authError = null

      const supabase = useSupabase()
      if (!supabase) {
        this.isLoading = false
        throw new Error('Supabase is not configured.')
      }

      try {
        const { error } = await supabase.auth.resetPasswordForEmail(email.trim(), {
          redirectTo: import.meta.client ? `${window.location.origin}/login` : undefined,
        })

        if (error) {
          this.authError = error.message
          throw new Error(error.message)
        }
        return true
      } finally {
        this.isLoading = false
      }
    },
  },
})
