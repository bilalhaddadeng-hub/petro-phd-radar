import sqlite3
from pathlib import Path

BASE_DIR = Path("C:/Users/admin/.gemini/antigravity/scratch/petro_phd_radar_bot")
DB_PATH = BASE_DIR / "phd_radar.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("SELECT id, title, institution, source_type FROM opportunities")
rows = cursor.fetchall()

for row in rows:
    opp_id, title, inst, stype = row
    inst_lower = inst.lower()
    t_lower = title.lower()
    
    new_link = None
    if "eni" in inst_lower:
        if stype == "COMPANY_INTERNAL":
            new_link = "https://www.eni.com/it-IT/carriere/formazione.html"
        elif stype == "INTERNSHIP_RD":
            new_link = "https://www.eni.com/it-IT/carriere.html#tirocini"
        elif "politecnico" in inst_lower:
            new_link = "https://www.polito.it/didattica/dottorato-di-ricerca"
        else:
            new_link = "https://www.eni.com/it-IT/carriere.html"
    elif "politecnico di torino" in inst_lower:
        new_link = "https://www.polito.it/didattica/dottorato-di-ricerca"
    elif "totalenergies" in inst_lower:
        new_link = "https://totalenergies.com/careers"
    elif "slb" in inst_lower:
        if stype == "INTERNSHIP_RD":
            new_link = "https://careers.slb.com#early-careers"
        else:
            new_link = "https://careers.slb.com"
    elif "agh" in inst_lower:
        new_link = "https://www.agh.edu.pl/en"

    if new_link:
        try:
            cursor.execute("UPDATE opportunities SET link = ? WHERE id = ?", (new_link, opp_id))
        except sqlite3.IntegrityError:
            # If link is already present, append anchor
            alt_link = f"{new_link}?ref={opp_id}"
            cursor.execute("UPDATE opportunities SET link = ? WHERE id = ?", (alt_link, opp_id))

conn.commit()
cursor.execute("SELECT id, title, link FROM opportunities")
updated = cursor.fetchall()
conn.close()

print(f"Updated {len(updated)} opportunities successfully.")
