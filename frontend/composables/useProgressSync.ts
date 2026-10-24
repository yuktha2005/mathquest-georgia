import { ref } from 'vue'
import { useSupabase } from '~/composables/useSupabase'
import { useAuthStore } from '~/stores/auth'
import { useSessionStore, type ActivityItem } from '~/stores/session'

const PENDING_SYNC_KEY = 'mathquest_pending_cloud_sync_v1'
const GUEST_BACKUP_KEY = 'mathquest_guest_backup_before_auth'

const BADGE_MAP: Record<string, { name: string; desc: string; emoji: string }> = {
  'First Steps': { name: 'First Steps', desc: 'Answered your first question', emoji: '🎯' },
  '5-Streak': { name: '5-Streak', desc: '5 correct answers in a row', emoji: '🔥' },
  'Fraction Master': { name: 'Fraction Master', desc: 'Mastered fraction operations', emoji: '🍰' },
  'Decimal Dynamo': { name: 'Decimal Dynamo', desc: 'Mastered decimal computation', emoji: '🎯' },
  'Ratio Ranger': { name: 'Ratio Ranger', desc: 'Mastered ratios & unit rates', emoji: '⚖️' },
  'Geometry Giant': { name: 'Geometry Giant', desc: 'Mastered 2D & 3D geometric figures', emoji: '📐' },
  'CBSE Champion': { name: 'CBSE Champion', desc: 'Mastered CBSE mathematics', emoji: '🇮🇳' },
  'Tenacious Thinker': { name: 'Tenacious Thinker', desc: 'Solved a Hard-tier challenge', emoji: '⚡' },
  'Comeback Kid': { name: 'Comeback Kid', desc: 'Recovered immediately after an incorrect answer', emoji: '🌟' },
  'Perfect Round': { name: 'Perfect Round', desc: '100% accuracy across a full practice round', emoji: '🏆' },
}

export function useProgressSync() {
  const supabase = useSupabase()
  const authStore = useAuthStore()
  const sessionStore = useSessionStore()

  const isSyncing = ref(false)
  const syncError = ref<string | null>(null)
  const hasUnsavedProgress = ref(false)

  // Check if there are local unsaved items
  if (import.meta.client) {
    const pending = localStorage.getItem(PENDING_SYNC_KEY)
    hasUnsavedProgress.value = !!pending
  }

  /**
   * Save a completed round into Supabase (or localStorage if guest or offline).
   */
  async function persistCompletedRound(roundStats?: {
    board?: string
    grade?: number
    topic?: string
    tier?: string
    roundScore?: number
  }): Promise<boolean> {
    const board = roundStats?.board || sessionStore.board
    const grade = roundStats?.grade || sessionStore.grade
    const topic = roundStats?.topic || sessionStore.topic
    const tier = roundStats?.tier || sessionStore.tier
    const roundScore = roundStats?.roundScore || sessionStore.roundRecords.reduce((sum, r) => sum + r.pointsEarned, 0)
    const accuracy = sessionStore.roundAccuracyPercent
    const correctCount = sessionStore.roundCorrectCount
    const totalQuestions = sessionStore.roundRecords.length

    // Record activity locally in store
    sessionStore.addActivity({
      topic,
      board,
      grade,
      tier,
      score: roundScore,
      accuracy_percent: accuracy,
      correct_count: correctCount,
      total_questions: totalQuestions,
      created_at: new Date().toISOString(),
    })

    // If student is playing as guest, store is already persisted to localStorage
    if (authStore.isGuest || !authStore.user) {
      sessionStore.saveToStorage()
      return true
    }

    // Authenticated user: persist to Supabase
    isSyncing.value = true
    syncError.value = null

    const sessionPayload = {
      user_id: authStore.user.id,
      board,
      grade,
      topic,
      tier,
      score: roundScore,
      streak: sessionStore.streak,
      best_streak: sessionStore.bestStreak,
      total_questions: totalQuestions,
      correct_count: correctCount,
      accuracy_percent: accuracy,
      completed: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }

    try {
      if (!supabase) {
        throw new Error('Supabase client is not connected')
      }

      // 1. Insert Session
      const { data: sessionData, error: sessionErr } = await supabase
        .from('sessions')
        .insert(sessionPayload)
        .select('id')
        .single()

      if (sessionErr) throw sessionErr
      const sessionId = sessionData.id

      // 2. Insert Answers
      if (sessionStore.roundRecords.length > 0) {
        const answersPayload = sessionStore.roundRecords.map((r) => ({
          session_id: sessionId,
          user_id: authStore.user!.id,
          question_id: r.question.id,
          topic,
          grade,
          tier: r.question.tier || tier,
          selected_option_id: r.selectedOptionId,
          correct_option_id: r.question.correct_option_id,
          is_correct: r.isCorrect,
          points_earned: r.pointsEarned,
          misconception_tag: r.misconceptionTag || null,
          explanation: r.explanation || r.question.explanation || '',
          created_at: new Date().toISOString(),
        }))

        const { error: answersErr } = await supabase
          .from('answers')
          .insert(answersPayload)

        if (answersErr) console.warn('[Sync] Answers insert error:', answersErr)
      }

      // 3. Upsert Mastery
      const topicMastery = sessionStore.mastery[topic] || 50
      const { error: masteryErr } = await supabase
        .from('mastery')
        .upsert(
          {
            user_id: authStore.user.id,
            board,
            topic,
            grade,
            mastery_score: topicMastery,
            total_attempted: totalQuestions,
            total_correct: correctCount,
            last_practiced_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
          { onConflict: 'user_id,board,topic,grade' }
        )

      if (masteryErr) console.warn('[Sync] Mastery upsert error:', masteryErr)

      // 4. Insert Badges
      if (sessionStore.badges.length > 0) {
        const badgesPayload = sessionStore.badges.map((bId) => {
          const info = BADGE_MAP[bId] || { name: bId, desc: 'Achievement unlocked', emoji: '🏆' }
          return {
            user_id: authStore.user!.id,
            badge_id: bId.toLowerCase().replace(/[\s-]/g, '_'),
            badge_name: info.name,
            badge_description: info.desc,
            icon_emoji: info.emoji,
            unlocked_at: new Date().toISOString(),
          }
        })

        const { error: badgesErr } = await supabase
          .from('badges')
          .upsert(badgesPayload, { onConflict: 'user_id,badge_id' })

        if (badgesErr) console.warn('[Sync] Badges upsert error:', badgesErr)
      }

      // 5. Update Profile Total Score
      await supabase
        .from('profiles')
        .update({
          total_score: sessionStore.score,
          updated_at: new Date().toISOString(),
        })
        .eq('id', authStore.user.id)

      // Successfully saved to cloud! Clear pending cache
      if (import.meta.client) {
        localStorage.removeItem(PENDING_SYNC_KEY)
      }
      hasUnsavedProgress.value = false
      return true
    } catch (err: any) {
      console.error('[Sync] Supabase save error:', err)
      syncError.value = err.message || 'Network error saving to cloud'
      hasUnsavedProgress.value = true

      // Save locally to pending sync key so student never loses data
      if (import.meta.client) {
        localStorage.setItem(PENDING_SYNC_KEY, JSON.stringify(sessionPayload))
      }
      return false
    } finally {
      isSyncing.value = false
    }
  }

  /**
   * Retry saving any unsaved progress to cloud.
   */
  async function retryPendingSync(): Promise<boolean> {
    if (!import.meta.client || !authStore.user) return false
    const raw = localStorage.getItem(PENDING_SYNC_KEY)
    if (!raw) {
      hasUnsavedProgress.value = false
      return true
    }

    try {
      const pendingData = JSON.parse(raw)
      return await persistCompletedRound({
        board: pendingData.board,
        grade: pendingData.grade,
        topic: pendingData.topic,
        tier: pendingData.tier,
        roundScore: pendingData.score,
      })
    } catch (e) {
      return false
    }
  }

  /**
   * Loads user cloud progress from Supabase into Pinia store upon sign in.
   */
  async function loadUserCloudProgress() {
    if (!authStore.user || !supabase) return

    isSyncing.value = true
    try {
      // 1. Load Mastery
      const { data: masteryRows, error: masteryErr } = await supabase
        .from('mastery')
        .select('*')
        .eq('user_id', authStore.user.id)

      if (!masteryErr && masteryRows) {
        masteryRows.forEach((row) => {
          if (row.topic && typeof row.mastery_score === 'number') {
            sessionStore.mastery[row.topic] = row.mastery_score
          }
        })
      }

      // 2. Load Badges
      const { data: badgeRows, error: badgeErr } = await supabase
        .from('badges')
        .select('*')
        .eq('user_id', authStore.user.id)

      if (!badgeErr && badgeRows) {
        badgeRows.forEach((row) => {
          if (row.badge_name && !sessionStore.badges.includes(row.badge_name)) {
            sessionStore.badges.push(row.badge_name)
          }
        })
      }

      // 3. Load Recent Sessions (Activity history)
      const { data: sessionRows, error: sessionErr } = await supabase
        .from('sessions')
        .select('*')
        .eq('user_id', authStore.user.id)
        .order('created_at', { ascending: false })
        .limit(10)

      if (!sessionErr && sessionRows) {
        sessionStore.recentActivities = sessionRows.map((s) => ({
          id: s.id,
          topic: s.topic,
          board: s.board,
          grade: s.grade,
          tier: s.tier,
          score: s.score,
          accuracy_percent: Number(s.accuracy_percent) || 0,
          correct_count: s.correct_count,
          total_questions: s.total_questions,
          created_at: s.created_at,
        }))
      }

      // 4. Load Profile Score
      if (authStore.profile?.total_score) {
        sessionStore.score = Math.max(sessionStore.score, authStore.profile.total_score)
      }

      sessionStore.saveToStorage()
    } catch (err) {
      console.warn('[Sync] Error loading cloud progress:', err)
    } finally {
      isSyncing.value = false
    }
  }

  /**
   * Check if there is guest progress saved in browser that can be merged.
   */
  function hasGuestProgressToImport(): boolean {
    if (!import.meta.client) return false
    const backupRaw = localStorage.getItem(GUEST_BACKUP_KEY)
    if (backupRaw) {
      try {
        const parsed = JSON.parse(backupRaw)
        return (parsed.score && parsed.score > 0) || (parsed.badges && parsed.badges.length > 0)
      } catch (e) {
        return false
      }
    }
    return false
  }

  /**
   * Move guest progress into the signed-in Supabase user account.
   */
  async function importGuestProgress(): Promise<boolean> {
    if (!import.meta.client || !authStore.user || !supabase) return false

    const backupRaw = localStorage.getItem(GUEST_BACKUP_KEY)
    if (!backupRaw) return false

    isSyncing.value = true
    try {
      const guestData = JSON.parse(backupRaw)

      // 1. Merge score & badges into session store
      if (typeof guestData.score === 'number') {
        sessionStore.score += guestData.score
      }
      if (Array.isArray(guestData.badges)) {
        guestData.badges.forEach((b: string) => {
          if (!sessionStore.badges.includes(b)) {
            sessionStore.badges.push(b)
          }
        })
      }
      if (guestData.mastery) {
        sessionStore.mastery = { ...sessionStore.mastery, ...guestData.mastery }
      }

      // 2. Save merged progress to Supabase
      await persistCompletedRound({
        board: guestData.board || sessionStore.board,
        grade: guestData.grade || sessionStore.grade,
        topic: guestData.topic || sessionStore.topic,
        tier: guestData.tier || sessionStore.tier,
        roundScore: guestData.score || 0,
      })

      // 3. Clear guest backup key
      localStorage.removeItem(GUEST_BACKUP_KEY)
      return true
    } catch (err) {
      console.error('[Sync] Error importing guest progress:', err)
      return false
    } finally {
      isSyncing.value = false
    }
  }

  return {
    isSyncing,
    syncError,
    hasUnsavedProgress,
    persistCompletedRound,
    retryPendingSync,
    loadUserCloudProgress,
    hasGuestProgressToImport,
    importGuestProgress,
  }
}
