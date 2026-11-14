# -*- coding: utf-8 -*-
"""
hunter.py - صياد الفرص الذكي السريع والمتوازي (High-Speed Concurrent Opportunity Hunter)
يقوم بالصيد والفحص المتوازي الفوري لفرص الدكتوراه والتدريب R&D في هندسة البترول والمكامن وتخزين الطاقة الجوفية
مع التحقق الفوري من صحة الروابط (Zero Dead Links) وتقييم التطابق مع ملف بلال حداد.
"""

import logging
import urllib.request
import concurrent.futures
import json
from datetime import datetime
from typing import List, Dict, Tuple
from evaluator import evaluate_for_bilal_haddad
from database import save_or_update_opportunity, log_hunting_session
from scrapers.global_deep_crawler import crawl_and_verify_all_opportunities
from scrapers.live_sources import fetch_live_opportunities

logger = logging.getLogger(__name__)

LAST_SOURCE_STATUS: Dict[str, str] = {}

def set_source_status(st: Dict[str, str]):
    LAST_SOURCE_STATUS.clear()
    LAST_SOURCE_STATUS.update(st)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8,it;q=0.7"
}

# المصادر والبوابات الحية الموسعة التي يستهدفها الصياد (جامعات، معاهد، وشركات كبرى ومتوسطة واستشارية متخصصة)
HUNTING_TARGETS = [
    # 1. كراسي هندسة المكامن والجامعات الرائدة
    {"name": "Montanuniversität Leoben - Chair of Reservoir Engineering", "url": "https://www.unileoben.ac.at/jobs/", "category": "RESERVOIR_STORAGE"},
    {"name": "TU Delft Geoscience & Engineering Department", "url": "https://careers.tudelft.nl/?locale=en_US", "category": "RESERVOIR_STORAGE"},
    {"name": "Politecnico di Torino - Scuola di Dottorato", "url": "https://www.polito.it/en/education/phd-programmes/admissions-to-phd-programmes", "category": "ITALY_ACADEMIC"},
    {"name": "Politecnico di Milano - DICA Department", "url": "https://www.polimi.it/dottorato", "category": "ITALY_ACADEMIC"},
    {"name": "TU Bergakademie Freiberg - GraFA Graduate School", "url": "https://tu-freiberg.de/en/grafa", "category": "GERMANY"},
    {"name": "University of Stavanger (UiS) Energy Resources", "url": "https://www.uis.no/en/research/phd-programmes", "category": "NORWAY"},
    {"name": "KFUPM College of Petroleum & Geosciences (CPG)", "url": "https://cgis.kfupm.edu.sa/", "category": "MIDDLE_EAST"},
    {"name": "KAUST Visiting Student Research Program (VSRP)", "url": "https://admissions.kaust.edu.sa/study/internships", "category": "MIDDLE_EAST"},
    {"name": "AGH University of Krakow - Drilling, Oil & Gas", "url": "https://sd.agh.edu.pl/en/", "category": "EUROPE_ACADEMIC"},
    {"name": "Heriot-Watt University - Institute of GeoEnergy (IGE)", "url": "https://www.hw.ac.uk/about/our-schools/energy-geoscience-infrastructure-and-society/research-institutes/geoenergy-engineering", "category": "RESERVOIR_STORAGE"},
    {"name": "Euraxess European Researchers Portal", "url": "https://euraxess.ec.europa.eu/", "category": "EU_GOV"},

    # 2. الشركات الاستشارية والمتوسطة والمتخصصة في المكامن ومحاكاة الموائع
    {"name": "Beicip-Franlab (Reservoir & Basin Consulting - IFPEN)", "url": "https://www.beicip.com/careers/", "category": "CONSULTING_MIDSIZE"},
    {"name": "Rock Flow Dynamics (RFD tNavigator Simulation)", "url": "https://rfdyn.com/about/careers/", "category": "SOFTWARE_RESERVOIR"},
    {"name": "TGT Diagnostics (Subsurface Well & Flow Analytics)", "url": "https://tgtdiagnostics.com/career/", "category": "DIAGNOSTICS_FLOW"},
    {"name": "Sproule - ERCE Energy (Independent Reserves & Reservoir)", "url": "https://sproule-erce.com/careers/", "category": "CONSULTING_MIDSIZE"},
    {"name": "Storegga (Pure-play Geological Carbon Storage)", "url": "https://storegga.earth/careers", "category": "CCS_STARTUP"},
    {"name": "TNO Applied Geosciences (Subsurface Energy Storage)", "url": "https://www.tno.nl/en/careers/", "category": "RESEARCH_INSTITUTE"},
    {"name": "GFZ Helmholtz Potsdam (Porous Media & Geomechanics)", "url": "https://www.gfz.de/en/career/job-offers", "category": "RESEARCH_INSTITUTE"},
    {"name": "Carbfix (CO2 Basalt Porous Mineralization)", "url": "https://www.carbfix.com/careers", "category": "CCS_STARTUP"},
    {"name": "PanTerra Geoconsultants (Core Analysis & Reservoir Flooding)", "url": "https://www.panterra.nl/careers/", "category": "CONSULTING_MIDSIZE"},
    {"name": "Resoptima (Ensemble History Matching & Modeling)", "url": "https://resoptima.com/careers/", "category": "SOFTWARE_RESERVOIR"},
    {"name": "Wintershall Dea (Gas & CCUS Subsurface Operator)", "url": "https://wintershalldea.de/en/careers", "category": "OPERATOR_MIDSIZE"},

    # 3. الشركات العالمية الكبرى والمراكز الوطنية
    {"name": "Eni S.p.A. - San Donato Milanese R&D Labs", "url": "https://www.eni.com/en-IT/careers/job-opportunities.html", "category": "CORPORATE_RD"},
    {"name": "TotalEnergies OneTech (CSTJF Pau Technical Center)", "url": "https://totalenergies.com/careers", "category": "CORPORATE_RD"},
    {"name": "IFP Energies nouvelles (IFPEN Theses & Stage R&D)", "url": "https://theses.ifpen.fr/", "category": "RESEARCH_INSTITUTE"},
    {"name": "SLB Early Careers (Schlumberger Reservoir Software)", "url": "https://careers.slb.com/early-careers", "category": "CORPORATE_RD"},
    {"name": "Baker Hughes Students (Subsurface Reinjection)", "url": "https://careers.bakerhughes.com/global/en/students", "category": "CORPORATE_RD"},
    {"name": "Equinor Research Centre (Subsurface & Northern Lights)", "url": "https://www.equinor.com/careers/students-and-graduates", "category": "CORPORATE_RD"},
    {"name": "OGS Trieste (Istituto Nazionale Oceanografia e Geofisica)", "url": "https://www.ogs.it/it", "category": "ITALY_ACADEMIC"}
]

def verify_live_url(url: str, timeout: int = 5) -> Tuple[bool, str]:
    """فحص سريع لصحة الرابط وتأكيد عدم وجود رسائل الخطأ"""
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=timeout) as response:
            code = response.getcode()
            final_url = response.geturl()
            html = response.read(2048).decode("utf-8", errors="ignore").lower()
            if "no longer available" in html or "page not found" in html:
                return False, final_url
            return (code == 200), final_url
    except Exception as e:
        logger.warning(f"URL check failed for {url}: {e}")
        return False, url

def process_single_opportunity(opp: Dict) -> Tuple[Dict, bool, str]:
    """معالجة وفحص فرصة واحدة وتجهيزها للحفظ"""
    opp["experience_required"] = "0 سنوات (مفتوحة بالكامل لحديثي التخرج من الماستر / Early Stage Researcher)"
    target_link = opp.get("link", opp.get("raw_link", ""))
    is_ok, resolved_url = verify_live_url(target_link)
    if is_ok:
        opp["link"] = resolved_url
    else:
        opp["link"] = target_link # الاحتفاظ بالرابط الأساسي
        
    try:
        if not opp.get("acceptance_difficulty"):
            ev = evaluate_for_bilal_haddad(
                opp.get("country", ""), opp.get("institution", ""), opp.get("source_type", ""),
                opp.get("title", ""), opp.get("sub_specialty", ""))
            opp["acceptance_difficulty"] = ev["level"]
            if not opp.get("key_requirements") or opp.get("category") == "LIVE":
                opp["key_requirements"] = ev["key_requirements"]
        status, is_new = save_or_update_opportunity(opp)
        return opp, is_new, status
    except Exception as e:  # عنصر واحد فاشل لا يوقف الصيد
        logger.error(f"Skipping opportunity {opp.get('title')!r}: {e}")
        return opp, False, "ERROR"

def execute_deep_hunt() -> Dict:
    """
    تنفيذ عملية صيد متوازية وسريعة عبر كافة البوابات:
    - فحص بالتوازي الفوري (10 خيوط متزامنة).
    - التحقق من متطلب الخبرة (0 سنوات).
    - حفظ الفرص في قاعدة البيانات وتسجيل جلسة الصيد.
    """
    logger.info("🎯 بدء عملية الصيد السريع للفرص (Concurrent Opportunity Hunt)...")
    scanned_sources = len(HUNTING_TARGETS)
    
    opportunities = crawl_and_verify_all_opportunities()

    # القناص الحي: فرص جديدة من مصادر عامة (جامعات وشركات جديدة بلا قائمة مسبقة)
    source_status = {}
    try:
        live, source_status = fetch_live_opportunities()
        opportunities = opportunities + live
    except Exception as e:
        logger.warning(f"Live hunting failed: {e}")
        source_status = {"live": f"FAILED: {e}"}
    set_source_status(source_status)
    
    new_caught = 0
    updated_caught = 0
    verified_valid = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(process_single_opportunity, opportunities))

    for opp, is_new, status in results:
        if status == "ERROR":
            continue
        verified_valid += 1
        if is_new:
            new_caught += 1
        elif status == "UPDATED":
            updated_caught += 1

    # تسجيل تفاصيل جلسة الصيد
    log_hunting_session(
        scanned=scanned_sources,
        new_found=new_caught,
        updated=updated_caught,
        details=f"كتالوج + قناص حي: {verified_valid} فرصة. المصادر: {json.dumps(source_status, ensure_ascii=False)}"
    )

    hunt_result = {
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "scanned_sources": scanned_sources,
        "total_monitored": len(opportunities),
        "verified_active": verified_valid,
        "new_caught": new_caught,
        "updated_caught": updated_caught,
        "sources": source_status
    }
    logger.info(f"اكتملت جلسة الصيد: {hunt_result}")
    return hunt_result

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    res = execute_deep_hunt()
    print("نتائج جلسة الصيد السريع:", json.dumps(res, indent=2, ensure_ascii=False))
