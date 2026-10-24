import { ref } from 'vue'

const isDyslexic = ref(false)
const isReadAloud = ref(false)
const isReducedMotion = ref(false)
let isInitialized = false

export function useAccessibility() {
  if (import.meta.client && !isInitialized) {
    isInitialized = true

    // 1. Restore Dyslexia Font preference
    const savedDyslexia = localStorage.getItem('mathquest_dyslexia_font')
    if (savedDyslexia === 'true') {
      isDyslexic.value = true
      document.documentElement.classList.add('dyslexia-font')
    }

    // 2. Restore Read-Aloud preference
    const savedReadAloud = localStorage.getItem('mathquest_read_aloud')
    if (savedReadAloud === 'true') {
      isReadAloud.value = true
    }

    // 3. Restore Reduced Motion preference
    const savedReducedMotion = localStorage.getItem('mathquest_reduced_motion')
    if (savedReducedMotion === 'true') {
      isReducedMotion.value = true
      document.documentElement.classList.add('reduced-motion')
    } else if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      isReducedMotion.value = true
      document.documentElement.classList.add('reduced-motion')
    }
  }

  function toggleDyslexia(val?: boolean) {
    isDyslexic.value = typeof val === 'boolean' ? val : !isDyslexic.value
    if (import.meta.client) {
      if (isDyslexic.value) {
        document.documentElement.classList.add('dyslexia-font')
        localStorage.setItem('mathquest_dyslexia_font', 'true')
      } else {
        document.documentElement.classList.remove('dyslexia-font')
        localStorage.setItem('mathquest_dyslexia_font', 'false')
      }
    }
  }

  function toggleReadAloud(val?: boolean) {
    isReadAloud.value = typeof val === 'boolean' ? val : !isReadAloud.value
    if (import.meta.client) {
      localStorage.setItem('mathquest_read_aloud', isReadAloud.value ? 'true' : 'false')
      if (isReadAloud.value) {
        speak('Read aloud is now enabled.')
      } else if (window.speechSynthesis) {
        window.speechSynthesis.cancel()
      }
    }
  }

  function toggleReducedMotion(val?: boolean) {
    isReducedMotion.value = typeof val === 'boolean' ? val : !isReducedMotion.value
    if (import.meta.client) {
      if (isReducedMotion.value) {
        document.documentElement.classList.add('reduced-motion')
        localStorage.setItem('mathquest_reduced_motion', 'true')
      } else {
        document.documentElement.classList.remove('reduced-motion')
        localStorage.setItem('mathquest_reduced_motion', 'false')
      }
    }
  }

  function speak(text: string) {
    if (!import.meta.client || !window.speechSynthesis) return
    window.speechSynthesis.cancel()
    const cleanText = text.replace(/<[^>]*>/g, '').replace(/[#*_`]/g, '')
    const utterance = new SpeechSynthesisUtterance(cleanText)
    utterance.rate = 0.95
    utterance.pitch = 1.05
    window.speechSynthesis.speak(utterance)
  }

  function stopSpeaking() {
    if (import.meta.client && window.speechSynthesis) {
      window.speechSynthesis.cancel()
    }
  }

  return {
    isDyslexic,
    isReadAloud,
    isReducedMotion,
    toggleDyslexia,
    toggleReadAloud,
    toggleReducedMotion,
    speak,
    stopSpeaking,
  }
}
