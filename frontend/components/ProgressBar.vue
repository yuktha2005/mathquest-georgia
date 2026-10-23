<template>
  <div class="w-full space-y-1.5">
    <div class="flex items-center justify-between text-xs sm:text-sm font-extrabold text-slate-700">
      <span class="flex items-center gap-1.5">
        <span class="text-indigo-600 font-black">Question {{ current }}</span>
        <span class="text-slate-400">/</span>
        <span class="text-slate-500">{{ total }}</span>
      </span>
      <span class="text-indigo-600 font-black">{{ Math.round((current / total) * 100) }}%</span>
    </div>

    <!-- Animated Progress Bar Track -->
    <div class="w-full bg-slate-200/80 h-3.5 sm:h-4 rounded-full p-0.5 border border-slate-300 shadow-inner overflow-hidden">
      <div
        class="h-full bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 rounded-full transition-all duration-500 ease-out shadow-sm relative overflow-hidden"
        :style="{ width: `${Math.min(100, Math.max(5, (current / total) * 100))}%` }"
      >
        <!-- Shimmer highlight bar -->
        <div class="absolute inset-0 bg-white/20 -skew-x-12 animate-pulse"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  current: number
  total: number
}>()
</script>
