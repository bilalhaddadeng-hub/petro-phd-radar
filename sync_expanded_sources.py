import sys
from pathlib import Path

BASE_DIR = Path("C:/Users/admin/.gemini/antigravity/scratch/petro_phd_radar_bot")
sys.path.append(str(BASE_DIR))

from database import init_db, save_or_update_opportunity, get_connection
from data.corporate_radar import CORPORATE_AND_INDUSTRIAL_PHD
from data.internships import RD_INTERNSHIPS_RADAR

init_db()

# مزامنة فرص الشركات والدكتوراه الصناعية
for item in CORPORATE_AND_INDUSTRIAL_PHD:
    opp_data = {
        "title": item["title"],
        "link": item["link"],
        "institution": item["company"],
        "country": item["country"],
        "source_type": "COMPANY_INTERNAL",
        "sub_specialty": item["sub_specialty"],
        "deadline": item["deadline"],
        "tuition_fee": item["tuition_fee"],
        "registration_fee": item["registration_fee"],
        "monthly_salary": item["monthly_salary"],
        "is_funded": "نعم (عقد عمل صناعي ممول من الشركة)",
        "seats": item["seats"],
        "acceptance_difficulty": item["acceptance_difficulty"]
    }
    save_or_update_opportunity(opp_data)

# مزامنة فرص التربصات والتدريب R&D
for item in RD_INTERNSHIPS_RADAR:
    opp_data = {
        "title": f"💼 {item['title']}",
        "link": item["link"],
        "institution": item["institution"],
        "country": item["country"],
        "source_type": "INTERNSHIP_RD",
        "sub_specialty": item["sub_specialty"],
        "deadline": item["deadline"],
        "tuition_fee": "0 € (تربص مدفوع الأجر)",
        "registration_fee": "0 €",
        "monthly_salary": item["monthly_stipend"],
        "is_funded": "نعم (مكافأة تدريب شهرية ممولة)",
        "seats": item["duration"],
        "acceptance_difficulty": f"{item['acceptance_difficulty']}\n\n🎯 هل يؤهل للدكتوراه؟:\n{item['leads_to_phd']}"
    }
    save_or_update_opportunity(opp_data)

conn = get_connection()
c = conn.cursor()
c.execute("SELECT count(*) FROM opportunities")
total = c.fetchone()[0]
conn.close()

print(f"✅ تم بنجاح دمج وتحديث كافة المصادر الموسعة! إجمالي الفرص الآن: {total}")
