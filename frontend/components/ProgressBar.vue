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

    <!-- Progress Bar Track -->
    <div
      class="w-full bg-warm-200 h-3.5 sm:h-4 rounded-full p-0.5 border border-warm-300 shadow-inner overflow-hidden"
      role="progressbar"
      :aria-valuenow="current"
      aria-valuemin="1"
      :aria-valuemax="total"
      :aria-label="`Question ${current} of ${total}`"
    >
      <div
        class="h-full bg-primary-600 rounded-full transition-all duration-500 ease-out shadow-sm"
        :style="{ width: `${Math.min(100, Math.max(5, (current / total) * 100))}%` }"
      ></div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  current: number
  total: number
}>()
</script>
