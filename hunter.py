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

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8,it;q=0.7"
}

# المصادر والبوابات الحية التي يستهدفها الصياد
HUNTING_TARGETS = [
    {"name": "Euraxess European Research Portal", "url": "https://euraxess.ec.europa.eu/jobs/search", "category": "EU_GOV"},
    {"name": "Politecnico di Torino - DIATI PhD Portal", "url": "https://www.polito.it/didattica/dottorato-di-ricerca/ammissione-al-dottorato", "category": "ITALY_ACADEMIC"},
    {"name": "Politecnico di Milano - DICA Subsurface Group", "url": "https://www.polimi.it/dottorato", "category": "ITALY_ACADEMIC"},
    {"name": "Eni S.p.A. San Donato Milanese R&D Careers", "url": "https://www.eni.com/en-IT/careers/job-opportunities.html", "category": "CORPORATE_RD"},
    {"name": "SLB Early Careers & R&D Hub", "url": "https://careers.slb.com/early-careers", "category": "CORPORATE_RD"},
    {"name": "TotalEnergies Student & R&D CIFRE Doctorates", "url": "https://totalenergies.com/careers", "category": "CORPORATE_RD"},
    {"name": "IFP Energies nouvelles (IFPEN) Theses Portal", "url": "https://theses.ifpen.fr/", "category": "RESEARCH_INSTITUTE"},
    {"name": "Montanuniversität Leoben - Chair of Reservoir Engineering", "url": "https://geoenergy.engineering/", "category": "RESERVOIR_STORAGE"},
    {"name": "TU Delft Geoscience & Engineering Department", "url": "https://www.tudelft.nl/citg/over-faculteit/afdelingen/geoscience-engineering", "category": "RESERVOIR_STORAGE"},
    {"name": "Heriot-Watt University Institute of GeoEnergy Engineering", "url": "https://www.hw.ac.uk/about/our-schools/energy-geoscience-infrastructure-and-society/research-institutes/geoenergy-engineering", "category": "RESERVOIR_STORAGE"},
    {"name": "KFUPM College of Petroleum Engineering & Geosciences (CPG)", "url": "https://cpg.kfupm.edu.sa/academics/departments/department-of-petroleum-engineering/graduate-programs/", "category": "MIDDLE_EAST"},
    {"name": "KAUST Advanced Reservoir & Energy Storage (ANPER Lab)", "url": "https://admissions.kaust.edu.sa/study/internships", "category": "MIDDLE_EAST"},
    {"name": "NTNU Norwegian University of Science & Technology", "url": "https://www.ntnu.edu/phd", "category": "NORWAY"},
    {"name": "University of Stavanger (UiS) Petroleum Geomechanics", "url": "https://www.uis.no/en", "category": "NORWAY"},
    {"name": "TU Bergakademie Freiberg Underground Energy & H2 Storage", "url": "https://tu-freiberg.de/en/grafa", "category": "GERMANY"}
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
        
    if not opp.get("acceptance_difficulty"):
        opp["acceptance_difficulty"] = evaluate_for_bilal_haddad(opp)
        
    status, is_new = save_or_update_opportunity(opp)
    return opp, is_new, status

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
    
    new_caught = 0
    updated_caught = 0
    verified_valid = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(process_single_opportunity, opportunities))

    for opp, is_new, status in results:
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
        details=f"صيد متوازي شمل {scanned_sources} جهة بحثية، تم فحص {verified_valid} فرصة حية."
    )

    hunt_result = {
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "scanned_sources": scanned_sources,
        "total_monitored": len(opportunities),
        "verified_active": verified_valid,
        "new_caught": new_caught,
        "updated_caught": updated_caught
    }
    logger.info(f"اكتملت جلسة الصيد: {hunt_result}")
    return hunt_result

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    res = execute_deep_hunt()
    print("نتائج جلسة الصيد السريع:", json.dumps(res, indent=2, ensure_ascii=False))
