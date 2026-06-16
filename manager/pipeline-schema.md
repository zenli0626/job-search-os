# Pipeline Schema

## The 8-Stage Funnel

Every role in your pipeline lives in exactly one stage at any given time.

```
SOURCED
    │
    ▼
APPLIED ──────────────────────────────────────────────────────▶ GHOSTED
    │                                                            (no response > 21 days)
    ▼
RECRUITER SCREEN ─────────────────────────────────────────────▶ REJECTED
    │
    ▼
HIRING MANAGER ───────────────────────────────────────────────▶ REJECTED
    │
    ▼
ONSITE / LOOP ────────────────────────────────────────────────▶ REJECTED
    │
    ▼
OFFER
    │
    ▼
ACCEPTED / DECLINED
```

### Stage Definitions

| Stage | Code | Meaning |
|---|---|---|
| Sourced | `SOURCED` | Found the role; not yet applied |
| Applied | `APPLIED` | Application submitted; waiting for response |
| Recruiter Screen | `RECRUITER` | Phone/video screen with recruiter scheduled or complete |
| Hiring Manager | `HM` | Hiring manager conversation scheduled or complete |
| Onsite / Loop | `ONSITE` | Full interview loop underway |
| Offer | `OFFER` | Verbal or written offer received |
| Rejected | `REJECTED` | Rejected at any stage (track which stage in notes) |
| Ghosted | `GHOSTED` | Applied > 21 days ago; no response |

---

## Shared Status Table Schema

This is the schema used by `sweep.sqlite` (written by Stage 03) and extended by the
pipeline tracker (updated manually via the HTML dashboard).

```sql
CREATE TABLE IF NOT EXISTS jobs (
    url        TEXT PRIMARY KEY,          -- canonical job URL (dedup key)
    title      TEXT NOT NULL,             -- job title as posted
    company    TEXT NOT NULL,             -- company slug or name
    lanes      TEXT NOT NULL DEFAULT '',  -- comma-separated matched lane codes
    location   TEXT NOT NULL DEFAULT '',  -- location string from ATS
    first_seen TEXT NOT NULL,             -- ISO 8601 datetime first discovered
    status     TEXT NOT NULL DEFAULT 'SEEN'
    -- status codes:
    --   SEEN        → discovered by sweep, not yet evaluated
    --   SKIP        → scored and rejected by fit scorer
    --   SOURCED     → bookmarked for application
    --   APPLIED     → application submitted
    --   RECRUITER   → recruiter screen stage
    --   HM          → hiring manager stage
    --   ONSITE      → onsite/loop stage
    --   OFFER       → offer received
    --   REJECTED    → rejected at any stage
    --   GHOSTED     → no response > 21 days
    --   DECLINED    → offer declined
);
```

### Extended tracking columns (add manually or via ALTER TABLE)

For richer tracking, add these columns as your pipeline grows:

```sql
ALTER TABLE jobs ADD COLUMN applied_date TEXT;   -- ISO 8601 date applied
ALTER TABLE jobs ADD COLUMN last_updated TEXT;   -- ISO 8601 last status change
ALTER TABLE jobs ADD COLUMN notes       TEXT;    -- free-form interview notes / outcome
ALTER TABLE jobs ADD COLUMN fit_score   INTEGER; -- fit scorer score (0–100)
ALTER TABLE jobs ADD COLUMN verdict     TEXT;    -- APPLY / STRETCH / SKIP
```

---

## Funnel Metrics

The weekly review computes these from the status table:

| Metric | Formula | Healthy range (rough benchmarks) |
|---|---|---|
| Application velocity | APPLIED rows / week | 3–8 for targeted search |
| Response rate | (RECRUITER + HM + ONSITE + OFFER + REJECTED) / APPLIED | 10–25% |
| Screen-to-HM rate | HM / RECRUITER | 40–70% |
| HM-to-onsite rate | ONSITE / HM | 50–80% |
| Offer rate | OFFER / ONSITE | 20–50% |
| Ghosted rate | GHOSTED / APPLIED | Should be < 30% |

"Healthy range" benchmarks vary widely by role type, market, and seniority. Track your
own trends over time rather than comparing to external benchmarks.

---

## Lane Breakdown

The `lanes` column allows per-lane funnel analysis. For example:

```sql
SELECT lanes, status, COUNT(*) as n
FROM jobs
WHERE status != 'SEEN' AND status != 'SKIP'
GROUP BY lanes, status
ORDER BY lanes, status;
```

This shows whether Lane A or Lane B roles are advancing further — a signal about
where your profile resonates most.
