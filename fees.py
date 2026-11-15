# -*- coding: utf-8 -*-
"""عرض الرسوم بصدق: لا نعرض رقماً غير موثّق كحقيقة.

الأرقام في الكتالوج مكتوبة يدوياً وقد تكون قديمة أو خاطئة (مثلاً "0 €" لرسوم
تقديم فعلية 30 €)، لذلك تُعرض كتقدير مع طلب التحقق من الصفحة الرسمية.
"""
import re

UNKNOWN = "غير مؤكدة، راجع الصفحة الرسمية"
_ZERO_RE = re.compile(r"^\s*0+([.,]0+)?\s*(€|\$|£|eur|usd|gbp|pln|nok|aed|rm|r\$)?\b", re.I)
_AMOUNT_RE = re.compile(r"\d")
_GENERIC = {"", "رسوم إدارية قياسية", "راجع الإعلان", "غير محدد", "none", "n/a"}


def display_registration_fee(value) -> str:
    """رسوم التسجيل/التقديم: الصفر المكتوب يدوياً لا يُعتمد أبداً."""
    v = (value or "").strip()
    if v.lower() in _GENERIC:
        return UNKNOWN
    if v == "راجع الإعلان":
        return v
    if _ZERO_RE.match(v) or not _AMOUNT_RE.search(v):
        # "0 €" أو "رمزية" أو "مغطاة": ادّعاء غير موثّق
        return f"{UNKNOWN} (قد توجد رسوم تقديم أو تسجيل)"
    return f"≈ {v} (تقدير، تحقق من الصفحة الرسمية)"


def display_tuition_fee(value) -> str:
    """رسوم الدراسة: الإعفاء مرتبط بشروط التمويل لا بالجامعة وحدها."""
    v = (value or "").strip()
    if v.lower() in _GENERIC:
        return UNKNOWN
    if v == "راجع الإعلان":
        return v
    if _AMOUNT_RE.search(v) and not _ZERO_RE.match(v):
        return f"≈ {v} (تقدير، تحقق من الصفحة الرسمية)"
    return f"{v} (حسب شروط التمويل المعلنة)"


def display_experience(value) -> str:
    v = (value or "").strip()
    return v if v else "غير محددة، راجع الإعلان"
