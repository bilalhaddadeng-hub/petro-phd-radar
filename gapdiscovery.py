# -*- coding: utf-8 -*-
"""gapdiscovery.py - اكتشاف فجوات جديدة تلقائياً من الأوراق الحديثة (OpenAlex، مجاني).

الفكرة: المؤلفون أنفسهم يكتبون في الملخصات عبارات مثل "remains unexplored" و"few studies" و"poorly understood".
نجمع الجمل التي تذكر ذلك من أوراق نُشرت خلال آخر ~5 أشهر في مواضيع اهتمامك، فتتجدد القائمة كلما نُشر جديد.

حدود صريحة: هذه *فجوات يصرّح بها مؤلفو ورقة واحدة*، وليست مثبتة ولا مقيّمة. قد تكون الفجوة قد سُدّت في ورقة أخرى،
أو تكون الجملة عامة. استعمل /gapcheck للتحقق من التشبّع قبل أي التزام.
"""
import logging
import re
import time
from datetime import date, timedelta
from typing import Dict, List, Optional

from gapcheck import _get, clean_query

logger = logging.getLogger(__name__)

# مواضيع المراقبة (منطق OpenAlex بالعنوان+الملخص)
DISCOVERY_TOPICS = [
    ("تخزين الهيدروجين الجوفي", '"underground hydrogen storage"', "underground hydrogen storage", ["hydrogen"]),
    ("تخزين CO2 الجيولوجي", '"CO2 storage" AND ("reservoir" OR "aquifer" OR "depleted")', "geological CO2 storage reservoir", ["co2", "carbon"]),
    ("الحرارة الجوفية والآبار", '"geothermal" AND ("reservoir" OR "wells")', "geothermal reservoir wells", ["geothermal"]),
    ("الهيدروجين الطبيعي", '("natural hydrogen" OR "geologic hydrogen" OR "white hydrogen")', "natural geologic hydrogen", ["hydrogen"]),
    ("محاكاة المكامن ومطابقة التاريخ", '("reservoir simulation" OR "history matching")', "reservoir simulation history matching", ["reservoir"]),
    ("الاسترداد المعزز EOR", '("enhanced oil recovery" OR "EOR")', "enhanced oil recovery", ["recovery", "eor"]),
    ("التدفق متعدد الأطوار في الأوساط المسامية", '"multiphase flow" AND "porous media"', "multiphase flow porous media", ["porous"]),
    ("تعلم آلي للمكامن", '("machine learning" OR "deep learning") AND ("reservoir" OR "petroleum")', "machine learning reservoir petroleum", ["reservoir", "petroleum"]),
]

TRIGGER_QUERY = ('("research gap" OR "knowledge gap" OR "remains unexplored" OR "poorly understood" OR "few studies" '
                 'OR "limited studies" OR "understudied" OR "underexplored" OR "little is known" OR "has not been" '
                 'OR "have not been" OR "remains unclear")')

_TRIGGER_RE = re.compile(
    r"(research gap|knowledge gap|remains?\s+(largely\s+)?(unexplored|unclear|unknown|poorly understood|understudied)"
    r"|(is|are|remains?)\s+(still\s+)?(poorly|not well|not fully|insufficiently)\s+(understood|explored|characteri[sz]ed|constrained)"
    r"|(few|limited|scarce)\s+(studies|experimental data|experimental studies|research|investigations)\b"
    r"|understudied|underexplored|little is known|has not been|have not been)", re.I)
# جمل تصف ما تفعله الورقة (منهج) وليست فجوة: تُستبعد
_METHOD_START = re.compile(r"^(this (study|work|paper|research)|in this|here,? we|we (propose|present|develop|investigate)|the present)\b", re.I)
_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z])")


def rebuild_abstract(inv: Optional[Dict]) -> str:
    """OpenAlex يعطي الملخص كفهرس مقلوب {كلمة: [مواضع]}؛ نعيد بناءه نصاً."""
    if not inv:
        return ""
    pos = {}
    for word, idxs in inv.items():
        for i in idxs:
            pos[i] = word
    return " ".join(pos[i] for i in sorted(pos))


def extract_gap_sentence(abstract: str) -> Optional[str]:
    """أول جملة معقولة الطول تحوي عبارة فجوة. نتجاهل جمل المنهج/النتائج بالاكتفاء بعبارات الفجوة."""
    for s in _SENT_SPLIT.split(re.sub(r"\s+", " ", abstract).strip()):
        if 50 <= len(s) <= 420 and _TRIGGER_RE.search(s) and not _METHOD_START.search(s.strip()):
            return s.strip()
    return None


def parse_discoveries(data: Optional[Dict], topic_label: str) -> List[Dict]:
    out = []
    for w in (data or {}).get("results", []):
        sent = extract_gap_sentence(rebuild_abstract(w.get("abstract_inverted_index")))
        title = (w.get("title") or "").strip()
        key = w.get("doi") or w.get("id")
        if not (sent and title and key):
            continue
        src = ((w.get("primary_location") or {}).get("source") or {}).get("display_name") or ""
        out.append({"key": key, "topic": topic_label, "sentence": sent, "title": title[:200],
                    "year": w.get("publication_year"), "date": w.get("publication_date") or "",
                    "venue": src[:80], "url": w.get("doi") or w.get("id"), "cites": w.get("cited_by_count", 0)})
    return out


def _clean_jats(txt: str) -> str:
    txt = re.sub(r"<[^>]+>", " ", txt or "")
    txt = re.sub(r"\s+", " ", txt).strip()
    return re.sub(r"^abstract\s*", "", txt, flags=re.I)


def parse_crossref(data: Optional[Dict], topic_label: str, keywords) -> List[Dict]:
    out = []
    for it in (data or {}).get("message", {}).get("items", []):
        title = ((it.get("title") or [""])[0]).strip()
        abstract = _clean_jats(it.get("abstract", ""))
        if not (title and abstract):
            continue
        hay = f"{title} {abstract}".lower()
        if keywords and not any(k in hay for k in keywords):
            continue
        sent = extract_gap_sentence(abstract)
        if not sent:
            continue
        parts = ((it.get("issued") or {}).get("date-parts") or [[None]])[0]
        y = parts[0] if parts else None
        d = "-".join(f"{int(x):02d}" if i else str(x) for i, x in enumerate(parts)) if parts and parts[0] else ""
        out.append({"key": f"https://doi.org/{it['DOI']}", "topic": topic_label, "sentence": sent, "title": title[:200],
                    "year": y, "date": d, "venue": ((it.get("container-title") or [""])[0])[:80],
                    "url": f"https://doi.org/{it['DOI']}", "cites": it.get("is-referenced-by-count", 0)})
    return out


def _crossref_fetch(simple_q: str, since: str, rows: int) -> Optional[Dict]:
    import requests
    for attempt in range(2):
        try:
            r = requests.get("https://api.crossref.org/works", timeout=40, headers={"User-Agent": "petro-phd-radar/1.0"},
                             params={"query": simple_q, "rows": rows, "select": "DOI,title,abstract,issued,container-title,is-referenced-by-count",
                                     "filter": f"from-pub-date:{since},has-abstract:true,type:journal-article"})
            if r.status_code == 200:
                return r.json()
            time.sleep(2.0)
        except (requests.RequestException, ValueError):
            time.sleep(2.0)
    return None


def discover(days: int = 150, per_topic: int = 25, topics=DISCOVERY_TOPICS) -> List[Dict]:
    """يجلب فجوات معلنة حديثة. يبدأ بـOpenAlex، وإن تعذّر (حد الطلبات) ينتقل إلى Crossref (مجاني بلا مفتاح)."""
    since = (date.today() - timedelta(days=days)).isoformat()
    found, failed, use_crossref = [], 0, False
    for label, q, simple_q, kws in topics:
        data = None
        if not use_crossref:
            data = _get({"filter": f"title_and_abstract.search:{clean_query(f'({q}) AND {TRIGGER_QUERY}')},"
                                   f"from_publication_date:{since}",
                         "sort": "publication_date:desc", "per-page": per_topic,
                         "select": "id,doi,title,publication_year,publication_date,primary_location,"
                                   "abstract_inverted_index,cited_by_count"})
            if data is None:
                use_crossref = True  # لا نهدر الوقت: OpenAlex محدود الآن، نكمل بالبديل لكل المواضيع
        if data is not None:
            found += parse_discoveries(data, label)
            continue
        cr = _crossref_fetch(simple_q, since, rows=60)
        if cr is None:
            failed += 1
            continue
        found += parse_crossref(cr, label, kws)
    logger.info(f"gap discovery: {len(found)} candidates, {failed}/{len(topics)} topics failed, crossref={use_crossref}")
    return found


def format_discovery(d: Dict, idx: int = 0, total: int = 0) -> str:
    head = f"🆕 *فجوة معلنة من ورقة حديثة* ({idx}/{total})\n" if total else "🆕 *فجوة معلنة من ورقة حديثة*\n"
    return (f"{head}المجال: {d['topic']}\n\n"
            f"«{d['sentence']}»\n\n"
            f"📄 {d['title']}\n🗓 {d.get('date') or d.get('pub_date') or d.get('year')} | {d['venue']}\n{d['url']}\n\n"
            "⚠️ مستخرجة آلياً من ملخص ورقة واحدة: ليست مثبتة ولا مقيّمة. "
            "قد تكون سُدّت في عمل آخر. تحقق بـ /gapcheck قبل أي التزام.")
