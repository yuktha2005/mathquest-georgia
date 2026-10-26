<template>
  <div class="space-y-8 animate-pop">
    <!-- Hero Banner (Warm neutral / rich primary, no purple-to-pink gradient) -->
    <div class="bg-primary-900 rounded-3xl p-6 sm:p-10 text-white shadow-warm-lg border-2 border-primary-950 relative overflow-hidden">
      <div class="absolute -right-6 -bottom-8 opacity-10 text-9xl select-none pointer-events-none">
        📐
      </div>
      <div class="max-w-2xl relative z-10 space-y-4">
        <div class="inline-flex items-center gap-2 bg-white/10 border border-white/20 backdrop-blur-md px-3.5 py-1.5 rounded-full text-xs sm:text-sm font-bold uppercase tracking-wider text-accent-300">
          <span>{{ sessionStore.board === 'cbse' ? '🇮🇳' : '🇬🇪' }}</span>
          <span>{{ sessionStore.boardTitle }}</span>
        </div>
        <h1 class="text-3xl sm:text-5xl font-extrabold tracking-tight text-white">
          Master Math with Confidence
        </h1>
        <p class="text-warm-100 text-base sm:text-lg leading-relaxed">
          Curriculum-aligned math for Grades 5 & 6. Solve engaging adaptive quests with instant mathematical verification, step-by-step clues, and diagnostic feedback.
        </p>
        <div class="pt-2 flex flex-wrap items-center gap-3">
          <a
            href="#topics-grid"
            class="px-6 py-3.5 rounded-2xl bg-accent-500 hover:bg-accent-600 active:scale-95 text-warm-900 font-extrabold text-sm sm:text-base transition shadow-game-amber inline-flex items-center gap-2 border-b-2 border-accent-700 min-h-[44px]"
          >
            <span>⚔️</span>
            <span>Start Math Adventure</span>
          </a>
          <NuxtLink
            to="/dashboard"
            class="px-5 py-3.5 rounded-2xl bg-white/10 hover:bg-white/20 active:scale-95 text-white font-extrabold text-sm sm:text-base border border-white/25 transition inline-flex items-center gap-2 min-h-[44px]"
          >
            <span>🏠</span>
            <span>Student Dashboard</span>
          </NuxtLink>
        </div>
      </div>
    </div>

    <!-- Curriculum Board Selection -->
    <div class="space-y-3">
      <h2 class="text-lg font-bold text-warm-900 flex items-center gap-2">
        <span aria-hidden="true">🏛️</span>
        <span>Select Curriculum Board</span>
      </h2>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4" role="tablist" aria-label="Curriculum board selection">
        <!-- Georgia Standards of Excellence -->
        <button
          type="button"
          role="tab"
          :aria-selected="sessionStore.board === 'georgia'"
          aria-label="Georgia Standards of Excellence (MGSE), Grades 5 & 6"
          @click="selectBoard('georgia')"
          :class="[
            'p-5 rounded-3xl border-4 text-left transition-all duration-200 cursor-pointer flex items-center justify-between focus:outline-none focus-visible:ring-4 focus-visible:ring-primary-400 focus-visible:ring-offset-2 min-h-[44px]',
            sessionStore.board === 'georgia'
              ? 'bg-primary-50 border-primary-600 shadow-game-blue translate-y-0'
              : 'bg-white border-warm-200 hover:border-warm-300 shadow-sm opacity-90 hover:opacity-100'
          ]"
        >
          <div class="space-y-1">
            <div class="flex items-center gap-2">
              <span class="text-2xl" aria-hidden="true">🇬🇪</span>
              <span class="text-xl font-black text-warm-900">Georgia GSE (MGSE)</span>
              <span
                v-if="sessionStore.board === 'georgia'"
                class="bg-primary-700 text-white text-xs px-2.5 py-0.5 rounded-full font-bold ml-1"
              >
                Active
              </span>
            </div>
            <p class="text-xs sm:text-sm text-warm-700">
              Primary Assessment Curriculum for Grades 5 and 6 (NF, NBT, RP, G, MD).
            </p>
          </div>
          <span class="text-2xl text-primary-700 font-bold ml-2" aria-hidden="true">➜</span>
        </button>

        <!-- CBSE NCERT Ganita Prakash -->
        <button
          type="button"
          role="tab"
          :aria-selected="sessionStore.board === 'cbse'"
          aria-label="CBSE Class 6 NCERT Ganita Prakash"
          @click="selectBoard('cbse')"
          :class="[
            'p-5 rounded-3xl border-4 text-left transition-all duration-200 cursor-pointer flex items-center justify-between focus:outline-none focus-visible:ring-4 focus-visible:ring-primary-400 focus-visible:ring-offset-2 min-h-[44px]',
            sessionStore.board === 'cbse'
              ? 'bg-primary-50 border-primary-600 shadow-game-blue translate-y-0'
              : 'bg-white border-warm-200 hover:border-warm-300 shadow-sm opacity-90 hover:opacity-100'
          ]"
        >
          <div class="space-y-1">
            <div class="flex items-center gap-2">
              <span class="text-2xl" aria-hidden="true">🇮🇳</span>
              <span class="text-xl font-black text-warm-900">CBSE Class 6 (NCERT)</span>
              <span
                v-if="sessionStore.board === 'cbse'"
                class="bg-primary-700 text-white text-xs px-2.5 py-0.5 rounded-full font-bold ml-1"
              >
                Active
              </span>
            </div>
            <p class="text-xs sm:text-sm text-warm-700">
              NCERT Ganita Prakash Class 6: Factors, Integers, Fractions, Decimals, Ratios.
            </p>
          </div>
          <span class="text-2xl text-primary-700 font-bold ml-2" aria-hidden="true">➜</span>
        </button>
      </div>
    </div>

    <!-- Grade Selection Tabs -->
    <div class="space-y-3">
      <h2 class="text-lg font-bold text-warm-900 flex items-center gap-2">
        <span aria-hidden="true">🎒</span>
        <span>Select Your Grade Level</span>
      </h2>
      <div
        :class="[
          'grid gap-4',
          sessionStore.board === 'cbse' ? 'grid-cols-1' : 'grid-cols-1 sm:grid-cols-2'
        ]"
        role="tablist"
        aria-label="Grade level selection"
      >
        <!-- Grade 5 Tab (Only for Georgia) -->
        <button
          v-if="sessionStore.board === 'georgia'"
          type="button"
          role="tab"
          :aria-selected="sessionStore.grade === 5"
          aria-label="Grade 5 Quest: Unlike denominators, decimal place values, line plots, and 2D area"
          @click="selectGrade(5)"
          :class="[
            'p-5 rounded-3xl border-4 text-left transition-all duration-200 cursor-pointer flex items-center justify-between focus:outline-none focus-visible:ring-4 focus-visible:ring-primary-400 focus-visible:ring-offset-2 min-h-[44px]',
            sessionStore.grade === 5
              ? 'bg-primary-50 border-primary-600 shadow-game-blue translate-y-0'
              : 'bg-white border-warm-200 hover:border-warm-300 shadow-sm opacity-90 hover:opacity-100'
          ]"
        >
          <div class="space-y-1">
            <div class="flex items-center gap-2">
              <span class="text-2xl" aria-hidden="true">🌱</span>
              <span class="text-2xl font-black text-warm-900">Grade 5 Quest</span>
              <span
                v-if="sessionStore.grade === 5"
                class="bg-primary-700 text-white text-xs px-2.5 py-0.5 rounded-full font-bold ml-1"
              >
                Active
              </span>
            </div>
            <p class="text-xs sm:text-sm text-warm-700">
              Unlike denominators, decimal place values, line plots, and 2D area.
            </p>
          </div>
          <span class="text-2xl text-primary-700 font-bold ml-2" aria-hidden="true">➜</span>
        </button>

        <!-- Grade 6 Tab -->
        <button
          type="button"
          role="tab"
          :aria-selected="sessionStore.grade === 6"
          :aria-label="sessionStore.board === 'cbse' ? 'CBSE Class 6 Quest (NCERT Ganita Prakash)' : 'Grade 6 Quest (MGSE)'"
          @click="selectGrade(6)"
          :class="[
            'p-5 rounded-3xl border-4 text-left transition-all duration-200 cursor-pointer flex items-center justify-between focus:outline-none focus-visible:ring-4 focus-visible:ring-primary-400 focus-visible:ring-offset-2 min-h-[44px]',
            sessionStore.grade === 6
              ? 'bg-primary-50 border-primary-600 shadow-game-blue translate-y-0'
              : 'bg-white border-warm-200 hover:border-warm-300 shadow-sm opacity-90 hover:opacity-100'
          ]"
        >
          <div class="space-y-1">
            <div class="flex items-center gap-2">
              <span class="text-2xl" aria-hidden="true">🚀</span>
              <span class="text-2xl font-black text-warm-900">
                {{ sessionStore.board === 'cbse' ? 'Class 6 Quest (NCERT Ganita Prakash)' : 'Grade 6 Quest' }}
              </span>
              <span
                v-if="sessionStore.grade === 6"
                class="bg-primary-700 text-white text-xs px-2.5 py-0.5 rounded-full font-bold ml-1"
              >
                Active
              </span>
            </div>
            <p class="text-xs sm:text-sm text-warm-700">
              {{ sessionStore.board === 'cbse'
                ? 'Prime factorization, LCM/HCF, negative integers, rational fractions, decimals, and geometry.'
                : 'Ratios, unit rates, fraction division, integers, and surface area.' }}
            </p>
          </div>
          <span class="text-2xl text-primary-700 font-bold ml-2" aria-hidden="true">➜</span>
        </button>
      </div>
    </div>

    <!-- Topics Grid (with circular mastery ring & short description) -->
    <div id="topics-grid" class="space-y-4 scroll-mt-20">
      <div class="flex items-center justify-between">
        <h2 class="text-xl font-black text-warm-900 flex items-center gap-2">
          <span>🗺️</span>
          <span>Choose a Topic to Master ({{ currentTopics.length }} Topics)</span>
        </h2>
        <span class="text-xs text-warm-500 font-medium hidden sm:inline">Select a topic for study guide or instant quiz</span>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div
          v-for="t in currentTopics"
          :key="t.id"
          @click="goToLearn(t.id)"
          class="card-game flex flex-col justify-between group cursor-pointer"
        >
          <div>
            <!-- Card Header -->
            <div class="flex items-start justify-between gap-3 mb-4">
              <div class="flex items-center gap-3">
                <div :class="['w-14 h-14 rounded-2xl flex items-center justify-center text-3xl shadow-sm', t.iconBg]">
                  {{ t.emoji }}
                </div>
                <div>
                  <h3 class="text-xl sm:text-2xl font-extrabold text-warm-900 group-hover:text-primary-700 transition">
                    {{ t.name }}
                  </h3>
                  <div class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-bold bg-warm-100 text-warm-700 border border-warm-200 mt-1">
                    <span>📜</span>
                    <span>{{ t.standardCode }}</span>
                  </div>
                </div>
              </div>

              <!-- Mastery Circular Ring -->
              <div class="flex flex-col items-center shrink-0">
                <div class="relative w-12 h-12 flex items-center justify-center">
                  <svg class="w-12 h-12 transform -rotate-90" viewBox="0 0 36 36" aria-hidden="true">
                    <!-- Background circle track -->
                    <path
                      class="text-warm-200"
                      stroke-width="3.5"
                      stroke="currentColor"
                      fill="none"
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    />
                    <!-- Foreground progress ring -->
                    <path
                      class="text-primary-600 transition-all duration-700"
                      stroke-width="3.5"
                      stroke-dasharray="100, 100"
                      :stroke-dashoffset="100 - (sessionStore.mastery[t.id] || 50)"
                      stroke-linecap="round"
                      stroke="currentColor"
                      fill="none"
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    />
                  </svg>
                  <span class="absolute text-[11px] font-black text-warm-900">
                    {{ sessionStore.mastery[t.id] || 50 }}%
                  </span>
                </div>
                <span class="text-[10px] font-black uppercase text-warm-500 tracking-wider mt-0.5">Mastery</span>
              </div>
            </div>

            <!-- Short Description -->
            <p class="text-sm text-warm-700 mb-4 leading-relaxed">
              {{ t.description }}
            </p>
          </div>

          <!-- Action Buttons -->
          <div class="grid grid-cols-2 gap-3 pt-2">
            <button
              type="button"
              @click.stop="goToLearn(t.id)"
              :aria-label="`Open study guide and video lesson for ${t.name}`"
              class="btn-game-white py-3 text-sm font-bold flex items-center justify-center gap-1.5 focus:outline-none focus-visible:ring-4 focus-visible:ring-warm-400 min-h-[44px]"
            >
              <span aria-hidden="true">📖</span>
              <span>Learn Guide</span>
            </button>

            <button
              type="button"
              @click.stop="startQuickQuiz(t.id)"
              :disabled="isLoading"
              :aria-label="`Start math quest for ${t.name}`"
              class="btn-game-primary py-3 text-sm font-bold flex items-center justify-center gap-1.5 text-white focus:outline-none focus-visible:ring-4 focus-visible:ring-primary-400 min-h-[44px]"
            >
              <span v-if="isLoading" class="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
              <span v-else aria-hidden="true">⚔️</span>
              <span>{{ isLoading ? 'Loading...' : 'Start Quest' }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Gamification & Badge Trophy Shelf -->
    <div class="bg-white rounded-3xl p-6 sm:p-8 border-2 border-slate-200 shadow-sm space-y-6">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div>
          <h2 class="text-xl font-bold text-slate-800 flex items-center gap-2">
            <span>🏆</span>
            <span>Adventure Trophy Shelf</span>
          </h2>
          <p class="text-xs sm:text-sm text-slate-500">
            Accomplish challenges to unlock all 10 heroic badges across Georgia & CBSE quests
          </p>
        </div>
        <div class="text-sm font-bold text-indigo-600 bg-indigo-50 px-3.5 py-1.5 rounded-2xl border border-indigo-200 self-start">
          {{ sessionStore.badges.length }} of 10 Unlocked
        </div>
      </div>

      <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4">
        <div
          v-for="b in allBadges"
          :key="b.name"
          @click="selectedBadge = b"
          role="button"
          tabindex="0"
          :aria-label="`${b.name} badge: ${b.desc}. Status: ${sessionStore.badges.includes(b.name) ? 'Unlocked' : 'Locked'}`"
          :class="[
            'p-4 rounded-2xl border-2 flex flex-col items-center text-center transition-all cursor-pointer hover:scale-105 active:scale-95 focus:outline-none focus-visible:ring-4 focus-visible:ring-amber-400',
            sessionStore.badges.includes(b.name)
              ? 'bg-amber-50 border-amber-300 shadow-game-amber'
              : 'bg-slate-50 border-dashed border-slate-300 opacity-75 hover:opacity-100'
          ]"
        >
          <span class="text-4xl mb-2" :class="{ 'grayscale opacity-50': !sessionStore.badges.includes(b.name) }">
            {{ b.emoji }}
          </span>
          <span class="font-extrabold text-sm text-slate-800 mb-1 leading-tight">
            {{ b.name }}
          </span>
          <span class="text-xs text-slate-500 leading-tight">
            {{ b.desc }}
          </span>
          <span
            v-if="sessionStore.badges.includes(b.name)"
            class="mt-2 text-[10px] font-bold uppercase bg-amber-200 text-amber-800 px-2 py-0.5 rounded-full"
          >
            Unlocked
          </span>
          <span
            v-else
            class="mt-2 text-[10px] font-bold uppercase bg-slate-200 text-slate-600 px-2 py-0.5 rounded-full"
          >
            Locked
          </span>
        </div>
      </div>
    </div>

    <!-- Badge Inspection Modal -->
    <div
      v-if="selectedBadge"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-fade-in"
      @click.self="selectedBadge = null"
      role="dialog"
      aria-modal="true"
      :aria-label="selectedBadge.name"
    >
      <div class="bg-white rounded-3xl p-6 sm:p-8 max-w-sm w-full border-4 border-amber-400 shadow-2xl text-center space-y-4 animate-pop">
        <div class="w-20 h-20 mx-auto rounded-3xl bg-amber-100 flex items-center justify-center text-5xl shadow-inner">
          {{ selectedBadge.emoji }}
        </div>
        <div>
          <h3 class="text-2xl font-black text-slate-800">{{ selectedBadge.name }}</h3>
          <p
            class="text-xs font-bold uppercase tracking-wider mt-1"
            :class="sessionStore.badges.includes(selectedBadge.name) ? 'text-amber-700' : 'text-slate-500'"
          >
            {{ sessionStore.badges.includes(selectedBadge.name) ? '🎉 Unlocked & Mastered!' : '🔒 Quest Challenge Locked' }}
          </p>
        </div>
        <p class="text-sm text-slate-600 bg-slate-50 p-3 rounded-2xl border border-slate-200 leading-relaxed">
          {{ selectedBadge.desc }}
        </p>
        <button
          type="button"
          @click="selectedBadge = null"
          class="btn-game-amber w-full py-3 rounded-2xl font-bold text-slate-900 focus:outline-none focus-visible:ring-4 focus-visible:ring-amber-400"
        >
          Awesome, Got It!
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useApi } from '~/composables/useApi'
import { useSessionStore, type BoardType, type GradeLevel, type TopicType } from '~/stores/session'

const router = useRouter()
const { fetchRoundBatch, isLoading } = useApi()
const sessionStore = useSessionStore()

const selectedBadge = ref<any>(null)

const goToLearn = (topicId: TopicType) => {
  sessionStore.setTopic(topicId)
  router.push(`/learn/${sessionStore.grade}/${topicId}`)
}

const selectBoard = (b: BoardType) => {
  sessionStore.setBoard(b)
  if (b === 'cbse') {
    sessionStore.setGrade(6)
  }
}

const selectGrade = (g: GradeLevel) => {
  sessionStore.setGrade(g)
}

interface DisplayTopic {
  id: TopicType
  name: string
  emoji: string
  iconBg: string
  btnColor: string
  progressColor: string
  standardCode: string
  description: string
}

const georgiaTopicsG5: DisplayTopic[] = [
  {
    id: 'fractions',
    name: 'Fractions',
    emoji: '🍕',
    iconBg: 'bg-emerald-100 text-emerald-700',
    btnColor: 'btn-game-green',
    progressColor: 'bg-emerald-500',
    standardCode: 'MGSE5.NF.1 / MGSE5.NF.4',
    description: 'Add and subtract fractions with unlike denominators, and multiply fractions by fractions.',
  },
  {
    id: 'decimals',
    name: 'Decimals',
    emoji: '🎯',
    iconBg: 'bg-sky-100 text-sky-700',
    btnColor: 'btn-game-blue',
    progressColor: 'bg-sky-500',
    standardCode: 'MGSE5.NBT.7',
    description: 'Add, subtract, and multiply decimals to hundredths using place-value models.',
  },
  {
    id: 'ratios',
    name: 'Patterns & Ratios',
    emoji: '⚖️',
    iconBg: 'bg-amber-100 text-amber-800',
    btnColor: 'btn-game-amber',
    progressColor: 'bg-amber-500',
    standardCode: 'MGSE5.OA.3',
    description: 'Generate numerical patterns, analyze rules, and understand multiplicative scale relationships.',
  },
  {
    id: 'geometry',
    name: 'Geometry & Volume',
    emoji: '📐',
    iconBg: 'bg-purple-100 text-purple-700',
    btnColor: 'btn-game-purple',
    progressColor: 'bg-purple-500',
    standardCode: 'MGSE5.MD.5',
    description: 'Calculate rectangular area, perimeter, and volume of rectangular prisms.',
  },
]

const georgiaTopicsG6: DisplayTopic[] = [
  {
    id: 'fractions',
    name: 'Fractions',
    emoji: '🍕',
    iconBg: 'bg-emerald-100 text-emerald-700',
    btnColor: 'btn-game-green',
    progressColor: 'bg-emerald-500',
    standardCode: 'MGSE6.NS.1',
    description: 'Divide fractions by fractions using reciprocals and solve real-world quotient scenarios.',
  },
  {
    id: 'decimals',
    name: 'Decimals',
    emoji: '🎯',
    iconBg: 'bg-sky-100 text-sky-700',
    btnColor: 'btn-game-blue',
    progressColor: 'bg-sky-500',
    standardCode: 'MGSE6.NS.3',
    description: 'Fluently calculate with multi-digit decimals using standard algorithms with zero drop checks.',
  },
  {
    id: 'ratios',
    name: 'Ratios & Proportions',
    emoji: '⚖️',
    iconBg: 'bg-amber-100 text-amber-800',
    btnColor: 'btn-game-amber',
    progressColor: 'bg-amber-500',
    standardCode: 'MGSE6.RP.1 / MGSE6.RP.2',
    description: 'Understand ratio concepts, scale factors, equivalent rates, and unit pricing.',
  },
  {
    id: 'geometry',
    name: 'Geometry & Area',
    emoji: '📐',
    iconBg: 'bg-purple-100 text-purple-700',
    btnColor: 'btn-game-purple',
    progressColor: 'bg-purple-500',
    standardCode: 'MGSE6.G.1',
    description: 'Find the area of triangles, special quadrilaterals, and composite geometric polygons.',
  },
]

const cbseTopicsG6: DisplayTopic[] = [
  {
    id: 'factors_multiples',
    name: 'Factors & Multiples',
    emoji: '🔢',
    iconBg: 'bg-blue-100 text-blue-700',
    btnColor: 'btn-game-blue',
    progressColor: 'bg-blue-500',
    standardCode: 'CBSE6.MATH.01 (NCERT)',
    description: 'Prime factorization, prime/composite numbers, lowest common multiple (LCM), and HCF/GCD.',
  },
  {
    id: 'fractions',
    name: 'Fractions',
    emoji: '🍕',
    iconBg: 'bg-emerald-100 text-emerald-700',
    btnColor: 'btn-game-green',
    progressColor: 'bg-emerald-500',
    standardCode: 'CBSE6.MATH.02 (NCERT)',
    description: 'Fractions on number lines, proper/improper fractions, equivalent fractions, and rational operations.',
  },
  {
    id: 'decimals',
    name: 'Decimals',
    emoji: '🎯',
    iconBg: 'bg-sky-100 text-sky-700',
    btnColor: 'btn-game-blue',
    progressColor: 'bg-sky-500',
    standardCode: 'CBSE6.MATH.03 (NCERT)',
    description: 'Decimal place values, tenths and hundredths, money/length conversion, and arithmetic.',
  },
  {
    id: 'integers',
    name: 'Integers',
    emoji: '🏔️',
    iconBg: 'bg-teal-100 text-teal-700',
    btnColor: 'btn-game-green',
    progressColor: 'bg-teal-500',
    standardCode: 'CBSE6.MATH.04 (NCERT)',
    description: 'Positive and negative numbers, number line representation, ordering, and addition/subtraction.',
  },
  {
    id: 'ratios',
    name: 'Ratio & Proportion',
    emoji: '⚖️',
    iconBg: 'bg-amber-100 text-amber-800',
    btnColor: 'btn-game-amber',
    progressColor: 'bg-amber-500',
    standardCode: 'CBSE6.MATH.05 (NCERT)',
    description: 'Ratio comparison, simplest forms, proportions, and unitary method problem solving.',
  },
  {
    id: 'geometry',
    name: 'Mensuration & Geometry',
    emoji: '📐',
    iconBg: 'bg-purple-100 text-purple-700',
    btnColor: 'btn-game-purple',
    progressColor: 'bg-purple-500',
    standardCode: 'CBSE6.MATH.06 (NCERT)',
    description: 'Perimeter and area of rectangles, squares, and introductory 2D geometric shapes.',
  },
]

const currentTopics = computed<DisplayTopic[]>(() => {
  if (sessionStore.board === 'cbse') {
    return cbseTopicsG6
  }
  return sessionStore.grade === 5 ? georgiaTopicsG5 : georgiaTopicsG6
})

const allBadges = [
  { name: 'First Steps', emoji: '👣', desc: 'Answer your very first quest question.' },
  { name: '5-Streak', emoji: '🔥', desc: 'Get 5 correct answers in a row.' },
  { name: 'Fraction Master', emoji: '🍕', desc: 'Reach 80+ mastery or 5 correct in fractions.' },
  { name: 'Decimal Dynamo', emoji: '🎯', desc: 'Reach 80+ mastery or 5 correct in decimals.' },
  { name: 'Ratio Ranger', emoji: '⚖️', desc: 'Reach 80+ mastery or 5 correct in ratios.' },
  { name: 'Geometry Giant', emoji: '📐', desc: 'Reach 80+ mastery or 5 correct in geometry.' },
  { name: 'CBSE Champion', emoji: '🇮🇳', desc: 'Complete a CBSE round with 80%+ accuracy.' },
  { name: 'Tenacious Thinker', emoji: '🧠', desc: 'Successfully conquer a Hard difficulty challenge.' },
  { name: 'Comeback Kid', emoji: '⚡', desc: 'Bounce back with a correct answer after a mistake.' },
  { name: 'Perfect Round', emoji: '🌟', desc: 'Complete a full round with 100% accuracy.' },
]

const startQuickQuiz = async (topicId: TopicType) => {
  sessionStore.setTopic(topicId)
  try {
    const res = await fetchRoundBatch(sessionStore.grade, topicId, sessionStore.tier, 10, sessionStore.board)
    if (res && res.questions && res.questions.length > 0) {
      sessionStore.startRound(res.questions)
    }
  } catch (err) {
    console.warn('Network issue during question loading; continuing with session fallback:', err)
  } finally {
    router.push('/quiz')
  }
}
</script>
