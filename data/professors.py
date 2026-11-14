from typing import List, Dict

# قاعدة بيانات نخبة الأساتذة ورؤساء المخابر في هندسة البترول والطاقة الجوفية
# (ممن لديهم ميزانيات Horizon Europe / ERC / مشاريع صناعية جارية ويبحثون دائماً عن مرشحين)

TOP_PROFESSORS_RADAR: List[Dict] = [
    {
        "name": "Prof. Holger Ott",
        "title": "Head of Chair of Reservoir Engineering",
        "institution": "Montanuniversität Leoben (DGE - Department of Geoenergy)",
        "country": "النمسا (Austria)",
        "email": "holger.ott@unileoben.ac.at",
        "lab_website": "https://geoenergy.engineering/reservoir-engineering/",
        "current_projects": "مشاريع ممولة من OMV والاتحاد الأوروبي حول حقن الرغوة الذكية (Smart Foams) وتخزين الهيدروجين الجوفي ومحاكاة موائع المكامن.",
        "open_positions": "مقاعد دكتوراه دورية وظيفية (Universitätsassistent) براتب ~2,450€ صافي.",
        "advice_for_user": "يبحث دوماً عن مهندسي مكامن يتقنون المحاكاة الرقمية أو العمل المخبري. شهادتك الإيطالية ECTS معتمدة فوراً في النمسا دون أي بيروقراطية."
    },
    {
        "name": "Prof. Hadi Hajibeygi",
        "title": "Professor of Geoscience & Engineering (Subsurface Energy Storage)",
        "institution": "Delft University of Technology (TU Delft)",
        "country": "هولندا (Netherlands)",
        "email": "H.Hajibeygi@tudelft.nl",
        "lab_website": "https://www.tudelft.nl/citg/over-faculteit/afdelingen/geoscience-engineering",
        "current_projects": "قائد مشروع ADMIRE ومشروع ELEGANCY (تخزين الهيدروجين والكربون في المكامن الناضبة وحسابات التدفق المتعدد الأطوار).",
        "open_positions": "مقاعد دكتوراه وظائف بحثية حكومية (PhD Employee) برواتب تبدأ من 2,770€ وتصل إلى 3,539€ شهرياً.",
        "advice_for_user": "يركز على النمذجة الرياضية (Multiscale Modeling). إذا كان الماستر الإيطالي خاصتك يركز على المحاكاة أو البرمجة (Python/C++/Matlab)، فهذه الوجهة رقم 1 لك."
    },
    {
        "name": "Prof. Laura Valentina & Prof. Dario Viberti",
        "title": "Professors of Reservoir Engineering & Deep Georesources",
        "institution": "Politecnico di Torino (DIATI Department)",
        "country": "إيطاليا (Italy)",
        "email": "dario.viberti@polito.it",
        "lab_website": "https://www.diati.polito.it/en/research/research_groups/georesources_and_geomechanics",
        "current_projects": "شراكات حصرية ضخمة مع عملاق الطاقة الإيطالي ENI في مجال مراقبة وضغط المكامن وتخزين ثاني أكسيد الكربون بحقول شمال إيطاليا والريف الإيطالي والبحر الأدرياتيكي.",
        "open_positions": "منح PNRR الوطنية + منح دكتوراه صناعية ممولة من ENI بمرتبات 1,250€-1,400€ شهرياً (+50% بالخارج).",
        "advice_for_user": "أقوى ورقة رابحة في مسارك: أنت في إيطاليا وتستطيع حجز موعد وزيارة مكتب الأستاذ في تورينو شخصياً لمناقشة أطروحة الماستر والدكتوراه القادمة!"
    },
    {
        "name": "Prof. Alberto Guadagnini",
        "title": "Head of Department of Civil and Environmental Engineering",
        "institution": "Politecnico di Milano (PoliMi)",
        "country": "إيطاليا (Italy)",
        "email": "alberto.guadagnini@polimi.it",
        "lab_website": "https://www.dica.polimi.it/",
        "current_projects": "مشاريع أوروبية ودولية في التدفق العشوائي في الأوساط المسامية (Stochastic Multiphase Flow & Uncertainty Quantification).",
        "open_positions": "منح دكتوراه بحثية ممولة من ميزانيات الاتحاد الأوروبي ووزارة الجامعات MUR.",
        "advice_for_user": "بما أنك تدرس في إيطاليا، التقديم على PoliMi يعتبر انتقالاً داخلياً سلساً، وتقدير الماستر الإيطالي لديهم مباشر."
    },
    {
        "name": "Prof. Hussein Hoteit",
        "title": "Professor of Petroleum Engineering & Subsurface Energy Systems",
        "institution": "KAUST (King Abdullah University of Science and Technology)",
        "country": "المملكة العربية السعودية (Saudi Arabia)",
        "email": "hussein.hoteit@kaust.edu.sa",
        "lab_website": "https://anper.kaust.edu.sa/",
        "current_projects": "مركز ANPER (أبحاث المكامن المتقدمة وتخزين الطاقة، أرامكو السعودية ومشاريع الذكاء الاصطناعي في هندسة البترول).",
        "open_positions": "منحة زمالة دكتوراه كاملة 100%: راتب 2,000$ - 2,500$ شهرياً + سكن فيلا فاخر مجاني + تغطية طبية وسفر.",
        "advice_for_user": "يرحب جداً بالمهندسين المتميزين من شمال أفريقيا وخريجي الجامعات التقنية الإيطالية. يركز على الجمع بين علوم البيانات وهندسة المكامن."
    },
    {
        "name": "Prof. Eric Mackay & Prof. Sebastian Geiger",
        "title": "Chairs of GeoEnergy Engineering",
        "institution": "Heriot-Watt University (Institute of GeoEnergy Engineering - IGE)",
        "country": "بريطانيا (United Kingdom)",
        "email": "eric.mackay@hw.ac.uk",
        "lab_website": "https://www.hw.ac.uk/uk/schools/energy-geoscience-infrastructure-society/research/ige.htm",
        "current_projects": "تحالفات أبحاث تدفق المكامن مع شركات بريطانية وأوروبية (Equinor, Shell, BP, TotalEnergies).",
        "open_positions": "مقاعد EPSRC ومنح صناعية Industrial Studentships.",
        "advice_for_user": "المعهد هو الأقدم والأعرق في أوروبا في هندسة البترول (سابقاً Institute of Petroleum Engineering). التواصل معهم بمقترح CCUS يضمن تفاعلاً سريعاً."
    }
]
