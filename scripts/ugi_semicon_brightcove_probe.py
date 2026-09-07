import re, html, requests, urllib.parse
from pathlib import Path

URL='https://www.taiwanplus.com/news/taiwan-news/technology-and-science/260902021/semicon-taiwan-2026-kicks-off-in-taipei'
out=Path('public/ugi/editorial/2026-09-08/semicon_brightcove_probe')
out.mkdir(parents=True, exist_ok=True)
s=requests.Session(); s.headers.update({'User-Agent':'Mozilla/5.0'})
text=s.get(URL,timeout=60).text
scripts=[]
for src in re.findall(r'<script[^>]+src=["\']([^"\']+)["\']',text,re.I):
    u=urllib.parse.urljoin(URL,html.unescape(src))
    if u not in scripts: scripts.append(u)
results=[]
patterns=[
    r'players\.brightcove\.net/[^"\'\\ ]+',
    r'brightcove[^\n]{0,500}',
    r'accountId[^\n]{0,300}',
    r'account_id[^\n]{0,300}',
    r'playerId[^\n]{0,300}',
    r'policyKey[^\n]{0,500}',
    r'6404485548112[^\n]{0,500}',
]
for i,u in enumerate(scripts):
    try:
        r=s.get(u,timeout=30)
        body=r.text
    except Exception as e:
        continue
    hits=[]
    for p in patterns:
        hits.extend(re.findall(p,body,re.I))
    if hits:
        results.append('SCRIPT '+u+'\n'+'\n'.join(h[:2000] for h in hits[:100]))
(out/'config_hits.txt').write_text('PAGE='+URL+'\nSCRIPTS='+str(len(scripts))+'\n\n'+'\n\n'.join(results),encoding='utf-8')
print('scripts',len(scripts),'hit scripts',len(results))
