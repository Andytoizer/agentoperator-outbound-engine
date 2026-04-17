---
name: plan-campaign
description: Plan a full outbound campaign in phases. Use this as the FIRST move when someone just cloned the repo and wants to run end-to-end. Writes CAMPAIGN_PLAN.md with six phases, each gated by a handoff file. Skip this and jump to individual skills if you only want one capability.
---

# /plan-campaign — campaign orchestrator

## When to use

- Someone just cloned this repo and hasn't run anything yet.
- User says "let's run a campaign" or "plan an outbound push" without specifying a capability.
- A long campaign is splitting across sessions and you need a fresh plan.

Do NOT use if the user explicitly asks for a specific capability (`/define-icp`, `/enrich-emails`, etc.) — jump straight there.

## What it produces

- `CAMPAIGN_PLAN.md` at the repo root — the master plan, 6 phases.
- `handoffs/PHASE_1.md` through `handoffs/PHASE_6.md` scaffolds — filled in as each phase completes.

## Steps

1. **Ask four questions** (one at a time, not a form):
   - Who are you selling to? (one-sentence ICP hypothesis)
   - How many contacts in the first batch? (default 15 if unclear)
   - When do you want the first sends to fire? (default: next weekday 9am local)
   - What's in the repo already? (fresh / existing ICP / existing target list / existing contacts)

2. **Pick a resume point** based on answer 4. If they already have a shortlist, skip to Phase 4. If they have an ICP, skip to Phase 2. Default: start at Phase 1.

3. **Write `CAMPAIGN_PLAN.md`** using `templates/CAMPAIGN_PLAN.md` as the scaffold. Fill in:
   - Campaign name + ICP hypothesis
   - Batch size + timeline
   - Which phases are active (skip any the user already has output for)
   - The six phase → skill mapping (see below)

4. **Create handoff scaffolds** — copy `templates/HANDOFF_PHASE_N.md` once per active phase into `handoffs/`.

5. **Tell the user what to run next**. Point them at the first active phase's skill:
   > "Plan written to CAMPAIGN_PLAN.md. Phase 1 is ICP definition. Run `/define-icp` when you're ready. Each phase writes a handoff file so we can split across sessions."

## The six phases

| # | Phase | Skill | Exit gate |
|---|---|---|---|
| 1 | ICP definition | `/define-icp` | `templates/icp.yaml` validates |
| 2 | Target accounts | `/build-target-accounts` | `people/accounts.json` exists with N ≥ batch_size × 3 |
| 3 | People at accounts | `/find-people-at-accounts` | `people/contacts_raw.json` with ≥ batch_size contacts across tiers |
| 4 | Email enrichment | `/enrich-emails` | `people/contacts_enriched.json`, ≥ 80% email hit rate |
| 5 | Research + write | `/research-company-and-contact` then `/write-email-and-linkedin` | `drafts/SEND_SHEET.md` with approved drafts for every contact |
| 6 | Schedule + send | `/schedule-sends` | Gmail drafts created, Slack DMs scheduled at T+0 + T+24h |

Each phase is independently runnable — users can skip ahead if they have upstream artifacts from another source (existing CRM export, Apollo pull, etc.).

## Gate philosophy

Every phase writes a handoff file on exit. The next phase reads it on entry. This means:
- A campaign can pause mid-run and resume in a new session.
- Nothing downstream runs against stale state — the handoff is the contract.
- If a gate fails (e.g. hit rate < 80%), the plan forces you to address it before moving on.
