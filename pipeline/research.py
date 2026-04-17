"""
Company + contact research orchestrator.

Research is the most Claude-native step in the pipeline. Rather than
hard-coding web-search logic, this module produces research *specs* that
Claude executes via parallel sub-agents (WebFetch / WebSearch / parallel
Haiku sub-agents).

The scheduler-adjacent code lives in pipeline/; the actual research is
done by Claude driving the research skill at skills/research-company-and-contact/.

Output format (per company, markdown written to research/<slug>.md):
    # <Company Name>
    ## What they do
    ## Recent signals (<12 months, dated)
    ## GTM motion (sales/marketing/product)
    ## Connector hook (tie to your customer/wedge)
    ## Contact research
      ### <Contact Name> — <Title>
      - role at company
      - recent LinkedIn activity (if any, <30 days)
      - prior roles (ONLY if relevant to wedge)
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ResearchSpec:
    company_name: str
    company_domain: str
    contacts: list[dict] = field(default_factory=list)
    signals_to_find: list[str] = field(default_factory=list)
    connector_hypothesis: str = ""  # e.g. "ClassDojo is our customer; they compete/are adjacent, so the connector is..."

    def research_prompt(self) -> str:
        """Build the prompt Claude passes to a research sub-agent."""
        contact_lines = "\n".join(
            f"  - {c.get('full_name', '')} ({c.get('title', '')}) — {c.get('linkedin_url', 'no LinkedIn URL')}"
            for c in self.contacts
        )
        signals = "\n".join(f"  - {s}" for s in self.signals_to_find) or "  - product / pricing changes\n  - recent fundraising / M&A\n  - hiring signals (sales-adjacent roles)\n  - competitor platform mentions"
        return f"""Research {self.company_name} ({self.company_domain}) for an outbound email.

Goal: find 2-3 concrete, recent (<12 months), DATED signals that could anchor a
connector opener. Never make up stats or dates. Skip signals older than 12 months.

Contacts to research:
{contact_lines or "  (none specified)"}

Signal categories to scan:
{signals}

Connector hypothesis: {self.connector_hypothesis or "(none specified)"}

Output as markdown with these sections:
- What they do (2 sentences, vendor-neutral)
- Recent signals (bullet list, each DATED and sourced)
- GTM motion (how they sell — inbound vs outbound, team structure if visible)
- Connector hook (how to tie the connector hypothesis to something recent)
- Per-contact research (under each contact name: role at company + any <30-day LinkedIn post if visible)

Rules:
- Current-company state signals ONLY. No "7 years at X" prior-job references.
- Dates must be absolute ("March 2026" not "recently").
- If LinkedIn is gated, say so — don't invent activity.
"""

    def output_path(self, base: str | Path) -> Path:
        slug = self.company_name.lower().replace(" ", "-").replace("/", "-")
        return Path(base) / f"{slug}.md"


def build_specs_from_shortlist(shortlist: list[dict], connector_hypothesis: str = "") -> list[ResearchSpec]:
    """Group contacts by company → one ResearchSpec per company."""
    by_company: dict[str, list[dict]] = {}
    company_names: dict[str, str] = {}
    for c in shortlist:
        domain = c.get("company_domain", "")
        by_company.setdefault(domain, []).append(c)
        company_names.setdefault(domain, c.get("company_name", domain))
    return [
        ResearchSpec(
            company_name=company_names[domain],
            company_domain=domain,
            contacts=by_company[domain],
            connector_hypothesis=connector_hypothesis,
        )
        for domain in by_company
    ]


def save_spec(spec: ResearchSpec, base: str | Path) -> Path:
    """Write the prompt for a research spec to disk (one .md per company)."""
    p = spec.output_path(base)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(spec.research_prompt())
    return p
