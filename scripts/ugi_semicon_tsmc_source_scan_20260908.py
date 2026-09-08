from pathlib import Path
import subprocess, urllib.parse

OUT = Path('public/ugi/editorial/2026-09-08/semicon-tsmc-scan')
SRC = Path('/tmp/ugi_semicon_tsmc_sources')
OUT.mkdir(parents=True, exist_ok=True)
SRC.mkdir(parents=True, exist_ok=True)

SOURCES = {
    'whitehouse_tsmc': {
        'filename': 'President Trump Makes an Investment Announcement.webm',
        'times': [80, 90, 100, 285, 300, 315, 330, 345, 360, 375, 390, 405],
        'license': 'U.S. White House / U.S. federal government work; Wikimedia Commons file page marks public domain.'
    },
    'japan_tsmc': {
        'filename': 'TSMC及び地元中小企業との車座 岸田総理.webm',
        'times': [0, 8, 16, 24, 32, 40, 50, 60, 70, 82, 96, 112],
        'license': 'Prime Minister’s Office of Japan; Wikimedia Commons CC BY 3.0.'
    },
}

def run(cmd):
    print('RUN', ' '.join(map(str, cmd)), flush=True)
    subprocess.run([str(x) for x in cmd], check=True)

for key, spec in SOURCES.items():
    fn = spec['filename']
    quoted = urllib.parse.quote(fn, safe='')
    url = f'https://commons.wikimedia.org/wiki/Special:Redirect/file/{quoted}'
    src = SRC / f'{key}.webm'
    run(['curl','-L','--fail','--retry','2','-A','Mozilla/5.0','-o',src,url])
    frames=[]
    for i,t in enumerate(spec['times']):
        f = SRC / f'{key}_{i:02d}.jpg'
        run(['ffmpeg','-y','-ss',str(t),'-i',src,'-frames:v','1','-vf','scale=480:270:force_original_aspect_ratio=decrease,pad=480:270:(ow-iw)/2:(oh-ih)/2:black','-q:v','2',f])
        frames.append(f)
    args=[]
    for f in frames: args += ['-i', f]
    fc=[]
    for i in range(len(frames)):
        fc.append(f'[{i}:v]scale=480:270[v{i}]')
    layout='|'.join(['0_0','480_0','960_0','1440_0','0_270','480_270','960_270','1440_270','0_540','480_540','960_540','1440_540'])
    filt=';'.join(fc)+';'+''.join(f'[v{i}]' for i in range(len(frames)))+f'xstack=inputs={len(frames)}:layout={layout}:fill=black[out]'
    sheet=OUT/f'{key}_contact.jpg'
    run(['ffmpeg','-y',*args,'-filter_complex',filt,'-map','[out]','-frames:v','1',sheet])
    (OUT/f'{key}_source.txt').write_text(f"SOURCE: {url}\nLICENSE NOTE: {spec['license']}\n", encoding='utf-8')

(OUT/'README.txt').write_text('SOURCE SCAN ONLY — licensed/public-domain company-context footage for TSMC/SEMICON editorial. Not for publication.\n', encoding='utf-8')
print('DONE')
