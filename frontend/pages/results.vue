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

    <!-- Victory Hero Banner -->
    <div class="bg-gradient-to-r from-amber-400 via-orange-500 to-pink-500 rounded-3xl p-8 sm:p-12 text-white shadow-game-amber text-center relative overflow-hidden">
      <!-- Decorative background icon -->
      <div class="absolute -right-6 -bottom-6 text-9xl opacity-15 select-none pointer-events-none">
        ⭐
      </div>

      <div class="max-w-2xl mx-auto space-y-3 relative z-10">
        <span class="text-6xl sm:text-7xl animate-bounce inline-block">🏆</span>
        <h1 class="text-3xl sm:text-5xl font-black tracking-tight">
          Round Completed!
        </h1>
        <p class="text-white/95 text-base sm:text-xl font-bold max-w-lg mx-auto leading-relaxed">
          {{ performanceMessage }}
        </p>
      </div>
    </div>

    <!-- 4 Key Performance Cards -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
      <!-- 1. Accuracy Card -->
      <div class="bg-white rounded-3xl p-5 border-2 border-slate-200 shadow-game text-center space-y-1">
        <span class="text-xs font-black uppercase text-slate-500 tracking-wider">Accuracy</span>
        <div class="text-3xl sm:text-4xl font-black text-emerald-600">
          {{ sessionStore.roundAccuracyPercent }}%
        </div>
        <span class="text-xs text-slate-500 font-bold block">
          {{ sessionStore.roundCorrectCount }} of {{ sessionStore.roundRecords.length || 10 }} Correct
        </span>
      </div>

      <!-- 2. Round Score Earned -->
      <div class="bg-white rounded-3xl p-5 border-2 border-slate-200 shadow-game text-center space-y-1">
        <span class="text-xs font-black uppercase text-slate-500 tracking-wider">Round XP</span>
        <div class="text-3xl sm:text-4xl font-black text-amber-500">
          +{{ roundPointsEarned }}
        </div>
        <span class="text-xs text-slate-500 font-bold block">
          Total: {{ sessionStore.score }} XP
        </span>
      </div>

      <!-- 3. Highest Streak -->
      <div class="bg-white rounded-3xl p-5 border-2 border-slate-200 shadow-game text-center space-y-1">
        <span class="text-xs font-black uppercase text-slate-500 tracking-wider">Best Streak</span>
        <div class="text-3xl sm:text-4xl font-black text-orange-500 flex items-center justify-center gap-1">
          <span>🔥</span>
          <span>{{ sessionStore.bestStreak }}</span>
        </div>
        <span class="text-xs text-slate-500 font-bold block">
          In a row
        </span>
      </div>

      <!-- 4. Adapted Tier Reached -->
      <div class="bg-white rounded-3xl p-5 border-2 border-slate-200 shadow-game text-center space-y-1">
        <span class="text-xs font-black uppercase text-slate-500 tracking-wider">Tier Reached</span>
        <div class="text-2xl sm:text-3xl font-black text-indigo-600 uppercase flex items-center justify-center gap-1">
          <span>{{ tierEmoji }}</span>
          <span>{{ sessionStore.tier }}</span>
        </div>
        <span class="text-xs text-slate-500 font-bold block">
          {{ sessionStore.mastery[sessionStore.topic] || 50 }}% Mastery
        </span>
      </div>
    </div>

    <!-- Badges Earned Showcase Section -->
    <div class="bg-white rounded-3xl p-6 sm:p-8 border-2 border-slate-200 shadow-game space-y-4">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-xl font-bold text-slate-800 flex items-center gap-2">
            <span>🎖️</span>
            <span>Earned Achievement Badges</span>
          </h2>
          <p class="text-xs sm:text-sm text-slate-500">
            Badges unlocked through mastery, streaks, and perseverance
          </p>
        </div>
        <span class="text-xs font-black text-indigo-600 bg-indigo-50 px-3 py-1.5 rounded-full border border-indigo-200">
          {{ sessionStore.badges.length }} Unlocked
        </span>
      </div>

      <div v-if="sessionStore.badges.length > 0" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3.5">
        <div
          v-for="badge in sessionStore.badges"
          :key="badge"
          class="bg-amber-50 border-2 border-amber-300 rounded-2xl p-4 text-center space-y-1 shadow-game-amber animate-pop"
        >
          <span class="text-3xl block">{{ getBadgeEmoji(badge) }}</span>
          <span class="font-extrabold text-xs sm:text-sm text-slate-800 block leading-tight">
            {{ badge }}
          </span>
          <span class="text-[10px] font-bold text-amber-800 uppercase block">Earned</span>
        </div>
      </div>
      <div v-else class="text-center py-4 text-slate-400 text-sm italic font-medium">
        Keep playing to earn your First Steps and 5-Streak badges!
      </div>
    </div>

    <!-- Problem-by-Problem Diagnostic Review List -->
    <div
      v-if="sessionStore.roundRecords.length > 0"
      class="bg-white rounded-3xl p-6 sm:p-8 border-2 border-slate-200 shadow-game space-y-5"
    >
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-xl font-bold text-slate-800 flex items-center gap-2">
            <span>📝</span>
            <span>Step-by-Step Question Review</span>
          </h2>
          <p class="text-xs sm:text-sm text-slate-500">
            Examine the correct procedures and diagnostic hints for every problem
          </p>
        </div>
        <button
          type="button"
          @click="showAllDetails = !showAllDetails"
          class="text-xs font-bold text-indigo-600 hover:text-indigo-800 transition"
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
                <span class="font-extrabold text-sm sm:text-base text-slate-900 block">
                  Question {{ idx + 1 }}: {{ rec.question.stem }}
                </span>
                <span class="text-xs font-mono font-bold text-indigo-700 bg-white px-2 py-0.5 rounded-md border border-slate-200 inline-block mt-0.5">
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
            <p class="font-extrabold text-slate-800 leading-snug">
              {{ rec.misconceptionFeedback }}
            </p>
          </div>

          <!-- Detailed Solution Walkthrough -->
          <div
            v-if="showAllDetails || !rec.isCorrect"
            class="bg-white/80 rounded-xl p-3 border border-slate-200 text-xs sm:text-sm text-slate-700 font-medium"
          >
            <span class="font-extrabold text-indigo-600 block text-xs uppercase mb-0.5">Solution Steps:</span>
            <p class="whitespace-pre-line leading-relaxed font-bold">
              {{ rec.explanation }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Bottom Navigation & Play Again Buttons -->
    <div class="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
      <!-- Play Again Button -->
      <button
        type="button"
        @click="playAgain"
        aria-label="Play another round on this topic"
        class="w-full sm:w-auto btn-game-green px-8 py-4 text-base sm:text-lg font-black shadow-game-green cursor-pointer flex items-center justify-center gap-2 focus:outline-none focus-visible:ring-4 focus-visible:ring-emerald-400 focus-visible:ring-offset-2"
      >
        <span aria-hidden="true">🔄</span>
        <span>Play Another Round ({{ sessionStore.tier.toUpperCase() }})</span>
      </button>

      <!-- Return to Map -->
      <NuxtLink
        to="/"
        aria-label="Return to territory map"
        class="w-full sm:w-auto btn-game-white px-6 py-4 text-base font-black shadow-game flex items-center justify-center gap-2 focus:outline-none focus-visible:ring-4 focus-visible:ring-slate-400 focus-visible:ring-offset-2"
      >
        <span aria-hidden="true">🗺️</span>
        <span>Territory Map</span>
      </NuxtLink>

      <!-- Go to Dashboard -->
      <NuxtLink
        to="/dashboard"
        aria-label="Go to student dashboard"
        class="w-full sm:w-auto btn-game-white px-6 py-4 text-base font-black shadow-game flex items-center justify-center gap-2 focus:outline-none focus-visible:ring-4 focus-visible:ring-slate-400 focus-visible:ring-offset-2"
      >
        <span aria-hidden="true">🏠</span>
        <span>Dashboard</span>
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

const playAgain = () => {
  sessionStore.roundRecords = []
  router.push('/quiz')
}
</script>
