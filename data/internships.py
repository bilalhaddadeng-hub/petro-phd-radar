from typing import List, Dict

# قاعدة بيانات فرص التدريب المتقدم والتربصات البحثية (R&D Internships & Master Thesis Positions)
# هذه الفرص تمنحك راتباً شهرياً ممتازاً وهي الجسر المباشر للتحول إلى دكتوراه ممولة بالكامل

RD_INTERNSHIPS_RADAR: List[Dict] = [
    {
        "title": "Master Thesis Internship (Stage R&D): Pore-scale Simulation for Geological H2 Storage",
        "institution": "IFP Energies nouvelles (IFPEN - مراكز أبحاث باريس وليون)",
        "country": "فرنسا (France)",
        "duration": "6 أشهر (تربص أطروحة ماستر Tesi di Laurea magistrale)",
        "monthly_stipend": "حوالي 1,350 € إلى 1,500 € شهرياً (Indemnité de stage معفاة من الضرائب) + وجبات غداء مدعومة",
        "sub_specialty": "Pore-scale Multiphase Flow & Subsurface Hydrogen Storage",
        "deadline": "2027-01-31 (لبدء التدريب في الربيع والصيف)",
        "leads_to_phd": "✅ بنسبة تزيد عن 85% يتحول المتدرب المتميز مباشرة إلى عقد دكتوراه وظيفي (CIFRE/IFPEN PhD) لثلاث سنوات إضافية.",
        "acceptance_difficulty": "🟢 سهلة جداً: تقبل طلبة الماستر الأوروبي (ECTS) مباشرة، واللغة الإنجليزية كافية تماماً داخل مخابر IFPEN.",
        "link": "https://www.ifpenergiesnouvelles.com/carrieres/offres-demploi-et-de-stage"
    },
    {
        "title": "Eni Curricular / Extra-Curricular Internship in Reservoir Geomodeling & CCUS",
        "institution": "Eni S.p.A. (Headquarters & R&D Labs - San Donato Milanese)",
        "country": "إيطاليا (Italy)",
        "duration": "6 أشهر (Tesi di Laurea in Azienda / Tirocinio Curriculare)",
        "monthly_stipend": "1,000 € شهرياً (Rimborso spese) + دخول مجاني لمطاعم الشركة ونقل مكوكي من ميلانو",
        "sub_specialty": "Reservoir Static/Dynamic Modeling & Carbon Capture Geomechanics",
        "deadline": "مفتوح على مدار العام (Rolling Admissions)",
        "leads_to_phd": "✅ ترشيح فوري لمنح الدكتوراه الصناعية (Dottorato Executive PNRR) بين Eni وجامعتك في إيطاليا.",
        "acceptance_difficulty": "🟢 سهلة جداً ومثالية لك: أنت طالب في إيطاليا ولديك إقامة إيطالية، وتستطيع جامعتك توقيع اتفاقية التدريب (Convenzione di Tirocinio) في 48 ساعة دون أي تعقيد فيزا.",
        "link": "https://www.eni.com/it-IT/carriere.html"
    },
    {
        "title": "KAUST VSRP Fellowship: Deep Learning for 3D Reservoir Seismic & Flow Modeling",
        "institution": "KAUST (Visiting Student Research Program - ANPER Lab)",
        "country": "المملكة العربية السعودية (Saudi Arabia)",
        "duration": "3 إلى 6 أشهر (تدريب بحثي دولي مكثف)",
        "monthly_stipend": "1,000 $ شهرياً + سكن جامعي فردي فاخر مجاناً + تذاكر طيران ذهاب وإياب وتأشيرة وتأمين صحي",
        "sub_specialty": "AI in Subsurface Geophysics & Reservoir Flow",
        "deadline": "مفتوح طوال العام (تقديم قبل 3 أشهر من تاريخ البدء المرغوب)",
        "leads_to_phd": "✅ 90% من طلبة برنامج VSRP يحصلون على قبول فوري لدكتوراه KAUST الممولة بالكامل (راتب 2,500$).",
        "acceptance_difficulty": "🟢 سهلة إلى متوسطة: تتطلب معدل ماستر تراكمي ممتاز (GPA > 3.5/4.0)، وأوراق التقديم تتم إلكترونياً بنسبة 100%.",
        "link": "https://vsrp.kaust.edu.sa/"
    },
    {
        "title": "Graduate R&D Intern: Petrel / Techlog Subsurface Analytics Software Development",
        "institution": "SLB Technology Center (Clamart - Paris / Abingdon - UK)",
        "country": "فرنسا / بريطانيا (France / UK)",
        "duration": "6 أشهر",
        "monthly_stipend": "حوالي 1,800 € إلى 2,200 € شهرياً",
        "sub_specialty": "Petrophysics, Rock Physics & Subsurface Software Engineering",
        "deadline": "2027-02-28",
        "leads_to_phd": "✅ يفتح باب التوظيف المباشر في SLB أو رعاية دكتوراه صناعية مشتركة.",
        "acceptance_difficulty": "🟡 متوسطة: تتطلب مهارات ممتازة في التحليل الفيزيائي والرياضي مع لغة برمجة (بايثون أو C++).",
        "link": "https://careers.slb.com/early-careers"
    },
    {
        "title": "Borsa di Ricerca / Research Internship in Subsurface Geophysics & CO2 Monitoring",
        "institution": "OGS - Istituto Nazionale di Oceanografia e di Geofisica Sperimentale (Trieste)",
        "country": "إيطاليا (Italy)",
        "duration": "6 إلى 12 شهراً",
        "monthly_stipend": "1,200 € إلى 1,400 € شهرياً معفى من الضرائب (Borsa di Studio)",
        "sub_specialty": "Seismic Monitoring of Geothermal Fields & Subsurface Gas Injections",
        "deadline": "2027-03-15 (حسب إعلانات معهد OGS الدورية)",
        "leads_to_phd": "✅ المعهد شريك رسمي مع جامعات إيطاليا (PoliTo, UniTS) لطرح مقاعد دكتوراه مشتركة.",
        "acceptance_difficulty": "🟢 سهلة جداً: معهد إيطالي حكومي مرموق يقدم منح بحثية مستمرة لطلبة الماستر المقيمين بإيطاليا.",
        "link": "https://www.ogs.it/it/concorsi-e-selezioni"
    }
]
