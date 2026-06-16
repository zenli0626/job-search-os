# Stage 03: Daily Research — ATS Sweep

## What This Stage Does

A dependency-free Python script sweeps company ATS (Applicant Tracking System) boards in
parallel and filters job titles to configurable "fit lanes." No auth required, no LLM calls,
no `pip install`. Runs in ~30 seconds against 50+ company boards.

---

## How It Works

```
config.json (company slugs + lane filters)
        ↓
job-sweep.py (parallel HTTP requests to ATS APIs)
        ↓
  ┌─────────────────────────────────────────────────────┐
  │  For each posting:                                  │
  │  1. Apply lane inclusion regex (any lane matches?)  │
  │  2. Apply global exclusion regex (intern/junior?)   │
  │  3. Apply seniority gate (senior/director/head of?) │
  │  4. Apply location filter (no intl-only roles)      │
  └─────────────────────────────────────────────────────┘
        ↓
 sweep.sqlite (persistent dedup across runs)
 job-targets-raw.json (full current results)
        ↓
 STDOUT: only NET-NEW roles (not already in DB)
```

---

## Supported ATS Platforms

| Platform | API | Auth |
|---|---|---|
| Greenhouse | `https://boards-api.greenhouse.io/v1/boards/{slug}/jobs` | None |
| Ashby | `https://api.ashbyhq.com/posting-api/job-board/{slug}` | None |
| Lever | `https://api.lever.co/v0/postings/{slug}` | None |

Add company slugs to `config.json` (not `config.example.json` — that's the template).
To find a slug: go to the company's job page, look at the URL or the `greenhouse.io/...` path.

---

## Output

- **STDOUT:** Net-new roles not seen in a previous sweep (deduplicated by URL)
- **`sweep.sqlite`:** Persistent store with status tracking (`SEEN` / `APPLIED` / etc.)
- **`job-targets-raw.json`:** Full current results for manual review or Stage 02 input

---

## Pipeline Integration

`sweep.sqlite` is the shared data layer between Stage 03 and the Manager Loop (Stage 05):
- Stage 03 writes: `(url, title, company, lanes, location, first_seen, status='SEEN')`
- Stage 02 updates status to `APPLIED` when you submit an application
- Manager Loop reads to compute net-new APPLY-tier roles, follow-up queue, and funnel velocity

---

## Setup

```bash
# Copy the example config and customize it
cp 03-daily-research/config.example.json 03-daily-research/config.json
# Edit config.json: add your target companies + lane patterns

# Run
python3 03-daily-research/job-sweep.py

# Or with explicit paths
python3 03-daily-research/job-sweep.py \
  --config 03-daily-research/config.json \
  --db 03-daily-research/sweep.sqlite \
  --output 03-daily-research/job-targets-raw.json
```

---

## Scheduling

The sweep is most useful when run daily. Suggested approach:

**macOS (launchd):** Add a plist to `~/Library/LaunchAgents/` that runs the script at 7am.
**Linux (cron):**
```
0 7 * * * cd /path/to/job-search-os && python3 03-daily-research/job-sweep.py >> /tmp/sweep.log 2>&1
```

Since the script prints only net-new roles, a daily run produces a manageable digest.
Pipe the output to a notification (Telegram, Slack, email) to get morning alerts.
