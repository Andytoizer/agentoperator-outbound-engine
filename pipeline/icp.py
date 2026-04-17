"""
ICP (Ideal Customer Profile) schema + validator.

An ICP is a structured description of who you want to sell to. The
rest of the pipeline reads this ICP to drive target-account search,
people search, and voice positioning.

Load with:
    from pipeline.icp import load_icp
    icp = load_icp("templates/icp.example.yaml")

Validate before running any costly enrichment:
    icp.validate()  # raises ValueError on missing required fields
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None


@dataclass
class PersonaTier:
    """One tier of buyer you're targeting within an account."""
    name: str                    # e.g. "sales_leader", "sdr_manager"
    titles: list[str]            # e.g. ["VP Sales", "SVP Sales", "Head of Sales"]
    seniority: list[str]         # e.g. ["vp", "director", "c_suite"]
    department: Optional[str] = None  # e.g. "sales", "marketing"
    per_account_cap: int = 2     # max contacts to pull per company


@dataclass
class ICP:
    """Full ICP definition."""
    name: str                              # e.g. "EdTech K-12 SaaS"
    verticals: list[str]                   # industry tags, e.g. ["education technology", "e-learning"]
    employee_range: tuple[int, int]        # (min, max) headcount
    regions: list[str] = field(default_factory=list)   # e.g. ["United States"]
    exclusions: list[str] = field(default_factory=list) # industries to exclude
    personas: list[PersonaTier] = field(default_factory=list)
    positioning: dict = field(default_factory=dict)    # free-form: e.g. {"peer_customer": "ClassDojo", "wedge": "..."}

    def validate(self) -> None:
        if not self.name:
            raise ValueError("ICP name is required")
        if not self.verticals:
            raise ValueError("ICP needs at least one vertical")
        if self.employee_range[0] < 0 or self.employee_range[1] < self.employee_range[0]:
            raise ValueError("employee_range must be (min, max) with min <= max")
        if not self.personas:
            raise ValueError("ICP needs at least one persona tier")

    def to_aiark_account_filter(self) -> dict:
        """Convert ICP → AI Ark account filter dict (see clients/aiark.py)."""
        account: dict = {}
        if self.verticals:
            account["industries"] = {
                "any": {
                    "include": {"mode": "SMART", "content": self.verticals}
                }
            }
        account["employeeSize"] = {"range": {"start": self.employee_range[0], "end": self.employee_range[1]}}
        if self.regions:
            account["location"] = {"any": {"include": self.regions}}
        return account


def load_icp(path: str | Path) -> ICP:
    """Load an ICP from YAML or JSON file."""
    if yaml is None:
        raise RuntimeError("pyyaml not installed. pip install pyyaml")
    raw = yaml.safe_load(Path(path).read_text())
    personas = [PersonaTier(**p) for p in raw.pop("personas", [])]
    raw["personas"] = personas
    raw["employee_range"] = tuple(raw.get("employee_range", [1, 10000]))
    icp = ICP(**raw)
    icp.validate()
    return icp
