"""
People-at-accounts search.

Given a list of target accounts and an ICP (with persona tiers), find
the right people at each account. Writes a people_raw.json dump.

Strategy:
1. For each account, for each persona tier, run a provider search
   (AI Ark primary, Apollo secondary, web-search fallback).
2. Dedupe by linkedin_url.
3. Keep up to persona.per_account_cap contacts per (account, tier).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from clients import aiark
from pipeline.icp import ICP, PersonaTier


def _aiark_contact_filter(tier: PersonaTier) -> dict:
    """Build the AI Ark contact filter from a persona tier."""
    contact: dict = {}
    if tier.seniority:
        contact["seniority"] = {"any": {"include": tier.seniority}}
    if tier.department:
        contact["departmentAndFunction"] = {
            "department": {"any": {"include": [tier.department]}}
        }
    if tier.titles:
        contact["experience"] = {
            "title": {
                "current": {
                    "any": {
                        "include": {"mode": "SMART", "content": tier.titles}
                    }
                }
            }
        }
    return contact


def _normalize_person(p: dict, tier_name: str) -> dict:
    exp = (p.get("experience") or {})
    current = (exp.get("current") or {}) if isinstance(exp.get("current"), dict) else {}
    return {
        "first_name": p.get("first_name") or p.get("firstName", ""),
        "last_name": p.get("last_name") or p.get("lastName", ""),
        "full_name": p.get("full_name") or p.get("name") or f"{p.get('first_name', '')} {p.get('last_name', '')}".strip(),
        "title": p.get("title") or current.get("title", ""),
        "seniority": p.get("seniority", ""),
        "department": p.get("department", ""),
        "linkedin_url": p.get("linkedin_url") or p.get("linkedinUrl", ""),
        "company_name": p.get("company_name") or p.get("account", {}).get("name", ""),
        "company_domain": (p.get("company_domain") or p.get("account", {}).get("domain") or "").lower(),
        "persona_tier": tier_name,
        "source": p.get("source", "aiark"),
    }


def find_people_at_account(account: dict, icp: ICP, size: int = 25) -> list[dict]:
    """For one account, find people across all persona tiers."""
    all_people: list[dict] = []
    account_filter = {"domain": {"any": {"include": [account["domain"]]}}}
    for tier in icp.personas:
        contact_filter = _aiark_contact_filter(tier)
        try:
            resp = aiark.people_search(account=account_filter, contact=contact_filter, size=size)
            hits = resp.get("people") or resp.get("data") or []
        except Exception:
            hits = []
        normalized = [_normalize_person(p, tier.name) for p in hits]
        all_people.extend(normalized[:tier.per_account_cap])
    return all_people


def find_people_for_accounts(accounts: list[dict], icp: ICP, progress_cb=None) -> list[dict]:
    """Run people search across every account in the list."""
    total = len(accounts)
    all_people: list[dict] = []
    for i, account in enumerate(accounts, 1):
        people = find_people_at_account(account, icp)
        all_people.extend(people)
        if progress_cb:
            progress_cb(i, total, account, len(people))
    return dedupe_people(all_people)


def dedupe_people(people: list[dict]) -> list[dict]:
    """Dedupe by linkedin_url (falls back to name+domain)."""
    seen = set()
    out = []
    for p in people:
        key = (p.get("linkedin_url") or "").strip().lower()
        if not key:
            key = f"{p.get('full_name', '').lower()}::{p.get('company_domain', '').lower()}"
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(p)
    return out


def save_people(people: list[dict], path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(people, indent=2))


def load_people(path: str | Path) -> list[dict]:
    return json.loads(Path(path).read_text())
