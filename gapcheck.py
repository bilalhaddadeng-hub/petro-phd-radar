# -*- coding: utf-8 -*-
"""gapcheck.py - فحص تشبّع موضوع بحثي عبر OpenAlex (مجاني، بلا مفتاح).

لا يثبت وجود فجوة. يقيس شيئين فقط: (1) كم ورقة تطابق الصياغة في العنوان/الملخص، (2) اتجاه النشر السنوي،
ويعرض أقرب الأوراق لتقرأها بنفسك. غياب التطابق قد يعني فجوة وقد يعني اختلاف الصياغة.
"""
import logging
from datetime import date
from typing import Dict, List, Optional

import requests

logger = logging.getLogger(__name__)
API = "https://api.openalex.org/works"
TIMEOUT = 30


def _get(params: Dict) -> Optional[Dict]:
    try:
        r = requests.get(API, params=params, timeout=TIMEOUT, headers={"User-Agent": "petro-phd-radar/1.0"})
        if r.status_code != 200:
            logger.warning(f"OpenAlex status {r.status_code}")
            return None
        return r.json()
    except (requests.RequestException, ValueError) as e:
        logger.warning(f"OpenAlex error: {e}")
        return None


def clean_query(q: str) -> str:
    """يمنع رموز الفلترة من كسر الاستعلام (الفاصلة والنقطتان تعنيان فلتراً جديداً في OpenAlex)."""
    return " ".join(q.replace(",", " ").replace(":", " ").replace("|", " ").split())[:150]


def parse_year_groups(data: Optional[Dict]) -> Dict[int, int]:
    if not data:
        return {}
    out = {}
    for g in data.get("group_by", []):
        try:
            out[int(g["key"])] = int(g["count"])
        except (KeyError, ValueError, TypeError):
            continue
    return out


def parse_closest(data: Optional[Dict], limit: int = 8) -> List[Dict]:
    out = []
    for w in (data or {}).get("results", [])[:limit]:
        title = (w.get("title") or "").strip()
        if not title:
            continue
        src = ((w.get("primary_location") or {}).get("source") or {}).get("display_name") or ""
        out.append({"title": title[:140], "year": w.get("publication_year"),
                    "cites": w.get("cited_by_count", 0), "venue": src[:60],
                    "url": w.get("doi") or w.get("id") or ""})
    return out


def verdict(n_recent: int) -> str:
    """حكم تقريبي على عدد الأوراق المطابقة منذ 2023؛ ليس علماً دقيقاً."""
    if n_recent == 0:
        return "⚪ لا تطابق مباشر في العنوان/الملخص. لا يثبت أنها فجوة (قد تختلف الصياغة)؛ جرّب صياغات أخرى."
    if n_recent <= 10:
        return "🟢 أعمال قريبة قليلة (≤10). اقرأها كلها قبل القرار: قد تكون فجوة حقيقية أو سبقك أحد."
    if n_recent <= 60:
        return "🟡 نشاط متوسط. تحتاج زاوية أضيق أو بيانات/منهج مختلف لتتميز."
    return "🔴 مطروق جداً. لا تبدأ إلا بميزة واضحة (بيانات حصرية أو منهج جديد فعلاً)."


def check_topic(narrow: str, broad: Optional[str] = None) -> Dict:
    narrow, broad = clean_query(narrow), clean_query(broad or "")
    y0 = date.today().year - 5
    since3 = f"{date.today().year - 3}-01-01"
    base = {"per-page": 1}
    cnt = _get({**base, "filter": f"title_and_abstract.search:{narrow},from_publication_date:{since3}"})
    rev = _get({**base, "filter": f"title_and_abstract.search:{narrow},from_publication_date:{since3},type:review"})
    years = _get({"filter": f"title_and_abstract.search:{broad or narrow},from_publication_date:{y0}-01-01",
                  "group_by": "publication_year"})
    near = _get({"search": narrow, "filter": f"from_publication_date:{y0}-01-01", "per-page": 8,
                 "select": "title,publication_year,cited_by_count,doi,id,primary_location"})
    if cnt is None and years is None and near is None:
        return {"ok": False}
    n_recent = (cnt or {}).get("meta", {}).get("count")
    return {"ok": True, "query": narrow, "broad": broad or narrow, "n_recent": n_recent,
            "n_reviews": (rev or {}).get("meta", {}).get("count"),
            "years": parse_year_groups(years), "closest": parse_closest(near)}


def format_check(res: Dict) -> str:
    if not res.get("ok"):
        return "❌ تعذّر الوصول إلى OpenAlex الآن. أعد المحاولة لاحقاً."
    thisy = date.today().year
    lines = [f"🔎 فحص التشبّع: «{res['query']}»"]
    if res["n_recent"] is not None:
        lines.append(f"• أوراق منذ {thisy - 3} تطابق الصياغة (عنوان/ملخص): {res['n_recent']}"
                     + (f"، منها مراجعات: {res['n_reviews']}" if res["n_reviews"] is not None else ""))
        lines.append(verdict(res["n_recent"]))
    yrs = {y: c for y, c in res["years"].items() if y >= thisy - 5}
    if yrs:
        lines.append(f"\n📈 نشر سنوي للمجال الأوسع «{res['broad']}»:")
        lines.append("  " + " | ".join(f"{y}{'*' if y == thisy else ''}: {c}" for y, c in sorted(yrs.items())))
        lines.append("  (* السنة الحالية ناقصة)")
    if res["closest"]:
        lines.append("\n📚 أقرب الأوراق (اقرأها قبل أي قرار):")
        for i, p in enumerate(res["closest"], 1):
            lines.append(f"{i}. {p['title']} ({p['year']}, {p['cites']} اقتباس) {p['venue']}\n   {p['url']}")
    lines.append("\n⚠️ هذا مؤشر آلي لا حكم نهائي: لا يقرأ النصوص الكاملة ولا يعرف الأوراق غير المفهرسة.")
    return "\n".join(lines)
