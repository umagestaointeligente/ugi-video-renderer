from pathlib import Path
import subprocess, json, math

OUT = Path('public/ugi/editorial/2026-09-08')
WORK = Path('/tmp/ugi_tsmc_sources')
OUT.mkdir(parents=True, exist_ok=True)
WORK.mkdir(parents=True, exist_ok=True)

SOURCES = {
    'arizona_fab': 'https://www.youtube.com/watch?v=MiKIaKgQH9s',
    'life_at_tsmc': 'https://www.youtube.com/watch?v=hv81XD_86RY',
    'global_rd': 'https://www.youtube.com/watch?v=-Al6hyXnqVg',
    'corporate': 'https://www.youtube.com/watch?v=hGdI-u0tyzA',
}

def run(cmd):
    print('RUN', ' '.join(str(x) for x in cmd), flush=True)
    subprocess.run([str(x) for x in cmd], check=True)

def duration(path):
    p = subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(path)], capture_output=True, text=True, check=True)
    return float(p.stdout.strip())

def download(name, url):
    tmpl = str(WORK / f'{name}.%(ext)s')
    cmd = [
        'yt-dlp','--no-playlist','--no-warnings','--restrict-filenames',
        '--extractor-args','youtube:player_client=android,web',
        '-f','bv*[height<=1080]+ba/b[height<=1080]',
        '--merge-output-format','mp4','-o',tmpl,url
    ]
    run(cmd)
    candidates = sorted(WORK.glob(f'{name}.*'))
    videos = [p for p in candidates if p.suffix.lower() in ('.mp4','.webm','.mkv','.mov')]
    if not videos:
        raise RuntimeError(f'No downloaded video for {name}')
    return videos[0]

def contact_sheet(name, src):
    d = duration(src)
    # 12 samples avoiding first/last title slates.
    times = [max(0.5, d * frac) for frac in (0.05,0.13,0.21,0.29,0.37,0.45,0.53,0.61,0.69,0.77,0.85,0.93)]
    frames=[]
    for i,t in enumerate(times):
        p = WORK / f'{name}_{i:02d}.jpg'
        run(['ffmpeg','-y','-ss',f'{t:.2f}','-i',src,'-frames:v','1','-vf','scale=480:-2','-q:v','2',p])
        frames.append(p)
    args=[]
    for p in frames:
        args += ['-i',p]
    filters=[]
    for i in range(len(frames)):
        filters.append(f'[{i}:v]scale=360:203[v{i}]')
    layout=[]
    for i in range(len(frames)):
        x=(i%3)*360; y=(i//3)*203
        layout.append(f'{x}_{y}')
    fc=';'.join(filters)+';'+''.join(f'[v{i}]' for i in range(len(frames)))+f"xstack=inputs={len(frames)}:layout={'|'.join(layout)}:fill=black[out]"
    out=OUT/f'tsmc-source-{name}-qa.jpg'
    run(['ffmpeg','-y',*args,'-filter_complex',fc,'-map','[out]','-frames:v','1',out])
    return {'source':str(src),'duration':d,'qa':str(out),'times':times}

manifest={}
for name,url in SOURCES.items():
    src=download(name,url)
    manifest[name]={'url':url,**contact_sheet(name,src)}

(OUT/'tsmc-source-audit.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps(manifest,indent=2))
