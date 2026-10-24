<template>
  <div class="space-y-6 sm:space-y-8 animate-pop">
    <!-- 1. Couldn't Save / Retry Notice Banner (Supabase Error Recovery) -->
    <div
      v-if="hasUnsavedProgress"
      class="bg-rose-50 border-2 border-rose-300 rounded-3xl p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-sm"
      role="alert"
    >
      <div class="flex items-center gap-3.5">
        <div class="w-12 h-12 rounded-2xl bg-rose-100 text-rose-700 flex items-center justify-center text-2xl font-black shrink-0">
          ⚠️
        </div>
        <div>
          <h2 class="font-extrabold text-rose-950 text-sm sm:text-base">
            Couldn't save, Retry
          </h2>
          <p class="text-xs sm:text-sm text-rose-700 mt-0.5">
            {{ syncError || "A network or server issue prevented saving recent quiz results to the cloud. Your progress is safely kept on this device." }}
          </p>
        </div>
      </div>
      <button
        type="button"
        @click="handleRetrySync"
        :disabled="isSyncing"
        class="px-5 py-2.5 rounded-2xl font-extrabold text-xs sm:text-sm text-white bg-rose-600 hover:bg-rose-700 active:scale-95 transition shadow disabled:opacity-50 flex items-center gap-2 shrink-0 cursor-pointer border-b-2 border-rose-800"
      >
        <span v-if="isSyncing" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
        <span>{{ isSyncing ? 'Retrying...' : 'Retry Save 🔄' }}</span>
      </button>
    </div>

    <!-- 2. Move Guest Progress Notice (Offered on First Signup / Account Login) -->
    <div
      v-if="!authStore.isGuest && canImportGuest"
      class="bg-gradient-to-r from-amber-50 via-emerald-50 to-teal-50 border-2 border-emerald-400 rounded-3xl p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-sm"
      role="region"
      aria-label="Guest Progress Import Offer"
    >
      <div class="flex items-center gap-3.5">
        <div class="w-12 h-12 rounded-2xl bg-emerald-100 text-emerald-800 flex items-center justify-center text-2xl shrink-0 shadow-inner">
          🎒
        </div>
        <div>
          <div class="flex items-center gap-2 flex-wrap">
            <h2 class="font-extrabold text-emerald-950 text-sm sm:text-base">
              Guest Adventure Progress Found!
            </h2>
            <span class="bg-emerald-200 text-emerald-900 text-[10px] font-black px-2 py-0.5 rounded-full uppercase">
              Action Available
            </span>
          </div>
          <p class="text-xs sm:text-sm text-emerald-800 mt-0.5">
            You played as a guest earlier. Would you like to move your guest XP, mastery, and badges into this permanent account?
          </p>
        </div>
      </div>
      <div class="flex items-center gap-2 self-end sm:self-auto shrink-0">
        <button
          type="button"
          @click="handleImportGuestProgress"
          :disabled="isSyncing"
          class="px-5 py-2.5 rounded-2xl font-extrabold text-xs sm:text-sm text-white bg-emerald-600 hover:bg-emerald-700 active:scale-95 transition shadow disabled:opacity-50 flex items-center gap-2 border-b-2 border-emerald-800 cursor-pointer"
        >
          <span v-if="isSyncing" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
          <span>{{ isSyncing ? 'Importing...' : 'Move my guest progress into this account ✨' }}</span>
        </button>
        <button
          type="button"
          @click="dismissGuestImport"
          class="px-3.5 py-2.5 rounded-2xl font-bold text-xs text-slate-600 bg-white hover:bg-slate-100 border border-slate-300 transition"
        >
          Dismiss
        </button>
      </div>
    </div>

    <!-- 3. Guest Mode Reminder Banner -->
    <div
      v-if="authStore.isGuest"
      class="bg-gradient-to-r from-amber-50 to-orange-50 border-2 border-amber-300 rounded-3xl p-4 sm:p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 shadow-sm"
    >
      <div class="flex items-center gap-3">
        <span class="text-3xl" aria-hidden="true">🎒</span>
        <div>
          <h2 class="font-extrabold text-slate-900 text-sm sm:text-base">
            Playing in Guest Mode
          </h2>
          <p class="text-xs text-slate-600">
            Your progress is currently saved in this browser. Create a free account to sync across devices and keep your achievements permanently!
          </p>
        </div>
      </div>
      <div class="flex items-center gap-2 self-end sm:self-auto shrink-0">
        <NuxtLink
          to="/signup"
          class="px-4 py-2 rounded-xl text-xs sm:text-sm font-extrabold text-white bg-indigo-600 hover:bg-indigo-700 transition shadow"
        >
          Sign Up Free ✨
        </NuxtLink>
        <NuxtLink
          to="/login"
          class="px-3 py-2 rounded-xl text-xs sm:text-sm font-bold text-slate-700 bg-white hover:bg-slate-100 transition border border-slate-300"
        >
          Sign In
        </NuxtLink>
      </div>
    </div>

    <!-- 4. User Hero Greeting Banner -->
    <div class="bg-white rounded-3xl border-2 border-slate-200 shadow-sm p-6 sm:p-8 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
      <div class="flex items-center gap-4 sm:gap-5">
        <div class="w-16 h-16 sm:w-20 sm:h-20 rounded-3xl bg-indigo-100 border-2 border-indigo-200 flex items-center justify-center text-3xl sm:text-4xl shadow-inner shrink-0">
          {{ authStore.isGuest ? '🎒' : '🧙‍♂️' }}
        </div>
        <div>
          <div class="flex items-center gap-2 flex-wrap">
            <h1 class="text-2xl sm:text-3xl font-extrabold text-slate-900">
              Welcome back, {{ authStore.displayName }}!
            </h1>
            <span
              class="px-2.5 py-0.5 rounded-full text-xs font-extrabold"
              :class="authStore.isGuest ? 'bg-amber-100 text-amber-800' : 'bg-emerald-100 text-emerald-800'"
            >
              {{ authStore.isGuest ? 'Guest Adventurer' : 'Explorer Account' }}
            </span>
          </div>
          <p class="text-xs sm:text-sm text-slate-600 mt-1 flex items-center gap-2 flex-wrap">
            <span>Grade {{ sessionStore.grade }}</span>
            <span>•</span>
            <span>{{ sessionStore.board === 'cbse' ? 'CBSE Class 6 (NCERT)' : 'Georgia Standards (MGSE)' }}</span>
            <span v-if="!authStore.isGuest && authStore.user?.email">•</span>
            <span v-if="!authStore.isGuest && authStore.user?.email" class="text-slate-500 font-mono text-xs">
              {{ authStore.user.email }}
            </span>
          </p>
        </div>
      </div>

      <!-- Quick Action Controls -->
      <div class="flex items-center gap-2.5 w-full md:w-auto">
        <NuxtLink
          to="/"
          class="flex-1 md:flex-initial px-5 py-3 rounded-2xl bg-indigo-600 hover:bg-indigo-700 text-white font-extrabold text-sm sm:text-base text-center transition shadow-md hover:shadow-lg border-b-4 border-indigo-800"
        >
          Browse Topics 🗺️
        </NuxtLink>
        <button
          v-if="!authStore.isGuest"
          type="button"
          @click="authStore.signOut()"
          class="px-4 py-3 rounded-2xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-sm transition border border-slate-300"
          title="Sign out of your account"
        >
          Sign Out
        </button>
      </div>
    </div>

    <!-- 5. Dual Action Cards: "Continue" Card & "Recommended Next Topic" Card -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-5 sm:gap-6">
      <!-- "Continue" Card (Last Topic and Tier) -->
      <div class="bg-gradient-to-br from-indigo-50/70 via-white to-blue-50/50 rounded-3xl border-2 border-indigo-200 shadow-sm p-6 sm:p-7 flex flex-col justify-between relative overflow-hidden">
        <div>
          <div class="flex items-center justify-between mb-3">
            <span class="text-xs font-black uppercase text-indigo-700 tracking-wider flex items-center gap-1.5">
              <span>⚔️</span>
              <span>Continue Quest</span>
            </span>
            <span
              class="px-3 py-1 rounded-full text-xs font-black uppercase border"
              :class="getTierBadgeClass(continueCard.tier)"
            >
              Tier: {{ continueCard.tier }}
            </span>
          </div>

          <div class="flex items-center gap-4 my-2">
            <div class="w-14 h-14 rounded-2xl bg-white border-2 border-indigo-200 flex items-center justify-center text-3xl shadow-sm shrink-0">
              {{ getTopicMeta(continueCard.topic).icon }}
            </div>
            <div>
              <h3 class="text-xl sm:text-2xl font-black text-slate-900 leading-tight">
                {{ getTopicMeta(continueCard.topic).name }}
              </h3>
              <p class="text-xs text-slate-500 font-semibold mt-0.5">
                Last practiced • Grade {{ continueCard.grade }} • {{ continueCard.board === 'cbse' ? 'CBSE' : 'Georgia GSE' }}
              </p>
            </div>
          </div>
        </div>

        <div class="pt-5 mt-3 border-t border-indigo-100 flex items-center gap-3">
          <NuxtLink
            :to="`/quiz?board=${continueCard.board}&grade=${continueCard.grade}&topic=${continueCard.topic}&tier=${continueCard.tier}`"
            class="flex-1 py-3 px-5 rounded-2xl bg-indigo-600 hover:bg-indigo-700 active:scale-[0.98] text-white font-extrabold text-sm sm:text-base text-center transition shadow-md hover:shadow-lg border-b-4 border-indigo-800 flex items-center justify-center gap-2"
          >
            <span>Resume Adventure →</span>
          </NuxtLink>
          <NuxtLink
            :to="`/learn/${continueCard.grade}/${continueCard.topic}`"
            class="py-3 px-4 rounded-2xl bg-white hover:bg-slate-50 text-slate-700 font-bold text-sm border border-slate-300 transition"
            title="Read topic explanation and view infographic"
          >
            📖 Lesson
          </NuxtLink>
        </div>
      </div>

      <!-- Recommended Next Topic Card (Lowest Mastery) -->
      <div class="bg-gradient-to-br from-amber-50/70 via-white to-orange-50/50 rounded-3xl border-2 border-amber-300 shadow-sm p-6 sm:p-7 flex flex-col justify-between relative overflow-hidden">
        <div>
          <div class="flex items-center justify-between mb-3">
            <span class="text-xs font-black uppercase text-amber-800 tracking-wider flex items-center gap-1.5">
              <span>🎯</span>
              <span>Recommended Next Target</span>
            </span>
            <span class="bg-amber-100 text-amber-900 text-xs font-black px-2.5 py-0.5 rounded-full border border-amber-300">
              Lowest Mastery
            </span>
          </div>

          <div class="flex items-center gap-4 my-2">
            <div class="w-14 h-14 rounded-2xl bg-white border-2 border-amber-300 flex items-center justify-center text-3xl shadow-sm shrink-0">
              {{ lowestMastery.emoji }}
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center justify-between">
                <h3 class="text-xl sm:text-2xl font-black text-slate-900 leading-tight truncate">
                  {{ lowestMastery.name }}
                </h3>
                <span class="text-sm font-extrabold text-amber-700 shrink-0 ml-2">
                  {{ Math.round(lowestMastery.score) }}%
                </span>
              </div>
              <div class="w-full bg-slate-200 rounded-full h-2 mt-2 overflow-hidden">
                <div
                  class="h-2 rounded-full transition-all duration-500"
                  :class="getMasteryBarColor(lowestMastery.score)"
                  :style="{ width: `${Math.min(lowestMastery.score, 100)}%` }"
                ></div>
              </div>
              <p class="text-[11px] text-slate-500 font-bold mt-1.5 font-mono">
                Standard: {{ lowestMastery.code }}
              </p>
            </div>
          </div>
        </div>

        <div class="pt-5 mt-3 border-t border-amber-100 flex items-center gap-3">
          <NuxtLink
            :to="`/quiz?board=${sessionStore.board}&grade=${sessionStore.grade}&topic=${lowestMastery.id}`"
            class="flex-1 py-3 px-5 rounded-2xl bg-amber-500 hover:bg-amber-600 active:scale-[0.98] text-white font-extrabold text-sm sm:text-base text-center transition shadow-md hover:shadow-lg border-b-4 border-amber-700 flex items-center justify-center gap-2"
          >
            <span>🚀 Boost Mastery</span>
          </NuxtLink>
          <NuxtLink
            :to="`/learn/${sessionStore.grade}/${lowestMastery.id}`"
            class="py-3 px-4 rounded-2xl bg-white hover:bg-slate-50 text-slate-700 font-bold text-sm border border-slate-300 transition"
          >
            📖 Lesson
          </NuxtLink>
        </div>
      </div>
    </div>

    <!-- 6. Gamified Metrics Row: Daily Goal Ring, Streak Counter, Total XP, Badges -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-5">
      <!-- 1. Daily Goal Circular Progress Ring -->
      <div class="bg-white rounded-3xl border-2 border-slate-200 p-5 shadow-sm flex flex-col items-center text-center justify-between">
        <div class="text-xs font-black text-slate-500 uppercase tracking-wider mb-2">
          Daily Goal Ring 🎯
        </div>

        <!-- SVG Circular Ring -->
        <div class="relative w-28 h-28 my-1 flex items-center justify-center">
          <svg class="w-28 h-28 transform -rotate-90" viewBox="0 0 100 100">
            <!-- Background circle track -->
            <circle
              cx="50"
              cy="50"
              r="38"
              stroke="#E2E8F0"
              stroke-width="9"
              fill="transparent"
            />
            <!-- Animated progress circle -->
            <circle
              cx="50"
              cy="50"
              r="38"
              :stroke="dailyRingColor"
              stroke-width="9"
              fill="transparent"
              :stroke-dasharray="238.76"
              :stroke-dashoffset="ringStrokeDashoffset"
              stroke-linecap="round"
              class="transition-all duration-700 ease-out"
            />
          </svg>
          <div class="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
            <span class="text-xl font-black text-slate-900 leading-none">
              {{ sessionStore.todayAnswersCount }}<span class="text-xs text-slate-400 font-bold">/{{ sessionStore.dailyGoal }}</span>
            </span>
            <span class="text-[10px] font-extrabold uppercase text-slate-500 tracking-wider mt-0.5">
              Answers
            </span>
          </div>
        </div>

        <div class="mt-2 text-xs font-bold" :class="dailyGoalPercent >= 100 ? 'text-emerald-600' : 'text-slate-600'">
          {{ dailyGoalStatusText }}
        </div>
      </div>

      <!-- 2. Streak Counter -->
      <div class="bg-white rounded-3xl border-2 border-slate-200 p-5 shadow-sm flex flex-col justify-between">
        <div>
          <div class="flex items-center justify-between mb-3">
            <span class="text-xs font-black text-slate-500 uppercase tracking-wider">Streak Counter</span>
            <span class="text-2xl animate-pulse">🔥</span>
          </div>
          <div class="text-3xl sm:text-4xl font-black text-orange-600 flex items-center gap-1.5">
            <span>{{ sessionStore.streak }}</span>
            <span class="text-sm font-bold text-slate-500">in a row</span>
          </div>
        </div>
        <div class="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs font-bold text-slate-600">
          <span>Best Streak:</span>
          <span class="text-sm font-black text-slate-900 flex items-center gap-1">
            <span>⚡</span>
            <span>{{ sessionStore.bestStreak || sessionStore.streak }}</span>
          </span>
        </div>
      </div>

      <!-- 3. Total XP Score -->
      <div class="bg-white rounded-3xl border-2 border-slate-200 p-5 shadow-sm flex flex-col justify-between">
        <div>
          <div class="flex items-center justify-between mb-3">
            <span class="text-xs font-black text-slate-500 uppercase tracking-wider">Total Score</span>
            <span class="text-2xl">⭐</span>
          </div>
          <div class="text-3xl sm:text-4xl font-black text-amber-500">
            {{ sessionStore.score }} <span class="text-sm font-bold text-slate-500">XP</span>
          </div>
        </div>
        <div class="mt-4 pt-3 border-t border-slate-100 text-xs font-bold text-slate-500">
          Earn +10 to +30 XP per correct answer based on tier difficulty
        </div>
      </div>

      <!-- 4. Badges Unlocked -->
      <div class="bg-white rounded-3xl border-2 border-slate-200 p-5 shadow-sm flex flex-col justify-between">
        <div>
          <div class="flex items-center justify-between mb-3">
            <span class="text-xs font-black text-slate-500 uppercase tracking-wider">Badges</span>
            <span class="text-2xl">🏆</span>
          </div>
          <div class="text-3xl sm:text-4xl font-black text-purple-600">
            {{ sessionStore.badges.length }} <span class="text-sm font-bold text-slate-500">Unlocked</span>
          </div>
        </div>
        <div class="mt-4 pt-3 border-t border-slate-100 text-xs font-bold text-slate-500">
          Reach streaks and 80%+ topic mastery to unlock trophies
        </div>
      </div>
    </div>

    <!-- 7. Curriculum Topic Mastery Overview -->
    <div class="bg-white rounded-3xl border-2 border-slate-200 shadow-sm p-6 sm:p-8">
      <div class="flex items-center justify-between mb-6 flex-wrap gap-2">
        <div>
          <h2 class="text-xl sm:text-2xl font-extrabold text-slate-900">
            Curriculum Topic Mastery
          </h2>
          <p class="text-xs sm:text-sm text-slate-600">
            Adaptive engine tracks diagnostic accuracy. Reach 80%+ to unlock domain mastery badges!
          </p>
        </div>
        <NuxtLink
          to="/"
          class="text-xs sm:text-sm font-bold text-indigo-600 hover:text-indigo-800 transition hover:underline"
        >
          View Territory Map →
        </NuxtLink>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
        <div
          v-for="topic in activeTopics"
          :key="topic.id"
          class="p-5 rounded-2xl border-2 border-slate-200 hover:border-indigo-300 transition flex flex-col justify-between bg-slate-50 hover:bg-white group"
        >
          <div>
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center gap-2.5">
                <span class="text-2xl" aria-hidden="true">{{ topic.icon }}</span>
                <div>
                  <h3 class="font-extrabold text-base text-slate-900 group-hover:text-indigo-700 transition">
                    {{ topic.name }}
                  </h3>
                  <span class="text-xs font-mono font-bold text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded">
                    {{ topic.code }}
                  </span>
                </div>
              </div>
              <div class="text-right">
                <span class="text-sm font-extrabold text-slate-800">
                  {{ Math.round(sessionStore.mastery[topic.id] !== undefined ? sessionStore.mastery[topic.id] : 50) }}%
                </span>
              </div>
            </div>

            <!-- Progress Bar -->
            <div class="w-full bg-slate-200 rounded-full h-2.5 mb-4 overflow-hidden">
              <div
                class="h-2.5 rounded-full transition-all duration-500"
                :class="getMasteryBarColor(sessionStore.mastery[topic.id] !== undefined ? sessionStore.mastery[topic.id] : 50)"
                :style="{ width: `${Math.min(sessionStore.mastery[topic.id] !== undefined ? sessionStore.mastery[topic.id] : 50, 100)}%` }"
              ></div>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="flex items-center gap-2 pt-2">
            <NuxtLink
              :to="`/learn/${sessionStore.grade}/${topic.id}`"
              class="flex-1 py-2 px-3 rounded-xl bg-white hover:bg-slate-100 text-slate-700 font-bold text-xs text-center border border-slate-300 transition"
            >
              📖 Lesson
            </NuxtLink>
            <NuxtLink
              :to="`/quiz?board=${sessionStore.board}&grade=${sessionStore.grade}&topic=${topic.id}`"
              class="flex-1 py-2 px-3 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-extrabold text-xs text-center transition shadow"
            >
              ⚔️ Practice
            </NuxtLink>
          </div>
        </div>
      </div>
    </div>

    <!-- 8. Recent Activity List -->
    <div class="bg-white rounded-3xl border-2 border-slate-200 shadow-sm p-6 sm:p-8">
      <div class="flex items-center justify-between mb-5">
        <div>
          <h2 class="text-xl sm:text-2xl font-extrabold text-slate-900 flex items-center gap-2">
            <span>📜</span>
            <span>Recent Activity List</span>
          </h2>
          <p class="text-xs sm:text-sm text-slate-600">
            Log of completed quiz sessions, scores, and diagnostic accuracy
          </p>
        </div>
        <span class="text-xs font-black text-slate-500 bg-slate-100 px-3 py-1 rounded-full">
          {{ sessionStore.recentActivities.length }} Sessions Logged
        </span>
      </div>

      <!-- Activity Items List -->
      <div v-if="sessionStore.recentActivities.length > 0" class="space-y-3">
        <div
          v-for="(act, idx) in sessionStore.recentActivities"
          :key="act.id || idx"
          class="p-4 rounded-2xl border-2 border-slate-200 hover:border-indigo-300 bg-slate-50/70 hover:bg-white transition flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3"
        >
          <div class="flex items-center gap-3.5">
            <div class="w-11 h-11 rounded-xl bg-indigo-100 text-indigo-700 flex items-center justify-center text-xl shrink-0 font-bold">
              {{ getTopicMeta(act.topic).icon }}
            </div>
            <div>
              <div class="flex items-center gap-2 flex-wrap">
                <h4 class="font-black text-sm sm:text-base text-slate-900">
                  {{ getTopicMeta(act.topic).name }}
                </h4>
                <span
                  class="px-2 py-0.5 rounded text-[10px] font-black uppercase border"
                  :class="getTierBadgeClass(act.tier)"
                >
                  {{ act.tier }}
                </span>
                <span class="text-xs text-slate-400 font-bold">•</span>
                <span class="text-xs text-slate-500 font-medium">
                  {{ formatActivityDate(act.created_at) }}
                </span>
              </div>
              <p class="text-xs text-slate-600 mt-0.5">
                Grade {{ act.grade }} • {{ act.correct_count }} of {{ act.total_questions }} correct
              </p>
            </div>
          </div>

          <div class="flex items-center gap-3 self-end sm:self-auto shrink-0">
            <!-- Accuracy Badge -->
            <span
              class="px-2.5 py-1 rounded-xl text-xs font-black border"
              :class="getAccuracyBadgeClass(act.accuracy_percent)"
            >
              {{ act.accuracy_percent }}% Accuracy
            </span>
            <!-- Score XP -->
            <span class="text-sm font-black text-amber-600 bg-amber-50 border border-amber-200 px-2.5 py-1 rounded-xl">
              +{{ act.score }} XP
            </span>
          </div>
        </div>
      </div>

      <!-- Empty Activity State -->
      <div v-else class="text-center py-10 bg-slate-50 rounded-2xl border-2 border-dashed border-slate-200">
        <span class="text-4xl block mb-2" aria-hidden="true">🗺️</span>
        <h3 class="text-base font-extrabold text-slate-800">No practice sessions completed yet</h3>
        <p class="text-xs text-slate-500 max-w-sm mx-auto mt-1 mb-4">
          Complete your first 10-question practice round to track your learning journey here!
        </p>
        <NuxtLink
          to="/quiz"
          class="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-extrabold text-xs transition shadow"
        >
          <span>Start Practice Quest ⚔️</span>
        </NuxtLink>
      </div>
    </div>

    <!-- 9. Achievements & Badges Showcase -->
    <div class="bg-white rounded-3xl border-2 border-slate-200 shadow-sm p-6 sm:p-8">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h2 class="text-xl sm:text-2xl font-extrabold text-slate-900 flex items-center gap-2">
            <span>🏆</span>
            <span>Earned Achievement Badges</span>
          </h2>
          <p class="text-xs sm:text-sm text-slate-600">
            Badges awarded for streaks, hard questions, and curriculum mastery
          </p>
        </div>
        <span class="text-xs font-black text-indigo-700 bg-indigo-50 border border-indigo-200 px-3 py-1 rounded-full">
          {{ sessionStore.badges.length }} Collected
        </span>
      </div>

      <div v-if="sessionStore.badges.length > 0" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3.5 pt-2">
        <div
          v-for="badge in sessionStore.badges"
          :key="badge"
          class="bg-amber-50 border-2 border-amber-300 rounded-2xl p-4 text-center space-y-1 shadow-sm"
        >
          <span class="text-3xl block">{{ getBadgeEmoji(badge) }}</span>
          <span class="font-extrabold text-xs sm:text-sm text-slate-800 block leading-tight">
            {{ badge }}
          </span>
          <span class="text-[10px] font-bold text-amber-800 uppercase block">Unlocked</span>
        </div>
      </div>
      <div v-else class="text-center py-8 text-slate-400 bg-slate-50 rounded-2xl border-2 border-dashed border-slate-200">
        <span class="text-3xl block mb-2" aria-hidden="true">🎯</span>
        <p class="text-sm font-semibold text-slate-700">No badges unlocked yet.</p>
        <p class="text-xs mt-1 text-slate-500">Complete a 10-question quiz practice session to earn your first "First Steps" badge!</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '~/stores/auth'
import { useSessionStore } from '~/stores/session'
import { useProgressSync } from '~/composables/useProgressSync'

const authStore = useAuthStore()
const sessionStore = useSessionStore()
const {
  hasUnsavedProgress,
  syncError,
  isSyncing,
  retryPendingSync,
  hasGuestProgressToImport,
  importGuestProgress,
} = useProgressSync()

const canImportGuest = ref(false)

onMounted(() => {
  sessionStore.loadFromStorage()
  if (import.meta.client) {
    canImportGuest.value = hasGuestProgressToImport()
  }
})

// Retry Supabase save
async function handleRetrySync() {
  await retryPendingSync()
}

// Import Guest Progress into signed-in account
async function handleImportGuestProgress() {
  const success = await importGuestProgress()
  if (success) {
    canImportGuest.value = false
  }
}

function dismissGuestImport() {
  if (import.meta.client) {
    localStorage.removeItem('mathquest_guest_backup_before_auth')
  }
  canImportGuest.value = false
}

// Continue adventure card info
const continueCard = computed(() => {
  return sessionStore.continueAdventureCard
})

// Lowest mastery topic
const lowestMastery = computed(() => {
  return sessionStore.lowestMasteryTopic
})

// Daily Goal Calculation
const dailyGoalPercent = computed(() => {
  const count = sessionStore.todayAnswersCount
  const goal = sessionStore.dailyGoal || 10
  return Math.min(Math.round((count / goal) * 100), 100)
})

const ringStrokeDashoffset = computed(() => {
  const circumference = 238.76 // 2 * PI * 38
  return circumference - (circumference * dailyGoalPercent.value) / 100
})

const dailyRingColor = computed(() => {
  if (dailyGoalPercent.value >= 100) return '#10B981' // emerald-500
  if (dailyGoalPercent.value >= 60) return '#6366F1' // indigo-500
  return '#F59E0B' // amber-500
})

const dailyGoalStatusText = computed(() => {
  const count = sessionStore.todayAnswersCount
  const goal = sessionStore.dailyGoal || 10
  if (count >= goal) {
    return 'Goal Completed! 🌟 Awesome job!'
  }
  const remaining = goal - count
  return `${remaining} more answer${remaining === 1 ? '' : 's'} to hit daily goal`
})

// Active topics for the current curriculum & grade
const activeTopics = computed(() => {
  if (sessionStore.board === 'cbse') {
    return [
      { id: 'factors_multiples', name: 'Factors & Multiples', icon: '🔢', code: 'CBSE6.MATH.01' },
      { id: 'fractions', name: 'Fractions', icon: '🍰', code: 'CBSE6.MATH.02' },
      { id: 'decimals', name: 'Decimals', icon: '🎯', code: 'CBSE6.MATH.03' },
      { id: 'integers', name: 'Integers', icon: '❄️', code: 'CBSE6.MATH.04' },
      { id: 'ratios', name: 'Ratios & Proportions', icon: '⚖️', code: 'CBSE6.MATH.05' },
      { id: 'geometry', name: 'Geometry', icon: '📐', code: 'CBSE6.MATH.06' },
    ]
  }

  if (sessionStore.grade === 6) {
    return [
      { id: 'fractions', name: 'Divide Fractions', icon: '🍰', code: 'MGSE6.NS.1' },
      { id: 'decimals', name: 'Decimal Computation', icon: '🎯', code: 'MGSE6.NS.3' },
      { id: 'ratios', name: 'Ratios & Unit Rates', icon: '⚖️', code: 'MGSE6.RP.1' },
      { id: 'geometry', name: 'Area & Surface Area', icon: '📐', code: 'MGSE6.G.1' },
    ]
  }

  return [
    { id: 'fractions', name: 'Unlike Fractions', icon: '🍰', code: 'MGSE5.NF.1' },
    { id: 'decimals', name: 'Decimals to Thousandths', icon: '🎯', code: 'MGSE5.NBT.3' },
    { id: 'ratios', name: 'Coordinate Patterns', icon: '⚖️', code: 'MGSE5.OA.3' },
    { id: 'geometry', name: 'Classify 2D Shapes', icon: '📐', code: 'MGSE5.G.3' },
  ]
})

const TOPIC_REGISTRY: Record<string, { name: string; icon: string }> = {
  fractions: { name: 'Fractions', icon: '🍰' },
  decimals: { name: 'Decimals', icon: '🎯' },
  ratios: { name: 'Ratios & Proportions', icon: '⚖️' },
  geometry: { name: 'Geometry', icon: '📐' },
  factors_multiples: { name: 'Factors & Multiples', icon: '🔢' },
  integers: { name: 'Integers', icon: '❄️' },
}

function getTopicMeta(topicId: string) {
  return TOPIC_REGISTRY[topicId] || { name: topicId.charAt(0).toUpperCase() + topicId.slice(1), icon: '📚' }
}

function getMasteryBarColor(val: number): string {
  if (val >= 80) return 'bg-emerald-500'
  if (val >= 60) return 'bg-indigo-500'
  if (val >= 40) return 'bg-amber-500'
  return 'bg-rose-500'
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

function formatActivityDate(isoString: string): string {
  try {
    const d = new Date(isoString)
    if (isNaN(d.getTime())) return 'Recently'
    const today = new Date()
    if (d.toDateString() === today.toDateString()) {
      return `Today, ${d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`
    }
    return d.toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch (e) {
    return 'Recently'
  }
}

function getBadgeEmoji(badgeName: string): string {
  switch (badgeName) {
    case 'First Steps':
      return '👣'
    case '5-Streak':
      return '🔥'
    case 'Fraction Master':
      return '🍕'
    case 'Decimal Dynamo':
      return '🎯'
    case 'Ratio Ranger':
      return '⚖️'
    case 'Geometry Giant':
      return '📐'
    case 'CBSE Champion':
      return '🇮🇳'
    case 'Tenacious Thinker':
      return '🧠'
    case 'Comeback Kid':
      return '⚡'
    case 'Perfect Round':
      return '🌟'
    default:
      return '🏆'
  }
}
</script>
