# Example Campaign — EdTech + ConstructionTech Batch 1 (sanitized)

Sanitized walkthrough of the first real batch this tool was built on. Names, emails, and LinkedIn URLs have been replaced with placeholders. Company names are preserved where they're public (the Freckle customer references — ClassDojo, BuildPass — are in Freckle's public case studies).

## What was in the real campaign

- 10 target companies — 5 EdTech (Seesaw, ParentSquare, Newsela, Raptor Technologies, Panorama Education) + 5 ConTech (Housecall Pro, BuildOps, CompanyCam, Jobber, Fieldwire)
- 15 contacts — 8 sales leaders (single Loom pitch) + 7 SDR/BDR managers (A/B test: 4 POC arm, 3 Loom arm)
- Peer customers in the connector opener: ClassDojo for EdTech, BuildPass for ConTech
- 2 pre-send blockers (stale / missing email) resolved via Lead Magic re-run before send

## What's in this directory

- `icp.yaml` — the EdTech ICP used for Phase 1
- `companies/accounts.json` — target account list (sanitized domains)
- `people/shortlist.json` — final shortlist (names redacted to `[EdTech Sales Leader 1]` etc.)
- `research/<slug>.md` — per-company research outputs (5 samples)
- `drafts/SEND_SHEET.md` — the full 15-contact send sheet in final form
- `handoffs/` — handoff files from each phase

## What you can learn by reading this

1. **The ICP shape** — verticals, employee range, persona tiers, positioning
2. **The send-sheet format** — exact markdown structure the scheduler parses
3. **The connector-opener pattern** — peer customer + why-it-applies woven into the first sentence
4. **The A/B split structure** — POC vs Loom arm, same opener/workflow, different CTA
5. **The pre-send checklist** — what the /write skill flags before /schedule-sends runs
6. **The handoff cadence** — what each phase writes so the next phase can resume cleanly

## What's redacted

- Individual contact first/last names → `[Sales Leader 1]`, `[SDR Manager 3]`, etc.
- Email addresses → `contact1@example-edtech.com`
- LinkedIn URLs → `https://linkedin.com/in/example-contact-1`
- Any research signal that names a specific person at a company

Company names are preserved because they're public — the campaigns are cold outreach to publicly-listed sales leaders, not insider information.

## Running against this example

You can't — these are sanitized dumps, not live API results. To run a real campaign, follow `CLAUDE.md` → `/plan-campaign` from the repo root.
