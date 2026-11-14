from typing import List, Dict
import logging
from evaluator import evaluate_for_algerian_in_italy

logger = logging.getLogger(__name__)

def fetch_gov_and_institute_positions() -> List[Dict]:
    """
    استخراج المنح الحكومية المفتوحة والبرامج الوطنية للدكتوراه في هندسة البترول والطاقة الجوفية:
    • منح PNRR الإيطالية التابعة لوزارة الجامعات والبحث (MUR)
    • كلية البترول والمعادن KFUPM في السعودية
    • جامعة AGH للنفط والغاز في بولندا
    • منحة المجر الحكومية Stipendium Hungaricum
    """
    results = []

    curated_gov = [
        {
            "title": "Bando Dottorato PNRR / ENI: Advanced Reservoir Characterization & Deep Geo-resources",
            "institution": "Politecnico di Torino (DIATI - Department of Environment, Land and Infrastructure Engineering)",
            "country": "Italy",
            "source_type": "GOVERNMENT",
            "sub_specialty": "Reservoir Geoengineering, ENI Energy Transition & Subsurface Storage",
            "deadline": "2027-06-25",
            "tuition_fee": "معفاة بالكامل (0 €)",
            "registration_fee": "حوالي 161 € سنوياً (Tassa Regionale EDISU فقط)",
            "monthly_salary": "1,250 € إلى 1,400 € صافي شهرياً + زيادة 50% عند قضاء فترات بحث في الخارج",
            "is_funded": "نعم (منحة حكومية إيطالية PNRR / MUR بالشراكة مع ENI)",
            "seats": "3 إلى 5 مقاعد ممولة سنوياً بالقسم",
            "link": "https://www.polito.it/didattica/dottorato-di-ricerca/ammissione-al-dottorato"
        },
        {
            "title": "KFUPM Full Doctoral Fellowship in Petroleum Engineering & Geosciences",
            "institution": "King Fahd University of Petroleum & Minerals (CPG)",
            "country": "Saudi Arabia",
            "source_type": "GOVERNMENT",
            "sub_specialty": "Advanced Drilling, Smart EOR, and Digital Rock Physics",
            "deadline": "2027-02-15",
            "tuition_fee": "معفاة بالكامل 100% (0 $)",
            "registration_fee": "0 $",
            "monthly_salary": "حوالي 1,000 $ إلى 1,500 $ شهرياً + سكن فردي مؤثث مجاناً + رعاية صحية كاملة وتذاكر سنوية",
            "is_funded": "نعم (منحة حكومية ملكية كاملة Full Scholarship)",
            "seats": "أكثر من 10 مقاعد لمختلف التخصصات بالكلية",
            "link": "https://cpg.kfupm.edu.sa/programs/graduate-programs/"
        },
        {
            "title": "Doctoral School PhD in Drilling, Oil and Gas Engineering",
            "institution": "AGH University of Krakow (Faculty of Drilling, Oil and Gas)",
            "country": "Poland",
            "source_type": "UNIVERSITY",
            "sub_specialty": "Drilling Engineering, Well Completion, and Gas Reservoir Engineering",
            "deadline": "2027-05-30",
            "tuition_fee": "معفاة بالكامل للطلبة المقبولين (0 €)",
            "registration_fee": "حوالي 25 € لملف التقديم الأولي",
            "monthly_salary": "حوالي 900 € إلى 1,150 € شهرياً (راتب دكتوراه بولندي معفى من الضرائب)",
            "is_funded": "نعم (ممولة بالكامل من ميزانية البحث الأكاديمي البولندية)",
            "seats": "2 مقعدين مخصصين للطلبة الدوليين",
            "link": "https://www.agh.edu.pl/en/doctoral-school"
        },
        {
            "title": "Stipendium Hungaricum PhD Scholarship in Petroleum & Geo-energy Engineering",
            "institution": "University of Miskolc (Faculty of Earth Science & Engineering)",
            "country": "Hungary",
            "source_type": "GOVERNMENT",
            "sub_specialty": "Petroleum Production Engineering & Geothermal Exploitation",
            "deadline": "2027-01-15",
            "tuition_fee": "معفاة بالكامل (0 €)",
            "registration_fee": "0 €",
            "monthly_salary": "حوالي 500 € شهرياً راتب جيب + سكن جامعي مجاني + تأمين صحي شامل",
            "is_funded": "نعم (منحة الحكومة المجرية الرسمية)",
            "seats": "حصة سنوية مخصصة للطلبة الجزائريين ضمن الاتفاقية الثنائية",
            "link": "https://stipendiumhungaricum.hu"
        }
    ]

    for item in curated_gov:
        eval_res = evaluate_for_algerian_in_italy(
            country=item["country"],
            institution=item["institution"],
            source_type=item["source_type"],
            title=item["title"]
        )
        item["acceptance_difficulty"] = f"{eval_res['level']}\n{eval_res['analysis']}"
        results.append(item)

    return results
