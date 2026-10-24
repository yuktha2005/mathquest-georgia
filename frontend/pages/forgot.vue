<template>
  <div class="min-h-[80vh] flex items-center justify-center py-6 px-4">
    <div class="w-full max-w-md">
      <!-- Mascot Header -->
      <div class="text-center mb-6">
        <div class="inline-flex items-center justify-center w-16 h-16 rounded-3xl bg-indigo-100 text-3xl mb-3 shadow-inner">
          🔑
        </div>
        <h1 class="text-3xl font-extrabold text-slate-900 tracking-tight">
          Reset <span class="text-indigo-600">Password</span>
        </h1>
        <p class="text-slate-600 text-sm mt-1">
          Enter your email and we'll send you instructions to recover your adventure!
        </p>
      </div>

      <!-- Main Card -->
      <div class="bg-white rounded-3xl border-2 border-slate-200 shadow-xl p-6 sm:p-8">
        <!-- Success Confirmation State -->
        <div v-if="isSuccess" class="text-center py-4 space-y-4">
          <div class="w-16 h-16 mx-auto rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center text-3xl font-bold">
            ✓
          </div>
          <h2 class="text-xl font-extrabold text-slate-800">
            Check your email inbox!
          </h2>
          <p class="text-sm text-slate-600">
            We have sent a password reset link to <strong class="text-slate-800">{{ email }}</strong>. Click the link in the email to set a new password.
          </p>
          <div class="pt-2">
            <NuxtLink
              to="/login"
              class="inline-flex items-center justify-center w-full py-2.5 px-4 rounded-2xl font-bold text-sm text-white bg-indigo-600 hover:bg-indigo-700 transition"
            >
              Back to Sign In
            </NuxtLink>
          </div>
        </div>

        <!-- Form State -->
        <form v-else @submit.prevent="handleReset" class="space-y-4" novalidate>
          <!-- Error Banner -->
          <transition
            enter-active-class="transition duration-200 ease-out"
            enter-from-class="-translate-y-2 opacity-0"
            enter-to-class="translate-y-0 opacity-100"
          >
            <div
              v-if="errorMessage"
              role="alert"
              class="p-3.5 rounded-2xl bg-rose-50 border-2 border-rose-300 text-rose-800 text-xs sm:text-sm font-semibold flex items-start gap-2.5"
            >
              <span class="text-lg leading-none" aria-hidden="true">⚠️</span>
              <div class="flex-1">
                <span>{{ errorMessage }}</span>
              </div>
            </div>
          </transition>

          <!-- Email Input -->
          <div>
            <label for="email" class="block text-xs sm:text-sm font-bold text-slate-700 mb-1">
              Account Email
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
                :class="error ? 'border-rose-400 bg-rose-50/50' : 'border-slate-300 focus:border-indigo-500'"
              />
            </div>
            <p v-if="error" class="text-xs text-rose-600 mt-1 font-semibold pl-1">
              {{ error }}
            </p>
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            :disabled="isLoading"
            class="w-full mt-2 py-3 px-4 rounded-2xl font-extrabold text-sm sm:text-base text-white bg-indigo-600 hover:bg-indigo-700 active:scale-[0.98] transition shadow-md hover:shadow-lg disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2 border-b-4 border-indigo-800"
          >
            <span v-if="isLoading" class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" aria-hidden="true"></span>
            <span>{{ isLoading ? 'Sending Link...' : 'Send Reset Link 📬' }}</span>
          </button>

          <!-- Back to login link -->
          <div class="text-center pt-2">
            <NuxtLink
              to="/login"
              class="text-xs text-slate-600 hover:text-indigo-600 font-bold transition hover:underline"
            >
              ← Back to Sign In
            </NuxtLink>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '~/stores/auth'

const authStore = useAuthStore()

const email = ref('')
const isLoading = ref(false)
const isSuccess = ref(false)
const error = ref('')
const errorMessage = ref('')

async function handleReset() {
  error.value = ''
  errorMessage.value = ''

  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!email.value.trim()) {
    error.value = 'Please enter your email.'
    return
  }
  if (!emailPattern.test(email.value.trim())) {
    error.value = 'Please enter a valid email address.'
    return
  }

  isLoading.value = true
  try {
    await authStore.resetPassword(email.value)
    isSuccess.value = true
  } catch (err: any) {
    errorMessage.value = err.message || 'Unable to send reset email. Please verify the address.'
  } finally {
    isLoading.value = false
  }
}
</script>
