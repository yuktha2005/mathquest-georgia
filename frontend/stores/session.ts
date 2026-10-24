import { defineStore } from 'pinia'
import type { AnswerResultResponse, Question } from '~/composables/useApi'

export type GradeLevel = 5 | 6
export type BoardType = 'georgia' | 'cbse' | string
export type TopicType = 'fractions' | 'decimals' | 'ratios' | 'geometry' | 'factors_multiples' | 'integers' | string
export type TierType = 'easy' | 'medium' | 'hard'

export interface RoundAnswerRecord {
  question: Question
  selectedOptionId: string
  isCorrect: boolean
  pointsEarned: number
  misconceptionTag?: string | null
  misconceptionFeedback?: string | null
  explanation: string
}

export interface ActivityItem {
  id?: string
  topic: string
  board: string
  grade: number
  tier: string
  score: number
  accuracy_percent: number
  correct_count: number
  total_questions: number
  created_at: string
}

export interface SessionState {
  board: BoardType
  grade: GradeLevel
  topic: TopicType
  tier: TierType
  score: number
  streak: number
  bestStreak: number
  history: boolean[]
  mastery: Record<string, number>
  badges: string[]
  roundQuestions: Question[]
  currentIndex: number
  roundRecords: RoundAnswerRecord[]
  lastResult: AnswerResultResponse | null
  recentActivities: ActivityItem[]
  lastTopic: string
  lastTier: string
  lastGrade: number
  dailyGoal: number
}

const STORAGE_KEY = 'mathquest_multi_curriculum_session_v2'

export const useSessionStore = defineStore('session', {
  state: (): SessionState => ({
    board: 'georgia',
    grade: 5,
    topic: 'fractions',
    tier: 'medium',
    score: 0,
    streak: 0,
    bestStreak: 0,
    history: [],
    mastery: {
      fractions: 50.0,
      decimals: 50.0,
      ratios: 50.0,
      geometry: 50.0,
      factors_multiples: 50.0,
      integers: 50.0,
    },
    badges: [],
    roundQuestions: [],
    currentIndex: 0,
    roundRecords: [],
    lastResult: null,
    recentActivities: [],
    lastTopic: 'fractions',
    lastTier: 'medium',
    lastGrade: 5,
    dailyGoal: 10,
  }),

  getters: {
    currentQuestion: (state): Question | null => {
      if (state.roundQuestions.length > 0 && state.currentIndex < state.roundQuestions.length) {
        return state.roundQuestions[state.currentIndex]
      }
      return null
    },
    isRoundComplete: (state): boolean => {
      return state.roundQuestions.length > 0 && state.currentIndex >= state.roundQuestions.length
    },
    totalQuestionsInRound: (state): number => state.roundQuestions.length,
    roundCorrectCount: (state): number => state.roundRecords.filter((r) => r.isCorrect).length,
    roundAccuracyPercent(): number {
      if (this.roundRecords.length === 0) return 0
      return Math.round((this.roundCorrectCount / this.roundRecords.length) * 100)
    },
    currentTopicMastery: (state): number => {
      return state.mastery[state.topic] || 50.0
    },
    boardTitle: (state): string => {
      if (state.board === 'cbse') {
        return 'CBSE Class 6 (NCERT Ganita Prakash)'
      }
      return `Georgia Standards of Excellence (MGSE) Grade ${state.grade}`
    },

    todayAnswersCount: (state): number => {
      const todayStr = new Date().toISOString().slice(0, 10)
      const fromRecent = state.recentActivities
        .filter((a) => a.created_at && a.created_at.slice(0, 10) === todayStr)
        .reduce((sum, a) => sum + (a.total_questions || 0), 0)
      const currentActive = state.roundRecords.length
      return fromRecent + currentActive
    },

    dailyGoalProgress: (state): number => {
      const todayStr = new Date().toISOString().slice(0, 10)
      const fromRecent = state.recentActivities
        .filter((a) => a.created_at && a.created_at.slice(0, 10) === todayStr)
        .reduce((sum, a) => sum + (a.total_questions || 0), 0)
      const total = fromRecent + state.roundRecords.length
      const goal = state.dailyGoal || 10
      return Math.min(Math.round((total / goal) * 100), 100)
    },

    lowestMasteryTopic: (state): { id: string; name: string; score: number; emoji: string; code: string } => {
      const candidateTopics =
        state.board === 'cbse'
          ? [
              { id: 'factors_multiples', name: 'Factors & Multiples', emoji: '🔢', code: 'CBSE6.MATH.01' },
              { id: 'fractions', name: 'Fractions', emoji: '🍰', code: 'CBSE6.MATH.02' },
              { id: 'decimals', name: 'Decimals', emoji: '🎯', code: 'CBSE6.MATH.03' },
              { id: 'integers', name: 'Integers', emoji: '❄️', code: 'CBSE6.MATH.04' },
              { id: 'ratios', name: 'Ratios & Proportions', emoji: '⚖️', code: 'CBSE6.MATH.05' },
              { id: 'geometry', name: 'Geometry', emoji: '📐', code: 'CBSE6.MATH.06' },
            ]
          : state.grade === 6
          ? [
              { id: 'fractions', name: 'Divide Fractions', emoji: '🍰', code: 'MGSE6.NS.1' },
              { id: 'decimals', name: 'Decimal Computation', emoji: '🎯', code: 'MGSE6.NS.3' },
              { id: 'ratios', name: 'Ratios & Unit Rates', emoji: '⚖️', code: 'MGSE6.RP.1' },
              { id: 'geometry', name: 'Area & Surface Area', emoji: '📐', code: 'MGSE6.G.1' },
            ]
          : [
              { id: 'fractions', name: 'Unlike Fractions', emoji: '🍰', code: 'MGSE5.NF.1' },
              { id: 'decimals', name: 'Decimals to Thousandths', emoji: '🎯', code: 'MGSE5.NBT.3' },
              { id: 'ratios', name: 'Coordinate Patterns', emoji: '⚖️', code: 'MGSE5.OA.3' },
              { id: 'geometry', name: 'Classify 2D Shapes', emoji: '📐', code: 'MGSE5.G.3' },
            ]

      const scored = candidateTopics.map((t) => ({
        ...t,
        score: state.mastery[t.id] !== undefined ? state.mastery[t.id] : 50.0,
      }))

      scored.sort((a, b) => a.score - b.score)
      return scored[0] || { id: 'fractions', name: 'Fractions', score: 50, emoji: '🍰', code: 'MGSE5.NF.1' }
    },

    continueAdventureCard: (state): { topic: string; tier: string; grade: number; board: string } => {
      return {
        topic: state.lastTopic || state.topic || 'fractions',
        tier: state.lastTier || state.tier || 'medium',
        grade: state.lastGrade || state.grade || 5,
        board: state.board || 'georgia',
      }
    },
  },

  actions: {
    addActivity(item: ActivityItem) {
      this.lastTopic = item.topic
      this.lastTier = item.tier
      this.lastGrade = item.grade
      this.recentActivities.unshift(item)
      if (this.recentActivities.length > 10) {
        this.recentActivities = this.recentActivities.slice(0, 10)
      }
      this.saveToStorage()
    },
    setBoard(board: BoardType) {
      this.board = board
      if (board === 'cbse') {
        this.grade = 6
        if (!['factors_multiples', 'fractions', 'decimals', 'integers', 'ratios', 'geometry'].includes(this.topic)) {
          this.topic = 'factors_multiples'
        }
      } else {
        if (!['fractions', 'decimals', 'ratios', 'geometry'].includes(this.topic)) {
          this.topic = 'fractions'
        }
      }
      this.saveToStorage()
    },

    setGrade(grade: GradeLevel) {
      this.grade = grade
      this.saveToStorage()
    },

    setTopic(topic: TopicType) {
      this.topic = topic
      this.saveToStorage()
    },

    setTier(tier: TierType) {
      this.tier = tier
      this.saveToStorage()
    },

    startRound(questions: Question[]) {
      this.roundQuestions = questions
      this.currentIndex = 0
      this.roundRecords = []
      this.lastResult = null
      this.saveToStorage()
    },

    recordAnswer(result: AnswerResultResponse, question: Question, selectedOptionId: string) {
      this.lastResult = result

      // Update score & streaks
      this.score += result.points
      this.streak = result.streak
      if (result.streak > this.bestStreak) {
        this.bestStreak = result.streak
      }

      // Update history & mastery
      this.history.push(result.is_correct)
      this.mastery[this.topic] = result.new_mastery
      this.tier = result.next_tier

      // Unlock new badges
      if (result.new_badges && result.new_badges.length > 0) {
        for (const badge of result.new_badges) {
          if (!this.badges.includes(badge)) {
            this.badges.push(badge)
          }
        }
      }

      // Record question answer detail
      this.roundRecords.push({
        question,
        selectedOptionId,
        isCorrect: result.is_correct,
        pointsEarned: result.points,
        misconceptionTag: result.misconception_tag,
        misconceptionFeedback: result.misconception_feedback,
        explanation: result.explanation,
      })

      this.saveToStorage()
    },

    nextQuestion() {
      this.currentIndex++
      this.saveToStorage()
    },

    resetRound() {
      this.roundQuestions = []
      this.currentIndex = 0
      this.roundRecords = []
      this.lastResult = null
      this.saveToStorage()
    },

    resetAllProgress() {
      this.score = 0
      this.streak = 0
      this.bestStreak = 0
      this.history = []
      this.mastery = {
        fractions: 50.0,
        decimals: 50.0,
        ratios: 50.0,
        geometry: 50.0,
        factors_multiples: 50.0,
        integers: 50.0,
      }
      this.badges = []
      this.roundQuestions = []
      this.currentIndex = 0
      this.roundRecords = []
      this.recentActivities = []
      this.lastTopic = 'fractions'
      this.lastTier = 'medium'
      this.lastResult = null
      this.saveToStorage()
    },

    saveToStorage() {
      if (import.meta.client) {
        try {
          const serialized = JSON.stringify({
            board: this.board,
            grade: this.grade,
            topic: this.topic,
            tier: this.tier,
            score: this.score,
            streak: this.streak,
            bestStreak: this.bestStreak,
            history: this.history,
            mastery: this.mastery,
            badges: this.badges,
            roundQuestions: this.roundQuestions,
            currentIndex: this.currentIndex,
            roundRecords: this.roundRecords,
            recentActivities: this.recentActivities,
            lastTopic: this.lastTopic,
            lastTier: this.lastTier,
            lastGrade: this.lastGrade,
          })
          localStorage.setItem(STORAGE_KEY, serialized)
        } catch (e) {
          console.warn('Failed to save session to localStorage:', e)
        }
      }
    },

    loadFromStorage() {
      if (import.meta.client) {
        try {
          const raw = localStorage.getItem(STORAGE_KEY)
          if (raw) {
            const data = JSON.parse(raw)
            if (data.board) this.board = data.board
            if (data.grade) this.grade = data.grade
            if (data.topic) this.topic = data.topic
            if (data.tier) this.tier = data.tier
            if (typeof data.score === 'number') this.score = data.score
            if (typeof data.streak === 'number') this.streak = data.streak
            if (typeof data.bestStreak === 'number') this.bestStreak = data.bestStreak
            if (Array.isArray(data.history)) this.history = data.history
            if (data.mastery) this.mastery = { ...this.mastery, ...data.mastery }
            if (Array.isArray(data.badges)) this.badges = data.badges
            if (Array.isArray(data.roundQuestions)) this.roundQuestions = data.roundQuestions
            if (typeof data.currentIndex === 'number') this.currentIndex = data.currentIndex
            if (Array.isArray(data.roundRecords)) this.roundRecords = data.roundRecords
            if (Array.isArray(data.recentActivities)) this.recentActivities = data.recentActivities
            if (data.lastTopic) this.lastTopic = data.lastTopic
            if (data.lastTier) this.lastTier = data.lastTier
            if (data.lastGrade) this.lastGrade = data.lastGrade
          }
        } catch (e) {
          console.warn('Failed to restore session from localStorage:', e)
        }
      }
    },
  },
})
