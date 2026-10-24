<template>
  <div class="max-w-4xl mx-auto space-y-6 sm:space-y-8 animate-pop">
    <!-- Header Hero Banner -->
    <div class="bg-white rounded-3xl border-2 border-slate-200 shadow-sm p-6 sm:p-8 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6">
      <div class="flex items-center gap-4 sm:gap-5">
        <div class="w-16 h-16 sm:w-20 sm:h-20 rounded-3xl bg-indigo-100 border-2 border-indigo-200 flex items-center justify-center text-3xl sm:text-4xl shadow-inner shrink-0">
          {{ authStore.isGuest ? '🎒' : '🧙‍♂️' }}
        </div>
        <div>
          <div class="flex items-center gap-2 flex-wrap">
            <h1 class="text-2xl sm:text-3xl font-extrabold text-slate-900">
              Adventurer Profile
            </h1>
            <span
              class="px-2.5 py-0.5 rounded-full text-xs font-extrabold"
              :class="authStore.isGuest ? 'bg-amber-100 text-amber-800' : 'bg-emerald-100 text-emerald-800'"
            >
              {{ authStore.isGuest ? 'Guest Mode' : 'Explorer Account' }}
            </span>
          </div>
          <p class="text-xs sm:text-sm text-slate-600 mt-1">
            Manage your display name, curriculum standard, accessibility settings, and data.
          </p>
        </div>
      </div>

      <!-- Quick Action Navigation -->
      <NuxtLink
        to="/dashboard"
        class="px-4 py-2.5 rounded-2xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs sm:text-sm transition border border-slate-300 self-end sm:self-auto"
      >
        ← Back to Dashboard
      </NuxtLink>
    </div>

    <!-- Success Feedback Notification -->
    <transition
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="-translate-y-2 opacity-0"
      enter-to-class="translate-y-0 opacity-100"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="translate-y-0 opacity-100"
      leave-to-class="-translate-y-2 opacity-0"
    >
      <div
        v-if="saveSuccessMessage"
        class="bg-emerald-50 border-2 border-emerald-300 text-emerald-900 px-5 py-3.5 rounded-2xl flex items-center justify-between gap-3 shadow-sm"
        role="status"
      >
        <div class="flex items-center gap-2.5 font-bold text-sm">
          <span>✨</span>
          <span>{{ saveSuccessMessage }}</span>
        </div>
        <button
          type="button"
          @click="saveSuccessMessage = null"
          class="text-emerald-700 hover:text-emerald-900 text-xs font-bold"
        >
          ✕
        </button>
      </div>
    </transition>

    <!-- Section 1: Edit Profile & Curriculum Form -->
    <div class="bg-white rounded-3xl border-2 border-slate-200 shadow-sm p-6 sm:p-8">
      <div class="flex items-center gap-2.5 mb-6">
        <span class="text-2xl" aria-hidden="true">🏷️</span>
        <div>
          <h2 class="text-xl font-black text-slate-900">
            Player & Curriculum Preferences
          </h2>
          <p class="text-xs sm:text-sm text-slate-500 font-medium">
            Customize your display name, grade level, and school curriculum standard
          </p>
        </div>
      </div>

      <form @submit.prevent="handleSaveProfile" class="space-y-6">
        <!-- Display Name -->
        <div>
          <label for="displayName" class="block text-sm font-extrabold text-slate-800 mb-1">
            Display Name
          </label>
          <p class="text-xs text-slate-500 mb-2">
            The adventurer nickname shown on high score tables and earned badges.
          </p>
          <input
            id="displayName"
            v-model="formDisplayName"
            type="text"
            required
            maxlength="30"
            placeholder="e.g. Math Wizard Alex"
            class="w-full px-4 py-3 rounded-2xl border-2 border-slate-300 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100 transition text-sm sm:text-base font-semibold text-slate-800"
          />
        </div>

        <!-- Grade Selection -->
        <div>
          <label class="block text-sm font-extrabold text-slate-800 mb-1">
            Grade Level
          </label>
          <p class="text-xs text-slate-500 mb-2">
            Sets the default difficulty and topic curriculum aligned with your school year.
          </p>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
            <button
              type="button"
              @click="formGrade = 5"
              class="p-4 rounded-2xl border-2 text-left transition flex items-center justify-between"
              :class="formGrade === 5 ? 'border-indigo-600 bg-indigo-50/70 shadow-sm ring-4 ring-indigo-100' : 'border-slate-200 hover:border-slate-300 bg-slate-50'"
            >
              <div class="flex items-center gap-3">
                <span class="text-3xl" aria-hidden="true">🌱</span>
                <div>
                  <h3 class="font-extrabold text-base text-slate-900">Grade 5</h3>
                  <p class="text-xs text-slate-600">Unlike fractions, decimals to thousandths, 2D shapes</p>
                </div>
              </div>
              <span
                v-if="formGrade === 5"
                class="w-6 h-6 rounded-full bg-indigo-600 text-white text-xs flex items-center justify-center font-bold shrink-0"
              >
                ✓
              </span>
            </button>

            <button
              type="button"
              @click="formGrade = 6"
              class="p-4 rounded-2xl border-2 text-left transition flex items-center justify-between"
              :class="formGrade === 6 ? 'border-indigo-600 bg-indigo-50/70 shadow-sm ring-4 ring-indigo-100' : 'border-slate-200 hover:border-slate-300 bg-slate-50'"
            >
              <div class="flex items-center gap-3">
                <span class="text-3xl" aria-hidden="true">🚀</span>
                <div>
                  <h3 class="font-extrabold text-base text-slate-900">Grade 6</h3>
                  <p class="text-xs text-slate-600">Fraction division, unit rates, percentages, surface area</p>
                </div>
              </div>
              <span
                v-if="formGrade === 6"
                class="w-6 h-6 rounded-full bg-indigo-600 text-white text-xs flex items-center justify-center font-bold shrink-0"
              >
                ✓
              </span>
            </button>
          </div>
        </div>

        <!-- Curriculum Board Selection -->
        <div>
          <label class="block text-sm font-extrabold text-slate-800 mb-1">
            Curriculum Educational Board
          </label>
          <p class="text-xs text-slate-500 mb-2">
            Standards alignment for question scenarios, terminology, and domain benchmarks.
          </p>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
            <button
              type="button"
              @click="formBoard = 'georgia'"
              class="p-4 rounded-2xl border-2 text-left transition flex items-center justify-between"
              :class="formBoard === 'georgia' ? 'border-amber-500 bg-amber-50/70 shadow-sm ring-4 ring-amber-100' : 'border-slate-200 hover:border-slate-300 bg-slate-50'"
            >
              <div class="flex items-center gap-3">
                <span class="text-3xl" aria-hidden="true">🍑</span>
                <div>
                  <h3 class="font-extrabold text-base text-slate-900">Georgia Standards (MGSE)</h3>
                  <p class="text-xs text-slate-600">State of Georgia GSE benchmarks (Grades 5 & 6)</p>
                </div>
              </div>
              <span
                v-if="formBoard === 'georgia'"
                class="w-6 h-6 rounded-full bg-amber-600 text-white text-xs flex items-center justify-center font-bold shrink-0"
              >
                ✓
              </span>
            </button>

            <button
              type="button"
              @click="formBoard = 'cbse'"
              class="p-4 rounded-2xl border-2 text-left transition flex items-center justify-between"
              :class="formBoard === 'cbse' ? 'border-emerald-500 bg-emerald-50/70 shadow-sm ring-4 ring-emerald-100' : 'border-slate-200 hover:border-slate-300 bg-slate-50'"
            >
              <div class="flex items-center gap-3">
                <span class="text-3xl" aria-hidden="true">🇮🇳</span>
                <div>
                  <h3 class="font-extrabold text-base text-slate-900">CBSE Class 6 (NCERT)</h3>
                  <p class="text-xs text-slate-600">Ganita Prakash (Factors, Integers, Ratios)</p>
                </div>
              </div>
              <span
                v-if="formBoard === 'cbse'"
                class="w-6 h-6 rounded-full bg-emerald-600 text-white text-xs flex items-center justify-center font-bold shrink-0"
              >
                ✓
              </span>
            </button>
          </div>
        </div>

        <div class="pt-2">
          <button
            type="submit"
            :disabled="isSavingProfile"
            class="px-6 py-3 rounded-2xl font-extrabold text-sm sm:text-base text-white bg-indigo-600 hover:bg-indigo-700 active:scale-95 transition shadow-md hover:shadow-lg disabled:opacity-60 flex items-center gap-2 border-b-4 border-indigo-800 cursor-pointer"
          >
            <span v-if="isSavingProfile" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
            <span>{{ isSavingProfile ? 'Saving Changes...' : 'Save Preferences ✨' }}</span>
          </button>
        </div>
      </form>
    </div>

    <!-- Section 2: Accessibility Preferences -->
    <div class="bg-white rounded-3xl border-2 border-slate-200 shadow-sm p-6 sm:p-8">
      <div class="flex items-center gap-2.5 mb-6">
        <span class="text-2xl" aria-hidden="true">♿</span>
        <div>
          <h2 class="text-xl font-black text-slate-900">
            Accessibility & Sensory Toggles
          </h2>
          <p class="text-xs sm:text-sm text-slate-500 font-medium">
            Customize readability, speech synthesis, and animations to fit your learning needs
          </p>
        </div>
      </div>

      <div class="space-y-4">
        <!-- 1. Dyslexia-Friendly Font Toggle -->
        <div class="p-4 sm:p-5 rounded-2xl border-2 border-slate-200 bg-slate-50/70 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div class="space-y-0.5">
            <div class="flex items-center gap-2">
              <span class="font-extrabold text-sm sm:text-base text-slate-900">
                Dyslexia-Friendly Font (Lexend)
              </span>
              <span class="text-xs bg-indigo-100 text-indigo-800 font-bold px-2 py-0.5 rounded">
                Readability
              </span>
            </div>
            <p class="text-xs text-slate-600 max-w-xl">
              Switches all typography to Lexend with generous character spacing, larger apertures, and increased line height for reduced visual crowding.
            </p>
          </div>

          <button
            type="button"
            role="switch"
            :aria-checked="isDyslexic"
            @click="toggleDyslexia"
            class="px-4 py-2 rounded-2xl font-black text-xs sm:text-sm border-2 transition flex items-center gap-2 shrink-0 cursor-pointer"
            :class="isDyslexic ? 'bg-indigo-600 text-white border-indigo-700 shadow-sm' : 'bg-white text-slate-700 border-slate-300 hover:bg-slate-100'"
          >
            <span>{{ isDyslexic ? 'Enabled ✓' : 'Disabled' }}</span>
          </button>
        </div>

        <!-- 2. Read-Aloud (Text-to-Speech) Toggle -->
        <div class="p-4 sm:p-5 rounded-2xl border-2 border-slate-200 bg-slate-50/70 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div class="space-y-0.5">
            <div class="flex items-center gap-2">
              <span class="font-extrabold text-sm sm:text-base text-slate-900">
                Read-Aloud Voice (Text-to-Speech)
              </span>
              <span class="text-xs bg-amber-100 text-amber-800 font-bold px-2 py-0.5 rounded">
                Auditory
              </span>
            </div>
            <p class="text-xs text-slate-600 max-w-xl">
              Enables speech synthesis playback for questions, answer choices, and diagnostic explanations.
            </p>
          </div>

          <div class="flex items-center gap-2 shrink-0">
            <button
              type="button"
              @click="testVoiceSpeech"
              class="px-3 py-2 rounded-2xl bg-white hover:bg-slate-100 text-slate-700 font-bold text-xs border border-slate-300 transition"
              title="Test the speech synthesis voice"
            >
              🔊 Test Voice
            </button>
            <button
              type="button"
              role="switch"
              :aria-checked="isReadAloud"
              @click="toggleReadAloud"
              class="px-4 py-2 rounded-2xl font-black text-xs sm:text-sm border-2 transition flex items-center gap-2 cursor-pointer"
              :class="isReadAloud ? 'bg-indigo-600 text-white border-indigo-700 shadow-sm' : 'bg-white text-slate-700 border-slate-300 hover:bg-slate-100'"
            >
              <span>{{ isReadAloud ? 'Enabled ✓' : 'Disabled' }}</span>
            </button>
          </div>
        </div>

        <!-- 3. Reduced Motion Toggle -->
        <div class="p-4 sm:p-5 rounded-2xl border-2 border-slate-200 bg-slate-50/70 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div class="space-y-0.5">
            <div class="flex items-center gap-2">
              <span class="font-extrabold text-sm sm:text-base text-slate-900">
                Reduced Motion Mode
              </span>
              <span class="text-xs bg-purple-100 text-purple-800 font-bold px-2 py-0.5 rounded">
                Vestibular
              </span>
            </div>
            <p class="text-xs text-slate-600 max-w-xl">
              Disables confetti bursts, floating background animations, and bounce transitions across the entire platform.
            </p>
          </div>

          <button
            type="button"
            role="switch"
            :aria-checked="isReducedMotion"
            @click="toggleReducedMotion"
            class="px-4 py-2 rounded-2xl font-black text-xs sm:text-sm border-2 transition flex items-center gap-2 shrink-0 cursor-pointer"
            :class="isReducedMotion ? 'bg-indigo-600 text-white border-indigo-700 shadow-sm' : 'bg-white text-slate-700 border-slate-300 hover:bg-slate-100'"
          >
            <span>{{ isReducedMotion ? 'Enabled ✓' : 'Disabled' }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Section 3: Data Management & Reset Progress -->
    <div class="bg-white rounded-3xl border-2 border-rose-200 shadow-sm p-6 sm:p-8">
      <div class="flex items-center gap-2.5 mb-4">
        <span class="text-2xl" aria-hidden="true">⚠️</span>
        <div>
          <h2 class="text-xl font-black text-rose-950">
            Danger Zone & Data Reset
          </h2>
          <p class="text-xs sm:text-sm text-slate-500 font-medium">
            Resetting your progress is permanent and cannot be undone
          </p>
        </div>
      </div>

      <div class="p-4 rounded-2xl bg-rose-50/70 border border-rose-200 mb-5">
        <p class="text-xs sm:text-sm text-rose-900 font-bold leading-relaxed">
          Resetting will set your Total XP to 0, clear your answer streaks, reset topic mastery to 50%, remove earned badges, and clear your session log.
        </p>
      </div>

      <button
        type="button"
        @click="showResetModal = true"
        class="px-5 py-2.5 rounded-2xl font-extrabold text-xs sm:text-sm text-rose-700 hover:text-white bg-rose-50 hover:bg-rose-600 border-2 border-rose-300 hover:border-rose-700 active:scale-95 transition shadow-sm cursor-pointer"
      >
        Reset My Progress ⚠️
      </button>
    </div>

    <!-- Section 4: Account Session & Sign Out -->
    <div class="bg-white rounded-3xl border-2 border-slate-200 shadow-sm p-6 sm:p-8 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
      <div>
        <h2 class="text-lg font-black text-slate-900">
          Account Session
        </h2>
        <p class="text-xs sm:text-sm text-slate-500">
          <span v-if="authStore.isGuest">Currently exploring as a Guest Adventurer.</span>
          <span v-else>Signed in as <strong class="text-slate-700">{{ authStore.user?.email }}</strong></span>
        </p>
      </div>

      <div class="flex items-center gap-3">
        <NuxtLink
          v-if="authStore.isGuest"
          to="/signup"
          class="px-5 py-2.5 rounded-2xl bg-indigo-600 hover:bg-indigo-700 text-white font-extrabold text-xs sm:text-sm transition shadow"
        >
          Create Permanent Account ✨
        </NuxtLink>

        <button
          type="button"
          @click="handleSignOut"
          class="px-5 py-2.5 rounded-2xl bg-slate-100 hover:bg-rose-50 text-slate-700 hover:text-rose-700 border border-slate-300 hover:border-rose-300 font-extrabold text-xs sm:text-sm transition cursor-pointer"
        >
          {{ authStore.isGuest ? 'Exit Guest Mode' : 'Sign Out' }}
        </button>
      </div>
    </div>

    <!-- Interactive Reset Progress Confirmation Modal -->
    <transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0 scale-95"
      enter-to-class="opacity-100 scale-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100 scale-100"
      leave-to-class="opacity-0 scale-95"
    >
      <div
        v-if="showResetModal"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm"
        role="dialog"
        aria-modal="true"
        aria-labelledby="reset-modal-title"
      >
        <div class="bg-white rounded-3xl border-2 border-rose-300 shadow-2xl max-w-md w-full p-6 sm:p-8 space-y-4">
          <div class="w-14 h-14 rounded-2xl bg-rose-100 text-rose-700 flex items-center justify-center text-3xl mx-auto shadow-inner">
            ⚠️
          </div>

          <div class="text-center space-y-2">
            <h3 id="reset-modal-title" class="text-xl font-black text-slate-900">
              Reset All Adventure Progress?
            </h3>
            <p class="text-xs sm:text-sm text-slate-600 leading-relaxed font-medium">
              Are you sure you want to reset everything? Your XP score will return to 0, streaks will clear, and all badges will be locked again.
            </p>
          </div>

          <div class="flex items-center gap-3 pt-3">
            <button
              type="button"
              @click="showResetModal = false"
              class="flex-1 py-3 px-4 rounded-2xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-extrabold text-xs sm:text-sm transition border border-slate-300 cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="button"
              @click="confirmResetProgress"
              :disabled="isResetting"
              class="flex-1 py-3 px-4 rounded-2xl bg-rose-600 hover:bg-rose-700 text-white font-extrabold text-xs sm:text-sm transition shadow border-b-4 border-rose-800 disabled:opacity-50 flex items-center justify-center gap-2 cursor-pointer"
            >
              <span v-if="isResetting" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
              <span>{{ isResetting ? 'Resetting...' : 'Yes, Reset' }}</span>
            </button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '~/stores/auth'
import { useSessionStore } from '~/stores/session'
import { useAccessibility } from '~/composables/useAccessibility'
import { useSupabase } from '~/composables/useSupabase'

const router = useRouter()
const authStore = useAuthStore()
const sessionStore = useSessionStore()
const supabase = useSupabase()

const {
  isDyslexic,
  isReadAloud,
  isReducedMotion,
  toggleDyslexia,
  toggleReadAloud,
  toggleReducedMotion,
  speak,
} = useAccessibility()

const formDisplayName = ref('')
const formGrade = ref<5 | 6>(5)
const formBoard = ref<'georgia' | 'cbse'>('georgia')

const isSavingProfile = ref(false)
const saveSuccessMessage = ref<string | null>(null)
const showResetModal = ref(false)
const isResetting = ref(false)

onMounted(() => {
  sessionStore.loadFromStorage()
  formDisplayName.value = authStore.displayName !== 'Math Adventurer' && authStore.displayName !== 'Student'
    ? authStore.displayName
    : (authStore.user?.email ? authStore.user.email.split('@')[0] : 'Math Hero')
  formGrade.value = (sessionStore.grade === 6 || authStore.userGrade === 6) ? 6 : 5
  formBoard.value = (sessionStore.board === 'cbse' || authStore.userBoard === 'cbse') ? 'cbse' : 'georgia'
})

async function handleSaveProfile() {
  isSavingProfile.value = true
  saveSuccessMessage.value = null

  try {
    const trimmed = formDisplayName.value.trim() || 'Math Hero'
    await authStore.saveSetupProfile({
      displayName: trimmed,
      grade: formGrade.value,
      board: formBoard.value,
    })

    sessionStore.setGrade(formGrade.value)
    sessionStore.setBoard(formBoard.value)

    saveSuccessMessage.value = 'Preferences saved successfully! Your adventure settings are updated.'
    setTimeout(() => {
      saveSuccessMessage.value = null
    }, 5000)
  } catch (err: any) {
    console.error('Failed to update profile preferences:', err)
  } finally {
    isSavingProfile.value = false
  }
}

function testVoiceSpeech() {
  speak('MathQuest read-aloud voice is active! Ready for fractions, decimals, and geometry.')
}

async function confirmResetProgress() {
  isResetting.value = true
  try {
    // 1. Reset local store
    sessionStore.resetAllProgress()
    sessionStore.recentActivities = []
    sessionStore.saveToStorage()

    // 2. Clear any pending sync keys
    if (import.meta.client) {
      localStorage.removeItem('mathquest_pending_cloud_sync_v1')
      localStorage.removeItem('mathquest_guest_backup_before_auth')
    }

    // 3. If authenticated user, clear user rows in Supabase
    if (authStore.user && supabase) {
      const uid = authStore.user.id
      await supabase.from('answers').delete().eq('user_id', uid)
      await supabase.from('sessions').delete().eq('user_id', uid)
      await supabase.from('badges').delete().eq('user_id', uid)
      await supabase.from('mastery').delete().eq('user_id', uid)
      await supabase.from('profiles').update({ total_score: 0, updated_at: new Date().toISOString() }).eq('id', uid)
    }

    showResetModal.value = false
    saveSuccessMessage.value = 'Your progress has been completely reset to zero.'
  } catch (err) {
    console.error('Failed to reset progress:', err)
  } finally {
    isResetting.value = false
  }
}

async function handleSignOut() {
  await authStore.signOut()
}
</script>
