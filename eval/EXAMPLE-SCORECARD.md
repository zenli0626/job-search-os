# Example Scorecard

*Frame: evaluating a reference Job Search OS implementation. Generic stage and lane names throughout. Zero personal details.*

---

## Scorecard

| Stage | Automation | Repeatability | Evidence | Feedback | Output | Avg |
|---|---|---|---|---|---|---|
| Stage 1: Know Yourself | 2 | 4 | 5 | 2 | 4 | **3.4** |
| Stage 2: Story Mining | 2 | 3 | 3 | 1 | 3 | **2.4** |
| Stage 3: JD→Application | 3 | 4 | 4 | 1 | 4 | **3.2** |
| Stage 4: Daily Research | 4 | 4 | 2 | 1 | 3 | **2.8** |
| Stage 5: Manager Loop | 1 | 1 | 1 | 1 | 2 | **1.2** |
| **Overall** | **2.4** | **3.2** | **3.0** | **1.2** | **3.2** | **2.6** |

---

## Stage Commentary

### Stage 1: Know Yourself (avg 3.4)

**Strengths:**
- KB is thorough and well-structured across all template files; evidence citations are dense
- Career Brain skill has auto-trigger phrases and classifies requests correctly into use cases

**Weaknesses:**
- KB is static: no mechanism to ingest new work, projects, or promotions as they happen
- No feedback loop from interview outcomes back into the evidence base — rejected applications
  don't update gap-analysis, and interview misses don't flag STAR stories for revision

---

### Stage 2: Story Mining (avg 2.4)

**Strengths:**
- Coaching app is deployed and functional; the 6-probe loop is well-designed for honest excavation
- Multiple session types cover the main coaching use cases (excavation, company prep, decisions)

**Weaknesses:**
- Mined stories don't flow back to the STAR bank; the integration gap means every session's
  output lives only in chat history unless manually copied
- No feedback path from real interview performance — stories aren't flagged when they land poorly
  or promoted when they resonate

---

### Stage 3: JD→Application (avg 3.2)

**Strengths:**
- Structured APPLY/STRETCH/SKIP gate prevents undifferentiated mass-applying
- Tailoring is grounded in KB with explicit no-fabrication rules; output quality is consistent

**Weaknesses:**
- Fit score is produced once and never revisited; if a role's requirements shift (e.g., updated
  JD) or the application is rejected at screening, there's no mechanism to update the score
  or capture why
- No signal on whether applications were screened out vs. advanced — can't diagnose whether
  the gap penalties were predictive

---

### Stage 4: Daily Research (avg 2.8)

**Strengths:**
- Best-automated stage: sweeps Greenhouse, Ashby, and Lever in parallel; multi-layer filtering
  (lane + exclusion + seniority + location) produces a tight, calibrated output
- Config-driven lane patterns are easy to tune

**Weaknesses:**
- As implemented, output was raw stdout with no persistence and no cross-run deduplication;
  the same jobs surface every run without a way to know which were already seen
- No connection to Stage 3: sweep produces matches but the user must manually copy-paste
  them into the scoring workflow; the "to_review" queue doesn't exist yet

---

### Stage 5: Manager Loop (avg 1.2)

**Strengths:**
- The pipeline schema and weekly review prompt exist and are well-specified

**Weaknesses:**
- Least built stage: no funnel tracker, no status log, no weekly cadence, no application
  velocity tracking, no follow-up queue — everything is ad hoc
- This is the highest-priority stage to build; without it, the system has no connective tissue

---

## Overall Summary

**Overall average: 2.6 / 5**

*"Early pipeline, strong inputs, broken middle."*

Each stage operates as a silo. Strong evidence base and no-fabrication discipline in Stage 1.
Decent automation in Stage 4. But no data flows automatically between stages. Stage 2's
stories don't reach Stage 1's STAR bank. Stage 4's sweep doesn't feed Stage 3's scorer.
No application is tracked after it's sent. No outcome updates the KB.

**The highest-leverage fix is Stage 5 (Manager Loop).** Specifically: a status table where
every application has a URL, company, stage, date, and lane. Once that exists, Stage 4 can
feed it automatically, Stage 2's feedback can flow back, and the weekly review becomes
computable rather than ad hoc.
