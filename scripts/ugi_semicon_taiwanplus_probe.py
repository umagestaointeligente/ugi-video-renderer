import re, html, requests
from pathlib import Path

URL='https://www.taiwanplus.com/news/taiwan-news/technology-and-science/260902021/semicon-taiwan-2026-kicks-off-in-taipei'
out=Path('public/ugi/editorial/2026-09-08/semicon_taiwanplus_probe')
out.mkdir(parents=True, exist_ok=True)
r=requests.get(URL,headers={'User-Agent':'Mozilla/5.0'},timeout=60)
r.raise_for_status()
text=r.text
patterns=[
 r'https?://[^\"\'<> ]+\.mp4(?:\?[^\"\'<> ]*)?',
 r'https?://[^\"\'<> ]+\.m3u8(?:\?[^\"\'<> ]*)?',
 r'https?://[^\"\'<> ]+(?:manifest|playlist)[^\"\'<> ]*',
 r'https?://(?:www\.)?youtube\.com/(?:watch\?v=|embed/)[^\"\'<> &]+',
 r'https?://player\.vimeo\.com/video/[^\"\'<> ]+',
]
found=[]
for p in patterns:
    for x in re.findall(p,text,re.I):
        x=html.unescape(x).replace('\\u0026','&').replace('\\/','/')
        if x not in found: found.append(x)
lines=[]
for line in text.splitlines():
    lo=line.lower()
    if any(k in lo for k in ['m3u8','mp4','videoid','video-url','video_url','playlist','manifest','jwplayer','brightcove','vimeo','youtube']):
        lines.append(line.strip()[:8000])
(out/'sources.txt').write_text('PAGE='+URL+'\nSTATUS='+str(r.status_code)+'\n\nFOUND\n'+'\n'.join(found)+'\n\nLINES\n'+'\n'.join(lines[:300]),encoding='utf-8')
print('FOUND',found)
