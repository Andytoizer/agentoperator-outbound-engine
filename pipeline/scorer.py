"""
Contact shortlist scorer.

Given enriched contacts + ICP persona tiers, produce the send-ready
shortlist by ranking contacts within each (company, tier) bucket.

Ranking heuristics:
- Verified email (status=valid) > catch_all > not_found
- Has LinkedIn URL (+5)
- Title keyword match vs tier.titles (+10 per match)
- Seniority match (+5)
"""
from __future__ import annotations

from collections import defaultdict
from typing import Optional

from pipeline.icp import ICP


def _score_contact(contact: dict, tier_name: str, icp: ICP) -> int:
    score = 0
    if contact.get("email_status") == "valid":
        score += 20
    elif contact.get("email_status") == "catch_all":
        score += 10
    if contact.get("linkedin_url"):
        score += 5
    tier = next((t for t in icp.personas if t.name == tier_name), None)
    if tier:
        title_lower = (contact.get("title") or "").lower()
        for wanted in tier.titles:
            if wanted.lower() in title_lower:
                score += 10
                break
        if contact.get("seniority", "").lower() in [s.lower() for s in tier.seniority]:
            score += 5
    return score


def select_shortlist(contacts: list[dict], icp: ICP, per_account_cap: Optional[int] = None) -> list[dict]:
    """
    Return contacts grouped by (company_domain, persona_tier), top N per group.

    per_account_cap: override per-tier cap from ICP personas.
    """
    buckets: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for c in contacts:
        key = (c.get("company_domain", ""), c.get("persona_tier", ""))
        buckets[key].append(c)

    shortlist: list[dict] = []
    for (domain, tier_name), group in buckets.items():
        scored = [(_score_contact(c, tier_name, icp), c) for c in group]
        scored.sort(key=lambda x: x[0], reverse=True)
        tier = next((t for t in icp.personas if t.name == tier_name), None)
        cap = per_account_cap or (tier.per_account_cap if tier else 2)
        for score, c in scored[:cap]:
            c2 = dict(c)
            c2["shortlist_score"] = score
            shortlist.append(c2)
    shortlist.sort(key=lambda x: (x.get("company_domain", ""), x.get("persona_tier", ""), -x.get("shortlist_score", 0)))
    return shortlist
