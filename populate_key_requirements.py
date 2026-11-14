# -*- coding: utf-8 -*-
"""
populate_key_requirements.py
Fills the key_requirements column for all existing opportunities in phd_radar.db
using the evaluator logic.
"""

import sqlite3
import os
from evaluator import determine_key_requirements

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "phd_radar.db")

def main():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Ensure column exists
    c.execute("PRAGMA table_info(opportunities)")
    cols = [r[1] for r in c.fetchall()]
    if "key_requirements" not in cols:
        c.execute("ALTER TABLE opportunities ADD COLUMN key_requirements TEXT")
        conn.commit()

    c.execute("SELECT id, country, institution, source_type, title, sub_specialty FROM opportunities")
    rows = c.fetchall()
    print(f"Updating key requirements for {len(rows)} opportunities...")

    for r in rows:
        opp_id, country, inst, source_type, title, sub = r
        reqs = determine_key_requirements(country or "", inst or "", source_type or "", title or "", sub or "")
        c.execute("UPDATE opportunities SET key_requirements = ? WHERE id = ?", (reqs, opp_id))

    conn.commit()
    print("All opportunities updated with key_requirements successfully.")

    # Show a sample
    sample = c.execute("SELECT title, institution, key_requirements FROM opportunities WHERE institution LIKE '%Leoben%' OR institution LIKE '%Politecnico%' LIMIT 2").fetchall()
    for s in sample:
        print(f"\n--- {s[0]} ({s[1]}) ---\n{s[2]}")

    conn.close()

if __name__ == "__main__":
    main()
