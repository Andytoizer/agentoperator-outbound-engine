---
name: write-email-and-linkedin
description: Draft cold email + LinkedIn 1/2 + LinkedIn 2/2 for every contact in the shortlist, using the repo's voice doc and locked structural patterns. Iterates with the user until the whole send sheet is approved. Phase 5b of a campaign.
---

# /write-email-and-linkedin — voice-locked drafting

## When to use

- Phase 5b of `/plan-campaign`, after `/research-company-and-contact` filled research files.
- Iterating on existing drafts (the user wants to rework tone on a send sheet).

## Prerequisites

- `people/shortlist.json` (or equivalent).
- `research/<slug>.md` per company.
- `config/voice/<your-voice>.md` — the voice doc.
- `config/voice/email_patterns.md` — locked structural rules.

## Steps

1. **Confirm voice doc** — by default the repo ships `config/voice/andys_voice.md` as an example. Users should:
   - If they ARE Andy: keep as-is.
   - If not: replace with their own voice file or run the `andys-voice` skill once as a template and customize from there.

2. **Build draft specs**:
   ```python
   import json
   from pathlib import Path
   from pipeline.writer import build_specs_from_shortlist

   shortlist = json.loads(Path("people/shortlist.json").read_text())

   def ab_arm(contact):
       # Simple: every 3rd SDR-tier contact gets "Loom", others get "POC"
       if contact.get("persona_tier") != "sdr_manager":
           return None
       return "Loom" if (hash(contact.get("full_name", "")) % 3) == 0 else "POC"

   specs = build_specs_from_shortlist(
       shortlist,
       research_dir="research/",
       voice_path="config/voice/andys_voice.md",
       patterns_path="config/voice/email_patterns.md",
       default_offer="Loom walkthrough",
       ab_assign_fn=ab_arm,
   )
   ```

3. **Draft in-conversation with Claude**, one spec at a time:
   - Paste `spec.draft_prompt()` output into the conversation (it's self-contained — has voice, patterns, research, contact info).
   - Claude produces subject + body + LI 1/2 + LI 2/2.
   - Iterate with the user until the draft lands. Typical revision cycles for voice: 5-15 rounds for the first draft in a batch, then 1-3 for subsequent drafts once the voice is locked.
   - Save each approved draft to `drafts/<slug>.md`.

4. **Assemble the send sheet** — `drafts/SEND_SHEET.md`:
   - One H2 per contact: `## N. First Last — Title, Company`
   - Email address in backticks: `` `email@domain.com` `` (or flag TODOs with `⚠️`)
   - `**Subject:** ...`
   - Body paragraphs
   - `**LI 1/2:** ...` and `**LI 2/2:** ...`
   See `examples/edtech_contech_batch1/drafts/_SEND_SHEET_batch1.md` for the shape.

5. **Pre-send checklist** at the top of the send sheet:
   - Missing / stale emails to fix
   - Fresh 2-min LinkedIn scan per contact before send (catches <30-day posts that change the hook)
   - Space sends over 2-3 days not a single blast
   - LI note 1/2 is the connect request; 2/2 goes immediately after accept (unless delayed per the scheduler)

6. **Handoff** — update `handoffs/PHASE_5b.md`:
   - Drafts approved count
   - A/B split (counts per arm)
   - Any contacts with placeholder emails still pending fix
   - Link to `drafts/SEND_SHEET.md`

## Gate

- Every contact in the shortlist has an approved draft OR a ⚠️ flag noting what's blocking.
- Pre-send checklist at the top of the send sheet.
- Send sheet parses cleanly via `pipeline.scheduler.parse_send_sheet()` (try it — if the regex misses a contact, the scheduler will silently skip them).

## Voice rules (locked in `config/voice/email_patterns.md`)

These survived the Batch 1 iteration and should NOT be re-litigated per campaign:

- **Connector opener** on every email. Peer-customer mention woven into the first sentence, not tacked on.
- **Personalization in the opener**, not after.
- **Customer workflow + real stats** (verified numbers, not invented).
- **Loom or POC offer on its own line.**
- **CTA = open question**, never a meeting ask.
- **Signoff: just "Andy"** (or your name) — no title, no link in the first email.
- Hyphens (`-`), never em dashes (`—`).
- No sentence starts with a colon.
- No listy persona dumps ("superintendents / comms directors / family engagement leads" — too salesy).
- No invented stats. No "60% invisible" math.
- No news signal from more than 12 months ago.
- No prior-job-history hooks.
- Contractions always.
- Short paragraphs (1-3 sentences).
- Rotate phrasing — don't use "pattern translates pretty directly" 4 times in one batch.

## Competitor-adjacent contacts

When your recipient's company competes with or is adjacent to your peer customer, **name it upfront**: "Quick heads-up since Seesaw and ClassDojo are clearly competitors..." Never hide the relationship.

## Drafting cadence

The first draft in a new batch always takes the longest — voice iteration. Once 2-3 drafts are locked, the rest go much faster because Claude has the voice in-context. A 15-contact send sheet typically takes 2-3 hours of interactive drafting + iteration.
