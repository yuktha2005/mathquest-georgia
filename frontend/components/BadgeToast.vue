<template>
  <transition
    enter-active-class="transition duration-300 ease-out"
    enter-from-class="translate-y-4 opacity-0 scale-95"
    enter-to-class="translate-y-0 opacity-100 scale-100"
    leave-active-class="transition duration-200 ease-in"
    leave-from-class="translate-y-0 opacity-100 scale-100"
    leave-to-class="translate-y-4 opacity-0 scale-95"
  >
    <div
      v-if="show && badges.length > 0"
      class="fixed bottom-6 right-6 z-50 max-w-sm w-full bg-amber-400 text-slate-900 rounded-3xl p-4 sm:p-5 shadow-2xl border-4 border-amber-500 animate-pop flex items-center justify-between gap-3"
    >
      <div class="flex items-center gap-3">
        <span class="text-4xl animate-bounce">🏆</span>
        <div>
          <span class="text-[11px] font-black uppercase tracking-wider text-amber-900 block">
            Badge Unlocked!
          </span>
          <span class="text-base sm:text-lg font-black leading-tight block">
            {{ badges.join(', ') }}
          </span>
        </div>
      </div>

      <button
        type="button"
        @click="$emit('dismiss')"
        class="text-amber-900 hover:text-black font-extrabold text-xl p-1 rounded-lg transition"
        aria-label="Close Badge Toast"
      >
        ✕
      </button>
    </div>
  </transition>
</template>

<script setup lang="ts">
defineProps<{
  badges: string[]
  show: boolean
}>()

defineEmits<{
  (e: 'dismiss'): void
}>()
</script>
