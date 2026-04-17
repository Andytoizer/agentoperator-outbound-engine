# ============================================================
# INTEGRATION FILE — Apollo (optional) for organization + people search.
# Original: Used via the Apollo MCP tool inside Claude Code, so this file
#   is a placeholder showing the data shape the pipeline expects.
# What to change: wire this to Apollo REST (https://apolloapi.com) if you
#   want to run Python-native instead of driving it through Claude.
# ============================================================
"""
Apollo client stub.

The original workflow drives Apollo through Claude Code's MCP tool
(apollo_mixed_people_search, apollo_mixed_companies_search), so the Python
side just parses results out of JSON dumps Claude produces.

If you want a direct REST client:
- Base: https://api.apollo.io/v1
- Auth: X-Api-Key header
- People search: POST /mixed_people/search
- Company search: POST /mixed_companies/search

The pipeline expects lists of dicts with these keys (whatever the source):
    person: {first_name, last_name, full_name, title, seniority, department,
             linkedin_url, company_name, company_domain, company_id}
    company: {name, domain, industries, employee_count, linkedin_url, hq_city,
              hq_country}
"""
from __future__ import annotations

import json
from pathlib import Path


def load_people_from_json_dump(path: Path) -> list[dict]:
    """Load a raw Apollo JSON dump (from MCP tool output) into normalized dicts."""
    data = json.loads(Path(path).read_text())
    people = data.get("people") or data.get("contacts") or data
    if not isinstance(people, list):
        return []
    out = []
    for p in people:
        org = p.get("organization") or {}
        out.append({
            "first_name": p.get("first_name", ""),
            "last_name": p.get("last_name", ""),
            "full_name": p.get("name") or f"{p.get('first_name', '')} {p.get('last_name', '')}".strip(),
            "title": p.get("title", ""),
            "seniority": p.get("seniority", ""),
            "department": (p.get("departments") or [None])[0] or "",
            "linkedin_url": p.get("linkedin_url", ""),
            "company_name": org.get("name") or p.get("organization_name", ""),
            "company_domain": org.get("primary_domain") or org.get("website_url", "").replace("https://", "").replace("http://", "").rstrip("/"),
            "company_id": org.get("id", ""),
            "source": "apollo",
        })
    return out


def load_companies_from_json_dump(path: Path) -> list[dict]:
    """Load raw Apollo org search dump into normalized dicts."""
    data = json.loads(Path(path).read_text())
    orgs = data.get("organizations") or data.get("companies") or data
    if not isinstance(orgs, list):
        return []
    out = []
    for o in orgs:
        out.append({
            "name": o.get("name", ""),
            "domain": o.get("primary_domain") or o.get("website_url", "").replace("https://", "").replace("http://", "").rstrip("/"),
            "industries": o.get("industries") or [],
            "employee_count": o.get("estimated_num_employees", 0),
            "linkedin_url": o.get("linkedin_url", ""),
            "hq_city": o.get("city", ""),
            "hq_country": o.get("country", ""),
            "source": "apollo",
        })
    return out
