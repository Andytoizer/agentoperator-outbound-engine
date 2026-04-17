# Batch 1 Send Sheet — 15 Contacts (sanitized)

Final drafts for the first test send. 8 sales leaders (single Loom pitch) + 7 SDR/BDR managers (A/B test: POC vs Loom).

## Pre-send checklist

- [ ] Fix [ConTech Sales Leader 2] email — placeholder still in To: field
- [ ] Source [ConTech SDR Manager 15] email — enrichment returned blank
- [ ] 2-min manual LinkedIn scan per contact for fresh <30-day post hook
- [ ] LinkedIn note 1/2 is the connect request; send 2/2 immediately after accept
- [ ] Space sends over 2-3 days, not one blast

## Overview

### Sales leaders (8 — single Loom pitch)

| # | Contact | Title | Company | Vertical | Email | Subject |
|---|---|---|---|---|---|---|
| 1 | [EdTech Sales Leader 1] | EVP Sales | Seesaw | EdTech | `contact1@seesaw.me` | the classdojo question |
| 2 | [ConTech Sales Leader 2] | VP Sales | Housecall Pro | ConTech | ⚠️ `todo-fix-hcp-email@placeholder.com` | 17 years of contractor-data pain |
| 3 | [EdTech Sales Leader 3] | SVP Sales | ParentSquare | EdTech | `contact3@parentsquare.com` | finding the ~10k non-customer districts |
| 4 | [EdTech Sales Leader 4] | Sr Dir Sales | Newsela | EdTech | `contact4@newsela.com` | how classdojo sources district contacts |
| 5 | [EdTech Sales Leader 5] | VP Sales | Raptor Technologies | EdTech | `contact5@raptortech.com` | district sourcing for raptor |
| 6 | [ConTech Sales Leader 6] | VP Sales | BuildOps | ConTech | `contact6@buildops.com` | contractor sourcing for buildops |
| 7 | [ConTech Sales Leader 7] | SVP Sales | CompanyCam | ConTech | `contact7@companycam.com` | contractor prospecting for companycam |
| 8 | [ConTech Sales Leader 8] | VP Sales | Jobber | ConTech | `contact8@getjobber.com` | contractor sourcing for jobber |

### SDR/BDR managers (7 — A/B split)

| # | Contact | Title | Company | Vertical | Email | Arm | Subject |
|---|---|---|---|---|---|---|---|
| 9 | [EdTech SDR Manager 9] | Sr Inside Sales Mgr | Panorama Education | EdTech | `contact9@panoramaed.com` | **POC** | day-1 lists for the panorama sdr team |
| 10 | [EdTech SDR Manager 10] | Mgr, Sales Dev | Newsela | EdTech | `contact10@newsela.com` | **POC** | day-1 lists for the newsela sdr team |
| 11 | [ConTech SDR Manager 11] | Mgr, Sales Dev | Jobber | ConTech | `contact11@getjobber.com` | **POC** | day-1 smb trades lists |
| 12 | [EdTech SDR Manager 12] | Inside Sales Mgr | ParentSquare | EdTech | `contact12@parentsquare.com` | **POC** (blind A/B) | blind a/b for your inside sales team |
| 13 | [ConTech SDR Manager 13] | SDR Manager | BuildOps | ConTech | `contact13@buildops.com` | **Loom** | ramping a raleigh sdr team from zero |
| 14 | [EdTech SDR Manager 14] | SD & Inside Sales Mgr | Seesaw | EdTech | `contact14@seesaw.me` | **Loom** | classdojo + your sdr team |
| 15 | [ConTech SDR Manager 15] | Sales Dev Mgr | Fieldwire | ConTech | ⚠️ `todo-source-email@placeholder.com` | **Loom** | day-1 lists for commercial construction sdrs |

---

# SALES LEADERS (8)

---

## 1. [EdTech Sales Leader 1] — EVP Sales, Seesaw

`contact1@seesaw.me`

**Subject:** the classdojo question

Hey [First1]-

To get right to the point - ClassDojo is a Freckle customer, and we've built a lot of the district-persona sourcing engine behind their outbound motion. Seesaw runs a "vs ClassDojo" page and bids on the term, so it felt weird not to just reach out directly.

Freckle scrapes district websites, staff pages, board minutes, etc. to find the family engagement / curriculum / SEL personas that don't show up cleanly in Apollo/ZoomInfo. ClassDojo's workflow pulls district lists from Salesforce, enriches them with ~2k comms + ~1.9k curriculum + ~1.8k SEL contacts, and pushes it all back into SFDC. Also pulls in competitor platform detection as a buying signal - so they know when a district mentions Seesaw in public materials.

Obviously I'd love to tell you the opposite story for your SDR team building net-new pipeline. Want me to share a quick Loom showing how the ClassDojo setup works?

Andy

**LI 1/2:** Hey [First1] - quick heads-up since Seesaw and ClassDojo are clearly competitors: we work with ClassDojo on their district persona enrichment, so figured I'd reach out directly rather than go around it. Curious how your SDR team is sourcing district contacts.

---

## 6. [ConTech Sales Leader 6] — VP Sales, BuildOps

`contact6@buildops.com`

**Subject:** contractor sourcing for buildops

Hey [First6]-

Running outbound for BuildOps at this stage probably means chasing a lot of regional commercial subs that barely exist in Apollo/ZoomInfo. We work with BuildPass solving exactly that - pulling HVAC/mechanical/electrical contractor lists out of Google Maps at scale - and since the ICPs overlap cleanly, figured worth reaching out.

They use Freckle to pull contractor lists from Google Maps - "general contractors in louisiana", "commercial builder tampa" - classify each as residential vs commercial vs sub, and enrich with owner + PM + superintendent + safety lead contacts. One recent workflow: 875 companies → 566 decision makers + 505 LinkedIn profiles + 505 emails + 404 phone numbers, all synced to HubSpot.

Happy to share a Loom walking through that workflow if you're interested.

Noticed BuildOps has a lot of open sales roles right now too - feels like a decent time to float this.

How's your team handling commercial subcontractor sourcing today?

Andy

**LI 1/2:** Hey [First6] - I helped set up a Google Places → HubSpot contractor enrichment workflow for BuildPass (875 companies → 566 decision makers + 505 emails + HubSpot sync). Same engine should map cleanly to BuildOps' commercial sub ICP. Worth connecting?

**LI 2/2:** Happy to share a Loom walking through their setup.

---

_[Drafts 2-5, 7-8 and 9-15 omitted in the sanitized example — the two above show the connector-opener pattern + LI structure in full. See the full batch sheet logic in `drafts/_SEND_SHEET_batch1.md` of the source campaign.]_

---

# Tracking

Columns: contact, email sent, email opened, email replied, reply sentiment, LI connected, LI 2/2 sent, LI replied, meeting booked.

Splits to watch:
- **A/B arm** (POC vs Loom) — response rate + positive-response rate across the 7 SDR drafts
- **Competitor disclosure** (3 contacts — drafts 1, 12, 14) vs others — same-space honesty is a big tone bet
- **Vertical** (EdTech vs ConTech) — different peer-customer references, different ICP framings
