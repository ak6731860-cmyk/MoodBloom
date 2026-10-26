import os
from dotenv import load_dotenv
from zoneinfo import ZoneInfo

from text_utils import bold

load_dotenv()

BOT_TOKEN = (os.getenv("BOT_TOKEN") or "").strip()
# Keep imports testable without secrets. bot.py validates the token at startup.

TIMEZONE = ZoneInfo("Asia/Kolkata")

DATA_FILE = "data/history.json"

BOT_NAME = "MoodBloom"

VERSION = "4.4 Owner & Privacy Edition"

# Telegram numeric user ID allowed to use owner-only commands.
# Set OWNER_ID in .env; leave empty to disable owner commands.
try:
    OWNER_ID = int((os.getenv("OWNER_ID") or "0").strip() or "0")
except (TypeError, ValueError):
    OWNER_ID = 0



# Welcome / Goodbye defaults
DEFAULT_WELCOME_MESSAGE = (
    f"🌸 {bold('Welcome to MoodBloom!')}\n\n"
    "👋 Hey {name}!\n"
    f"Welcome to {bold('{group}')} 💖\n\n"
    "💭 Share moods\n"
    "📊 Group insights\n"
    "🏆 Leaderboard\n"
    "🎮 Fun games\n\n"
    "🌈 Let's keep this space positive!"
)

DEFAULT_GOODBYE_MESSAGE = (
    f"👋 {bold('Goodbye, {name}!')}\n\n"
    "🌸 Take care and keep blooming.\n"
    "— MoodBloom • {group}"
)

# Scheduler times (hours, minutes) — IST
MORNING_WISH_HOUR = 8
DAILY_GOALS_HOUR = 8
DAILY_REWARDS_HOUR = 8
BIRTHDAY_HOUR = 8
DAILY_MAINTENANCE_HOUR = 0
AUTO_BACKUP_HOUR = 3
