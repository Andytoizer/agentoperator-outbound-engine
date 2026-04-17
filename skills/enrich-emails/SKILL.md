---
name: enrich-emails
description: Run the email enrichment waterfall (Lead Magic → Findymail) on a contact list. Uses a resumable cache, never re-spends credits on previously-resolved contacts, and treats valid + catch_all as hits. Phase 4 of a campaign.
---

# /enrich-emails — Lead Magic → Findymail waterfall

## When to use

- Phase 4 of `/plan-campaign`, after `/find-people-at-accounts` wrote `people/contacts_raw.json`.
- Any time you need to resolve emails for a contact list.

## Prerequisites

- `people/contacts_raw.json` (or equivalent) with `first_name`, `last_name`, `company_domain`, `linkedin_url` fields.
- `LEADMAGIC_API_KEY` and `FINDYMAIL_API_KEY` in `.env`.

## Steps

1. **Test-gate first — non-negotiable.** Before the full run:
   ```bash
   python -c "from clients import leadmagic, findymail; print(leadmagic.credits(), findymail.credits())"
   ```
   Confirm both providers return balances. Misconfigured API keys are the #1 failure mode and burn credits silently when the error responses look like cache misses.

2. **Run on a 5-contact sample first**:
   ```python
   from pathlib import Path
   from pipeline.enrichment import enrich_contacts
   import json
   contacts = json.loads(Path("people/contacts_raw.json").read_text())[:5]
   out = enrich_contacts(contacts, cache_path=Path(".email_cache.json"))
   print([c["email_status"] for c in out])
   ```
   If all 5 come back `not_found`, something's wrong with domains or LinkedIn URLs. Stop and investigate.

3. **Run the full list**:
   ```python
   contacts = json.loads(Path("people/contacts_raw.json").read_text())
   enriched = enrich_contacts(contacts, cache_path=Path(".email_cache.json"),
                              progress_cb=lambda i, t, c, r: print(f"[{i}/{t}] {c.get('full_name')}: {r.email_status}"))
   Path("people/contacts_enriched.json").write_text(json.dumps(enriched, indent=2))
   ```

4. **Handoff** — update `handoffs/PHASE_4.md`:
   - Total contacts enriched
   - Hit rate (valid + catch_all)
   - Credit spend per provider
   - Gaps: contacts with no email (these go to the write step with TODO flag)
   - Link to `people/contacts_enriched.json`

## Gate

- Hit rate ≥ 80% (industry baseline for well-curated lists).
- If below 80%: check whether domains are broken, LinkedIn URLs are stale, or the waterfall providers are misconfigured. Don't move to Phase 5 with a bad hit rate — you'll waste research time on contacts you can't email.

## The waterfall (pipeline/enrichment.py)

```
Lead Magic
  ├─ LinkedIn URL first (highest accuracy)
  └─ name + domain fallback
      ↓ cached result? use it. valid/catch_all? stop. else →
Findymail
  ├─ LinkedIn URL
  └─ name + domain
      ↓ cached result? use it. valid? stop. else → no match.
```

Why this order:
- Lead Magic's LinkedIn lookup has the best accuracy for senior titles.
- Findymail is a cheaper fallback that catches what LM misses, especially for SMB domains.
- Status `catch_all` is a hit — most deliverable catch-all domains accept real emails even if the provider can't verify the exact mailbox.

## Recommended provider stack

| Rung | Default | Also works |
|---|---|---|
| 1 | Lead Magic | Prospeo, Hunter, Apollo |
| 2 | Findymail | Clay, ZoomInfo, Apollo |
| Validation | trust `status` field | NeverBounce, ZeroBounce |

The waterfall is modular — swap either rung by editing `clients/leadmagic.py` or `clients/findymail.py` and keeping the normalized return shape: `{email, status, credits_consumed, source, raw}`.

## Common failure modes

- **API key misconfigured** — silent fails look like cache misses. The test gate in step 1 prevents this.
- **Stale cache** — if you changed domains, the cache key still hits. Delete `.email_cache.json` to force re-run.
- **Catch-all treated as miss** — if you're strict (`valid` only), override with `HIT_STATUSES = {"valid"}` in `pipeline/enrichment.py`.
