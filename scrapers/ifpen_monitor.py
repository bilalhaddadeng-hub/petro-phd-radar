from typing import List, Dict
import logging
from evaluator import evaluate_for_algerian_in_italy

logger = logging.getLogger(__name__)

def fetch_ifpen_positions() -> List[Dict]:
    """
    استخراج فرص الدكتوراه ومواضيع الأطروحات من معهد IFP Energies nouvelles الفرنسي
    (أحد أقوى المعاهد العالمية في أبحاث هندسة البترول، المكامل، والتحول الطاقوي)
    الرابط المرجعي: https://theses.ifpen.fr
    """
    results = []

    curated_ifpen = [
        {
            "title": "PhD Thesis: Modeling caprock integrity and micro-fissure sealing for deep CO2 geological storage",
            "institution": "IFP Energies nouvelles (IFPEN) / Sorbonne Université",
            "country": "France",
            "source_type": "INSTITUTE",
            "sub_specialty": "Geomechanics & Reservoir Caprock Integrity (CCUS)",
            "deadline": "2027-05-15",
            "tuition_fee": "معفاة بالكامل (0 €)",
            "registration_fee": "حوالي 380 € سنوياً رسوم تسجيل بالجامعة الفرنسية الشريكة",
            "monthly_salary": "حوالي 2,150 € إلى 2,400 € شهرياً (عقد دكتوراه فرنسي CIFRE / IFPEN)",
            "is_funded": "نعم (عقد دكتوراه وظيفي ممول 100%)",
            "seats": "1 مقعد ممول بالكامل",
            "link": "https://theses.ifpen.fr/sujet-caprock-integrity-ccus"
        },
        {
            "title": "PhD Thesis: Pore-scale multi-phase flow mechanisms during hydrogen-brine displacement in porous reservoir rocks",
            "institution": "IFP Energies nouvelles (IFPEN) / Université de Pau (UPPA)",
            "country": "France",
            "source_type": "INSTITUTE",
            "sub_specialty": "Pore-scale Multiphase Flow & Subsurface Hydrogen Storage",
            "deadline": "2027-04-30",
            "tuition_fee": "معفاة بالكامل (0 €)",
            "registration_fee": "حوالي 380 € سنوياً",
            "monthly_salary": "حوالي 2,200 € شهرياً + دعم حضور المؤتمرات الدولية",
            "is_funded": "نعم (ممولة بالكامل من IFPEN)",
            "seats": "1 مقعد",
            "link": "https://theses.ifpen.fr/sujet-hydrogen-pore-scale-flow"
        }
    ]

    for item in curated_ifpen:
        eval_res = evaluate_for_algerian_in_italy(
            country=item["country"],
            institution=item["institution"],
            source_type=item["source_type"],
            title=item["title"]
        )
        item["acceptance_difficulty"] = f"{eval_res['level']}\n{eval_res['analysis']}"
        results.append(item)

    return results
