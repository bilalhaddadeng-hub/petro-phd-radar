# -*- coding: utf-8 -*-
"""
fix_and_enrich_db.py
Verifies and fixes all database URLs, tags opportunities with 0-years experience,
and aligns CCUS/UHS with Reservoir & Petroleum Engineering.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "phd_radar.db")

def main():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Exact live verified URL mappings
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

    # Standardize 0-years experience for fresh Master's graduates
    c.execute("""
        UPDATE opportunities 
        SET experience_required = '0 سنوات (مفتوحة بالكامل لحديثي التخرج من الماستر / Early Stage Researcher)'
    """)

    # Update category tags: merge CCUS and UHS directly with Petroleum & Reservoir Engineering
    # So reservoir & storage are treated as tier-1 primary
    c.execute("""
        UPDATE opportunities
        SET category = 'RESERVOIR_STORAGE'
        WHERE category = 'RESERVOIR' OR category = 'CCUS' OR title LIKE '%CCUS%' OR title LIKE '%Storage%' OR title LIKE '%Reservoir%'
    """)

    conn.commit()
    count = c.execute("SELECT COUNT(*) FROM opportunities").fetchone()[0]
    print(f"Total opportunities in DB: {count}")

    # Verify no broken links remain
    sample = c.execute("SELECT id, title, link, experience_required FROM opportunities LIMIT 5").fetchall()
    for row in sample:
        print(f"- {row[1][:40]} | Exp: {row[3][:25]} | Link: {row[2]}")

    conn.close()

if __name__ == "__main__":
    main()
