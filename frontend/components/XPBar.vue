<template>
  <div class="card-game p-3.5 sm:p-4.5 flex items-center justify-between gap-3 flex-wrap">
    <!-- Topic & Tier Indicator -->
    <div class="flex items-center gap-2">
      <!-- Topic Pill -->
      <span class="px-3 py-1.5 rounded-xl text-xs font-black uppercase tracking-wider bg-warm-100 text-warm-700 border border-warm-200">
        {{ topic }}
      </span>

      <!-- Dynamic Tier Indicator -->
      <div
        :class="[
          'inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-black uppercase tracking-wider border transition-all duration-300',
          tierConfig.badgeClass
        ]"
      >
        <span>{{ tierConfig.icon }}</span>
        <span>Tier: {{ tierConfig.label }}</span>
      </div>
    </div>

    <!-- Right Stats: Streak & Score -->
    <div class="flex items-center gap-2.5">
      <!-- Streak Counter -->
      <div
        v-if="streak > 0"
        class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-orange-50 border-2 border-orange-200 text-orange-600 font-black text-xs sm:text-sm animate-pop"
      >
        <span class="text-base animate-pulse" aria-hidden="true">🔥</span>
        <span>{{ streak }} Streak</span>
      </div>

      <!-- XP Points Counter -->
      <div class="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-accent-50 border-2 border-accent-300 text-warm-900 font-black text-xs sm:text-sm shadow-xs">
        <span class="text-base" aria-hidden="true">⭐</span>
        <span class="tabular-nums">{{ score }} XP</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  score: number
  streak: number
  tier: 'easy' | 'medium' | 'hard' | string
  topic: string
}>()

const tierConfig = computed(() => {
  const t = props.tier.toLowerCase()
  if (t === 'easy') {
    return {
      label: 'Easy',
      icon: '🌱',
      badgeClass: 'bg-emerald-50 text-emerald-800 border-emerald-300',
    }
  }
  if (t === 'hard') {
    return {
      label: 'Hard',
      icon: '⚡',
      badgeClass: 'bg-rose-50 text-rose-800 border-rose-300',
    }
  }
  return {
    label: 'Medium',
    icon: '🎯',
    badgeClass: 'bg-accent-50 text-warm-900 border-accent-300',
  }
})
</script>
