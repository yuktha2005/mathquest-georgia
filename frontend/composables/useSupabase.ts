import { createClient, type SupabaseClient } from '@supabase/supabase-js'

let supabaseInstance: SupabaseClient | null = null

/**
 * Returns a configured Supabase client singleton, or null if credentials are not configured.
 */
export function useSupabase(): SupabaseClient | null {
  let url = ''
  let key = ''

  try {
    if (typeof useRuntimeConfig === 'function') {
      const config = useRuntimeConfig()
      url = (config.public?.supabaseUrl || '') as string
      key = (config.public?.supabaseKey || '') as string
    }
  } catch {
    // Non-Nuxt test runner environment
  }

  if (!url && typeof process !== 'undefined' && process.env) {
    url = process.env.NUXT_PUBLIC_SUPABASE_URL || ''
  }
  if (!key && typeof process !== 'undefined' && process.env) {
    key = process.env.NUXT_PUBLIC_SUPABASE_KEY || ''
  }

  if (!url || !key) {
    return null
  }

  if (!supabaseInstance) {
    supabaseInstance = createClient(url, key, {
      auth: {
        persistSession: true,
        autoRefreshToken: true,
        detectSessionInUrl: true,
      },
    })
  }

  return supabaseInstance
}
