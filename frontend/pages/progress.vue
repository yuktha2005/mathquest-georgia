<template>
  <div class="space-y-6 sm:space-y-8 animate-pop">
    <!-- Hero Banner -->
    <div class="bg-gradient-to-r from-indigo-700 via-indigo-600 to-purple-600 rounded-3xl p-6 sm:p-8 text-white shadow-lg flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
      <div>
        <div class="flex items-center gap-2 mb-2">
          <span class="px-2.5 py-0.5 rounded-full text-xs font-black uppercase tracking-wider bg-white/20 text-white backdrop-blur-sm">
            Diagnostic Analytics
          </span>
          <span class="text-xs text-indigo-200 font-bold">
            Grade {{ sessionStore.grade }} • {{ sessionStore.boardTitle }}
          </span>
        </div>
        <h1 class="text-2xl sm:text-4xl font-black tracking-tight">
          Mastery & Learning Progress 📊
        </h1>
        <p class="text-indigo-100 text-xs sm:text-sm mt-1 max-w-xl">
          Track your mathematical growth across curriculum domains, monitor question accuracy trends, and analyze misconception patterns.
        </p>
      </div>

      <div class="flex items-center gap-3 w-full md:w-auto">
        <NuxtLink
          to="/quiz"
          class="flex-1 md:flex-initial px-5 py-3 rounded-2xl bg-amber-400 hover:bg-amber-300 text-slate-900 font-black text-xs sm:text-sm text-center shadow-md hover:shadow-lg transition active:scale-95 border-b-4 border-amber-600"
        >
          Start Practice Quiz ⚔️
        </NuxtLink>
        <NuxtLink
          to="/dashboard"
          class="px-4 py-3 rounded-2xl bg-white/10 hover:bg-white/20 text-white font-extrabold text-xs sm:text-sm transition backdrop-blur-sm border border-white/20"
        >
          Dashboard 🏠
        </NuxtLink>
      </div>
    </div>

    <!-- Row 1: Mastery Radar Chart & Accuracy Trend Line Chart -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- 1. Mastery Radar by Topic -->
      <div class="bg-white rounded-3xl border-2 border-slate-200 shadow-sm p-6 sm:p-7 flex flex-col justify-between">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h2 class="text-lg sm:text-xl font-black text-slate-900 flex items-center gap-2">
              <span>🕸️</span>
              <span>Topic Mastery Radar</span>
            </h2>
            <p class="text-xs text-slate-500 font-medium">
              Multi-axis proficiency map (0% center to 100% edge)
            </p>
          </div>
          <span class="text-xs font-black px-2.5 py-1 rounded-xl bg-indigo-50 text-indigo-700 border border-indigo-200">
            Avg: {{ averageMastery }}%
          </span>
        </div>

        <!-- Radar Chart SVG Container -->
        <div class="relative w-full aspect-square max-w-[340px] mx-auto flex items-center justify-center my-2">
          <svg class="w-full h-full overflow-visible" viewBox="0 0 320 320">
            <!-- Background Concentric Circles / Polygons (25%, 50%, 75%, 100%) -->
            <polygon
              v-for="level in [0.25, 0.5, 0.75, 1.0]"
              :key="level"
              :points="getConcentricPoints(level)"
              fill="transparent"
              stroke="#E2E8F0"
              :stroke-dasharray="level === 1.0 ? 'none' : '3 3'"
              stroke-width="1.5"
            />

            <!-- Radial Axis Lines -->
            <line
              v-for="(axis, idx) in radarAxes"
              :key="idx"
              x1="160"
              y1="160"
              :x2="axis.edgeX"
              :y2="axis.edgeY"
              stroke="#E2E8F0"
              stroke-width="1.5"
            />

            <!-- Data Polygon Area (Filled) -->
            <polygon
              :points="radarDataPointsString"
              fill="rgba(99, 102, 241, 0.25)"
              stroke="#4F46E5"
              stroke-width="3"
              stroke-linejoin="round"
              class="transition-all duration-700 ease-out"
            />

            <!-- Data Vertices Dots -->
            <circle
              v-for="(pt, idx) in radarDataCoords"
              :key="'pt-' + idx"
              :cx="pt.x"
              :cy="pt.y"
              r="5"
              fill="#4F46E5"
              stroke="#FFFFFF"
              stroke-width="2"
              class="transition-all duration-700 ease-out hover:r-7 cursor-pointer"
            >
              <title>{{ pt.label }}: {{ pt.score }}% Mastery</title>
            </circle>

            <!-- Axis Labels around perimeter -->
            <text
              v-for="(axis, idx) in radarAxes"
              :key="'lbl-' + idx"
              :x="axis.labelX"
              :y="axis.labelY"
              :text-anchor="axis.textAnchor"
              dominant-baseline="central"
              class="text-[11px] font-extrabold fill-slate-700 select-none"
            >
              {{ axis.icon }} {{ axis.name }} ({{ axis.score }}%)
            </text>
          </svg>
        </div>

        <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-4 border-t border-slate-100 text-center">
          <div
            v-for="topic in activeTopicList.slice(0, 4)"
            :key="topic.id"
            class="bg-slate-50 rounded-xl p-2 border border-slate-200"
          >
            <div class="text-[11px] font-bold text-slate-500 truncate">{{ topic.name }}</div>
            <div class="text-sm font-black text-indigo-700">{{ Math.round(sessionStore.mastery[topic.id] || 50) }}%</div>
          </div>
        </div>
      </div>

      <!-- 2. Accuracy Over Last 10 Sessions (Line Chart) -->
      <div class="bg-white rounded-3xl border-2 border-slate-200 shadow-sm p-6 sm:p-7 flex flex-col justify-between">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h2 class="text-lg sm:text-xl font-black text-slate-900 flex items-center gap-2">
              <span>📈</span>
              <span>Recent Accuracy Trend</span>
            </h2>
            <p class="text-xs text-slate-500 font-medium">
              Diagnostic accuracy across your last 10 practice quests
            </p>
          </div>
          <span
            v-if="trendAccuracy !== null"
            class="text-xs font-black px-2.5 py-1 rounded-xl"
            :class="trendAccuracy >= 70 ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-amber-50 text-amber-800 border border-amber-200'"
          >
            Recent: {{ trendAccuracy }}%
          </span>
        </div>

        <!-- Line Chart SVG when sessions exist -->
        <div v-if="lineChartPoints.length > 0" class="w-full flex-1 flex flex-col justify-center my-2">
          <div class="relative w-full h-52 sm:h-56">
            <svg class="w-full h-full overflow-visible" viewBox="0 0 440 200">
              <!-- Y-Axis Grid Lines & Labels -->
              <g class="text-[10px] fill-slate-400 font-bold">
                <line x1="40" y1="20" x2="420" y2="20" stroke="#F1F5F9" stroke-width="1.5" />
                <text x="32" y="24" text-anchor="end">100%</text>

                <line x1="40" y1="60" x2="420" y2="60" stroke="#F1F5F9" stroke-width="1.5" />
                <text x="32" y="64" text-anchor="end">75%</text>

                <line x1="40" y1="100" x2="420" y2="100" stroke="#F1F5F9" stroke-width="1.5" />
                <text x="32" y="104" text-anchor="end">50%</text>

                <line x1="40" y1="140" x2="420" y2="140" stroke="#F1F5F9" stroke-width="1.5" />
                <text x="32" y="144" text-anchor="end">25%</text>

                <line x1="40" y1="180" x2="420" y2="180" stroke="#E2E8F0" stroke-width="1.5" />
                <text x="32" y="184" text-anchor="end">0%</text>
              </g>

              <!-- Filled Area Under Curve -->
              <path
                :d="lineChartAreaPath"
                fill="url(#accuracyGradient)"
                class="transition-all duration-700 ease-out"
              />

              <!-- Linear Gradient Definition -->
              <defs>
                <linearGradient id="accuracyGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stop-color="#10B981" stop-opacity="0.35" />
                  <stop offset="100%" stop-color="#10B981" stop-opacity="0.0" />
                </linearGradient>
              </defs>

              <!-- Line Path -->
              <path
                :d="lineChartLinePath"
                fill="none"
                stroke="#10B981"
                stroke-width="3.5"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="transition-all duration-700 ease-out"
              />

              <!-- Data Points (Circles) -->
              <g v-for="(pt, idx) in lineChartPoints" :key="'dot-' + idx">
                <circle
                  :cx="pt.x"
                  :cy="pt.y"
                  r="5"
                  fill="#10B981"
                  stroke="#FFFFFF"
                  stroke-width="2.5"
                  class="cursor-pointer hover:r-7 transition-all"
                >
                  <title>Session {{ idx + 1 }} ({{ pt.topic }}): {{ pt.accuracy }}% Accuracy</title>
                </circle>
                <!-- Label on top of point -->
                <text
                  :x="pt.x"
                  :y="pt.y - 9"
                  text-anchor="middle"
                  class="text-[9px] font-black fill-slate-700"
                >
                  {{ pt.accuracy }}%
                </text>
                <!-- Session index label below axis -->
                <text
                  :x="pt.x"
                  y="195"
                  text-anchor="middle"
                  class="text-[9px] font-bold fill-slate-400"
                >
                  #{{ idx + 1 }}
                </text>
              </g>
            </svg>
          </div>

          <div class="flex items-center justify-between text-xs text-slate-500 font-bold px-2 pt-2 border-t border-slate-100 mt-2">
            <span>Earliest Round</span>
            <span>Latest Round</span>
          </div>
        </div>

        <!-- Empty State for Line Chart -->
        <div v-else class="text-center py-12 bg-slate-50 rounded-2xl border-2 border-dashed border-slate-200 my-auto">
          <span class="text-4xl block mb-2" aria-hidden="true">📈</span>
          <h3 class="text-sm font-extrabold text-slate-800">No session trend line yet</h3>
          <p class="text-xs text-slate-500 max-w-xs mx-auto mt-1 mb-4">
            Complete your first 10-question practice round to start tracking your accuracy curve!
          </p>
          <NuxtLink
            to="/quiz"
            class="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-extrabold text-xs transition shadow"
          >
            <span>Play First Quest 🎯</span>
          </NuxtLink>
        </div>

        <div class="pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-600 font-medium">
          <span>Target benchmark: <strong class="text-emerald-700">80%+ accuracy</strong></span>
          <span>Goal: Level up from Medium to Hard</span>
        </div>
      </div>
    </div>

    <!-- Row 2: Most Common Misconception Diagnostic Card -->
    <div class="bg-white rounded-3xl border-2 border-slate-200 shadow-sm p-6 sm:p-8">
      <div class="flex items-center justify-between mb-4 flex-wrap gap-2">
        <div>
          <h2 class="text-xl sm:text-2xl font-extrabold text-slate-900 flex items-center gap-2">
            <span>🧠</span>
            <span>Diagnostic Misconception Analysis</span>
          </h2>
          <p class="text-xs sm:text-sm text-slate-600">
            Automated pedagogical diagnosis pinpointing common error traps
          </p>
        </div>
        <span class="text-xs font-black px-3 py-1 rounded-full bg-rose-50 text-rose-700 border border-rose-200">
          Curriculum Pedagogy
        </span>
      </div>

      <!-- Identified Common Misconception -->
      <div
        v-if="topMisconception"
        class="bg-gradient-to-r from-rose-50 via-amber-50 to-orange-50 border-2 border-rose-300 rounded-2xl p-5 sm:p-6"
      >
        <div class="flex items-start gap-4">
          <div class="w-12 h-12 rounded-2xl bg-rose-100 text-rose-700 flex items-center justify-center text-2xl font-black shrink-0">
            ⚠️
          </div>
          <div class="space-y-2 flex-1">
            <div class="flex items-center gap-2 flex-wrap">
              <span class="text-xs font-black uppercase text-rose-800 tracking-wider">
                Most Frequent Conceptual Trap
              </span>
              <span class="bg-rose-200 text-rose-900 text-xs font-bold px-2 py-0.5 rounded">
                Domain: {{ topMisconception.domain }}
              </span>
            </div>
            <h3 class="text-lg sm:text-xl font-black text-slate-900">
              {{ topMisconception.title }}
            </h3>
            <p class="text-xs sm:text-sm text-slate-700 font-medium leading-relaxed">
              {{ topMisconception.explanation }}
            </p>
            <div class="pt-2 flex items-center gap-3">
              <NuxtLink
                :to="topMisconception.practiceLink"
                class="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-extrabold text-xs transition shadow"
              >
                Targeted Practice on This Trap ⚔️
              </NuxtLink>
              <NuxtLink
                :to="topMisconception.lessonLink"
                class="px-4 py-2 rounded-xl bg-white text-slate-700 hover:bg-slate-100 border border-slate-300 font-bold text-xs transition"
              >
                Review Lesson 📖
              </NuxtLink>
            </div>
          </div>
        </div>
      </div>

      <!-- No Misconceptions Detected State -->
      <div
        v-else
        class="bg-gradient-to-r from-emerald-50 via-teal-50 to-blue-50 border-2 border-emerald-300 rounded-2xl p-5 sm:p-6"
      >
        <div class="flex items-start gap-4">
          <div class="w-12 h-12 rounded-2xl bg-emerald-100 text-emerald-800 flex items-center justify-center text-2xl font-black shrink-0">
            🌟
          </div>
          <div class="space-y-1.5 flex-1">
            <h3 class="text-base sm:text-lg font-black text-emerald-950">
              Zero Conceptual Traps Detected!
            </h3>
            <p class="text-xs sm:text-sm text-emerald-900 leading-relaxed">
              Your recent answers demonstrate clear conceptual understanding across operation rules, common denominators, and shape formulas. Keep tackling Medium and Hard questions to maintain sharp reasoning!
            </p>
          </div>
        </div>
      </div>

      <!-- Key Curriculum Traps Reference Grid -->
      <div class="mt-6 pt-5 border-t border-slate-200">
        <h4 class="text-xs font-extrabold uppercase text-slate-500 tracking-wider mb-3">
          Curriculum Diagnostic Pitfalls Monitored by MathQuest
        </h4>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div class="p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs">
            <span class="font-bold text-slate-900 block mb-0.5">🍰 Fractions: Adding Across</span>
            <span class="text-slate-600">Adding numerators and denominators directly instead of finding the LCM common denominator.</span>
          </div>
          <div class="p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs">
            <span class="font-bold text-slate-900 block mb-0.5">🎯 Decimals: Right-Alignment</span>
            <span class="text-slate-600">Treating decimals like whole numbers and aligning digits to the right rather than by decimal place.</span>
          </div>
          <div class="p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs">
            <span class="font-bold text-slate-900 block mb-0.5">📐 Geometry: Perimeter vs Area</span>
            <span class="text-slate-600">Confusing boundary perimeter sum with interior square area, or omitting the ½ in triangle area.</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Row 3: Badge Gallery (Earned vs Locked with Unlock Conditions) -->
    <div class="bg-white rounded-3xl border-2 border-slate-200 shadow-sm p-6 sm:p-8">
      <div class="flex items-center justify-between mb-5 flex-wrap gap-3">
        <div>
          <h2 class="text-xl sm:text-2xl font-extrabold text-slate-900 flex items-center gap-2">
            <span>🏆</span>
            <span>Badge & Trophy Gallery</span>
          </h2>
          <p class="text-xs sm:text-sm text-slate-600">
            Every badge in the MathQuest universe: earned achievements and how to unlock the rest
          </p>
        </div>

        <!-- Filter Tabs -->
        <div class="flex items-center gap-1 bg-slate-100 p-1 rounded-2xl border border-slate-200 text-xs font-bold">
          <button
            type="button"
            @click="badgeFilter = 'all'"
            class="px-3 py-1.5 rounded-xl transition"
            :class="badgeFilter === 'all' ? 'bg-white text-indigo-700 shadow-sm font-extrabold' : 'text-slate-600 hover:text-slate-900'"
          >
            All ({{ BADGE_CATALOG.length }})
          </button>
          <button
            type="button"
            @click="badgeFilter = 'earned'"
            class="px-3 py-1.5 rounded-xl transition"
            :class="badgeFilter === 'earned' ? 'bg-white text-indigo-700 shadow-sm font-extrabold' : 'text-slate-600 hover:text-slate-900'"
          >
            Earned ({{ earnedBadgesCount }})
          </button>
          <button
            type="button"
            @click="badgeFilter = 'locked'"
            class="px-3 py-1.5 rounded-xl transition"
            :class="badgeFilter === 'locked' ? 'bg-white text-indigo-700 shadow-sm font-extrabold' : 'text-slate-600 hover:text-slate-900'"
          >
            Locked ({{ lockedBadgesCount }})
          </button>
        </div>
      </div>

      <!-- Badge Cards Grid -->
      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        <div
          v-for="badge in filteredBadges"
          :key="badge.id"
          class="rounded-2xl p-4 transition-all duration-200 flex flex-col justify-between border-2"
          :class="isBadgeEarned(badge.name)
            ? 'bg-amber-50/80 border-amber-300 shadow-sm hover:shadow'
            : 'bg-slate-50/70 border-slate-200 opacity-75 hover:opacity-95'"
        >
          <div>
            <div class="flex items-center justify-between mb-2">
              <span class="text-3xl" :class="{ 'grayscale': !isBadgeEarned(badge.name) }">
                {{ badge.emoji }}
              </span>
              <span
                class="text-[10px] font-black uppercase px-2 py-0.5 rounded-full"
                :class="isBadgeEarned(badge.name)
                  ? 'bg-amber-200 text-amber-900'
                  : 'bg-slate-200 text-slate-600'"
              >
                {{ isBadgeEarned(badge.name) ? 'Earned 🏆' : 'Locked 🔒' }}
              </span>
            </div>

            <h3 class="font-black text-sm text-slate-900 leading-tight mb-1">
              {{ badge.name }}
            </h3>
            <p class="text-xs text-slate-600 font-medium leading-snug">
              {{ badge.condition }}
            </p>
          </div>

          <div class="mt-3 pt-2 border-t text-[11px] font-bold" :class="isBadgeEarned(badge.name) ? 'border-amber-200 text-amber-800' : 'border-slate-200 text-slate-400'">
            {{ isBadgeEarned(badge.name) ? 'Unlocked in your trophy case' : 'How to unlock: ' + badge.hint }}
          </div>
        </div>
      </div>
    </div>

    <!-- Row 4: Session History Table -->
    <div class="bg-white rounded-3xl border-2 border-slate-200 shadow-sm p-6 sm:p-8">
      <div class="flex items-center justify-between mb-5 flex-wrap gap-2">
        <div>
          <h2 class="text-xl sm:text-2xl font-extrabold text-slate-900 flex items-center gap-2">
            <span>📜</span>
            <span>Comprehensive Session History</span>
          </h2>
          <p class="text-xs sm:text-sm text-slate-600">
            Historical log of all completed practice rounds, diagnostic scores, and curriculum tiers
          </p>
        </div>
        <span class="text-xs font-bold text-slate-500 bg-slate-100 px-3 py-1 rounded-full">
          {{ sessionStore.recentActivities.length }} Sessions Completed
        </span>
      </div>

      <!-- History Table Container -->
      <div v-if="sessionStore.recentActivities.length > 0" class="overflow-x-auto">
        <table class="w-full text-left border-collapse text-xs sm:text-sm">
          <thead>
            <tr class="border-b-2 border-slate-200 text-slate-500 uppercase text-[11px] font-black tracking-wider">
              <th class="py-3 px-3">Date & Time</th>
              <th class="py-3 px-3">Topic</th>
              <th class="py-3 px-3">Tier</th>
              <th class="py-3 px-3">Accuracy</th>
              <th class="py-3 px-3">Correct / Total</th>
              <th class="py-3 px-3">XP Earned</th>
              <th class="py-3 px-3 text-right">Standard</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 font-medium text-slate-800">
            <tr
              v-for="(session, idx) in sessionStore.recentActivities"
              :key="session.id || idx"
              class="hover:bg-slate-50 transition"
            >
              <!-- Date -->
              <td class="py-3.5 px-3 font-semibold text-slate-600 whitespace-nowrap">
                {{ formatFullDate(session.created_at) }}
              </td>

              <!-- Topic -->
              <td class="py-3.5 px-3 whitespace-nowrap">
                <span class="font-extrabold text-slate-900 flex items-center gap-1.5">
                  <span>{{ getTopicMeta(session.topic).icon }}</span>
                  <span>{{ getTopicMeta(session.topic).name }}</span>
                </span>
              </td>

              <!-- Tier -->
              <td class="py-3.5 px-3">
                <span
                  class="px-2 py-0.5 rounded text-[10px] font-black uppercase border"
                  :class="getTierBadgeClass(session.tier)"
                >
                  {{ session.tier }}
                </span>
              </td>

              <!-- Accuracy -->
              <td class="py-3.5 px-3">
                <span
                  class="px-2.5 py-0.5 rounded-full text-xs font-black border"
                  :class="getAccuracyBadgeClass(session.accuracy_percent)"
                >
                  {{ session.accuracy_percent }}%
                </span>
              </td>

              <!-- Correct / Total -->
              <td class="py-3.5 px-3 font-bold text-slate-700">
                {{ session.correct_count }} / {{ session.total_questions }}
              </td>

              <!-- XP Earned -->
              <td class="py-3.5 px-3">
                <span class="font-black text-amber-600 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
                  +{{ session.score }} XP
                </span>
              </td>

              <!-- Standard -->
              <td class="py-3.5 px-3 text-right font-mono text-xs text-slate-500 whitespace-nowrap">
                {{ session.board === 'cbse' ? 'CBSE G6' : `MGSE G${session.grade}` }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Empty History Table State -->
      <div v-else class="text-center py-12 bg-slate-50 rounded-2xl border-2 border-dashed border-slate-200">
        <span class="text-4xl block mb-2" aria-hidden="true">📜</span>
        <h3 class="text-base font-extrabold text-slate-800">No session history yet</h3>
        <p class="text-xs text-slate-500 max-w-sm mx-auto mt-1 mb-4">
          Start your math journey! When you complete practice rounds, each session's accuracy and diagnostic outcomes will be archived here.
        </p>
        <NuxtLink
          to="/quiz"
          class="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-extrabold text-xs transition shadow"
        >
          <span>Take a 10-Question Quiz ⚔️</span>
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useSessionStore } from '~/stores/session'

const sessionStore = useSessionStore()
const badgeFilter = ref<'all' | 'earned' | 'locked'>('all')

onMounted(() => {
  sessionStore.loadFromStorage()
})

// Complete Badge Catalog with Unlock Conditions
const BADGE_CATALOG = [
  { id: 'first_steps', name: 'First Steps', emoji: '👣', condition: 'Answer your first math question', hint: 'Play any practice question' },
  { id: '5_streak', name: '5-Streak', emoji: '🔥', condition: '5 correct answers in a row', hint: 'Maintain accuracy across 5 questions' },
  { id: 'fraction_master', name: 'Fraction Master', emoji: '🍰', condition: 'Reach 80%+ mastery in Fractions', hint: 'Score 80%+ on unlike fractions & division' },
  { id: 'decimal_dynamo', name: 'Decimal Dynamo', emoji: '🎯', condition: 'Reach 80%+ mastery in Decimals', hint: 'Score 80%+ on decimal place value & operations' },
  { id: 'ratio_ranger', name: 'Ratio Ranger', emoji: '⚖️', condition: 'Reach 80%+ mastery in Ratios & Proportions', hint: 'Score 80%+ on unit rates & proportions' },
  { id: 'geometry_giant', name: 'Geometry Giant', emoji: '📐', condition: 'Reach 80%+ mastery in Geometry', hint: 'Score 80%+ on area, surface area, and shapes' },
  { id: 'cbse_champion', name: 'CBSE Champion', emoji: '🇮🇳', condition: 'Reach 80%+ mastery in CBSE Mathematics', hint: 'Complete Class 6 NCERT modules' },
  { id: 'tenacious_thinker', name: 'Tenacious Thinker', emoji: '🧠', condition: 'Solve a Hard-tier challenge correctly', hint: 'Advance to Hard tier and answer correctly' },
  { id: 'comeback_kid', name: 'Comeback Kid', emoji: '⚡', condition: 'Recover with a correct answer immediately after an error', hint: 'Keep going after making a mistake' },
  { id: 'perfect_round', name: 'Perfect Round', emoji: '🌟', condition: 'Complete a full 10-question round with 100% accuracy', hint: 'Get all 10 questions right in one quest' },
]

function isBadgeEarned(badgeName: string): boolean {
  return sessionStore.badges.includes(badgeName)
}

const earnedBadgesCount = computed(() => {
  return BADGE_CATALOG.filter((b) => isBadgeEarned(b.name)).length
})

const lockedBadgesCount = computed(() => {
  return BADGE_CATALOG.length - earnedBadgesCount.value
})

const filteredBadges = computed(() => {
  if (badgeFilter.value === 'earned') {
    return BADGE_CATALOG.filter((b) => isBadgeEarned(b.name))
  }
  if (badgeFilter.value === 'locked') {
    return BADGE_CATALOG.filter((b) => !isBadgeEarned(b.name))
  }
  return BADGE_CATALOG
})

// Active Topics List
const activeTopicList = computed(() => {
  if (sessionStore.board === 'cbse') {
    return [
      { id: 'factors_multiples', name: 'Factors', icon: '🔢' },
      { id: 'fractions', name: 'Fractions', icon: '🍰' },
      { id: 'decimals', name: 'Decimals', icon: '🎯' },
      { id: 'integers', name: 'Integers', icon: '❄️' },
      { id: 'ratios', name: 'Ratios', icon: '⚖️' },
      { id: 'geometry', name: 'Geometry', icon: '📐' },
    ]
  }

  return [
    { id: 'fractions', name: 'Fractions', icon: '🍰' },
    { id: 'decimals', name: 'Decimals', icon: '🎯' },
    { id: 'ratios', name: 'Ratios', icon: '⚖️' },
    { id: 'geometry', name: 'Geometry', icon: '📐' },
  ]
})

const averageMastery = computed(() => {
  const list = activeTopicList.value
  if (list.length === 0) return 50
  const sum = list.reduce((acc, t) => acc + (sessionStore.mastery[t.id] !== undefined ? sessionStore.mastery[t.id] : 50), 0)
  return Math.round(sum / list.length)
})

// Radar Chart Coordinates & Calculations (Center 160, 160, Radius 100)
const RADAR_CENTER = 160
const RADAR_RADIUS = 100

function getConcentricPoints(level: number): string {
  const count = activeTopicList.value.length
  const r = RADAR_RADIUS * level
  const points: string[] = []
  for (let i = 0; i < count; i++) {
    const angle = -Math.PI / 2 + (2 * Math.PI * i) / count
    const x = RADAR_CENTER + r * Math.cos(angle)
    const y = RADAR_CENTER + r * Math.sin(angle)
    points.push(`${x.toFixed(1)},${y.toFixed(1)}`)
  }
  return points.join(' ')
}

const radarAxes = computed(() => {
  const count = activeTopicList.value.length
  return activeTopicList.value.map((topic, i) => {
    const angle = -Math.PI / 2 + (2 * Math.PI * i) / count
    const edgeX = RADAR_CENTER + RADAR_RADIUS * Math.cos(angle)
    const edgeY = RADAR_CENTER + RADAR_RADIUS * Math.sin(angle)
    const labelR = RADAR_RADIUS + 28
    const labelX = RADAR_CENTER + labelR * Math.cos(angle)
    const labelY = RADAR_CENTER + labelR * Math.sin(angle)

    let textAnchor = 'middle'
    if (Math.cos(angle) > 0.3) textAnchor = 'start'
    else if (Math.cos(angle) < -0.3) textAnchor = 'end'

    const score = Math.round(sessionStore.mastery[topic.id] !== undefined ? sessionStore.mastery[topic.id] : 50)

    return {
      name: topic.name,
      icon: topic.icon,
      score,
      edgeX,
      edgeY,
      labelX,
      labelY,
      textAnchor,
    }
  })
})

const radarDataCoords = computed(() => {
  const count = activeTopicList.value.length
  return activeTopicList.value.map((topic, i) => {
    const angle = -Math.PI / 2 + (2 * Math.PI * i) / count
    const score = sessionStore.mastery[topic.id] !== undefined ? sessionStore.mastery[topic.id] : 50
    const normalized = Math.min(Math.max(score / 100, 0.05), 1.0)
    const r = RADAR_RADIUS * normalized
    const x = RADAR_CENTER + r * Math.cos(angle)
    const y = RADAR_CENTER + r * Math.sin(angle)
    return {
      x,
      y,
      score: Math.round(score),
      label: topic.name,
    }
  })
})

const radarDataPointsString = computed(() => {
  return radarDataCoords.value.map((pt) => `${pt.x.toFixed(1)},${pt.y.toFixed(1)}`).join(' ')
})

// Line Chart Calculations for Accuracy over Last 10 Sessions
const lineChartSessions = computed(() => {
  const sessions = [...sessionStore.recentActivities].slice(0, 10).reverse()
  return sessions
})

const trendAccuracy = computed(() => {
  if (lineChartSessions.value.length === 0) return null
  const last = lineChartSessions.value[lineChartSessions.value.length - 1]
  return Math.round(last.accuracy_percent)
})

const lineChartPoints = computed(() => {
  const list = lineChartSessions.value
  if (list.length === 0) return []

  const xStart = 50
  const xEnd = 410
  const yTop = 20
  const yBottom = 180
  const count = list.length

  const stepX = count > 1 ? (xEnd - xStart) / (count - 1) : 0

  return list.map((s, idx) => {
    const x = count === 1 ? (xStart + xEnd) / 2 : xStart + idx * stepX
    const acc = Math.min(Math.max(s.accuracy_percent || 0, 0), 100)
    // 100% -> yTop (20), 0% -> yBottom (180)
    const y = yBottom - (acc / 100) * (yBottom - yTop)
    return {
      x,
      y,
      accuracy: Math.round(acc),
      topic: s.topic,
    }
  })
})

const lineChartLinePath = computed(() => {
  const pts = lineChartPoints.value
  if (pts.length === 0) return ''
  return pts.map((pt, i) => `${i === 0 ? 'M' : 'L'} ${pt.x.toFixed(1)} ${pt.y.toFixed(1)}`).join(' ')
})

const lineChartAreaPath = computed(() => {
  const pts = lineChartPoints.value
  if (pts.length === 0) return ''
  const first = pts[0]
  const last = pts[pts.length - 1]
  const yBottom = 180
  const linePart = pts.map((pt, i) => `${i === 0 ? 'M' : 'L'} ${pt.x.toFixed(1)} ${pt.y.toFixed(1)}`).join(' ')
  return `${linePart} L ${last.x.toFixed(1)} ${yBottom} L ${first.x.toFixed(1)} ${yBottom} Z`
})

// Misconception Aggregation
const topMisconception = computed(() => {
  // Check if student has roundRecords with misconception tags
  const tags: Record<string, number> = {}
  sessionStore.roundRecords.forEach((r) => {
    if (r.misconceptionTag) {
      tags[r.misconceptionTag] = (tags[r.misconceptionTag] || 0) + 1
    }
  })

  // If tags exist in current round
  const sortedTags = Object.entries(tags).sort((a, b) => b[1] - a[1])
  if (sortedTags.length > 0) {
    const topTag = sortedTags[0][0]
    return getMisconceptionDetails(topTag)
  }

  // Fallback: Check lowest mastery topic to highlight its primary diagnostic trap
  const lowest = sessionStore.lowestMasteryTopic
  if (lowest.score < 75) {
    if (lowest.id === 'fractions') {
      return {
        domain: 'Fractions',
        title: 'Direct Numerator & Denominator Addition',
        explanation: 'When adding fractions with unlike denominators, adding numerators across and denominators across directly ignores proportional parts. Always convert to common denominators using the LCM before adding.',
        practiceLink: `/quiz?board=${sessionStore.board}&grade=${sessionStore.grade}&topic=fractions`,
        lessonLink: `/learn/${sessionStore.grade}/fractions`,
      }
    }
    if (lowest.id === 'decimals') {
      return {
        domain: 'Decimals',
        title: 'Decimal Alignment vs Digit Count',
        explanation: 'Aligning decimals by their rightmost digit instead of matching tenths with tenths and hundredths with hundredths leads to place-value drift. Align by the decimal point!',
        practiceLink: `/quiz?board=${sessionStore.board}&grade=${sessionStore.grade}&topic=decimals`,
        lessonLink: `/learn/${sessionStore.grade}/decimals`,
      }
    }
    if (lowest.id === 'geometry') {
      return {
        domain: 'Geometry',
        title: 'Area vs Perimeter Confusion',
        explanation: 'Confusing 2D boundary distance (perimeter = sum of all sides) with 2D surface coverage (area = length × width or ½ base × height). Check your units (cm vs cm²)!',
        practiceLink: `/quiz?board=${sessionStore.board}&grade=${sessionStore.grade}&topic=geometry`,
        lessonLink: `/learn/${sessionStore.grade}/geometry`,
      }
    }
  }

  return null
})

function getMisconceptionDetails(tag: string) {
  const map: Record<string, any> = {
    add_numerators_add_denominators: {
      domain: 'Fractions',
      title: 'Direct Denominator Addition Trap',
      explanation: 'You added numerators and denominators across directly. Remember that denominators represent the total size of equal slices—they must match before numerators can be joined.',
      practiceLink: `/quiz?board=${sessionStore.board}&grade=${sessionStore.grade}&topic=fractions`,
      lessonLink: `/learn/${sessionStore.grade}/fractions`,
    },
    decimal_place_value_shift: {
      domain: 'Decimals',
      title: 'Decimal Alignment Drift',
      explanation: 'Digits were computed without locking the decimal points into matching place values. Pad with trailing zeros to verify alignment.',
      practiceLink: `/quiz?board=${sessionStore.board}&grade=${sessionStore.grade}&topic=decimals`,
      lessonLink: `/learn/${sessionStore.grade}/decimals`,
    },
    area_perimeter_confusion: {
      domain: 'Geometry',
      title: 'Perimeter vs Area Formula Swap',
      explanation: 'Perimeter measures the boundary fence around a shape, while area measures the carpet tiles inside. Don’t swap side addition with dimension multiplication!',
      practiceLink: `/quiz?board=${sessionStore.board}&grade=${sessionStore.grade}&topic=geometry`,
      lessonLink: `/learn/${sessionStore.grade}/geometry`,
    },
  }

  return map[tag] || {
    domain: 'General Math',
    title: 'Procedural Calculation Trap',
    explanation: 'Check the step-by-step procedure and verify units carefully before submitting your answer.',
    practiceLink: `/quiz?board=${sessionStore.board}&grade=${sessionStore.grade}&topic=${sessionStore.topic}`,
    lessonLink: `/learn/${sessionStore.grade}/${sessionStore.topic}`,
  }
}

const TOPIC_REGISTRY: Record<string, { name: string; icon: string }> = {
  fractions: { name: 'Fractions', icon: '🍰' },
  decimals: { name: 'Decimals', icon: '🎯' },
  ratios: { name: 'Ratios', icon: '⚖️' },
  geometry: { name: 'Geometry', icon: '📐' },
  factors_multiples: { name: 'Factors', icon: '🔢' },
  integers: { name: 'Integers', icon: '❄️' },
}

function getTopicMeta(topicId: string) {
  return TOPIC_REGISTRY[topicId] || { name: topicId.charAt(0).toUpperCase() + topicId.slice(1), icon: '📚' }
}

function getTierBadgeClass(tier: string): string {
  const t = (tier || '').toLowerCase()
  if (t === 'hard') return 'bg-purple-100 text-purple-900 border-purple-300'
  if (t === 'easy') return 'bg-emerald-100 text-emerald-900 border-emerald-300'
  return 'bg-indigo-100 text-indigo-900 border-indigo-300'
}

function getAccuracyBadgeClass(acc: number): string {
  if (acc >= 80) return 'bg-emerald-100 text-emerald-800 border-emerald-300'
  if (acc >= 60) return 'bg-indigo-100 text-indigo-800 border-indigo-300'
  if (acc >= 40) return 'bg-amber-100 text-amber-800 border-amber-300'
  return 'bg-rose-100 text-rose-800 border-rose-300'
}

function formatFullDate(isoString: string): string {
  try {
    const d = new Date(isoString)
    if (isNaN(d.getTime())) return 'Recently'
    return d.toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch (e) {
    return 'Recently'
  }
}
</script>
