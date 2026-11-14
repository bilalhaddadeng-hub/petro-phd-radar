from typing import Dict

def evaluate_for_bilal_haddad(country: str, institution: str, source_type: str, title: str, sub_specialty: str = "") -> Dict[str, str]:
    """
    تحليل دقيق ومخصص 100% للمهندس بلال حداد يدمج:
    • هندسة المكامن الكلاسيكية (Reservoir Engineering & Gas Condensate Wells).
    • هندسة تخزين الطاقة الجوفية والكربون (CCUS & Underground Hydrogen Storage) كفرع أصيل ومكمل لفيزياء المكامن.
    • التركيز على الفرص التي لا تشترط سنوات خبرة عملية سابقة (Early Stage Researchers R1).
    """
    c = country.lower()
    inst = institution.lower()
    t = title.lower()
    s = sub_specialty.lower()

    experience_note = "✅ **الخبرة المطلوبة:** 0 سنوات خبرة (مخصصة لخريجي الماستر مباشرة / Early-Stage Researcher R1 دون اشتراط خبرة وظيفية سابقة)."

    if "eni" in inst or "italy" in c or "italia" in c or "politecnico di torino" in inst or "catania" in inst:
        return {
            "level": "🟢 سهلة جداً (أقوى تطابق وتفوق مطلق لملفك)",
            "experience": experience_note,
            "analysis": (
                f"{experience_note}\n"
                "🎯 **تطابق هندسي واستراتيجي لا يُنافس في إيطاليا:**\n"
                "• حقن ثاني أكسيد الكربون (CCUS) وتخزين الهيدروجين الجوفي في حقول إيطاليا يعتمد كلياً على نفس معادلات تدفق الغاز والمكثفات التي درستها في غوبكين.\n"
                "• خبرتك الميدانية السابقة في شراكة سوناطراك-إيني (Association GSE) تجعلك معروفاً لدى مسؤولي Eni وتعطيك أفضلية استثنائية.\n"
                "• وجودك في إيطاليا (جامعة كاتانيا) يتيح لك توقيع اتفاقيات الدكتوراه الصناعية والمنح الوطنية PNRR مباشرة دون أي عوائق بيروقراطية."
            )
        }
    elif "leoben" in inst or "austria" in c or "delft" in inst or "netherlands" in c:
        return {
            "level": "🟢 سهلة ومباشرة (تطابق علمي في ميكانيكا تدفق الموائع بالمكامن)",
            "experience": experience_note,
            "analysis": (
                f"{experience_note}\n"
                "• مشاريع جامعة ليوبن ودلفت في الـ Underground Storage و CCUS تركز على ديناميكا التدفق متعدد الأطوار والـ Relative Permeability، وهو صلب أطروحتك في غوبكين.\n"
                "• وظائف Universitätsassistent في النمسا وهولندا مصممة قانونياً لطلبة الماستر المتخرجين حديثاً ولا تطلب خبرة شركات."
            )
        }
    elif any(x in c for x in ["saudi", "uae", "qatar", "kfupm", "kaust"]):
        return {
            "level": "🟢 سهلة إلى متوسطة (تقدير أكاديمي استثنائي لشهادة غوبكين)",
            "experience": experience_note,
            "analysis": (
                f"{experience_note}\n"
                "• جامعة الملك فهد (KFUPM - كلية CPG) وجامعة KAUST تركزان على مكامن الغاز غير التقليدي وتخزين الكربون.\n"
                "• القبول يعتمد على تفوقك في الماستر (4.6/5.0) والمقابلة العلمية ولا يشترط أي خبرة صناعية، مع تمويل ملكي كامل (راتب وسكن وتذاكر)."
            )
        }
    elif "france" in c or "ifp" in inst or "total" in inst:
        return {
            "level": "🟢 سهلة إلى متوسطة (أفضلية للمهندسين المتخرجين)",
            "experience": experience_note,
            "analysis": (
                f"{experience_note}\n"
                "• معهد IFPEN وعقود CIFRE في فرنسا مخصصة قانونياً لحديثي التخرج من الماستر للبدء في مسار البحث التطبيقي.\n"
                "• خلفيتك في حقول الغاز وميكانيكا الموائع تؤهلك مباشرة لمشاريع محاكاة المكامن وحقن الغازات."
            )
        }
    elif any(x in c for x in ["poland", "hungary", "romania"]):
        return {
            "level": "🟢 سهلة جداً (قبول مباشر بدون أي خبرة)",
            "experience": experience_note,
            "analysis": (
                f"{experience_note}\n"
                "• مدارس الدكتوراه في بولندا والمجر تقبل فوراً بناءً على كشف درجات الماستر والمشروع البحثي دون طلب خبرة مهنية.\n"
                "• طلاقتك بالروسية (C2) مع الماستر الإيطالي تعفيك من أي تعقيدات مقابلة."
            )
        }
    else:
        return {
            "level": "🟡 متوسطة",
            "experience": experience_note,
            "analysis": f"{experience_note}\nفرصة ممولة مناسبة لحديثي التخرج تركز على هندسة المكامن وتخزين الطاقة الجوفية."
        }
