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
    "fellowship", "msc project", "master project", "stage ", "researcher", "scholarship", "bolsa", "borsa",
    "assegno", "doctoral candidate", "early-stage", "early career", "apprentice", "co-op", "working student",
    "praktikum", "werkstudent", "stagiaire", "tirocinio",
]
EXCLUDE_TERMS = ["senior ", "head of", "professor of", "associate professor", "full professor", "chair of", "director",
                 "postdoc", "post-doc", "post doc", "postdoctoral", "post-doctoral", "assistant professor", "lecturer",
                 "principal ", "manager", "vice president"]

SEARCH_QUERIES = [
    "reservoir engineering", "petroleum engineering", "CCUS", "CO2 storage", "carbon capture storage",
    "hydrogen storage", "geothermal", "geomechanics", "porous media", "enhanced oil recovery",
    "drilling engineering", "subsurface", "oil and gas", "multiphase flow", "petrophysics",
]
# كلمات إضافية للمصادر السريعة (jobs.ac.uk وCORDIS) حيث لا يوجد حد معدل مزعج
EXTRA_QUERIES = [
    "carbon storage", "hydrogen", "energy transition", "geoscience PhD", "geology PhD", "earth science PhD",
    "fluid flow", "numerical modelling subsurface", "rock physics", "digital rock", "reactive transport",
    "wellbore", "geophysics PhD", "energy geoscience", "decarbonisation PhD", "net zero PhD",
]


NOTES: Dict[str, str] = {}  # ملاحظات تشخيصية لكل مصدر تُضاف إلى حالة الصيد


class SourceSkipped(Exception):
    """مصدر معطّل بإعداد ناقص (ليس عطلاً)."""


def _get(url: str, params: Optional[dict] = None, timeout: int = 20) -> Optional[requests.Response]:
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=timeout)
        return r if r.status_code == 200 else None
    except requests.RequestException as e:
        logger.warning(f"live fetch failed {url}: {e}")
        return None


def _get_retry(url: str, params: Optional[dict] = None, tries: int = 3) -> Optional[requests.Response]:
    """طلب مع انتظار قصير عند 429 (حد المعدل): نحترم الخادم ولا نتجاوزه."""
    import time
    for i in range(tries):
        try:
            r = requests.get(url, params=params, headers=HEADERS, timeout=20)
        except requests.RequestException:
            return None
        if r.status_code == 200:
            return r
        if r.status_code != 429:
            return None
        time.sleep(2 * (i + 1))
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


_COUNTRIES = {
    "united kingdom": "UK", "uk": "UK", "england": "UK", "scotland": "UK", "wales": "UK",
    "norway": "Norway", "germany": "Germany", "france": "France", "italy": "Italy",
    "netherlands": "Netherlands", "spain": "Spain", "portugal": "Portugal", "austria": "Austria",
    "switzerland": "Switzerland", "denmark": "Denmark", "sweden": "Sweden", "finland": "Finland",
    "belgium": "Belgium", "poland": "Poland", "hungary": "Hungary", "romania": "Romania",
    "czech": "Czechia", "ireland": "Ireland", "canada": "Canada", "australia": "Australia",
    "united states": "USA", "usa": "USA", "saudi": "Saudi Arabia", "united arab": "UAE",
    "qatar": "Qatar", "kuwait": "Kuwait", "malaysia": "Malaysia", "brazil": "Brazil",
}
_CITIES = {
    "london": "UK", "aberdeen": "UK", "edinburgh": "UK", "cambridge": "UK", "oxford": "UK",
    "manchester": "UK", "imperial": "UK", "trondheim": "Norway", "stavanger": "Norway",
    "oslo": "Norway", "berlin": "Germany", "munich": "Germany", "paris": "France",
    "pau": "France", "milan": "Italy", "rome": "Italy", "turin": "Italy", "delft": "Netherlands",
    "amsterdam": "Netherlands", "vienna": "Austria", "leoben": "Austria", "zurich": "Switzerland",
    "houston": "USA", "calgary": "Canada", "perth": "Australia",
}


def normalize_country(location: str) -> str:
    """يحوّل نص الموقع (مدينة/منطقة) إلى بلد معروف، وإلا "دولي"."""
    low = (location or "").lower()
    for table in (_COUNTRIES, _CITIES):
        for key, val in table.items():
            if key in low:
                return val
    return "دولي"


def _make(title, link, employer, location, deadline, snippet, source) -> Dict:
    return {
        "title": re.sub(r"\s+", " ", title).strip(),
        "link": link,
        "institution": employer or "جهة غير محددة",
        "country": normalize_country(location),
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
    def one(args):
        q, start = args
        r = _get("https://www.jobs.ac.uk/search/",
                 {"keywords": q, "sortOrder": 1, "pageSize": 25, "startIndex": start})
        return parse_jobsac(r.text) if r else None

    jobs = [(q, st) for q in SEARCH_QUERIES + EXTRA_QUERIES for st in (1, 26, 51, 76, 101)]
    results, failures = [], 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        for res in ex.map(one, jobs):
            if res is None:
                failures += 1
            else:
                results += res
    if failures == len(jobs):
        raise RuntimeError("jobs.ac.uk unreachable")
    return results


# ------------------------------ Nature Careers (أقسام علوم الأرض/الهندسة) ------------------------------
NATURE_PAGES = [
    "https://www.nature.com/naturecareers/jobs/phd-studentship/earth-sciences/",
    "https://www.nature.com/naturecareers/jobs/earth-sciences/",
    "https://www.nature.com/naturecareers/jobs/phd-studentship/engineering/",
    "https://www.nature.com/naturecareers/jobs/phd-studentship/chemistry/",
]


def parse_nature(html: str) -> List[Dict]:
    soup = BeautifulSoup(html, "html.parser")
    out = []
    for li in soup.select("li.lister__item, div.lister__item"):
        a = li.select_one("h3.lister__header a[href]")
        if not a:
            continue
        employer = li.select_one(".lister__meta-item--recruiter")
        loc = li.select_one(".lister__meta-item--location")
        out.append(_make(a.get_text(" ", strip=True), urljoin("https://www.nature.com", a["href"].strip()),
                         employer.get_text(" ", strip=True) if employer else "",
                         loc.get_text(" ", strip=True) if loc else "",
                         None, li.get_text(" ", strip=True)[:500], "Nature Careers"))
    return out


def fetch_nature() -> List[Dict]:
    results, failures = [], 0
    for url in NATURE_PAGES:
        r = _get(url)
        if r is None:
            failures += 1
        else:
            results += parse_nature(r.text)
    if failures == len(NATURE_PAGES):
        raise RuntimeError("Nature Careers unreachable")
    return results


# ------------------------------ CORDIS (شبكات الدكتوراه الأوروبية MSCA) ------------------------------
CORDIS_QUERIES = ["reservoir", "CO2 storage", "carbon storage", "hydrogen storage", "geothermal", "porous media",
                  "subsurface", "geomechanics", "petroleum", "CCUS", "multiphase flow", "oil and gas"]


def parse_cordis(data: dict, today: Optional[date] = None) -> List[Dict]:
    """مشاريع Horizon/MSCA الحالية التي توظف باحثي دكتوراه: تُعلن الوظائف لاحقاً عبر EURAXESS."""
    today = today or date.today()
    out = []
    for h in (data.get("payload") or {}).get("results", []):
        title, teaser = h.get("title") or "", h.get("teaser") or ""
        end = re.search(r"(\d{4})\s*$", str(h.get("endDate") or ""))
        if end and int(end.group(1)) < today.year:
            continue  # مشروع منتهٍ
        text = f"{title} {teaser}"
        if not re.search(r"doctoral|phd|early[- ]stage|marie|msca|training network", text, re.I):
            continue
        pid = h.get("id") or h.get("rcn")
        if not pid:
            continue
        acr = h.get("acronym") or ""
        item = _make(f"Doctoral/PhD project network {acr}: {title}", f"https://cordis.europa.eu/project/id/{pid}",
                     "Horizon Europe / MSCA (CORDIS)", "Europe", "راجع صفحة المشروع و EURAXESS", text[:300], "CORDIS")
        item["key_requirements"] = ("🔎 مشروع أوروبي ممول يضم/يوظف باحثي دكتوراه؛ لا يعني وجود مقعد مفتوح الآن. "
                                    "راجع موقع المشروع وEURAXESS وراسل منسق المشروع.")
        out.append(item)
    return out


def fetch_cordis() -> List[Dict]:
    def one(q):
        try:
            r = requests.get("https://cordis.europa.eu/api/search/results", headers=HEADERS, timeout=30, params={
                "q": f"contenttype='project' AND '{q}' AND ('doctoral' OR 'MSCA' OR 'early-stage researchers')",
                "p": 1, "num": 25, "srt": "/project/contentUpdateDate:decreasing", "format": "json"})
            return parse_cordis(r.json()) if r.status_code == 200 else None
        except (requests.RequestException, ValueError):
            return None

    results, failures = [], 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        for res in ex.map(one, CORDIS_QUERIES):
            if res is None:
                failures += 1
            else:
                results += res
    if failures == len(CORDIS_QUERIES):
        raise RuntimeError("CORDIS unreachable")
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


def fetch_euraxess(pages: int = 3, recent_pages: int = 15) -> List[Dict]:
    """بحث EURAXESS الرسمي بالكلمة المفتاحية (f[0]=keywords:...) + أحدث الصفحات، بوتيرة هادئة."""
    import time

    def one(params):
        time.sleep(2.0)  # رفق بالخادم: تجنباً لحد المعدل 429
        r = _get_retry("https://euraxess.ec.europa.eu/jobs/search", params)
        return parse_euraxess(r.text) if r else None

    jobs = [{"f[0]": f"keywords:{q}", "page": p} for q in SEARCH_QUERIES for p in range(pages)]
    jobs += [{"page": p} for p in range(recent_pages)]

    results, failures = [], 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
        for res in ex.map(one, jobs):
            if res is None:
                failures += 1
            else:
                results += res
    if failures == len(jobs):
        raise RuntimeError("EURAXESS unreachable")
    NOTES["EURAXESS"] = f"{failures}/{len(jobs)} requests failed, {len({r['title'] for r in results})} unique titles"
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
# الصيغ: greenhouse:token | lever:token | ashby:token | smartrecruiters:token | workable:token
#        workday:tenant:N:site   (مثال: workday:bakerhughes:5:BakerHughes)
DEFAULT_COMPANY_BOARDS = [
    "greenhouse:fervoenergy", "greenhouse:quaise", "greenhouse:cognite",
    "smartrecruiters:ormat", "smartrecruiters:mazama", "workable:1pointfive", "workable:slb",
    "workday:bakerhughes:5:BakerHughes",
]
WORKDAY_QUERIES = ["reservoir", "subsurface", "graduate", "intern", "geoscience", "carbon storage"]


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


def parse_ashby(token: str, data: dict) -> List[Dict]:
    return [_make(j.get("title", ""), j.get("jobUrl", ""), token.title(), j.get("location", "") or "دولي", None,
                  f"{j.get('title', '')} {(j.get('descriptionPlain') or '')[:400]}", f"Ashby/{token}")
            for j in data.get("jobs", [])]


def parse_smartrecruiters(token: str, data: dict) -> List[Dict]:
    out = []
    for j in data.get("content", []):
        loc = j.get("location") or {}
        out.append(_make(j.get("name", ""), f"https://jobs.smartrecruiters.com/{token}/{j.get('id', '')}",
                         (j.get("company") or {}).get("name", token.title()),
                         f"{loc.get('city', '')} {loc.get('country', '')}", None, j.get("name", ""),
                         f"SmartRecruiters/{token}"))
    return out


def parse_workable(token: str, data: dict) -> List[Dict]:
    return [_make(j.get("title", ""), j.get("url") or j.get("shortlink", ""), data.get("name", token.title()),
                  f"{j.get('city', '')} {j.get('country', '')}", None, j.get("title", ""), f"Workable/{token}")
            for j in data.get("jobs", [])]


def parse_workday(tenant: str, n: str, site: str, data: dict) -> List[Dict]:
    out = []
    for j in data.get("jobPostings", []):
        out.append(_make(j.get("title", ""), f"https://{tenant}.wd{n}.myworkdayjobs.com/{site}{j.get('externalPath', '')}",
                         tenant.title(), j.get("locationsText", "") or "دولي", None, j.get("title", ""),
                         f"Workday/{tenant}"))
    return out


def _fetch_workday(tenant: str, n: str, site: str) -> Optional[List[Dict]]:
    url = f"https://{tenant}.wd{n}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs"
    out, ok = [], False
    for q in WORKDAY_QUERIES:
        try:
            r = requests.post(url, json={"appliedFacets": {}, "limit": 20, "offset": 0, "searchText": q},
                              headers={**HEADERS, "Content-Type": "application/json"}, timeout=20)
        except requests.RequestException:
            continue
        if r.status_code == 200:
            ok = True
            out += parse_workday(tenant, n, site, r.json())
    return out if ok else None


def _fetch_board(b: str) -> Optional[List[Dict]]:
    kind, _, rest = b.partition(":")
    if kind == "workday":
        tenant, n, site = rest.split(":")
        return _fetch_workday(tenant, n, site)
    table = {
        "greenhouse": (f"https://boards-api.greenhouse.io/v1/boards/{rest}/jobs", None, lambda j: parse_greenhouse(rest, j)),
        "lever": (f"https://api.lever.co/v0/postings/{rest}", {"mode": "json"}, lambda j: parse_lever(rest, j)),
        "ashby": (f"https://api.ashbyhq.com/posting-api/job-board/{rest}", None, lambda j: parse_ashby(rest, j)),
        "smartrecruiters": (f"https://api.smartrecruiters.com/v1/companies/{rest}/postings", {"limit": 100},
                            lambda j: parse_smartrecruiters(rest, j)),
        "workable": (f"https://apply.workable.com/api/v1/widget/accounts/{rest}", None, lambda j: parse_workable(rest, j)),
    }
    if kind not in table:
        return None
    url, params, parser = table[kind]
    r = _get_retry(url, params)
    return parser(r.json()) if r else None


def _safe_board(b: str) -> Optional[List[Dict]]:
    try:
        return _fetch_board(b)
    except Exception as e:
        logger.warning(f"board {b} failed: {e}")
        return None


def fetch_company_boards() -> List[Dict]:
    boards = company_boards()
    results, failures = [], 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        for res in ex.map(_safe_board, boards):
            if res is None:
                failures += 1
            else:
                results += res
    if boards and failures == len(boards):
        raise RuntimeError("company boards unreachable")
    return results


# ------------------- Adzuna (واجهة رسمية، تتطلب مفتاحاً مجانياً) -------------------
ADZUNA_COUNTRIES = ["gb", "de", "fr", "it", "nl", "at", "pl", "us", "ca", "au", "br", "ch", "be", "es"]


def parse_adzuna(country: str, data: dict) -> List[Dict]:
    out = []
    codes = {"gb": "UK", "us": "USA", "ca": "Canada", "au": "Australia", "de": "Germany", "fr": "France",
             "it": "Italy", "nl": "Netherlands", "at": "Austria", "ch": "Switzerland", "pl": "Poland",
             "es": "Spain", "be": "Belgium", "br": "Brazil"}
    for j in data.get("results", []):
        item = _make(j.get("title", ""), j.get("redirect_url", ""), (j.get("company") or {}).get("display_name", ""),
                     (j.get("location") or {}).get("display_name", ""), None,
                     j.get("description", ""), "Adzuna")
        item["country"] = codes.get(country.lower(), item["country"])
        out.append(item)
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
    "CORDIS": fetch_cordis,
    "NatureCareers": fetch_nature,
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
            note = f" [{NOTES[name]}]" if name in NOTES else ""
            status[name] = f"ok: {len(raw)} scanned, {len(rel)} relevant{note}"
            found += rel
        except SourceSkipped as e:
            status[name] = f"skipped: {e}"
        except Exception as e:  # عزل الأعطال
            logger.warning(f"source {name} failed: {e}")
            status[name] = f"FAILED: {e}"
    return filter_relevant(found), status
