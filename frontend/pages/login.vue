<template>
  <div class="min-h-[80vh] flex items-center justify-center py-6 px-4">
    <div class="w-full max-w-md">
      <!-- Brand & Mascot Header -->
      <div class="text-center mb-6">
        <div class="inline-flex items-center justify-center w-16 h-16 rounded-3xl bg-indigo-100 text-3xl mb-3 shadow-inner animate-bounce">
          🎮
        </div>
        <h1 class="text-3xl font-extrabold text-slate-900 tracking-tight">
          Welcome to <span class="text-indigo-600">MathQuest</span>
        </h1>
        <p class="text-slate-600 text-sm mt-1">
          Sign in to save your math adventure, earn badges, and track mastery!
        </p>
      </div>

      <!-- Main Login Card -->
      <div class="bg-white rounded-3xl border-2 border-slate-200 shadow-xl p-6 sm:p-8">
        <!-- Error Banner -->
        <transition
          enter-active-class="transition duration-200 ease-out"
          enter-from-class="-translate-y-2 opacity-0"
          enter-to-class="translate-y-0 opacity-100"
        >
          <div
            v-if="errorMessage"
            role="alert"
            class="mb-5 p-3.5 rounded-2xl bg-rose-50 border-2 border-rose-300 text-rose-800 text-xs sm:text-sm font-semibold flex items-start gap-2.5"
          >
            <span class="text-lg leading-none" aria-hidden="true">⚠️</span>
            <div class="flex-1">
              <span>{{ errorMessage }}</span>
            </div>
          </div>
        </transition>

        <!-- Form -->
        <form @submit.prevent="handleLogin" class="space-y-4" novalidate>
          <!-- Email Input -->
          <div>
            <label for="email" class="block text-xs sm:text-sm font-bold text-slate-700 mb-1">
              Email Address
            </label>
            <div class="relative">
              <span class="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-400" aria-hidden="true">
                📧
              </span>
              <input
                id="email"
                v-model="email"
                type="email"
                autocomplete="email"
                required
                :disabled="isLoading"
                placeholder="student@example.com"
                class="w-full pl-10 pr-4 py-2.5 rounded-2xl border-2 transition text-sm text-slate-800 focus:outline-none focus:ring-4 focus:ring-indigo-200"
                :class="errors.email ? 'border-rose-400 bg-rose-50/50' : 'border-slate-300 focus:border-indigo-500'"
              />
            </div>
            <p v-if="errors.email" class="text-xs text-rose-600 mt-1 font-semibold pl-1">
              {{ errors.email }}
            </p>
          </div>

          <!-- Password Input -->
          <div>
            <div class="flex items-center justify-between mb-1">
              <label for="password" class="block text-xs sm:text-sm font-bold text-slate-700">
                Password
              </label>
              <NuxtLink
                to="/forgot"
                class="text-xs text-indigo-600 hover:text-indigo-800 font-bold transition hover:underline"
              >
                Forgot password?
              </NuxtLink>
            </div>
            <div class="relative">
              <span class="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-400" aria-hidden="true">
                🔒
              </span>
              <input
                id="password"
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                autocomplete="current-password"
                required
                :disabled="isLoading"
                placeholder="••••••••"
                class="w-full pl-10 pr-11 py-2.5 rounded-2xl border-2 transition text-sm text-slate-800 focus:outline-none focus:ring-4 focus:ring-indigo-200"
                :class="errors.password ? 'border-rose-400 bg-rose-50/50' : 'border-slate-300 focus:border-indigo-500'"
              />
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="absolute inset-y-0 right-0 pr-3.5 flex items-center text-slate-400 hover:text-slate-600 focus:outline-none"
                :aria-label="showPassword ? 'Hide password' : 'Show password'"
              >
                <span>{{ showPassword ? '🙈' : '👁️' }}</span>
              </button>
            </div>
            <p v-if="errors.password" class="text-xs text-rose-600 mt-1 font-semibold pl-1">
              {{ errors.password }}
            </p>
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            :disabled="isLoading"
            class="w-full mt-2 py-3 px-4 rounded-2xl font-extrabold text-sm sm:text-base text-white bg-indigo-600 hover:bg-indigo-700 active:scale-[0.98] transition shadow-md hover:shadow-lg disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2 border-b-4 border-indigo-800"
          >
            <span v-if="isLoading" class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" aria-hidden="true"></span>
            <span>{{ isLoading ? 'Signing In...' : 'Sign In 🚀' }}</span>
          </button>
        </form>

        <!-- Divider -->
        <div class="relative my-6">
          <div class="absolute inset-0 flex items-center" aria-hidden="true">
            <div class="w-full border-t-2 border-slate-200"></div>
          </div>
          <div class="relative flex justify-center text-xs uppercase tracking-wider font-extrabold">
            <span class="bg-white px-3 text-slate-400">or</span>
          </div>
        </div>

        <!-- Continue as Guest Button -->
        <button
          type="button"
          @click="handleGuest"
          :disabled="isLoading"
          class="w-full py-2.5 px-4 rounded-2xl font-bold text-sm text-slate-700 bg-slate-100 hover:bg-slate-200 active:scale-[0.98] transition border-2 border-slate-300 flex items-center justify-center gap-2"
        >
          <span>🎒</span>
          <span>Continue as Guest</span>
        </button>
      </div>

      <!-- Footer / Switch to Signup -->
      <div class="text-center mt-6 text-sm text-slate-600 font-semibold">
        Don't have an account yet?
        <NuxtLink to="/signup" class="text-indigo-600 hover:text-indigo-800 font-extrabold hover:underline ml-1">
          Create free account ✨
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '~/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const showPassword = ref(false)
const isLoading = ref(false)
const errorMessage = ref('')

const errors = reactive({
  email: '',
  password: '',
})

function validateForm(): boolean {
  errors.email = ''
  errors.password = ''
  let isValid = true

  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!email.value.trim()) {
    errors.email = 'Please enter your email address.'
    isValid = false
  } else if (!emailPattern.test(email.value.trim())) {
    errors.email = 'Please enter a valid email address (e.g. student@school.edu).'
    isValid = false
  }

  if (!password.value) {
    errors.password = 'Please enter your password.'
    isValid = false
  }

  return isValid
}

async function handleLogin() {
  errorMessage.value = ''
  if (!validateForm()) return

  isLoading.value = true
  try {
    await authStore.signIn(email.value, password.value)

    // Redirect to requested page or dashboard
    const target = (route.query.redirect as string) || (authStore.needsSetup ? '/onboarding' : '/dashboard')
    await router.push(target)
  } catch (err: any) {
    errorMessage.value = err.message || 'Unable to sign in. Please check your credentials.'
  } finally {
    isLoading.value = false
  }
}

async function handleGuest() {
  authStore.continueAsGuest()
  const target = (route.query.redirect as string) || '/dashboard'
  await router.push(target)
}
</script>
