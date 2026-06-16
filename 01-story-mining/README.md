# Stage 01: Story Mining

## What This Stage Does

Story Mining is the training layer of the Job Search OS. It does two things:

1. **Excavates STAR stories** from your lived experience using a structured 6-probe coaching loop
2. **Drills interview delivery** — helps you practice speaking stories aloud, pressure-tests them, and preps company-specific angles

The output flows back into your Career KB (`00-know-yourself/templates/accomplishments-STAR.md`). Or it should — see the gap note in `INTEGRATION.md`.

---

## The Sessions-as-Data Architecture

Each coaching session is a small data object:
```js
{
  id: "story-mining",
  name: "Story Mining",
  blurb: "Excavate a STAR story using the 6-probe loop",
  category: "excavation",
  systemPrompt: "..."
}
```

This means:
- No per-session UI required — the session object is the UI config
- Sessions are pluggable: add new coaching modes by adding an object to the array
- The coaching logic lives entirely in the `systemPrompt` field
- A frontend just iterates the array to build a session picker

See `sessions.example.js` for a working example of 4 session types.

---

## The 6-Probe Excavation Loop

The core `story-mining.prompt.md` runs a structured excavation through 6 probes:

1. **Scene** — Where were you? Who was there? Set the context without editorializing.
2. **Feeling** — What were you feeling at the time (not what you should have felt)?
3. **The actual words** — What did you literally say or do in the key moment?
4. **The selfish read** — What did you want for yourself in that moment? Be honest.
5. **What was hard** — What was genuinely difficult about it?
6. **Personal vs. work cross-check** — Would this matter to you outside of work?

The coach does NOT praise. Praise shuts down honest reflection. The coach probes, asks follow-up questions, and stays neutral until the story is fully excavated. Then it produces a 3-sentence summary.

---

## Session Types

| Session | Purpose |
|---|---|
| Story Mining | Core 6-probe STAR excavation |
| Company Prep | Deep-dive on a specific target company: culture, business model, what interviewers there care about |
| Decision Pressure Test | Present a real career decision; coach surfaces second-order consequences and blind spots |
| 1-Minute Speech | Drill the "tell me about yourself" answer to a crisp, confident 60 seconds |

---

## Known Gap

Stories refined here don't automatically sync back to your STAR bank. See `INTEGRATION.md` for the intended design and the current workaround.

---

## Usage

Load the session you want in Claude Code or any LLM interface:
```
Paste the contents of story-mining.prompt.md, then describe the story you want to work on.
```

Or, if you have a web app pointing at `sessions.example.js`, select the session from the UI.
