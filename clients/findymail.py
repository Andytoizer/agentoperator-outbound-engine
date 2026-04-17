# ============================================================
# INTEGRATION FILE — Email enrichment, fallback rung.
# Original: Built for Findymail (https://findymail.com/api)
# What to change: if you use a different fallback provider, replace HTTP
#   calls but keep the normalized return shape.
# ============================================================
"""
Findymail API client — email finding fallback rung.
Base URL: https://app.findymail.com/api
Auth: Bearer token.

Endpoints used:
- POST /search/name      body: {"name", "domain"}
- POST /search/linkedin  body: {"linkedin_url"}

Normalized response:
    {"email": "...", "status": "valid|not_found|unknown",
     "credits_consumed": int, "source": "findymail", "raw": {...}}
"""
from __future__ import annotations

import time

import requests

from config.settings import FINDYMAIL_API_BASE, FINDYMAIL_API_KEY

_LAST_CALL = 0.0
_MIN_INTERVAL = 0.2


def _throttle() -> None:
    global _LAST_CALL
    now = time.monotonic()
    wait = _MIN_INTERVAL - (now - _LAST_CALL)
    if wait > 0:
        time.sleep(wait)
    _LAST_CALL = time.monotonic()


def _headers() -> dict:
    if not FINDYMAIL_API_KEY:
        raise RuntimeError("FINDYMAIL_API_KEY not set in .env")
    return {
        "Authorization": f"Bearer {FINDYMAIL_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def _post(path: str, payload: dict, timeout: int = 30) -> dict:
    _throttle()
    url = f"{FINDYMAIL_API_BASE}{path}"
    resp = requests.post(url, json=payload, headers=_headers(), timeout=timeout)
    try:
        return resp.json()
    except ValueError:
        return {"error": f"non-json response ({resp.status_code}): {resp.text[:200]}"}


def _normalize(raw: dict) -> dict:
    contact = raw.get("contact") if isinstance(raw.get("contact"), dict) else None
    email = ""
    if contact:
        email = contact.get("email") or ""
    elif raw.get("email"):
        email = raw.get("email")
    if email:
        status = "valid"
    elif raw.get("error") or raw.get("message"):
        status = "not_found"
    else:
        status = "unknown"
    credits = raw.get("credits_consumed", raw.get("credits_used", 0)) or 0
    return {
        "email": email,
        "status": status,
        "credits_consumed": int(credits) if isinstance(credits, (int, float)) else 0,
        "source": "findymail",
        "raw": raw,
    }


def find_email_by_name_domain(name: str, domain: str) -> dict:
    if not (name and domain):
        return {"email": "", "status": "skipped_missing_input", "credits_consumed": 0, "source": "findymail", "raw": {}}
    return _normalize(_post("/search/name", {"name": name, "domain": domain}))


def find_email_by_linkedin(linkedin_url: str) -> dict:
    if not linkedin_url:
        return {"email": "", "status": "skipped_missing_input", "credits_consumed": 0, "source": "findymail", "raw": {}}
    return _normalize(_post("/search/linkedin", {"linkedin_url": linkedin_url}))


def credits() -> dict:
    _throttle()
    try:
        resp = requests.get(f"{FINDYMAIL_API_BASE}/credits", headers=_headers(), timeout=10)
        return resp.json() if resp.content else {}
    except Exception as e:
        return {"error": str(e)}
