<template>
  <div class="w-full max-w-md mx-auto space-y-2 select-none">
    <!-- Header -->
    <div class="flex items-center justify-between text-xs font-black text-slate-600">
      <span class="flex items-center gap-1.5">
        <span>📏</span>
        <span>Number Line Vector</span>
      </span>
      <span class="font-mono text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded-md border border-indigo-200">
        {{ startVal }} ➔ {{ endVal }} ({{ jumpSign }}{{ jumpDiff.toFixed(2) }})
      </span>
    </div>

    <!-- SVG Container -->
    <div class="bg-white p-4 rounded-2xl border-2 border-indigo-100 shadow-sm flex flex-col items-center justify-center">
      <svg
        :viewBox="`0 0 ${width} ${height}`"
        class="w-full h-auto max-h-28"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <marker
            id="numLineArrow"
            markerWidth="8"
            markerHeight="8"
            refX="6"
            refY="3"
            orient="auto"
          >
            <path d="M0,0 L6,3 L0,6 Z" fill="#64748b" />
          </marker>
          <marker
            id="jumpArrow"
            markerWidth="8"
            markerHeight="8"
            refX="5"
            refY="3"
            orient="auto"
          >
            <path d="M0,0 L6,3 L0,6 Z" fill="#6366f1" />
          </marker>
        </defs>

        <!-- Main Horizontal Axis -->
        <line
          :x1="paddingX"
          :y1="axisY"
          :x2="width - paddingX"
          :y2="axisY"
          stroke="#94a3b8"
          stroke-width="3"
          stroke-linecap="round"
          marker-end="url(#numLineArrow)"
        />

        <!-- Tick Marks & Numbers -->
        <g v-for="tick in ticks" :key="tick.value">
          <line
            :x1="tick.x"
            :y1="axisY - 6"
            :x2="tick.x"
            :y2="axisY + 6"
            stroke="#64748b"
            stroke-width="2"
          />
          <text
            :x="tick.x"
            :y="axisY + 22"
            text-anchor="middle"
            font-size="11"
            font-weight="bold"
            fill="#475569"
            font-family="Fredoka, sans-serif"
          >
            {{ tick.label }}
          </text>
        </g>

        <!-- Curved Jump Arc -->
        <path
          v-if="startX !== endX"
          :d="arcPath"
          fill="none"
          stroke="#6366f1"
          stroke-width="3.5"
          stroke-dasharray="6,4"
          marker-end="url(#jumpArrow)"
          class="animate-pulse"
        />

        <!-- Jump Label Pill -->
        <g v-if="startX !== endX" :transform="`translate(${(startX + endX) / 2}, ${axisY - arcHeight - 10})`">
          <rect
            x="-28"
            y="-10"
            width="56"
            height="20"
            rx="10"
            fill="#4f46e5"
          />
          <text
            x="0"
            y="4"
            text-anchor="middle"
            font-size="11"
            font-weight="bold"
            fill="#ffffff"
            font-family="Fredoka, sans-serif"
          >
            {{ jumpSign }}{{ jumpDiff.toFixed(2) }}
          </text>
        </g>

        <!-- Start Point Dot -->
        <circle
          :cx="startX"
          :cy="axisY"
          r="6"
          fill="#3b82f6"
          stroke="#ffffff"
          stroke-width="2"
        />

        <!-- End Point Dot -->
        <circle
          :cx="endX"
          :cy="axisY"
          r="6.5"
          fill="#10b981"
          stroke="#ffffff"
          stroke-width="2"
        />
      </svg>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    startVal: number
    endVal: number
    min?: number
    max?: number
  }>(),
  {
    min: undefined,
    max: undefined,
  }
)

const width = 380
const height = 90
const paddingX = 24
const axisY = 60
const arcHeight = 35

const effectiveMin = computed(() => {
  if (props.min !== undefined) return props.min
  const lower = Math.min(props.startVal, props.endVal)
  return Math.floor(lower)
})

const effectiveMax = computed(() => {
  if (props.max !== undefined) return props.max
  const upper = Math.max(props.startVal, props.endVal)
  return Math.ceil(upper) === effectiveMin.value ? effectiveMin.value + 1 : Math.ceil(upper)
})

const jumpDiff = computed(() => Math.abs(props.endVal - props.startVal))
const jumpSign = computed(() => (props.endVal >= props.startVal ? '+' : '−'))

const scaleX = (val: number): number => {
  const range = effectiveMax.value - effectiveMin.value || 1
  const ratio = (val - effectiveMin.value) / range
  const innerW = width - paddingX * 2
  return paddingX + ratio * innerW
}

const startX = computed(() => scaleX(props.startVal))
const endX = computed(() => scaleX(props.endVal))

const arcPath = computed(() => {
  const sx = startX.value
  const ex = endX.value
  const mx = (sx + ex) / 2
  const my = axisY - arcHeight
  return `M ${sx} ${axisY} Q ${mx} ${my} ${ex} ${axisY}`
})

const ticks = computed(() => {
  const count = 5
  const step = (effectiveMax.value - effectiveMin.value) / count
  const items = []
  for (let i = 0; i <= count; i++) {
    const val = Number((effectiveMin.value + i * step).toFixed(2))
    items.push({
      value: val,
      x: scaleX(val),
      label: val % 1 === 0 ? String(val) : val.toFixed(1),
    })
  }
  return items
})
</script>
