# -*- coding: utf-8 -*-
"""gapcheck.py - فحص تشبّع موضوع بحثي عبر OpenAlex (مجاني، بلا مفتاح).

لا يثبت وجود فجوة. يقيس شيئين فقط: (1) كم ورقة تطابق الصياغة في العنوان/الملخص، (2) اتجاه النشر السنوي،
ويعرض أقرب الأوراق لتقرأها بنفسك. غياب التطابق قد يعني فجوة وقد يعني اختلاف الصياغة.
"""
import logging
import os
import threading
import time
from datetime import date
from typing import Dict, List, Optional

import requests

logger = logging.getLogger(__name__)
API = "https://api.openalex.org/works"
TIMEOUT = 30


_LOCK = threading.Lock()
_LAST = [0.0]
MIN_GAP = 0.4  # ثانية بين الطلبات: الميزانية المجانية المشتركة تُستنفد بسرعة بدون تهدئة


def _throttle():
    with _LOCK:
        wait = MIN_GAP - (time.time() - _LAST[0])
        if wait > 0:
            time.sleep(wait)
        _LAST[0] = time.time()


def _get(params: Dict) -> Optional[Dict]:
    key = os.environ.get("OPENALEX_API_KEY", "").strip()
    if key:
        params = {**params, "api_key": key}  # مفتاح مجاني اختياري من openalex.org/settings/api
    for attempt in range(3):
        try:
            _throttle()
            r = requests.get(API, params=params, timeout=TIMEOUT, headers={"User-Agent": "petro-phd-radar/1.0"})
            if r.status_code == 429 and attempt < 2:  # حد المعدل: انتظر ثم أعد
                time.sleep(2.0 * (attempt + 1))
                continue
            if r.status_code != 200:
                logger.warning(f"OpenAlex status {r.status_code}")
                return None
            return r.json()
        except (requests.RequestException, ValueError) as e:
            logger.warning(f"OpenAlex error: {e}")
            return None
    return None


def clean_query(q: str) -> str:
    """يمنع رموز الفلترة من كسر الاستعلام (الفاصلة والنقطتان تعنيان فلتراً جديداً في OpenAlex)."""
    return " ".join(q.replace(",", " ").replace(":", " ").replace("|", " ").split())[:800]


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
    sel = "title,publication_year,cited_by_count,doi,id,primary_location"
    near = _get({"filter": f"title_and_abstract.search:{narrow},from_publication_date:{y0}-01-01",
                 "sort": "cited_by_count:desc", "per-page": 8, "select": sel})
    fuzzy = False
    if not (near or {}).get("results"):  # لا تطابق حرفي: نعرض الأقرب تقريباً وننبّه
        near = _get({"search": narrow, "filter": f"from_publication_date:{y0}-01-01", "per-page": 8, "select": sel})
        fuzzy = True
    if cnt is None and years is None and near is None:
        return {"ok": False}
    n_recent = (cnt or {}).get("meta", {}).get("count")
    return {"ok": True, "query": narrow, "broad": broad or narrow, "n_recent": n_recent,
            "n_reviews": (rev or {}).get("meta", {}).get("count"),
            "years": parse_year_groups(years), "closest": parse_closest(near), "fuzzy": fuzzy}


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


# ------------------------------ تقييم موضوعي بالأرقام ------------------------------
import concurrent.futures

import json
from pathlib import Path

CACHE_TTL = 7 * 24 * 3600  # الأعداد تتغير ببطء: أسبوع كافٍ ويخفف الحمل عن الميزانية المجانية
CACHE_FILE = Path(os.environ.get("GAP_CACHE_FILE") or (Path(os.environ.get("DB_PATH", "phd_radar.db")).parent / "gap_cache.json"))
_CACHE: Dict[str, tuple] = {}


def _load_cache():
    try:
        raw = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        _CACHE.update({k: (float(v[0]), v[1]) for k, v in raw.items()})
    except (OSError, ValueError, TypeError, IndexError):
        pass


def _save_cache():
    try:
        CACHE_FILE.write_text(json.dumps({k: list(v) for k, v in _CACHE.items()}), encoding="utf-8")
    except OSError as e:
        logger.debug(f"gap cache not saved: {e}")


_load_cache()


def count_recent(q: str, years: int = 3, cached_only: bool = False) -> Optional[int]:
    """عدد أوراق title+abstract المطابقة منذ N سنوات، مخزَّن على القرص أسبوعاً (يعمل بلا مفتاح)."""
    q = clean_query(q)
    key = f"{years}|{q}"
    hit = _CACHE.get(key)
    if hit and time.time() - hit[0] < CACHE_TTL:
        return hit[1]
    if cached_only:
        return hit[1] if hit else None  # قديم أفضل من لا شيء حين لا نريد استعلاماً
    since = f"{date.today().year - years}-01-01"
    d = _get({"filter": f"title_and_abstract.search:{q},from_publication_date:{since}", "per-page": 1})
    n = (d or {}).get("meta", {}).get("count")
    if n is not None:
        _CACHE[key] = (time.time(), n)
        _save_cache()
    elif hit:
        return hit[1]
    return n


def warm_cache(gaps: List[Dict], budget_s: float = 600.0) -> int:
    """مهمة خلفية بطيئة تملأ الذاكرة المؤقتة لكل الفجوات، فيصبح /gaprank فورياً دون مفتاح."""
    t0, done = time.time(), 0
    for g in gaps:
        if time.time() - t0 > budget_s:
            break
        before = _CACHE.get(f"3|{clean_query(g['query'])}")
        if before and time.time() - before[0] < CACHE_TTL:
            continue
        if count_recent(g["query"]) is not None:
            done += 1
    return done


DATA_PTS = {"none": 2.0, "public": 1.5, "partner": -1.0, "lab": -2.0}
CROWD_PTS = {"low": 2.0, "medium": 0.5, "high": -1.5}


def live_crowd_points(n: Optional[int]) -> Optional[float]:
    """نقاط الازدحام من عدد الأوراق المطابقة فعلاً. الصفر لا يعني فجوة مؤكدة فنكافئه بحذر."""
    if n is None:
        return None
    if n == 0:
        return 0.5
    if n <= 10:
        return 1.5
    if n <= 60:
        return 0.5
    if n <= 200:
        return -0.5
    return -1.5


def priority(g: Dict, n_recent: Optional[int] = None) -> float:
    """درجة أولوية من 0 تقريباً إلى 11: سهولة (حتى 5) + بيانات (حتى 2) + ازدحام (حتى 2) + ملاءمة لك (حتى 2).
    إن وُجد عدد حي استُعمل بدل تقدير الازدحام الأولي. هي أداة ترتيب وليست تنبؤاً بالقبول."""
    crowd = live_crowd_points(n_recent)
    if crowd is None:
        crowd = CROWD_PTS[g["crowd"]]
    return round((6 - g["difficulty"]) + DATA_PTS[g["data"]] + crowd + g["fit"], 1)


def rank_gaps(gaps: List[Dict], live: bool = True) -> List[Dict]:
    """يرتّب الفجوات. يعتمد على الذاكرة المؤقتة أولاً؛ ويجلب الناقص ضمن ميزانية وقت 40 ثانية فقط."""
    counts: Dict[int, Optional[int]] = {g["id"]: None for g in gaps}
    if live:
        t0 = time.time()
        for g in gaps:
            counts[g["id"]] = count_recent(g["query"], cached_only=(time.time() - t0 > 40))
    out = [{**g, "n_recent": counts[g["id"]], "score": priority(g, counts[g["id"]])} for g in gaps]
    return sorted(out, key=lambda x: -x["score"])


def build_matrix(methods, apps) -> Dict:
    """عدد الأوراق لكل تقاطع طريقة×تطبيق منذ 3 سنوات. الخلايا القليلة مع هوامش كبيرة مرشحة لفجوات."""
    cells = [(m, a) for m in methods for a in apps]
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
        nums = list(ex.map(lambda c: count_recent(f"{c[0][1]} AND {c[1][1]}"), cells))
    return {(m[0], a[0]): n for (m, a), n in zip(cells, nums)}


def format_matrix(methods, apps, grid: Dict) -> str:
    head = "method / app".ljust(24) + "".join(a[0][:10].rjust(11) for a in apps)
    rows = [head]
    empty = []
    for m in methods:
        vals = [grid.get((m[0], a[0])) for a in apps]
        rows.append(m[0][:23].ljust(24) + "".join(("?" if v is None else str(v)).rjust(11) for v in vals))
        for a, v in zip(apps, vals):
            if v is not None and v <= 5:
                empty.append(f"{m[0]} × {a[0]} ({v})")
    txt = "🧮 تقاطع الطرق والتطبيقات (أوراق منذ 3 سنوات، عنوان/ملخص)\n```\n" + "\n".join(rows) + "\n```"
    if empty:
        txt += "\n\n🔍 خلايا شبه فارغة (≤5): " + "؛ ".join(empty)
    txt += ("\n\n⚠️ خلية فارغة لا تعني فجوة تلقائياً: قد لا يوجد سبب علمي للجمع بينهما أو الصياغة تختلف. "
            "هي أماكن تستحق قراءة أعمق، لا استنتاجات.")
    return txt
