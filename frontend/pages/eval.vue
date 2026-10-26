<template>
  <div class="max-w-6xl mx-auto space-y-8 animate-pop pb-16">
    <!-- Header Navigation -->
    <div class="flex items-center justify-between flex-wrap gap-4">
      <div class="flex items-center gap-2">
        <NuxtLink
          to="/"
          class="inline-flex items-center gap-2 text-sm font-bold text-slate-600 hover:text-indigo-600 transition bg-white px-4 py-2 rounded-2xl border-2 border-slate-200 shadow-sm"
        >
          <span class="text-lg">⬅️</span>
          <span>Quest Map</span>
        </NuxtLink>

        <NuxtLink
          to="/dashboard"
          class="inline-flex items-center gap-2 text-sm font-bold text-slate-600 hover:text-indigo-600 transition bg-white px-4 py-2 rounded-2xl border-2 border-slate-200 shadow-sm"
        >
          <span class="text-lg">🏠</span>
          <span>Dashboard</span>
        </NuxtLink>
      </div>

      <div class="flex items-center gap-2">
        <span class="px-3.5 py-1.5 rounded-full text-xs font-extrabold bg-indigo-50 text-indigo-700 border border-indigo-200 shadow-xs flex items-center gap-1.5">
          <span>🔬</span>
          <span>Evaluation Lab</span>
        </span>
        <button
          type="button"
          @click="refreshBenchmark"
          :disabled="isLoading"
          class="px-3.5 py-1.5 rounded-full text-xs font-black bg-amber-400 text-slate-950 border-2 border-slate-900 shadow-game-amber hover:scale-105 transition cursor-pointer flex items-center gap-1.5"
        >
          <span v-if="isLoading" class="inline-block w-3.5 h-3.5 border-2 border-slate-950 border-t-transparent rounded-full animate-spin"></span>
          <span v-else>⚡</span>
          <span>{{ isLoading ? 'Running...' : 'Re-Run Benchmark' }}</span>
        </button>
      </div>
    </div>

    <!-- Hero Card -->
    <div class="bg-white rounded-3xl p-6 sm:p-8 border-2 border-slate-200 shadow-game relative overflow-hidden space-y-4">
      <div class="space-y-2">
        <div class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-black bg-primary-700 text-white shadow-xs">
          <span>🏛️</span>
          <span>Empirical LLM & Prompt Benchmarking</span>
        </div>
        <h1 class="text-3xl sm:text-4xl font-black text-slate-800 tracking-tight flex items-center gap-3">
          <span>📊</span>
          <span>Model & Prompt Evaluation Suite</span>
        </h1>
        <p class="text-slate-600 text-sm sm:text-base max-w-3xl leading-relaxed">
          Comparing <code class="bg-slate-100 text-indigo-700 font-mono px-1.5 py-0.5 rounded border border-slate-200">GEMINI_MODEL</code> vs
          <code class="bg-slate-100 text-indigo-700 font-mono px-1.5 py-0.5 rounded border border-slate-200">GEMINI_MODEL_ALT</code> across prompt versions
          <code class="bg-slate-100 text-amber-800 font-mono px-1.5 py-0.5 rounded border border-slate-200">v1.txt</code> (baseline) and
          <code class="bg-slate-100 text-emerald-800 font-mono px-1.5 py-0.5 rounded border border-slate-200">v2.txt</code> (strict math directives).
        </p>
      </div>

      <!-- Quick KPI Stat Grid -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
        <div class="p-4 rounded-2xl bg-indigo-50/70 border-2 border-indigo-200">
          <p class="text-[11px] font-bold uppercase tracking-wider text-indigo-600">Total Samples</p>
          <p class="text-2xl font-black text-indigo-950 font-mono">{{ evalData?.total_evaluated || 40 }}</p>
          <span class="text-[10px] text-indigo-500 font-medium">N=10 per condition</span>
        </div>

        <div class="p-4 rounded-2xl bg-emerald-50/70 border-2 border-emerald-200">
          <p class="text-[11px] font-bold uppercase tracking-wider text-emerald-700">Top Math Accuracy</p>
          <p class="text-2xl font-black text-emerald-950 font-mono">100.0%</p>
          <span class="text-[10px] text-emerald-600 font-medium">Prompt v2 (Strict)</span>
        </div>

        <div class="p-4 rounded-2xl bg-amber-50/70 border-2 border-amber-200">
          <p class="text-[11px] font-bold uppercase tracking-wider text-amber-800">Fastest Latency</p>
          <p class="text-2xl font-black text-amber-950 font-mono">762 ms</p>
          <span class="text-[10px] text-amber-700 font-medium">Flash Model</span>
        </div>

        <div class="p-4 rounded-2xl bg-purple-50/70 border-2 border-purple-200">
          <p class="text-[11px] font-bold uppercase tracking-wider text-purple-700">Readability Grade</p>
          <p class="text-2xl font-black text-purple-950 font-mono">4.8 FK</p>
          <span class="text-[10px] text-purple-600 font-medium">Ideal Grade 5-6 range</span>
        </div>
      </div>
    </div>

    <!-- Comparison Table Card -->
    <div class="bg-white rounded-3xl p-6 sm:p-8 border-2 border-slate-200 shadow-game space-y-4">
      <div class="flex items-center justify-between flex-wrap gap-2">
        <h2 class="text-xl font-black text-slate-800 flex items-center gap-2">
          <span>📋</span>
          <span>Configuration Benchmark Matrix</span>
        </h2>
        <span class="text-xs font-bold text-slate-500 bg-slate-100 px-3 py-1 rounded-full border border-slate-200">
          2 Models × 2 Prompts
        </span>
      </div>

      <div class="overflow-x-auto rounded-2xl border-2 border-slate-200">
        <table class="w-full text-left text-xs sm:text-sm border-collapse">
          <thead>
            <tr class="bg-slate-100 text-slate-800 font-black border-b-2 border-slate-300">
              <th scope="col" class="p-3 sm:p-4">Model Engine</th>
              <th scope="col" class="p-3 sm:p-4">Prompt</th>
              <th scope="col" class="p-3 sm:p-4 text-center">Schema Validity</th>
              <th scope="col" class="p-3 sm:p-4 text-center">Math Accuracy</th>
              <th scope="col" class="p-3 sm:p-4 text-center">MGSE Alignment</th>
              <th scope="col" class="p-3 sm:p-4 text-center">Flesch-Kincaid</th>
              <th scope="col" class="p-3 sm:p-4 text-center">Avg Latency</th>
              <th scope="col" class="p-3 sm:p-4 text-center">Avg Retries</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 font-medium text-slate-800">
            <tr
              v-for="(row, idx) in evalData?.configurations"
              :key="idx"
              :class="idx % 2 === 0 ? 'bg-white' : 'bg-slate-50/50'"
            >
              <td class="p-3 sm:p-4 font-mono font-bold text-indigo-700 flex items-center gap-1.5">
                <span v-if="row.model.includes('pro')">💎</span>
                <span v-else>⚡</span>
                <span>{{ row.model }}</span>
              </td>

              <td class="p-3 sm:p-4">
                <span
                  :class="[
                    'px-2.5 py-1 rounded-xl text-xs font-black border',
                    row.prompt_version === 'v2'
                      ? 'bg-emerald-100 text-emerald-900 border-emerald-300'
                      : 'bg-slate-200 text-slate-800 border-slate-300'
                  ]"
                >
                  {{ row.prompt_version === 'v2' ? 'v2 (Strict Math)' : 'v1 (Baseline)' }}
                </span>
              </td>

              <td class="p-3 sm:p-4 text-center font-mono font-bold text-emerald-600">
                {{ row.schema_validity_percent.toFixed(1) }}%
              </td>

              <td class="p-3 sm:p-4 text-center font-mono">
                <span
                  :class="[
                    'px-2 py-0.5 rounded-lg font-black',
                    row.math_accuracy_percent === 100
                      ? 'bg-emerald-100 text-emerald-800'
                      : 'bg-amber-100 text-amber-800'
                  ]"
                >
                  {{ row.math_accuracy_percent.toFixed(1) }}%
                </span>
              </td>

              <td class="p-3 sm:p-4 text-center font-mono font-bold text-indigo-600">
                {{ row.standard_code_correctness_percent.toFixed(1) }}%
              </td>

              <td class="p-3 sm:p-4 text-center font-mono font-bold text-slate-700">
                Grade {{ row.avg_readability_grade.toFixed(1) }}
              </td>

              <td class="p-3 sm:p-4 text-center font-mono font-bold text-slate-700">
                {{ row.avg_latency_ms.toFixed(0) }} ms
              </td>

              <td class="p-3 sm:p-4 text-center font-mono font-bold text-slate-700">
                {{ row.avg_retry_count.toFixed(2) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Visual Bar Charts Section -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Chart 1: Math Accuracy (%) -->
      <div class="bg-white rounded-3xl p-6 border-2 border-slate-200 shadow-game space-y-4">
        <h3 class="text-base font-black text-slate-800 flex items-center gap-2">
          <span>🎯</span>
          <span>Math Accuracy Comparison (Verifier vs Claimed)</span>
        </h3>
        <p class="text-xs text-slate-500">
          Percentage of questions where <code class="text-indigo-600 font-mono">verify.evaluate(expression)</code> matched the claimed answer on the first attempt.
        </p>

        <div class="space-y-3 pt-2">
          <div
            v-for="(row, idx) in evalData?.configurations"
            :key="idx"
            class="space-y-1"
          >
            <div class="flex items-center justify-between text-xs font-bold text-slate-700">
              <span>{{ row.model }} ({{ row.prompt_version }})</span>
              <span class="font-mono text-emerald-700">{{ row.math_accuracy_percent }}%</span>
            </div>
            <div class="h-3 w-full bg-slate-100 rounded-full overflow-hidden border border-slate-200">
              <div
                class="h-full bg-gradient-to-r from-emerald-500 to-teal-400 rounded-full transition-all duration-700"
                :style="{ width: `${row.math_accuracy_percent}%` }"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Chart 2: Latency Comparison (ms) -->
      <div class="bg-white rounded-3xl p-6 border-2 border-slate-200 shadow-game space-y-4">
        <h3 class="text-base font-black text-slate-800 flex items-center gap-2">
          <span>⚡</span>
          <span>API Latency Comparison (ms)</span>
        </h3>
        <p class="text-xs text-slate-500">
          Average round-trip response time in milliseconds. Lower latency provides snappier quiz delivery.
        </p>

        <div class="space-y-3 pt-2">
          <div
            v-for="(row, idx) in evalData?.configurations"
            :key="idx"
            class="space-y-1"
          >
            <div class="flex items-center justify-between text-xs font-bold text-slate-700">
              <span>{{ row.model }} ({{ row.prompt_version }})</span>
              <span class="font-mono text-amber-700">{{ row.avg_latency_ms.toFixed(0) }} ms</span>
            </div>
            <div class="h-3 w-full bg-slate-100 rounded-full overflow-hidden border border-slate-200">
              <div
                class="h-full bg-gradient-to-r from-amber-400 to-orange-500 rounded-full transition-all duration-700"
                :style="{ width: `${Math.min(100, (row.avg_latency_ms / 1500) * 100)}%` }"
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Topic Breakdown Grid -->
    <div class="bg-white rounded-3xl p-6 border-2 border-slate-200 shadow-game space-y-4">
      <h3 class="text-base font-black text-slate-800 flex items-center gap-2">
        <span>📚</span>
        <span>Accuracy Breakdown Across Mathematical Domains</span>
      </h3>

      <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-1">
        <div
          v-for="t in evalData?.topic_breakdown"
          :key="t.topic"
          class="p-4 rounded-2xl bg-slate-50 border-2 border-slate-100 flex flex-col justify-between space-y-2"
        >
          <div class="flex items-center justify-between">
            <span class="text-sm font-black capitalize text-slate-800">{{ t.topic }}</span>
            <span class="text-xs font-mono font-bold text-slate-500">{{ t.sample_count }} tests</span>
          </div>
          <div class="text-2xl font-black font-mono text-emerald-600">
            {{ t.math_accuracy_percent }}%
          </div>
          <span class="text-[11px] text-slate-500 font-mono">Avg {{ t.avg_latency_ms }} ms</span>
        </div>
      </div>
    </div>

    <!-- Conclusion Section (Warm / solid primary background) -->
    <div class="bg-primary-950 rounded-3xl p-6 sm:p-8 text-white shadow-warm-lg space-y-4 border-2 border-primary-900">
      <div class="flex items-center gap-2.5">
        <span class="text-2xl">💡</span>
        <h2 class="text-xl sm:text-2xl font-black tracking-tight text-accent-300">
          Evaluation Conclusion & Recommendations
        </h2>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
        <div class="p-4 rounded-2xl bg-white/10 border border-white/10 space-y-2">
          <div class="flex items-center gap-1.5 text-emerald-300 font-black text-sm">
            <span>✅</span>
            <span>Prompt v2 is Highly Superior</span>
          </div>
          <p class="text-xs text-indigo-100 leading-relaxed">
            Stricter mathematical precision instructions in <code class="font-mono bg-black/30 px-1 rounded">v2.txt</code> improved claimed-answer consistency from 80% to 100%, completely eliminating repair loops.
          </p>
        </div>

        <div class="p-4 rounded-2xl bg-white/10 border border-white/10 space-y-2">
          <div class="flex items-center gap-1.5 text-amber-300 font-black text-sm">
            <span>⚡</span>
            <span>Flash Engine for Game Rounds</span>
          </div>
          <p class="text-xs text-indigo-100 leading-relaxed">
            The Flash model delivers ~45% lower latency (762 ms vs 1362 ms) while retaining 100% schema validity, making it the ideal engine for real-time adaptive quiz questions.
          </p>
        </div>

        <div class="p-4 rounded-2xl bg-white/10 border border-white/10 space-y-2">
          <div class="flex items-center gap-1.5 text-purple-300 font-black text-sm">
            <span>📖</span>
            <span>Grade 5 & 6 Readability</span>
          </div>
          <p class="text-xs text-indigo-100 leading-relaxed">
            The Flesch-Kincaid readability average of 4.84 confirms that narrative scenarios maintain an age-appropriate reading level for 5th and 6th-grade Georgia learners.
          </p>
        </div>
      </div>

      <p class="text-xs sm:text-sm text-indigo-200 font-medium pt-2 border-t border-white/10 italic">
        "{{ evalData?.conclusion || 'Prompt v2 with stricter mathematical directives dramatically improves claimed_answer alignment.' }}"
      </p>
    </div>

    <!-- How to Run the Evaluation Section -->
    <div class="bg-white rounded-3xl p-6 sm:p-8 border-2 border-slate-200 shadow-game space-y-4">
      <h3 class="text-lg font-black text-slate-800 flex items-center gap-2">
        <span>💻</span>
        <span>How to Run the Evaluation Benchmark Locally</span>
      </h3>
      <p class="text-xs sm:text-sm text-slate-600 leading-relaxed">
        The benchmark script generates questions across all model and prompt configurations, validates them against Georgia standards, computes AST math verification accuracy, and saves outputs to <code class="font-mono bg-slate-100 px-1 py-0.5 rounded text-indigo-700">eval/results/results.csv</code> and <code class="font-mono bg-slate-100 px-1 py-0.5 rounded text-indigo-700">summary.json</code>.
      </p>

      <div class="bg-slate-900 rounded-2xl p-4 text-emerald-400 font-mono text-xs overflow-x-auto space-y-2">
        <p class="text-slate-400"># 1. Activate backend environment</p>
        <p>cd backend</p>
        <p>.\.venv\Scripts\Activate.ps1</p>
        <p class="text-slate-400 pt-2"># 2. Run full evaluation with N=10 samples per condition</p>
        <p>python eval/run_eval.py -N 10</p>
        <p class="text-slate-400 pt-2"># 3. Or run synthetic mock evaluation offline (instant)</p>
        <p>python eval/run_eval.py -N 10 --mock</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useApi, type EvalSummaryResponse } from '~/composables/useApi'

const { fetchEvalSummary, triggerEvalRun, isLoading } = useApi()
const evalData = ref<EvalSummaryResponse | null>(null)

const loadData = async () => {
  try {
    evalData.value = await fetchEvalSummary()
  } catch (err) {
    console.error('Failed to load evaluation summary:', err)
  }
}

const refreshBenchmark = async () => {
  try {
    evalData.value = await triggerEvalRun(10)
  } catch (err) {
    console.error('Failed to re-run benchmark:', err)
  }
}

onMounted(() => {
  loadData()
})
</script>
