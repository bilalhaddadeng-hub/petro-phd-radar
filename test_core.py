import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

from database import init_db, get_all_active_open, save_or_update_opportunity
from scrapers.euraxess_monitor import fetch_euraxess_positions
from scrapers.ifpen_monitor import fetch_ifpen_positions
from scrapers.institutes_gov_monitor import fetch_gov_and_institute_positions
from scrapers.professor_lab_radar import fetch_professor_lab_positions
from notifier import format_opportunity_card

init_db()

all_found = []
all_found.extend(fetch_euraxess_positions())
all_found.extend(fetch_ifpen_positions())
all_found.extend(fetch_gov_and_institute_positions())
all_found.extend(fetch_professor_lab_positions())

for item in all_found:
    status, is_new = save_or_update_opportunity(item)

opps = get_all_active_open()
print(f"Total active opportunities in DB: {len(opps)}")
print("\n--- SAMPLE CARD PREVIEW ---")
if opps:
    print(format_opportunity_card(opps[0], tag="⚡ فرصة جديدة تم فحصها"))
