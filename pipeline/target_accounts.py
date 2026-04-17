"""
Target account list builder.

Given an ICP, produce a ranked list of companies to go after.
Two modes:
- Seed expansion: start with N known-good logos, find lookalikes via
  provider lookups (AI Ark, Apollo).
- Net-new: pure ICP filter, paginated company search.

The output is a list of dicts matching the "company" shape in clients/apollo.py:
    {name, domain, industries, employee_count, linkedin_url, hq_city, hq_country,
     score, matched_signals, source}
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from clients import aiark
from pipeline.icp import ICP


def search_accounts_aiark(icp: ICP, limit: int = 100) -> list[dict]:
    """Pull companies matching the ICP from AI Ark."""
    account_filter = icp.to_aiark_account_filter()
    all_results: list[dict] = []
    page = 0
    page_size = 25
    while len(all_results) < limit:
        resp = aiark.company_search(account=account_filter, page=page, size=page_size)
        hits = resp.get("companies") or resp.get("data") or []
        if not hits:
            break
        all_results.extend(hits)
        if len(hits) < page_size:
            break
        page += 1
    return [_normalize_company(c) for c in all_results[:limit]]


def _normalize_company(c: dict) -> dict:
    domain = c.get("domain") or c.get("primary_domain") or ""
    if domain:
        domain = domain.replace("https://", "").replace("http://", "").split("/")[0].lower()
    return {
        "name": c.get("name") or c.get("company_name", ""),
        "domain": domain,
        "industries": c.get("industries") or [],
        "employee_count": c.get("employee_count") or c.get("employeeSize") or 0,
        "linkedin_url": c.get("linkedin_url") or "",
        "hq_city": c.get("city") or "",
        "hq_country": c.get("country") or "",
        "source": c.get("source") or "aiark",
    }


def score_accounts(accounts: list[dict], icp: ICP, signals: Optional[dict] = None) -> list[dict]:
    """
    Score accounts for priority. Pure heuristic — tune for your context.

    Defaults:
    - +10 per matched vertical keyword in industries
    - +5  if employee count in the sweet spot middle third of ICP range
    - +3  per signal match (signals is {domain: [signal_str, ...]})
    """
    lo, hi = icp.employee_range
    sweet_lo, sweet_hi = lo + (hi - lo) // 3, lo + 2 * (hi - lo) // 3
    scored = []
    for a in accounts:
        score = 0
        industries = [i.lower() for i in a.get("industries", [])]
        for v in icp.verticals:
            if any(v.lower() in ind for ind in industries):
                score += 10
        emp = a.get("employee_count", 0)
        if sweet_lo <= emp <= sweet_hi:
            score += 5
        matched_signals = []
        if signals:
            sigs = signals.get(a["domain"], [])
            score += 3 * len(sigs)
            matched_signals = sigs
        a2 = dict(a)
        a2["score"] = score
        a2["matched_signals"] = matched_signals
        scored.append(a2)
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored


def dedupe_accounts(accounts: list[dict]) -> list[dict]:
    """Remove duplicates by domain."""
    seen = set()
    out = []
    for a in accounts:
        d = (a.get("domain") or "").lower().strip()
        if not d or d in seen:
            continue
        seen.add(d)
        out.append(a)
    return out


def save_accounts(accounts: list[dict], path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(accounts, indent=2))


def load_accounts(path: str | Path) -> list[dict]:
    return json.loads(Path(path).read_text())
