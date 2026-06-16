# Integration: Story Mining ↔ Career KB

## The Intended Design

Story Mining (Stage 01) should have a **bi-directional sync** with the Career KB (Stage 00):

```
┌─────────────────────────────┐          ┌─────────────────────────────┐
│  Stage 00: Career KB        │          │  Stage 01: Story Mining     │
│  accomplishments-STAR.md    │──────▶   │  Coaching sessions          │
│                             │  pull    │  6-probe excavation         │
│  (source of truth for       │          │  Delivery drill             │
│   stories going INTO        │          │                             │
│   interviews)               │◀──────   │  (refines and surfaces      │
│                             │  push    │   new stories from lived    │
└─────────────────────────────┘          │   experience)               │
                                         └─────────────────────────────┘
```

**Pull direction (KB → Mining):** The coaching session loads existing STAR stories from
the KB so the coach has context. It can suggest which existing story to drill rather than
excavating from scratch.

**Push direction (Mining → KB):** When the 6-probe loop produces a refined or newly
excavated story, the coach produces a formatted entry ready to paste into
`accomplishments-STAR.md`. The user copies it in.

---

## The Current Gap

**Neither direction is automated.** The two stages currently operate as isolated tools:

1. The coaching session doesn't read the KB. It has no access to existing STAR stories.
2. Refined stories from mining sessions are not written back to the KB. The user has to
   manually copy the formatted output from the coaching session into `accomplishments-STAR.md`.

In practice, this means:
- The coach may excavate a story that already exists in a better-formed version in the KB
- Refined stories often live only in chat history and are never captured
- The KB gets stale: interview feedback ("this story didn't land") never updates the entry

---

## Intended Fix (TODO)

### Short-term (manual, no code required)
At the end of every story-mining session, the coach produces a formatted STAR bank entry.
The user runs:
```
@career-brain Append this story to my STAR bank:
[paste the formatted entry from the coaching session]
```
This at least standardizes the format. The human still does the copy-paste.

### Medium-term (file-based sync)
The coaching session is given `CAREER_KB_PATH` and can read `accomplishments-STAR.md`
at session start. At session end, the coach writes a new story draft to a staging file:
```
$CAREER_KB_PATH/drafts/story-draft-[id].md
```
A human review step then promotes drafts to the main STAR bank. This avoids auto-overwriting
the canonical KB but closes most of the friction.

### Long-term (outcome loop)
When an interview happens, the outcome (strong story / didn't land / wasn't asked) is
noted in the pipeline tracker. A weekly prompt prompts the manager to flag which stories
performed and which need revision. That feedback propagates back to the STAR bank entries
via a "performance notes" field.

---

## Design Principle

The KB is the source of truth. Mining sessions are a workspace. The sync direction is:
**workspace → KB review → KB commit**, not automatic overwrite. This prevents a bad
coaching session from degrading a hard-won, well-evidenced STAR story.
