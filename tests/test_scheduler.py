"""Basic scheduler tests — verify weekday skipping and gap logic without any API calls."""
from datetime import datetime
from zoneinfo import ZoneInfo

from pipeline.scheduler import _is_weekday, _next_workday_same_time, plan_sends


def test_weekday_skip():
    friday = datetime(2026, 4, 17, 9, 3, tzinfo=ZoneInfo("America/Los_Angeles"))  # Fri
    saturday = datetime(2026, 4, 18, 9, 3, tzinfo=ZoneInfo("America/Los_Angeles"))
    monday = datetime(2026, 4, 20, 9, 3, tzinfo=ZoneInfo("America/Los_Angeles"))

    assert _is_weekday(friday)
    assert not _is_weekday(saturday)
    assert _next_workday_same_time(friday) == monday


def test_plan_sends_spreads_across_days():
    start = datetime(2026, 4, 17, 9, 3, tzinfo=ZoneInfo("America/Los_Angeles"))
    contacts = [{"full_name": f"Contact {i}", "linkedin_url": f"https://linkedin.com/in/c{i}"} for i in range(15)]
    plan = plan_sends(contacts, start_at=start, per_day_cap=10, min_gap_min=11, max_gap_min=18, rng_seed=42)

    assert len(plan.email_sends) == 15
    assert len(plan.li_sends) == 15

    # First 10 should be on Friday
    for contact, t in plan.email_sends[:10]:
        assert t.date() == start.date()

    # Remainder roll to next weekday (Monday, since Sat/Sun skipped)
    for contact, t in plan.email_sends[10:]:
        assert t.weekday() < 5
        assert t.date() > start.date()

    # LI sends are +24h weekdays after email sends
    for (_, email_t), (_, li_t) in zip(plan.email_sends, plan.li_sends):
        assert li_t > email_t
        assert li_t.weekday() < 5


def test_varied_gaps():
    start = datetime(2026, 4, 20, 9, 0, tzinfo=ZoneInfo("America/Los_Angeles"))  # Monday
    contacts = [{"full_name": f"C{i}"} for i in range(5)]
    plan = plan_sends(contacts, start_at=start, min_gap_min=11, max_gap_min=18, rng_seed=123)

    gaps = []
    for i in range(1, len(plan.email_sends)):
        gap_sec = (plan.email_sends[i][1] - plan.email_sends[i-1][1]).total_seconds() / 60
        gaps.append(gap_sec)

    for g in gaps:
        assert 11 <= g <= 18
    # Non-uniform — shouldn't all be the same value
    assert len(set(gaps)) > 1
