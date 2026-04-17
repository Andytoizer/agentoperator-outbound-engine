---
name: find-people-at-accounts
description: Find the right buyers at each target account. Runs persona-tier searches (sales leaders, SDR managers, marketing) per account and writes people/contacts_raw.json. Phase 3 of a campaign.
---

# /find-people-at-accounts — surface buyers per account

## When to use

- Phase 3 of `/plan-campaign`, after `/build-target-accounts` wrote `people/accounts.json`.
- User has accounts but no contacts.

## Prerequisites

- `people/accounts.json` exists.
- `templates/icp.yaml` with persona tiers defined.
- AI Ark and/or Apollo credentials.

## Steps

1. **Load inputs**:
   ```python
   from pipeline.icp import load_icp
   from pipeline.target_accounts import load_accounts
   icp = load_icp("templates/icp.yaml")
   accounts = load_accounts("people/accounts.json")
   ```

2. **Run search** — one call per (account, persona tier):
   ```python
   from pipeline.people_search import find_people_for_accounts, save_people

   def progress(i, total, account, count):
       print(f"[{i}/{total}] {account['name']}: {count} contacts")

   people = find_people_for_accounts(accounts, icp, progress_cb=progress)
   save_people(people, "people/contacts_raw.json")
   ```

3. **Audit** — sample 20 random contacts. Check:
   - Title matches the persona tier (no stray VPs in the SDR bucket)
   - `linkedin_url` present for ≥80% (needed for enrichment + LI followup)
   - Company domains match the account list (catch name-collision bugs)

4. **Fallback — web search for missing contacts**:
   If AI Ark / Apollo returned nothing for a company but you need coverage,
   spawn parallel Claude sub-agents to do LinkedIn lookups (see
   `feedback_parallel_web_search.md` for the pattern if you're Andy).
   Split into batches of 30-40, merge JSON results back into the people list.

5. **Handoff** — update `handoffs/PHASE_3.md`:
   - Total contacts surfaced
   - Count per persona tier
   - Accounts with zero coverage (candidates for web-search fallback)
   - LinkedIn URL coverage %
   - Link to `people/contacts_raw.json`

## Gate

- `people/contacts_raw.json` has ≥ `batch_size` contacts.
- At least 1 contact in each persona tier you care about.
- LinkedIn URL coverage ≥ 80% (needed for both enrichment rung 1 and the LI followup step).

## Recommended provider stack

| Need | Default | Also works |
|---|---|---|
| Title-based search | AI Ark (`mode: SMART` for fuzzy title match) | Apollo, Sales Nav |
| Seniority filter | AI Ark `seniority` filter | Apollo `seniorities` |
| Department filter | AI Ark `departmentAndFunction` | Apollo `functions` |
| Long-tail coverage | Parallel Haiku sub-agents doing LinkedIn web search | LeadGenius, manual |

## Common failure modes

- **Title pollution** — "Director" returns Customer Success, Product, etc. alongside Sales. Always constrain with `department`.
- **Stale LinkedIn URLs** — some providers return URLs that 404. Validate before enrichment burns credits.
- **"SMART" mode too fuzzy** — `"SDR Manager"` under SMART can return random manager roles. Drop to WORD mode for precise titles.
