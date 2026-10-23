<template>
  <div class="w-full max-w-md mx-auto space-y-2 select-none">
    <!-- Title / Subtitle -->
    <div class="flex items-center justify-between text-xs font-black text-slate-600">
      <span class="flex items-center gap-1.5">
        <span>📊</span>
        <span>Fraction Visual Model</span>
      </span>
      <span class="font-mono text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded-md border border-indigo-200">
        {{ displayFraction }}
      </span>
    </div>

    <!-- SVG Fraction Bar Diagram -->
    <div class="bg-white p-3 rounded-2xl border-2 border-indigo-100 shadow-sm flex flex-col items-center justify-center">
      <svg
        :viewBox="`0 0 ${barWidth} ${barHeight}`"
        class="w-full h-auto max-h-20 drop-shadow-sm"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <!-- Primary Segment Gradient -->
          <linearGradient id="fractionPrimary" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#3b82f6" />
            <stop offset="100%" stop-color="#2563eb" />
          </linearGradient>
          <!-- Secondary Segment Gradient (e.g. for + operation) -->
          <linearGradient id="fractionSecondary" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#10b981" />
            <stop offset="100%" stop-color="#059669" />
          </linearGradient>
          <!-- Unshaded Segment Gradient -->
          <linearGradient id="fractionEmpty" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#f8fafc" />
            <stop offset="100%" stop-color="#f1f5f9" />
          </linearGradient>
        </defs>

        <!-- Background Container Bar -->
        <rect
          x="2"
          y="2"
          :width="barWidth - 4"
          :height="barHeight - 4"
          rx="12"
          ry="12"
          fill="#f8fafc"
          stroke="#cbd5e1"
          stroke-width="2"
        />

        <!-- Segment Blocks -->
        <g v-for="(seg, idx) in segments" :key="idx">
          <rect
            :x="seg.x"
            :y="4"
            :width="seg.width"
            :height="barHeight - 8"
            :rx="idx === 0 || idx === segments.length - 1 ? 8 : 2"
            :fill="seg.fill"
            stroke="#ffffff"
            stroke-width="2"
            class="transition-colors duration-300"
          />

          <!-- Unit Fraction Text Label inside segment -->
          <text
            :x="seg.x + seg.width / 2"
            :y="barHeight / 2 + 5"
            text-anchor="middle"
            :fill="seg.isShaded ? '#ffffff' : '#94a3b8'"
            font-size="12"
            font-weight="bold"
            font-family="Fredoka, sans-serif"
          >
            1/{{ safeDenominator }}
          </text>
        </g>
      </svg>

      <!-- Visual Legend Breakdown -->
      <div class="mt-2 text-center text-xs font-bold text-slate-500">
        <span class="text-indigo-600 font-extrabold">{{ safeNumerator }}</span>
        <span> of </span>
        <span class="text-slate-700 font-extrabold">{{ safeDenominator }}</span>
        <span> equal parts shaded</span>
        <span v-if="secondaryNumerator" class="text-emerald-600 ml-1">
          (+{{ secondaryNumerator }} added)
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    numerator: number
    denominator: number
    secondaryNumerator?: number
  }>(),
  {
    secondaryNumerator: 0,
  }
)

const barWidth = 360
const barHeight = 56

const safeDenominator = computed(() => Math.max(1, Math.min(20, Math.round(props.denominator || 4))))
const safeNumerator = computed(() => Math.max(0, Math.min(safeDenominator.value, Math.round(props.numerator || 1))))

const displayFraction = computed(() => {
  if (props.secondaryNumerator > 0) {
    return `${safeNumerator.value}/${safeDenominator.value} + ${props.secondaryNumerator}/${safeDenominator.value}`
  }
  return `${safeNumerator.value}/${safeDenominator.value}`
})

const segments = computed(() => {
  const count = safeDenominator.value
  const segW = (barWidth - 8) / count
  const list = []

  for (let i = 0; i < count; i++) {
    const isPrimary = i < safeNumerator.value
    const isSecondary =
      props.secondaryNumerator > 0 &&
      i >= safeNumerator.value &&
      i < safeNumerator.value + props.secondaryNumerator

    let fill = 'url(#fractionEmpty)'
    if (isPrimary) {
      fill = 'url(#fractionPrimary)'
    } else if (isSecondary) {
      fill = 'url(#fractionSecondary)'
    }

    list.push({
      x: 4 + i * segW,
      width: segW,
      isShaded: isPrimary || isSecondary,
      fill,
    })
  }

  return list
})
</script>
