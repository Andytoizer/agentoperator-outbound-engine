# ============================================================
# INTEGRATION FILE — Email enrichment, rung 1 of the waterfall.
# Original: Built for Lead Magic (https://docs.leadmagic.io)
# What to change: if you use a different rung-1 provider (Hunter, Prospeo),
#   replace the HTTP calls but keep the normalized return shape.
# What to preserve: status normalization (valid / catch_all / unknown /
#   not_found) — pipeline/enrichment.py relies on it.
# ============================================================
"""
Lead Magic API client — email finding from LinkedIn URL or name+domain.
Base URL: https://api.leadmagic.io
Auth: X-API-Key header.

Endpoints used:
- POST /email-finder       body: {"first_name", "last_name", "domain"}
- POST /b2b-social-email   body: {"profile_url"}   (LinkedIn URL -> email)

Normalized response:
    {"email": "...", "status": "valid|catch_all|unknown|not_found",
     "credits_consumed": int, "source": "leadmagic", "raw": {...}}
"""
from __future__ import annotations

import time

import requests

from config.settings import LEADMAGIC_API_BASE, LEADMAGIC_API_KEY

_LAST_CALL = 0.0
_MIN_INTERVAL = 0.1


def _throttle() -> None:
    global _LAST_CALL
    now = time.monotonic()
    wait = _MIN_INTERVAL - (now - _LAST_CALL)
    if wait > 0:
        time.sleep(wait)
    _LAST_CALL = time.monotonic()


def _headers() -> dict:
    if not LEADMAGIC_API_KEY:
        raise RuntimeError("LEADMAGIC_API_KEY not set in .env")
    return {
        "X-API-Key": LEADMAGIC_API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def _post(path: str, payload: dict, timeout: int = 30) -> dict:
    _throttle()
    url = f"{LEADMAGIC_API_BASE}{path}"
    resp = requests.post(url, json=payload, headers=_headers(), timeout=timeout)
    try:
        return resp.json()
    except ValueError:
        return {"error": f"non-json response ({resp.status_code}): {resp.text[:200]}"}


def _normalize(raw: dict) -> dict:
    email = raw.get("email") or raw.get("work_email") or ""
    status = (raw.get("status") or raw.get("email_status") or "").lower()
    if not status:
        if email:
            status = "valid"
        elif raw.get("message") or raw.get("error"):
            status = "not_found"
        else:
            status = "unknown"
    credits = raw.get("credits_consumed", raw.get("credits", 0)) or 0
    return {
        "email": email or "",
        "status": status,
        "credits_consumed": int(credits) if isinstance(credits, (int, float)) else 0,
        "source": "leadmagic",
        "raw": raw,
    }


def find_email_by_name_domain(first_name: str, last_name: str, domain: str) -> dict:
    if not (first_name and last_name and domain):
        return {"email": "", "status": "skipped_missing_input", "credits_consumed": 0, "source": "leadmagic", "raw": {}}
    return _normalize(_post("/email-finder", {"first_name": first_name, "last_name": last_name, "domain": domain}))


def find_email_by_linkedin(linkedin_url: str) -> dict:
    if not linkedin_url:
        return {"email": "", "status": "skipped_missing_input", "credits_consumed": 0, "source": "leadmagic", "raw": {}}
    return _normalize(_post("/b2b-social-email", {"profile_url": linkedin_url}))


def credits() -> dict:
    _throttle()
    try:
        resp = requests.get(f"{LEADMAGIC_API_BASE}/credits", headers=_headers(), timeout=10)
        return resp.json() if resp.content else {}
    except Exception as e:
        return {"error": str(e)}
