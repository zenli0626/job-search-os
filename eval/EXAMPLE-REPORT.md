# Example Gaps + Roadmap Report

*Frame: genericized reference implementation analysis. No personal details.*

---

## Strengths

- **Unusually deep evidence base in the Career KB.** The KB covers accomplishments with
  specific metrics, a skills matrix with evidence citations, gap framing strategies, and
  resume variant selection logic. Most job seekers operate from a single resume and
  fuzzy self-knowledge; this implementation has a structured, cited foundation.

- **No-fabrication constraint enforced at the skill level.** The Career Brain skill will
  surface missing KB evidence rather than invent it. This is structurally rare — most LLM
  job-search tooling hallucinates freely.

- **ATS sweep is parallel + multi-layer filtered across Greenhouse, Ashby, and Lever.**
  The sweep handles 50+ company boards in ~30 seconds without LLM cost. The lane/exclusion/
  seniority/location filter stack is well-calibrated and config-driven.

- **Clear named fit lanes.** The system has explicit Lane A / Lane B / Lane C definitions
  with trigger patterns. This enables per-lane funnel analysis — which lanes are converting,
  which need more targeting.

- **Automation triggers exist at the skill layer.** The Career Brain skill auto-fires on
  natural language phrases, reducing the activation energy for common workflows.

---

## Gaps (Prioritized)

### Gap 1: No application status tracker
**Affects:** Stages 4, 5
**Why it matters:** There is no single record of which roles were applied to, when, at what
stage, or with what outcome. Without this, there's no pipeline velocity, no follow-up cadence,
no funnel metrics, and no ability to diagnose where the search is breaking.
**Effort:** Low — a SQLite table with (url, company, title, stage, date, lanes) solves this.

### Gap 2: Stage 4 → Stage 3 connection is broken
**Affects:** Stages 3, 4
**Why it matters:** The sweep produces matches via stdout. The user must manually copy-paste
them into the fit scorer. This manual step is where matches get lost — the gap between
"found a role" and "evaluated a role" is a dropped handoff.
**Effort:** Low — sweep writes to `sweep.sqlite`; add a SEEN→PENDING review queue; daily
digest prints unscored APPLY-tier roles.

### Gap 3: No closed loop from interview outcome back to KB
**Affects:** Stages 1, 2, 5
**Why it matters:** When an interview happens, the outcome (strong story / didn't land / wasn't
asked) is not captured. Gap analysis doesn't update. STAR stories aren't flagged for revision
when they underperform. Over time, the KB stagnates and the system stops learning.
**Effort:** Medium — requires a structured outcome-capture form and a prompt that feeds notes
back into `gap-analysis.md` and `accomplishments-STAR.md`.

### Gap 4: Story-mining is an island
**Affects:** Stages 1, 2
**Why it matters:** Stories refined in coaching sessions exist only in chat history. They
don't sync back to the STAR bank. The STAR bank doesn't seed coaching sessions. See
`01-story-mining/INTEGRATION.md` for the full design intent.
**Effort:** Low-Medium — short-term: structured output format + manual copy step; medium-term:
skill writes to `$CAREER_KB_PATH/drafts/`.

### Gap 5: No sweep persistence / dedup across runs
**Affects:** Stage 4
**Why it matters:** Without persistence, every sweep run shows the same roles. The user can't
tell what's new vs. what's been seen before. A 30-second sweep that shows 40 roles every morning
is noise; one that shows only the 3 net-new roles is signal.
**Effort:** Low — `sweep.sqlite` with URL as primary key. Already specified in `pipeline-schema.md`.

### Gap 6: No weekly cadence or activity metrics
**Affects:** Stage 5
**Why it matters:** Without a weekly review cadence, the search runs in open-loop mode. There's
no signal on application velocity, no follow-up discipline, and no way to know whether the
approach is working.
**Effort:** Medium — the `weekly-review.prompt.md` exists; the gap is the pipeline data it
needs to read. Build the status table first (Gap 1), then the review becomes automatable.

---

## Redundancies and Friction

- **Career KB split across two access patterns requiring a judgment call.** The Brain reads
  from `CAREER_KB_PATH` directly, but some artifacts are also referenced via the skills matrix
  and via STAR story IDs. A unified index file (already spec'd as `CAREER_CONTEXT.md`) resolves
  this, but needs to be kept current.

- **Two partial fit-assessment views with no shared format.** The HTML scorer and the application
  package prompt both assess fit, but via different mechanisms and in different formats. The HTML
  scorer output should be parseable JSON that feeds directly into the application prompt.

- **Sweep runs from a hardcoded temp path rather than scheduled.** The script exists and works,
  but the scheduling step is unbuilt. A simple launchd plist or cron entry would make the sweep
  a zero-friction daily feed rather than a remembered manual step.

---

## Roadmap

### Now (this week)
1. **Persist sweep output to SQLite** with `(url, title, company, lanes, location, first_seen, status='SEEN')`.
   Add status field with codes: `SEEN / SKIP / SOURCED / APPLIED / RECRUITER / HM / ONSITE / OFFER / REJECTED / GHOSTED`.
   Print only net-new on each run.

2. **Add one post-interview outcome prompt** that asks 3 questions after a recruiter screen
   (which stories came up? what surprised you? any gap signals?) and appends structured notes
   to `gap-analysis.md`. Even if manual, closing this loop changes what the system learns.

### Next (this month)
3. **Route Stage 4 → Stage 3 via a to-review queue.** After each sweep, net-new roles with
   no score are added to a pending list. A daily digest prompt surfaces the top 5 unscored
   roles for evaluation. Stage 3 scoring marks them as scored in the DB.

4. **Schedule the sweep nightly** (launchd or cron). Add a notification step that sends
   net-new APPLY roles to a phone notification (Telegram, email, or iOS shortcut). This
   makes Stage 4 a passive feed instead of an active task.

5. **Story-mining staging folder.** Coach writes refined stories to `$CAREER_KB_PATH/drafts/`.
   A weekly review step promotes approved drafts to the main STAR bank. Closes the
   integration gap without risking auto-overwrite of existing stories.

### Later (next quarter)
6. **Weekly Manager Loop report** — compute velocity, response rate, funnel drop-off by lane,
   and follow-up queue from `sweep.sqlite`. Produce a markdown Week in Review automatically
   on Monday morning.

7. **Outcome-weighted rubric scoring.** Track which lane rubric weights produced APPLY verdicts
   that advanced vs. were rejected. Adjust `weight` fields in `rubric.json` based on which
   strength buckets correlated with actual callbacks. The scorer becomes calibrated to your
   real signal, not just your prior beliefs.

---

## Single Most Important Fix

**Build the status table (Gap 1).** Everything else depends on it: the sweep can't dedup,
the Manager Loop can't review, the weekly report can't compute velocity. A single SQLite
table with 8 columns unlocks the rest of the roadmap.
