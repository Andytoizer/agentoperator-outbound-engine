# ============================================================
# INTEGRATION FILE — Slack scheduled-DM notifications.
# Original: Drives the Claude Code Slack MCP tool (slack_schedule_message).
#   This module builds the message spec; the MCP tool actually posts it.
# What to change: swap to another channel (Email digest, Discord, SMS)
#   by re-implementing schedule_dm with your provider's SDK. Keep the
#   DMSpec shape so the scheduler keeps working.
# ============================================================
"""
Slack DM client.

The scheduler uses two DM types:
1. Email send reminder (T+0): fires when it's time to send an email.
   Includes: contact name, subject, LinkedIn URL, "connect request queued
   for T+24h" note.
2. LinkedIn send reminder (T+24h, weekdays only): fires when it's time to
   send the LI connect. Includes: LinkedIn URL (click to navigate), LI 1/2
   (connect note) + LI 2/2 (after-accept message).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class DMSpec:
    channel_id: str  # Slack user_id for DM-to-self, or channel_id for channel
    post_at: int     # unix timestamp
    message: str

    def to_mcp_args(self) -> dict:
        return {"channel_id": self.channel_id, "post_at": self.post_at, "message": self.message}


def email_send_reminder(
    index: int,
    total: int,
    contact_name: str,
    title: str,
    company: str,
    vertical: str,
    email_subject: str,
    linkedin_url: str,
    send_warning: Optional[str] = None,
    notes: Optional[str] = None,
) -> str:
    """Build the Slack message body for an email send reminder (T+0)."""
    header = ":rocket:" if not send_warning else ":warning:"
    lines = [
        f"{header} *Send {index}/{total}* — {contact_name} ({title}, {company}) — {vertical}",
        f"Subject: _{email_subject}_",
    ]
    if send_warning:
        lines.append(f":warning: {send_warning}")
    lines.append("Open Gmail Drafts → review → send.")
    if linkedin_url:
        lines.append(f"LinkedIn: {linkedin_url}")
        lines.append("*Task:* connect request is queued — Slack will remind you ~24h from now with the note copy.")
    if notes:
        lines.append(notes)
    return "\n".join(lines)


def linkedin_send_reminder(
    index: int,
    total: int,
    contact_name: str,
    company: str,
    vertical: str,
    linkedin_url: str,
    li_note_1: str,
    li_note_2: Optional[str] = None,
    arm: Optional[str] = None,
    send_warning: Optional[str] = None,
) -> str:
    """Build the Slack message body for a LinkedIn send reminder (T+24h)."""
    arm_str = f" — *{arm}*" if arm else ""
    warn = ":warning:" if send_warning else ":handshake:"
    lines = [
        f"{warn} *LI {index}/{total}* — {contact_name} ({company}, {vertical}){arm_str}",
        f"Profile: {linkedin_url}" if linkedin_url else "Profile: (missing URL)",
        "",
    ]
    if send_warning:
        lines.append(f":warning: {send_warning}")
        lines.append("")
    lines.append("*LI 1/2 (connect note):*")
    lines.append(f"&gt; {li_note_1}")
    if li_note_2:
        lines.append("")
        lines.append("*LI 2/2 (after accept):*")
        lines.append(f"&gt; {li_note_2}")
    return "\n".join(lines)


def schedule_dm(channel_id: str, post_at: int, message: str) -> DMSpec:
    """Return a DMSpec. Caller materializes it via the slack_schedule_message MCP tool."""
    return DMSpec(channel_id=channel_id, post_at=post_at, message=message)
