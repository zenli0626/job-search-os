# Weekly Manager Loop — Agent Prompt

## Purpose

Run this prompt every week (suggest: Monday morning or Sunday evening).
Paste it into Claude Code or any LLM and provide the requested data inputs.
The agent produces a "Week in Review" markdown document covering:
- Pipeline velocity and funnel metrics
- Follow-ups due
- Net-new APPLY-tier roles from the sweep
- Recommended actions for the week

This prompt is designed to run as a scheduled agent (weekly cron) — see notes at the bottom.

---

## Data Inputs Required

Before running, gather:
1. **Pipeline export** — export JSON from `pipeline-tracker.html`
2. **Sweep output** — the most recent stdout from `job-sweep.py`, or query `sweep.sqlite`
3. **Date range** — the start and end of the review week

---

## The Prompt

Copy from here and paste into Claude Code:

---

```
You are the Job Search Manager Loop agent. Produce a "Week in Review" report
for the job search pipeline.

Today's date: [TODAY_DATE]
Review period: [WEEK_START] to [WEEK_END]

PIPELINE DATA (JSON export from pipeline-tracker.html):
[PASTE PIPELINE JSON HERE]

NET-NEW SWEEP RESULTS (from job-sweep.py stdout or sweep.sqlite):
[PASTE SWEEP OUTPUT HERE — just the net-new section is fine]

REPORT FORMAT:

## Week in Review — [WEEK_START] to [WEEK_END]

### 1. Pipeline Snapshot
Count rows by status. Produce a table:
| Stage | Count | Δ vs last week |
(If you don't have last week's data, skip the delta column.)

### 2. Funnel Metrics
Compute and display:
- Application velocity: applications sent this week (APPLIED rows with applied_date in range)
- Response rate: (RECRUITER + HM + ONSITE + OFFER + REJECTED) / total APPLIED
- Active pipeline: rows in RECRUITER / HM / ONSITE stages
- Ghosted: rows in GHOSTED stage
Flag: if response rate < 10% across 15+ applications, note "targeting or materials issue"
Flag: if no applications sent this week, note "velocity gap"

### 3. Follow-Ups Due
List every row where:
  status = 'APPLIED' AND applied_date < today - 7 days
For each: company name, title, date applied, days elapsed.
Mark: "URGENT" if > 14 days elapsed with no response.

### 4. Stage Movements This Week
List any row where last_updated falls within the review period AND status changed.
For each: company, title, old status → new status, date.

### 5. Net-New APPLY-Tier Roles
From the sweep output, list roles not yet in the pipeline.
Prioritize: Lane A matches first, then Lane B, then Lane C.
Flag any that overlap with companies already in APPLIED or ONSITE stage (warm context).

### 6. Actions for This Week
Produce a numbered action list:
1. Follow-up emails to send (from section 3) — list company + suggested follow-up date
2. Applications to review (from section 5) — list top 3 net-new roles to score this week
3. Interview prep needed — list any ONSITE rows and what prep is most critical
4. KB updates needed — any outcome from last week (rejection feedback, interview notes)
   that should flow back to gap-analysis.md or accomplishments-STAR.md

### 7. One-Paragraph Assessment
Summarize the state of the search in 3–4 sentences. Be direct:
- Is velocity adequate?
- Is the funnel converting at each stage?
- What's the single most important thing to fix this week?

---

OUTPUT: Write the full Week in Review as a markdown document.
Save it to: manager/reviews/week-[WEEK_START].md
```

---

## Running as a Scheduled Agent

### Claude Code (manual weekly)
Keep this prompt in `manager/weekly-review.prompt.md` and paste it each Monday.
Replace the data placeholders by exporting from `pipeline-tracker.html` and running
`python3 03-daily-research/job-sweep.py`.

### Automated (optional)
If you use Claude Code's schedule feature or a cron-triggered Claude agent:

1. Export pipeline JSON nightly via a localStorage sync script (or manual export Sunday)
2. Run `job-sweep.py` on schedule (stores results in `sweep.sqlite`)
3. On Monday morning, trigger this prompt with the exported data auto-inserted

The prompt is designed to be self-contained — a fresh agent with no prior context can run it
as long as the data inputs are provided.

---

## Review Archive

Save each week's report to `manager/reviews/week-[DATE].md`.
Over time, compare velocity and rate trends across weeks to spot patterns:
- Which lanes are converting?
- Are specific company sizes/types responding more?
- Is prep time affecting late-round performance?

The review archive is your search's longitudinal data.
