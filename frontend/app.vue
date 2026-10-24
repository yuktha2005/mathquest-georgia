<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useApi } from '~/composables/useApi'
import { useSessionStore } from '~/stores/session'
import { useAuthStore } from '~/stores/auth'

const { checkHealth } = useApi()
const sessionStore = useSessionStore()
const authStore = useAuthStore()

onMounted(async () => {
  sessionStore.loadFromStorage()
  await authStore.init()

  // Load dyslexia font preference from localStorage
  if (import.meta.client) {
    const savedDyslexia = localStorage.getItem('mathquest_dyslexia_font')
    if (savedDyslexia === 'true') {
      document.documentElement.classList.add('dyslexia-font')
    }
  }

  // Gentle background ping to warm up backend on load
  try {
    await checkHealth()
  } catch (e) {
    // Expected if cold start or local backend waking up
  }
})
</script>
