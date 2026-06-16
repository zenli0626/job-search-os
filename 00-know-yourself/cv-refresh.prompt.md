# CV Refresh — keep the Career KB (and resume) from going stale

A reusable agent prompt. The Career KB is only as good as its last update — most job-search setups build a resume once and let it rot. This workflow runs on a cadence (monthly is a good default) and pulls your **recent work** into the KB, so your STAR bank, skills matrix, and resume variants always reflect what you've actually shipped.

It closes the single biggest gap a fresh Job Search OS has: **the KB is static — nothing ingests new accomplishments over time.**

---

## Inputs

1. **`templates/work-log.template.md`** (your filled-in copy at `$CAREER_KB_PATH/work-log.md`) — a running, low-friction capture of wins, shipped projects, metrics, feedback, and new skills since the last refresh. Jot a line whenever something happens; don't wait for the refresh.
2. **Optional signal sources** you can point the agent at:
   - recent commits / PRs / changelog (`git log --since="<last refresh>"`)
   - performance-review notes, peer/manager feedback, recognition
   - new certifications, talks, or side projects
3. The **last refresh date** (from the `Last Updated` line in each KB file).

---

## What it does (the loop)

Run this prompt against your KB:

```
You are the CV Refresh agent for my Career KB at $CAREER_KB_PATH.

1. INGEST. Read work-log.md and any signal sources I point you at. List every
   net-new accomplishment, metric, skill, or piece of feedback since the last
   refresh date. Skip anything already represented in the KB (dedupe).

2. STAR-IFY. For each net-new accomplishment worth keeping, draft a STAR story
   in the exact format of accomplishments-STAR.template.md (Situation / Task /
   Action / Result, theme tags, interview use cases). Use real numbers from the
   work log. Append — never overwrite existing stories.

3. UPDATE EVIDENCE. Add new skills (with evidence citations) to
   skills-matrix.md. Update gap-analysis.md if a known gap is now closed by new
   work. Refresh CAREER_CONTEXT.md's "current role / recent focus" if it changed.

4. REGENERATE VARIANTS. For each resume variant in resume-variants.md, surface
   which new bullets now belong in it and which stale bullets they replace.
   Produce the updated bullet list per variant — do not invent, only promote
   real KB evidence.

5. DIFF. Output a concise "What changed this refresh" report:
   - new STAR stories added (titles)
   - new skills / closed gaps
   - resume bullets added or swapped, per variant
   - anything in the work log you could NOT ground (flag for me to clarify)

6. STAMP. Update the `Last Updated` date in every file you touched.
```

---

## Discipline (inherited from the Career Brain)

The same rules apply — a refresh must not quietly inflate your record:

- **No fabrication.** Every new bullet/story cites a real work-log entry. If the agent can't ground a claim, it flags it instead of writing it.
- **Measured vs. targeted.** A goal or in-flight project is logged as in-progress, never flipped to a finished past-tense result.
- **Append, don't overwrite.** History is preserved; the refresh adds and promotes, it doesn't silently delete prior stories.
- **Private precision, public mask.** The KB keeps real numbers; masking only happens when the Career Brain later emits a public artifact.

---

## Cadence

- **Monthly** (default): catch wins while the details are fresh.
- **After any milestone**: shipped a launch, closed a big project, got strong feedback → log it the same day, refresh opportunistically.
- **Before a job-search sprint**: always refresh first, so every tailored resume draws from a current KB.

Schedule it the same way as the weekly Manager Loop — a `launchd`/cron job that runs the prompt and writes the diff report to a dated file, or just run it by hand on the first of the month.

---

## Why this is its own stage-00 module

Stages 01–06 all read from the Career KB. If the KB drifts out of date, every
downstream artifact drifts with it — your resume undersells your last six months,
your STAR bank is missing your best recent story, your skills matrix lags your
real ability. CV Refresh is the maintenance loop that keeps the single source of
truth actually *true*. It pairs with the **Outcome Loop** (stage 08), which feeds
interview signal back in — together they make the KB a living system instead of a
one-time document.
