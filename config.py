import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "phd_radar.db"

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "9193205865:AAFt1vEe9R5I66tveXYMc-vD-IFYjilqJ20")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

KEYWORDS = [
    "petroleum engineering",
    "reservoir engineering",
    "drilling engineering",
    "enhanced oil recovery",
    "eor",
    "ccus",
    "co2 storage",
    "geological carbon storage",
    "subsurface energy",
    "hydrogen underground storage",
    "geothermal energy",
    "geomechanics",
    "multiphase flow in porous media",
    "petrophysics",
    "fluid-rock interaction"
]

DAILY_REPORT_HOUR = 9
DAILY_REPORT_MINUTE = 0
CLOSING_SOON_DAYS = 7
