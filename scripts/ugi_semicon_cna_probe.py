import re, html, requests
from pathlib import Path

URL='https://www.cna.com.tw/video/news/4356229'
out=Path('public/ugi/editorial/2026-09-08/semicon_cna_probe')
out.mkdir(parents=True, exist_ok=True)
r=requests.get(URL,headers={'User-Agent':'Mozilla/5.0'},timeout=60)
r.raise_for_status()
text=r.text
patterns=[
 r'https?://[^\"\'<> ]+\.mp4[^\"\'<> ]*',
 r'https?://(?:www\.)?youtube\.com/embed/[^\"\'<> ]+',
 r'https?://youtu\.be/[^\"\'<> ]+',
 r'https?://[^\"\'<> ]+m3u8[^\"\'<> ]*',
]
found=[]
for p in patterns:
    for x in re.findall(p,text,re.I):
        x=html.unescape(x)
        if x not in found: found.append(x)
# also store nearby lines around video/embed markers
lines=[]
for line in text.splitlines():
    lo=line.lower()
    if any(k in lo for k in ['youtube','mp4','m3u8','iframe','videojs','video']):
        lines.append(line.strip()[:5000])
(out/'sources.txt').write_text('PAGE='+URL+'\nSTATUS='+str(r.status_code)+'\n\nFOUND\n'+'\n'.join(found)+'\n\nLINES\n'+'\n'.join(lines[:200]),encoding='utf-8')
print('FOUND',found)
