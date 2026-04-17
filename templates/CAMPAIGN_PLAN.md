# Campaign Plan — [Campaign Name]

Filled in by `/plan-campaign`. Update as phases complete.

## Overview

- **Campaign name**: [e.g. "EdTech + ConstructionTech Batch 1"]
- **ICP hypothesis**: [one sentence]
- **Batch size**: [e.g. 15 contacts]
- **Timeline**: [e.g. first sends Mon 2026-04-20, 9am PDT]
- **Success signal**: [e.g. ≥2 positive replies from the SDR arm to prove A/B design]

## Phases

- [ ] **Phase 1 — ICP** (`/define-icp`) — writes `templates/icp.yaml`
- [ ] **Phase 2 — Target accounts** (`/build-target-accounts`) — writes `people/accounts.json`
- [ ] **Phase 3 — People at accounts** (`/find-people-at-accounts`) — writes `people/contacts_raw.json`
- [ ] **Phase 4 — Email enrichment** (`/enrich-emails`) — writes `people/contacts_enriched.json`
- [ ] **Phase 5a — Research** (`/research-company-and-contact`) — writes `research/<slug>.md`
- [ ] **Phase 5b — Write** (`/write-email-and-linkedin`) — writes `drafts/SEND_SHEET.md`
- [ ] **Phase 6 — Schedule** (`/schedule-sends`) — writes `SEND_SCHEDULE.md`, creates Gmail drafts + Slack DMs

## Handoffs

Each phase writes to `handoffs/PHASE_N.md` on exit. Start a new session from the most recent handoff.

## Notes

[Anything specific to this campaign — unusual constraints, stakeholders, what's different from the default flow]
