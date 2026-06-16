# Eval Agent — System Maturity Assessment Prompt

## When to Use

Run monthly during an active search, or after any significant build sprint.
This prompt directs an evaluator agent to score each stage of the Job Search OS
on five dimensions and produce a gaps + roadmap report.

---

## The Prompt

Paste this into Claude Code (or your LLM) along with your implementation notes:

---

```
You are an evaluator agent assessing the maturity of a Job Search OS implementation.
Score each of the 5 stages on 5 rubric dimensions.

IMPLEMENTATION NOTES — describe your current setup for each stage:
[Stage 1 - Know Yourself]: [DESCRIBE YOUR KB AND CAREER BRAIN SETUP]
[Stage 2 - Story Mining]: [DESCRIBE YOUR COACHING LOOP SETUP]
[Stage 3 - JD→Application]: [DESCRIBE YOUR SCORING AND PACKAGING SETUP]
[Stage 4 - Daily Research]: [DESCRIBE YOUR SWEEP SETUP]
[Stage 5 - Manager Loop]: [DESCRIBE YOUR TRACKING AND REVIEW SETUP]

SCORING RUBRIC:

For each stage, score 1–5 on each dimension:

| Dimension | 1 | 3 | 5 |
|---|---|---|---|
| Automation | Fully manual | Some scripts | Runs on schedule without intervention |
| Repeatability | Ad hoc each time | Mostly consistent | Same process every time, documented |
| Evidence-grounding | Vibes / guesses | Some data | Every claim cites a source |
| Feedback loop | No loop | Occasional | Outcomes automatically update system |
| Output quality | Rough draft | Good enough | Polished, consistent, high-signal |

DELIVERABLES — produce both:

## Part 1: Scorecard

Format as a markdown table:

| Stage | Automation | Repeatability | Evidence | Feedback | Output | Avg |
|---|---|---|---|---|---|---|
| Stage 1: Know Yourself | [1-5] | [1-5] | [1-5] | [1-5] | [1-5] | [avg] |
| Stage 2: Story Mining  | ... | ... | ... | ... | ... | ... |
| Stage 3: JD→Application | ... | ... | ... | ... | ... | ... |
| Stage 4: Daily Research | ... | ... | ... | ... | ... | ... |
| Stage 5: Manager Loop  | ... | ... | ... | ... | ... | ... |
| **Overall** | ... | ... | ... | ... | ... | [overall avg] |

For each stage, add 2 bullet points:
- Strength: [what's working well in this stage]
- Weakness: [the single most important thing to fix]

## Part 2: Gaps + Roadmap

### Strengths (across the whole system)
List 3–5 genuine strengths of the implementation.

### Gaps (prioritized)
List gaps in priority order. For each gap:
- Gap name
- Which stages it affects
- Why it matters (what breaks without fixing it)
- Estimated effort to fix (low / medium / high)

### Redundancies / Friction
List any places where the setup has unnecessary duplication, manual steps that could
be eliminated, or process steps that add friction without adding value.

### Roadmap (3 horizons)
**Now (this week):** [1-2 highest-leverage fixes, low effort]
**Next (this month):** [2-3 medium-effort improvements]
**Later (next quarter):** [1-2 structural improvements worth planning]

### Single Most Important Fix
In one sentence: the single change that would most improve the system's overall effectiveness.

---

CONSTRAINTS:
- Score honestly, not charitably. A 5 means truly excellent — most stages deserve 2–3.
- Base scores on what the person DESCRIBED, not on the ideal design.
- The roadmap should be specific and actionable, not generic advice.
- If implementation notes are vague, note what additional information would improve the assessment.
```

---

## After Running

Save the output to `eval/reviews/eval-[DATE].md`. Track your overall average over time.

| Date | Overall Avg | Lowest Stage | Key Fix |
|---|---|---|---|
| [DATE] | [avg]/5 | [stage name] | [one-liner] |

This table (maintained manually) is your search's learning trajectory.
