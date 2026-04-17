"""
Email + LinkedIn draft generator.

Like research.py, writing is mostly Claude-driven. This module produces
*spec* objects (voice doc + template + research) that the write skill
hands to Claude for drafting. The actual copy is iterated in-conversation.

The output of the write step is a send sheet (markdown) that the scheduler
can consume. See templates/SEND_SHEET_example.md for the shape.

Why not generate drafts programmatically? Voice quality at cold-email
scale is the whole game. A template-filling function produces generic
copy. Claude + a voice doc + recent research produces copy that lands.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class DraftSpec:
    """Everything Claude needs to draft one email + LI pair for one contact."""
    contact: dict                  # from shortlist
    research_md: str               # contents of research/<slug>.md for the company
    voice_doc: str                 # contents of config/voice/andys_voice.md (or yours)
    structural_patterns: str       # contents of config/voice/email_patterns.md
    offer: str                     # e.g. "Loom walkthrough", "free POC", "blind A/B"
    ab_arm: Optional[str] = None   # "POC" / "Loom" if this contact is in an A/B test

    def draft_prompt(self) -> str:
        contact = self.contact
        name = contact.get("first_name") or contact.get("full_name", "")
        return f"""Draft a cold outbound email + LinkedIn 1/2 + LinkedIn 2/2 for this contact.

Contact:
- {contact.get('full_name')} — {contact.get('title')} at {contact.get('company_name')}
- Email: {contact.get('email', '(missing)')}
- LinkedIn: {contact.get('linkedin_url', '(missing)')}
- Persona tier: {contact.get('persona_tier')}

Offer: {self.offer}
{f'A/B arm: {self.ab_arm}' if self.ab_arm else ''}

Voice doc (use this tone — exact):
---
{self.voice_doc}
---

Structural patterns (follow these — they're locked from iteration):
---
{self.structural_patterns}
---

Company research (use 1-2 concrete, dated signals in the connector — never make up stats):
---
{self.research_md}
---

Output format (markdown):

**Subject:** <lowercase subject line, no colons, no listy stacks>

<email body, 3-4 short paragraphs, opens "Hey {name}-", ends "Andy">

**LI 1/2:** <~200 char connect-request note with a specific hook>

**LI 2/2:** <1 sentence sent immediately after accept; matches the email offer>

Hard rules:
- Hyphens, not em dashes.
- No sentence starts with a colon.
- Contractions always.
- No prior-job references.
- News signals must be <12 months and dated.
- Short paragraphs (1-3 sentences).
- Signoff: just "Andy".
"""


def build_specs_from_shortlist(
    shortlist: list[dict],
    research_dir: str | Path,
    voice_path: str | Path,
    patterns_path: str | Path,
    default_offer: str = "Loom walkthrough",
    ab_assign_fn=None,
) -> list[DraftSpec]:
    """Build one DraftSpec per contact. ab_assign_fn(contact) -> Optional[str] for A/B arms."""
    voice = Path(voice_path).read_text()
    patterns = Path(patterns_path).read_text()
    research_dir = Path(research_dir)
    specs = []
    for c in shortlist:
        slug = c.get("company_name", "").lower().replace(" ", "-").replace("/", "-")
        research_file = research_dir / f"{slug}.md"
        research_md = research_file.read_text() if research_file.exists() else "(no research available — do live research before drafting)"
        arm = ab_assign_fn(c) if ab_assign_fn else None
        specs.append(DraftSpec(
            contact=c,
            research_md=research_md,
            voice_doc=voice,
            structural_patterns=patterns,
            offer=default_offer,
            ab_arm=arm,
        ))
    return specs
