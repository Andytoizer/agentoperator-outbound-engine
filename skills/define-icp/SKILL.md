---
name: define-icp
description: Define an Ideal Customer Profile (ICP) for an outbound campaign. Produces a validated icp.yaml file with verticals, employee range, regions, persona tiers, and positioning. Use when starting a new campaign or when current ICP is vague.
---

# /define-icp — turn a hypothesis into a structured ICP

## When to use

- Phase 1 of `/plan-campaign`.
- User has a loose "we want to sell to X" idea and needs to make it concrete before any account list work.
- Existing ICP is stale or untested.

## Prerequisites

- `templates/icp.example.yaml` exists in the repo.
- User can answer: who they sell to, which verticals, headcount range, which regions, what peer customer wins they can reference.

## Steps

1. **Read `templates/icp.example.yaml`** to understand the schema.

2. **Interview** — ask these in order, one at a time:
   - **Verticals**: "What industry keywords describe your best customers? (e.g. 'education technology', 'construction SaaS')"
   - **Employee range**: "Headcount range of target companies? (min, max)"
   - **Regions**: "Any geo constraints? (e.g. 'United States', 'EMEA', or leave empty for global)"
   - **Personas (tier by tier)**: "For each persona tier — sales leader, SDR manager, marketing — give me 3-5 title variations and the department."
   - **Peer customer positioning**: "Name 1-2 customers you've already won that are in the same space as this ICP. We'll use them as the connector hook."
   - **Wedge**: "One-sentence reason you'd win vs the incumbent."

3. **Draft the ICP** and read it back for confirmation. Use the `pipeline.icp.ICP` dataclass schema:
   ```yaml
   name: <ICP name>
   verticals: [...]
   employee_range: [min, max]
   regions: [...]
   exclusions: [...]
   personas:
     - name: sales_leader
       titles: ["VP Sales", "SVP Sales", "Head of Sales"]
       seniority: ["vp", "director", "c_suite"]
       department: sales
       per_account_cap: 1
     - name: sdr_manager
       titles: ["SDR Manager", "Sales Development Manager"]
       seniority: ["manager", "director"]
       department: sales
       per_account_cap: 1
   positioning:
     peer_customers: ["ClassDojo"]
     wedge: "Freckle finds district personas Apollo/ZoomInfo miss."
   ```

4. **Validate** — run `python -c "from pipeline.icp import load_icp; load_icp('templates/icp.yaml').validate()"`. If it raises, fix the file.

5. **Write handoff** — update `handoffs/PHASE_1.md`:
   - ICP name, verticals, employee range, persona tiers
   - Total addressable target count (rough estimate from user)
   - Peer customer list for the connector opener
   - Link to `templates/icp.yaml`

## Gate

- `templates/icp.yaml` exists and `load_icp()` passes validation.
- At least 1 peer customer named for the connector hook (the /write skill needs this).
- At least 1 persona tier defined.

## Common failure modes

- **Too broad** — "B2B SaaS companies" isn't specific enough. Push for vertical + size + region.
- **No peer customer** — without one, the connector opener falls apart. If they truly have none, pivot the wedge to data-gap instead of social-proof.
- **Forgetting exclusions** — ask explicitly: "Any sub-industries to exclude?" (e.g. EdTech ICP excludes Higher Ed if the play is K-12).
