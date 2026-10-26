<template>
  <div class="min-h-[70vh] flex flex-col items-center justify-center p-4 text-center">
    <div class="w-full max-w-lg space-y-6">
      <!-- Mascot Illustration -->
      <div class="inline-flex items-center justify-center w-28 h-28 rounded-3xl bg-indigo-100 border-4 border-indigo-200 text-5xl shadow-xl animate-bounce" aria-hidden="true">
        🚀
      </div>

      <!-- Error Code Badge -->
      <div>
        <span class="px-4 py-1.5 rounded-full bg-accent-100 border-2 border-accent-300 text-warm-900 font-extrabold text-xs uppercase tracking-wider">
          Error 404
        </span>
      </div>

      <!-- Headings -->
      <div class="space-y-2">
        <h1 class="text-3xl sm:text-4xl font-extrabold text-warm-900 tracking-tight">
          Lost in Math Space?
        </h1>
        <p class="text-warm-700 text-sm sm:text-base font-semibold max-w-md mx-auto">
          We searched every dimension of Georgia and CBSE math, but we couldn't find this page or challenge.
        </p>
      </div>

      <!-- Action Buttons -->
      <div class="flex flex-col sm:flex-row gap-3 justify-center max-w-xs sm:max-w-md mx-auto pt-2">
        <NuxtLink
          to="/dashboard"
          class="flex-1 py-3.5 px-6 rounded-2xl font-extrabold text-sm sm:text-base text-white bg-primary-700 hover:bg-primary-800 active:scale-95 transition shadow-game-blue border-b-4 border-primary-900 flex items-center justify-center gap-2 min-h-[44px]"
        >
          <span>🏠</span>
          <span>Return to Dashboard</span>
        </NuxtLink>

        <NuxtLink
          to="/"
          class="flex-1 py-3.5 px-6 rounded-2xl font-bold text-sm sm:text-base text-warm-800 bg-white hover:bg-warm-100 active:scale-95 transition border-2 border-warm-300 flex items-center justify-center gap-2 min-h-[44px]"
        >
          <span>🗺️</span>
          <span>Browse Topics</span>
        </NuxtLink>
      </div>

      <!-- Back Link -->
      <div>
        <button
          type="button"
          @click="goBack"
          class="text-xs text-indigo-600 hover:text-indigo-800 font-extrabold transition hover:underline cursor-pointer"
        >
          ← Go back to previous page
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

// Set 404 HTTP status code for SSR crawlers and API clients
if (import.meta.server) {
  const event = useRequestEvent()
  if (event) {
    setResponseStatus(event, 404, 'Page Not Found')
  }
}

useHead({
  title: '404 - Page Not Found | MathQuest',
})

function goBack() {
  if (import.meta.client && window.history.length > 1) {
    router.back()
  } else {
    router.push('/dashboard')
  }
}
</script>
