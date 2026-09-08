import re, json, html
from urllib.parse import urljoin
from urllib.request import Request, urlopen
from pathlib import Path

PAGES = [
 'https://www.tsmc.com/static/english/careers/brilliantTogether_US.htm',
 'https://www.tsmc.com/static/english/careers/campus_recruitment_2025/index.html',
 'https://www.tsmc.com/static/english/careers/totalRewards/workAtTSMC.html',
 'https://pr.tsmc.com/english/gallery-videos',
 'https://www.tsmc.com/static/abouttsmcaz/index.htm',
]
OUT=Path('public/ugi/editorial/2026-09-08/tsmc-direct-probe')
OUT.mkdir(parents=True,exist_ok=True)
results=[]
for page in PAGES:
    req=Request(page,headers={'User-Agent':'Mozilla/5.0'})
    with urlopen(req,timeout=60) as r:
        text=r.read().decode('utf-8','ignore')
    # Catch source/src/href refs that look like video files or HLS manifests.
    refs=set()
    for pat in [r'''(?:src|href)\s*=\s*["']([^"']+\.(?:mp4|webm|m3u8)(?:\?[^"']*)?)["']''',
                r'''https?://[^\s"'<>]+\.(?:mp4|webm|m3u8)(?:\?[^\s"'<>]*)?''']:
        for m in re.finditer(pat,text,re.I):
            ref=m.group(1) if m.lastindex else m.group(0)
            refs.add(urljoin(page,html.unescape(ref)))
    results.append({'page':page,'video_refs':sorted(refs)})
(OUT/'direct_video_refs.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print(json.dumps(results,indent=2))
