# Stage 02: JD → Application

## What This Stage Does

Takes a job description as input, runs it through a configurable rubric, and produces:
1. A **fit score** (0–100) and verdict: **APPLY / STRETCH / SKIP**
2. The specific **evidence from your KB** that maps to the role's requirements
3. A **pitch angle** — the 1–2 sentence framing that leads your application
4. For APPLY and STRETCH roles: a full **application package** (tailored resume, cover letter, optional interview prep)

This stage is where the Career Brain (Stage 00) and the Daily Sweep (Stage 03) connect.
The Sweep finds the roles; this stage decides which ones are worth the investment.

---

## Components

### `fit-scorer/` — The Scoring Engine

| File | Purpose |
|---|---|
| `scorer.js` | Pure CommonJS function: `scoreJD(jdText, rubric)` → score + verdict + evidence |
| `rubric.example.json` | Example rubric schema — customize this for your lane mix |
| `index.html` | Local single-file HTML app: paste JD → get score → see breakdown |

**To use the scorer:**
1. Copy `rubric.example.json` → `rubric.json` (not committed — in `.gitignore` via `*.local`)
2. Customize your strength buckets, gap buckets, and dealbreakers
3. Open `index.html` in your browser

### `application-package.prompt.md`

A reusable prompt that invokes the Career Brain (Stage 00) to produce a full application
package for an APPLY or STRETCH role. Outputs go to `applications/[company]/`.

---

## Scoring Philosophy

**Strength buckets** represent where you're genuinely strong. The rubric weights them by
how much you want to foreground each area. Trigger words are not magic — they signal
that the JD describes work you've done.

**Gap buckets** are known weaknesses relative to your target lanes. The rubric applies
weighted penalties when a JD description suggests these gaps matter.

**Dealbreakers** are hard stops. A PhD requirement or security clearance you don't have
caps the score at 29 regardless of strengths. Don't waste time on a SKIP.

**The APPLY/STRETCH/SKIP gate is a decision aid, not a rule.** A STRETCH role at a dream
company may be worth applying to. A high-scoring APPLY at a company you have concerns about
may be worth passing. Use the score to calibrate, not to decide mechanically.

---

## Workflow

```
Stage 03 sweep → net-new APPLY-tier candidates
        ↓
Open index.html → paste JD → run scorer
        ↓
Score ≥ 70: APPLY     → run application-package.prompt.md
Score 45–69: STRETCH  → run application-package.prompt.md (with gap notes)
Score < 45: SKIP      → log and move on
        ↓
Application files → applications/[company]/
        ↓
Log in Manager Loop pipeline tracker (update status: SEEN → APPLIED)
```

---

## Customizing Your Rubric

The rubric is the heart of the scorer. Generic rubrics produce generic results.
Spend 30 minutes customizing `rubric.example.json`:

1. **Name your strength buckets** to match the 2–3 things you're genuinely best at.
2. **Weight them** proportionally to how often they appear in your target JDs.
3. **Name your gap buckets** honestly — the things that appear in your target JDs that you're weaker on.
4. **Add your actual dealbreakers** — the requirements that immediately disqualify a role for you.
5. **Write `pitchLine`** for each strength bucket: the 1-sentence framing you'd use in a cover letter opener for a role where this bucket fired.
