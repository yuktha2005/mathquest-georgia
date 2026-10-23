/**
 * Composable for interacting with the MathQuest Georgia FastAPI backend.
 *
 * Handles:
 * - Dynamic API Base URL from runtimeConfig (NUXT_PUBLIC_API_BASE)
 * - Render free-tier cold start detection (>2.5s) with child-friendly loading notices
 * - Robust error handling with graceful fallback options
 */

export interface Option {
  id: string
  text: string
  misconception_tag?: string | null
}

export interface Question {
  id: string
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
}

export interface AnswerSubmissionPayload {
  question_id: string
  selected_option_id: string
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

    // If server takes longer than 2.5 seconds, show cold-start message
    const wakeTimer = setTimeout(() => {
      isServerWakingUp.value = true
      wakeUpNotice.value =
        '🚀 Waking up the MathQuest adventure server! (Render free services sleep after inactivity and take ~50s to start). Hang tight!'
    }, 2500)

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
    count: number = 1
  ): Promise<Question | BatchQuestionResponse> => {
    return requestWithColdStartHandling<Question | BatchQuestionResponse>('api/question', {
      method: 'POST',
      body: JSON.stringify({ grade, topic, tier, count }),
    })
  }

  /**
   * Fetch a full batch of 10 questions for a game round.
   */
  const fetchRoundBatch = async (
    grade: number,
    topic: string,
    tier: 'easy' | 'medium' | 'hard' = 'medium',
    count: number = 10
  ): Promise<BatchQuestionResponse> => {
    return requestWithColdStartHandling<BatchQuestionResponse>('api/question/batch', {
      method: 'POST',
      body: JSON.stringify({ grade, topic, tier, count }),
    })
  }

  /**
   * Submit an answer to receive instantaneous feedback, points, and badge updates.
   */
  const submitAnswer = async (
    payload: AnswerSubmissionPayload
  ): Promise<AnswerResultResponse> => {
    return requestWithColdStartHandling<AnswerResultResponse>('api/answer', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
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
    fetchEvalSummary,
    triggerEvalRun,
    checkHealth,
  }
}
