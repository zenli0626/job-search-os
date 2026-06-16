# Architecture

## Two Rhythms

The system operates on two distinct cadences:

### Daily Top-of-Funnel (automated, low-effort)
- **Stage 03** sweeps ATS boards in parallel every morning (~30s, no LLM cost)
- New APPLY-tier matches drop into a `to_review` queue
- The Manager Loop surfaces these in the weekly digest

### Per-Opportunity Deep Work (high-effort, LLM-assisted)
- Each APPLY/STRETCH role triggers Stage 02: score, tailored resume, cover letter, interview prep
- Stage 01 surfaces the right STAR stories for that company's context
- Both draw on the Career KB (Stage 00) as the single source of truth

---

## Stage Handoffs

```
┌───────────────────────────────────────────────────────────────────┐
│  Stage 00: Know Yourself                                          │
│  Career KB (private markdown files) + Career Brain (skill)        │
│  ─────────────────────────────────────────────────────────────── │
│  Outputs: tailored resume, STAR stories, cover letter, gap framing│
│  Consumed by: Stage 01 (stories), Stage 02 (tailoring)           │
└───────────────────────┬───────────────────────────────────────────┘
                        │ reads KB
         ┌──────────────┴──────────────┐
         ▼                             ▼
┌─────────────────┐          ┌──────────────────────┐
│  Stage 01:      │          │  Stage 02:           │
│  Story Mining   │          │  JD → Application    │
│  ─────────────  │          │  ──────────────────  │
│  Excavates +    │          │  Scores JD,          │
│  refines STAR   │          │  produces tailored   │
│  stories via    │          │  application package │
│  coaching loop  │          │                      │
│                 │          │  Reads: KB           │
│  Gap: should    │          │  Inputs: JD text     │
│  write back to  │          │  Outputs: files in   │
│  KB STAR bank   │          │  applications/[co]/  │
└────────┬────────┘          └──────────┬───────────┘
         │                             │
         │  interview performance      │  application sent
         └──────────────┬──────────────┘
                        ▼
         ┌──────────────────────────┐
         │  Stage 03: Daily Sweep   │
         │  ──────────────────────  │
         │  Parallel ATS API calls  │
         │  Lane filter + exclusion │
         │  → sweep.sqlite (dedup)  │
         │  → job-targets-raw.json  │
         └──────────────┬───────────┘
                        │  net-new APPLY roles
                        ▼
         ┌──────────────────────────────────────────┐
         │  Manager Loop (weekly)                   │
         │  ────────────────────────────────────── │
         │  Reads: sweep.sqlite + status table      │
         │  Computes: velocity, response rate,       │
         │    interview rate, drop-off by lane       │
         │  Actions: follow-up queue, stage updates  │
         │  Writes: Week in Review markdown          │
         │  Closes loop: outcome → KB gap notes      │
         └──────────────────────────────────────────┘
```

---

## Key Design Principle: The Broken Middle

Most job-search setups fail in the middle. The inputs are strong:
- A polished resume
- A list of target companies
- Some STAR stories

But they fail on connective tissue:
- No record of which roles were applied to or when
- No signal on what's getting screened vs. advanced
- No cadence to follow up systematically
- No way to weight effort by what's actually working

**This framework's core job is the connective tissue.** The Manager Loop isn't optional ceremony — it's the mechanism that turns activity into learning.

### The three connections that matter most:
1. **Stage 03 → Stage 02:** Sweep produces a queue; Stage 02 consumes it. Without this, discovery and application are manually stitched by copy-paste.
2. **Stage 02 → Manager:** Applications sent become funnel rows. Without this, there's no pipeline velocity or follow-up cadence.
3. **Manager → Stage 00:** Outcomes (interview feedback, offer feedback, ghosted patterns) feed back into the KB gap analysis. Without this, the system doesn't learn.

---

## Data Flows

| Source | Format | Consumer |
|---|---|---|
| Career KB (`CAREER_KB_PATH/*.md`) | Markdown files | Career Brain skill (read-only) |
| `sweep.sqlite` | SQLite | Stage 03 (write), Manager Loop (read) |
| `job-targets-raw.json` | JSON array | Stage 02 manual review queue |
| `applications/[company]/` | Markdown files | Archival; referenced in Manager Loop |
| `pipeline-tracker.html` localStorage | JSON | Manager Loop dashboard |

---

## Extension Points

- **ATS APIs:** Add more ATS slugs in `config.json`. The sweep script handles Greenhouse, Ashby, and Lever natively. Add a new `fetch_*` function following the existing pattern.
- **Fit Rubric:** `rubric.example.json` is the schema. Copy it, customize strength buckets / gap buckets / dealbreakers for your own lane mix. Load it in `index.html`.
- **Career Brain:** The skill classifies requests into use cases. Add new use cases by extending the classification list and the corresponding output instructions.
- **Eval cadence:** Run `eval/eval-agent.prompt.md` monthly. The scorecard shows where the system has regressed or improved.
