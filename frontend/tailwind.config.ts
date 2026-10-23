import type { Config } from 'tailwindcss'

export default <Partial<Config>>{
  content: [
    './components/**/*.{vue,js,ts}',
    './layouts/**/*.vue',
    './pages/**/*.vue',
    './composables/**/*.{js,ts}',
    './app.vue',
  ],
  theme: {
    extend: {
      fontFamily: {
        fredoka: ['Fredoka', 'sans-serif'],
        outfit: ['Outfit', 'sans-serif'],
        lexend: ['Lexend', 'sans-serif'],
        sans: ['Fredoka', 'Outfit', 'sans-serif'],
      },
      colors: {
        quest: {
          blue: '#3b82f6',
          sky: '#0ea5e9',
          indigo: '#6366f1',
          purple: '#8b5cf6',
          pink: '#ec4899',
          rose: '#f43f5e',
          amber: '#f59e0b',
          yellow: '#fbbf24',
          emerald: '#10b981',
          green: '#22c55e',
          slate: '#334155',
          cream: '#fefce8',
          canvas: '#f8fafc',
        },
      },
      borderRadius: {
        '2xl': '1rem',
        '3xl': '1.5rem',
        '4xl': '2rem',
        '5xl': '2.5rem',
      },
      boxShadow: {
        'game-sm': '0 4px 0 rgba(0, 0, 0, 0.08)',
        'game': '0 6px 0 rgba(0, 0, 0, 0.12)',
        'game-lg': '0 10px 0 rgba(0, 0, 0, 0.14)',
        'game-blue': '0 6px 0 #1d4ed8',
        'game-green': '0 6px 0 #15803d',
        'game-purple': '0 6px 0 #6d28d9',
        'game-amber': '0 6px 0 #b45309',
        'game-rose': '0 6px 0 #be123c',
      },
      keyframes: {
        wiggle: {
          '0%, 100%': { transform: 'rotate(-3deg)' },
          '50%': { transform: 'rotate(3deg)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-6px)' },
        },
        pop: {
          '0%': { transform: 'scale(0.95)' },
          '50%': { transform: 'scale(1.04)' },
          '100%': { transform: 'scale(1)' },
        },
      },
      animation: {
        wiggle: 'wiggle 1s ease-in-out infinite',
        float: 'float 3s ease-in-out infinite',
        pop: 'pop 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275)',
      },
    },
  },
  plugins: [],
}
