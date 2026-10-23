<template>
  <div class="space-y-8 animate-pop">
    <!-- Hero Banner -->
    <div class="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-500 rounded-3xl p-6 sm:p-10 text-white shadow-game-purple relative overflow-hidden">
      <div class="absolute -right-6 -bottom-8 opacity-20 text-9xl select-none pointer-events-none">
        📐
      </div>
      <div class="max-w-2xl relative z-10 space-y-3">
        <div class="inline-flex items-center gap-2 bg-white/20 backdrop-blur-md px-3.5 py-1.5 rounded-full text-xs sm:text-sm font-bold uppercase tracking-wider">
          <span>🇬🇪</span>
          <span>Georgia Standards of Excellence (MGSE)</span>
        </div>
        <h1 class="text-3xl sm:text-5xl font-extrabold tracking-tight">
          Choose Your Math Quest!
        </h1>
        <p class="text-white/90 text-sm sm:text-lg">
          Master real math with smart feedback, earn XP points, and unlock heroic badges in Grade 5 and 6.
        </p>
      </div>
    </div>

    <!-- Grade Selection Tabs -->
    <div class="space-y-3">
      <h2 class="text-lg font-bold text-slate-900 flex items-center gap-2">
        <span aria-hidden="true">🎒</span>
        <span>Select Your Grade Level</span>
      </h2>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4" role="tablist" aria-label="Grade level selection">
        <!-- Grade 5 Tab -->
        <button
          type="button"
          role="tab"
          :aria-selected="sessionStore.grade === 5"
          aria-label="Grade 5 Quest: Unlike denominators, decimal place values, line plots, and 2D area"
          @click="selectGrade(5)"
          :class="[
            'p-5 rounded-3xl border-4 text-left transition-all duration-200 cursor-pointer flex items-center justify-between focus:outline-none focus-visible:ring-4 focus-visible:ring-indigo-400 focus-visible:ring-offset-2',
            sessionStore.grade === 5
              ? 'bg-indigo-50 border-indigo-600 shadow-game-blue translate-y-0'
              : 'bg-white border-slate-300 hover:border-slate-400 shadow-sm opacity-90 hover:opacity-100'
          ]"
        >
          <div class="space-y-1">
            <div class="flex items-center gap-2">
              <span class="text-2xl" aria-hidden="true">🌱</span>
              <span class="text-2xl font-black text-slate-900">Grade 5 Quest</span>
              <span
                v-if="sessionStore.grade === 5"
                class="bg-indigo-600 text-white text-xs px-2.5 py-0.5 rounded-full font-bold ml-1"
              >
                Active
              </span>
            </div>
            <p class="text-xs sm:text-sm text-slate-700">
              Unlike denominators, decimal place values, line plots, and 2D area.
            </p>
          </div>
          <span class="text-3xl text-indigo-600 font-bold ml-2" aria-hidden="true">➜</span>
        </button>

        <!-- Grade 6 Tab -->
        <button
          type="button"
          role="tab"
          :aria-selected="sessionStore.grade === 6"
          aria-label="Grade 6 Quest: Ratios, unit rates, fraction division, integers, and surface area"
          @click="selectGrade(6)"
          :class="[
            'p-5 rounded-3xl border-4 text-left transition-all duration-200 cursor-pointer flex items-center justify-between focus:outline-none focus-visible:ring-4 focus-visible:ring-purple-400 focus-visible:ring-offset-2',
            sessionStore.grade === 6
              ? 'bg-purple-50 border-purple-600 shadow-game-purple translate-y-0'
              : 'bg-white border-slate-300 hover:border-slate-400 shadow-sm opacity-90 hover:opacity-100'
          ]"
        >
          <div class="space-y-1">
            <div class="flex items-center gap-2">
              <span class="text-2xl" aria-hidden="true">🚀</span>
              <span class="text-2xl font-black text-slate-900">Grade 6 Quest</span>
              <span
                v-if="sessionStore.grade === 6"
                class="bg-purple-600 text-white text-xs px-2.5 py-0.5 rounded-full font-bold ml-1"
              >
                Active
              </span>
            </div>
            <p class="text-xs sm:text-sm text-slate-700">
              Ratios, unit rates, fraction division, integers, and surface area.
            </p>
          </div>
          <span class="text-3xl text-purple-600 font-bold ml-2" aria-hidden="true">➜</span>
        </button>
      </div>
    </div>

    <!-- Topics Grid -->
    <div class="space-y-4">
      <div class="flex items-center justify-between">
        <h2 class="text-lg font-bold text-slate-800 flex items-center gap-2">
          <span>🗺️</span>
          <span>Pick a Mathematical Territory</span>
        </h2>
        <span class="text-xs text-slate-500 font-medium">Click a topic to inspect rules or jump straight into a quiz</span>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div
          v-for="t in topics"
          :key="t.id"
          class="bg-white rounded-3xl p-6 border-2 border-slate-200 shadow-game hover:shadow-game-lg transition-all duration-200 flex flex-col justify-between group"
        >
          <div>
            <!-- Card Header -->
            <div class="flex items-start justify-between gap-3 mb-4">
              <div class="flex items-center gap-3">
                <div :class="['w-14 h-14 rounded-2xl flex items-center justify-center text-3xl shadow-sm', t.iconBg]">
                  {{ t.emoji }}
                </div>
                <div>
                  <h3 class="text-2xl font-extrabold text-slate-800 group-hover:text-indigo-600 transition">
                    {{ t.name }}
                  </h3>
                  <div class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-bold bg-slate-100 text-slate-600 mt-0.5">
                    <span>📜</span>
                    <span>{{ sessionStore.grade === 5 ? t.mgseG5 : t.mgseG6 }}</span>
                  </div>
                </div>
              </div>

              <!-- Mastery Pill -->
              <div class="text-right">
                <span class="text-xs font-bold text-slate-500 block uppercase">Mastery</span>
                <span class="text-base font-extrabold text-indigo-600">
                  {{ sessionStore.mastery[t.id] || 50 }}%
                </span>
              </div>
            </div>

            <!-- Description -->
            <p class="text-sm text-slate-600 mb-4 leading-relaxed">
              {{ sessionStore.grade === 5 ? t.descG5 : t.descG6 }}
            </p>

            <!-- Mastery Progress Bar -->
            <div class="mb-6 space-y-1">
              <div class="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
                <div
                  class="h-full rounded-full transition-all duration-500"
                  :class="t.progressColor"
                  :style="{ width: `${sessionStore.mastery[t.id] || 50}%` }"
                ></div>
              </div>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="grid grid-cols-2 gap-3 pt-2">
            <NuxtLink
              :to="`/learn/${sessionStore.grade}/${t.id}`"
              :aria-label="`Open study guide and video masterclass for ${t.name}`"
              class="btn-game-white py-3 text-sm font-bold flex items-center justify-center gap-1.5 focus:outline-none focus-visible:ring-4 focus-visible:ring-slate-400 focus-visible:ring-offset-2"
            >
              <span aria-hidden="true">📖</span>
              <span>Learn Guide</span>
            </NuxtLink>

            <button
              type="button"
              @click="startQuickQuiz(t.id)"
              :disabled="isLoading"
              :aria-label="`Start math quest for ${t.name}`"
              :class="[
                'btn-game py-3 text-sm font-bold flex items-center justify-center gap-1.5 text-white focus:outline-none focus-visible:ring-4 focus-visible:ring-offset-2',
                t.btnColor
              ]"
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
            Accomplish challenges to unlock all 5 heroic badges
          </p>
        </div>
        <div class="text-sm font-bold text-indigo-600 bg-indigo-50 px-3.5 py-1.5 rounded-2xl border border-indigo-200 self-start">
          {{ sessionStore.badges.length }} of 5 Unlocked
        </div>
      </div>

      <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4">
        <div
          v-for="b in allBadges"
          :key="b.name"
          :class="[
            'p-4 rounded-2xl border-2 flex flex-col items-center text-center transition-all',
            sessionStore.badges.includes(b.name)
              ? 'bg-amber-50 border-amber-300 shadow-game-amber'
              : 'bg-slate-50 border-dashed border-slate-300 opacity-60'
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
  </div>
</template>

<script setup lang="ts">
import { useApi } from '~/composables/useApi'
import { useSessionStore, type GradeLevel, type TopicType } from '~/stores/session'

const router = useRouter()
const { fetchRoundBatch, isLoading } = useApi()
const sessionStore = useSessionStore()

const selectGrade = (g: GradeLevel) => {
  sessionStore.setGrade(g)
}

const topics = [
  {
    id: 'fractions' as TopicType,
    name: 'Fractions',
    emoji: '🍕',
    iconBg: 'bg-emerald-100 text-emerald-700',
    btnColor: 'btn-game-green',
    progressColor: 'bg-emerald-500',
    mgseG5: 'MGSE5.NF.1 / MGSE5.NF.4',
    mgseG6: 'MGSE6.NS.1',
    descG5: 'Add and subtract fractions with unlike denominators, and multiply fractions by fractions.',
    descG6: 'Divide fractions by fractions using reciprocals and solve real-world quotient scenarios.',
  },
  {
    id: 'decimals' as TopicType,
    name: 'Decimals',
    emoji: '🎯',
    iconBg: 'bg-sky-100 text-sky-700',
    btnColor: 'btn-game-blue',
    progressColor: 'bg-sky-500',
    mgseG5: 'MGSE5.NBT.7',
    mgseG6: 'MGSE6.NS.3',
    descG5: 'Add, subtract, and multiply decimals to hundredths using place-value models.',
    descG6: 'Fluently calculate with multi-digit decimals using standard algorithms with zero drop checks.',
  },
  {
    id: 'ratios' as TopicType,
    name: 'Ratios & Proportions',
    emoji: '⚖️',
    iconBg: 'bg-amber-100 text-amber-800',
    btnColor: 'btn-game-amber',
    progressColor: 'bg-amber-500',
    mgseG5: 'MGSE5.OA.3',
    mgseG6: 'MGSE6.RP.1 / MGSE6.RP.2',
    descG5: 'Generate numerical patterns, analyze rules, and understand multiplicative scale relationships.',
    descG6: 'Understand ratio concepts, scale factors, equivalent rates, and unit pricing.',
  },
  {
    id: 'geometry' as TopicType,
    name: 'Geometry & Area',
    emoji: '📐',
    iconBg: 'bg-purple-100 text-purple-700',
    btnColor: 'btn-game-purple',
    progressColor: 'bg-purple-500',
    mgseG5: 'MGSE5.MD.5',
    mgseG6: 'MGSE6.G.1',
    descG5: 'Calculate rectangular area, perimeter, and volume of rectangular prisms.',
    descG6: 'Find the area of triangles, special quadrilaterals, and composite geometric polygons.',
  },
]

const allBadges = [
  { name: 'First Steps', emoji: '👣', desc: 'Answer your very first quest question.' },
  { name: '5-Streak', emoji: '🔥', desc: 'Get 5 correct answers in a row.' },
  { name: 'Fraction Master', emoji: '🍕', desc: 'Reach 80+ mastery or 5 correct in fractions.' },
  { name: 'Comeback Kid', emoji: '⚡', desc: 'Bounce back with a correct answer after a mistake.' },
  { name: 'Perfect Round', emoji: '🌟', desc: 'Complete a full round with 100% accuracy.' },
]

const startQuickQuiz = async (topicId: TopicType) => {
  sessionStore.setTopic(topicId)
  try {
    const res = await fetchRoundBatch(sessionStore.grade, topicId, sessionStore.tier, 10)
    sessionStore.startRound(res.questions)
    router.push('/quiz')
  } catch (err) {
    console.error('Failed to load questions:', err)
  }
}
</script>
