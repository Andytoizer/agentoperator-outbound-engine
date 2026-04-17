"""
Send scheduler.

Reads a send sheet (markdown) and produces:
1. Gmail draft specs (one per contact).
2. Slack DM specs at T+0 (email send reminder, with LinkedIn URL +
   "connect task queued" note).
3. Slack DM specs at T+24h weekdays-only (LinkedIn send reminder, with
   profile URL + LI 1/2 + LI 2/2 copy).

The actual Gmail draft creation and Slack scheduling is done by the
caller via MCP tools. This module only builds the specs and computes
timings — keeping the logic unit-testable without hitting any APIs.

Deliverability built-ins:
- Varied 11-18 min gaps between sends (non-uniform).
- Configurable daily window (default 9-12 PDT local).
- Max N sends/day (default 10).
- Weekends skipped for 24h LI delay calc.
- --test gate required before live run (enforce in the CLI, not here).
"""
from __future__ import annotations

import random
import re
from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from pathlib import Path
from typing import Optional
from zoneinfo import ZoneInfo

from clients.gmail import DraftSpec, create_draft
from clients.slack import DMSpec, email_send_reminder, linkedin_send_reminder, schedule_dm


# ── Plan computation ────────────────────────────────────────────


@dataclass
class SendPlan:
    contacts: list[dict] = field(default_factory=list)
    email_sends: list[tuple[dict, datetime]] = field(default_factory=list)   # (contact, send_time)
    li_sends: list[tuple[dict, datetime]] = field(default_factory=list)      # (contact, send_time)


def _next_workday_same_time(dt: datetime) -> datetime:
    """Return dt +1 day if that's Mon-Fri, else advance to Monday."""
    candidate = dt + timedelta(days=1)
    while candidate.weekday() >= 5:  # Sat=5, Sun=6
        candidate += timedelta(days=1)
    return candidate


def _is_weekday(d: datetime) -> bool:
    return d.weekday() < 5


def plan_sends(
    contacts: list[dict],
    start_at: datetime,
    tz: str = "America/Los_Angeles",
    window_end_hour: int = 12,
    per_day_cap: int = 10,
    min_gap_min: int = 11,
    max_gap_min: int = 18,
    li_delay_hours: int = 24,
    rng_seed: Optional[int] = None,
) -> SendPlan:
    """
    Build a SendPlan with varied gaps. Fills the current day up to per_day_cap
    within [start_at, window_end_hour], then rolls to the next weekday morning
    (keeping start hour and minute at :03 as a small non-top-of-hour offset).
    """
    rng = random.Random(rng_seed)
    zone = ZoneInfo(tz)
    if start_at.tzinfo is None:
        start_at = start_at.replace(tzinfo=zone)
    start_hour = start_at.hour
    start_minute = start_at.minute

    plan = SendPlan(contacts=list(contacts))
    cursor = start_at
    day_count = 0

    for i, contact in enumerate(contacts):
        # roll to next weekday morning if past window or hit daily cap
        if day_count >= per_day_cap or cursor.hour >= window_end_hour or not _is_weekday(cursor):
            next_day = cursor + timedelta(days=1)
            while not _is_weekday(next_day):
                next_day += timedelta(days=1)
            cursor = next_day.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
            day_count = 0

        plan.email_sends.append((contact, cursor))

        # LinkedIn: T+24h workdays only
        li_time = cursor
        for _ in range(li_delay_hours // 24 or 1):
            li_time = _next_workday_same_time(li_time)
        plan.li_sends.append((contact, li_time))

        # advance cursor by a varied gap
        gap = rng.randint(min_gap_min, max_gap_min)
        cursor = cursor + timedelta(minutes=gap)
        day_count += 1

    return plan


# ── Send sheet parser ───────────────────────────────────────────


_CONTACT_BLOCK_RE = re.compile(
    r"^##\s+(?P<num>\d+)\.\s+(?P<name>[^—]+)—\s+(?P<title>[^,]+),\s+(?P<company>[^\n]+)$",
    re.MULTILINE,
)
_SUBJECT_RE = re.compile(r"^\*\*Subject:\*\*\s+(?P<subject>.+)$", re.MULTILINE)
_EMAIL_RE = re.compile(r"`(?P<email>[^`\s@]+@[^`\s]+)`")
_LI_LINKEDIN_RE = re.compile(r"^\*\*LI 1/2:?\*\*\s+(?P<li1>.+?)(?=\n\n|\n\*\*|\Z)", re.DOTALL | re.MULTILINE)
_LI_2_RE = re.compile(r"^\*\*LI 2/2:?\*\*\s+(?P<li2>.+?)(?=\n\n|\n---|\n##|\Z)", re.DOTALL | re.MULTILINE)


def parse_send_sheet(text: str) -> list[dict]:
    """Extract contacts + drafts from a send-sheet markdown.

    Expected per-contact block:
        ## 1. First Last — Title, Company
        `email@domain.com`  (or `⚠️ placeholder@...` for TODO)
        **Subject:** subject line
        body...

        **LI 1/2:** connect note
        **LI 2/2:** after-accept message
    """
    entries = []
    # Split on h2 sections (leading ##). Very lightweight parser — real files vary.
    blocks = re.split(r"\n(?=##\s+\d+\.)", text)
    for block in blocks:
        m = _CONTACT_BLOCK_RE.search(block)
        if not m:
            continue
        email_m = _EMAIL_RE.search(block)
        subject_m = _SUBJECT_RE.search(block)
        li1_m = _LI_LINKEDIN_RE.search(block)
        li2_m = _LI_2_RE.search(block)

        # Body: text between subject line and LI 1/2
        body = ""
        if subject_m and li1_m:
            body = block[subject_m.end(): li1_m.start()].strip()
        elif subject_m:
            body = block[subject_m.end():].strip()

        entries.append({
            "index": int(m.group("num")),
            "full_name": m.group("name").strip(),
            "title": m.group("title").strip(),
            "company_name": m.group("company").strip(),
            "email": email_m.group("email") if email_m else "",
            "subject": subject_m.group("subject").strip() if subject_m else "",
            "body": body,
            "li_note_1": li1_m.group("li1").strip() if li1_m else "",
            "li_note_2": li2_m.group("li2").strip() if li2_m else "",
            "email_is_placeholder": bool(email_m and "placeholder" in email_m.group("email").lower()),
        })
    return entries


# ── Spec emission (Gmail drafts + Slack DMs) ────────────────────


def build_gmail_drafts(entries: list[dict]) -> list[DraftSpec]:
    return [create_draft(to=e["email"], subject=e["subject"], body=e["body"]) for e in entries]


def build_slack_email_reminders(
    plan: SendPlan,
    entries: list[dict],
    channel_id: str,
    vertical_by_domain: Optional[dict] = None,
) -> list[DMSpec]:
    total = len(entries)
    out = []
    for i, ((contact, send_time), entry) in enumerate(zip(plan.email_sends, entries), 1):
        vertical = ""
        if vertical_by_domain:
            vertical = vertical_by_domain.get(contact.get("company_domain", ""), "")
        warning = None
        if entry.get("email_is_placeholder"):
            warning = "Draft has placeholder To: address — source real email, replace, then send."
        msg = email_send_reminder(
            index=i,
            total=total,
            contact_name=entry.get("full_name", contact.get("full_name", "")),
            title=entry.get("title", contact.get("title", "")),
            company=entry.get("company_name", contact.get("company_name", "")),
            vertical=vertical,
            email_subject=entry.get("subject", ""),
            linkedin_url=contact.get("linkedin_url", ""),
            send_warning=warning,
        )
        out.append(schedule_dm(channel_id=channel_id, post_at=int(send_time.timestamp()), message=msg))
    return out


def build_slack_linkedin_reminders(
    plan: SendPlan,
    entries: list[dict],
    channel_id: str,
    vertical_by_domain: Optional[dict] = None,
    ab_arm_by_contact=None,
) -> list[DMSpec]:
    total = len(entries)
    out = []
    for i, ((contact, send_time), entry) in enumerate(zip(plan.li_sends, entries), 1):
        vertical = ""
        if vertical_by_domain:
            vertical = vertical_by_domain.get(contact.get("company_domain", ""), "")
        arm = ab_arm_by_contact(contact) if ab_arm_by_contact else None
        warning = None
        if entry.get("email_is_placeholder"):
            warning = "Only send LI if the email actually went out (draft had placeholder address)."
        msg = linkedin_send_reminder(
            index=i,
            total=total,
            contact_name=entry.get("full_name", contact.get("full_name", "")),
            company=entry.get("company_name", contact.get("company_name", "")),
            vertical=vertical,
            linkedin_url=contact.get("linkedin_url", ""),
            li_note_1=entry.get("li_note_1", ""),
            li_note_2=entry.get("li_note_2") or None,
            arm=arm,
            send_warning=warning,
        )
        out.append(schedule_dm(channel_id=channel_id, post_at=int(send_time.timestamp()), message=msg))
    return out
