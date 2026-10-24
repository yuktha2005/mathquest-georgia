<template>
  <div :class="['min-h-screen flex flex-col bg-slate-50 selection:bg-indigo-500 selection:text-white', isDyslexic ? 'dyslexia-font' : 'font-fredoka']">
    <!-- Skip to content for keyboard accessibility -->
    <a
      href="#main-content"
      class="sr-only focus:not-sr-only focus:fixed focus:top-3 focus:left-3 focus:z-50 focus:px-4 focus:py-2.5 focus:bg-indigo-600 focus:text-white focus:font-bold focus:rounded-xl focus:shadow-xl focus:ring-4 focus:ring-indigo-300"
    >
      Skip to main content
    </a>

    <!-- Render Cold Start Wake-Up Banner -->
    <transition
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="-translate-y-full opacity-0"
      enter-to-class="translate-y-0 opacity-100"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="translate-y-0 opacity-100"
      leave-to-class="-translate-y-full opacity-0"
    >
      <div
        v-if="isServerWakingUp"
        role="status"
        aria-live="polite"
        class="bg-amber-400 text-slate-900 px-4 py-3 text-center font-bold text-xs sm:text-sm border-b-4 border-amber-500 shadow-md flex items-center justify-center gap-2 z-50 sticky top-0"
      >
        <span class="animate-bounce text-lg" aria-hidden="true">🚀</span>
        <span>{{ wakeUpNotice || 'Waking up the MathQuest adventure server... Render free instances take ~50s to wake up from sleep. Thanks for your patience!' }}</span>
        <span class="inline-block w-4 h-4 border-2 border-slate-900 border-t-transparent rounded-full animate-spin ml-2" aria-hidden="true"></span>
      </div>
    </transition>

    <!-- Top Navigation Bar -->
    <header class="bg-white border-b-2 border-slate-200 sticky top-0 z-40 shadow-sm" role="banner">
      <div class="max-w-6xl mx-auto px-3 sm:px-6 py-2.5 sm:py-3 flex flex-wrap items-center justify-between gap-2 sm:gap-4">
        <!-- Logo -->
        <NuxtLink
          to="/"
          class="flex items-center gap-2 text-lg sm:text-2xl font-bold tracking-tight text-indigo-700 hover:text-indigo-800 transition group focus-visible:ring-4 focus-visible:ring-indigo-300 rounded-xl px-1"
          aria-label="MathQuest Georgia Home"
        >
          <span class="text-2xl sm:text-3xl group-hover:scale-110 transition-transform" aria-hidden="true">🎮</span>
          <div class="leading-none">
            <span class="text-indigo-700 font-extrabold">MathQuest</span>
            <span class="text-amber-600 text-sm sm:text-lg block sm:inline sm:ml-1 font-bold">{{ sessionStore.board === 'cbse' ? 'CBSE' : 'Georgia' }}</span>
          </div>
        </NuxtLink>

        <!-- Right Header Stats & Accessibility Controls -->
        <div class="flex items-center flex-wrap gap-1.5 sm:gap-3" role="toolbar" aria-label="Quick controls and player stats">
          <!-- Dyslexia Font Toggle Button -->
          <button
            type="button"
            role="switch"
            :aria-checked="isDyslexic"
            @click="toggleDyslexiaFont"
            class="px-2.5 sm:px-3 py-1.5 rounded-2xl border-2 transition flex items-center gap-1.5 text-xs sm:text-sm font-bold focus:outline-none focus-visible:ring-4 focus-visible:ring-indigo-400"
            :class="isDyslexic ? 'bg-indigo-600 text-white border-indigo-700 shadow-sm' : 'bg-slate-100 text-slate-700 border-slate-300 hover:bg-slate-200'"
            :title="isDyslexic ? 'Dyslexia font is ON (Click to switch to standard font)' : 'Switch to dyslexia-friendly font (Lexend)'"
            aria-label="Toggle dyslexia-friendly font"
          >
            <span class="font-mono text-sm font-extrabold" aria-hidden="true">Aa</span>
            <span class="hidden md:inline">{{ isDyslexic ? 'Dyslexia Font ON' : 'Dyslexia Font' }}</span>
          </button>

          <!-- Eval Benchmark Link -->
          <NuxtLink
            to="/eval"
            class="px-2.5 sm:px-3 py-1.5 rounded-2xl bg-slate-100 text-slate-700 font-bold text-xs sm:text-sm border-2 border-slate-300 hover:bg-slate-200 hover:text-indigo-800 transition flex items-center gap-1 focus-visible:ring-4 focus-visible:ring-indigo-400"
            aria-label="View evaluation benchmark"
          >
            <span aria-hidden="true">📊</span>
            <span class="hidden sm:inline">Eval</span>
          </NuxtLink>

          <!-- Grade Indicator -->
          <NuxtLink
            to="/"
            class="px-2.5 sm:px-3 py-1.5 rounded-2xl bg-indigo-50 text-indigo-800 font-bold text-xs sm:text-sm border-2 border-indigo-300 hover:bg-indigo-100 transition flex items-center gap-1 focus-visible:ring-4 focus-visible:ring-indigo-400"
            aria-label="Current Grade: Grade {{ sessionStore.grade }}"
          >
            <span aria-hidden="true">🎒</span>
            <span>G{{ sessionStore.grade }}</span>
          </NuxtLink>

          <!-- Current Streak -->
          <div
            v-if="sessionStore.streak > 0"
            role="status"
            aria-label="Current streak: {{ sessionStore.streak }} in a row"
            class="px-2.5 sm:px-3 py-1.5 rounded-2xl bg-orange-50 text-orange-700 font-bold text-xs sm:text-sm border-2 border-orange-300 flex items-center gap-1 animate-pop"
          >
            <span class="text-sm sm:text-base animate-pulse" aria-hidden="true">🔥</span>
            <span>{{ sessionStore.streak }}</span>
          </div>

          <!-- Total Score -->
          <div
            role="status"
            aria-label="Total score: {{ sessionStore.score }} experience points"
            class="px-2.5 sm:px-3.5 py-1.5 rounded-2xl bg-amber-50 text-amber-900 font-bold text-xs sm:text-sm border-2 border-amber-300 flex items-center gap-1 shadow-sm"
          >
            <span class="text-sm sm:text-base" aria-hidden="true">⭐</span>
            <span>{{ sessionStore.score }} XP</span>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main id="main-content" class="flex-1 max-w-6xl w-full mx-auto p-3 sm:p-6 md:p-8 outline-none" tabindex="-1">
      <NuxtPage />
    </main>

    <!-- Footer -->
    <footer class="bg-white border-t-2 border-slate-200 py-6 text-center text-xs text-slate-600" role="contentinfo">
      <div class="max-w-6xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
        <div class="flex items-center gap-1.5 text-slate-700 font-semibold flex-wrap justify-center">
          <span>Georgia Standards (MGSE)</span>
          <span aria-hidden="true">•</span>
          <span>CBSE Class 6 (NCERT)</span>
          <span aria-hidden="true">•</span>
          <span>Grades 5 & 6</span>
        </div>
        <div class="text-slate-500 text-xs">
          Safe AST math verification • Child-friendly adaptive learning • Zero hallucinated math
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useApi } from '~/composables/useApi'
import { useSessionStore } from '~/stores/session'

const { isServerWakingUp, wakeUpNotice, checkHealth } = useApi()
const sessionStore = useSessionStore()

const isDyslexic = ref(false)

const toggleDyslexiaFont = () => {
  isDyslexic.value = !isDyslexic.value
  if (import.meta.client) {
    if (isDyslexic.value) {
      document.documentElement.classList.add('dyslexia-font')
      localStorage.setItem('mathquest_dyslexia_font', 'true')
    } else {
      document.documentElement.classList.remove('dyslexia-font')
      localStorage.setItem('mathquest_dyslexia_font', 'false')
    }
  }
}

onMounted(async () => {
  sessionStore.loadFromStorage()

  // Load dyslexia font preference
  if (import.meta.client) {
    const savedDyslexia = localStorage.getItem('mathquest_dyslexia_font')
    if (savedDyslexia === 'true') {
      isDyslexic.value = true
      document.documentElement.classList.add('dyslexia-font')
    }
  }

  // Gentle background ping to warm up backend on load
  try {
    await checkHealth()
  } catch (e) {
    // Expected if cold start or local backend waking up
  }
})
</script>
