<template>
  <div :class="['min-h-screen flex flex-col bg-warm-50 text-warm-900 selection:bg-primary-600 selection:text-white', isDyslexic ? 'dyslexia-font' : 'font-fredoka']">
    <!-- Global Nuxt Loading Progress Bar -->
    <NuxtLoadingIndicator color="#4338ca" :height="3" />

    <!-- Skip to Content (Keyboard Accessibility) -->
    <a
      href="#main-content"
      class="sr-only focus:not-sr-only focus:fixed focus:top-3 focus:left-3 focus:z-50 focus:px-4 focus:py-2.5 focus:bg-primary-700 focus:text-white focus:font-bold focus:rounded-xl focus:shadow-xl focus:ring-4 focus:ring-primary-300 min-h-[44px] flex items-center"
    >
      Skip to main content
    </a>

    <!-- Render Cold Start Wake-Up Banner (> 3s latency) -->
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
        class="bg-accent-400 text-warm-900 px-4 py-3 text-center font-bold text-xs sm:text-sm border-b-4 border-accent-600 shadow-md flex items-center justify-center gap-2 z-50 sticky top-0"
      >
        <span class="animate-bounce text-lg" aria-hidden="true">🚀</span>
        <span>{{ wakeUpNotice || 'Waking up the MathQuest adventure server... Free tier instances take ~50s to wake up from sleep. Thanks for your patience!' }}</span>
        <span class="inline-block w-4 h-4 border-2 border-warm-900 border-t-transparent rounded-full animate-spin ml-2" aria-hidden="true"></span>
      </div>
    </transition>

    <!-- Desktop & Tablet Top Navbar (Only visible when user is authenticated and not on auth pages) -->
    <header v-if="showNavigation" class="bg-white border-b-2 border-warm-200 sticky top-0 z-30 shadow-warm-sm" role="banner">
      <div class="max-w-6xl mx-auto px-3 sm:px-6 py-2.5 sm:py-3 flex items-center justify-between gap-2 sm:gap-4">
        <!-- Brand Logo -->
        <NuxtLink
          to="/dashboard"
          class="flex items-center gap-2 text-lg sm:text-2xl font-bold tracking-tight text-indigo-700 hover:text-indigo-800 transition group focus-visible:ring-4 focus-visible:ring-indigo-300 rounded-xl px-1"
          aria-label="MathQuest Dashboard"
        >
          <span class="text-2xl sm:text-3xl group-hover:scale-110 transition-transform" aria-hidden="true">🎮</span>
          <div class="leading-none">
            <span class="text-indigo-700 font-extrabold">MathQuest</span>
            <span class="text-amber-600 text-xs sm:text-sm block sm:inline sm:ml-1 font-bold">
              {{ sessionStore.board === 'cbse' ? 'CBSE' : 'Georgia' }}
            </span>
          </div>
        </NuxtLink>

        <!-- Desktop Navigation Links -->
        <nav class="hidden md:flex items-center gap-1 bg-slate-100 p-1 rounded-2xl border border-slate-200" aria-label="Main Navigation">
          <NuxtLink
            to="/dashboard"
            class="px-3.5 py-1.5 rounded-xl text-xs sm:text-sm font-extrabold transition flex items-center gap-1.5"
            :class="isActive('/dashboard') ? 'bg-white text-indigo-700 shadow-sm' : 'text-slate-600 hover:text-indigo-600'"
          >
            <span>🏠</span>
            <span>Dashboard</span>
          </NuxtLink>

          <NuxtLink
            to="/"
            class="px-3.5 py-1.5 rounded-xl text-xs sm:text-sm font-extrabold transition flex items-center gap-1.5"
            :class="isActive('/') ? 'bg-white text-indigo-700 shadow-sm' : 'text-slate-600 hover:text-indigo-600'"
          >
            <span>🗺️</span>
            <span>Topics</span>
          </NuxtLink>

          <NuxtLink
            to="/progress"
            class="px-3.5 py-1.5 rounded-xl text-xs sm:text-sm font-extrabold transition flex items-center gap-1.5"
            :class="isActive('/progress') ? 'bg-white text-indigo-700 shadow-sm' : 'text-slate-600 hover:text-indigo-600'"
          >
            <span>📊</span>
            <span>Progress</span>
          </NuxtLink>

          <NuxtLink
            to="/eval"
            class="px-3 py-1.5 rounded-xl text-xs sm:text-sm font-extrabold transition flex items-center gap-1"
            :class="isActive('/eval') ? 'bg-white text-indigo-700 shadow-sm' : 'text-slate-600 hover:text-indigo-600'"
          >
            <span>🔬</span>
            <span>Eval</span>
          </NuxtLink>
        </nav>

        <!-- Right Header Stats & Profile Controls -->
        <div class="flex items-center gap-1.5 sm:gap-3" role="toolbar" aria-label="Player profile and quick stats">
          <!-- Dyslexia Font Toggle -->
          <button
            type="button"
            role="switch"
            :aria-checked="isDyslexic"
            @click="toggleDyslexia"
            class="px-2.5 sm:px-3 py-1.5 rounded-2xl border-2 transition flex items-center gap-1.5 text-xs sm:text-sm font-bold focus:outline-none focus-visible:ring-4 focus-visible:ring-indigo-400"
            :class="isDyslexic ? 'bg-indigo-600 text-white border-indigo-700 shadow-sm' : 'bg-slate-100 text-slate-700 border-slate-300 hover:bg-slate-200'"
            :title="isDyslexic ? 'Dyslexia font ON (Click for standard font)' : 'Switch to dyslexia-friendly font (Lexend)'"
            aria-label="Toggle dyslexia-friendly font"
          >
            <span class="font-mono text-xs font-extrabold" aria-hidden="true">Aa</span>
            <span class="hidden lg:inline">{{ isDyslexic ? 'Dyslexic ON' : 'Dyslexic' }}</span>
          </button>

          <!-- Current Grade Pill -->
          <NuxtLink
            to="/"
            class="hidden sm:flex px-2.5 sm:px-3 py-1.5 rounded-2xl bg-indigo-50 text-indigo-800 font-bold text-xs sm:text-sm border-2 border-indigo-200 hover:bg-indigo-100 transition items-center gap-1"
            aria-label="Current Grade: Grade {{ sessionStore.grade }}"
          >
            <span aria-hidden="true">🎒</span>
            <span>G{{ sessionStore.grade }}</span>
          </NuxtLink>

          <!-- Total Score Pill -->
          <div
            role="status"
            aria-label="Total score: {{ sessionStore.score }} experience points"
            class="px-2.5 sm:px-3 py-1.5 rounded-2xl bg-amber-50 text-amber-900 font-bold text-xs sm:text-sm border-2 border-amber-300 flex items-center gap-1 shadow-sm"
          >
            <span class="text-sm" aria-hidden="true">⭐</span>
            <span>{{ sessionStore.score }} XP</span>
          </div>

          <!-- Profile Menu (Desktop) -->
          <div v-if="authStore.isAuthenticated" class="relative">
            <button
              type="button"
              @click="isProfileMenuOpen = !isProfileMenuOpen"
              class="flex items-center gap-2 pl-2 pr-3 py-1.5 rounded-2xl bg-indigo-50 hover:bg-indigo-100 border-2 border-indigo-200 text-indigo-900 font-extrabold text-xs sm:text-sm transition focus:outline-none focus-visible:ring-4 focus-visible:ring-indigo-400"
              aria-haspopup="true"
              :aria-expanded="isProfileMenuOpen"
            >
              <span class="w-6 h-6 rounded-full bg-indigo-600 text-white flex items-center justify-center text-xs">
                🧙‍♂️
              </span>
              <span class="max-w-[80px] sm:max-w-[110px] truncate">{{ authStore.displayName }}</span>
              <span class="text-xs text-indigo-500" aria-hidden="true">▼</span>
            </button>

            <!-- Profile Dropdown Menu -->
            <div
              v-if="isProfileMenuOpen"
              class="absolute right-0 mt-2 w-48 bg-white rounded-2xl shadow-xl border-2 border-slate-200 py-2 z-50 text-slate-800 animate-pop"
              role="menu"
            >
              <div class="px-4 py-2 border-b border-slate-100">
                <p class="text-xs text-slate-400 font-bold uppercase tracking-wider">Signed in as</p>
                <p class="text-sm font-extrabold text-slate-900 truncate">{{ authStore.displayName }}</p>
              </div>

              <NuxtLink
                to="/profile"
                @click="isProfileMenuOpen = false"
                class="flex items-center gap-2 px-4 py-2 text-xs sm:text-sm font-bold text-slate-700 hover:bg-indigo-50 hover:text-indigo-700 transition"
                role="menuitem"
              >
                <span>👤</span>
                <span>Profile & Settings</span>
              </NuxtLink>

              <NuxtLink
                to="/progress"
                @click="isProfileMenuOpen = false"
                class="flex items-center gap-2 px-4 py-2 text-xs sm:text-sm font-bold text-slate-700 hover:bg-indigo-50 hover:text-indigo-700 transition"
                role="menuitem"
              >
                <span>📊</span>
                <span>Mastery & History</span>
              </NuxtLink>

              <div class="border-t border-slate-100 my-1"></div>

              <button
                type="button"
                @click="handleLogout"
                class="w-full text-left flex items-center gap-2 px-4 py-2 text-xs sm:text-sm font-bold text-rose-600 hover:bg-rose-50 transition"
                role="menuitem"
              >
                <span>🚪</span>
                <span>Logout</span>
              </button>
            </div>
          </div>

          <!-- Guest / Login CTA (if not authenticated) -->
          <div v-else class="flex items-center gap-1.5">
            <NuxtLink
              to="/profile"
              class="px-3 py-1.5 rounded-2xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs sm:text-sm transition border border-slate-300"
              title="Settings & Accessibility"
            >
              ⚙️
            </NuxtLink>
            <NuxtLink
              to="/login"
              class="px-3 py-1.5 rounded-2xl bg-indigo-600 hover:bg-indigo-700 text-white font-extrabold text-xs sm:text-sm transition shadow-sm"
            >
              Sign In
            </NuxtLink>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content Slot (with mobile bottom padding only when tab bar is visible) -->
    <main
      id="main-content"
      class="flex-1 max-w-6xl w-full mx-auto p-3 sm:p-6 md:p-8 outline-none"
      :class="showNavigation ? 'pb-24 md:pb-8' : 'pb-8'"
      tabindex="-1"
    >
      <slot />
    </main>

    <!-- Mobile Bottom Tab Bar (Only visible when user is authenticated and not on auth pages) -->
    <nav
      v-if="showNavigation"
      class="md:hidden fixed bottom-0 inset-x-0 bg-white/95 backdrop-blur-md border-t-2 border-warm-200 z-40 shadow-lg px-2 py-1 flex items-center justify-around"
      role="navigation"
      aria-label="Mobile Navigation Bar"
    >
      <NuxtLink
        to="/dashboard"
        class="flex flex-col items-center justify-center py-1 px-3 rounded-xl transition text-xs font-bold min-h-[48px] min-w-[48px]"
        :class="isActive('/dashboard') ? 'text-primary-700 font-extrabold scale-105' : 'text-warm-500 hover:text-warm-800'"
      >
        <span class="text-lg" aria-hidden="true">🏠</span>
        <span>Home</span>
      </NuxtLink>

      <NuxtLink
        to="/"
        class="flex flex-col items-center justify-center py-1 px-3 rounded-xl transition text-xs font-bold min-h-[48px] min-w-[48px]"
        :class="isActive('/') ? 'text-primary-700 font-extrabold scale-105' : 'text-warm-500 hover:text-warm-800'"
      >
        <span class="text-lg" aria-hidden="true">🗺️</span>
        <span>Topics</span>
      </NuxtLink>

      <NuxtLink
        to="/progress"
        class="flex flex-col items-center justify-center py-1 px-3 rounded-xl transition text-xs font-bold min-h-[48px] min-w-[48px]"
        :class="isActive('/progress') ? 'text-primary-700 font-extrabold scale-105' : 'text-warm-500 hover:text-warm-800'"
      >
        <span class="text-lg" aria-hidden="true">📊</span>
        <span>Progress</span>
      </NuxtLink>

      <NuxtLink
        to="/profile"
        class="flex flex-col items-center justify-center py-1 px-3 rounded-xl transition text-xs font-bold min-h-[48px] min-w-[48px]"
        :class="isActive('/profile') ? 'text-primary-700 font-extrabold scale-105' : 'text-warm-500 hover:text-warm-800'"
      >
        <span class="text-lg" aria-hidden="true">👤</span>
        <span>Profile</span>
      </NuxtLink>
    </nav>

    <!-- Footer (Only visible when user is authenticated and not on auth pages) -->
    <footer v-if="showNavigation" class="bg-white border-t-2 border-warm-200 py-6 text-center text-xs text-warm-600 hidden md:block" role="contentinfo">
      <div class="max-w-6xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
        <div class="flex items-center gap-1.5 text-warm-700 font-semibold flex-wrap justify-center">
          <span>Georgia Standards (MGSE)</span>
          <span aria-hidden="true">•</span>
          <span>CBSE Class 6 (NCERT)</span>
          <span aria-hidden="true">•</span>
          <span>Grades 5 & 6</span>
        </div>
        <div class="text-warm-500 text-xs">
          Safe AST math verification • Child-friendly adaptive learning • Zero hallucinated math
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useApi } from '~/composables/useApi'
import { useSessionStore } from '~/stores/session'
import { useAuthStore } from '~/stores/auth'
import { useAccessibility } from '~/composables/useAccessibility'

const route = useRoute()
const { isServerWakingUp, wakeUpNotice } = useApi()
const sessionStore = useSessionStore()
const authStore = useAuthStore()
const { isDyslexic, toggleDyslexia } = useAccessibility()

const isProfileMenuOpen = ref(false)

const showNavigation = computed(() => {
  if (!authStore.isAuthenticated) return false
  if (['/signup', '/login', '/forgot', '/onboarding'].includes(route.path)) {
    return false
  }
  return true
})

function isActive(path: string): boolean {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}

async function handleLogout() {
  isProfileMenuOpen.value = false
  await authStore.signOut()
}
</script>
