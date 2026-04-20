# Send Sheet — Batch N

Filled in by `/write-email-and-linkedin`. Consumed by `/schedule-sends`.

## Pre-send checklist

- [ ] All emails resolved (no ⚠️ placeholders)
- [ ] 2-min manual LinkedIn scan per contact for <30-day posts
- [ ] Sends spaced over 2-3 days, not a blast
- [ ] A/B arms tagged if running a split test
- [ ] Send sheet parses cleanly via `pipeline.scheduler.parse_send_sheet()`

## Overview

| # | Contact | Title | Company | Vertical | Email | Arm (if A/B) | Subject |
|---|---|---|---|---|---|---|---|
| 1 | First Last | VP Sales | ExampleCo | EdTech | `first.last@example.com` | — | subject line here |
| 2 | ... | ... | ... | ... | `⚠️ placeholder@placeholder.com` | — | ... |

---

## 1. First Last — VP Sales, ExampleCo

`first.last@example.com`

**Subject:** subject line here

Hey First-

Connector opener with peer-customer reference + why it applies here.

Workflow + real stats paragraph.

Happy to share a Loom walking through that workflow if you're interested.

Research hook referencing a dated <12mo signal.

How's your team handling X today?

Andy

**LI 1/2:** Hey First - connect-request-sized note with hook.

**LI 2/2:** Happy to share a Loom walking through their setup.

---

## 2. Next Contact — ...

...

---

## Tracking

Columns: contact, email sent, email opened, email replied, reply sentiment, LI connected, LI 2/2 sent, LI replied, meeting booked.

Splits to watch:
- A/B arm (POC vs Loom) — response rate + positive-response rate
- Competitor-disclosure contacts vs others — tone bet
- Vertical — different wedge references, different ICP framings
