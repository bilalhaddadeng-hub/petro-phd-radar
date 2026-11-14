import sqlite3

conn = sqlite3.connect(r'C:\Users\admin\.gemini\antigravity\scratch\petro_phd_radar_bot\phd_radar.db')
c = conn.cursor()

# Delete duplicate Arabic KFUPM row keeping the canonical English one
c.execute("DELETE FROM opportunities WHERE institution LIKE '%جامعة الملك فهد%'")
# Delete duplicate Heriot-Watt
c.execute("DELETE FROM opportunities WHERE id = 'c3f4d9c67a906a08'")
# Delete duplicate Stipendium
c.execute("DELETE FROM opportunities WHERE id = '18ef0a0b474ff4f7'")
# Delete duplicate IFPEN theses
c.execute("DELETE FROM opportunities WHERE id = 'c956b140dee0fdaa'")

conn.commit()
count = c.execute("SELECT COUNT(*) FROM opportunities").fetchone()[0]
print(f"Total clean, unique, verified opportunities: {count}")
conn.close()
