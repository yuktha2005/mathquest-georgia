<template>
  <div :class="['min-h-screen flex flex-col bg-warm-50 text-warm-900 selection:bg-primary-600 selection:text-white', isDyslexic ? 'dyslexia-font' : 'font-fredoka']">
    <!-- Global Nuxt Loading Progress Bar -->
    <NuxtLoadingIndicator color="#4338ca" :height="3" />

    <!-- Cold Start Wake-Up Banner -->
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
        class="bg-accent-400 text-warm-900 px-4 py-2.5 text-center font-bold text-xs sm:text-sm border-b-4 border-accent-600 shadow-md flex items-center justify-center gap-2 z-50 sticky top-0"
      >
        <span class="animate-bounce" aria-hidden="true">🚀</span>
        <span>{{ wakeUpNotice || 'Waking up the MathQuest adventure server... Hang tight!' }}</span>
      </div>
    </transition>

    <!-- Minimalist Focus Header -->
    <header class="bg-white border-b-2 border-warm-200 sticky top-0 z-30 shadow-warm-sm" role="banner">
      <div class="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between gap-3">
        <!-- Back / Exit Button with Confirmation -->
        <button
          type="button"
          @click="showExitModal = true"
          class="flex items-center gap-1.5 px-3.5 py-1.5 rounded-2xl bg-warm-100 hover:bg-warm-200 active:scale-95 text-warm-800 font-extrabold text-xs sm:text-sm border-2 border-warm-300 transition focus:outline-none focus-visible:ring-4 focus-visible:ring-primary-400 min-h-[44px]"
          aria-label="Exit current activity"
        >
          <span aria-hidden="true">←</span>
          <span>Exit</span>
        </button>

        <!-- Centered Activity Title -->
        <div class="text-center font-extrabold text-warm-900 text-sm sm:text-base flex items-center gap-1.5">
          <span class="text-primary-700">🎮 MathQuest</span>
          <span class="text-warm-400 font-normal">|</span>
          <span class="text-accent-700 font-bold capitalize">{{ sessionStore.topic }}</span>
          <span class="hidden sm:inline text-xs text-warm-500 font-semibold">(Grade {{ sessionStore.grade }})</span>
        </div>

        <!-- Right Quick Stats (Streak & Dyslexia Toggle) -->
        <div class="flex items-center gap-2">
          <!-- Dyslexia Font Toggle -->
          <button
            type="button"
            role="switch"
            :aria-checked="isDyslexic"
            @click="toggleDyslexiaFont"
            class="px-2.5 py-1.5 rounded-xl border-2 transition text-xs font-bold"
            :class="isDyslexic ? 'bg-indigo-600 text-white border-indigo-700' : 'bg-slate-100 text-slate-700 border-slate-300 hover:bg-slate-200'"
            title="Toggle dyslexia-friendly font"
          >
            Aa
          </button>

          <!-- Current Streak -->
          <div
            v-if="sessionStore.streak > 0"
            class="px-2.5 py-1 rounded-xl bg-orange-100 text-orange-800 font-extrabold text-xs flex items-center gap-1 border border-orange-300"
          >
            <span>🔥</span>
            <span>{{ sessionStore.streak }}</span>
          </div>

          <!-- Total Score -->
          <div class="px-2.5 py-1 rounded-xl bg-amber-100 text-amber-900 font-extrabold text-xs flex items-center gap-1 border border-amber-300">
            <span>⭐</span>
            <span>{{ sessionStore.score }}</span>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Focus Content (Full width/height, distraction-free) -->
    <main id="main-content" class="flex-1 max-w-5xl w-full mx-auto p-3 sm:p-6 md:p-8 outline-none" tabindex="-1">
      <slot />
    </main>

    <!-- Exit Confirmation Modal Dialog -->
    <transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0 scale-95"
      enter-to-class="opacity-100 scale-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100 scale-100"
      leave-to-class="opacity-0 scale-95"
    >
      <div
        v-if="showExitModal"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
        aria-describedby="modal-description"
      >
        <div class="bg-white rounded-3xl border-2 border-slate-200 shadow-2xl max-w-sm w-full p-6 text-center space-y-4 animate-pop">
          <div class="w-16 h-16 mx-auto rounded-3xl bg-amber-100 text-amber-700 flex items-center justify-center text-3xl shadow-inner">
            ⚠️
          </div>

          <h2 id="modal-title" class="text-xl font-extrabold text-slate-900">
            Exit Quiz?
          </h2>

          <p id="modal-description" class="text-sm text-slate-600 font-semibold">
            Progress will be lost! If you leave now, your current round answers and streak will be reset.
          </p>

          <div class="flex flex-col sm:flex-row gap-2 pt-2">
            <button
              type="button"
              @click="showExitModal = false"
              class="flex-1 py-3 px-4 rounded-2xl font-extrabold text-sm text-white bg-indigo-600 hover:bg-indigo-700 active:scale-95 transition shadow border-b-4 border-indigo-800"
            >
              Keep Playing ⚔️
            </button>

            <button
              type="button"
              @click="confirmExit"
              class="flex-1 py-3 px-4 rounded-2xl font-bold text-sm text-rose-700 bg-rose-50 hover:bg-rose-100 active:scale-95 transition border-2 border-rose-200"
            >
              Yes, Exit
            </button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useApi } from '~/composables/useApi'
import { useSessionStore } from '~/stores/session'

const router = useRouter()
const { isServerWakingUp, wakeUpNotice } = useApi()
const sessionStore = useSessionStore()

const showExitModal = ref(false)
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

function confirmExit() {
  showExitModal.value = false
  router.push('/dashboard')
}
</script>
