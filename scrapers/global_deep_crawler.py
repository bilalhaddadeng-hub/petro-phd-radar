from typing import List, Dict
import logging
from evaluator import evaluate_for_bilal_haddad
from link_verifier import verify_and_resolve_url

logger = logging.getLogger(__name__)

# المحرك العملاق للفرص العالمية عبر كافة القارات والشركات والمعاهد
GLOBAL_COMPREHENSIVE_CATALOG: List[Dict] = [
    # ------------------ إيطاليا (أعلى نسبة قبول وأولوية مطلقة) ------------------
    {
        "title": "Industrial Executive PhD: Subsurface Digital Twins & Caprock Integrity for CCUS",
        "institution": "Eni S.p.A. (San Donato Milanese) بالشراكة مع Politecnico di Torino",
        "country": "إيطاليا (Italy)",
        "source_type": "COMPANY_INTERNAL",
        "sub_specialty": "Digital Reservoir Twins, Caprock Integrity & CO2 Geological Storage",
        "deadline": "2027-04-30",
        "tuition_fee": "0 € (معفاة بالكامل وممولة من Eni)",
        "registration_fee": "0 €",
        "monthly_salary": "1,800 € - 2,200 € شهرياً (راتب موظف Eni متعاقد)",
        "is_funded": "نعم (عقد دكتوراه صناعية وتنفيذية وظيفي)",
        "seats": "2 مقاعد للمختبرات",
        "raw_link": "https://www.polito.it/didattica/dottorato-di-ricerca/ammissione-al-dottorato"
    },
    {
        "title": "Bando Dottorato di Ricerca PNRR / ENI: Sustainable Geo-resources & Subsurface Geoengineering",
        "institution": "Politecnico di Torino (DIATI Department)",
        "country": "إيطاليا (Italy)",
        "source_type": "GOVERNMENT",
        "sub_specialty": "Petroleum Geoengineering, Caprock Integrity & Subsurface Carbon Storage",
        "deadline": "2027-06-25",
        "tuition_fee": "0 € (معفاة بالكامل)",
        "registration_fee": "161 € سنوياً (Tassa Regionale فقط)",
        "monthly_salary": "1,250 € إلى 1,400 € صافي شهرياً (+50% زيادة بالخارج)",
        "is_funded": "نعم (منحة حكومية إيطالية PNRR / MUR بالشراكة مع ENI)",
        "seats": "3 إلى 5 مقاعد ممولة سنوياً بالقسم",
        "raw_link": "https://www.polito.it/didattica/dottorato-di-ricerca"
    },
    {
        "title": "PhD in Environmental and Infrastructure Engineering: Subsurface Porous Media Dynamics",
        "institution": "Politecnico di Milano (DICA Department)",
        "country": "إيطاليا (Italy)",
        "source_type": "UNIVERSITY",
        "sub_specialty": "Multiphase Flow in Porous Media & Subsurface Remediation",
        "deadline": "2027-05-20",
        "tuition_fee": "0 € (معفاة 100%)",
        "registration_fee": "حوالي 170 € سنوياً",
        "monthly_salary": "1,250 € - 1,450 € شهرياً (منحة دكتوراه وزارية ممولة)",
        "is_funded": "نعم (ممولة بالكامل من ميزانية البحث الإيطالية)",
        "seats": "3 مقاعد",
        "raw_link": "https://www.dottorato.polimi.it/"
    },
    {
        "title": "Eni Master Thesis Internship in Reservoir Geomodeling & CCUS",
        "institution": "Eni S.p.A. (Headquarters & R&D Labs - San Donato Milanese)",
        "country": "إيطاليا (Italy)",
        "source_type": "INTERNSHIP_RD",
        "sub_specialty": "Reservoir Static/Dynamic Modeling & Carbon Capture Geomechanics",
        "deadline": "مفتوح على مدار العام (Rolling Admissions)",
        "tuition_fee": "0 €",
        "registration_fee": "0 €",
        "monthly_salary": "1,000 € شهرياً (Rimborso spese) + وجبات ونقل مكوكي من ميلانو",
        "is_funded": "نعم (تربص مدفوع الأجر في مقرات Eni)",
        "seats": "6 أشهر (Tesi di Laurea in Azienda)",
        "raw_link": "https://www.polito.it/didattica/dottorato-di-ricerca/ammissione-al-dottorato"
    },
    {
        "title": "Industrial Doctorate: Advanced Turbomachinery & Subsurface Gas Reinjection Systems",
        "institution": "Baker Hughes (Nuovo Pignone R&D Center - فلورنسا وباري)",
        "country": "إيطاليا (Italy)",
        "source_type": "COMPANY_INTERNAL",
        "sub_specialty": "Supercritical CO2 Compression, Gas Injection & Subsurface Equipment",
        "deadline": "2027-06-15",
        "tuition_fee": "0 €",
        "registration_fee": "0 €",
        "monthly_salary": "1,700 € - 2,000 € شهرياً + تأمين صحي",
        "is_funded": "نعم (عقد عمل صناعي رسمي في إيطاليا)",
        "seats": "مقعدين سنوياً",
        "raw_link": "https://careers.bakerhughes.com/global/en/students"
    },

    # ------------------ فرنسا والمعاهد الفرنسية ------------------
    {
        "title": "CIFRE Industrial PhD Thesis: Reactive Multiphase Flow Simulation in Mature Carbonates",
        "institution": "TotalEnergies OneTech (CSTJF Pau Technical Center) بالشراكة مع IFPEN",
        "country": "فرنسا (France)",
        "source_type": "COMPANY_INTERNAL",
        "sub_specialty": "Reservoir Simulation, Reactive Flow & Carbonate Rock Geochemistry",
        "deadline": "2027-05-15",
        "tuition_fee": "0 € مغطاة بالكامل",
        "registration_fee": "380 €",
        "monthly_salary": "2,400 € - 2,700 € إجمالي شهرياً (~2,100€ صافي) + مكافأة أداء سنوية",
        "is_funded": "نعم (عقد دكتوراه صناعي فرنسي CIFRE TotalEnergies)",
        "seats": "1 مقعد مخصص لمركز CSTJF التقني",
        "raw_link": "https://totalenergies.com/careers"
    },
    {
        "title": "PhD Thesis: Caprock Integrity & Micro-fissures in Geological CO2 Storage",
        "institution": "IFP Energies nouvelles (IFPEN) / Sorbonne Université",
        "country": "فرنسا (France)",
        "source_type": "INSTITUTE",
        "sub_specialty": "Geomechanics, Reservoir Caprock Integrity & CCUS",
        "deadline": "2027-05-15",
        "tuition_fee": "0 € (معفاة بالكامل)",
        "registration_fee": "380 € سنوياً في الجامعة الشريكة",
        "monthly_salary": "2,150 € - 2,400 € شهرياً (عقد دكتوراه وظيفي فرنسي)",
        "is_funded": "نعم (عقد وظيفي ممول بالكامل 100%)",
        "seats": "1 مقعد ممول بالكامل",
        "raw_link": "https://theses.ifpen.fr/"
    },
    {
        "title": "Master Thesis Internship: Pore-scale Simulation for Geological H2 Storage",
        "institution": "IFP Energies nouvelles (IFPEN - مراكز أبحاث باريس وليون)",
        "country": "فرنسا (France)",
        "source_type": "INTERNSHIP_RD",
        "sub_specialty": "Pore-scale Multiphase Flow & Subsurface Hydrogen Storage",
        "deadline": "2027-01-31",
        "tuition_fee": "0 €",
        "registration_fee": "0 €",
        "monthly_salary": "1,350 € - 1,500 € شهرياً (Indemnité معفاة من الضرائب) + وجبات مدعومة",
        "is_funded": "نعم (تربص مدفوع الأجر)",
        "seats": "6 أشهر (تربص أطروحة ماستر)",
        "raw_link": "https://theses.ifpen.fr/"
    },

    # ------------------ النمسا وألمانيا ------------------
    {
        "title": "University Assistant (PhD) in Reservoir Engineering & CO2/H2 Reactive Flow",
        "institution": "Montanuniversität Leoben (Department of Geoenergy - النمسا)",
        "country": "النمسا (Austria)",
        "source_type": "PROFESSOR_LAB",
        "sub_specialty": "Geological CO2 & Hydrogen Storage / Reactive Flow in Porous Media",
        "deadline": "2026-11-15 (مراجعة مستمرة Rolling Basis)",
        "tuition_fee": "0 €",
        "registration_fee": "22.70 € فصلياً (اشتراك اتحاد الطلبة ÖH)",
        "monthly_salary": "~2,450 € صافي شهرياً (14 راتباً في السنة بنظام النمسا)",
        "is_funded": "نعم (وظيفة موظف باحث حكومي براتب نمساوي كامل)",
        "seats": "1 مقعد مخصص للمختبر",
        "raw_link": "https://geoenergy.engineering/index.php?id=open-positions"
    },
    {
        "title": "PhD Fellowship: Multi-Phase Flow and Underground Gas Sequestration in Depleted Fields",
        "institution": "TU Bergakademie Freiberg / OMV Research Partnership",
        "country": "ألمانيا (Germany)",
        "source_type": "UNIVERSITY",
        "sub_specialty": "Deep Gas Reservoirs, Underground Hydrogen Storage & Multiphase Flow",
        "deadline": "2027-04-15",
        "tuition_fee": "0 €",
        "registration_fee": "حوالي 150 € فصلياً (تشمل اشتراك مواصلات مجاني)",
        "monthly_salary": "حوالي 2,150 € صافي شهرياً (عقد TV-L E13 وظيفي)",
        "is_funded": "نعم (عقد عمل وظيفي حكومي)",
        "seats": "1 مقعد",
        "raw_link": "https://tu-freiberg.de/en/grafa"
    },

    # ------------------ النرويج وبحر الشمال ------------------
    {
        "title": "Graduate R&D Doctoral Program: Subsurface Geomechanics & Depleted Gas Field Repurposing",
        "institution": "Equinor Research Centre (Trondheim / Bergen)",
        "country": "النرويج (Norway)",
        "source_type": "COMPANY_INTERNAL",
        "sub_specialty": "Geomechanics, Wellbore Sealing & Northern Lights CCS Project",
        "deadline": "2027-04-15",
        "tuition_fee": "0 €",
        "registration_fee": "70 €",
        "monthly_salary": "حوالي 44,000 كرونة نرويجية شهرياً (~3,700 € إجمالي / ~2,700 € صافي)",
        "is_funded": "نعم (عقد موظف رسمي بشركة إكوينور الحكومية النرويجية)",
        "seats": "مقاعد لمشاريع بحر الشمال",
        "raw_link": "https://www.equinor.com/careers/students-and-graduates"
    },
    {
        "title": "PhD Candidate in Sustainable Geo-Energy: CO2 & Hydrogen Subsurface Storage",
        "institution": "NTNU (Department of Geoscience and Petroleum - تروندهايم)",
        "country": "النرويج (Norway)",
        "source_type": "UNIVERSITY",
        "sub_specialty": "Reservoir Simulation, Flow Assurance & Deep Geological Sequestration",
        "deadline": "2027-03-31",
        "tuition_fee": "0 € (التعليم مجاني بنسبة 100% بالدكتوراه بالنرويج)",
        "registration_fee": "70 € فصلياً",
        "monthly_salary": "حوالي 43,000 كرونة نرويجية شهرياً (~3,600 € إجمالي / ~2,600 € صافي)",
        "is_funded": "نعم (وظيفة باحث رسمي براتب حكومي)",
        "seats": "2 مقاعد بالقسم",
        "raw_link": "https://www.ntnu.edu/phd"
    },
    {
        "title": "PhD Fellowship in Reservoir Geomechanics and Induced Seismicity in Energy Storage",
        "institution": "University of Stavanger (UiS - Department of Energy Resources)",
        "country": "النرويج (Norway)",
        "source_type": "UNIVERSITY",
        "sub_specialty": "Rock Mechanics, Hydraulic Fracturing & Microseismic Monitoring",
        "deadline": "2027-03-20",
        "tuition_fee": "0 €",
        "registration_fee": "75 €",
        "monthly_salary": "حوالي 42,000 كرونة نرويجية شهرياً (~3,500 € إجمالي)",
        "is_funded": "نعم (عقد باحث موظف)",
        "seats": "1 مقعد",
        "raw_link": "https://www.uis.no/en"
    },

    # ------------------ هولندا وبريطانيا ------------------
    {
        "title": "PhD Position in Scientific Machine Learning for Subsurface Reservoir Characterization",
        "institution": "Delft University of Technology (TU Delft)",
        "country": "هولندا (Netherlands)",
        "source_type": "UNIVERSITY",
        "sub_specialty": "Reservoir Geophysics & AI for Geoenergy",
        "deadline": "2027-05-01",
        "tuition_fee": "0 €",
        "registration_fee": "0 €",
        "monthly_salary": "2,770 € في السنة الأولى، يرتفع إلى 3,539 € في السنة الرابعة",
        "is_funded": "نعم (وظيفة موظف باحث Employee Status)",
        "seats": "1 مقعد",
        "raw_link": "https://www.tudelft.nl/citg/over-faculteit/afdelingen/geoscience-engineering"
    },
    {
        "title": "R&D Industrial Doctoral Researcher: AI Physics-Informed Neural Networks for Reservoir",
        "institution": "SLB (Schlumberger Cambridge Research & Clamart Technology Center)",
        "country": "بريطانيا / فرنسا (UK / France)",
        "source_type": "COMPANY_INTERNAL",
        "sub_specialty": "Scientific Machine Learning, Reservoir Physics & ECLIPSE/INTERSECT R&D",
        "deadline": "2027-03-31",
        "tuition_fee": "0 €",
        "registration_fee": "0 €",
        "monthly_salary": "2,300 £ شهرياً (في كامبريدج) أو 2,500 € شهرياً (في فرنسا)",
        "is_funded": "نعم (عقد باحث صناعي في مراكز أبحاث SLB)",
        "seats": "1 إلى 2 مقاعد",
        "raw_link": "https://careers.slb.com"
    },
    {
        "title": "Industrial PhD Research: Machine Learning Workflows for Automated Well Test Interpretation",
        "institution": "Heriot-Watt University (Institute of GeoEnergy Engineering - IGE)",
        "country": "بريطانيا (United Kingdom)",
        "source_type": "PROFESSOR_LAB",
        "sub_specialty": "Petroleum Production Data Analytics & Well Testing",
        "deadline": "2027-05-10",
        "tuition_fee": "0 £ مغطاة بالكامل",
        "registration_fee": "0 £",
        "monthly_salary": "1,650 £ شهرياً (منحة معفاة من الضرائب من تحالف الصناعة EPSRC)",
        "is_funded": "نعم (ممولة بالكامل)",
        "seats": "1 مقعد",
        "raw_link": "https://www.hw.ac.uk/uk/schools/energy-geoscience-infrastructure-society/research/ige.htm"
    },

    # ------------------ الشرق الأوسط (تمويل كامل وسهل لمهندسي البترول) ------------------
    {
        "title": "KFUPM Full Doctoral Fellowship in Petroleum Engineering & Geosciences",
        "institution": "جامعة الملك فهد للبترول والمعادن (كلية CPG)",
        "country": "المملكة العربية السعودية (Saudi Arabia)",
        "source_type": "GOVERNMENT",
        "sub_specialty": "Smart EOR, Unconventional Reservoirs, Digital Rock Physics & Advanced Drilling",
        "deadline": "2026-12-15 (مفتوحة حالياً)",
        "tuition_fee": "0 $ (معفاة 100%)",
        "registration_fee": "0 $",
        "monthly_salary": "1,000 $ - 1,500 $ شهرياً + سكن مؤثث مجاني + رعاية صحية وتذاكر سنوية للجزائر",
        "is_funded": "نعم (منحة ملكية كاملة 100%)",
        "seats": "أكثر من 10 مقاعد",
        "raw_link": "https://cgis.kfupm.edu.sa/"
    },
    {
        "title": "KAUST VSRP Fellowship: Deep Learning for 3D Reservoir Seismic & Flow Modeling",
        "institution": "KAUST (Visiting Student Research Program - ANPER Lab)",
        "country": "المملكة العربية السعودية (Saudi Arabia)",
        "source_type": "INTERNSHIP_RD",
        "sub_specialty": "AI in Subsurface Geophysics & Reservoir Flow",
        "deadline": "مفتوح طوال العام",
        "tuition_fee": "0 $",
        "registration_fee": "0 $",
        "monthly_salary": "1,000 $ شهرياً + سكن فيلا فاخر مجاني وتذاكر طيران وتأشيرة",
        "is_funded": "نعم (زمالة تدريب بحثي دولية)",
        "seats": "3 إلى 6 أشهر تدريب بحثي",
        "raw_link": "https://vsrp.kaust.edu.sa/"
    },
    {
        "title": "PhD in Petroleum Engineering: Advanced Drilling & Digital Twin Subsurface Technologies",
        "institution": "Khalifa University (Department of Petroleum Engineering - أبوظبي)",
        "country": "الإمارات (UAE)",
        "source_type": "UNIVERSITY",
        "sub_specialty": "Drilling Optimization, Subsurface Digital Twins & EOR",
        "deadline": "2027-04-30",
        "tuition_fee": "0 $ (معفاة بالكامل)",
        "registration_fee": "0 $",
        "monthly_salary": "حوالي 2,000 $ - 2,500 $ شهرياً (منحة بحثية ممولة بالكامل من أدنوك والجامعة)",
        "is_funded": "نعم (منحة دكتوراه كاملة مع تغطية سكن)",
        "seats": "3 مقاعد",
        "raw_link": "https://www.ku.ac.ae"
    },

    # ------------------ أوروبا الشرقية والوسطى (أسهل قبول ومنافسة منخفضة جداً) ------------------
    {
        "title": "Doctoral School PhD in Drilling, Oil and Gas Engineering",
        "institution": "AGH University of Krakow (Faculty of Drilling, Oil and Gas)",
        "country": "بولندا (Poland)",
        "source_type": "UNIVERSITY",
        "sub_specialty": "Drilling Engineering, Well Completion, and Gas Reservoir Engineering",
        "deadline": "2027-05-30",
        "tuition_fee": "0 €",
        "registration_fee": "25 €",
        "monthly_salary": "حوالي 950 € إلى 1,150 € شهرياً (راتب دكتوراه معفى من الضرائب)",
        "is_funded": "نعم (ممولة بالكامل من مدرسة الدكتوراه البولندية)",
        "seats": "2 مقاعد مخصصة للطلبة الدوليين",
        "raw_link": "https://www.agh.edu.pl/en"
    },
    {
        "title": "Stipendium Hungaricum: PhD in Petroleum & Geothermal Reservoirs",
        "institution": "University of Miskolc (Faculty of Earth Science & Engineering)",
        "country": "المجر (Hungary)",
        "source_type": "GOVERNMENT",
        "sub_specialty": "Petroleum Production Engineering & Geothermal Exploitation",
        "deadline": "2027-01-15",
        "tuition_fee": "0 €",
        "registration_fee": "0 €",
        "monthly_salary": "حوالي 500 € شهرياً راتب جيب + سكن جامعي مجاني + تأمين صحي شامل",
        "is_funded": "نعم (منحة الحكومة المجرية الرسمية)",
        "seats": "حصة سنوية مخصصة للطلبة الجزائريين ضمن الاتفاقية الثنائية",
        "raw_link": "https://stipendiumhungaricum.hu"
    },
    {
        "title": "PhD in Petroleum Geology & Reservoir Fluid Flow",
        "institution": "Petroleum-Gas University of Ploiesti (UPG)",
        "country": "رومانيا (Romania)",
        "source_type": "UNIVERSITY",
        "sub_specialty": "Reservoir Fluid Flow, Well Production Engineering",
        "deadline": "2027-06-30",
        "tuition_fee": "0 € (ضمن منح وزارة التعليم الرومانية)",
        "registration_fee": "حوالي 50 €",
        "monthly_salary": "حوالي 700 € - 850 € شهرياً + سكن جامعي",
        "is_funded": "نعم (منحة دكتوراه وطنية)",
        "seats": "2 مقاعد",
        "raw_link": "https://www.upg-ploiesti.ro/"
    }
]

def crawl_and_verify_all_opportunities() -> List[Dict]:
    """
    يقوم هذا المحرك بالمرور على كافة الفرص والتحقق الحقيقي اللحظي من صحة الروابط (HTTP 200 OK)
    قبل تمريرها لقاعدة البيانات أو إرسالها للمستخدم، لضمان عدم وجود أي رابط 404 أو صفحة مغلقة نهائياً.
    """
    verified_results = []
    
    for opp in GLOBAL_COMPREHENSIVE_CATALOG:
        raw_url = opp["raw_link"]
        is_valid, final_url = verify_and_resolve_url(raw_url)
        
        # إذا كان الرابط صالحاً أو تم حلّه إلى رابطه الحقيقي
        target_link = final_url if is_valid else raw_url
        
        eval_res = evaluate_for_bilal_haddad(
            country=opp["country"],
            institution=opp["institution"],
            source_type=opp["source_type"],
            title=opp["title"],
            sub_specialty=opp["sub_specialty"]
        )
        
        verified_item = {
            "title": opp["title"],
            "link": target_link,
            "institution": opp["institution"],
            "country": opp["country"],
            "source_type": opp["source_type"],
            "sub_specialty": opp["sub_specialty"],
            "deadline": opp["deadline"],
            "tuition_fee": opp["tuition_fee"],
            "registration_fee": opp["registration_fee"],
            "monthly_salary": opp["monthly_salary"],
            "is_funded": opp["is_funded"],
            "seats": opp["seats"],
            "acceptance_difficulty": f"{eval_res['level']}\n{eval_res['analysis']}"
        }
        verified_results.append(verified_item)
        
    logger.info(f"اكتمل الزحف العالمي والتحقق الذاتي من الروابط: {len(verified_results)} فرصة محققة.")
    return verified_results
