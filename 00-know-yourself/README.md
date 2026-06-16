# Stage 00: Know Yourself — Career Brain

## What This Stage Does

Stage 00 is the single source of truth for everything you know about yourself professionally. It has two parts:

1. **Career KB** — a set of private markdown files (templates in `templates/`) you fill in once and maintain over time
2. **Career Brain** — a Claude Code skill (`career-brain.skill.md`) that reads your KB and produces any external artifact on demand

When you need a tailored resume, the Career Brain reads your KB. When you need a cover letter, it reads your KB. When you need to frame a gap, it reads your KB. You never write from scratch; you maintain one authoritative source and let the skill translate it.

---

## The Career KB Pattern

Your KB lives at a private path you control (`$CAREER_KB_PATH`). The templates directory gives you the full structure:

| Template | Purpose |
|---|---|
| `CAREER_CONTEXT.template.md` | Brain entrypoint: identity, target roles, constraints |
| `accomplishments-STAR.template.md` | STAR story bank — the raw material for interviews |
| `gap-analysis.template.md` | Known gaps vs. target roles, with framing strategies |
| `resume-variants.template.md` | Which resume variant targets which JD type |
| `skills-matrix.template.md` | Skills by level with evidence citations |
| `work-log.template.md` | Low-friction running capture of recent wins — the input to CV Refresh |

Copy these to your private directory, fill them in, and set `CAREER_KB_PATH` in your shell to point there.

---

## The No-Fabrication Rule

The Career Brain skill enforces a strict no-fabrication constraint:

- **Every claim must cite a KB source.** If it can't find evidence in your KB, it says so rather than inventing.
- **Never present a design target as a realized result.** "I increased efficiency by 30%" requires that 30% to exist in your KB as a measured outcome, not a plan or estimate.
- **Measured vs. targeted discipline:** If something is a goal or projection, it's framed that way. Never flipped to past tense to sound more impressive.

---

## Public-Surface Masking

Your KB contains real numbers, real timelines, real employer names. External artifacts (resume, LinkedIn, recruiter pitch) may need those details softened for privacy or competitive positioning:

- Convert absolute headcount to "a team of X" or "cross-functional team"
- Convert absolute dollar amounts to percentage improvements or "X-figure" ranges where appropriate
- Convert absolute timelines to relative ones ("within 6 months")

The private KB retains full precision. Public artifacts apply the mask. The skill knows which mode to use based on the artifact type.

---

## How to Use

**Generate a tailored resume:**
```
@career-brain Tailor my resume for this JD: [paste JD]
```

**Draft a cover letter:**
```
@career-brain Write a cover letter for [Company Name], role: [Title]
```

**Frame a skill gap:**
```
@career-brain How should I frame my gap in [skill] for a [role type] audience?
```

**Pull a STAR story:**
```
@career-brain Give me a STAR story for "describe a time you drove alignment across competing stakeholders"
```

**Write a recruiter pitch:**
```
@career-brain Write a 3-sentence recruiter positioning pitch targeting [Lane A/B/C]
```

All outputs are grounded in your KB. If a story doesn't exist in the KB, the Brain will tell you it's missing rather than inventing one.

---

## Keeping the KB Fresh — CV Refresh

A KB built once goes stale: your resume undersells your last six months and your STAR bank is missing your best recent story. The **CV Refresh** workflow (`cv-refresh.prompt.md`) is the maintenance loop that keeps the single source of truth actually true.

**The pattern:**

1. **Capture as you go.** Jot one line into `work-log.md` (from `templates/work-log.template.md`) whenever something happens — a shipped project, a metric that moved, strong feedback, a new skill. Low friction, no formatting.
2. **Refresh on a cadence.** Monthly (or before a job-search sprint), run the CV Refresh prompt. It ingests everything new in the work log, drafts STAR stories for what's worth keeping, updates the skills matrix and gap analysis, surfaces which resume bullets each variant should now carry, and outputs a **"What changed this refresh"** diff.
3. **Same discipline.** No fabrication, measured-vs-targeted, append-don't-overwrite. The refresh promotes real evidence; it never inflates.

```
@cv-refresh Refresh my Career KB from work-log.md plus my commits since [last refresh date]
```

CV Refresh (new work → KB) pairs with the **Outcome Loop** in stage 08 (interview signal → KB). Together they turn the KB from a one-time document into a living system.
