<template>
  <div class="max-w-6xl mx-auto space-y-8 animate-pop pb-16">
    <!-- Navigation & Grade Indicator -->
    <div class="flex items-center justify-between flex-wrap gap-4">
      <NuxtLink
        to="/"
        class="inline-flex items-center gap-2 text-sm font-bold text-slate-600 hover:text-indigo-600 transition bg-white px-4 py-2 rounded-2xl border-2 border-slate-200 shadow-sm"
      >
        <span class="text-lg">⬅️</span>
        <span>Back to Quest Map</span>
      </NuxtLink>

      <div class="flex items-center gap-2">
        <span class="px-3.5 py-1.5 rounded-full text-xs font-extrabold bg-indigo-100 text-indigo-800 border border-indigo-300 shadow-xs flex items-center gap-1.5">
          <span>🎒</span>
          <span>Grade {{ grade }}</span>
        </span>
        <span class="px-3.5 py-1.5 rounded-full text-xs font-extrabold bg-amber-100 text-amber-900 border border-amber-300 shadow-xs capitalize flex items-center gap-1.5">
          <span>{{ topicMeta.emoji }}</span>
          <span>{{ topic }}</span>
        </span>
      </div>
    </div>

    <!-- Hero Card with MGSE Badge & Title -->
    <div class="bg-white rounded-3xl p-6 sm:p-8 border-2 border-slate-200 shadow-game space-y-4 relative overflow-hidden">
      <!-- Decorative background glow -->
      <div class="absolute -right-16 -top-16 w-56 h-56 bg-gradient-to-br from-indigo-100 to-amber-100 rounded-full blur-3xl opacity-60 pointer-events-none"></div>

      <!-- Aligned to MGSE Badge with Snippet -->
      <div class="flex items-start sm:items-center gap-2.5 flex-wrap">
        <div class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs sm:text-sm font-extrabold bg-gradient-to-r from-indigo-600 to-indigo-800 text-white shadow-sm shrink-0">
          <span>🏛️</span>
          <span>Aligned to {{ currentStandardCode }}</span>
        </div>
        <p v-if="currentStandardSnippet" class="text-xs sm:text-sm font-semibold text-slate-600 max-w-2xl">
          {{ currentStandardSnippet }}
        </p>
      </div>

      <!-- Main Title -->
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-6 pt-2">
        <div class="space-y-2">
          <h1 class="text-3xl sm:text-4xl font-black text-slate-800 tracking-tight flex items-center gap-3">
            <span>{{ topicMeta.emoji }}</span>
            <span>{{ explanation?.title || topicMeta.title }}</span>
          </h1>
          <p class="text-slate-600 text-base sm:text-lg max-w-3xl leading-relaxed">
            {{ explanation?.intro || topicMeta.subtitle }}
          </p>
        </div>

        <!-- Quick Start Practice CTA -->
        <button
          type="button"
          @click="startQuest"
          :disabled="isLaunchingRound"
          class="btn-game-green px-7 py-4 text-base font-black shadow-game-green whitespace-nowrap self-start md:self-center shrink-0 cursor-pointer hover:scale-105 transition-transform"
        >
          <span v-if="isLaunchingRound" class="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></span>
          <span v-else class="mr-2">⚔️</span>
          <span>{{ isLaunchingRound ? 'Summoning...' : 'Start Practice' }}</span>
        </button>
      </div>

      <!-- "Explain Differently" Button Group -->
      <div class="pt-4 border-t border-slate-100 space-y-2.5">
        <div class="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-slate-500">
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
              'px-4 py-3 rounded-2xl text-xs sm:text-sm font-black transition-all flex items-center justify-center gap-2 border-2 text-center cursor-pointer',
              selectedStyle === btn.id
                ? 'bg-amber-400 text-slate-900 border-slate-900 shadow-game-amber scale-[1.02]'
                : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100 hover:border-slate-300'
            ]"
          >
            <span>{{ btn.icon }}</span>
            <span>{{ btn.label }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Cold Start Wakeup Notice -->
    <div v-if="isServerWakingUp" class="p-4 rounded-2xl bg-amber-50 border-2 border-amber-300 text-amber-900 text-sm font-bold flex items-center gap-3 animate-pulse">
      <span class="text-xl">🚀</span>
      <span>{{ wakeUpNotice || 'Waking up the server for your explanation...' }}</span>
    </div>

    <!-- Section: 6-Slide Interactive Video Player Masterclass -->
    <div class="space-y-3">
      <div class="flex items-center justify-between flex-wrap gap-2">
        <h2 class="text-2xl font-black text-slate-800 flex items-center gap-2.5">
          <span class="inline-flex items-center justify-center w-8 h-8 rounded-2xl bg-amber-400 text-slate-950 text-lg shadow-sm">
            🎬
          </span>
          <span>Interactive 6-Slide Video Lesson</span>
        </h2>
        <span class="text-xs font-bold text-slate-500 bg-white px-3 py-1.5 rounded-full border border-slate-200">
          🎙️ Web Speech Narration & Live Subtitles
        </span>
      </div>

      <!-- Loading Skeleton for Video Player -->
      <div
        v-if="isLoadingScript"
        class="w-full bg-slate-900 rounded-3xl p-12 flex flex-col items-center justify-center space-y-4 animate-pulse min-h-[380px] border-4 border-slate-800"
      >
        <div class="w-12 h-12 border-4 border-amber-400 border-t-transparent rounded-full animate-spin"></div>
        <p class="text-slate-400 font-bold text-sm">Preparing your 6-slide video lesson...</p>
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

    <!-- Main Content Layout: Explanation Text beside Infographic -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start pt-4">
      <!-- Left Column: Explanation Details (Col span 7) -->
      <div class="lg:col-span-7 space-y-6">
        <!-- Loading Skeleton for Explanation Change -->
        <div v-if="isLoadingStyle" class="bg-white rounded-3xl p-8 border-2 border-slate-200 shadow-game space-y-6 animate-pulse">
          <div class="h-6 bg-slate-200 rounded-full w-2/3"></div>
          <div class="space-y-2">
            <div class="h-4 bg-slate-100 rounded-full w-full"></div>
            <div class="h-4 bg-slate-100 rounded-full w-5/6"></div>
          </div>
          <div class="h-32 bg-slate-100 rounded-2xl"></div>
        </div>

        <template v-else>
          <!-- Key Ideas Card -->
          <div class="bg-white rounded-3xl p-6 sm:p-7 border-2 border-slate-200 shadow-game space-y-4">
            <h2 class="text-xl font-black text-slate-800 flex items-center gap-2.5">
              <span class="inline-flex items-center justify-center w-7 h-7 rounded-xl bg-indigo-100 text-indigo-700 text-base">🔑</span>
              <span>Key Ideas to Remember</span>
            </h2>

            <ul class="space-y-3">
              <li
                v-for="(idea, idx) in currentKeyIdeas"
                :key="idx"
                class="flex items-start gap-3 text-sm sm:text-base text-slate-700 font-medium leading-relaxed"
              >
                <span class="inline-flex items-center justify-center w-5 h-5 rounded-full bg-indigo-600 text-white text-xs font-bold shrink-0 mt-0.5">
                  {{ idx + 1 }}
                </span>
                <span>{{ idea }}</span>
              </li>
            </ul>
          </div>

          <!-- Worked Examples (Rule 1 Verified Math) -->
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <h2 class="text-xl font-black text-slate-800 flex items-center gap-2.5">
                <span class="inline-flex items-center justify-center w-7 h-7 rounded-xl bg-emerald-100 text-emerald-700 text-base">📝</span>
                <span>Worked Examples (Verified Solutions)</span>
              </h2>
              <span class="text-xs font-extrabold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200">
                100% Math Verified
              </span>
            </div>

            <!-- Example Cards -->
            <div
              v-for="(example, idx) in currentWorkedExamples"
              :key="idx"
              class="bg-white rounded-3xl p-6 sm:p-7 border-2 border-slate-200 shadow-game space-y-4"
            >
              <div class="flex items-center justify-between flex-wrap gap-2">
                <span class="px-3 py-1 rounded-full text-xs font-extrabold bg-emerald-100 text-emerald-900 border border-emerald-300">
                  Example #{{ idx + 1 }}
                </span>
                <span class="font-mono text-xs font-bold text-slate-500 bg-slate-100 px-2.5 py-0.5 rounded-lg border border-slate-200">
                  Problem: {{ example.expression }}
                </span>
              </div>

              <!-- Problem Narrative -->
              <p class="text-base font-bold text-slate-800 leading-snug">
                {{ example.problem }}
              </p>

              <!-- Step-by-Step Breakdown -->
              <div class="bg-slate-50 rounded-2xl p-4 border border-slate-200 space-y-2">
                <p class="text-xs font-bold uppercase tracking-wider text-slate-500">
                  Solution Walkthrough:
                </p>
                <ul class="space-y-1.5">
                  <li
                    v-for="(step, sIdx) in example.steps"
                    :key="sIdx"
                    class="text-xs sm:text-sm text-slate-700 flex items-start gap-2"
                  >
                    <span class="text-indigo-500 font-bold shrink-0">•</span>
                    <span>{{ step }}</span>
                  </li>
                </ul>
              </div>

              <!-- Verified Final Answer Banner -->
              <div class="flex items-center justify-between bg-emerald-50 border-2 border-emerald-200 rounded-2xl px-4 py-2.5 text-emerald-950">
                <div class="flex items-center gap-2">
                  <span class="text-base">✅</span>
                  <span class="text-xs sm:text-sm font-bold">Verified Final Answer:</span>
                </div>
                <span class="font-black text-base sm:text-lg text-emerald-800 font-mono bg-white px-3 py-0.5 rounded-xl border border-emerald-300 shadow-xs">
                  {{ example.verified_answer }}
                </span>
              </div>
            </div>
          </div>

          <!-- Common Mistakes Card -->
          <div class="bg-rose-50 rounded-3xl p-6 sm:p-7 border-2 border-rose-200 shadow-sm space-y-4">
            <h2 class="text-lg font-black text-rose-900 flex items-center gap-2">
              <span>⚠️</span>
              <span>Common Mistakes & Traps to Avoid</span>
            </h2>
            <ul class="space-y-2.5">
              <li
                v-for="(mistake, idx) in currentCommonMistakes"
                :key="idx"
                class="flex items-start gap-2.5 text-xs sm:text-sm text-rose-950 font-medium leading-relaxed"
              >
                <span class="text-base shrink-0 mt-0.5">🚫</span>
                <span>{{ mistake }}</span>
              </li>
            </ul>
          </div>
        </template>
      </div>

      <!-- Right Column: Educational Infographic beside the text (Col span 5) -->
      <div class="lg:col-span-5 space-y-6 lg:sticky lg:top-6">
        <div class="bg-white rounded-3xl p-6 border-2 border-slate-200 shadow-game space-y-4">
          <div class="flex items-center justify-between">
            <h2 class="text-lg font-black text-slate-800 flex items-center gap-2">
              <span>🖼️</span>
              <span>Topic Infographic</span>
            </h2>
            <span
              :class="[
                'text-xs font-extrabold px-2.5 py-1 rounded-full border',
                usingFallbackImage
                  ? 'bg-slate-100 text-slate-700 border-slate-300'
                  : 'bg-purple-50 text-purple-700 border-purple-200'
              ]"
            >
              {{ usingFallbackImage ? 'Vector Guide' : 'AI Illustrated' }}
            </span>
          </div>

          <!-- Infographic Image Frame with SVG Fallback -->
          <div class="bg-slate-50 rounded-2xl p-3 border-2 border-slate-100 flex flex-col items-center justify-center overflow-hidden min-h-[300px] relative">
            <!-- Loading Indicator for Image -->
            <div v-if="isImageLoading" class="absolute inset-0 bg-slate-50 flex items-center justify-center z-10">
              <div class="flex flex-col items-center gap-2">
                <div class="w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
                <span class="text-xs font-bold text-slate-500">Painting infographic...</span>
              </div>
            </div>

            <img
              :src="infographicSrc"
              :alt="`${topic} Educational Infographic`"
              @load="onImageLoad"
              @error="onImageError"
              class="max-w-full h-auto rounded-xl shadow-sm transition-transform hover:scale-105 duration-300 object-contain"
            />
          </div>

          <!-- Infographic Caption & Prompt Snippet -->
          <div class="text-xs text-slate-500 font-medium text-center space-y-1">
            <p v-if="!usingFallbackImage" class="text-purple-600 font-bold">
              ✨ Generated live via Pollinations AI
            </p>
            <p v-else class="text-slate-500">
              📐 High-clarity geometric vector diagram
            </p>
          </div>

          <!-- Bottom Action Card inside Infographic Card -->
          <div class="pt-3 border-t border-slate-100 space-y-3 text-center">
            <h3 class="text-sm font-black text-slate-800">
              Ready to test your mastery?
            </h3>
            <button
              type="button"
              @click="startQuest"
              :disabled="isLaunchingRound"
              class="btn-game-amber w-full py-3.5 text-base font-black shadow-game-amber cursor-pointer flex items-center justify-center gap-2"
            >
              <span v-if="isLaunchingRound" class="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
              <span v-else>⚔️</span>
              <span>{{ isLaunchingRound ? 'Summoning Arena...' : 'Start Practice' }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  useApi,
  type ExplainResponse,
  type ExplainStyle,
  type WorkedExample,
  type ScriptResponse,
} from '~/composables/useApi'
import { useSessionStore, type GradeLevel, type TopicType } from '~/stores/session'
import VideoPlayer from '~/components/VideoPlayer.vue'

const route = useRoute()
const router = useRouter()
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
  if (['fractions', 'decimals', 'ratios', 'geometry'].includes(t)) {
    return t as TopicType
  }
  return 'fractions'
})

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
    const res = await fetchRoundBatch(grade.value, topic.value, sessionStore.tier, 10)
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
