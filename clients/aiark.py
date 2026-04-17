# ============================================================
# INTEGRATION FILE — Adapt this for your people-search provider.
# Original: Built for AI Ark (https://docs.ai-ark.com/reference)
# What to change: swap the HTTP calls if you use Clay / Lusha / another
#   provider. Keep the function signatures (people_search, company_search,
#   reverse_people_lookup) so pipeline/people_search.py keeps working.
# What to preserve: the filter-building pattern (any.include / exclude /
#   all.include) is extremely powerful — replicate the shape if possible.
# ============================================================
"""
AI Ark API client — B2B data for people and company search.
Base URL: https://api.ai-ark.com/api/developer-portal/v1
Auth: X-TOKEN header.
Rate limits: 5 req/sec, 300/min, 18,000/hour.

Filter nesting pattern (all filters use this):
    "field": {
        "any": { "include": [...], "exclude": [...] },
        "all": { "include": [...] }
    }
For text fields, include items are {"mode": "SMART"|"WORD"|"STRICT", "content": [...]}
For simple list fields, include items are plain strings.
"""
from __future__ import annotations

import json
import subprocess
import time

from config.settings import AI_ARK_API_BASE, AI_ARK_API_KEY

_LAST_CALL = 0.0
_MIN_INTERVAL = 0.2  # 5 req/sec


def _throttle() -> None:
    global _LAST_CALL
    now = time.monotonic()
    wait = _MIN_INTERVAL - (now - _LAST_CALL)
    if wait > 0:
        time.sleep(wait)
    _LAST_CALL = time.monotonic()


def _curl_post(endpoint: str, payload: dict) -> dict:
    _throttle()
    url = f"{AI_ARK_API_BASE}{endpoint}"
    result = subprocess.run(
        [
            "/usr/bin/curl", "-s",
            "-X", "POST",
            "-H", f"X-TOKEN: {AI_ARK_API_KEY}",
            "-H", "Content-Type: application/json",
            "-H", "Accept: application/json",
            "-d", json.dumps(payload),
            url,
        ],
        capture_output=True, text=True, timeout=60,
    )
    if result.returncode != 0:
        raise RuntimeError(f"curl failed: {result.stderr}")
    return json.loads(result.stdout)


def _curl_get(endpoint: str) -> dict:
    _throttle()
    url = f"{AI_ARK_API_BASE}{endpoint}"
    result = subprocess.run(
        [
            "/usr/bin/curl", "-s",
            "-H", f"X-TOKEN: {AI_ARK_API_KEY}",
            "-H", "Accept: application/json",
            url,
        ],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(f"curl failed: {result.stderr}")
    return json.loads(result.stdout)


def people_search(account: dict = None, contact: dict = None, page: int = 0, size: int = 10) -> dict:
    """Search for people across 500M+ profiles."""
    payload = {"page": page, "size": size}
    if account:
        payload["account"] = account
    if contact:
        payload["contact"] = contact
    return _curl_post("/people", payload)


def company_search(account: dict = None, page: int = 0, size: int = 10) -> dict:
    """Search for companies across 70M+ profiles."""
    payload = {"page": page, "size": size}
    if account:
        payload.update(account)
    return _curl_post("/companies", payload)


def reverse_people_lookup(email: str = None, linkedin_url: str = None) -> dict:
    """Look up a person by email or LinkedIn URL."""
    payload = {}
    if email:
        payload["email"] = email
    if linkedin_url:
        payload["linkedin_url"] = linkedin_url
    return _curl_post("/reverse-people-lookup", payload)


def export_single_person_with_email(person_id: str) -> dict:
    return _curl_post("/export-single-person-with-email", {"id": person_id})


def export_people_with_email(person_ids: list[str]) -> dict:
    return _curl_post("/export-people-with-email", {"ids": person_ids})


def export_people_results(track_id: str) -> dict:
    return _curl_get(f"/export-people-results/{track_id}")
