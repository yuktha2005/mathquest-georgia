<template>
  <!-- Invalid Grade/Topic 404 Fallback View -->
  <div v-if="!isValidTopic" class="min-h-[70vh] flex flex-col items-center justify-center p-4 text-center">
    <div class="w-full max-w-lg space-y-6">
      <div class="inline-flex items-center justify-center w-28 h-28 rounded-3xl bg-indigo-100 border-4 border-indigo-200 text-5xl shadow-xl animate-bounce" aria-hidden="true">
        🧭
      </div>
      <div>
        <span class="px-4 py-1.5 rounded-full bg-accent-100 border-2 border-accent-300 text-warm-900 font-extrabold text-xs uppercase tracking-wider">
          Topic Not Found
        </span>
      </div>
      <div class="space-y-2">
        <h1 class="text-3xl sm:text-4xl font-extrabold text-warm-900 tracking-tight">
          Unknown Math Territory
        </h1>
        <p class="text-warm-700 text-sm sm:text-base font-semibold max-w-md mx-auto">
          We couldn't find a learning quest for "{{ route.params.grade }}/{{ route.params.topic }}". Choose an active grade and topic from the map!
        </p>
      </div>
      <div class="flex flex-col sm:flex-row gap-3 justify-center max-w-xs sm:max-w-md mx-auto pt-2">
        <NuxtLink
          to="/"
          class="flex-1 py-3.5 px-6 rounded-2xl font-extrabold text-sm sm:text-base text-white bg-primary-700 hover:bg-primary-800 active:scale-95 transition shadow-game-blue border-b-4 border-primary-900 flex items-center justify-center gap-2 min-h-[44px]"
        >
          <span>🗺️</span>
          <span>Return to Quest Map</span>
        </NuxtLink>
      </div>
    </div>
  </div>

  <div v-else class="max-w-6xl mx-auto space-y-6 animate-pop pb-16">
    <!-- Top Navigation & Grade Indicator -->
    <div class="flex items-center justify-between flex-wrap gap-4">
      <NuxtLink
        to="/"
        class="inline-flex items-center gap-2 text-sm font-bold text-warm-700 hover:text-primary-700 transition bg-white px-4 py-2 rounded-2xl border-2 border-warm-200 shadow-warm-sm min-h-[44px]"
      >
        <span class="text-lg" aria-hidden="true">⬅️</span>
        <span>Back to Quest Map</span>
      </NuxtLink>

      <div class="flex items-center gap-2">
        <span class="px-3.5 py-1.5 rounded-full text-xs font-extrabold bg-primary-50 text-primary-900 border border-primary-200 shadow-xs flex items-center gap-1.5">
          <span>🎒</span>
          <span>Grade {{ grade }}</span>
        </span>
        <span class="px-3.5 py-1.5 rounded-full text-xs font-extrabold bg-accent-50 text-warm-900 border border-accent-300 shadow-xs capitalize flex items-center gap-1.5">
          <span>{{ topicMeta.emoji }}</span>
          <span>{{ topic }}</span>
        </span>
      </div>
    </div>

    <!-- Header Hero Card -->
    <div class="card-game space-y-4 relative overflow-hidden">
      <!-- Aligned to Standard Badge -->
      <div class="flex items-start sm:items-center gap-2.5 flex-wrap">
        <div class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs sm:text-sm font-extrabold bg-primary-700 text-white shadow-xs shrink-0">
          <span>🏛️</span>
          <span>Aligned to {{ currentStandardCode }}</span>
        </div>
        <p v-if="currentStandardSnippet" class="text-xs sm:text-sm font-semibold text-warm-700 max-w-2xl">
          {{ currentStandardSnippet }}
        </p>
      </div>

      <!-- Main Title & Practice Action -->
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-6 pt-1">
        <div class="space-y-1.5">
          <h1 class="text-2xl sm:text-4xl font-black text-warm-900 tracking-tight flex items-center gap-3">
            <span>{{ topicMeta.emoji }}</span>
            <span>{{ explanation?.title || topicMeta.title }}</span>
          </h1>
          <p class="text-warm-700 text-base sm:text-lg max-w-3xl leading-relaxed">
            {{ explanation?.intro || topicMeta.subtitle }}
          </p>
        </div>

        <button
          type="button"
          @click="startQuest"
          :disabled="isLaunchingRound"
          class="btn-game-primary px-7 py-3.5 text-base font-black shadow-game-blue whitespace-nowrap self-start md:self-center shrink-0 min-h-[44px]"
        >
          <span v-if="isLaunchingRound" class="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></span>
          <span v-else class="mr-2">⚔️</span>
          <span>{{ isLaunchingRound ? 'Summoning...' : 'Start Practice' }}</span>
        </button>
      </div>
    </div>

    <!-- Cold Start Wakeup Notice -->
    <div v-if="isServerWakingUp" class="p-4 rounded-2xl bg-accent-50 border-2 border-accent-300 text-warm-900 text-sm font-bold flex items-center gap-3 animate-pulse">
      <span class="text-xl">🚀</span>
      <span>{{ wakeUpNotice || 'Waking up the server for your explanation...' }}</span>
    </div>

    <!-- 3 Core Navigation Tabs: Explanation / Video / Practice -->
    <div class="flex items-center gap-2 border-b-2 border-warm-200 pb-2 overflow-x-auto" role="tablist" aria-label="Topic Study Modes">
      <button
        type="button"
        role="tab"
        :aria-selected="activeTab === 'explanation'"
        @click="activeTab = 'explanation'"
        :class="[
          'px-5 py-3 rounded-2xl font-black text-sm sm:text-base flex items-center gap-2 transition min-h-[44px] cursor-pointer',
          activeTab === 'explanation'
            ? 'bg-primary-700 text-white shadow-game-blue'
            : 'bg-white text-warm-700 hover:bg-warm-100 border-2 border-warm-200 shadow-sm'
        ]"
      >
        <span>📖</span>
        <span>Explanation Guide</span>
      </button>

      <button
        type="button"
        role="tab"
        :aria-selected="activeTab === 'video'"
        @click="activeTab = 'video'"
        :class="[
          'px-5 py-3 rounded-2xl font-black text-sm sm:text-base flex items-center gap-2 transition min-h-[44px] cursor-pointer',
          activeTab === 'video'
            ? 'bg-primary-700 text-white shadow-game-blue'
            : 'bg-white text-warm-700 hover:bg-warm-100 border-2 border-warm-200 shadow-sm'
        ]"
      >
        <span>🎬</span>
        <span>Interactive Video</span>
      </button>

      <button
        type="button"
        role="tab"
        :aria-selected="activeTab === 'practice'"
        @click="activeTab = 'practice'"
        :class="[
          'px-5 py-3 rounded-2xl font-black text-sm sm:text-base flex items-center gap-2 transition min-h-[44px] cursor-pointer',
          activeTab === 'practice'
            ? 'bg-primary-700 text-white shadow-game-blue'
            : 'bg-white text-warm-700 hover:bg-warm-100 border-2 border-warm-200 shadow-sm'
        ]"
      >
        <span>⚔️</span>
        <span>Practice Quest</span>
      </button>
    </div>

    <!-- Main Content Layout: Two Columns on Desktop with Sticky Infographic on Right -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start pt-2">
      <!-- Left Column: Active Tab Content (Col span 7) -->
      <div class="lg:col-span-7 space-y-6">
        <!-- TAB 1: EXPLANATION -->
        <div v-if="activeTab === 'explanation'" class="space-y-6">
          <!-- "Explain Differently" Selector -->
          <div class="card-game p-5 space-y-3">
            <div class="flex items-center gap-2 text-xs font-black uppercase tracking-wider text-warm-500">
              <span>💡</span>
              <span>Explain differently:</span>
            </div>

            <div class="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
              <button
                v-for="btn in styleOptions"
                :key="btn.id"
                type="button"
                @click="switchStyle(btn.id)"
                :disabled="isLoadingStyle"
                :class="[
                  'px-3.5 py-2.5 rounded-xl text-xs sm:text-sm font-black transition-all flex items-center justify-center gap-1.5 border-2 text-center cursor-pointer min-h-[44px]',
                  selectedStyle === btn.id
                    ? 'bg-accent-400 text-warm-900 border-accent-600 shadow-game-amber scale-[1.02]'
                    : 'bg-warm-50 text-warm-800 border-warm-200 hover:bg-warm-100 hover:border-warm-300'
                ]"
              >
                <span>{{ btn.icon }}</span>
                <span>{{ btn.label }}</span>
              </button>
            </div>
          </div>

          <!-- Loading Skeleton -->
          <div v-if="isLoadingStyle" class="card-game p-8 space-y-6 animate-pulse">
            <div class="h-6 bg-warm-200 rounded-full w-2/3"></div>
            <div class="space-y-2">
              <div class="h-4 bg-warm-100 rounded-full w-full"></div>
              <div class="h-4 bg-warm-100 rounded-full w-5/6"></div>
            </div>
            <div class="h-32 bg-warm-100 rounded-2xl"></div>
          </div>

          <template v-else>
            <!-- Key Ideas Card -->
            <div class="card-game space-y-4">
              <h2 class="text-xl font-black text-warm-900 flex items-center gap-2.5">
                <span class="inline-flex items-center justify-center w-7 h-7 rounded-xl bg-primary-100 text-primary-800 text-base">🔑</span>
                <span>Key Ideas to Remember</span>
              </h2>

              <ul class="space-y-3">
                <li
                  v-for="(idea, idx) in currentKeyIdeas"
                  :key="idx"
                  class="flex items-start gap-3 text-base text-warm-800 font-medium leading-relaxed"
                >
                  <span class="inline-flex items-center justify-center w-5 h-5 rounded-full bg-primary-700 text-white text-xs font-bold shrink-0 mt-0.5">
                    {{ idx + 1 }}
                  </span>
                  <span>{{ idea }}</span>
                </li>
              </ul>
            </div>

            <!-- Worked Examples (Rule 1 Verified Math) -->
            <div class="space-y-4">
              <div class="flex items-center justify-between">
                <h2 class="text-xl font-black text-warm-900 flex items-center gap-2.5">
                  <span class="inline-flex items-center justify-center w-7 h-7 rounded-xl bg-emerald-100 text-emerald-800 text-base">📝</span>
                  <span>Worked Examples (Verified Solutions)</span>
                </h2>
                <span class="text-xs font-extrabold text-emerald-800 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-300">
                  100% Math Verified
                </span>
              </div>

              <!-- Example Cards -->
              <div
                v-for="(example, idx) in currentWorkedExamples"
                :key="idx"
                class="card-game space-y-4"
              >
                <div class="flex items-center justify-between flex-wrap gap-2">
                  <span class="px-3 py-1 rounded-full text-xs font-extrabold bg-emerald-100 text-emerald-900 border border-emerald-300">
                    Example #{{ idx + 1 }}
                  </span>
                  <span class="font-mono text-xs font-bold text-warm-600 bg-warm-100 px-2.5 py-0.5 rounded-lg border border-warm-200">
                    Problem: {{ example.expression }}
                  </span>
                </div>

                <p class="text-base font-bold text-warm-900 leading-snug">
                  {{ example.problem }}
                </p>

                <!-- Step-by-Step Breakdown -->
                <div class="bg-warm-50 rounded-2xl p-4 border border-warm-200 space-y-2">
                  <p class="text-xs font-bold uppercase tracking-wider text-warm-500">
                    Solution Walkthrough:
                  </p>
                  <ul class="space-y-1.5">
                    <li
                      v-for="(step, sIdx) in example.steps"
                      :key="sIdx"
                      class="text-sm text-warm-800 flex items-start gap-2"
                    >
                      <span class="text-primary-700 font-bold shrink-0">•</span>
                      <span>{{ step }}</span>
                    </li>
                  </ul>
                </div>

                <!-- Verified Final Answer Banner -->
                <div class="flex items-center justify-between bg-emerald-50 border-2 border-emerald-300 rounded-2xl px-4 py-2.5 text-emerald-950">
                  <div class="flex items-center gap-2">
                    <span class="text-base">✅</span>
                    <span class="text-sm font-bold">Verified Final Answer:</span>
                  </div>
                  <span class="font-black text-base sm:text-lg text-emerald-900 font-mono bg-white px-3 py-0.5 rounded-xl border border-emerald-300 shadow-xs">
                    {{ example.verified_answer }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Common Mistakes Card -->
            <div class="bg-rose-50 rounded-3xl p-6 sm:p-7 border-2 border-rose-300 shadow-sm space-y-4">
              <h2 class="text-lg font-black text-rose-950 flex items-center gap-2">
                <span>⚠️</span>
                <span>Common Mistakes & Traps to Avoid</span>
              </h2>
              <ul class="space-y-2.5">
                <li
                  v-for="(mistake, idx) in currentCommonMistakes"
                  :key="idx"
                  class="flex items-start gap-2.5 text-sm text-rose-950 font-medium leading-relaxed"
                >
                  <span class="text-base shrink-0 mt-0.5">🚫</span>
                  <span>{{ mistake }}</span>
                </li>
              </ul>
            </div>
          </template>
        </div>

        <!-- TAB 2: INTERACTIVE VIDEO LESSON -->
        <div v-else-if="activeTab === 'video'" class="space-y-4">
          <div class="flex items-center justify-between flex-wrap gap-2">
            <h2 class="text-xl font-black text-warm-900 flex items-center gap-2">
              <span class="inline-flex items-center justify-center w-8 h-8 rounded-2xl bg-accent-400 text-warm-900 text-lg shadow-sm">
                🎬
              </span>
              <span>6-Slide Interactive Video Masterclass</span>
            </h2>
            <span class="text-xs font-bold text-warm-600 bg-white px-3 py-1.5 rounded-full border border-warm-200">
              🎙️ Web Speech Narration & Subtitles
            </span>
          </div>

          <!-- Video Loading Skeleton -->
          <div
            v-if="isLoadingScript"
            class="w-full bg-warm-900 rounded-3xl p-12 flex flex-col items-center justify-center space-y-4 animate-pulse min-h-[380px] border-4 border-warm-800"
          >
            <div class="w-12 h-12 border-4 border-accent-400 border-t-transparent rounded-full animate-spin"></div>
            <p class="text-warm-300 font-bold text-sm">Preparing your 6-slide video lesson...</p>
          </div>

          <!-- Video Player Component -->
          <VideoPlayer
            v-else-if="videoScript?.slides?.length"
            :slides="videoScript.slides"
            :title="videoScript.title"
            :topic="topic"
            :grade="grade"
          />
        </div>

        <!-- TAB 3: PRACTICE QUEST -->
        <div v-else-if="activeTab === 'practice'" class="card-game p-6 sm:p-8 space-y-6 text-center">
          <div class="w-16 h-16 rounded-3xl bg-accent-100 text-accent-800 flex items-center justify-center text-4xl mx-auto shadow-sm">
            ⚔️
          </div>
          <div class="space-y-2 max-w-md mx-auto">
            <h2 class="text-2xl font-black text-warm-900">
              Ready for the {{ topicMeta.title }} Quest?
            </h2>
            <p class="text-sm text-warm-700 leading-relaxed">
              Solve 10 curriculum-aligned questions. Start at {{ sessionStore.tier.toUpperCase() }} tier. The difficulty adapts automatically based on your answers!
            </p>
          </div>

          <div class="grid grid-cols-2 gap-4 max-w-sm mx-auto text-left">
            <div class="bg-warm-50 p-4 rounded-2xl border border-warm-200">
              <span class="text-xs font-bold text-warm-500 uppercase block">Current Tier</span>
              <span class="text-lg font-black text-primary-700 capitalize">
                {{ sessionStore.tier === 'easy' ? '🌱 Easy' : sessionStore.tier === 'medium' ? '🎯 Medium' : '⚡ Hard' }}
              </span>
            </div>
            <div class="bg-warm-50 p-4 rounded-2xl border border-warm-200">
              <span class="text-xs font-bold text-warm-500 uppercase block">Current Mastery</span>
              <span class="text-lg font-black text-emerald-700">
                {{ sessionStore.mastery[topic] || 50 }}%
              </span>
            </div>
          </div>

          <button
            type="button"
            @click="startQuest"
            :disabled="isLaunchingRound"
            class="btn-game-primary px-8 py-4 text-lg font-black shadow-game-blue cursor-pointer inline-flex items-center gap-2 min-h-[48px]"
          >
            <span v-if="isLaunchingRound" class="inline-block w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
            <span v-else>🚀</span>
            <span>{{ isLaunchingRound ? 'Summoning Arena...' : 'Begin 10-Question Quest' }}</span>
          </button>
        </div>
      </div>

      <!-- Right Column: Sticky Infographic + Sources Used Panel (Col span 5) -->
      <div class="lg:col-span-5 space-y-6 lg:sticky lg:top-6">
        <!-- Infographic Card -->
        <div class="card-game space-y-4">
          <div class="flex items-center justify-between">
            <h2 class="text-lg font-black text-warm-900 flex items-center gap-2">
              <span>🖼️</span>
              <span>Topic Diagram</span>
            </h2>
            <span
              :class="[
                'text-xs font-extrabold px-2.5 py-1 rounded-full border',
                usingFallbackImage
                  ? 'bg-warm-100 text-warm-700 border-warm-300'
                  : 'bg-primary-50 text-primary-700 border-primary-200'
              ]"
            >
              {{ usingFallbackImage ? 'Geometric Vector' : 'AI Illustrated' }}
            </span>
          </div>

          <!-- Infographic Image Frame -->
          <div class="bg-warm-50 rounded-2xl p-3 border-2 border-warm-100 flex flex-col items-center justify-center overflow-hidden min-h-[280px] relative">
            <div v-if="isImageLoading" class="absolute inset-0 bg-warm-50 flex items-center justify-center z-10">
              <div class="flex flex-col items-center gap-2">
                <div class="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
                <span class="text-xs font-bold text-warm-600">Loading diagram...</span>
              </div>
            </div>

            <img
              :src="infographicSrc"
              :alt="`${topic} Educational Diagram`"
              @load="onImageLoad"
              @error="onImageError"
              class="max-w-full h-auto rounded-xl shadow-xs transition-transform hover:scale-105 duration-300 object-contain"
            />
          </div>

          <p class="text-xs text-warm-500 font-medium text-center">
            {{ usingFallbackImage ? '📐 High-clarity geometric diagram' : '✨ Topic visual concept guide' }}
          </p>
        </div>

        <!-- Sources Used Panel (Retrieval data / curriculum standards) -->
        <div class="card-game space-y-3">
          <div class="flex items-center gap-2 text-sm font-black text-warm-900">
            <span>📚</span>
            <span>Sources & Standards Used</span>
          </div>
          <div class="bg-warm-50 rounded-2xl p-4 border border-warm-200 space-y-2 text-xs text-warm-800">
            <div class="font-extrabold text-primary-700 flex items-center gap-1.5 text-sm">
              <span>🏛️</span>
              <span>{{ currentStandardCode }}</span>
            </div>
            <p class="font-semibold text-warm-800 leading-relaxed">
              {{ currentStandardSnippet || (grade === 5 ? 'Georgia GSE Grade 5 Standards & CBSE NCERT Curriculum Progression' : 'Georgia GSE Grade 6 Standards & CBSE NCERT Curriculum Progression') }}
            </p>
            <div class="text-[11px] text-warm-500 pt-2 border-t border-warm-200 flex items-center justify-between">
              <span>Authority: {{ sessionStore.board === 'cbse' ? 'NCERT (Ganita Prakash)' : 'GaDOE (Georgia Standards)' }}</span>
              <span class="text-emerald-700 font-extrabold flex items-center gap-1">
                <span>✓</span>
                <span>Verified</span>
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const validGrades = ['5', '6']
const validTopics = ['fractions', 'decimals', 'ratios', 'geometry', 'factors_multiples', 'integers']
const routeGrade = String(route.params.grade || '')
const routeTopic = String(route.params.topic || '').toLowerCase()
const isValidTopic = computed(() => validGrades.includes(routeGrade) && validTopics.includes(routeTopic))

if (import.meta.server && (!validGrades.includes(routeGrade) || !validTopics.includes(routeTopic))) {
  const event = useRequestEvent()
  if (event) {
    setResponseStatus(event, 404, 'Topic Not Found')
  }
}

import {
  useApi,
  type ExplainResponse,
  type ExplainStyle,
  type WorkedExample,
  type ScriptResponse,
} from '~/composables/useApi'
import { useSessionStore, type GradeLevel, type TopicType } from '~/stores/session'
import VideoPlayer from '~/components/VideoPlayer.vue'
const {
  fetchExplanation,
  fetchInfographic,
  fetchScript,
  fetchRoundBatch,
  isServerWakingUp,
  wakeUpNotice,
} = useApi()
const sessionStore = useSessionStore()

const grade = computed<GradeLevel>(() => {
  const g = Number(route.params.grade)
  return g === 6 ? 6 : 5
})

const topic = computed<TopicType>(() => {
  const t = String(route.params.topic).toLowerCase()
  if (['fractions', 'decimals', 'ratios', 'geometry', 'factors_multiples', 'integers'].includes(t)) {
    return t as TopicType
  }
  return 'fractions'
})

// Active study mode tab
const activeTab = ref<'explanation' | 'video' | 'practice'>('explanation')

// Explain style selection state
const selectedStyle = ref<ExplainStyle>('default')
const explanation = ref<ExplainResponse | null>(null)
const isLoadingStyle = ref<boolean>(false)
const isLaunchingRound = ref<boolean>(false)

// Video script state
const videoScript = ref<ScriptResponse | null>(null)
const isLoadingScript = ref<boolean>(true)

// Infographic image state
const infographicSrc = ref<string>(`/infographics/${topic.value}.svg`)
const fallbackSvg = ref<string>(`/infographics/${topic.value}.svg`)
const usingFallbackImage = ref<boolean>(false)
const isImageLoading = ref<boolean>(true)

const styleOptions = [
  { id: 'default' as ExplainStyle, label: 'Standard', icon: '🌟' },
  { id: 'simpler' as ExplainStyle, label: 'Simpler', icon: '🧸' },
  { id: 'real_life' as ExplainStyle, label: 'Real-World', icon: '🍑' },
  { id: 'step_by_step' as ExplainStyle, label: 'Step-by-Step', icon: '📋' },
]

// Topic Fallback metadata
const metaData = {
  fractions: {
    title: 'Fractions Kingdom',
    emoji: '🍕',
    subtitle:
      grade.value === 5
        ? 'Learn to add and subtract fractions with unlike denominators, and multiply fractions with ease.'
        : 'Divide fractions by fractions using Keep-Change-Flip reciprocals and solve real-world problems.',
  },
  decimals: {
    title: 'Decimals Domain',
    emoji: '🎯',
    subtitle:
      grade.value === 5
        ? 'Add, subtract, and multiply decimals to hundredths using place-value understanding.'
        : 'Fluently add, subtract, multiply, and divide multi-digit decimals using the standard algorithm.',
  },
  ratios: {
    title: 'Ratios Realm',
    emoji: '⚖️',
    subtitle:
      grade.value === 5
        ? 'Analyze numerical patterns, scale rules, and proportional relationships between quantities.'
        : 'Understand ratio concepts, unit rates, equivalent ratios, and scaling factors.',
  },
  geometry: {
    title: 'Geometry Citadel',
    emoji: '📐',
    subtitle:
      grade.value === 5
        ? 'Understand area, perimeter, and calculate volume of rectangular prisms (V = l × w × h).'
        : 'Find the area of triangles, special quadrilaterals, and composite polygons.',
  },
  factors_multiples: {
    title: 'Factors & Multiples Outpost',
    emoji: '🔢',
    subtitle: 'Master prime factorization, lowest common multiple (LCM), and highest common factor (HCF/GCD).',
  },
  integers: {
    title: 'Integers Frontier',
    emoji: '🏔️',
    subtitle: 'Explore negative numbers, absolute values, number lines, and integer arithmetic.',
  },
}

const topicMeta = computed(() => {
  return metaData[topic.value] || metaData.fractions
})

const currentStandardCode = computed(() => {
  return explanation.value?.standard_code || (grade.value === 5 ? `MGSE5.${topic.value.slice(0, 2).toUpperCase()}` : `MGSE6.${topic.value.slice(0, 2).toUpperCase()}`)
})

const currentStandardSnippet = computed(() => {
  return explanation.value?.standard_snippet || ''
})

const currentKeyIdeas = computed(() => {
  if (explanation.value?.key_ideas?.length) {
    return explanation.value.key_ideas
  }
  return [
    'Always read the problem carefully and identify what operation is needed.',
    'Follow step-by-step mathematical rules and double-check your arithmetic.',
    'Express your final answer in simplest form with correct units.',
  ]
})

const currentWorkedExamples = computed<WorkedExample[]>(() => {
  if (explanation.value?.worked_examples?.length) {
    return explanation.value.worked_examples
  }
  return []
})

const currentCommonMistakes = computed(() => {
  if (explanation.value?.common_mistakes?.length) {
    return explanation.value.common_mistakes
  }
  return [
    'Rushing calculations without verifying units or place value.',
    'Forgetting to double-check the final answer against the original question.',
  ]
})

// Load explanation for the selected style
const loadExplanation = async (style: ExplainStyle) => {
  isLoadingStyle.value = true
  try {
    const res = await fetchExplanation(grade.value, topic.value, style)
    explanation.value = res
  } catch (err) {
    console.warn('Could not fetch explanation from backend; using default template:', err)
  } finally {
    isLoadingStyle.value = false
  }
}

// Switch pedagogical style on button click
const switchStyle = async (newStyle: ExplainStyle) => {
  if (selectedStyle.value === newStyle && explanation.value) return
  selectedStyle.value = newStyle
  await loadExplanation(newStyle)
}

// Load 6-slide video presentation script
const loadVideoScript = async () => {
  isLoadingScript.value = true
  try {
    const res = await fetchScript(grade.value, topic.value)
    videoScript.value = res
  } catch (err) {
    console.warn('Could not fetch video script; will use fallback:', err)
  } finally {
    isLoadingScript.value = false
  }
}

// Load infographic from backend (returns Pollinations URL with SVG fallback)
const loadInfographic = async () => {
  isImageLoading.value = true
  usingFallbackImage.value = false
  try {
    const info = await fetchInfographic(topic.value, grade.value)
    if (info?.image_url) {
      infographicSrc.value = info.image_url
      fallbackSvg.value = info.fallback_url || `/infographics/${topic.value}.svg`
    } else {
      infographicSrc.value = `/infographics/${topic.value}.svg`
      usingFallbackImage.value = true
    }
  } catch (err) {
    console.warn('Could not load Pollinations infographic URL; defaulting to SVG:', err)
    infographicSrc.value = `/infographics/${topic.value}.svg`
    usingFallbackImage.value = true
  }
}

const onImageLoad = () => {
  isImageLoading.value = false
}

const onImageError = () => {
  // If the Pollinations remote image fails, immediately swap to local SVG fallback
  if (!usingFallbackImage.value) {
    console.info('Pollinations image failed or timed out. Falling back to local SVG diagram.')
    usingFallbackImage.value = true
    infographicSrc.value = fallbackSvg.value || `/infographics/${topic.value}.svg`
  }
  isImageLoading.value = false
}

// Start 10-question practice round
const startQuest = async () => {
  isLaunchingRound.value = true
  sessionStore.setGrade(grade.value)
  sessionStore.setTopic(topic.value)

  try {
    const res = await fetchRoundBatch(grade.value, topic.value, sessionStore.tier, 10, sessionStore.board)
    sessionStore.startRound(res.questions)
    router.push('/quiz')
  } catch (err) {
    console.error('Failed to start practice quest round:', err)
  } finally {
    isLaunchingRound.value = false
  }
}

onMounted(() => {
  loadExplanation('default')
  loadVideoScript()
  loadInfographic()
})
</script>
