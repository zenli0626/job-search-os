# Application Package — Prompt / Recipe

## When to Use

Run this prompt after a JD scores APPLY (70+) or STRETCH (45–69) in the fit scorer.
Do NOT run for SKIP roles (score < 45) — the return on investment isn't there.

This recipe directs the Career Brain (Stage 00) to produce a complete application package
and write the outputs to `applications/[COMPANY_SLUG]/`.

---

## Inputs Required

Before running, gather:
- [ ] The JD text (paste below)
- [ ] The fit scorer output (score, verdict, matched strengths, gap penalties, pitch angle)
- [ ] The company name and role title
- [ ] Any specific context: hiring manager name, referral, company news you want to reference

---

## The Prompt

Copy everything below the `---` and paste it into Claude Code (or your LLM) along with the JD and scorer output.

---

```
You are the Career Brain. I need a full application package for the role below.

ROLE: [COMPANY_NAME] — [ROLE_TITLE]
JD: [PASTE JD HERE]

FIT SCORER OUTPUT:
- Score: [SCORE] ([VERDICT])
- Matched strengths: [LIST FROM SCORER]
- Gap penalties: [LIST FROM SCORER]
- Recommended pitch angle: [PITCH_ANGLE FROM SCORER]

CAREER KB PATH: $CAREER_KB_PATH
(Read CAREER_CONTEXT.md, accomplishments-STAR.md, skills-matrix.md, and resume-variants.md before producing any output.)

DELIVERABLES — produce all of the following:

## 1. Resume Tailoring Notes
- Select the best base variant from resume-variants.md
- List the top 5 bullet edits: what to change and why (cite KB source for each)
- Flag any JD requirement with no KB evidence (do NOT invent evidence)

## 2. Cover Letter
- ~280 words
- Opening: connect the company's specific challenge/mission to a KB accomplishment
- Body: 2 paragraphs covering the top 2 matched strengths with specific evidence
- Closing: why this role, why now — specific and honest
- NO filler: no "passionate", no "proven track record", no generic enthusiasm

## 3. Gap Acknowledgment Notes (if STRETCH)
- For each gap penalty, provide the 2-sentence framing strategy (from gap-analysis.md)
- Flag which gaps are likely to come up in screening vs. which won't

## 4. Interview Prep Summary (optional, include if score < 80)
- 3 likely first-round behavioral questions based on the JD
- For each: the best matching STAR story from KB (cite story name/ID)
- Flag any likely question with no matching story (gap to fill)

## 5. Output Directory
Write each deliverable as a separate file to: applications/[COMPANY_SLUG]/
  - resume-notes.md
  - cover-letter.md
  - gap-notes.md (if STRETCH)
  - interview-prep.md (if score < 80)

CONSTRAINTS:
- No fabrication. Every claim cites a KB source.
- No metric invented. If a number doesn't exist in the KB, say "no metric available."
- Apply public-surface masking to cover letter (per CAREER_CONTEXT.md masking instructions).
- If a required deliverable can't be completed due to missing KB data, flag it as a gap.
```

---

## After Running

1. Review `applications/[COMPANY_SLUG]/cover-letter.md` — edit to your voice before sending
2. Apply resume edits from `resume-notes.md` to your base resume file
3. Update the pipeline tracker in `manager/pipeline-tracker.html`:
   - Company, Title, Score, Lane, Stage: APPLIED, Date applied
4. Set a 7-day follow-up reminder

---

## No-Fabrication Reminder

The Career Brain will flag missing KB evidence rather than invent it. If you see a flag
like "No story found for: leading a team of >10 people", that's working as intended.
Either add the story to your STAR bank (via Stage 01 excavation) or accept the gap.
Do not manually add invented bullets to the output.
