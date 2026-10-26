<template>
  <section
    class="bg-white rounded-3xl p-5 sm:p-8 border-2 border-slate-200 shadow-game space-y-6"
    aria-label="Math Question Card"
  >
    <!-- Top Metadata Bar -->
    <div class="flex flex-wrap items-center justify-between gap-2.5">
      <!-- Standard Code & Source Badge -->
      <div class="flex items-center gap-2 flex-wrap">
        <span
          class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-black bg-indigo-50 text-indigo-800 border border-indigo-300 shadow-sm"
          :title="`Georgia Standards of Excellence code: ${standardCode}`"
          aria-label="Standard code {{ standardCode }}"
        >
          <span aria-hidden="true">📜</span>
          <span>{{ standardCode }}</span>
        </span>

        <span
          v-if="source"
          class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-black border uppercase tracking-wider"
          :class="[
            source === 'llm'
              ? 'bg-purple-50 text-purple-800 border-purple-300'
              : source === 'cache'
              ? 'bg-amber-50 text-amber-800 border-amber-300'
              : 'bg-emerald-50 text-emerald-800 border-emerald-300'
          ]"
        >
          <span aria-hidden="true">{{ source === 'llm' ? '✨' : source === 'cache' ? '⚡' : '📚' }}</span>
          <span>{{ source === 'llm' ? 'AI Gen' : source === 'cache' ? 'Cached' : 'Vetted Bank' }}</span>
        </span>
      </div>

      <!-- Action Controls: Read Aloud + Hint Ladder -->
      <div class="flex items-center flex-wrap gap-2">
        <!-- Read Aloud Button -->
        <button
          type="button"
          @click="toggleReadAloud"
          :class="[
            'inline-flex items-center gap-1.5 text-xs font-black px-3 py-1.5 rounded-xl border transition active:scale-95 cursor-pointer focus:outline-none focus-visible:ring-4 focus-visible:ring-indigo-400',
            isSpeaking
              ? 'bg-indigo-600 text-white border-indigo-700 shadow-md animate-pulse'
              : 'bg-indigo-50 text-indigo-900 border-indigo-300 hover:bg-indigo-100'
          ]"
          :aria-label="isSpeaking ? 'Stop reading question aloud' : 'Read question aloud with text to speech'"
          :title="isSpeaking ? 'Stop speech' : 'Read question and choices aloud'"
        >
          <span aria-hidden="true">{{ isSpeaking ? '⏹' : '🔊' }}</span>
          <span>{{ isSpeaking ? 'Stop Reading' : 'Read Aloud' }}</span>
        </button>

        <!-- 3-Level Progressive Hint Ladder Toggle with transparent cost -->
        <button
          type="button"
          @click="isHintOpen = !isHintOpen"
          :disabled="isSubmitted"
          :aria-expanded="isHintOpen"
          :class="[
            'inline-flex items-center gap-1.5 text-xs font-black px-3.5 py-1.5 rounded-xl border transition active:translate-y-0.5 cursor-pointer disabled:opacity-50 focus:outline-none focus-visible:ring-4 focus-visible:ring-accent-400 min-h-[38px]',
            hintsUsed > 0
              ? 'bg-accent-100 text-warm-900 border-accent-400'
              : 'bg-accent-50 text-warm-900 border-accent-300 hover:bg-accent-100'
          ]"
          aria-label="Toggle hints (-5 XP per hint)"
        >
          <span aria-hidden="true">💡</span>
          <span>{{ isHintOpen ? 'Hide Hints' : hintsUsed === 0 ? 'Need a Hint? (-5 XP)' : `Hints (${hintsUsed}/3, -${hintsUsed * 5} XP)` }}</span>
          <span
            v-if="hintsUsed > 0"
            class="w-4 h-4 rounded-full bg-accent-400 text-warm-900 text-[10px] flex items-center justify-center font-bold"
            aria-hidden="true"
          >
            {{ hintsUsed }}
          </span>
        </button>
      </div>
    </div>

    <!-- Question Stem -->
    <h2 class="text-xl sm:text-2xl font-black text-warm-900 leading-snug tracking-tight">
      {{ stem }}
    </h2>

    <!-- Math Expression Highlight Box -->
    <div
      role="region"
      aria-label="Mathematical expression to solve"
      class="bg-warm-100/90 border-2 border-warm-300 rounded-2xl p-4 sm:p-5 text-center shadow-inner relative overflow-hidden"
    >
      <span class="text-[11px] font-black uppercase tracking-widest text-primary-700 block mb-1">
        Mathematical Expression
      </span>
      <span class="text-2xl sm:text-4xl font-extrabold text-warm-900 font-mono tracking-wider drop-shadow-sm inline-block">
        {{ expression }}
      </span>
    </div>

    <!-- Interactive SVG Visual Diagram (Rendered when question expression supports it) -->
    <div v-if="visualData" class="py-1">
      <!-- 1. Fraction Bar SVG Diagram -->
      <FractionBar
        v-if="visualData.type === 'fraction'"
        :numerator="visualData.numerator"
        :denominator="visualData.denominator"
        :secondary-numerator="visualData.secondaryNumerator"
      />

      <!-- 2. Number Line SVG Diagram -->
      <NumberLine
        v-else-if="visualData.type === 'number_line'"
        :start-val="visualData.startVal"
        :end-val="visualData.endVal"
      />

      <!-- 3. Shape Diagram SVG -->
      <ShapeDiagram
        v-else-if="visualData.type === 'shape'"
        :shape="visualData.shape"
        :width="visualData.width"
        :height="visualData.height"
        :unit="visualData.unit"
        :highlight="visualData.highlight"
      />
    </div>

    <!-- 3-Level Progressive Hint Ladder Drawer -->
    <transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="-translate-y-2 opacity-0"
      enter-to-class="translate-y-0 opacity-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="translate-y-0 opacity-100"
      leave-to-class="-translate-y-2 opacity-0"
    >
      <div
        v-if="isHintOpen"
        role="region"
        aria-label="Hint Ladder"
        class="bg-amber-50 border-2 border-amber-300 rounded-3xl p-4 sm:p-5 space-y-4 shadow-sm"
      >
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <span class="text-xl" aria-hidden="true">🪜</span>
            <span class="text-sm font-black uppercase tracking-wider text-amber-950">
              3-Level Hint Ladder
            </span>
          </div>
          <span class="text-[11px] font-bold text-amber-800 italic">
            Each level costs 5 XP
          </span>
        </div>

        <!-- Levels Progression -->
        <div class="space-y-3">
          <!-- Level 1: Nudge -->
          <div
            class="rounded-2xl border-2 p-3.5 transition-all"
            :class="hintsUsed >= 1 ? 'bg-white border-amber-400 shadow-sm' : 'bg-amber-100/60 border-amber-200 opacity-90'"
          >
            <div class="flex items-center justify-between mb-1">
              <span class="text-xs font-black uppercase text-amber-900 flex items-center gap-1.5">
                <span>🌱 Level 1: Nudge</span>
                <span v-if="hintsUsed >= 1" class="text-emerald-700 font-bold">(-5 pts)</span>
              </span>
              <button
                v-if="hintsUsed === 0 && !isSubmitted"
                type="button"
                @click="unlockHint(1)"
                class="px-3 py-1 rounded-xl bg-amber-400 hover:bg-amber-500 text-amber-950 text-xs font-black shadow-sm transition active:scale-95 cursor-pointer focus-visible:ring-4 focus-visible:ring-amber-500"
              >
                Unlock (-5 XP)
              </button>
            </div>
            <p v-if="hintsUsed >= 1" class="text-xs sm:text-sm font-bold text-slate-900 leading-relaxed">
              {{ hintLadder[0].text }}
            </p>
            <p v-else class="text-xs text-amber-800 italic">
              Gentle conceptual pointer to get your thoughts rolling.
            </p>
          </div>

          <!-- Level 2: Step -->
          <div
            class="rounded-2xl border-2 p-3.5 transition-all"
            :class="hintsUsed >= 2 ? 'bg-white border-amber-400 shadow-sm' : 'bg-amber-100/60 border-amber-200 opacity-90'"
          >
            <div class="flex items-center justify-between mb-1">
              <span class="text-xs font-black uppercase text-amber-900 flex items-center gap-1.5">
                <span>🎯 Level 2: Step</span>
                <span v-if="hintsUsed >= 2" class="text-emerald-700 font-bold">(-10 pts total)</span>
              </span>
              <button
                v-if="hintsUsed === 1 && !isSubmitted"
                type="button"
                @click="unlockHint(2)"
                class="px-3 py-1 rounded-xl bg-amber-400 hover:bg-amber-500 text-amber-950 text-xs font-black shadow-sm transition active:scale-95 cursor-pointer focus-visible:ring-4 focus-visible:ring-amber-500"
              >
                Unlock Next (-5 XP)
              </button>
            </div>
            <p v-if="hintsUsed >= 2" class="text-xs sm:text-sm font-bold text-slate-900 leading-relaxed">
              {{ hintLadder[1].text }}
            </p>
            <p v-else class="text-xs text-amber-800 italic">
              Clear procedural instruction to set up the calculation.
            </p>
          </div>

          <!-- Level 3: Worked Solution -->
          <div
            class="rounded-2xl border-2 p-3.5 transition-all"
            :class="hintsUsed >= 3 ? 'bg-white border-amber-400 shadow-sm' : 'bg-amber-100/60 border-amber-200 opacity-90'"
          >
            <div class="flex items-center justify-between mb-1">
              <span class="text-xs font-black uppercase text-amber-900 flex items-center gap-1.5">
                <span>💡 Level 3: Worked Solution</span>
                <span v-if="hintsUsed >= 3" class="text-emerald-700 font-bold">(-15 pts total)</span>
              </span>
              <button
                v-if="hintsUsed === 2 && !isSubmitted"
                type="button"
                @click="unlockHint(3)"
                class="px-3 py-1 rounded-xl bg-amber-400 hover:bg-amber-500 text-amber-950 text-xs font-black shadow-sm transition active:scale-95 cursor-pointer focus-visible:ring-4 focus-visible:ring-amber-500"
              >
                Unlock Solution (-5 XP)
              </button>
            </div>
            <p v-if="hintsUsed >= 3" class="text-xs sm:text-sm font-bold text-slate-900 leading-relaxed">
              {{ hintLadder[2].text }}
            </p>
            <p v-else class="text-xs text-amber-800 italic">
              Complete walkthrough steps to guide you to the final result.
            </p>
          </div>
        </div>
      </div>
    </transition>

    <!-- Slot for Multiple-Choice Options & Confirm Button -->
    <slot />
  </section>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useMathVisuals } from '~/composables/useMathVisuals'
import { useAccessibility } from '~/composables/useAccessibility'
import FractionBar from '~/components/FractionBar.vue'
import NumberLine from '~/components/NumberLine.vue'
import ShapeDiagram from '~/components/ShapeDiagram.vue'

interface OptionItem {
  id: string
  text: string
}

const props = defineProps<{
  stem: string
  expression: string
  standardCode: string
  topic: string
  hintsUsed: number
  isSubmitted: boolean
  options?: OptionItem[]
  source?: string
}>()

const emit = defineEmits<{
  (e: 'update:hintsUsed', count: number): void
}>()

const { parseMathVisual, generateHintLadder } = useMathVisuals()

const isHintOpen = ref(false)
const isSpeaking = ref(false)

// Parse SVG visual representation
const visualData = computed(() => {
  return parseMathVisual(props.expression, props.topic, props.stem)
})

// Generate progressive 3-level hints from expression and topic
const hintLadder = computed(() => {
  return generateHintLadder(props.expression, props.topic, props.stem)
})

const unlockHint = (level: number) => {
  emit('update:hintsUsed', level)
  isHintOpen.value = true
}

const formatMathSpeech = (expr: string): string => {
  return expr
    .replace(/\+/g, ' plus ')
    .replace(/-/g, ' minus ')
    .replace(/\*/g, ' times ')
    .replace(/×/g, ' times ')
    .replace(/÷/g, ' divided by ')
    .replace(/\//g, ' over ')
    .replace(/=/g, ' equals ')
    .replace(/\s+/g, ' ')
    .trim()
}

const toggleReadAloud = () => {
  if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
    return
  }

  if (isSpeaking.value) {
    stopSpeaking()
    return
  }

  window.speechSynthesis.cancel()

  let fullSpeech = `Question: ${props.stem}. Mathematical expression: ${formatMathSpeech(props.expression)}.`
  if (props.options && props.options.length > 0) {
    fullSpeech += ' Here are the choices. '
    props.options.forEach((opt) => {
      fullSpeech += `Option ${opt.id}: ${formatMathSpeech(opt.text)}. `
    })
  }

  const utterance = new SpeechSynthesisUtterance(fullSpeech)
  utterance.rate = 0.95
  utterance.pitch = 1.0

  utterance.onstart = () => {
    isSpeaking.value = true
  }

  utterance.onend = () => {
    isSpeaking.value = false
  }

  utterance.onerror = () => {
    isSpeaking.value = false
  }

  window.speechSynthesis.speak(utterance)
}

const stopSpeaking = () => {
  if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
    window.speechSynthesis.cancel()
  }
  isSpeaking.value = false
}

const { isReadAloud } = useAccessibility()

// Auto read-aloud if enabled when question changes or mounts
watch(() => props.stem, () => {
  stopSpeaking()
  if (isReadAloud.value) {
    toggleReadAloud()
  }
})

onMounted(() => {
  if (isReadAloud.value) {
    toggleReadAloud()
  }
})

onBeforeUnmount(() => {
  stopSpeaking()
})
</script>
