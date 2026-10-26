<template>
  <div class="max-w-3xl mx-auto space-y-6">
    <!-- Top Action Row: Exit Quest & Progress indicator -->
    <div class="flex items-center justify-between gap-4">
      <button
        type="button"
        @click="showExitModal = true"
        class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-slate-300 text-xs font-bold text-slate-600 hover:bg-slate-100 hover:text-slate-900 transition active:scale-95 cursor-pointer focus:outline-none focus-visible:ring-4 focus-visible:ring-slate-400"
        aria-label="Exit quest"
      >
        <span aria-hidden="true">🚪</span>
        <span>Exit Quest</span>
      </button>

      <span class="text-xs font-bold text-slate-500">
        Question {{ questionNumber }} of 10
      </span>
    </div>

    <!-- Resume Quest Notice if in-progress round detected -->
    <div
      v-if="showResumeBanner"
      class="bg-amber-50 border-2 border-amber-300 rounded-3xl p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-sm"
      role="region"
      aria-label="Resume quest notice"
    >
      <div class="flex items-center gap-3">
        <span class="text-3xl" aria-hidden="true">⏳</span>
        <div>
          <h4 class="text-sm font-black text-amber-950">Active Quest Found!</h4>
          <p class="text-xs font-semibold text-amber-800">
            You were on Question {{ sessionStore.roundRecords.length + 1 }} of 10. Would you like to resume?
          </p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <button
          type="button"
          @click="resumeSavedQuest"
          class="btn-game-amber px-4 py-2 text-xs font-bold"
        >
          Resume Quest
        </button>
        <button
          type="button"
          @click="startFreshRound"
          class="btn-game-white px-3 py-2 text-xs font-bold text-slate-600"
        >
          Start Over
        </button>
      </div>
    </div>

    <!-- XP & Tier Status Bar -->
    <XPBar
      :score="sessionStore.score"
      :streak="sessionStore.streak"
      :tier="sessionStore.tier"
      :topic="sessionStore.topic"
    />

    <!-- Progress Bar (1 to 10) -->
    <ProgressBar
      :current="questionNumber"
      :total="10"
    />

    <!-- Loading Skeleton State -->
    <div
      v-if="isLoading && !activeQuestion"
      class="bg-white rounded-3xl p-6 sm:p-8 border-2 border-slate-200 shadow-game space-y-6 animate-pulse"
    >
      <div class="flex justify-between items-center">
        <div class="h-6 w-28 bg-slate-200 rounded-full"></div>
        <div class="h-6 w-24 bg-slate-200 rounded-xl"></div>
      </div>
      <div class="space-y-2.5">
        <div class="h-7 w-5/6 bg-slate-200 rounded-xl"></div>
        <div class="h-7 w-3/4 bg-slate-200 rounded-xl"></div>
      </div>
      <div class="h-24 bg-indigo-50/70 border-2 border-indigo-100 rounded-2xl flex items-center justify-center">
        <div class="h-10 w-44 bg-indigo-200/60 rounded-xl"></div>
      </div>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3.5 pt-2">
        <div v-for="i in 4" :key="i" class="h-16 bg-slate-100 rounded-2xl border-2 border-slate-200"></div>
      </div>
    </div>

    <!-- Error & Retry State -->
    <div
      v-else-if="fetchError"
      class="bg-white rounded-3xl p-8 border-2 border-rose-300 shadow-game-rose text-center space-y-4 animate-pop"
    >
      <span class="text-5xl inline-block">⚠️</span>
      <h3 class="text-2xl font-black text-rose-900">Oops! Couldn't Summon Question</h3>
      <p class="text-slate-600 text-sm max-w-md mx-auto">
        {{ fetchError }}
      </p>
      <div class="pt-2 flex items-center justify-center gap-3">
        <button
          type="button"
          @click="loadCurrentQuestion"
          class="btn-game-blue px-6 py-3 font-bold"
        >
          <span>🔄 Retry Question</span>
        </button>
        <NuxtLink to="/" class="btn-game-white px-6 py-3 font-bold">
          <span>🗺️ Territory Map</span>
        </NuxtLink>
      </div>
    </div>

    <!-- Active Question Card -->
    <div v-else-if="activeQuestion" class="space-y-6">
      <QuizCard
        :stem="activeQuestion.stem"
        :expression="activeQuestion.expression"
        :standard-code="activeQuestion.standard_code"
        :topic="activeQuestion.topic"
        :hints-used="hintsUsed"
        :is-submitted="hasSubmitted"
        :options="activeQuestion.options"
        :source="activeQuestion.source"
        @update:hints-used="val => hintsUsed = val"
      >

        <!-- 4 Multiple Choice Options (1-4 or A-D) -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3.5 pt-2">
          <OptionButton
            v-for="(opt, idx) in activeQuestion.options"
            :key="opt.id"
            :id="opt.id"
            :text="opt.text"
            :index="idx"
            :is-selected="selectedOptionId === opt.id"
            :is-submitted="hasSubmitted"
            :is-correct-option="hasSubmitted && opt.id === (evalResult?.correct_option_id || activeQuestion.correct_option_id)"
            :is-chosen-wrong="hasSubmitted && opt.id === selectedOptionId && !evalResult?.is_correct"
            :disabled="hasSubmitted || isEvaluating"
            @select="selectOption"
          />
        </div>

        <!-- Confirm Answer Action Button -->
        <div v-if="selectedOptionId && !hasSubmitted" class="pt-3">
          <button
            type="button"
            @click="submitAnswerAction"
            :disabled="isEvaluating"
            class="w-full btn-game-green py-4 text-lg font-black shadow-game-green cursor-pointer flex items-center justify-center gap-2"
          >
            <span v-if="isEvaluating" class="inline-block w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
            <span v-else>🚀</span>
            <span>{{ isEvaluating ? 'Verifying with Math Engine...' : 'Confirm Answer (Press Enter)' }}</span>
          </button>
        </div>
      </QuizCard>

      <!-- Feedback Panel (Evaluated Result) -->
      <FeedbackPanel
        v-if="hasSubmitted && evalResult"
        :is-correct="evalResult.is_correct"
        :points="evalResult.points"
        :next-tier="evalResult.next_tier"
        :correct-answer="evalResult.correct_answer || activeQuestion.correct_option_id"
        :misconception-tag="evalResult.misconception_tag"
        :misconception-feedback="evalResult.misconception_feedback"
        :explanation="evalResult.explanation"
        :is-last-question="questionNumber >= 10"
        @next="advanceQuestion"
      />
    </div>

    <!-- Exit Confirmation Modal -->
    <div
      v-if="showExitModal"
      class="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="exit-modal-title"
    >
      <div class="bg-white rounded-3xl p-6 sm:p-8 max-w-sm w-full border-2 border-slate-200 shadow-2xl text-center space-y-4 animate-pop">
        <span class="text-5xl inline-block" aria-hidden="true">⏸️</span>
        <h3 id="exit-modal-title" class="text-xl font-black text-slate-800">
          Leave Quest Arena?
        </h3>
        <p class="text-sm font-semibold text-slate-600">
          Your score and progress are saved. You can jump back into this quest anytime!
        </p>
        <div class="flex items-center justify-center gap-3 pt-2">
          <button
            type="button"
            @click="showExitModal = false"
            class="btn-game-white px-4 py-2.5 text-sm font-bold flex-1"
          >
            Keep Playing
          </button>
          <button
            type="button"
            @click="confirmExit"
            class="btn-game-rose px-4 py-2.5 text-sm font-bold flex-1"
          >
            Exit to Map
          </button>
        </div>
      </div>
    </div>

    <!-- Achievement Toast -->
    <BadgeToast
      :badges="newBadgesUnlocked"
      :show="showBadgeToast"
      @dismiss="showBadgeToast = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useApi, type AnswerResultResponse, type Question } from '~/composables/useApi'
import { useSessionStore } from '~/stores/session'

definePageMeta({
  layout: 'focus',
})

const router = useRouter()
const { fetchQuestion, submitAnswer, isLoading } = useApi()
const sessionStore = useSessionStore()

// State
const questionNumber = ref(1)
const activeQuestion = ref<Question | null>(null)
const fetchError = ref<string | null>(null)
const selectedOptionId = ref<string | null>(null)
const hasSubmitted = ref(false)
const isEvaluating = ref(false)
const showHint = ref(false)
const hintsUsed = ref(0)
const evalResult = ref<AnswerResultResponse | null>(null)
const showExitModal = ref(false)
const showResumeBanner = ref(false)

// Badges notification
const newBadgesUnlocked = ref<string[]>([])
const showBadgeToast = ref(false)

// Keyboard Support: 1-4 keys for options, Enter for confirm / next
const handleKeyDown = (event: KeyboardEvent) => {
  if (['INPUT', 'TEXTAREA'].includes((event.target as HTMLElement)?.tagName)) {
    return
  }

  // 1. Enter key: Submit or Next
  if (event.key === 'Enter') {
    if (!hasSubmitted.value && selectedOptionId.value) {
      event.preventDefault()
      submitAnswerAction()
    } else if (hasSubmitted.value && evalResult.value) {
      event.preventDefault()
      advanceQuestion()
    }
    return
  }

  // 2. Options selection via 1-4 or A-D
  if (!hasSubmitted.value && activeQuestion.value) {
    const key = event.key.toUpperCase()
    const options = activeQuestion.value.options

    // Check number keys 1, 2, 3, 4
    if (['1', '2', '3', '4'].includes(key)) {
      const idx = parseInt(key, 10) - 1
      if (options[idx]) {
        event.preventDefault()
        selectOption(options[idx].id)
      }
    }
    // Check letter keys A, B, C, D
    else if (['A', 'B', 'C', 'D'].includes(key)) {
      const found = options.find((o) => o.id.toUpperCase() === key)
      if (found) {
        event.preventDefault()
        selectOption(found.id)
      }
    }
  }
}

onMounted(() => {
  sessionStore.loadFromStorage()
  window.addEventListener('keydown', handleKeyDown)

  // Check if a saved round was in-progress
  if (sessionStore.roundRecords.length > 0 && sessionStore.roundRecords.length < 10) {
    showResumeBanner.value = true
    questionNumber.value = sessionStore.roundRecords.length + 1
    loadCurrentQuestion()
  } else {
    sessionStore.roundRecords = []
    questionNumber.value = 1
    loadCurrentQuestion()
  }
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
})

const resumeSavedQuest = () => {
  showResumeBanner.value = false
}

const startFreshRound = () => {
  showResumeBanner.value = false
  sessionStore.roundRecords = []
  questionNumber.value = 1
  loadCurrentQuestion()
}

const confirmExit = () => {
  showExitModal.value = false
  router.push('/')
}

/**
 * Fetch question from backend /api/question using the current dynamic adaptive tier
 */
const loadCurrentQuestion = async () => {
  fetchError.value = null
  selectedOptionId.value = null
  hasSubmitted.value = false
  showHint.value = false
  hintsUsed.value = 0
  evalResult.value = null
  activeQuestion.value = null

  try {
    const excludeIds = sessionStore.roundRecords.map((r) => r.question.id)
    const res = await fetchQuestion(
      sessionStore.grade,
      sessionStore.topic,
      sessionStore.tier,
      1,
      sessionStore.board,
      excludeIds
    )

    // Handle either single Question or Batch response
    if ('questions' in res && Array.isArray(res.questions) && res.questions.length > 0) {
      activeQuestion.value = res.questions[0]
    } else if ('id' in res) {
      activeQuestion.value = res as Question
    } else {
      throw new Error('Received unexpected question response format.')
    }
  } catch (err: any) {
    console.error('Failed to load question:', err)
    fetchError.value = err.message || 'Unable to connect to the math quest server.'
  }
}

const selectOption = (optId: string) => {
  if (hasSubmitted.value || isEvaluating.value) return
  selectedOptionId.value = optId
}

const toggleHint = () => {
  showHint.value = !showHint.value
  if (showHint.value) {
    hintsUsed.value++
  }
}

/**
 * Submit answer to /api/answer and receive adaptive evaluation
 */
const submitAnswerAction = async () => {
  if (!selectedOptionId.value || !activeQuestion.value || hasSubmitted.value || isEvaluating.value) {
    return
  }

  isEvaluating.value = true
  const q = activeQuestion.value

  try {
    const payload = {
      question_id: q.id,
      board: sessionStore.board,
      selected_option_id: selectedOptionId.value,
      topic: q.topic,
      tier: q.tier,
      hints_used: hintsUsed.value,
      streak: sessionStore.streak,
      history: sessionStore.history,
      current_mastery: sessionStore.mastery[q.topic as any] || 50.0,
      session_stats: {
        total_answered: sessionStore.history.length,
        streak: sessionStore.streak,
        best_streak: sessionStore.bestStreak,
        fraction_mastery: sessionStore.mastery['fractions'] || 50.0,
        earned_badges: sessionStore.badges,
        consecutive_at_tier: sessionStore.history.slice(-sessionStore.streak).filter(Boolean).length,
      },
      correct_option_id: q.correct_option_id,
      options: q.options,
      explanation: q.explanation,
    }

    const res = await submitAnswer(payload)
    evalResult.value = res
    hasSubmitted.value = true

    // Update Pinia store (updates score, streak, mastery, and tier shown on XPBar)
    sessionStore.recordAnswer(res, q, selectedOptionId.value)

    // Trigger Badge Toast if newly awarded
    if (res.new_badges && res.new_badges.length > 0) {
      newBadgesUnlocked.value = res.new_badges
      showBadgeToast.value = true
      setTimeout(() => {
        showBadgeToast.value = false
      }, 5000)
    }
  } catch (err: any) {
    console.error('Submission failed:', err)
  } finally {
    isEvaluating.value = false
  }
}

/**
 * Move on to next question or navigate to results when round finishes
 */
const advanceQuestion = () => {
  if (questionNumber.value >= 10) {
    router.push('/results')
  } else {
    questionNumber.value++
    loadCurrentQuestion()
  }
}
</script>
