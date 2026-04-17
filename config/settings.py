"""
Environment configuration loader.

All API keys and provider-specific constants live here. Values are loaded
from the .env file at the repo root. Copy .env.example to .env and fill in
your values.
"""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*_args, **_kwargs):
        pass

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_PROJECT_ROOT / ".env", override=True)

# ── AI Ark (people + company search) ──────────────────────────
AI_ARK_API_KEY = os.getenv("AI_ARK_API_KEY", "")
AI_ARK_API_BASE = "https://api.ai-ark.com/api/developer-portal/v1"
AI_ARK_RATE_LIMIT_PER_SEC = 5

# ── Lead Magic (email enrichment — rung 1) ────────────────────
LEADMAGIC_API_KEY = os.getenv("LEADMAGIC_API_KEY", "")
LEADMAGIC_API_BASE = "https://api.leadmagic.io"

# ── Findymail (email enrichment — fallback) ───────────────────
FINDYMAIL_API_KEY = os.getenv("FINDYMAIL_API_KEY", "")
FINDYMAIL_API_BASE = "https://app.findymail.com/api"

# ── Apollo (optional — typically driven via Claude MCP) ───────
APOLLO_API_KEY = os.getenv("APOLLO_API_KEY", "")
APOLLO_API_BASE = "https://api.apollo.io/v1"

# ── Slack (DM notifications) ──────────────────────────────────
SLACK_USER_ID = os.getenv("SLACK_USER_ID", "")  # your own user ID for DMs-to-self
SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID", "")  # optional channel for campaign logs

# ── Gmail (draft creation — typically via Claude MCP) ─────────
GMAIL_SENDER = os.getenv("GMAIL_SENDER", "")

# ── Anthropic (for parallel research sub-agents if running standalone) ─
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# ── Send scheduler defaults ───────────────────────────────────
SEND_TIMEZONE = os.getenv("SEND_TIMEZONE", "America/Los_Angeles")
SEND_WINDOW_START_HOUR = int(os.getenv("SEND_WINDOW_START_HOUR", "9"))
SEND_WINDOW_END_HOUR = int(os.getenv("SEND_WINDOW_END_HOUR", "12"))
SEND_PER_DAY_CAP = int(os.getenv("SEND_PER_DAY_CAP", "10"))
SEND_MIN_GAP_MIN = int(os.getenv("SEND_MIN_GAP_MIN", "11"))
SEND_MAX_GAP_MIN = int(os.getenv("SEND_MAX_GAP_MIN", "18"))
LI_DELAY_HOURS = int(os.getenv("LI_DELAY_HOURS", "24"))
