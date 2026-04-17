---
name: research-company-and-contact
description: Research each target company + key contacts before drafting. Spawns parallel Claude sub-agents to gather recent (<12 months, dated) signals for the connector opener. Writes research/<slug>.md per company. Phase 5a of a campaign.
---

# /research-company-and-contact — parallel research for connector hooks

## When to use

- Phase 5a of `/plan-campaign`, before `/write-email-and-linkedin`.
- Any time you need a fresh research pass on a company (e.g. 6 months after a first touch, re-researching with new news).

## Prerequisites

- `people/contacts_enriched.json` OR `people/shortlist.json` (the people you'll email).
- Web access (`WebSearch`, `WebFetch` tools).

## Steps

1. **Build research specs** from the shortlist:
   ```python
   import json
   from pathlib import Path
   from pipeline.research import build_specs_from_shortlist, save_spec

   shortlist = json.loads(Path("people/shortlist.json").read_text())
   specs = build_specs_from_shortlist(
       shortlist,
       connector_hypothesis="We work with ClassDojo — your competitor. Connector is that we sourced their district personas.",
   )
   for s in specs:
       save_spec(s, "research/")
   ```
   This writes one prompt-file per company at `research/<slug>.md` — the text inside is what a research sub-agent should execute.

2. **Spawn parallel sub-agents — one per company**:
   In Claude Code, for each spec file, spawn an Explore or general-purpose agent:
   ```
   Agent(description="Research <company>", prompt=<contents of research/<slug>.md>)
   ```
   Send multiple Agent calls in a SINGLE message so they run concurrently. Research for 10 companies in parallel takes ~5 min vs 30+ min sequential.

3. **Overwrite each research/<slug>.md** with the agent's output (the filled-in research, not the prompt).

4. **Consolidation pass** — read all research files, write `research/_consolidation.md` with:
   - Per-company: 1-line "what they do" + top 2 signals
   - Cross-company themes (e.g. 3 of 10 companies have an M&A story worth naming in the opener)

5. **Handoff** — update `handoffs/PHASE_5a.md`:
   - Company count researched
   - Signals per company (average, min, max)
   - Companies with <2 recent signals (flag for manual research or deprioritize)
   - Link to `research/_consolidation.md`

## Gate

- Each company has ≥ 2 dated signals (<12 months).
- At least 1 per-contact note per contact (LinkedIn posts scanned, current-role reality noted).
- No "2023 news" — delete anything older than 12 months from today.

## Research rules (locked from the Batch 1 voice iteration)

- **Current-company state signals only.** Never use prior-job references ("7 years at X", "came from Y"). They read creepy/researchy.
- **Dated, not "recently".** "March 2026" not "recently launched".
- **Don't invent stats.** If you can't source a number, don't use it.
- **News signals must be <12 months old.** Today is the anchor — older signals get stripped.
- **If LinkedIn is gated**, say so. Don't invent activity.
- **Hiring signals are directional, not news.** "Hiring SDRs" is useful context for the write step, not a news hook for the opener.

## Parallel sub-agent pattern

See Andy's memory `feedback_parallel_web_search.md` — for bulk LinkedIn lookups or company research, split into batches of 30-40 contacts/companies, run parallel Haiku agents, merge JSON results back. ~6x faster than sequential web search.
