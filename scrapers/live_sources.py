# -*- coding: utf-8 -*-
"""
scrapers/live_sources.py - قناص الفرص الحي.

يقرأ إعلانات حقيقية من مصادر عامة (jobs.ac.uk, EURAXESS) ويصفّيها محلياً بالكلمات المفتاحية،
فيلتقط أي جامعة أو شركة جديدة دون الاعتماد على قائمة مكتوبة يدوياً.
كل مصدر معزول: فشل مصدر لا يوقف الباقي، وحالته تُرجَع في التقرير.
"""
import concurrent.futures
import logging
import re
from datetime import date, datetime, timedelta
from typing import Callable, Dict, List, Optional, Tuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

# مواضيع الاهتمام (أي واحدة تكفي ليُعتبر الإعلان ذا صلة)
TOPIC_TERMS = [
    "reservoir", "petroleum", "oil and gas", "oil & gas", "hydrocarbon", "ccus", "ccs ", "carbon capture",
    "carbon storage", "co2 storage", "co2 sequestration", "co₂", "subsurface", "geo-energy", "geoenergy",
    "hydrogen storage", "underground hydrogen", "geothermal", "geomechanic", "porous media", "multiphase",
    "enhanced oil recovery", " eor ", "drilling", "petrophysic", "well testing", "natural gas",
    "fluid flow in", "caprock", "carbon sequestration", "energy storage in", "geological storage",
]
# أنواع الفرص المقبولة (دكتوراه / تدريب / باحث مبتدئ)
LEVEL_TERMS = [
    "phd", "ph.d", "doctoral", "doctorate", "studentship", "dottorato", "doctorat", "thesis", "internship",
    "intern ", "trainee", "graduate", "early stage researcher", "esr", "research assistant", "junior",
    "fellowship", "msc project", "master project", "stage ",
]
EXCLUDE_TERMS = ["senior ", "head of", "professor of", "associate professor", "full professor", "chair of", "director"]

SEARCH_QUERIES = [
    "reservoir engineering", "petroleum engineering", "CCUS", "CO2 storage", "carbon capture storage",
    "hydrogen storage", "geothermal", "geomechanics", "porous media", "enhanced oil recovery",
    "drilling engineering", "subsurface", "oil and gas", "multiphase flow", "petrophysics",
]


class SourceSkipped(Exception):
    """مصدر معطّل بإعداد ناقص (ليس عطلاً)."""


def _get(url: str, params: Optional[dict] = None, timeout: int = 20) -> Optional[requests.Response]:
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=timeout)
        return r if r.status_code == 200 else None
    except requests.RequestException as e:
        logger.warning(f"live fetch failed {url}: {e}")
        return None


def parse_closing_date(text: str, today: Optional[date] = None) -> Optional[str]:
    """'21 Dec' أو '21 December 2026' -> 'YYYY-MM-DD' (يستنتج السنة القادمة عند غيابها)."""
    today = today or date.today()
    m = re.search(r"(\d{1,2})\s+([A-Za-z]{3,9})\.?(?:\s+(\d{4}))?", text or "")
    if not m:
        return None
    day, mon, year = int(m.group(1)), m.group(2)[:3].title(), m.group(3)
    try:
        month = datetime.strptime(mon, "%b").month
        d = date(int(year) if year else today.year, month, day)
        if not year and d < today - timedelta(days=30):
            d = date(today.year + 1, month, day)
        return d.isoformat()
    except ValueError:
        return None


def relevance(title: str, snippet: str = "") -> Tuple[int, bool]:
    """(درجة الصلة بالموضوع، هل المستوى مناسب)."""
    text = f" {title} {snippet} ".lower()
    title_l = f" {title} ".lower()
    score = sum(2 if t in title_l else 1 for t in TOPIC_TERMS if t in text)
    level_ok = any(t in text for t in LEVEL_TERMS) and not any(t in title_l for t in EXCLUDE_TERMS)
    return score, level_ok


def guess_source_type(title: str, employer: str) -> str:
    t, e = title.lower(), employer.lower()
    if any(k in t for k in ("intern", "stage ", "thesis", "trainee")):
        return "INTERNSHIP_RD"
    if any(k in e for k in ("ltd", "inc", "gmbh", "plc", "s.p.a", "energies", "petro", "oil", "group", "consult")):
        return "COMPANY_INTERNAL"
    if any(k in e for k in ("institute", "centre", "center", "helmholtz", "cnrs", "survey", "laborator")):
        return "INSTITUTE"
    return "UNIVERSITY"


def _make(title, link, employer, location, deadline, snippet, source) -> Dict:
    return {
        "title": re.sub(r"\s+", " ", title).strip(),
        "link": link,
        "institution": employer or "جهة غير محددة",
        "country": location or "دولي",
        "source_type": guess_source_type(title, employer or ""),
        "sub_specialty": (snippet[:120] or title)[:120],
        "deadline": deadline or "مفتوح حتى ملء الشواغر",
        "is_funded": "حسب الإعلان",
        "monthly_salary": "راجع الإعلان",
        "tuition_fee": "راجع الإعلان",
        "registration_fee": "راجع الإعلان",
        "seats": "1 مقعد",
        "application_method": f"عبر صفحة الإعلان الأصلية ({source})",
        "key_requirements": f"🔎 فرصة التُقطت تلقائياً من {source} — راجع الإعلان الرسمي للتفاصيل والشروط.",
        "category": "LIVE",
        "_source": source,
    }


# ----------------------------- jobs.ac.uk -----------------------------
def parse_jobsac(html: str) -> List[Dict]:
    soup = BeautifulSoup(html, "html.parser")
    out = []
    for block in soup.select("div.j-search-result__result"):
        a = block.select_one("div.j-search-result__text a[href]")
        if not a:
            continue
        employer = (block.select_one(".j-search-result__employer") or block).get_text(" ", strip=True) if block.select_one(".j-search-result__employer") else ""
        dept = block.select_one(".j-search-result__department")
        loc = re.search(r"Location:\s*([^\n]+)", block.get_text("\n", strip=True))
        exp = block.select_one(".j-search-result__date--blue")
        text = block.get_text(" ", strip=True)
        out.append(_make(a.get_text(" ", strip=True), urljoin("https://www.jobs.ac.uk", a["href"]), employer,
                         loc.group(1).strip() if loc else "UK", parse_closing_date(exp.get_text() if exp else ""),
                         f"{dept.get_text(' ', strip=True) if dept else ''} {text}", "jobs.ac.uk"))
    return out


def fetch_jobsac() -> List[Dict]:
    def one(q):
        r = _get("https://www.jobs.ac.uk/search/", {"keywords": q, "sortOrder": 1, "pageSize": 50})
        return parse_jobsac(r.text) if r else None

    results, failures = [], 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        for res in ex.map(one, SEARCH_QUERIES):
            if res is None:
                failures += 1
            else:
                results += res
    if failures == len(SEARCH_QUERIES):
        raise RuntimeError("jobs.ac.uk unreachable")
    return results


# ------------------------------ EURAXESS ------------------------------
def parse_euraxess(html: str) -> List[Dict]:
    soup = BeautifulSoup(html, "html.parser")
    out = []
    for art in soup.select("article"):
        a = art.select_one("h3 a[href*='/jobs/'], h2 a[href*='/jobs/']")
        if not a:
            continue
        text = art.get_text(" ", strip=True)
        org = art.select_one("a[href*='/partnering/organisations/']")
        deadline = re.search(r"(?:Application Deadline|Deadline)[:\s]*(\d{1,2}\s+\w+\s+\d{4})", text)
        loc = re.search(r"Work Locations?:\s*([^:]{0,60}?)(?:\s+Researcher Profile|\s+Funding|$)", text)
        out.append(_make(a.get_text(" ", strip=True), urljoin("https://euraxess.ec.europa.eu", a["href"]),
                         org.get_text(" ", strip=True) if org else "", loc.group(1).strip() if loc else "Europe",
                         parse_closing_date(deadline.group(1)) if deadline else None, text, "EURAXESS"))
    return out


def fetch_euraxess(pages: int = 80) -> List[Dict]:
    # EURAXESS لا يطبّق فلتر الكلمات من الرابط، لذا نقرأ أحدث الصفحات ونصفّي محلياً
    def one(p):
        r = _get("https://euraxess.ec.europa.eu/jobs/search", {"page": p})
        return parse_euraxess(r.text) if r else None

    results, failures = [], 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        for res in ex.map(one, range(pages)):
            if res is None:
                failures += 1
            else:
                results += res
    if failures == pages:
        raise RuntimeError("EURAXESS unreachable")
    return results


# ------------------------------ Arbeitnow (شركات ألمانيا/أوروبا) ------------------------------
def parse_arbeitnow(data: dict) -> List[Dict]:
    out = []
    for d in data.get("data", []):
        text = BeautifulSoup(d.get("description", "") or "", "html.parser").get_text(" ", strip=True)[:600]
        out.append(_make(d.get("title", ""), d.get("url", ""), d.get("company_name", ""),
                         d.get("location", "Europe"), None, f"{' '.join(d.get('tags', []))} {text}", "Arbeitnow"))
    return out


def fetch_arbeitnow(pages: int = 6) -> List[Dict]:
    def one(p):
        r = _get("https://www.arbeitnow.com/api/job-board-api", {"page": p})
        try:
            return parse_arbeitnow(r.json()) if r else None
        except ValueError:
            return None

    results, failures = [], 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        for res in ex.map(one, range(1, pages + 1)):
            if res is None:
                failures += 1
            else:
                results += res
    if failures == pages:
        raise RuntimeError("Arbeitnow unreachable")
    return results


# ------------------- لوحات توظيف الشركات المفتوحة (Greenhouse / Lever) -------------------
# واجهات JSON عامة مخصصة للقراءة الآلية. أضف شركات جديدة بصيغة "greenhouse:token" أو "lever:token"
# عبر متغير COMPANY_BOARDS في .env (مفصولة بفواصل).
DEFAULT_COMPANY_BOARDS = ["greenhouse:fervoenergy", "greenhouse:quaise"]


def company_boards() -> List[str]:
    import os
    extra = [x.strip() for x in os.getenv("COMPANY_BOARDS", "").split(",") if x.strip()]
    return DEFAULT_COMPANY_BOARDS + [x for x in extra if x not in DEFAULT_COMPANY_BOARDS]


def parse_greenhouse(token: str, data: dict) -> List[Dict]:
    return [_make(j.get("title", ""), j.get("absolute_url", ""), token.title(),
                  (j.get("location") or {}).get("name", "دولي"), None, j.get("title", ""), f"Greenhouse/{token}")
            for j in data.get("jobs", [])]


def parse_lever(token: str, data: list) -> List[Dict]:
    return [_make(j.get("text", ""), j.get("hostedUrl", ""), token.title(),
                  (j.get("categories") or {}).get("location", "دولي"), None,
                  f"{j.get('text', '')} {j.get('descriptionPlain', '')[:400]}", f"Lever/{token}") for j in data]


def fetch_company_boards() -> List[Dict]:
    results, failures, boards = [], 0, company_boards()
    for b in boards:
        kind, _, token = b.partition(":")
        try:
            if kind == "greenhouse":
                r = _get(f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs")
                results += parse_greenhouse(token, r.json()) if r else []
            elif kind == "lever":
                r = _get(f"https://api.lever.co/v0/postings/{token}", {"mode": "json"})
                results += parse_lever(token, r.json()) if r else []
            if not r:
                failures += 1
        except Exception as e:
            logger.warning(f"board {b} failed: {e}")
            failures += 1
    if boards and failures == len(boards):
        raise RuntimeError("company boards unreachable")
    return results


# ------------------- Adzuna (واجهة رسمية، تتطلب مفتاحاً مجانياً) -------------------
ADZUNA_COUNTRIES = ["gb", "de", "fr", "it", "nl", "at", "pl", "us", "ca", "au", "br", "ch", "be", "es"]


def parse_adzuna(country: str, data: dict) -> List[Dict]:
    out = []
    for j in data.get("results", []):
        out.append(_make(j.get("title", ""), j.get("redirect_url", ""), (j.get("company") or {}).get("display_name", ""),
                         (j.get("location") or {}).get("display_name", country.upper()), None,
                         j.get("description", ""), "Adzuna"))
    return out


def fetch_adzuna() -> List[Dict]:
    import os
    app_id, app_key = os.getenv("ADZUNA_APP_ID", ""), os.getenv("ADZUNA_APP_KEY", "")
    if not (app_id and app_key):
        raise SourceSkipped("set ADZUNA_APP_ID / ADZUNA_APP_KEY in .env (free key at developer.adzuna.com)")
    jobs = [(c, q) for c in ADZUNA_COUNTRIES for q in ("phd reservoir", "internship petroleum", "phd CCUS geothermal hydrogen storage")]

    def one(cq):
        c, q = cq
        r = _get(f"https://api.adzuna.com/v1/api/jobs/{c}/search/1",
                 {"app_id": app_id, "app_key": app_key, "what": q, "results_per_page": 50, "content-type": "application/json"})
        return parse_adzuna(c, r.json()) if r else None

    results, failures = [], 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        for res in ex.map(one, jobs):
            if res is None:
                failures += 1
            else:
                results += res
    if failures == len(jobs):
        raise RuntimeError("Adzuna unreachable or key invalid")
    return results


SOURCES: Dict[str, Callable[[], List[Dict]]] = {
    "Adzuna": fetch_adzuna,
    "CompanyBoards": fetch_company_boards,
    "Arbeitnow": fetch_arbeitnow,
    "jobs.ac.uk": fetch_jobsac,
    "EURAXESS": fetch_euraxess,
}


def filter_relevant(items: List[Dict], min_score: int = 1) -> List[Dict]:
    seen, out = set(), []
    for it in items:
        score, level_ok = relevance(it["title"], it.get("sub_specialty", ""))
        key = re.sub(r"\W+", "", it["title"].lower())
        if score >= min_score and level_ok and key not in seen:
            seen.add(key)
            it["_score"] = score
            out.append(it)
    return sorted(out, key=lambda x: -x["_score"])


def fetch_live_opportunities() -> Tuple[List[Dict], Dict[str, str]]:
    """يرجع (الفرص ذات الصلة، حالة كل مصدر)."""
    found, status = [], {}
    for name, fn in SOURCES.items():
        try:
            raw = fn()
            rel = filter_relevant(raw)
            status[name] = f"ok: {len(raw)} scanned, {len(rel)} relevant"
            found += rel
        except SourceSkipped as e:
            status[name] = f"skipped: {e}"
        except Exception as e:  # عزل الأعطال
            logger.warning(f"source {name} failed: {e}")
            status[name] = f"FAILED: {e}"
    return filter_relevant(found), status
