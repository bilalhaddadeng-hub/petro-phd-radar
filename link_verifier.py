import requests
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5,it;q=0.3,fr;q=0.3"
}

def verify_and_resolve_url(url: str, timeout: int = 6) -> Tuple[bool, str]:
    """
    محرك التحقق الذاتي من صحة الروابط:
    1. يتصل بالرابط ويتتبع كافة التحويلات (Redirects) للحصول على الرابط النهائي الدقيق.
    2. يتأكد من أن كود الاستجابة هو 200 OK وأنه ليس صفحة خطأ 404 أو صفحة محذوفة.
    3. يرجع (is_valid, final_url)
    """
    if not url or not url.startswith("http"):
        return False, url

    try:
        # تجربة HEAD أولاً لتوفير الوقت واستهلاك البيانات
        resp = requests.head(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        if resp.status_code == 200:
            return True, resp.url
        elif resp.status_code in [403, 405]:
            # بعض المواقع ترفض HEAD وتطلب GET
            resp = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
            if resp.status_code == 200 and "not available" not in resp.text.lower() and "page not found" not in resp.text.lower():
                return True, resp.url
        elif resp.status_code == 404:
            return False, url
            
        # تجربة GET أخيرة
        resp = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        if resp.status_code < 400:
            # التأكد من أن الصفحة لا تحتوي على رسائل خطأ داخلية
            text_sample = resp.text[:1500].lower()
            if "page is no longer available" in text_sample or "404 not found" in text_sample:
                return False, url
            return True, resp.url
        else:
            return False, url
    except Exception as e:
        logger.warning(f"فشل التحقق من الرابط {url}: {e}")
        return False, url
