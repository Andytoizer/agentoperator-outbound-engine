---
name: schedule-sends
description: Parse a send sheet, create Gmail drafts, and schedule Slack DM reminders at T+0 (email send, with LinkedIn URL + connect task) and T+24h weekdays (LinkedIn send, with URL + LI 1/2 + LI 2/2 copy inline). Built-in deliverability spacing. Phase 6 of a campaign.
---

# /schedule-sends — send sheet → Gmail drafts + Slack DMs

## When to use

- Phase 6 of `/plan-campaign`, after `/write-email-and-linkedin` wrote an approved `drafts/SEND_SHEET.md`.
- Re-scheduling a paused campaign (e.g. skipped a day, need to re-slot remaining contacts).

## Prerequisites

- `drafts/SEND_SHEET.md` with approved drafts.
- Claude Code with Gmail MCP tool (`create_draft`) and Slack MCP tool (`slack_schedule_message`).
- Known Slack user ID for DM-to-self (the MCP tool description exposes it).

## Steps

1. **Parse the send sheet**:
   ```python
   from pathlib import Path
   from pipeline.scheduler import parse_send_sheet
   entries = parse_send_sheet(Path("drafts/SEND_SHEET.md").read_text())
   print(f"Parsed {len(entries)} contacts")
   ```
   If the count looks wrong, the send sheet's formatting drifted. The parser expects:
   - `## N. First Last — Title, Company` H2 per contact
   - `` `email@domain.com` `` on its own line
   - `**Subject:** ...`
   - `**LI 1/2:** ...` and `**LI 2/2:** ...`

2. **Cross-check entries against the shortlist** — ensure each entry's LinkedIn URL from `people/shortlist.json` is available (the Slack DMs need it). If missing, stop and source.

3. **Plan the sends** — compute the timing grid:
   ```python
   from datetime import datetime
   from zoneinfo import ZoneInfo
   from pipeline.scheduler import plan_sends

   start = datetime.now(ZoneInfo("America/Los_Angeles")).replace(hour=9, minute=3, second=0, microsecond=0)
   if start < datetime.now(ZoneInfo("America/Los_Angeles")):
       # push to tomorrow 9am if we're past today's 9am
       from datetime import timedelta
       start = start + timedelta(days=1)
   # skip weekends
   while start.weekday() >= 5:
       start = start + timedelta(days=1)

   # Convert entries → minimal contact dicts with linkedin_url populated from shortlist
   contacts = [{...}, ...]  # join entries with shortlist by full_name or email
   plan = plan_sends(contacts, start_at=start, per_day_cap=10, min_gap_min=11, max_gap_min=18)
   ```

4. **Build the specs**:
   ```python
   from pipeline.scheduler import build_gmail_drafts, build_slack_email_reminders, build_slack_linkedin_reminders

   drafts = build_gmail_drafts(entries)
   email_dms = build_slack_email_reminders(plan, entries, channel_id="U09XXXXXXXX")
   li_dms = build_slack_linkedin_reminders(plan, entries, channel_id="U09XXXXXXXX")
   ```

5. **Materialize via MCP tools — CRITICAL INVARIANT: every Slack reminder must have a matching Gmail draft.** Hand the specs to Claude Code:
   - For each `DraftSpec`: call `create_draft` (Gmail MCP) with `spec.to_mcp_args()`. The dict contains both `body` (plain-text) and `htmlBody` (`<p>`-wrapped), so Gmail renders naturally without the plain-text column-wrap that makes emails look automated.
   - For each `DMSpec`: call `slack_schedule_message` with `spec.to_mcp_args()`.
   - **Fire drafts FIRST, then DMs.** If draft creation fails and the Slack reminder fires, the user sees "send this email" with no draft to send — the exact bug that made us add this invariant. Never schedule a DM without confirming its draft exists.
   - Batch in parallel (5-10 tool calls per message) for speed. Expect occasional rate-limit errors — retry individually.

6. **Write the schedule reference file** — `SEND_SCHEDULE.md` at repo root:
   - Table of all sends with times, contacts, subjects, warnings
   - LI followup schedule
   - Monday pager-map if the schedule spans a day where both email reminders + LI followups fire

7. **Handoff** — update `handoffs/PHASE_6.md`:
   - Drafts created count
   - DMs scheduled count (email + LI)
   - Any rate-limit retries
   - Link to `SEND_SCHEDULE.md`

## Gate

- All `drafts/SEND_SHEET.md` entries have a corresponding Gmail draft AND 2 Slack DMs (T+0 + T+24h).
- Placeholder emails (`⚠️` flag) carry the warning into the Slack DM so you don't fire a LI followup on a contact whose email never went out.

## Deliverability built-ins

| Rule | Why |
|---|---|
| Varied 11-18 min gaps | Non-uniform timing avoids burst-send patterns on receive side |
| 9am-12pm send window | Cold email hit rates peak mornings Tue-Thu |
| Max 10/day | Well under Gmail reputation thresholds for manual-send accounts |
| 24h email → LI delay | Lets email engagement signal the LI accept; same-time is noisy |
| Weekdays only for LI delay | Mon connects get better accept rates than Sat/Sun |
| Human-click-to-send | Carries normal session signals vs bulk API send |

## Slack DM format

**Email send reminder (T+0):**
```
🚀 Send 1/15 — First Last (Title, Company) — Vertical
Subject: *the subject line*
Open Gmail Drafts → review → send.
LinkedIn: https://linkedin.com/in/...
Task: connect request is queued — Slack will remind you ~24h from now with the note copy.
```

**LinkedIn send reminder (T+24h, weekday):**
```
🤝 LI 1/15 — First Last (Company, Vertical) — POC arm
Profile: https://linkedin.com/in/...

LI 1/2 (connect note):
> [text]

LI 2/2 (after accept):
> [text]
```

## Common failure modes

- **Parse misses** — non-conforming H2 format silently drops contacts. Count entries before fanning out.
- **Rate limits** — Slack `slack_schedule_message` rate-limits ~4-5/15 when fired in parallel. Retry individually.
- **Weekend timestamp** — LI delay can land on Saturday if you forget to check weekends in `_next_workday_same_time`. The built-in helper handles this but audit timestamps.
- **Skipping the test gate** — ALWAYS test with a 2-3 contact send before firing the full 15. Once Slack DMs are scheduled, editing them requires the Slack UI.
- **Reminder without draft (DON'T SHIP)** — if draft creation silently fails but the DM schedule succeeds, the user gets a "send this now" ping with nothing to send. Enforce: Gmail draft creation succeeds FIRST, only then schedule the matching Slack DM. `pipeline.scheduler.build_gmail_drafts()` returns specs; the caller must confirm each draft materialized before calling `build_slack_email_reminders()`.
- **Plain-text column wrap** — Gmail auto-wraps plain-text `body` at ~76 chars, which makes emails look pre-formatted. The `clients.gmail.create_draft()` helper auto-generates an `htmlBody` from the plain body (one `<p>` per paragraph) so the reader's client reflows naturally. Don't pass `html_body=""` unless you explicitly want plain text.
