from pathlib import Path
import urllib.request, re, html

OUT = Path('public/ugi/editorial/2026-09-08/semicon-tsmc-scan')
OUT.mkdir(parents=True, exist_ok=True)

PAGES = {
    'gallery': 'https://pr.tsmc.com/english/gallery-videos',
    'careers2025': 'https://www.tsmc.com/static/english/careers/campus_recruitment_2025/index.html',
    'careers2024': 'https://www.tsmc.com/static/english/careers/campus_recruitment_2024/index.html',
}

lines=[]
for key,url in PAGES.items():
    req=urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=60) as r:
        text=r.read().decode('utf-8','ignore')
    (OUT/f'{key}.html').write_text(text, encoding='utf-8')
    lines.append(f'PAGE {key} {url}')
    decoded=html.unescape(text)
    # collect explicit media URLs and surrounding snippets likely to carry video source data
    urls=set(re.findall(r'https?://[^\"\'<>\\s]+', decoded))
    for u in sorted(urls):
        lu=u.lower()
        if any(x in lu for x in ['.mp4','.m3u8','.webm','youtube','youtu.be','vimeo','video']):
            lines.append(u)
    for m in re.finditer(r'(?i)(?:mp4|m3u8|video|youtube|vimeo)', decoded):
        a=max(0,m.start()-220); b=min(len(decoded),m.end()+320)
        snippet=' '.join(decoded[a:b].split())
        if snippet not in lines:
            lines.append('SNIP '+snippet)

(OUT/'probe.txt').write_text('\n'.join(lines), encoding='utf-8')
(OUT/'README.txt').write_text('SOURCE PROBE ONLY — official TSMC pages. Not for publication.\n', encoding='utf-8')
print('\n'.join(lines[:200]))
