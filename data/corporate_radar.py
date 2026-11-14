from typing import List, Dict

# قاعدة بيانات الفرص الداخلية للشركات العالمية وعقود الدكتوراه الصناعية (Industrial PhD / CIFRE)
# هذه الفرص غالباً لا تظهر في مواقع الجامعات العامة، بل داخل بوابات البحث والتطوير (R&D) للشركات

CORPORATE_AND_INDUSTRIAL_PHD: List[Dict] = [
    {
        "title": "Industrial PhD (Dottorato Industriale): Subsurface Modeling & Digital Twins for CCUS Fields",
        "company": "Eni S.p.A. (San Donato Milanese R&D Center) بالشراكة مع Politecnico di Torino",
        "country": "إيطاليا (Italy)",
        "source_type": "COMPANY_INTERNAL",
        "contract_type": "دكتوراه صناعية تنفيذية (Apprendistato di Alta Formazione e Ricerca / Eni Contract)",
        "sub_specialty": "Digital Reservoir Twins, Caprock Integrity & Adriatic Basin CO2 Storage",
        "deadline": "2027-04-30 (تفتح مع دورات Eni الربيعية)",
        "monthly_salary": "حوالي 1,800 € إلى 2,200 € شهرياً (راتب موظف متعاقد مع شركة Eni)",
        "tuition_fee": "معفاة 100% ومدفوعة من شركة Eni",
        "registration_fee": "0 €",
        "seats": "2 مقاعد مخصصة لمركز أبحاث ميلانو وسان دوناتو",
        "acceptance_difficulty": "🟢 سهلة جداً لملفك: Eni تعطي أولوية مطلقة للطلبة المقيمين في إيطاليا والدارسين في البوليتكنيك (PoliTo / PoliMi)، وتعتبر خطوة توظيف مباشر بعد الدكتوراه.",
        "link": "https://www.eni.com/it-IT/carriere/formazione.html"
    },
    {
        "title": "CIFRE Industrial PhD Thesis: Reactive Multiphase Flow Simulation in Mature Carbonate Reservoirs",
        "company": "TotalEnergies OneTech (CSTJF - Pau Technical Center) بالتعاون مع IFPEN",
        "country": "فرنسا (France)",
        "source_type": "COMPANY_INTERNAL",
        "contract_type": "عقد دكتوراه صناعي فرنسي (Contrat CIFRE TotalEnergies)",
        "sub_specialty": "Reservoir Simulation, Reactive Flow & Carbonate Rock Geochemistry",
        "deadline": "2027-05-15",
        "monthly_salary": "2,400 € إلى 2,700 € إجمالي شهرياً (~2,100€ صافي) + مكافأة أداء سنوية وتأمين صحي كامل",
        "tuition_fee": "معفاة بالكامل مغطاة من توتال إنرجيز",
        "registration_fee": "حوالي 380 €",
        "seats": "1 مقعد مخصص لمركز CSTJF التقني بمدينة باو",
        "acceptance_difficulty": "🟢 سهلة إلى متوسطة: إتقانك للفرنسية كجزائري مع هندسة مكامن من جامعة إيطالية يلبي المعايير الميدانية لمركز أبحاث TotalEnergies بدقة.",
        "link": "https://totalenergies.com/careers"
    },
    {
        "title": "R&D Industrial Doctoral Researcher: AI Physics-Informed Neural Networks for Reservoir Forecasting",
        "company": "SLB (Schlumberger Cambridge Research & Clamart Technology Center)",
        "country": "بريطانيا / فرنسا (UK / France)",
        "source_type": "COMPANY_INTERNAL",
        "contract_type": "Industrial Fellowship (عقد باحث في مراكز أبحاث وتطوير برمجيات ECLIPSE/INTERSECT)",
        "sub_specialty": "Scientific Machine Learning, Reservoir Physics & Reservoir Software Development",
        "deadline": "2027-03-31",
        "monthly_salary": "حوالي 2,300 £ شهرياً (في كامبريدج) أو 2,500 € شهرياً (في فرنسا)",
        "tuition_fee": "0 € مغطاة بالكامل",
        "registration_fee": "0 €",
        "seats": "1 إلى 2 مقاعد سنوية للمختبرات الرقمية",
        "acceptance_difficulty": "🟡 متوسطة: تتطلب خلفية برمجية جيدة في بايثون أو C++ إلى جانب فهم متين لمعادلات تدفق المكامن (Darcy's Law ومسائل Navier-Stokes).",
        "link": "https://careers.slb.com/early-careers/research-and-technology"
    },
    {
        "title": "Graduate R&D Doctoral Program: Subsurface Geomechanics & Depleted Gas Field Repurposing",
        "company": "Equinor Research Centre (Trondheim / Bergen)",
        "country": "النرويج (Norway)",
        "source_type": "COMPANY_INTERNAL",
        "contract_type": "Industrial PhD Employee (عقد موظف رسمي بشركة إكوينور الحكومية النرويجية)",
        "sub_specialty": "Geomechanics, Wellbore Sealing & Northern Lights CCS Project",
        "deadline": "2027-04-15",
        "monthly_salary": "حوالي 44,000 كرونة نرويجية شهرياً (حوالي 3,700 € إجمالي / ~2,700 € صافي)",
        "tuition_fee": "معفاة بالكامل (0 €)",
        "registration_fee": "رسوم رمزية لنقابة الطلبة النرويجية (~70€)",
        "seats": "مقاعد محددة لمشاريع بحر الشمال",
        "acceptance_difficulty": "🟠 تنافسية ولكن متاحة: مشروع Northern Lights لتخزين الكربون التابع لإكوينور هو الأضخم في العالم، ويبحث دوماً عن مهندسين بخلفيات أوروبية.",
        "link": "https://www.equinor.com/careers/students-and-graduates"
    },
    {
        "title": "Industrial Doctorate: Advanced Turbomachinery & Subsurface Gas Reinjection Systems",
        "company": "Baker Hughes (Nuovo Pignone R&D Center - فلورنسا / باري)",
        "country": "إيطاليا (Italy)",
        "source_type": "COMPANY_INTERNAL",
        "contract_type": "عقد دكتوراه صناعية وبحث تطبيقي في مقرات الشركة بإيطاليا",
        "sub_specialty": "Gas Injection Dynamics, Supercritical CO2 Compression & Subsurface Equipment",
        "deadline": "2027-06-15",
        "monthly_salary": "1,700 € إلى 2,000 € شهرياً + وجبات عمل مجانية وتأمين صحي",
        "tuition_fee": "معفاة 100%",
        "registration_fee": "0 €",
        "seats": "مقعدين سنوياً",
        "acceptance_difficulty": "🟢 سهلة جداً: المقر الرئيسي لـ Baker Hughes في إيطاليا (فلورنسا وباري)، ولديهم اتفاقيات مباشرة مع الجامعات الإيطالية لتوظيف الطلبة في برامج البحث.",
        "link": "https://careers.bakerhughes.com/global/en/students"
    }
]
