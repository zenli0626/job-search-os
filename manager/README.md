# Manager Loop (Stage 05)

## What This Stage Does

The Manager Loop is the weekly aggregation and review stage. It is the highest-leverage
stage in the system — the one that turns scattered activity into learning and action.

Without it:
- You don't know your application velocity (are you sending enough?)
- You don't know your response rate (are the right roles responding?)
- You don't know your drop-off pattern (where does your funnel break?)
- You don't follow up on ghosted applications
- You don't have a cadence

---

## What It Aggregates

| Input | Source |
|---|---|
| Net-new APPLY-tier roles | `sweep.sqlite` (Stage 03) |
| Applications sent + dates | Pipeline tracker (localStorage or status table) |
| Stage movements | Manual updates in `pipeline-tracker.html` |
| Follow-ups due | Any row in APPLIED status with date > 7 days ago |
| Interview outcomes | Manual notes after each conversation |

---

## The Weekly Rhythm

Run the weekly review every Monday morning (or Sunday night):

1. Open `pipeline-tracker.html` — review stage counts and export JSON
2. Run `weekly-review.prompt.md` (paste into Claude Code or your LLM) — get the full digest
3. Triage follow-ups: send any 7-day follow-ups before the day is out
4. Review net-new APPLY roles from `sweep.sqlite` — score any you haven't seen yet (Stage 02)
5. Note outcomes from the previous week: any interview feedback goes back to `gap-analysis.md`

Time investment: 30–45 minutes per week. This is the session that makes everything else compound.

---

## Files in This Stage

| File | Purpose |
|---|---|
| `pipeline-schema.md` | The 8-stage funnel definition and shared status table schema |
| `weekly-review.prompt.md` | Reusable agent prompt for the weekly digest |
| `pipeline-tracker.html` | Local HTML funnel dashboard (localStorage, no server) |

---

## The Broken Middle Diagnosis

If your response rate is < 10% across 20+ applications: the issue is usually targeting
(wrong roles) or materials (resume/cover letter not resonating). Run the Career Brain
on a sample of rejected roles and compare against the fit scorer output.

If your response rate is > 20% but interview rate is low: the issue is usually screening
conversations. Return to Stage 01 (Story Mining) and drill your 1-minute speech and
company-specific stories.

If your interview rate is high but offers are low: the issue is usually late-round prep
(technical depth, case presentation, negotiation). That's a different playbook.

The Manager Loop surfaces which diagnosis applies to you — but only if you keep the
status table updated.
