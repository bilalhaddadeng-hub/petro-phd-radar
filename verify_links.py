import requests
import sqlite3
from pathlib import Path

BASE_DIR = Path("C:/Users/admin/.gemini/antigravity/scratch/petro_phd_radar_bot")
DB_PATH = BASE_DIR / "phd_radar.db"

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
c = conn.cursor()
c.execute("SELECT id, title, link FROM opportunities")
rows = c.fetchall()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

print(f"Checking {len(rows)} links in database...")
for r in rows:
    link = r["link"]
    try:
        resp = requests.head(link, headers=headers, timeout=5, allow_redirects=True)
        if resp.status_code >= 400:
            # Retry with GET in case HEAD is blocked
            resp = requests.get(link, headers=headers, timeout=5)
        print(f"[{resp.status_code}] {link}")
    except Exception as e:
        print(f"[ERR] {link} -> {e}")

conn.close()
