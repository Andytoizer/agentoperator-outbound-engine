---
name: build-target-accounts
description: Build a ranked list of target companies from a validated ICP. Runs AI Ark / Apollo company search, scores accounts by vertical fit + headcount sweet spot + external signals, writes people/accounts.json. Phase 2 of a campaign.
---

# /build-target-accounts — ICP → ranked company list

## When to use

- Phase 2 of `/plan-campaign`, after `/define-icp` produced a valid `templates/icp.yaml`.
- User has an ICP but no target list yet.
- User has an ad-hoc list they want to expand with lookalikes.

## Prerequisites

- `templates/icp.yaml` validates.
- `AI_ARK_API_KEY` set in `.env` (primary provider) OR Apollo JSON dumps available.

## Steps

1. **Load the ICP**: `from pipeline.icp import load_icp; icp = load_icp("templates/icp.yaml")`.

2. **Ask about seed**:
   - "Starting fresh (pure ICP search) or seeding with known logos?"
   - If seeding: ask for 5-15 existing customers or known-good prospects as anchors.

3. **Run the search**:
   ```python
   from pipeline.target_accounts import search_accounts_aiark, score_accounts, dedupe_accounts, save_accounts
   accounts = search_accounts_aiark(icp, limit=200)
   accounts = dedupe_accounts(accounts)
   accounts = score_accounts(accounts, icp, signals=None)
   save_accounts(accounts, "people/accounts.json")
   ```

4. **Optional — layer in signals** (manual for now, automatable later):
   - Recent fundraising
   - Hiring SDRs / AEs / ops
   - Tech-stack changes (competitor platform adoption)
   - Build a `{domain: [signal_str, ...]}` dict and pass as `signals=` to `score_accounts`.

5. **Review the top 50 with the user** — paste `head -50` of the scored list. Kill obvious misfits by hand, write back.

6. **Handoff** — update `handoffs/PHASE_2.md`:
   - Total accounts surfaced
   - Top-scoring 20 (for quick scan)
   - Any signals layered in
   - Link to `people/accounts.json`

## Gate

- `people/accounts.json` has at least `batch_size × 3` accounts (headroom for people-search misses).
- Top 10 pass a sanity check with the user — no obvious wrong-vertical companies.

## Recommended provider stack

| Need | Default | Also works |
|---|---|---|
| Primary search | AI Ark | Clay, Crunchbase |
| Secondary / seed expansion | Apollo | ZoomInfo |
| Signals | Built-in scoring + manual layer | Clearbit Reveal, Common Room |

## Common failure modes

- **Zero hits** — ICP verticals too narrow, or AI Ark's SMART mode doesn't match your industry keywords. Try WORD or STRICT mode.
- **Too many hits** — you got 2000 companies. Tighten employee_range or add regions to cut.
- **Domain pollution** — scraped domains sometimes have `www.`, trailing slashes, or paths. `_normalize_company()` in `pipeline/target_accounts.py` cleans this, but audit the top results.
