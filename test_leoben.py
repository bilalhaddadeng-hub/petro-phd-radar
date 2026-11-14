import urllib.request
import re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
url = 'https://www.unileoben.ac.at/en/jobs/'
req = urllib.request.Request(url, headers=headers)
html = urllib.request.urlopen(req, timeout=8).read().decode('utf-8', errors='ignore')

matches = set(re.findall(r'href=[\'"]([^\'"]+)[\'"]', html))
for m in sorted(matches):
    if any(k in m.lower() for k in ['job', 'career', 'portal', 'bewerb', 'stellen', 'wissenschaft', 'apply']):
        print(m)
