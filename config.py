import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv("DB_PATH", BASE_DIR / "phd_radar.db"))

# الأسرار تُقرأ من متغيرات البيئة / ملف .env فقط (لا تضعها في الكود أبداً)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

# رمز الدعوة السري لتفعيل الوصول (عيّنه في .env). إن تُرك فارغاً يُعطَّل التفعيل بالرمز.
SECRET_ACCESS_TOKEN = os.getenv("SECRET_ACCESS_TOKEN", "").strip()


def _csv(name: str) -> list:
    return [x.strip().lstrip("@").lower() for x in os.getenv(name, "").split(",") if x.strip()]


# مالكو البوت المعتمدون تلقائياً (معرّفات الدردشة وأسماء المستخدمين)
OWNER_CHAT_IDS = [x.strip() for x in os.getenv("OWNER_CHAT_IDS", TELEGRAM_CHAT_ID).split(",") if x.strip()]
AUTHORIZED_USERNAMES = _csv("AUTHORIZED_USERNAMES")
# بوت مفتوح لأي مستخدم افتراضياً؛ ضع OPEN_ACCESS=0 لإعادة القفل (يبقى المالك والمعتمدون فقط)
OPEN_ACCESS = os.getenv("OPEN_ACCESS", "1").strip().lower() not in ("0", "false", "no", "off")


def require_token() -> str:
    if not TELEGRAM_BOT_TOKEN:
        raise SystemExit("TELEGRAM_BOT_TOKEN is not set. Put it in .env (see .env.example).")
    return TELEGRAM_BOT_TOKEN


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

DAILY_REPORT_HOUR = int(os.getenv("DAILY_REPORT_HOUR", "9"))
DAILY_REPORT_MINUTE = int(os.getenv("DAILY_REPORT_MINUTE", "0"))
CLOSING_SOON_DAYS = 7
REMINDER_DAYS = (7, 3, 1)  # تذكير المفضلة والمقدَّم لها قبل الإغلاق
