from pathlib import Path
import subprocess, urllib.parse

OUT = Path('public/ugi/editorial/2026-09-08/semicon-tsmc-scan')
SRC = Path('/tmp/ugi_semicon_tsmc_sources')
OUT.mkdir(parents=True, exist_ok=True)
SRC.mkdir(parents=True, exist_ok=True)

SOURCES = {
    'whitehouse_tsmc': {
        'url': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/' + urllib.parse.quote('President Trump Makes an Investment Announcement.webm', safe=''),
        'times': [80, 90, 100, 285, 300, 315, 330, 345, 360, 375, 390, 405],
        'license': 'U.S. White House / U.S. federal government work; Wikimedia Commons public-domain marking.'
    },
    'japan_tsmc': {
        'url': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/' + urllib.parse.quote('TSMC及び地元中小企業との車座 岸田総理.webm', safe=''),
        'times': [0, 8, 16, 24, 32, 40, 50, 60, 70, 82, 96, 112],
        'license': 'Prime Minister’s Office of Japan; Wikimedia Commons CC BY 3.0.'
    },
    'dvids_tsmc_arizona': {
        'url': 'https://d34w7g4gy10iej.cloudfront.net/video/2212/DOD_109358136/DOD_109358136.mp4',
        'times': [0, 30, 60, 120, 180, 240, 330, 450, 600, 750, 900, 1020],
        'license': 'White House Communications Agency via DVIDS, Video ID 866988; DVIDS marks the work PUBLIC DOMAIN.'
    },
}

def run(cmd, check=True):
    print('RUN', ' '.join(map(str, cmd)), flush=True)
    return subprocess.run([str(x) for x in cmd], check=check)

for key, spec in SOURCES.items():
    url=spec['url']
    src = SRC / f'{key}'
    ext='.mp4' if '.mp4' in url else '.webm'
    src=src.with_suffix(ext)
    rc=run(['curl','-L','--fail','--retry','2','-A','Mozilla/5.0','-o',src,url], check=False)
    if rc.returncode != 0 or not src.exists() or src.stat().st_size < 100000:
        (OUT/f'{key}_FAILED.txt').write_text(f'FAILED TO FETCH {url}\n', encoding='utf-8')
        continue
    frames=[]
    for i,t in enumerate(spec['times']):
        f = SRC / f'{key}_{i:02d}.jpg'
        rc=run(['ffmpeg','-y','-ss',str(t),'-i',src,'-frames:v','1','-vf','scale=480:270:force_original_aspect_ratio=decrease,pad=480:270:(ow-iw)/2:(oh-ih)/2:black','-q:v','2',f], check=False)
        if rc.returncode == 0 and f.exists(): frames.append(f)
    if not frames:
        (OUT/f'{key}_FAILED.txt').write_text(f'FETCHED BUT NO FRAMES {url}\n', encoding='utf-8')
        continue
    args=[]
    for f in frames: args += ['-i', f]
    fc=[]
    for i in range(len(frames)): fc.append(f'[{i}:v]scale=480:270[v{i}]')
    positions=[]
    for i in range(len(frames)):
        positions.append(f'{(i%4)*480}_{(i//4)*270}')
    filt=';'.join(fc)+';'+''.join(f'[v{i}]' for i in range(len(frames)))+f'xstack=inputs={len(frames)}:layout={"|".join(positions)}:fill=black[out]'
    sheet=OUT/f'{key}_contact.jpg'
    run(['ffmpeg','-y',*args,'-filter_complex',filt,'-map','[out]','-frames:v','1',sheet])
    (OUT/f'{key}_source.txt').write_text(f"SOURCE: {url}\nLICENSE NOTE: {spec['license']}\n", encoding='utf-8')

(OUT/'README.txt').write_text('SOURCE SCAN ONLY — licensed/public-domain company-context footage for TSMC/SEMICON editorial. Not for publication.\n', encoding='utf-8')
print('DONE')
