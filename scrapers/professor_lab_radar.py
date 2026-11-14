from typing import List, Dict
import logging
from evaluator import evaluate_for_algerian_in_italy

logger = logging.getLogger(__name__)

def fetch_professor_lab_positions() -> List[Dict]:
    """
    استخراج الفرص المباشرة الممولة من مشاريع المخابر والأساتذة (Lab & Professor Funded Positions)
    حيث يعلن الأستاذ عن مقعد دكتوراه ممول من مشروع صناعي أو منحة ERC دون انتظار دورات القبول العامة.
    """
    results = []

    curated_prof_positions = [
        {
            "title": "PhD Position (Praedoc): Experimental Investigation of Foam-Assisted CO2 and Hydrogen Injection",
            "institution": "Montanuniversität Leoben (Chair of Reservoir Engineering - Prof. Research Grant)",
            "country": "Austria",
            "source_type": "PROFESSOR_LAB",
            "sub_specialty": "Reservoir Fluid Mechanics & Foam EOR / Underground Storage",
            "deadline": "2027-04-10",
            "tuition_fee": "معفاة بالكامل (0 €)",
            "registration_fee": "حوالي 22 € فصلياً (ÖH-Beitrag رسوم اتحاد الطلبة النمساوي فقط)",
            "monthly_salary": "حوالي 2,450 € صافي شهرياً (راتب وظيفي نمساوي B1 / 30 ساعة أسبوعياً مع 14 راتباً في السنة)",
            "is_funded": "نعم (وظيفة بحثية ممولة من مشروع بروفيسور صناعي)",
            "seats": "1 مقعد مخصص للمختبر",
            "link": "https://dpe.ac.at/jobs-career/"
        },
        {
            "title": "Funded PhD Opportunity: Multi-scale Geo-mechanical Modeling for Deep Subsurface Energy Storage",
            "institution": "University of Stavanger (UiS - National Centre for Sustainable Subsurface Utilization)",
            "country": "Norway",
            "source_type": "PROFESSOR_LAB",
            "sub_specialty": "Geomechanics & Reservoir Stimulation",
            "deadline": "2027-03-20",
            "tuition_fee": "معفاة بالكامل (0 €)",
            "registration_fee": "حوالي 75 € فصلياً رسوم نقابة الطلبة (Semesteravgift)",
            "monthly_salary": "حوالي 42,000 إلى 45,000 كرونة نرويجية شهرياً (ما يعادل تقريباً 3,600 € إجمالي / ~2,600 € صافي)",
            "is_funded": "نعم (عقد وظيفي كامل بمرتب موظف حكومي نرويجي)",
            "seats": "1 مقعد",
            "link": "https://www.uis.no/en/research/phd-programmes"
        },
        {
            "title": "Industrial PhD Research Student: Machine Learning Workflows for Automated Well Test Interpretation",
            "institution": "Heriot-Watt University (Institute of GeoEnergy Engineering - IGE)",
            "country": "United Kingdom",
            "source_type": "PROFESSOR_LAB",
            "sub_specialty": "Petroleum Production Data Analytics & Well Testing",
            "deadline": "2027-05-10",
            "tuition_fee": "معفاة بالكامل مغطاة من التحالف الصناعي للبروفيسور",
            "registration_fee": "0 £",
            "monthly_salary": "1,650 £ شهرياً (منحة معفاة من الضرائب Stipend من ميزانية EPSRC / شركاء الصناعة)",
            "is_funded": "نعم (ممولة بالكامل مع ميزانية حضور مؤتمرات SPE)",
            "seats": "1 مقعد",
            "link": "https://www.hw.ac.uk/uk/schools/energy-geoscience-infrastructure-society/research/ige.htm"
        }
    ]

    for item in curated_prof_positions:
        eval_res = evaluate_for_algerian_in_italy(
            country=item["country"],
            institution=item["institution"],
            source_type=item["source_type"],
            title=item["title"]
        )
        item["acceptance_difficulty"] = f"{eval_res['level']}\n{eval_res['analysis']}"
        results.append(item)

    return results
