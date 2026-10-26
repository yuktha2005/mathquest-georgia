<template>
  <button
    type="button"
    @click="$emit('select', id)"
    :disabled="disabled"
    :aria-pressed="isSelected"
    :aria-label="`Option ${id}: ${text}`"
    :class="[
      'w-full min-h-[56px] p-4 sm:p-5 rounded-2xl border-2 font-bold text-left transition-all duration-150 flex items-center gap-3.5 select-none relative group focus:outline-none focus-visible:ring-4 focus-visible:ring-primary-500 focus-visible:ring-offset-2',
      stateClass
    ]"
  >
    <!-- Letter / Number Bubble -->
    <div
      :class="[
        'w-10 h-10 rounded-xl flex items-center justify-center font-extrabold text-base shrink-0 border-2 transition-colors',
        letterClass
      ]"
      aria-hidden="true"
    >
      <span>{{ id }}</span>
    </div>

    <!-- Option Text -->
    <div class="flex-1 text-warm-900 text-lg sm:text-xl font-extrabold tracking-tight">
      {{ text }}
    </div>

    <!-- Keyboard Shortcut Hint Pill (Desktop) -->
    <span
      v-if="!isSubmitted"
      aria-hidden="true"
      class="hidden sm:inline-flex items-center justify-center text-[10px] font-black uppercase text-warm-500 bg-warm-100 px-2 py-0.5 rounded-md border border-warm-300"
    >
      Key {{ index + 1 }}
    </span>

    <!-- Status Icons on Submission (Icon + text, never color alone) -->
    <div v-if="isSubmitted" class="shrink-0 text-2xl" aria-hidden="true">
      <span v-if="isCorrectOption" class="text-emerald-700 animate-pop">✅</span>
      <span v-else-if="isChosenWrong" class="text-rose-600 animate-wiggle">❌</span>
    </div>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  id: string
  text: string
  index: number
  isSelected: boolean
  isSubmitted: boolean
  isCorrectOption: boolean
  isChosenWrong: boolean
  disabled: boolean
}>()

defineEmits<{
  (e: 'select', optionId: string): void
}>()

const stateClass = computed(() => {
  if (!props.isSubmitted) {
    if (props.isSelected) {
      return 'bg-primary-50 border-primary-600 shadow-game-blue text-primary-950 scale-[1.01] ring-2 ring-primary-300'
    }
    return 'bg-white border-warm-200 hover:border-primary-400 hover:bg-warm-50 shadow-game active:translate-y-1 active:shadow-none cursor-pointer'
  }

  // Submitted states
  if (props.isCorrectOption) {
    return 'bg-emerald-50 border-emerald-600 text-emerald-950 shadow-game-green scale-[1.01]'
  }
  if (props.isChosenWrong) {
    return 'bg-rose-50 border-rose-500 text-rose-950 opacity-95 shadow-game-rose'
  }
  return 'bg-warm-100 border-warm-200 opacity-60'
})

const letterClass = computed(() => {
  if (!props.isSubmitted) {
    if (props.isSelected) {
      return 'bg-primary-700 text-white border-primary-800'
    }
    return 'bg-warm-100 text-warm-800 border-warm-300 group-hover:bg-primary-100 group-hover:text-primary-800'
  }

  if (props.isCorrectOption) {
    return 'bg-emerald-600 text-white border-emerald-700'
  }
  if (props.isChosenWrong) {
    return 'bg-rose-600 text-white border-rose-700'
  }
  return 'bg-warm-200 text-warm-600 border-warm-400'
})
</script>
