<template>
  <div class="w-full bg-slate-950 text-white rounded-3xl border-4 border-slate-800 shadow-2xl overflow-hidden relative flex flex-col select-none transition-all">
    <!-- Top Progress Bar & Header -->
    <div class="px-5 py-4 bg-slate-900/90 border-b border-slate-800/80 backdrop-blur flex flex-col gap-3">
      <div class="flex items-center justify-between flex-wrap gap-2">
        <div class="flex items-center gap-2">
          <span class="inline-flex items-center justify-center w-6 h-6 rounded-full bg-red-600 text-white text-xs font-black animate-pulse">
            ●
          </span>
          <span class="text-xs sm:text-sm font-extrabold tracking-wide uppercase text-slate-300">
            {{ title || 'MathQuest Interactive Video Lesson' }}
          </span>
        </div>

        <div class="flex items-center gap-2.5">
          <!-- Speech Support Status Tag -->
          <span
            :class="[
              'px-2.5 py-1 rounded-full text-xs font-bold flex items-center gap-1.5 border',
              hasSpeechSupport && !isSpeechMuted
                ? 'bg-emerald-950 text-emerald-300 border-emerald-800'
                : 'bg-amber-950 text-amber-300 border-amber-800'
            ]"
            :title="hasSpeechSupport ? 'Browser Speech Synthesis is active' : 'Speech synthesis not supported in this browser'"
          >
            <span>{{ hasSpeechSupport && !isSpeechMuted ? '🎙️ Narration ON' : '🔇 Visual Subtitle Mode' }}</span>
          </span>

          <span class="text-xs font-bold font-mono text-slate-400 bg-slate-800 px-2.5 py-1 rounded-lg border border-slate-700">
            Slide {{ currentSlideIndex + 1 }} / {{ totalSlides }}
          </span>
        </div>
      </div>

      <!-- Segmented Slide Progress Bar (6 Segments) -->
      <div class="grid grid-cols-6 gap-2 w-full">
        <div
          v-for="idx in totalSlides"
          :key="idx"
          @click="jumpToSlide(idx - 1)"
          class="h-2 rounded-full cursor-pointer overflow-hidden bg-slate-800 relative transition-all hover:opacity-80"
          :title="`Jump to Slide ${idx}`"
        >
          <!-- Completed slides -->
          <div
            v-if="idx - 1 < currentSlideIndex"
            class="h-full w-full bg-emerald-500 rounded-full transition-all"
          ></div>
          <!-- Current active slide -->
          <div
            v-else-if="idx - 1 === currentSlideIndex"
            class="h-full bg-gradient-to-r from-amber-400 to-amber-500 rounded-full transition-all duration-100"
            :style="{ width: `${slideProgressPercent}%` }"
          ></div>
        </div>
      </div>
    </div>

    <!-- Main Presentation Slide Canvas (16:9 responsive frame) -->
    <div class="p-6 sm:p-10 flex-1 min-h-[380px] sm:min-h-[440px] flex flex-col justify-between relative bg-gradient-to-b from-slate-900 via-slate-900/90 to-slate-950 overflow-hidden">
      <!-- Background Ambient Glow -->
      <div class="absolute -right-20 -top-20 w-72 h-72 bg-indigo-600/10 rounded-full blur-3xl pointer-events-none"></div>
      <div class="absolute -left-20 -bottom-20 w-72 h-72 bg-amber-500/10 rounded-full blur-3xl pointer-events-none"></div>

      <!-- Active Slide Content -->
      <transition name="slide-fade" mode="out-in">
        <div :key="currentSlideIndex" class="space-y-6 flex-1 flex flex-col justify-between">
          <!-- Slide Heading -->
          <div class="space-y-1">
            <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-black bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
              <span>🌟</span>
              <span>Slide {{ currentSlide.slide_number }}: {{ getSlideCategory(currentSlide.slide_number) }}</span>
            </div>
            <h2 class="text-2xl sm:text-3xl font-black text-white tracking-tight leading-snug">
              {{ currentSlide.title }}
            </h2>
          </div>

          <!-- Slide Body: Bullets on Left, Visual Component on Right -->
          <div class="grid grid-cols-1 md:grid-cols-12 gap-6 items-center flex-1 my-2">
            <!-- Bullet Points (Cols 7) -->
            <div class="md:col-span-7 space-y-3">
              <div
                v-for="(bullet, bIdx) in currentSlide.bullets"
                :key="bIdx"
                class="flex items-start gap-3 p-3 rounded-2xl bg-slate-800/60 border border-slate-700/60 backdrop-blur-sm transition-all duration-300 hover:border-slate-600"
                :style="{ animationDelay: `${bIdx * 150}ms` }"
              >
                <span class="inline-flex items-center justify-center w-6 h-6 rounded-full bg-amber-400 text-slate-950 text-xs font-black shrink-0 mt-0.5 shadow-sm">
                  {{ bIdx + 1 }}
                </span>
                <span class="text-sm sm:text-base text-slate-200 font-medium leading-relaxed">
                  {{ bullet }}
                </span>
              </div>
            </div>

            <!-- Dynamic Visual Math Component (Cols 5) -->
            <div class="md:col-span-5 flex flex-col items-center justify-center p-4 rounded-3xl bg-slate-800/40 border border-slate-700/50 backdrop-blur min-h-[180px]">
              <!-- 1. FractionBar -->
              <FractionBar
                v-if="currentSlide.visual_component === 'FractionBar'"
                :numerator="Number(visualProps.numerator) || 3"
                :denominator="Number(visualProps.denominator) || 4"
                :secondary-numerator="Number(visualProps.secondaryNumerator) || 0"
              />

              <!-- 2. NumberLine -->
              <NumberLine
                v-else-if="currentSlide.visual_component === 'NumberLine'"
                :start-val="Number(visualProps.startVal ?? 0)"
                :end-val="Number(visualProps.endVal ?? 1)"
                :min="visualProps.min !== undefined ? Number(visualProps.min) : undefined"
                :max="visualProps.max !== undefined ? Number(visualProps.max) : undefined"
              />

              <!-- 3. ShapeDiagram -->
              <ShapeDiagram
                v-else-if="currentSlide.visual_component === 'ShapeDiagram'"
                :shape="visualProps.shape || 'rectangle'"
                :width="Number(visualProps.width) || 8"
                :height="Number(visualProps.height) || 5"
                :highlight="visualProps.highlight || 'area'"
              />

              <!-- 4. Topic Graphic / Badge Fallback -->
              <div v-else class="flex flex-col items-center justify-center text-center p-6 space-y-3">
                <div class="w-20 h-20 rounded-3xl bg-gradient-to-br from-amber-400 to-amber-600 flex items-center justify-center text-4xl shadow-game-amber animate-bounce-gentle">
                  {{ visualProps.emoji || '🎯' }}
                </div>
                <span class="text-xs font-extrabold uppercase tracking-widest text-slate-300">
                  {{ visualProps.label || 'MathQuest Exploration' }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </transition>
    </div>

    <!-- Highlighted Captions / Subtitle Bar -->
    <div class="px-6 py-4 bg-slate-900 border-t border-slate-800 flex items-start gap-3">
      <span class="text-base shrink-0 mt-0.5 text-amber-400">💬</span>
      <div class="flex-1 text-xs sm:text-sm leading-relaxed min-h-[44px]">
        <span class="text-slate-500 font-bold mr-2 uppercase tracking-wider text-[10px]">
          Narration:
        </span>
        <span
          v-for="(word, wIdx) in narrationWords"
          :key="wIdx"
          :class="[
            'transition-all duration-150 inline-block mr-1',
            wIdx === activeWordIndex
              ? 'bg-amber-400 text-slate-950 font-black px-1.5 py-0.5 rounded shadow-sm scale-105'
              : wIdx < activeWordIndex
                ? 'text-slate-100 font-medium'
                : 'text-slate-400'
          ]"
        >
          {{ word }}
        </span>
      </div>
    </div>

    <!-- Bottom Controls Deck -->
    <div class="px-5 py-4 bg-slate-950 border-t border-slate-800 flex items-center justify-between flex-wrap gap-4">
      <!-- Playback Actions: Prev, Play/Pause, Next, Restart -->
      <div class="flex items-center gap-2 sm:gap-3">
        <!-- Restart Button -->
        <button
          type="button"
          @click="restartVideo"
          class="p-2.5 rounded-2xl bg-slate-800 text-slate-300 hover:text-white hover:bg-slate-700 transition border border-slate-700 cursor-pointer"
          title="Restart Video from Slide 1"
        >
          <span class="text-lg">🔄</span>
        </button>

        <!-- Previous Slide Button -->
        <button
          type="button"
          @click="prevSlide"
          :disabled="currentSlideIndex === 0"
          class="p-2.5 rounded-2xl bg-slate-800 text-slate-300 hover:text-white hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed transition border border-slate-700 cursor-pointer"
          title="Previous Slide"
        >
          <span class="text-lg">⏮️</span>
        </button>

        <!-- Main Play/Pause Button -->
        <button
          type="button"
          @click="togglePlay"
          class="btn-game-amber px-6 py-2.5 text-sm sm:text-base font-black shadow-game-amber flex items-center gap-2 cursor-pointer hover:scale-105 transition-transform"
        >
          <span>{{ isPlaying ? '⏸️ Pause' : '▶️ Play Video' }}</span>
        </button>

        <!-- Next Slide Button -->
        <button
          type="button"
          @click="nextSlide"
          :disabled="currentSlideIndex === totalSlides - 1"
          class="p-2.5 rounded-2xl bg-slate-800 text-slate-300 hover:text-white hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed transition border border-slate-700 cursor-pointer"
          title="Next Slide"
        >
          <span class="text-lg">⏭️</span>
        </button>
      </div>

      <!-- Playback Speed Control -->
      <div class="flex items-center gap-2">
        <span class="text-xs font-bold text-slate-400">Speed:</span>
        <div class="inline-flex rounded-xl bg-slate-900 border border-slate-800 p-1">
          <button
            v-for="spd in [0.75, 1.0, 1.25, 1.5]"
            :key="spd"
            type="button"
            @click="setSpeed(spd)"
            :class="[
              'px-2.5 py-1 rounded-lg text-xs font-extrabold transition cursor-pointer',
              playbackSpeed === spd
                ? 'bg-amber-400 text-slate-950 font-black shadow-xs'
                : 'text-slate-400 hover:text-slate-200'
            ]"
          >
            {{ spd }}x
          </button>
        </div>

        <!-- Mute Audio Toggle -->
        <button
          type="button"
          @click="toggleMute"
          class="p-2 rounded-xl bg-slate-900 text-slate-300 hover:text-white border border-slate-800 transition cursor-pointer"
          :title="isSpeechMuted ? 'Unmute Audio Narration' : 'Mute Audio Narration'"
        >
          <span class="text-sm">{{ isSpeechMuted ? '🔇' : '🔊' }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import type { Slide } from '~/composables/useApi'

const props = withDefaults(
  defineProps<{
    slides: Slide[]
    title?: string
    topic?: string
    grade?: number
  }>(),
  {
    title: 'MathQuest Interactive Video Lesson',
    topic: 'fractions',
    grade: 5,
  }
)

const emit = defineEmits<{
  (e: 'finished'): void
}>()

// State
const currentSlideIndex = ref<number>(0)
const isPlaying = ref<boolean>(false)
const playbackSpeed = ref<number>(1.0)
const isSpeechMuted = ref<boolean>(false)
const hasSpeechSupport = ref<boolean>(true)
const activeWordIndex = ref<number>(-1)
const slideProgressPercent = ref<number>(0)

let progressTimer: any = null
let currentUtterance: SpeechSynthesisUtterance | null = null

const totalSlides = computed(() => props.slides?.length || 6)

const currentSlide = computed<Slide>(() => {
  if (props.slides && props.slides[currentSlideIndex.value]) {
    return props.slides[currentSlideIndex.value]
  }
  // Default slide fallback
  return {
    slide_number: currentSlideIndex.value + 1,
    title: 'Exploring MathQuest Georgia',
    bullets: ['Learn math concepts step by step', 'Visualize problems with models', 'Prepare for victory!'],
    narration: 'Welcome to this interactive math lesson. Follow along with each step to master this topic!',
    visual_component: 'TopicGraphic',
    visual_props: {},
    duration_seconds: 8,
  }
})

const visualProps = computed(() => currentSlide.value.visual_props || {})

const narrationWords = computed(() => {
  return currentSlide.value.narration ? currentSlide.value.narration.split(/\s+/) : []
})

const getSlideCategory = (num: number) => {
  const categories = [
    'Mission Brief',
    'Core Concept',
    'Visual Deep Dive',
    'Worked Solution',
    'Trap Alert',
    'Quest Ready',
  ]
  return categories[num - 1] || 'Lesson'
}

// Check speech synthesis support on mount
const checkSpeechSupport = () => {
  if (typeof window === 'undefined' || !('speechSynthesis' in window) || !('SpeechSynthesisUtterance' in window)) {
    hasSpeechSupport.value = false
    console.warn('Web Speech API is not supported in this browser. Running in visual timer mode.')
  } else {
    hasSpeechSupport.value = true
  }
}

// Stop any running speech or progress timers
const stopCurrentSpeech = () => {
  if (progressTimer) {
    clearInterval(progressTimer)
    progressTimer = null
  }
  if (typeof window !== 'undefined' && window.speechSynthesis) {
    window.speechSynthesis.cancel()
  }
  currentUtterance = null
}

// Start narration and timer for the active slide
const playCurrentSlide = () => {
  stopCurrentSpeech()
  activeWordIndex.value = -1
  slideProgressPercent.value = 0

  if (!isPlaying.value) return

  const slideDurationSeconds = Math.max(4, currentSlide.value.duration_seconds || 8) / playbackSpeed.value
  const startTime = Date.now()
  const durationMs = slideDurationSeconds * 1000

  // Interval timer to update the visual progress bar smoothly
  progressTimer = setInterval(() => {
    if (!isPlaying.value) {
      clearInterval(progressTimer)
      return
    }
    const elapsed = Date.now() - startTime
    const percent = Math.min(100, (elapsed / durationMs) * 100)
    slideProgressPercent.value = percent

    // In visual fallback mode or muted mode, simulate word-by-word caption highlight
    if (!hasSpeechSupport.value || isSpeechMuted.value) {
      const wordsCount = narrationWords.value.length
      if (wordsCount > 0) {
        const wordIdx = Math.min(wordsCount - 1, Math.floor((elapsed / durationMs) * wordsCount))
        activeWordIndex.value = wordIdx
      }
    }

    if (percent >= 100) {
      clearInterval(progressTimer)
      progressTimer = null
      onSlideFinished()
    }
  }, 100)

  // Web Speech API Narration
  if (hasSpeechSupport.value && !isSpeechMuted.value && typeof window !== 'undefined' && window.speechSynthesis) {
    try {
      const utt = new SpeechSynthesisUtterance(currentSlide.value.narration)
      utt.rate = playbackSpeed.value
      utt.pitch = 1.05

      // Pick an English voice
      const voices = window.speechSynthesis.getVoices()
      const englishVoice = voices.find((v) => v.lang.startsWith('en') && (v.name.includes('Natural') || v.name.includes('Google') || v.name.includes('Samantha') || v.name.includes('David'))) || voices.find((v) => v.lang.startsWith('en'))
      if (englishVoice) {
        utt.voice = englishVoice
      }

      // Word boundary event for highlighted captions
      utt.onboundary = (event) => {
        if (event.name === 'word') {
          const charIndex = event.charIndex
          const textUpToChar = currentSlide.value.narration.substring(0, charIndex).trim()
          activeWordIndex.value = textUpToChar ? textUpToChar.split(/\s+/).length : 0
        }
      }

      utt.onend = () => {
        // If speech ended before the visual duration, let the visual timer finish or advance
        if (slideProgressPercent.value < 85) {
          slideProgressPercent.value = 100
        }
      }

      utt.onerror = (e) => {
        console.warn('SpeechSynthesis error:', e)
      }

      currentUtterance = utt
      window.speechSynthesis.speak(utt)
    } catch (err) {
      console.warn('Could not initialize speech utterance:', err)
    }
  }
}

// Auto-advance or complete video
const onSlideFinished = () => {
  if (!isPlaying.value) return

  if (currentSlideIndex.value < totalSlides.value - 1) {
    // Wait a brief beat before transitioning to the next slide
    setTimeout(() => {
      if (!isPlaying.value) return
      currentSlideIndex.value++
      playCurrentSlide()
    }, 600)
  } else {
    // Finished all 6 slides
    isPlaying.value = false
    slideProgressPercent.value = 100
    emit('finished')
  }
}

// Player controls
const togglePlay = () => {
  isPlaying.value = !isPlaying.value
  if (isPlaying.value) {
    playCurrentSlide()
  } else {
    stopCurrentSpeech()
  }
}

const restartVideo = () => {
  currentSlideIndex.value = 0
  isPlaying.value = true
  playCurrentSlide()
}

const nextSlide = () => {
  if (currentSlideIndex.value < totalSlides.value - 1) {
    currentSlideIndex.value++
    if (isPlaying.value) {
      playCurrentSlide()
    } else {
      activeWordIndex.value = -1
      slideProgressPercent.value = 0
    }
  }
}

const prevSlide = () => {
  if (currentSlideIndex.value > 0) {
    currentSlideIndex.value--
    if (isPlaying.value) {
      playCurrentSlide()
    } else {
      activeWordIndex.value = -1
      slideProgressPercent.value = 0
    }
  }
}

const jumpToSlide = (idx: number) => {
  if (idx >= 0 && idx < totalSlides.value) {
    currentSlideIndex.value = idx
    if (isPlaying.value) {
      playCurrentSlide()
    } else {
      activeWordIndex.value = -1
      slideProgressPercent.value = 0
    }
  }
}

const setSpeed = (spd: number) => {
  playbackSpeed.value = spd
  if (isPlaying.value) {
    playCurrentSlide()
  }
}

const toggleMute = () => {
  isSpeechMuted.value = !isSpeechMuted.value
  if (isSpeechMuted.value) {
    if (typeof window !== 'undefined' && window.speechSynthesis) {
      window.speechSynthesis.cancel()
    }
  } else if (isPlaying.value) {
    playCurrentSlide()
  }
}

// Re-read when slide changes manually
watch(currentSlideIndex, () => {
  activeWordIndex.value = -1
  slideProgressPercent.value = 0
})

onMounted(() => {
  checkSpeechSupport()
})

onBeforeUnmount(() => {
  stopCurrentSpeech()
})
</script>

<style scoped>
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.3s ease-out;
}
.slide-fade-enter-from {
  opacity: 0;
  transform: translateX(16px);
}
.slide-fade-leave-to {
  opacity: 0;
  transform: translateX(-16px);
}

@keyframes bounce-gentle {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-8px);
  }
}

.animate-bounce-gentle {
  animation: bounce-gentle 2.5s infinite ease-in-out;
}
</style>
