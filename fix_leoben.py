# -*- coding: utf-8 -*-
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "phd_radar.db")

def fix_leoben_and_all():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # استبدال روابط جامعة ليوبن برابط بوابة التوظيف والتقديم الرسمي المباشر
    c.execute("""
    UPDATE opportunities
    SET link = 'https://www.unileoben.ac.at/en/jobs/'
    WHERE institution LIKE '%Leoben%' OR link LIKE '%geoenergy.engineering%'
    """)

    # استبدال رابط كامبريدج ببوابة الدراسات العليا والبحث
    c.execute("""
    UPDATE opportunities
    SET link = 'https://www.postgraduate.study.cam.ac.uk/'
    WHERE institution LIKE '%Cambridge%'
    """)

    # استبدال روابط يوراكسيس بالبحث المباشر
    c.execute("""
    UPDATE opportunities
    SET link = 'https://euraxess.ec.europa.eu/jobs/search'
    WHERE link = 'https://euraxess.ec.europa.eu'
    """)

    conn.commit()
    print("Database updated successfully.")

    # فحص الفرص المحدثة
    rows = c.execute("SELECT title, institution, link FROM opportunities WHERE institution LIKE '%Leoben%'").fetchall()
    for r in rows:
        print(f"Updated Leoben record: {r[0]} | Link: {r[2]}")

    conn.close()

if __name__ == "__main__":
    fix_leoben_and_all()
