import { defineStore } from 'pinia'
import type { AnswerResultResponse, Question } from '~/composables/useApi'

export type GradeLevel = 5 | 6
export type TopicType = 'fractions' | 'decimals' | 'ratios' | 'geometry'
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

export interface SessionState {
  grade: GradeLevel
  topic: TopicType
  tier: TierType
  score: number
  streak: number
  bestStreak: number
  history: boolean[]
  mastery: Record<TopicType, number>
  badges: string[]
  roundQuestions: Question[]
  currentIndex: number
  roundRecords: RoundAnswerRecord[]
  lastResult: AnswerResultResponse | null
}

const STORAGE_KEY = 'mathquest_georgia_session_v1'

export const useSessionStore = defineStore('session', {
  state: (): SessionState => ({
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
    },
    badges: [],
    roundQuestions: [],
    currentIndex: 0,
    roundRecords: [],
    lastResult: null,
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
  },

  actions: {
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
      }
      this.badges = []
      this.roundQuestions = []
      this.currentIndex = 0
      this.roundRecords = []
      this.lastResult = null
      this.saveToStorage()
    },

    saveToStorage() {
      if (import.meta.client) {
        try {
          const serialized = JSON.stringify({
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
          }
        } catch (e) {
          console.warn('Failed to restore session from localStorage:', e)
        }
      }
    },
  },
})
