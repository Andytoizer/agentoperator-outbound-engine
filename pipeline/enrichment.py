"""
Email enrichment waterfall.

    Lead Magic (LinkedIn URL → name+domain) → Findymail (LinkedIn URL → name+domain)
    Cache every response on disk so a crash doesn't re-spend credits.
    Stop on first "valid" or "catch_all".

Public API:
    enrich_contacts(contacts, cache_path, progress_cb=None) -> list[dict]
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Optional

from clients import findymail, leadmagic

HIT_STATUSES = {"valid", "catch_all"}


@dataclass
class EnrichmentResult:
    email: str
    email_status: str
    email_source: str
    credits_consumed: int
    attempts: list[dict]


def _contact_key(contact: dict) -> str:
    if contact.get("linkedin_url"):
        return f"li::{contact['linkedin_url'].strip().lower()}"
    return f"nd::{(contact.get('first_name') or '').lower()}::{(contact.get('last_name') or '').lower()}::{(contact.get('company_domain') or '').lower()}"


def _is_hit(resp: dict) -> bool:
    return bool(resp.get("email")) and resp.get("status", "").lower() in HIT_STATUSES


def _load_cache(cache_path: Path) -> dict:
    if cache_path.exists():
        try:
            return json.loads(cache_path.read_text())
        except json.JSONDecodeError:
            return {}
    return {}


def _save_cache(cache_path: Path, cache: dict) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = cache_path.with_suffix(cache_path.suffix + ".tmp")
    tmp.write_text(json.dumps(cache, indent=2))
    os.replace(tmp, cache_path)


def _enrich_one(contact: dict, cache_entry: Optional[dict], providers: Optional[set] = None) -> EnrichmentResult:
    attempts: list[dict] = list(cache_entry.get("attempts", [])) if cache_entry else []
    tried = {(a["provider"], a["method"]) for a in attempts}

    first = (contact.get("first_name") or "").strip()
    last = (contact.get("last_name") or "").strip()
    full_name = (contact.get("full_name") or f"{first} {last}").strip()
    domain = (contact.get("company_domain") or "").strip()
    linkedin = (contact.get("linkedin_url") or "").strip()

    for a in attempts:
        if _is_hit(a) and (providers is None or a["provider"] in providers):
            return EnrichmentResult(
                email=a["email"],
                email_status=a["status"],
                email_source=a["provider"],
                credits_consumed=sum(x.get("credits_consumed", 0) for x in attempts),
                attempts=attempts,
            )

    rungs: list[tuple[str, str, Callable[[], dict]]] = []
    if providers is None or "leadmagic" in providers:
        if linkedin:
            rungs.append(("leadmagic", "linkedin", lambda: leadmagic.find_email_by_linkedin(linkedin)))
        if first and last and domain:
            rungs.append(("leadmagic", "name_domain", lambda: leadmagic.find_email_by_name_domain(first, last, domain)))
    if providers is None or "findymail" in providers:
        if linkedin:
            rungs.append(("findymail", "linkedin", lambda: findymail.find_email_by_linkedin(linkedin)))
        if full_name and domain:
            rungs.append(("findymail", "name_domain", lambda: findymail.find_email_by_name_domain(full_name, domain)))

    for provider, method, call in rungs:
        if (provider, method) in tried:
            continue
        try:
            resp = call()
        except Exception as e:
            resp = {"email": "", "status": "error", "credits_consumed": 0, "source": provider, "raw": {"error": str(e)}}
        attempt = {
            "provider": provider,
            "method": method,
            "email": resp.get("email", ""),
            "status": resp.get("status", "unknown"),
            "credits_consumed": resp.get("credits_consumed", 0),
        }
        attempts.append(attempt)
        if _is_hit(attempt):
            break

    total_credits = sum(a.get("credits_consumed", 0) for a in attempts)
    hit = next((a for a in attempts if _is_hit(a)), None)
    if hit:
        return EnrichmentResult(
            email=hit["email"], email_status=hit["status"], email_source=hit["provider"],
            credits_consumed=total_credits, attempts=attempts,
        )
    last_attempt = attempts[-1] if attempts else None
    return EnrichmentResult(
        email="",
        email_status=(last_attempt["status"] if last_attempt else "no_inputs"),
        email_source="",
        credits_consumed=total_credits,
        attempts=attempts,
    )


def enrich_contacts(
    contacts: Iterable[dict],
    cache_path: Path,
    progress_cb: Optional[Callable[[int, int, dict, EnrichmentResult], None]] = None,
    providers: Optional[set] = None,
) -> list[dict]:
    """Enrich an iterable of contacts; returns list with email fields merged in.
    Cache is read/written at cache_path as the run progresses (resumable).
    """
    contacts = list(contacts)
    total = len(contacts)
    cache = _load_cache(cache_path)
    enriched: list[dict] = []

    for idx, contact in enumerate(contacts, 1):
        out = dict(contact)
        key = _contact_key(contact)
        result = _enrich_one(contact, cache.get(key), providers=providers)
        cache[key] = {
            "email": result.email,
            "status": result.email_status,
            "source": result.email_source,
            "attempts": result.attempts,
        }
        _save_cache(cache_path, cache)

        out.update({
            "email": result.email,
            "email_status": result.email_status,
            "email_source": result.email_source,
            "email_credits": result.credits_consumed,
            "email_attempts": result.attempts,
        })
        enriched.append(out)
        if progress_cb:
            progress_cb(idx, total, contact, result)

    return enriched
