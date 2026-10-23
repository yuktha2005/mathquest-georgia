<template>
  <div class="w-full max-w-md mx-auto space-y-2 select-none">
    <!-- Header -->
    <div class="flex items-center justify-between text-xs font-black text-slate-600">
      <span class="flex items-center gap-1.5">
        <span>📐</span>
        <span>Geometric Diagram ({{ shapeLabel }})</span>
      </span>
      <span class="font-mono text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded-md border border-indigo-200 uppercase">
        {{ highlight }}
      </span>
    </div>

    <!-- SVG Container -->
    <div class="bg-white p-4 rounded-2xl border-2 border-indigo-100 shadow-sm flex flex-col items-center justify-center">
      <svg
        viewBox="0 0 320 180"
        class="w-full h-auto max-h-40"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <linearGradient id="shapeGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#e0e7ff" />
            <stop offset="100%" stop-color="#c7d2fe" />
          </linearGradient>
          <marker
            id="dimArrow"
            markerWidth="6"
            markerHeight="6"
            refX="3"
            refY="3"
            orient="auto"
          >
            <path d="M0,0 L6,3 L0,6 Z" fill="#6366f1" />
          </marker>
        </defs>

        <!-- 1. Rectangle or Square -->
        <g v-if="shape !== 'triangle'">
          <!-- Main Rectangle Shape -->
          <rect
            :x="rectX"
            :y="rectY"
            :width="rectW"
            :height="rectH"
            rx="8"
            fill="url(#shapeGradient)"
            :stroke="highlight === 'perimeter' ? '#4f46e5' : '#818cf8'"
            :stroke-width="highlight === 'perimeter' ? 3.5 : 2"
            :stroke-dasharray="highlight === 'perimeter' ? '6,3' : 'none'"
          />

          <!-- Center Calculation Pill -->
          <g :transform="`translate(${rectX + rectW / 2}, ${rectY + rectH / 2})`">
            <rect
              :x="-innerPillW / 2"
              y="-12"
              :width="innerPillW"
              height="24"
              rx="12"
              fill="#ffffff"
              stroke="#c7d2fe"
              stroke-width="1.5"
            />
            <text
              x="0"
              y="4"
              text-anchor="middle"
              font-size="11"
              font-weight="bold"
              fill="#3730a3"
              font-family="Fredoka, sans-serif"
            >
              {{ centerCalculationText }}
            </text>
          </g>

          <!-- Top Width Dimension Label & Line -->
          <line
            :x1="rectX"
            :y1="rectY - 12"
            :x2="rectX + rectW"
            :y2="rectY - 12"
            stroke="#6366f1"
            stroke-width="1.5"
            marker-start="url(#dimArrow)"
            marker-end="url(#dimArrow)"
          />
          <text
            :x="rectX + rectW / 2"
            :y="rectY - 18"
            text-anchor="middle"
            font-size="12"
            font-weight="bold"
            fill="#4338ca"
            font-family="Fredoka, sans-serif"
          >
            {{ width }} {{ unit }}
          </text>

          <!-- Right Height Dimension Label & Line -->
          <line
            :x1="rectX + rectW + 14"
            :y1="rectY"
            :x2="rectX + rectW + 14"
            :y2="rectY + rectH"
            stroke="#6366f1"
            stroke-width="1.5"
            marker-start="url(#dimArrow)"
            marker-end="url(#dimArrow)"
          />
          <text
            :x="rectX + rectW + 22"
            :y="rectY + rectH / 2 + 4"
            text-anchor="start"
            font-size="12"
            font-weight="bold"
            fill="#4338ca"
            font-family="Fredoka, sans-serif"
          >
            {{ height }} {{ unit }}
          </text>
        </g>

        <!-- 2. Triangle -->
        <g v-else>
          <!-- Triangle Polygon -->
          <polygon
            :points="`${triX1},${triY1} ${triX2},${triY2} ${triX3},${triY3}`"
            fill="url(#shapeGradient)"
            :stroke="highlight === 'perimeter' ? '#4f46e5' : '#818cf8'"
            :stroke-width="highlight === 'perimeter' ? 3.5 : 2"
          />

          <!-- Altitude Height Dashed Line -->
          <line
            :x1="triX2"
            :y1="triY2"
            :x2="triX2"
            :y2="triY1"
            stroke="#4f46e5"
            stroke-width="2"
            stroke-dasharray="4,4"
          />

          <!-- Right angle symbol at base of height -->
          <path
            :d="`M ${triX2 - 8} ${triY1} L ${triX2 - 8} ${triY1 - 8} L ${triX2} ${triY1 - 8}`"
            fill="none"
            stroke="#4f46e5"
            stroke-width="1.5"
          />

          <!-- Base Dimension Line & Text -->
          <line
            :x1="triX1"
            :y1="triY1 + 14"
            :x2="triX3"
            :y2="triY3 + 14"
            stroke="#6366f1"
            stroke-width="1.5"
            marker-start="url(#dimArrow)"
            marker-end="url(#dimArrow)"
          />
          <text
            :x="(triX1 + triX3) / 2"
            :y="triY1 + 28"
            text-anchor="middle"
            font-size="12"
            font-weight="bold"
            fill="#4338ca"
            font-family="Fredoka, sans-serif"
          >
            base = {{ width }} {{ unit }}
          </text>

          <!-- Height Label -->
          <text
            :x="triX2 - 8"
            :y="(triY2 + triY1) / 2"
            text-anchor="end"
            font-size="11"
            font-weight="bold"
            fill="#4338ca"
            font-family="Fredoka, sans-serif"
          >
            h = {{ height }} {{ unit }}
          </text>

          <!-- Triangle Area Formula Pill -->
          <g :transform="`translate(${triX2 + 35}, ${(triY2 + triY1) / 2 + 10})`">
            <rect
              x="-45"
              y="-10"
              width="90"
              height="20"
              rx="10"
              fill="#ffffff"
              stroke="#c7d2fe"
              stroke-width="1.5"
            />
            <text
              x="0"
              y="4"
              text-anchor="middle"
              font-size="10"
              font-weight="bold"
              fill="#3730a3"
              font-family="Fredoka, sans-serif"
            >
              Area = (b × h) ÷ 2
            </text>
          </g>
        </g>
      </svg>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    shape?: 'rectangle' | 'square' | 'triangle'
    width: number
    height: number
    unit?: string
    highlight?: 'area' | 'perimeter'
  }>(),
  {
    shape: 'rectangle',
    unit: 'units',
    highlight: 'area',
  }
)

const shapeLabel = computed(() => {
  if (props.shape === 'triangle') return 'Triangle'
  if (props.shape === 'square' || props.width === props.height) return 'Square'
  return 'Rectangle'
})

// Bounding sizes for SVG viewBox (320 x 180)
const rectW = computed(() => {
  const aspect = props.width / (props.height || 1)
  if (aspect >= 1) return 180
  return Math.max(90, Math.min(180, 180 * aspect))
})

const rectH = computed(() => {
  const aspect = props.width / (props.height || 1)
  if (aspect >= 1) return Math.max(70, Math.min(110, 180 / aspect))
  return 110
})

const rectX = computed(() => (320 - rectW.value) / 2 - 15)
const rectY = computed(() => (180 - rectH.value) / 2 + 5)

const innerPillW = computed(() => (props.highlight === 'perimeter' ? 140 : 120))

const centerCalculationText = computed(() => {
  if (props.highlight === 'perimeter') {
    const p = 2 * (props.width + props.height)
    return `P = 2(${props.width} + ${props.height}) = ${p} ${props.unit}`
  }
  const a = props.width * props.height
  return `Area = ${props.width} × ${props.height} = ${a} ${props.unit}²`
})

// Triangle coordinates (base on bottom, vertex on top)
const triX1 = 60
const triY1 = 140
const triX2 = 140
const triY2 = 35
const triX3 = 240
const triY3 = 140
</script>
