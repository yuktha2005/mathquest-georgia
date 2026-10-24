<template>
  <div class="min-h-screen flex flex-col items-center justify-center bg-slate-50 p-4 font-fredoka selection:bg-indigo-500 selection:text-white">
    <div class="w-full max-w-lg text-center space-y-6">
      <!-- Mascot / Visual Error Illustration -->
      <div class="inline-flex items-center justify-center w-28 h-28 rounded-3xl bg-indigo-100 border-4 border-indigo-200 text-5xl shadow-xl animate-bounce">
        {{ error?.statusCode === 404 ? '🚀' : '👾' }}
      </div>

      <!-- Error Code Badge -->
      <div>
        <span class="px-4 py-1.5 rounded-full bg-amber-100 border-2 border-amber-300 text-amber-900 font-extrabold text-xs uppercase tracking-wider">
          Error {{ error?.statusCode || 404 }}
        </span>
      </div>

      <!-- Headings -->
      <div class="space-y-2">
        <h1 class="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
          {{ is404 ? 'Lost in Math Space?' : 'Oops! Something went sideways' }}
        </h1>
        <p class="text-slate-600 text-sm sm:text-base font-semibold max-w-md mx-auto">
          {{ is404
            ? "We searched every dimension of Georgia and CBSE math, but we couldn't find this page or challenge."
            : (error?.message || "Don't worry! Your adventurer progress and points are completely safe.")
          }}
        </p>
      </div>

      <!-- Action Buttons (Clear primary action + clear way back) -->
      <div class="flex flex-col sm:flex-row gap-3 justify-center max-w-xs sm:max-w-md mx-auto pt-2">
        <button
          type="button"
          @click="handleClearError"
          class="flex-1 py-3.5 px-6 rounded-2xl font-extrabold text-sm sm:text-base text-white bg-indigo-600 hover:bg-indigo-700 active:scale-95 transition shadow-md hover:shadow-lg border-b-4 border-indigo-800 flex items-center justify-center gap-2"
        >
          <span>🏠</span>
          <span>Return to Dashboard</span>
        </button>

        <button
          type="button"
          @click="handleBrowseTopics"
          class="flex-1 py-3.5 px-6 rounded-2xl font-bold text-sm sm:text-base text-slate-700 bg-white hover:bg-slate-100 active:scale-95 transition border-2 border-slate-300 flex items-center justify-center gap-2"
        >
          <span>🗺️</span>
          <span>Browse Topics</span>
        </button>
      </div>

      <!-- Back Link -->
      <div>
        <button
          type="button"
          @click="handleGoBack"
          class="text-xs text-indigo-600 hover:text-indigo-800 font-extrabold transition hover:underline"
        >
          ← Go back to previous page
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  error: {
    type: Object,
    default: () => ({ statusCode: 404, message: 'Page not found' }),
  },
})

const router = useRouter()
const is404 = computed(() => !props.error?.statusCode || props.error.statusCode === 404)

function handleClearError() {
  clearError({ redirect: '/dashboard' })
}

function handleBrowseTopics() {
  clearError({ redirect: '/' })
}

function handleGoBack() {
  if (import.meta.client && window.history.length > 1) {
    clearError()
    router.back()
  } else {
    clearError({ redirect: '/dashboard' })
  }
}
</script>
