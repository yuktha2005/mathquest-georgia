import { defineConfig } from 'vitest/config'
import path from 'path'

export default defineConfig({
  test: {
    environment: 'happy-dom',
    globals: true,
    include: ['tests/**/*.spec.ts'],
    exclude: ['tests/**/*.playwright.spec.ts', 'node_modules'],
  },
  define: {
    'import.meta.client': 'true',
  },
  resolve: {
    alias: {
      '~': path.resolve(import.meta.dirname, './'),
      '@': path.resolve(import.meta.dirname, './'),
    },
  },
})
