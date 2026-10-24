# MathQuest: Engineering & Architecture Interview Notes

These notes provide deep architectural context, design rationale, and technical trade-offs behind **MathQuest**, prepared for technical evaluators, engineering leadership, and client handoff.

---

## 1. Core Philosophy: *"The LLM writes, code verifies, the engine adapts."*

### Why We Never Trust LLM Math
Large Language Models (LLMs) operate on token probabilities rather than formal logical structures or arithmetic execution. In benchmark testing:
- LLMs routinely hallucinate fraction simplification steps (e.g., claiming $\frac{7}{8} - \frac{3}{8} = \frac{4}{16} = \frac{1}{4}$).
- LLMs invert division logic under word-problem narrative complexity.
- LLMs often confuse perimeter and area formulas when parsing multi-sentence scenarios.

If an EdTech platform presents an unverified LLM-generated answer as the grading key, it destroys student trust and reinforces mathematical misconceptions.

### The MathQuest Invariant
MathQuest decouples the **creative narrative layer** from the **mathematical verification layer**:
1. **LLM Proposes**: Gemini generates the scenario context, LaTeX expression, and its claimed answer.
2. **Code Verifies**: Python's safe recursive parser (`services/verify.py`) parses the expression using exact rational arithmetic (`fractions.Fraction`). If `evaluate(expression) != claimed_answer`, the system triggers an automatic repair prompt with the exact rational difference. If repair fails, it gracefully falls back to the curated `fallback_bank.json`.
3. **Engine Adapts**: The adaptive engine (`services/adaptive.py`) routes the student dynamically across Easy, Medium, and Hard tiers, diagnosing specific misconceptions when a distractor is chosen.

---

## 2. Security & Safe Mathematical Parser

### Total Ban on `eval()` and `exec()`
Standard Python implementations often rely on `eval()` or `ast.literal_eval()`, but:
- `eval()` is vulnerable to Remote Code Execution (RCE) via `__import__('os').system(...)` or `__subclasses__()` exploits.
- `ast.literal_eval()` does not evaluate arithmetic operators (it only evaluates static literals).

### The MathQuest Parser Architecture (`backend/app/services/verify.py`)
We implemented a strict, sandboxed arithmetic evaluator:
- **Token Whitelist**: Only digits, fractions (`/`), decimal points, parentheses, and arithmetic operators (`+`, `-`, `*`, `/`, `^`, `×`, `÷`) are permitted.
- **Lexer/Parser**: Validates token balance and structure before execution.
- **Exact Rational Arithmetic**: Every number is converted into a `fractions.Fraction(numerator, denominator)`. This completely eliminates binary floating-point errors (e.g., `0.1 + 0.2 = 0.30000000000000004` becomes exactly `3/10`).
- **Forbidden Builtins**: Any payload containing alphabetic characters outside permitted units or math symbols triggers an immediate `MathVerificationError` without touching Python evaluation.

---

## 3. Diagnostic Distractors & Misconception Taxonomy

### Why Random Distractors Are Bad Pedagogy
Traditional quiz engines generate distractors by adding random offsets ($n \pm 1, n \pm 2$). Students can easily eliminate obvious nonsensical options through test-taking tricks without engaging with the underlying math.

### Diagnostic Distractor Engine (`backend/app/services/misconceptions.py`)
MathQuest generates options where **every single distractor maps to a documented cognitive misconception**:

| Domain | Cognitive Misconception | Mathematical Manifestation | Diagnostic Feedback |
| :--- | :--- | :--- | :--- |
| **Fractions** | Added Denominators | $\frac{a}{b} + \frac{c}{d} = \frac{a+c}{b+d}$ | *"Denominators represent total parts in a whole—find a common denominator first!"* |
| **Fractions** | Inverted Dividend Instead of Divisor | $\frac{a}{b} \div \frac{c}{d} = \frac{b}{a} \times \frac{c}{d}$ | *"When dividing, keep the first fraction and multiply by the reciprocal of the second!"* |
| **Decimals** | Ignored Place Value | $0.4 + 0.05 = 0.9$ (treated as $4+5$) | *"Line up decimal points by place value: tenths with tenths, hundredths with hundredths!"* |
| **Decimals** | Dropped Trailing Zero | $2.5 - 0.75 = 1.75$ (calculated $2 - 0.75$) | *"Append a placeholder zero: $2.50 - 0.75 = 1.75$!"* |
| **Ratios** | Part-to-Part vs Part-to-Whole | Given $2:3$, claims total ratio is $2/3$ | *"The whole is $2 + 3 = 5$ parts; ratio to total is $2/5$!"* |
| **Geometry** | Area vs Perimeter Confusion | Area of $6 \times 4$ rectangle given as $2(6+4) = 20$ | *"You calculated the perimeter around the edges! Area is length $\times$ width."* |
| **Geometry** | Triangle Area Forgot $\frac{1}{2}$ | Area of triangle given as $b \times h$ | *"A triangle is half a rectangle—don't forget to divide by 2!"* |
| **CBSE Factors** | Factors vs Multiples Confusion | Factors of $12$ includes $24, 36$ | *"Factors divide into 12 without remainder; multiples are products of 12."* |
| **CBSE LCM/GCD** | Product Instead of LCM | $\text{LCM}(6, 8) = 48$ instead of $24$ | *"While $6 \times 8 = 48$ is a common multiple, the LEAST common multiple is 24."* |

---

## 4. Multi-Curriculum Extensibility (Zero Code Modifications)

### The Curriculum Pack Pattern
MathQuest was architected so that supporting a new state or international educational board requires **only adding data files**, with zero code changes:

```
backend/data/packs/
├── georgia-g5.json      # Georgia Standards of Excellence (Grade 5)
├── georgia-g6.json      # Georgia Standards of Excellence (Grade 6)
└── cbse-g6.json         # CBSE Class 6 (NCERT Ganita Prakash)
```

### Pack Schema Architecture
Each pack declares:
1. `board_id` and `grade`
2. `topics`: Code, label, pedagogical description, and mapped standard codes (e.g. `MGSE5.NF.1` or `NCERT-6-MAT-CH05`).
3. `tier_rules`: Topic-specific difficulty parameters (e.g., maximum denominator, whole number ranges, operations allowed).
4. `verified`: Strict boolean tracking whether standard codes were cross-verified against official ministry documentation.

---

## 5. Free-Tier Production Engineering

Operating under a strict **100% Free-Tier constraint** required deliberate architectural choices:

1. **Model Decoupling via Environment Variables**:
   - `GEMINI_MODEL`, `GEMINI_MODEL_ALT`, and `GEMINI_EMBED_MODEL` are injected at runtime. No model names exist in code or prompts.
2. **Dual-Tier RAG Architecture**:
   - Primary: Supabase PostgreSQL with `pgvector` for semantic standard retrieval.
   - Fallback: Local markdown reader (`backend/data/standards/`) that automatically engages if Supabase credentials are missing or the database is paused.
3. **Zero-Failure Fallback Bank**:
   - 60 pre-verified, deterministic questions in `backend/data/fallback_bank.json` across all Georgia and CBSE topics. If LLM rate limits (429) or network latency occur, students experience zero interruption.
4. **Edge Delivery & State Persistence**:
   - Nuxt 3 frontend deployed on Vercel with zero server state.
   - Student mastery, XP, streaks, and unlocked badges persist in browser `localStorage`, ensuring complete COPPA/FERPA compliance (zero student PII transmitted to LLMs or stored in backend databases).

---

## 6. Technical Trade-Offs & Decisions

| Decision | Chosen Approach | Alternative Considered | Rationale |
| :--- | :--- | :--- | :--- |
| **Arithmetic** | Exact `fractions.Fraction` | Floating point (`float`) | Eliminates IEEE 754 precision errors in rational grading. |
| **Formula Parser** | Custom AST token scanner | SymPy / PyPI Math Parsers | SymPy adds heavy dependency weight (~40MB); custom scanner has 0 external dependencies and executes in microseconds. |
| **State Storage** | Client `localStorage` | Supabase User Auth/DB | Zero PII risk for minors; 100% free-tier; instant client-side offline continuity. |
| **Rate Limiter** | `slowapi` in-memory | Redis / Upstash | Avoids requiring an external Redis server on free-tier Render while effectively preventing client spam. |
| **Frontend** | Nuxt 3 + Pinia + Tailwind | React / Next.js | Vue 3 reactivity provides simpler reactive state machines for quiz flows and built-in SSR/static generation with zero boilerplate. |

---

## 7. What We Would Build With a Production Budget

If provided a production cloud budget ($500–$2,000/month), the next architectural iterations would include:
1. **Distributed Redis Rate Limiter**: Shared rate limiting across multiple Render backend worker replicas.
2. **Fine-Tuned Small Language Model (SLM)**: Fine-tune a 7B/8B model (e.g., Gemma 2) specifically on math word problem generation and distractor tagging, reducing API latency from ~1.2s to ~150ms.
3. **Teacher Classroom Telemetry**: Real-time WebSocket room dashboard for teachers to view class-wide misconception heatmaps live during class exercises.
4. **Multimodal Audio Generation**: Neural voice generation via ElevenLabs or Gemini Live API for dynamic read-aloud in English, Spanish, Hindi, and Tamil.
