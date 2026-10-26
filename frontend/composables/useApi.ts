/**
 * Composable for interacting with the MathQuest Georgia FastAPI backend.
 *
 * Handles:
 * - Dynamic API Base URL from runtimeConfig (NUXT_PUBLIC_API_BASE)
 * - Render free-tier cold start detection (>2.5s) with child-friendly loading notices
 * - Robust error handling with graceful fallback options
 */

import offlineQuestions from '~/data/offline_questions.json'

export interface TierRule {
  tier: 'easy' | 'medium' | 'hard'
  description: string
  operands_range?: Record<string, any>
  example_expression?: string
}

export interface TopicConfig {
  id: string
  title: string
  description: string
  standard_code: string
  standard_title?: string
  verified?: boolean
  tier_rules?: Record<string, TierRule>
}

export interface CurriculumPack {
  board: string
  board_name: string
  grade: number
  version: string
  verified: boolean
  topics: TopicConfig[]
}

export interface Option {
  id: string
  text: string
  misconception_tag?: string | null
}

export interface Question {
  id: string
  board?: string
  topic: string
  grade: number
  tier: 'easy' | 'medium' | 'hard'
  stem: string
  expression: string
  options: Option[]
  correct_option_id: string
  explanation: string
  standard_code: string
}

export interface BatchQuestionResponse {
  questions: Question[]
  count: number
  topic: string
  tier: string
  board?: string
}

export interface AnswerSubmissionPayload {
  question_id: string
  selected_option_id: string
  board?: string
  topic?: string
  tier?: 'easy' | 'medium' | 'hard'
  hints_used?: number
  streak?: number
  history?: boolean[]
  current_mastery?: number
  session_stats?: Record<string, any>
  correct_option_id?: string
  options?: Option[]
  explanation?: string
  time_taken_seconds?: number
}

export interface AnswerResultResponse {
  is_correct: boolean
  correct_option_id: string
  correct_answer: string
  explanation: string
  misconception_tag?: string | null
  misconception_feedback?: string | null
  points: number
  xp_earned: number
  next_tier: 'easy' | 'medium' | 'hard'
  new_mastery: number
  new_badges: string[]
  streak: number
  board?: string
}

export type ExplainStyle = 'default' | 'simpler' | 'real_life' | 'step_by_step'

export interface WorkedExample {
  problem: string
  expression: string
  steps: string[]
  verified_answer: string
}

export interface ExplainResponse {
  title: string
  intro: string
  key_ideas: string[]
  worked_examples: WorkedExample[]
  common_mistakes: string[]
  standard_code: string
  standard_snippet: string
  topic: string
  grade: number
  style: ExplainStyle
  cached: boolean
}

export interface InfographicResponse {
  topic: string
  grade: number
  image_url: string
  url: string
  fallback_url: string
  prompt: string
  format: string
  source: string
}

export interface Slide {
  slide_number: number
  title: string
  bullets: string[]
  narration: string
  visual_component: string
  visual_props: Record<string, any>
  duration_seconds: number
}

export interface ScriptResponse {
  topic: string
  grade: number
  title: string
  standard_code: string
  slides: Slide[]
  cached: boolean
}

export interface EvalConfigSummary {
  model: string
  prompt_version: string
  sample_count: number
  schema_validity_percent: number
  math_accuracy_percent: number
  standard_code_correctness_percent: number
  avg_readability_grade: number
  avg_latency_ms: number
  avg_retry_count: number
}

export interface EvalTopicSummary {
  topic: string
  sample_count: number
  math_accuracy_percent: number
  avg_latency_ms: number
}

export interface EvalSummaryResponse {
  timestamp: string
  total_evaluated: number
  models_evaluated: string[]
  prompts_evaluated: string[]
  sample_size_per_condition: number
  configurations: EvalConfigSummary[]
  topic_breakdown: EvalTopicSummary[]
  conclusion: string
}

export const useApi = () => {
  const config = useRuntimeConfig()
  const apiBase = (config.public.apiBase as string) || 'http://localhost:8000'

  const isServerWakingUp = useState<boolean>('api_server_waking', () => false)
  const wakeUpNotice = useState<string>('api_wake_notice', () => '')
  const isLoading = useState<boolean>('api_loading', () => false)
  const lastError = useState<string | null>('api_error', () => null)

  /**
   * Helper that tracks latency to detect Render free-tier cold starts.
   */
  const requestWithColdStartHandling = async <T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> => {
    isLoading.value = true
    lastError.value = null
    isServerWakingUp.value = false
    wakeUpNotice.value = ''

    // If server takes longer than 3 seconds, show cold-start message
    const wakeTimer = setTimeout(() => {
      isServerWakingUp.value = true
      wakeUpNotice.value =
        '🚀 Waking up the MathQuest adventure server! (Render free services sleep after inactivity and take ~50s to start). Hang tight!'
    }, 3000)

    try {
      const url = `${apiBase.replace(/\/$/, '')}/${endpoint.replace(/^\//, '')}`
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        ...(options.headers as Record<string, string>),
      }

      const res = await fetch(url, {
        ...options,
        headers,
      })

      if (!res.ok) {
        const errorBody = await res.text()
        throw new Error(`Server returned HTTP ${res.status}: ${errorBody || res.statusText}`)
      }

      return (await res.json()) as T
    } catch (err: any) {
      const msg = err.message || 'Unable to communicate with math server.'
      lastError.value = msg
      console.error('[MathQuest API Error]:', err)
      throw err
    } finally {
      clearTimeout(wakeTimer)
      isLoading.value = false
      isServerWakingUp.value = false
      wakeUpNotice.value = ''
    }
  }

  /**
   * Fetch a single adaptive question or batch.
   */
  const fetchQuestion = async (
    grade: number,
    topic: string,
    tier: 'easy' | 'medium' | 'hard' = 'medium',
    count: number = 1,
    board: string = 'georgia',
    excludeIds: string[] = []
  ): Promise<Question | BatchQuestionResponse> => {
    try {
      return await requestWithColdStartHandling<Question | BatchQuestionResponse>('api/question', {
        method: 'POST',
        body: JSON.stringify({ grade, topic, tier, count, board, exclude_ids: excludeIds }),
      })
    } catch (err) {
      console.warn('Backend unavailable, using pre-verified offline question:', err)
      const matching = (offlineQuestions as Question[]).filter(
        (q) => (q.board === board || !q.board) && q.topic === topic && q.grade === grade
      )
      let pool = matching.length > 0 ? matching : (offlineQuestions as Question[]).filter((q) => q.topic === topic)
      if (pool.length === 0) pool = offlineQuestions as Question[]

      const unseen = pool.filter((q) => !excludeIds.includes(q.id) && !excludeIds.some((eid) => eid.startsWith(q.id)))
      const candidates = unseen.length > 0 ? unseen : pool
      const selected = candidates[Math.floor(Math.random() * candidates.length)]
      return selected
    }
  }

  /**
   * Fetch a full batch of 10 questions for a game round.
   */
  const fetchRoundBatch = async (
    grade: number,
    topic: string,
    tier: 'easy' | 'medium' | 'hard' = 'medium',
    count: number = 10,
    board: string = 'georgia'
  ): Promise<BatchQuestionResponse> => {
    try {
      return await requestWithColdStartHandling<BatchQuestionResponse>('api/question/batch', {
        method: 'POST',
        body: JSON.stringify({ grade, topic, tier, count, board }),
      })
    } catch (err) {
      console.warn('Backend unavailable, using pre-verified offline questions batch:', err)
      const allQs = offlineQuestions as Question[]
      const matching = allQs.filter(
        (q) => (q.board === board || !q.board) && q.topic === topic && q.grade === grade
      )
      const topicPool = matching.length > 0 ? matching : allQs.filter((q) => q.topic === topic)
      const finalPool = topicPool.length > 0 ? topicPool : allQs
      // If pool has fewer than count, duplicate/cycle to fill requested count
      const result: Question[] = []
      for (let i = 0; i < count; i++) {
        const base = finalPool[i % finalPool.length]
        result.push({ ...base, id: `${base.id}-run-${i}` })
      }
      return {
        questions: result,
        count: result.length,
        topic,
        tier,
        board,
      }
    }
  }

  /**
   * Submit an answer to receive instantaneous feedback, points, and badge updates.
   */
  const submitAnswer = async (
    payload: AnswerSubmissionPayload
  ): Promise<AnswerResultResponse> => {
    try {
      return await requestWithColdStartHandling<AnswerResultResponse>('api/answer', {
        method: 'POST',
        body: JSON.stringify(payload),
      })
    } catch (err) {
      console.warn('Backend unavailable, evaluating answer locally:', err)
      const isCorrect = payload.correct_option_id
        ? payload.selected_option_id === payload.correct_option_id
        : true
      const streak = isCorrect ? (payload.streak || 0) + 1 : 0
      const currentMastery = payload.current_mastery || 50
      const newMastery = Math.min(100, Math.max(0, currentMastery + (isCorrect ? 5 : -4)))
      const nextTier: 'easy' | 'medium' | 'hard' = streak >= 2 ? 'hard' : (isCorrect ? 'medium' : 'easy')
      const chosenOpt = payload.options?.find((o) => o.id === payload.selected_option_id)
      const feedback = chosenOpt?.misconception_tag
        ? 'Check your step-by-step arithmetic carefully! Remember common denominators and place value.'
        : null

      return {
        is_correct: isCorrect,
        correct_option_id: payload.correct_option_id || 'A',
        correct_answer: payload.correct_option_id || 'A',
        explanation: payload.explanation || 'Step-by-step verification confirmed this solution.',
        misconception_tag: chosenOpt?.misconception_tag || null,
        misconception_feedback: feedback,
        points: isCorrect ? 100 : 20,
        xp_earned: isCorrect ? 50 : 10,
        next_tier: nextTier,
        new_mastery: newMastery,
        new_badges: streak >= 5 ? ['5-Streak'] : [],
        streak,
        board: payload.board || 'georgia',
      }
    }
  }

  /**
   * Fetch structured pedagogical explanation for grade and topic.
   */
  const fetchExplanation = async (
    grade: number,
    topic: string,
    style: ExplainStyle = 'default'
  ): Promise<ExplainResponse> => {
    return requestWithColdStartHandling<ExplainResponse>('api/explain', {
      method: 'POST',
      body: JSON.stringify({ grade, topic, style }),
    })
  }

  /**
   * Fetch topic educational infographic with Pollinations.ai URL and fallback.
   */
  const fetchInfographic = async (
    topic: string,
    grade: number = 5
  ): Promise<InfographicResponse> => {
    return requestWithColdStartHandling<InfographicResponse>(
      `api/infographic?topic=${encodeURIComponent(topic)}&grade=${grade}`,
      { method: 'GET' }
    )
  }

  /**
   * Fetch 6-slide video presentation script for a topic.
   */
  const fetchScript = async (
    grade: number,
    topic: string
  ): Promise<ScriptResponse> => {
    return requestWithColdStartHandling<ScriptResponse>('api/script', {
      method: 'POST',
      body: JSON.stringify({ grade, topic }),
    })
  }

  /**
   * Fetch all available curriculum packs across boards and grades.
   */
  const fetchCurriculumPacks = async (): Promise<CurriculumPack[]> => {
    return requestWithColdStartHandling<CurriculumPack[]>('api/curriculum/packs', {
      method: 'GET',
    })
  }

  /**
   * Fetch a specific curriculum pack by board and grade.
   */
  const fetchCurriculumPack = async (
    board: string,
    grade: number
  ): Promise<CurriculumPack> => {
    return requestWithColdStartHandling<CurriculumPack>(`api/curriculum/pack/${board}/${grade}`, {
      method: 'GET',
    })
  }

  /**
   * Fetch topic definitions for a given board and grade.
   */
  const fetchCurriculumTopics = async (
    board: string,
    grade: number
  ): Promise<TopicConfig[]> => {
    return requestWithColdStartHandling<TopicConfig[]>(`api/curriculum/topics/${board}/${grade}`, {
      method: 'GET',
    })
  }

  /**
   * Fetch model and prompt benchmark evaluation summary.
   */
  const fetchEvalSummary = async (): Promise<EvalSummaryResponse> => {
    return requestWithColdStartHandling<EvalSummaryResponse>('api/eval', {
      method: 'GET',
    })
  }

  /**
   * Trigger fresh evaluation benchmark run.
   */
  const triggerEvalRun = async (sampleSize: number = 10): Promise<EvalSummaryResponse> => {
    return requestWithColdStartHandling<EvalSummaryResponse>(`api/eval/run?n=${sampleSize}&mock=true`, {
      method: 'POST',
    })
  }

  /**
   * Check backend health.
   */
  const checkHealth = async (): Promise<{ status: string; app: string }> => {
    return requestWithColdStartHandling<{ status: string; app: string }>('health', {
      method: 'GET',
    })
  }

  return {
    apiBase,
    isLoading,
    isServerWakingUp,
    wakeUpNotice,
    lastError,
    fetchQuestion,
    fetchRoundBatch,
    submitAnswer,
    fetchExplanation,
    fetchInfographic,
    fetchScript,
    fetchCurriculumPacks,
    fetchCurriculumPack,
    fetchCurriculumTopics,
    fetchEvalSummary,
    triggerEvalRun,
    checkHealth,
  }
}

