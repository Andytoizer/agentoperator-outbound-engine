# ============================================================
# INTEGRATION FILE — Gmail draft creation.
# Original: Drives the Claude Code Gmail MCP tool (create_draft). This
#   module is a thin wrapper + a REST fallback for non-Claude use.
# What to change: if you use Outlook / SES / another provider, replace
#   the _create_draft_via_rest function. The public API (create_draft)
#   stays identical.
# ============================================================
"""
Gmail draft client.

Two modes:
1. MCP mode (default when running inside Claude Code) — the scheduler
   emits a draft spec and Claude's Gmail tool creates it. This module's
   create_draft() returns the spec so the caller can hand it to Claude.
2. REST mode — uses the Gmail API directly via google-auth-oauthlib. Not
   wired up by default; enable if you want a standalone runner.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class DraftSpec:
    to: list[str]
    subject: str
    body: str
    cc: Optional[list[str]] = None
    bcc: Optional[list[str]] = None

    def to_mcp_args(self) -> dict:
        """Shape suitable for the Claude Code Gmail MCP tool create_draft."""
        args = {"to": self.to, "subject": self.subject, "body": self.body}
        if self.cc:
            args["cc"] = self.cc
        if self.bcc:
            args["bcc"] = self.bcc
        return args


def create_draft(
    to: str | list[str],
    subject: str,
    body: str,
    cc: Optional[list[str]] = None,
    bcc: Optional[list[str]] = None,
) -> DraftSpec:
    """Return a DraftSpec. Caller (Claude Code) materializes it via the MCP tool."""
    to_list = [to] if isinstance(to, str) else list(to)
    return DraftSpec(to=to_list, subject=subject, body=body, cc=cc, bcc=bcc)
