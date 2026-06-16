# Eval Stage — System Maturity Assessment

## What This Stage Does

The eval stage evaluates the **whole system's maturity**, not individual job applications.
Run it monthly (or after a major build sprint) to understand where the system is strong,
where it's weak, and where to invest next.

---

## The Five Dimensions

Each stage is scored on five dimensions (1–5 each):

| Dimension | What it measures |
|---|---|
| **Automation** | How much runs without your hands on it? |
| **Repeatability** | Can you do this the same way every time, without thinking? |
| **Evidence-grounding** | Are outputs anchored in real data, not vibes? |
| **Feedback loop** | Do outcomes feed back and improve the system? |
| **Output quality** | How good is the actual deliverable? |

---

## Files

| File | Purpose |
|---|---|
| `eval-agent.prompt.md` | The reusable evaluation prompt — paste into Claude Code |
| `EXAMPLE-SCORECARD.md` | Worked example scorecard with generic scores and commentary |
| `EXAMPLE-REPORT.md` | Worked example gaps + roadmap report |

---

## How to Run

1. Copy `eval-agent.prompt.md` and paste into Claude Code
2. Provide a brief description of your current implementation of each stage
3. The agent produces a scorecard table + gaps report
4. Save the output to `eval/reviews/eval-[DATE].md`

---

## Frequency

- **Monthly:** standard cadence during active search
- **After a major sprint:** if you've built out Stage 03 or Stage 05 this week, re-eval
- **At start of search:** baseline before you build anything

---

## What to Do With the Scores

The eval is not a performance review — it's a roadmap input. After each eval:

1. Look at the lowest-scoring stage (usually the Manager Loop for early implementations)
2. Identify the single highest-leverage fix in that stage
3. Build that fix before the next eval
4. Track your average score over time

A system that goes from 2.0/5 to 3.5/5 over 8 weeks is a system that's learning.
A system stuck at 2.0/5 for 8 weeks has broken connective tissue that needs diagnosis.

---

## Maturity Benchmarks (rough)

| Average score | Interpretation |
|---|---|
| 1.0–1.9 | Early stage: mostly manual, each stage is siloed |
| 2.0–2.9 | Pipeline forming: inputs are strong, middle is broken |
| 3.0–3.9 | Connected: stages hand off to each other, some automation |
| 4.0–4.9 | Operating system: all loops close, feedback propagates |
| 5.0 | Theoretical ceiling — not a real target |

Most job searches that feel "managed" operate around 2.5–3.0. The goal of this framework
is to push toward 3.5–4.0 by the end of an active search.
