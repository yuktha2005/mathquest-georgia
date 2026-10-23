<template>
  <div
    role="alert"
    aria-live="assertive"
    :class="[
      'rounded-3xl p-5 sm:p-8 border-4 shadow-game-lg space-y-5 animate-pop',
      isCorrect
        ? 'bg-emerald-50 border-emerald-500'
        : 'bg-rose-50 border-rose-400'
    ]"
  >
    <!-- Top Header -->
    <div class="flex flex-wrap items-center justify-between gap-3 sm:gap-4">
      <div class="flex items-center gap-3">
        <span class="text-4xl sm:text-5xl" aria-hidden="true">
          {{ isCorrect ? '🎉' : '💡' }}
        </span>
        <div>
          <h3
            :class="[
              'text-2xl sm:text-3xl font-black leading-tight',
              isCorrect ? 'text-emerald-950' : 'text-rose-950'
            ]"
          >
            {{ isCorrect ? 'Spot On! Mathematical Mastery!' : 'Not Quite — Check What Happened' }}
          </h3>
          <!-- Points Earned Tag -->
          <div class="flex items-center gap-2 mt-1">
            <span
              :class="[
                'text-xs font-black uppercase px-2.5 py-0.5 rounded-full',
                isCorrect ? 'bg-emerald-200 text-emerald-950' : 'bg-rose-200 text-rose-950'
              ]"
            >
              {{ isCorrect ? `+${points} XP Points Earned` : '0 XP for this problem' }}
            </span>
          </div>
        </div>
      </div>

      <!-- Next Tier Preview Indicator -->
      <div class="flex flex-col sm:items-end">
        <span class="text-[11px] font-black uppercase tracking-wider text-slate-600">
          Difficulty Adjusted
        </span>
        <span class="text-xs font-black uppercase px-3 py-1 rounded-full bg-white border border-slate-300 shadow-sm mt-0.5 text-slate-900">
          Tier: {{ nextTier }} 🚀
        </span>
      </div>
    </div>

    <!-- Diagnostic Misconception Alert Box (If Wrong) -->
    <div
      v-if="!isCorrect && misconceptionFeedback"
      class="bg-white rounded-2xl p-4 sm:p-5 border-2 border-rose-300 shadow-sm space-y-1.5"
    >
      <div class="flex items-center gap-1.5 text-xs font-black uppercase text-rose-800 tracking-wider">
        <span aria-hidden="true">⚠️</span>
        <span>Diagnostic Clue</span>
        <span v-if="misconceptionTag" class="text-slate-500 font-semibold lowercase">
          ({{ misconceptionTag }})
        </span>
      </div>
      <p class="text-base font-extrabold text-slate-900 leading-relaxed">
        {{ misconceptionFeedback }}
      </p>
    </div>

    <!-- Correct Answer Confirmation (If Wrong) -->
    <div v-if="!isCorrect" class="text-xs sm:text-sm font-bold text-slate-700">
      Correct Answer: <span class="font-black text-indigo-800 text-base">{{ correctAnswer }}</span>
    </div>

    <!-- Step-by-Step Solution Explanation -->
    <div class="bg-white rounded-2xl p-4 sm:p-5 border-2 border-slate-200 text-sm text-slate-900 space-y-1.5 shadow-sm">
      <span class="text-xs font-black uppercase text-indigo-800 block tracking-wider">
        Step-by-Step Walkthrough:
      </span>
      <p class="whitespace-pre-line leading-relaxed font-bold text-slate-800">
        {{ explanation }}
      </p>
    </div>

    <!-- Next Question Action Button -->
    <div class="pt-1">
      <button
        type="button"
        @click="$emit('next')"
        class="w-full btn-game-blue py-4 text-lg font-black shadow-game-blue cursor-pointer flex items-center justify-center gap-2 focus:outline-none focus-visible:ring-4 focus-visible:ring-blue-400 focus-visible:ring-offset-2"
        aria-label="Continue to next question"
      >
        <span>{{ isLastQuestion ? 'Complete Quest & View Results 🏆' : 'Next Question ➡️' }}</span>
        <span class="text-xs font-normal text-white/90 hidden sm:inline">(Press Enter)</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  isCorrect: boolean
  points: number
  nextTier: string
  correctAnswer: string
  misconceptionTag?: string | null
  misconceptionFeedback?: string | null
  explanation: string
  isLastQuestion: boolean
}>()

defineEmits<{
  (e: 'next'): void
}>()
</script>
