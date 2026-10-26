<template>
  <div class="min-h-[80vh] flex items-center justify-center py-6 px-4">
    <div class="w-full max-w-md">
      <!-- Mascot Header -->
      <div class="text-center mb-6">
        <div class="inline-flex items-center justify-center w-16 h-16 rounded-3xl bg-amber-100 text-3xl mb-3 shadow-inner animate-bounce">
          ✨
        </div>
        <h1 class="text-3xl font-extrabold text-slate-900 tracking-tight">
          Join the <span class="text-indigo-600">Adventure</span>
        </h1>
        <p class="text-slate-600 text-sm mt-1">
          Create your MathQuest account to unlock achievements and track your mastery!
        </p>
      </div>

      <!-- Main Signup Card -->
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
        <form @submit.prevent="handleSignup" class="space-y-4" novalidate>
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
            <label for="password" class="block text-xs sm:text-sm font-bold text-slate-700 mb-1">
              Password <span class="text-slate-400 font-normal">(6+ characters)</span>
            </label>
            <div class="relative">
              <span class="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-400" aria-hidden="true">
                🔒
              </span>
              <input
                id="password"
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                autocomplete="new-password"
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

          <!-- Confirm Password Input -->
          <div>
            <label for="confirmPassword" class="block text-xs sm:text-sm font-bold text-slate-700 mb-1">
              Confirm Password
            </label>
            <div class="relative">
              <span class="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-400" aria-hidden="true">
                🔁
              </span>
              <input
                id="confirmPassword"
                v-model="confirmPassword"
                :type="showPassword ? 'text' : 'password'"
                autocomplete="new-password"
                required
                :disabled="isLoading"
                placeholder="••••••••"
                class="w-full pl-10 pr-4 py-2.5 rounded-2xl border-2 transition text-sm text-slate-800 focus:outline-none focus:ring-4 focus:ring-indigo-200"
                :class="errors.confirmPassword ? 'border-rose-400 bg-rose-50/50' : 'border-slate-300 focus:border-indigo-500'"
              />
            </div>
            <p v-if="errors.confirmPassword" class="text-xs text-rose-600 mt-1 font-semibold pl-1">
              {{ errors.confirmPassword }}
            </p>
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            :disabled="isLoading"
            class="w-full mt-2 py-3 px-4 rounded-2xl font-extrabold text-sm sm:text-base text-white bg-indigo-600 hover:bg-indigo-700 active:scale-[0.98] transition shadow-md hover:shadow-lg disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2 border-b-4 border-indigo-800"
          >
            <span v-if="isLoading" class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" aria-hidden="true"></span>
            <span>{{ isLoading ? 'Creating Account...' : 'Start My Adventure 🌟' }}</span>
          </button>
        </form>
      </div>

      <!-- Footer / Switch to Login -->
      <div class="text-center mt-6 text-sm text-slate-600 font-semibold">
        Already have an account?
        <NuxtLink to="/login" class="text-indigo-600 hover:text-indigo-800 font-extrabold hover:underline ml-1">
          Sign In here ✨
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '~/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const showPassword = ref(false)
const isLoading = ref(false)
const errorMessage = ref('')

const errors = reactive({
  email: '',
  password: '',
  confirmPassword: '',
})

function validateForm(): boolean {
  errors.email = ''
  errors.password = ''
  errors.confirmPassword = ''
  let isValid = true

  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!email.value.trim()) {
    errors.email = 'Please enter an email address.'
    isValid = false
  } else if (!emailPattern.test(email.value.trim())) {
    errors.email = 'Please enter a valid email address.'
    isValid = false
  }

  if (!password.value) {
    errors.password = 'Please create a password.'
    isValid = false
  } else if (password.value.length < 6) {
    errors.password = 'Password must be at least 6 characters long.'
    isValid = false
  }

  if (!confirmPassword.value) {
    errors.confirmPassword = 'Please re-enter your password.'
    isValid = false
  } else if (password.value !== confirmPassword.value) {
    errors.confirmPassword = 'Passwords do not match.'
    isValid = false
  }

  return isValid
}

async function handleSignup() {
  errorMessage.value = ''
  if (!validateForm()) return

  isLoading.value = true
  try {
    await authStore.signUp(email.value, password.value)
    // After signup, take user to the first-time setup step
    await router.push('/onboarding')
  } catch (err: any) {
    errorMessage.value = err.message || 'Unable to create account. Please try again.'
  } finally {
    isLoading.value = false
  }
}
</script>
