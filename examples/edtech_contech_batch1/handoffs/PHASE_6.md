# Handoff — Phase 6: Schedule + Send

## Status

- [x] Complete

## Inputs read

- `drafts/SEND_SHEET.md` — 15 contacts parsed
- `people/shortlist.json` — for LinkedIn URLs used in Slack DMs

## Outputs written

- `SEND_SCHEDULE.md` (at repo root) — full timing table, Monday pager-map
- 15 Gmail drafts (via create_draft MCP tool)
- 15 Slack DMs at T+0 (email send reminders — LinkedIn URL attached, connect task queued note)
- 15 Slack DMs at T+24h workdays (LinkedIn send reminders — URL + LI 1/2 + LI 2/2 copy inline)

## Gates passed

- [x] Every entry in SEND_SHEET.md has a Gmail draft
- [x] Every entry has 2 Slack DMs scheduled (email + LI)
- [x] Placeholder emails (drafts 2 + 15) carry TODO warnings into Slack DMs
- [x] Varied 11-18 min gaps verified (non-uniform)
- [x] 24h LI delay skips weekends

## Notable decisions

- 10 sends on Friday 9-12 PDT, 5 sends overflow to Monday (per per_day_cap=10)
- LI followups for Friday sends land on Monday; LI followups for Monday sends land on Tuesday
- Monday ends up with 15 Slack pings interleaved (5 email reminders + 10 LI followups for Friday's sends). Pager-map added to SEND_SCHEDULE.md so it's visible.
- 2 rate-limit retries needed during Slack DM fan-out (retried individually, succeeded)

## Blockers or open questions

- [ConTech Sales Leader 2] — HCP email still stale as of schedule creation. Reminder DM carries warning; if not resolved by 9:20 Fri, skip and reschedule.
- [ConTech SDR Manager 15] — Fieldwire email still missing. Same handling.

## Next step

Watch for Slack DM at 9:03 Fri. Batch 1 send window runs until 11:39 Fri + continues Mon 9:04. LI followup DMs begin Mon 9:03.
