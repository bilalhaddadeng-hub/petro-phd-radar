# -*- coding: utf-8 -*-
"""تدقيق الكتالوج اليدوي: ما لم يُتحقق منه من الصفحة الرسمية لا يُعرض كحقيقة.

تمت مقارنة روابط الكتالوج بمحتوى صفحاتها (2026-11). النتيجة: عناوين ورواتب ومواعيد
كثيرة كانت مكتوبة يدوياً ولا تطابق الصفحة، لذلك:
 - OVERRIDES: حقول صُحّحت من نص الصفحة نفسها.
 - بقية العناصر: الراتب يُوسَم تقديرياً، والموعد غير الموثّق يصبح "راجع الصفحة".
"""
from copy import deepcopy
from typing import Dict, List

CHECK = "راجع الصفحة الرسمية"
EST = "≈ "
EST_NOTE = " (تقدير غير موثّق)"

# المفتاح: جزء من الرابط. القيم المصحّحة مأخوذة من الصفحة المرتبطة.
OVERRIDES: Dict[str, Dict] = {
    "uni-miskolc.hu": {
        "title": "PhD in Earth Sciences (Petroleum & Gas), University of Miskolc: intake 2027/28",
        "tuition_fee": "3,500 € لكل فصل للمسار المدفوع؛ 0 فقط لمن يحصل على منحة (مثل Stipendium Hungaricum)",
        "registration_fee": "150 € رسوم تقديم (حسب صفحة الجامعة)",
        "deadline": CHECK,
    },
    "workinsouthholland.nl": {
        "title": "PhD Position Process-Based Fluvial Models at (Sub)Reservoir Scale (TU Delft)",
        "sub_specialty": "نماذج رسوبية نهرية على مقياس المكمن الفرعي",
        "monthly_salary": "2,770 € في السنة الأولى حتى 3,539 € في الرابعة، إجمالي شهرياً (حسب الإعلان)",
        "tuition_fee": "لا رسوم دراسة (عقد موظف)",
        "registration_fee": "لا تنطبق (عقد توظيف)",
        "deadline": CHECK,
    },
    "tno.nl/en/careers": {
        "title": "Starter Scientist in Materials for Hydrogen Carriers (TNO, Delft)",
        "sub_specialty": "مواد لحوامل الهيدروجين: ليست تخصص مكامن مباشرة",
        "monthly_salary": "3,533 € إلى 5,047 € إجمالي شهرياً (حسب الإعلان)",
        "deadline": "2026-11-22",
    },
    "gfz.de/en/career": {
        "title": "Student / Scientific Assistant, Project World Stress Map (GFZ)",
        "sub_specialty": "مساعد بحث لمشروع World Stress Map: ليست وظيفة دكتوراه",
        "monthly_salary": "بالساعة: 15.20 € (بدون بكالوريوس) أو 15.81 € (ببكالوريوس) إجمالي (حسب الإعلان)",
        "deadline": CHECK,
    },
    "halliburton.com": {  # كان مرتبطاً بـ Resoptima خطأً
        "link": "https://resoptima.com/",
        "deadline": CHECK,
        "monthly_salary": "≈ حوالي 45,000 NOK شهرياً (تقدير غير موثّق)",
        "application_method": "عبر الموقع الرسمي للشركة (تحقق من صفحة الوظائف)",
    },
}

_GENERIC_DEADLINES = ("مفتوح", "راجع", "غير")


def _estimate(value: str) -> str:
    v = (value or "").strip()
    if not v or v.startswith(EST) or "حسب الإعلان" in v or "غير موثّق" in v:
        return v or CHECK
    return f"{EST}{v}{EST_NOTE}"


def apply_audit(items: List[Dict]) -> List[Dict]:
    out = []
    for raw in items:
        it = deepcopy(raw)
        override = next((o for k, o in OVERRIDES.items() if k in it.get("link", "")), None)
        verified = bool(override)
        if override:
            it.update(override)
        if not verified:
            it["monthly_salary"] = _estimate(it.get("monthly_salary", ""))
            dl = it.get("deadline", "")
            if dl[:2] == "20":  # موعد ISO مكتوب يدوياً وغير موثّق
                it["deadline"] = CHECK
        out.append(it)
    return out
