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

Why HTML by default:
    Plain-text bodies get auto-wrapped by Gmail at ~76 chars, which makes
    the email look pre-formatted / automated (hard line breaks at column
    boundaries that visibly interrupt paragraphs). Wrapping each paragraph
    in <p> tags lets Gmail reflow naturally in the reader's window.
    The plain-text `body` is kept as the fallback alternative.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class DraftSpec:
    to: list[str]
    subject: str
    body: str                           # plain-text alternative
    html_body: Optional[str] = None     # rich-text version (preferred by Gmail if present)
    cc: Optional[list[str]] = None
    bcc: Optional[list[str]] = None

    def to_mcp_args(self) -> dict:
        """Shape suitable for the Claude Code Gmail MCP tool create_draft."""
        args = {"to": self.to, "subject": self.subject, "body": self.body}
        if self.html_body:
            args["htmlBody"] = self.html_body
        if self.cc:
            args["cc"] = self.cc
        if self.bcc:
            args["bcc"] = self.bcc
        return args


def _plain_to_html(body: str) -> str:
    """Convert a plain-text body into simple <p>-wrapped HTML.

    Splits on blank lines, wraps each block in <p>. Preserves intra-paragraph
    newlines as <br> only if the paragraph already contains them. Safe for
    typical outbound copy — do NOT rely on it for complex HTML.
    """
    paragraphs = [p.strip() for p in body.split("\n\n") if p.strip()]

    def wrap(p: str) -> str:
        if "\n" in p:
            return "<p>" + "<br>".join(line.strip() for line in p.split("\n")) + "</p>"
        return f"<p>{p}</p>"

    return "".join(wrap(p) for p in paragraphs)


def create_draft(
    to: str | list[str],
    subject: str,
    body: str,
    html_body: Optional[str] = None,
    cc: Optional[list[str]] = None,
    bcc: Optional[list[str]] = None,
) -> DraftSpec:
    """Return a DraftSpec. Caller (Claude Code) materializes it via the MCP tool.

    If `html_body` is not provided, one is auto-generated from `body` by
    wrapping paragraphs in <p> tags. This avoids Gmail's plain-text
    auto-wrap (which makes emails look automated). Pass `html_body=""` if
    you explicitly want plain-text only (not recommended for outbound).
    """
    to_list = [to] if isinstance(to, str) else list(to)
    if html_body is None:
        html_body = _plain_to_html(body)
    elif html_body == "":
        html_body = None  # caller opted out of HTML
    return DraftSpec(to=to_list, subject=subject, body=body, html_body=html_body, cc=cc, bcc=bcc)
