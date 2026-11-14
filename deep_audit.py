import sqlite3
import urllib.request
import re
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5'
}

def audit_all_links():
    conn = sqlite3.connect(r"C:\Users\admin\.gemini\antigravity\scratch\petro_phd_radar_bot\phd_radar.db")
    c = conn.cursor()
    c.execute("SELECT id, title, institution, link FROM opportunities")
    rows = c.fetchall()
    
    print(f"Auditing {len(rows)} opportunities from phd_radar.db...\n")
    
    results = []
    for oid, title, inst, link in rows:
        status_info = {"id": oid, "title": title, "inst": inst, "link": link, "ok": False, "reason": ""}
        try:
            req = urllib.request.Request(link, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=12, context=ctx) as resp:
                final_url = resp.geturl()
                code = resp.status
                body = resp.read(65536).decode('utf-8', errors='ignore')
                
                # Check for soft 404 or dead page indicators
                dead_phrases = [
                    "the page is no longer available",
                    "page no longer available",
                    "page not found",
                    "404 not found",
                    "pagina non trovata",
                    "seite nicht gefunden",
                    "job has expired",
                    "this position has been closed",
                    "offer is closed",
                    "page introuvable"
                ]
                
                found_dead = None
                for phrase in dead_phrases:
                    if phrase in body.lower():
                        # Make sure it's not just a false positive in a generic footer or script
                        found_dead = phrase
                        break
                
                if found_dead:
                    status_info["ok"] = False
                    status_info["reason"] = f"Soft 404 / Dead message: '{found_dead}' (Final: {final_url})"
                elif code >= 400:
                    status_info["ok"] = False
                    status_info["reason"] = f"HTTP {code}"
                else:
                    status_info["ok"] = True
                    status_info["reason"] = f"HTTP {code} -> {final_url}"
        except urllib.error.HTTPError as e:
            status_info["ok"] = False
            status_info["reason"] = f"HTTPError {e.code}"
        except Exception as e:
            status_info["ok"] = False
            status_info["reason"] = f"Exception: {str(e)[:60]}"
            
        results.append(status_info)
        mark = "✅" if status_info["ok"] else "❌"
        print(f"{mark} [{oid[:8]}] {title[:35]} | {inst[:25]}\n    URL: {link}\n    Status: {status_info['reason']}\n")

    conn.close()
    return results

if __name__ == "__main__":
    audit_all_links()
