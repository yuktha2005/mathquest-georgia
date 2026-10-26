<template>
  <div class="min-h-[85vh] flex items-center justify-center py-6 px-4">
    <div class="w-full max-w-xl">
      <!-- Header -->
      <div class="text-center mb-6">
        <div class="inline-flex items-center justify-center w-16 h-16 rounded-3xl bg-indigo-100 text-3xl mb-3 shadow-inner animate-pop">
          🌟
        </div>
        <h1 class="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
          Welcome to <span class="text-indigo-600">MathQuest</span>!
        </h1>
        <p class="text-slate-600 text-sm sm:text-base mt-1">
          Let's customize your math adventure so challenges match your grade and school curriculum.
        </p>
      </div>

      <!-- Setup Card -->
      <div class="bg-white rounded-3xl border-2 border-slate-200 shadow-xl p-6 sm:p-8">
        <!-- Error / Warning Banner -->
        <transition
          enter-active-class="transition duration-200 ease-out"
          enter-from-class="-translate-y-2 opacity-0"
          enter-to-class="translate-y-0 opacity-100"
        >
          <div
            v-if="errorMessage"
            role="alert"
            class="mb-5 p-3.5 rounded-2xl bg-amber-50 border-2 border-amber-300 text-amber-900 text-xs sm:text-sm font-semibold flex items-start gap-2.5"
          >
            <span class="text-lg leading-none" aria-hidden="true">⚠️</span>
            <div class="flex-1">
              <span>{{ errorMessage }}</span>
            </div>
          </div>
        </transition>

        <form @submit.prevent="handleFinishSetup" class="space-y-6">
          <!-- Step 1: Display Name -->
          <div>
            <label for="displayName" class="block text-sm font-extrabold text-slate-800 mb-1">
              1. What should we call you? 🏷️
            </label>
            <p class="text-xs text-slate-500 mb-2">
              Your adventurer nickname displayed on badges and high scores.
            </p>
            <input
              id="displayName"
              v-model="displayName"
              type="text"
              required
              maxlength="30"
              placeholder="e.g. Math Wizard Alex"
              class="w-full px-4 py-3 rounded-2xl border-2 border-slate-300 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100 transition text-sm sm:text-base font-semibold text-slate-800"
            />
          </div>

          <!-- Step 2: Grade Level -->
          <div>
            <label class="block text-sm font-extrabold text-slate-800 mb-1">
              2. Choose your Grade Level 🎒
            </label>
            <p class="text-xs text-slate-500 mb-2">
              You can always switch between grades anytime from the header.
            </p>
            <div class="grid grid-cols-2 gap-3 sm:gap-4">
              <!-- Grade 5 Card -->
              <button
                type="button"
                @click="selectedGrade = 5"
                class="p-4 rounded-2xl border-2 text-left transition flex flex-col justify-between"
                :class="selectedGrade === 5 ? 'border-indigo-600 bg-indigo-50/70 shadow-sm ring-4 ring-indigo-200' : 'border-slate-200 hover:border-slate-300 bg-slate-50'"
              >
                <div class="flex items-center justify-between mb-2">
                  <span class="text-2xl" aria-hidden="true">🌱</span>
                  <span
                    v-if="selectedGrade === 5"
                    class="w-5 h-5 rounded-full bg-indigo-600 text-white text-xs flex items-center justify-center font-bold"
                  >
                    ✓
                  </span>
                </div>
                <div>
                  <h3 class="font-extrabold text-base text-slate-900">Grade 5</h3>
                  <p class="text-xs text-slate-600 mt-0.5">Unlike fractions, decimals, coordinate graphs, 2D shapes</p>
                </div>
              </button>

              <!-- Grade 6 Card -->
              <button
                type="button"
                @click="selectedGrade = 6"
                class="p-4 rounded-2xl border-2 text-left transition flex flex-col justify-between"
                :class="selectedGrade === 6 ? 'border-indigo-600 bg-indigo-50/70 shadow-sm ring-4 ring-indigo-200' : 'border-slate-200 hover:border-slate-300 bg-slate-50'"
              >
                <div class="flex items-center justify-between mb-2">
                  <span class="text-2xl" aria-hidden="true">🚀</span>
                  <span
                    v-if="selectedGrade === 6"
                    class="w-5 h-5 rounded-full bg-indigo-600 text-white text-xs flex items-center justify-center font-bold"
                  >
                    ✓
                  </span>
                </div>
                <div>
                  <h3 class="font-extrabold text-base text-slate-900">Grade 6</h3>
                  <p class="text-xs text-slate-600 mt-0.5">Fraction division, unit rates, percentages, surface area</p>
                </div>
              </button>
            </div>
          </div>

          <!-- Step 3: Curriculum Board -->
          <div>
            <label class="block text-sm font-extrabold text-slate-800 mb-1">
              3. Curriculum Standard 🗺️
            </label>
            <p class="text-xs text-slate-500 mb-2">
              Select your school's educational board for aligned question benchmarks.
            </p>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
              <!-- Georgia Standards of Excellence -->
              <button
                type="button"
                @click="selectedBoard = 'georgia'"
                class="p-4 rounded-2xl border-2 text-left transition flex flex-col justify-between"
                :class="selectedBoard === 'georgia' ? 'border-amber-500 bg-amber-50/70 shadow-sm ring-4 ring-amber-200' : 'border-slate-200 hover:border-slate-300 bg-slate-50'"
              >
                <div class="flex items-center justify-between mb-2">
                  <span class="text-2xl" aria-hidden="true">🍑</span>
                  <span
                    v-if="selectedBoard === 'georgia'"
                    class="w-5 h-5 rounded-full bg-amber-600 text-white text-xs flex items-center justify-center font-bold"
                  >
                    ✓
                  </span>
                </div>
                <div>
                  <h3 class="font-extrabold text-base text-slate-900">Georgia Standards (GSE)</h3>
                  <p class="text-xs text-slate-600 mt-0.5">State of Georgia curriculum (MGSE5 & MGSE6)</p>
                </div>
              </button>

              <!-- CBSE India (NCERT) -->
              <button
                type="button"
                @click="selectedBoard = 'cbse'"
                class="p-4 rounded-2xl border-2 text-left transition flex flex-col justify-between"
                :class="selectedBoard === 'cbse' ? 'border-emerald-500 bg-emerald-50/70 shadow-sm ring-4 ring-emerald-200' : 'border-slate-200 hover:border-slate-300 bg-slate-50'"
              >
                <div class="flex items-center justify-between mb-2">
                  <span class="text-2xl" aria-hidden="true">🇮🇳</span>
                  <span
                    v-if="selectedBoard === 'cbse'"
                    class="w-5 h-5 rounded-full bg-emerald-600 text-white text-xs flex items-center justify-center font-bold"
                  >
                    ✓
                  </span>
                </div>
                <div>
                  <h3 class="font-extrabold text-base text-slate-900">CBSE Class 6 (NCERT)</h3>
                  <p class="text-xs text-slate-600 mt-0.5">Ganita Prakash (Factors, Integers, Ratios)</p>
                </div>
              </button>
            </div>
          </div>

          <!-- Submit Button -->
          <div class="pt-2">
            <button
              type="submit"
              :disabled="isLoading"
              class="w-full py-3.5 px-6 rounded-2xl font-extrabold text-base text-white bg-indigo-600 hover:bg-indigo-700 active:scale-[0.98] transition shadow-lg hover:shadow-xl disabled:opacity-60 flex items-center justify-center gap-2 border-b-4 border-indigo-800"
            >
              <span v-if="isLoading" class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" aria-hidden="true"></span>
              <span>{{ isLoading ? 'Saving Profile...' : 'Launch My Adventure! 🚀' }}</span>
            </button>
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

const displayName = ref(authStore.displayName !== 'Math Adventurer' && authStore.displayName !== 'Student' ? authStore.displayName : '')
const selectedGrade = ref<5 | 6>(authStore.userGrade || 5)
const selectedBoard = ref<'georgia' | 'cbse'>((authStore.userBoard as 'georgia' | 'cbse') || 'georgia')
const isLoading = ref(false)
const errorMessage = ref('')

async function handleFinishSetup() {
  isLoading.value = true
  errorMessage.value = ''

  try {
    await authStore.saveSetupProfile({
      displayName: displayName.value.trim() || 'Math Hero',
      grade: selectedGrade.value,
      board: selectedBoard.value,
    })
  } catch (err: any) {
    console.error('Failed to save profile setup:', err)
    errorMessage.value = err?.message || 'Notice saving remote profile; proceeding with local setup.'
  } finally {
    isLoading.value = false
    // Always navigate to /dashboard so student is never stuck on onboarding
    await navigateTo('/dashboard')
  }
}
</script>
