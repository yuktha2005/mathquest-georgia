<template>
  <div class="max-w-4xl mx-auto space-y-8 animate-pop">
    <!-- Unsaved Cloud Sync Notice -->
    <div
      v-if="hasUnsavedProgress"
      class="bg-rose-50 border-2 border-rose-300 rounded-3xl p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-sm"
      role="alert"
    >
      <div class="flex items-center gap-3">
        <span class="text-3xl shrink-0" aria-hidden="true">⚠️</span>
        <div>
          <h2 class="font-extrabold text-rose-900 text-sm sm:text-base">
            Couldn't save, Retry
          </h2>
          <p class="text-xs text-rose-700 mt-0.5">
            {{ syncError || "Network issue prevented saving to cloud. Your quiz data is safely stored on this device." }}
          </p>
        </div>
      </div>
      <button
        type="button"
        @click="handleRetrySync"
        :disabled="isSyncing"
        class="px-5 py-2.5 rounded-xl font-extrabold text-xs sm:text-sm text-white bg-rose-600 hover:bg-rose-700 active:scale-95 transition shadow disabled:opacity-50 flex items-center gap-2 shrink-0 cursor-pointer"
      >
        <span v-if="isSyncing" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
        <span>{{ isSyncing ? 'Saving...' : 'Retry Save 🔄' }}</span>
      </button>
    </div>

    <!-- Victory Hero Banner (Warm celebratory hero without purple/pink gradient) -->
    <div class="bg-primary-900 rounded-3xl p-8 sm:p-12 text-white shadow-warm-lg border-2 border-primary-950 text-center relative overflow-hidden">
      <!-- Decorative background icon -->
      <div class="absolute -right-6 -bottom-6 text-9xl opacity-10 select-none pointer-events-none">
        ⭐
      </div>

      <div class="max-w-2xl mx-auto space-y-3 relative z-10">
        <span class="text-6xl sm:text-7xl animate-bounce inline-block" aria-hidden="true">🏆</span>
        <h1 class="text-3xl sm:text-5xl font-black tracking-tight text-white">
          Round Completed!
        </h1>
        <p class="text-warm-100 text-base sm:text-xl font-bold max-w-lg mx-auto leading-relaxed">
          {{ performanceMessage }}
        </p>
      </div>
    </div>

    <!-- 4 Key Performance Cards -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
      <!-- 1. Accuracy Card -->
      <div class="card-game p-5 text-center space-y-1">
        <span class="text-xs font-black uppercase text-warm-500 tracking-wider">Accuracy</span>
        <div class="text-3xl sm:text-4xl font-black text-emerald-700">
          {{ sessionStore.roundAccuracyPercent }}%
        </div>
        <span class="text-xs text-warm-600 font-bold block">
          {{ sessionStore.roundCorrectCount }} of {{ sessionStore.roundRecords.length || 10 }} Correct
        </span>
      </div>

      <!-- 2. Round Score Earned -->
      <div class="card-game p-5 text-center space-y-1">
        <span class="text-xs font-black uppercase text-warm-500 tracking-wider">Round XP</span>
        <div class="text-3xl sm:text-4xl font-black text-accent-600">
          +{{ roundPointsEarned }}
        </div>
        <span class="text-xs text-warm-600 font-bold block">
          Total: {{ sessionStore.score }} XP
        </span>
      </div>

      <!-- 3. Highest Streak -->
      <div class="card-game p-5 text-center space-y-1">
        <span class="text-xs font-black uppercase text-warm-500 tracking-wider">Best Streak</span>
        <div class="text-3xl sm:text-4xl font-black text-orange-600 flex items-center justify-center gap-1">
          <span aria-hidden="true">🔥</span>
          <span>{{ sessionStore.bestStreak }}</span>
        </div>
        <span class="text-xs text-warm-600 font-bold block">
          In a row
        </span>
      </div>

      <!-- 4. Adapted Tier Reached -->
      <div class="card-game p-5 text-center space-y-1">
        <span class="text-xs font-black uppercase text-warm-500 tracking-wider">Tier Reached</span>
        <div class="text-2xl sm:text-3xl font-black text-primary-700 uppercase flex items-center justify-center gap-1">
          <span aria-hidden="true">{{ tierEmoji }}</span>
          <span>{{ sessionStore.tier }}</span>
        </div>
        <span class="text-xs text-warm-600 font-bold block">
          {{ sessionStore.mastery[sessionStore.topic] || 50 }}% Mastery
        </span>
      </div>
    </div>

    <!-- Diagnostic Summary: Most Common Mistake Section -->
    <div class="card-game space-y-3">
      <div class="flex items-center gap-2">
        <span class="text-2xl" aria-hidden="true">💡</span>
        <h2 class="text-lg sm:text-xl font-black text-warm-900">
          Diagnostic Clue: Most Common Mistake
        </h2>
      </div>

      <div
        v-if="mostCommonMistake"
        class="bg-rose-50 border-2 border-rose-200 rounded-2xl p-4 sm:p-5 text-sm space-y-2"
      >
        <div class="flex items-center gap-2 font-black uppercase text-xs text-rose-800">
          <span>⚠️ Misconception Trap Identified</span>
          <span class="font-mono text-[11px] bg-white px-2 py-0.5 rounded border border-rose-300">
            {{ mostCommonMistake.tag }}
          </span>
        </div>
        <p class="font-bold text-warm-900 text-base leading-snug">
          {{ mostCommonMistake.feedback }}
        </p>
        <p class="text-xs text-warm-600 pt-1 border-t border-rose-200">
          Identified in {{ mostCommonMistake.count }} question{{ mostCommonMistake.count > 1 ? 's' : '' }} during this round. Use the solution steps below to master this concept!
        </p>
      </div>

      <div
        v-else
        class="bg-emerald-50 border-2 border-emerald-200 rounded-2xl p-4 sm:p-5 text-sm text-emerald-950 flex items-center gap-3"
      >
        <span class="text-3xl" aria-hidden="true">🌟</span>
        <div>
          <p class="font-extrabold text-base text-emerald-900">Flawless Mathematical Reasoning!</p>
          <p class="text-xs sm:text-sm text-emerald-800">You didn't fall for any common misconception traps or distractor traps in this quest.</p>
        </div>
      </div>
    </div>

    <!-- Badges Earned Showcase Section -->
    <div class="card-game space-y-4">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-xl font-bold text-warm-900 flex items-center gap-2">
            <span>🎖️</span>
            <span>Earned Achievement Badges</span>
          </h2>
          <p class="text-xs sm:text-sm text-warm-500">
            Badges unlocked through mastery, streaks, and perseverance
          </p>
        </div>
        <span class="text-xs font-black text-primary-700 bg-primary-50 px-3 py-1.5 rounded-full border border-primary-200">
          {{ sessionStore.badges.length }} Unlocked
        </span>
      </div>

      <div v-if="sessionStore.badges.length > 0" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3.5">
        <div
          v-for="badge in sessionStore.badges"
          :key="badge"
          class="bg-accent-50 border-2 border-accent-300 rounded-2xl p-4 text-center space-y-1 shadow-game-amber animate-pop"
        >
          <span class="text-3xl block">{{ getBadgeEmoji(badge) }}</span>
          <span class="font-extrabold text-xs sm:text-sm text-warm-900 block leading-tight">
            {{ badge }}
          </span>
          <span class="text-[10px] font-black text-accent-800 uppercase block">Earned</span>
        </div>
      </div>
      <div v-else class="text-center py-4 text-warm-400 text-sm italic font-medium">
        Keep playing to earn your First Steps and 5-Streak badges!
      </div>
    </div>

    <!-- Problem-by-Problem Diagnostic Review List -->
    <div
      v-if="sessionStore.roundRecords.length > 0"
      class="card-game space-y-5"
    >
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-xl font-bold text-warm-900 flex items-center gap-2">
            <span>📝</span>
            <span>Step-by-Step Question Review</span>
          </h2>
          <p class="text-xs sm:text-sm text-warm-500">
            Examine the correct procedures and diagnostic hints for every problem
          </p>
        </div>
        <button
          type="button"
          @click="showAllDetails = !showAllDetails"
          class="text-xs font-bold text-primary-700 hover:text-primary-800 transition min-h-[36px] flex items-center"
        >
          {{ showAllDetails ? 'Collapse All' : 'Expand All' }}
        </button>
      </div>

      <div class="space-y-3.5">
        <div
          v-for="(rec, idx) in sessionStore.roundRecords"
          :key="idx"
          :class="[
            'rounded-2xl border-2 p-5 transition-all space-y-2.5',
            rec.isCorrect
              ? 'bg-emerald-50/50 border-emerald-200'
              : 'bg-rose-50/60 border-rose-200'
          ]"
        >
          <!-- Question Header Row -->
          <div class="flex items-start justify-between gap-3">
            <div class="flex items-center gap-2.5">
              <span class="text-2xl shrink-0">
                {{ rec.isCorrect ? '✅' : '❌' }}
              </span>
              <div>
                <span class="font-extrabold text-sm sm:text-base text-warm-900 block">
                  Question {{ idx + 1 }}: {{ rec.question.stem }}
                </span>
                <span class="text-xs font-mono font-bold text-primary-700 bg-white px-2 py-0.5 rounded-md border border-warm-200 inline-block mt-0.5">
                  Expression: {{ rec.question.expression }}
                </span>
              </div>
            </div>

            <span
              :class="[
                'text-xs font-black px-2.5 py-0.5 rounded-full shrink-0',
                rec.isCorrect ? 'bg-emerald-200 text-emerald-900' : 'bg-rose-200 text-rose-900'
              ]"
            >
              +{{ rec.pointsEarned }} XP
            </span>
          </div>

          <!-- Misconception Alert (If Wrong) -->
          <div
            v-if="!rec.isCorrect && rec.misconceptionFeedback"
            class="bg-white rounded-xl p-3.5 border-2 border-rose-200 text-xs sm:text-sm space-y-1"
          >
            <div class="flex items-center gap-1.5 text-xs font-black uppercase text-rose-700">
              <span>⚠️ Misconception Trap Identified</span>
            </div>
            <p class="font-extrabold text-warm-900 leading-snug">
              {{ rec.misconceptionFeedback }}
            </p>
          </div>

          <!-- Detailed Solution Walkthrough -->
          <div
            v-if="showAllDetails || !rec.isCorrect"
            class="bg-white/80 rounded-xl p-3 border border-warm-200 text-xs sm:text-sm text-warm-700 font-medium"
          >
            <span class="font-extrabold text-primary-700 block text-xs uppercase mb-0.5">Solution Steps:</span>
            <p class="whitespace-pre-line leading-relaxed font-bold">
              {{ rec.explanation }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Action Buttons Row: Practice Weak Topic / Next Topic / Play Again / Map -->
    <div class="flex flex-wrap items-center justify-center gap-3 pt-4">
      <!-- Practice Weak Topic Button -->
      <button
        type="button"
        @click="goToWeakTopic"
        aria-label="Practice your weakest topic based on round diagnostics"
        class="btn-game-accent px-6 py-3.5 text-sm sm:text-base font-black shadow-game-amber cursor-pointer flex items-center justify-center gap-2 min-h-[44px]"
      >
        <span aria-hidden="true">🎯</span>
        <span>Practice Weak Topic ({{ weakTopicName }})</span>
      </button>

      <!-- Next Topic Button -->
      <button
        type="button"
        @click="goToNextTopic"
        aria-label="Advance to next curriculum topic"
        class="btn-game-primary px-6 py-3.5 text-sm sm:text-base font-black shadow-game-blue cursor-pointer flex items-center justify-center gap-2 min-h-[44px]"
      >
        <span aria-hidden="true">➡️</span>
        <span>Next Topic ({{ nextTopicName }})</span>
      </button>

      <!-- Play Another Round -->
      <button
        type="button"
        @click="playAgain"
        aria-label="Play another round on this topic"
        class="btn-game-green px-6 py-3.5 text-sm sm:text-base font-black shadow-game-green cursor-pointer flex items-center justify-center gap-2 min-h-[44px]"
      >
        <span aria-hidden="true">🔄</span>
        <span>Play Again ({{ sessionStore.tier.toUpperCase() }})</span>
      </button>

      <!-- Return to Map -->
      <NuxtLink
        to="/"
        aria-label="Return to territory map"
        class="btn-game-white px-5 py-3.5 text-sm sm:text-base font-bold shadow-game flex items-center justify-center gap-2 min-h-[44px]"
      >
        <span aria-hidden="true">🗺️</span>
        <span>Territory Map</span>
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import confetti from 'canvas-confetti'
import { useSessionStore } from '~/stores/session'
import { useProgressSync } from '~/composables/useProgressSync'

const router = useRouter()
const sessionStore = useSessionStore()
const {
  persistCompletedRound,
  retryPendingSync,
  hasUnsavedProgress,
  syncError,
  isSyncing,
} = useProgressSync()

const showAllDetails = ref(false)
const hasPersisted = ref(false)

const roundPointsEarned = computed(() => {
  return sessionStore.roundRecords.reduce((sum, r) => sum + r.pointsEarned, 0)
})

const tierEmoji = computed(() => {
  const t = sessionStore.tier.toLowerCase()
  if (t === 'easy') return '🌱'
  if (t === 'hard') return '⚡'
  return '🎯'
})

const performanceMessage = computed(() => {
  const acc = sessionStore.roundAccuracyPercent
  const champTitle = sessionStore.board === 'cbse' ? 'CBSE Math Champion!' : 'Georgia Math Champion!'
  if (acc === 100) {
    return `🌟 Perfection! You conquered all 10 questions with zero errors! You are a ${champTitle}`
  }
  if (acc >= 80) {
    return '🚀 Outstanding Adventure! Your mathematical reasoning was razor sharp throughout this quest!'
  }
  if (acc >= 60) {
    return '🌱 Solid Work! You tackled tough challenges and leveled up your problem-solving skills!'
  }
  return '🛡️ Every Quest Teaches You! Mistakes are the secret clues that build true mastery. Review your steps and jump back in!'
})

const getBadgeEmoji = (badgeName: string): string => {
  switch (badgeName) {
    case 'First Steps':
      return '👣'
    case '5-Streak':
      return '🔥'
    case 'Fraction Master':
      return '🍕'
    case 'Decimal Dynamo':
      return '🎯'
    case 'Ratio Ranger':
      return '⚖️'
    case 'Geometry Giant':
      return '📐'
    case 'CBSE Champion':
      return '🇮🇳'
    case 'Tenacious Thinker':
      return '🧠'
    case 'Comeback Kid':
      return '⚡'
    case 'Perfect Round':
      return '🌟'
    default:
      return '🏆'
  }
}

onMounted(async () => {
  sessionStore.loadFromStorage()

  // Persist completed round if records exist
  if (sessionStore.roundRecords.length > 0 && !hasPersisted.value) {
    hasPersisted.value = true
    await persistCompletedRound()
  }

  // Fireworks celebration
  confetti({
    particleCount: 120,
    spread: 75,
    origin: { y: 0.6 },
  })
})

const handleRetrySync = async () => {
  await retryPendingSync()
}

// Most Common Mistake calculation across round records
const mostCommonMistake = computed(() => {
  const mistakes: Record<string, { tag: string; feedback: string; count: number }> = {}
  for (const rec of sessionStore.roundRecords) {
    if (!rec.isCorrect && rec.misconceptionTag) {
      if (!mistakes[rec.misconceptionTag]) {
        mistakes[rec.misconceptionTag] = {
          tag: rec.misconceptionTag,
          feedback: rec.misconceptionFeedback || 'Review the arithmetic operation and unit steps carefully.',
          count: 0
        }
      }
      mistakes[rec.misconceptionTag].count++
    }
  }
  const sorted = Object.values(mistakes).sort((a, b) => b.count - a.count)
  return sorted[0] || null
})

// Topic list based on curriculum board & grade
const activeCurriculumTopics = computed<string[]>(() => {
  if (sessionStore.board === 'cbse') {
    return ['factors_multiples', 'integers', 'fractions', 'decimals', 'ratios']
  }
  return sessionStore.grade === 5
    ? ['fractions', 'decimals', 'ratios', 'geometry']
    : ['ratios', 'fractions', 'decimals', 'geometry']
})

const topicDisplayNames: Record<string, string> = {
  fractions: 'Fractions',
  decimals: 'Decimals',
  ratios: 'Ratios',
  geometry: 'Geometry',
  factors_multiples: 'Factors & Multiples',
  integers: 'Integers',
}

const weakTopic = computed<string>(() => {
  const topics = activeCurriculumTopics.value
  let lowestTopic = topics[0]
  let lowestMastery = 101

  for (const t of topics) {
    const m = sessionStore.mastery[t] !== undefined ? sessionStore.mastery[t] : 50
    if (m < lowestMastery) {
      lowestMastery = m
      lowestTopic = t
    }
  }
  return lowestTopic
})

const weakTopicName = computed(() => {
  return topicDisplayNames[weakTopic.value] || weakTopic.value
})

const nextTopic = computed<string>(() => {
  const topics = activeCurriculumTopics.value
  const currentIdx = topics.indexOf(sessionStore.topic)
  if (currentIdx === -1 || currentIdx === topics.length - 1) {
    return topics[0]
  }
  return topics[currentIdx + 1]
})

const nextTopicName = computed(() => {
  return topicDisplayNames[nextTopic.value] || nextTopic.value
})

const goToWeakTopic = () => {
  sessionStore.setTopic(weakTopic.value as any)
  sessionStore.roundRecords = []
  router.push(`/learn/${sessionStore.grade}/${weakTopic.value}`)
}

const goToNextTopic = () => {
  sessionStore.setTopic(nextTopic.value as any)
  sessionStore.roundRecords = []
  router.push(`/learn/${sessionStore.grade}/${nextTopic.value}`)
}

const playAgain = () => {
  sessionStore.roundRecords = []
  router.push('/quiz')
}
</script>
