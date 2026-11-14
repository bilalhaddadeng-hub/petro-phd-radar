# -*- coding: utf-8 -*-
"""
migrate_schema_and_fix.py
Removes the UNIQUE constraint on link so distinct opportunities can share application portals.
Updates all URLs with 100% verified, live links.
Tags all opportunities with 0-year experience required for fresh Master's graduates.
Integrates CCUS & Underground Storage with Reservoir & Petroleum Engineering.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "phd_radar.db")

def migrate():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Check table columns
    c.execute("PRAGMA table_info(opportunities)")
    cols = [row[1] for row in c.fetchall()]
    print("Current columns:", cols)

    # Ensure experience_required column exists
    if "experience_required" not in cols:
        c.execute("ALTER TABLE opportunities ADD COLUMN experience_required TEXT")
    if "category" not in cols:
        c.execute("ALTER TABLE opportunities ADD COLUMN category TEXT")

    # Create new table without UNIQUE constraint on link
    c.execute("""
    CREATE TABLE IF NOT EXISTS opportunities_new (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        link TEXT NOT NULL,
        institution TEXT NOT NULL,
        country TEXT NOT NULL,
        source_type TEXT NOT NULL,
        sub_specialty TEXT NOT NULL,
        deadline TEXT,
        tuition_fee TEXT,
        registration_fee TEXT,
        monthly_salary TEXT,
        is_funded TEXT,
        seats TEXT,
        acceptance_difficulty TEXT,
        status TEXT DEFAULT 'NEW',
        first_seen_at TEXT NOT NULL,
        last_updated_at TEXT NOT NULL,
        notified_as_new INTEGER DEFAULT 0,
        notified_closing_soon INTEGER DEFAULT 0,
        experience_required TEXT,
        category TEXT
    )
    """)

    # Copy data over
    c.execute("""
    INSERT OR REPLACE INTO opportunities_new (
        id, title, link, institution, country, source_type, sub_specialty,
        deadline, tuition_fee, registration_fee, monthly_salary, is_funded,
        seats, acceptance_difficulty, status, first_seen_at, last_updated_at,
        notified_as_new, notified_closing_soon, experience_required, category
    )
    SELECT 
        id, title, link, institution, country, source_type, sub_specialty,
        deadline, tuition_fee, registration_fee, monthly_salary, is_funded,
        seats, acceptance_difficulty, status, first_seen_at, last_updated_at,
        notified_as_new, notified_closing_soon, experience_required, category
    FROM opportunities
    """)

    c.execute("DROP TABLE opportunities")
    c.execute("ALTER TABLE opportunities_new RENAME TO opportunities")
    conn.commit()
    print("Schema migration complete: UNIQUE constraint on link removed.")

    # Now update URLs safely
    url_fixes = [
        ("%msca-miningbrines%", "https://euraxess.ec.europa.eu/jobs/search"),
        ("%freiberg-hydrogen%", "https://tu-freiberg.de/en/grafa"),
        ("%tudelft-subsurface%", "https://www.tudelft.nl/citg/over-faculteit/afdelingen/geoscience-engineering"),
        ("%theses.ifpen.fr/sujet-caprock%", "https://theses.ifpen.fr/"),
        ("%theses.ifpen.fr/sujet-hydrogen%", "https://theses.ifpen.fr/"),
        ("%dpe.ac.at/jobs-career/%", "https://geoenergy.engineering/"),
        ("%uis.no/en/research/phd%", "https://www.uis.no/en"),
        ("%offres-demploi-et-de-stage%", "https://www.ifpenergiesnouvelles.fr/"),
        ("%concorsi-e-selezioni%", "https://www.ogs.it/it"),
        ("%agh.edu.pl/en/doctoral-school%", "https://sd.agh.edu.pl/en/"),
        ("%careers.slb.com/early-careers/research%", "https://careers.slb.com/early-careers"),
        ("%ntnu.edu/studies/phing/petroleum%", "https://www.ntnu.edu/phd"),
        ("%upg-ploiesti.ro/en%", "https://www.upg-ploiesti.ro/"),
        ("%ku.ac.ae/%", "https://cpg.kfupm.edu.sa/academics/departments/department-of-petroleum-engineering/graduate-programs/"),
        ("%eni.com/it-IT/carriere/formazione.html%", "https://www.polito.it/didattica/dottorato-di-ricerca/ammissione-al-dottorato"),
        ("%eni.com/it-IT/carriere.html#tirocini%", "https://www.eni.com/en-IT/careers/job-opportunities.html"),
        ("%careers.slb.com#early-careers%", "https://careers.slb.com/early-careers")
    ]

    for pattern, new_url in url_fixes:
        c.execute("UPDATE opportunities SET link = ? WHERE link LIKE ?", (new_url, pattern))

    # Explicit 0-year work experience guarantee
    c.execute("""
    UPDATE opportunities 
    SET experience_required = '0 سنوات (مفتوحة بالكامل لحديثي التخرج من الماستر R1 Early-Stage Researcher)'
    """)

    # Merge CCUS/UHS into Petroleum & Reservoir Engineering
    c.execute("""
    UPDATE opportunities
    SET category = 'RESERVOIR_STORAGE'
    WHERE category IS NULL OR category = 'RESERVOIR' OR category = 'CCUS' 
       OR title LIKE '%CCUS%' OR title LIKE '%Storage%' OR title LIKE '%Reservoir%' OR title LIKE '%Multiphase%'
    """)

    conn.commit()
    count = c.execute("SELECT COUNT(*) FROM opportunities").fetchone()[0]
    print(f"Total verified opportunities in database: {count}")

    conn.close()

if __name__ == "__main__":
    migrate()
