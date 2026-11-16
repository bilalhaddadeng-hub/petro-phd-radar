# -*- coding: utf-8 -*-
"""مجموعات وأساتذة أوروبيون في المكامن وتخزين CO2/H2 والتدفق في الأوساط المسامية.

كل معلومة هنا طابقتُها مع صفحات رسمية أو مصادر منشورة (2026-11). ما لم يثبت يُكتب صراحة
"غير مؤكد". لا رواتب ولا مواعيد ولا بريد مخمّن: الفرص تُراجع في صفحة المجموعة نفسها،
فالأساتذة لا يعلنون مقاعد ثابتة طوال العام.
"""
from typing import Dict, List

NO_EMAIL = "غير مؤكد، راجع صفحة الأستاذ الرسمية"
OPEN_NOTE = "تُعلَن المقاعد حسب المشاريع الممولة؛ راجع صفحة المجموعة وEURAXESS، وراسل الأستاذ مباشرة."


def _p(name, title, institution, country, site, projects, advice, email=NO_EMAIL, positions=OPEN_NOTE):
    return {
        "name": name, "title": title, "institution": institution, "country": country,
        "email": email, "lab_website": site, "current_projects": projects,
        "open_positions": positions, "advice_for_user": advice,
    }


TOP_PROFESSORS_RADAR: List[Dict] = [
    _p("Prof. Hadi Hajibeygi", "Subsurface Storage & Multiscale Modeling (Energi Simulation Chair)",
       "Delft University of Technology (TU Delft)", "هولندا (Netherlands)",
       "https://tudelft.nl/innovatie-impact/project-cases/subsurface-energy-storage",
       "يقود برنامج ADMIRE وAdmire Hydrogen Lab لتخزين الهيدروجين الجوفي، ويشارك في DARSim لمحاكاة المكامن، "
       "وهو Science Lead في IEA TCP 42 للتخزين الجوفي للهيدروجين. (لقبه يختلف بين المصادر: تحقق من صفحة TU Delft.)",
       "مناسب جداً لملفك إن كان لديك أساس في المحاكاة العددية أو البرمجة. الدكتوراه في هولندا وظيفة براتب نظامي."),
    _p("Dr./Prof. Denis Voskov", "Reservoir simulation, geothermal & CO2 storage (Open-DARTS)",
       "Delft University of Technology (TU Delft)", "هولندا (Netherlands)",
       "https://repository.tudelft.nl/person/academic/Person_ab9a2b39-38b3-4ead-9716-28c86c36d204",
       "مؤلف المحاكي مفتوح المصدر Open-DARTS لتخزين CO2 والحرارة الجوفية والهيدروجين وتحليل عدم اليقين. "
       "(لقبه الحالي غير مؤكد من نتائجي.)",
       "فرصة قوية إن كنت تميل إلى المحاكاة التركيبية والحرارية-التفاعلية."),
    _p("Prof. Holger Ott", "Head, Chair of Reservoir Engineering & Department Geoenergy",
       "Montanuniversität Leoben", "النمسا (Austria)",
       "https://www.dpe.ac.at/people/",
       "رئيس كرسي هندسة المكامن منذ 2016 ورئيس القسم (Geoenergy). منشورات حديثة في تخزين CO2 والهيدروجين وEOR.",
       "قوي في التدفق على مستوى المسام والعمل المخبري. تحقق من الوظائف في صفحة الكرسي وموقع الجامعة."),
    _p("Prof. Dario Viberti", "Full Professor, Reservoir Engineering (DIATI)",
       "Politecnico di Torino", "إيطاليا (Italy)",
       "https://www.diati.polito.it/en/research/areas/underground_energy_systems_energy_transition2",
       "قائد علمي لمشروع صناعي في تخزين CO2 في المكامن الناضبة والطبقات المائية، وضمن مجموعة التخزين الجوفي "
       "للهيدروجين منذ 2019. يشرف على أطروحات مع Prof. Francesca Verga.",
       "أنت في إيطاليا، فزيارة تورينو ومناقشة أطروحة أو دكتوراه ممكنة شخصياً. تظهر منح الدكتوراه في مواقع بوليتو (borse)."),
    _p("Prof. Alberto Guadagnini", "Full Professor of Hydraulic Engineering; Vice Rector for Research",
       "Politecnico di Milano", "إيطاليا (Italy)",
       "https://guadagnini.faculty.polimi.it/",
       "ينسق مجموعة MIPORE (Porous Media across scales): التدفق والنقل في الأوساط المسامية وعدم اليقين وموارد "
       "الطاقة الجوفية. حاصل على Henry Darcy Medal وInterPore Medal عام 2024.",
       "مناسب لمن يريد الجانب الإحصائي وتحليل عدم اليقين. منصبه الإداري قد يحدّ من وقته، فراسل أعضاء المجموعة أيضاً."),
    _p("Prof. Martin Blunt (مع Dr. Sam Krevor وDr. Ronny Pini)", "Chair in Petroleum Engineering",
       "Imperial College London", "بريطانيا (UK)",
       "https://www.imperial.ac.uk/a-z-research/qatar-carbonates-and-carbon-storage/research/labs/msilab/msisummary/",
       "مختبر Multi-Scale Imaging: آليات التدفق على مقياس المسام في تخزين CO2 والاحتجاز الشعري، وإشراف على أطروحات "
       "دكتوراه حديثة في هذا المجال.",
       "من أعلى المجموعات تنافساً عالمياً؛ التمويل غالباً عبر منح DTP/EPSRC أو مشاريع محددة."),
    _p("Prof. Mehran Sohrabi", "Director, Centre of Enhanced Oil Recovery and CO2 Solutions",
       "Heriot-Watt University (Institute of GeoEnergy Engineering)", "بريطانيا (UK)",
       "https://www.eor.hw.ac.uk/mehran-sohrabi/",
       "EOR وحقن CO2 للاسترداد والتخزين الجيولوجي والنفط الثقيل، مع إشراف مشترك على طلاب دكتوراه.",
       "مجال مباشر لخلفيتك في إنتاج الآبار والمكامن."),
    _p("Prof. Martin Fernø", "Professor, Reservoir Physics group", "University of Bergen", "النرويج (Norway)",
       "https://www.uib.no/en/rg/ptech",
       "يقود فريقي تخزين الهيدروجين تحت الأرض وتخزين الكربون؛ مشاريع NCS2030 (مركز النرويج لأبحاث CCS) وTime4CO2، "
       "ومنصة FluidFlower المخبرية.",
       "الدكتوراه في النرويج وظيفة براتب مرتفع وتُعلَن على Jobbnorge.", email="Martin.Ferno@uib.no"),
    _p("Prof. Carl Fredrik Berg", "Professor, Geoscience & Petroleum; PoreLab deputy director", "NTNU", "النرويج (Norway)",
       "https://ntnu.edu/physics/research/porelab",
       "PoreLab مركز تميز نرويجي (NTNU وOslo): الصخور الرقمية والتدفق على مقياس المسام وتحديد أنواع الصخور بالتعلم الآلي.",
       "مناسب إن كنت تريد التدفق المسامي والتصوير الرقمي. تُعلن الوظائف على Jobbnorge."),
    _p("Prof. Merete Vadla Madland", "Professor, Reservoir Technology (Geomechanics)", "University of Stavanger", "النرويج (Norway)",
       "https://www.uis.no/en/research/national-iorcentre-of-norway",
       "الجيوميكانيكا وتأثير حقن مياه البحر على طبقات الطباشير؛ مرتبطة بمركز IOR الوطني النرويجي. "
       "(مصادري قديمة جزئياً: تحقق من نشاطها الحالي.)",
       "مناسب للجيوميكانيكا وEOR في الكربونات."),
    _p("Prof. Martin Saar", "Professor, Geothermal Energy & Geofluids (GEG)", "ETH Zurich", "سويسرا (Switzerland)",
       "https://geg.ethz.ch/",
       "الحرارة الجوفية وCO2 فوق الحرج والهيدروجين الطبيعي. إعلانات حديثة: دكتوراه في الرنين المغناطيسي للأوساط "
       "المسامية (مفتوحة حتى الشغور عند آخر مراجعة)، وأخرى في الهيدروجين الميكانيكي-الكيميائي (قد تكون أُغلقت).",
       "التقديم عبر بوابة ETH الرسمية فقط. السلم المالي في سويسرا مرتفع."),
    _p("Prof. Leonhard Ganzer (و Dr. Birger Hagemann)", "Reservoir Engineering, Institute of Subsurface Energy Systems",
       "TU Clausthal", "ألمانيا (Germany)",
       "https://www.ite.tu-clausthal.de/en/research/subsurface-energy-and-gas-storage",
       "محاكاة المكامن وتخزين الهيدروجين تحت الأرض وحقن CO2 والحرارة الجوفية؛ مشروع HyUSPRe وسلامة إكمال الآبار في تخزين H2.",
       "ألمانيا من أوسع أسواق وظائف الدكتوراه الممولة (TV-L)."),
    _p("Prof. Rainer Helmig", "Multiphase flow in porous media (Stuttgart, status unclear)", "University of Stuttgart", "ألمانيا (Germany)",
       "https://www.iws.uni-stuttgart.de/institut/team/Helmig",
       "التدفق متعدد الأطوار في الأوساط المسامية وتخزين CO2 والهيدروجين ومحاكي DuMux. "
       "(مصادري تتضارب حول وضعه الحالي: أستاذ متقاعد أم بحثي؛ راسل مجموعة LH2/IWS.)",
       "قيمة علمية عالية في النمذجة؛ تأكد من المجموعة النشطة قبل المراسلة."),
    _p("Prof. Jesús Carrera", "Research Professor, hydrogeology & reactive transport", "IDAEA-CSIC (Barcelona)", "إسبانيا (Spain)",
       "https://www.ae-info.org/ae/User/Carrera_Ramirez_Jesus",
       "النقل التفاعلي والمشكلة العكسية، وعمل مجموعته امتد إلى تخزين CO2 (Hontomín) والصدوع. لم أجد دكتوراه "
       "محددة في تخزين الهيدروجين، وتُعلَن الوظائف عبر IDAEA وUPC.",
       "إسبانيا خيار جيد للنقل التفاعلي وتخزين الكربون؛ أرسل بريداً مباشراً.", email="jcrgeo@idaea.csic.es"),
    _p("Dr. Zoltán Turzó (رئيس القسم في صفحة قديمة)", "Petroleum Engineering, Faculty of Earth & Environmental Sciences and Engineering",
       "University of Miskolc", "المجر (Hungary)",
       "https://www.uni-miskolc.hu/en/university/organisations/faculties/faculty-of-earth-and-environmental-sciences-and-engineering/",
       "القسم الوحيد في المجر لهندسة البترول منذ 1951؛ فرق بحثية في إنتاج النفط والغاز وحفر الآبار العميقة وهجرة "
       "الهيدروكربونات. (من يرأس القسم الآن غير مؤكد.)",
       "برنامج الدكتوراه (PhD in Earth Sciences) فيه مسار مدفوع بكلفة معلنة ومسار منحة Stipendium Hungaricum؛ "
       "راجع الرسوم الفعلية قبل التقديم."),
]
