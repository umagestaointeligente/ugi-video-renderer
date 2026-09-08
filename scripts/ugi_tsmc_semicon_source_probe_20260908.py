from pathlib import Path
import subprocess, json, os, shlex

ROOT = Path('public/ugi/editorial/2026-09-08/tsmc-probe')
WORK = Path('/tmp/ugi_tsmc_probe')
ROOT.mkdir(parents=True, exist_ok=True)
WORK.mkdir(parents=True, exist_ok=True)

SOURCES = {
    'arizona_fab': 'https://www.youtube.com/watch?v=MiKIaKgQH9s',
    'rnd_center': 'https://www.youtube.com/watch?v=-Al6hyXnqVg',
    'corporate': 'https://www.youtube.com/watch?v=hGdI-u0tyzA',
    'life_at_tsmc': 'https://www.youtube.com/watch?v=hv81XD_86RY',
}

def run(cmd):
    print('RUN', ' '.join(shlex.quote(str(x)) for x in cmd), flush=True)
    subprocess.run([str(x) for x in cmd], check=True)

def probe_duration(path):
    p = subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(path)], capture_output=True, text=True, check=True)
    return float(p.stdout.strip())

manifest = {}
for name, url in SOURCES.items():
    outtmpl = str(WORK / f'{name}.%(ext)s')
    run(['yt-dlp','--no-playlist','-f','bv*[height<=1080]+ba/b[height<=1080]','--merge-output-format','mp4','-o',outtmpl,url])
    candidates = sorted(WORK.glob(f'{name}.*'))
    video = next((p for p in candidates if p.suffix.lower() in {'.mp4','.mkv','.webm','.mov'}), None)
    if not video:
        raise RuntimeError(f'No video for {name}')
    dur = probe_duration(video)
    # 12 evenly spaced frames, avoiding very first/last frames.
    times = [dur*(i+1)/13 for i in range(12)]
    frames=[]
    for idx,t in enumerate(times):
        jpg = WORK / f'{name}_{idx:02d}.jpg'
        run(['ffmpeg','-y','-ss',f'{t:.3f}','-i',video,'-frames:v','1','-q:v','2',jpg])
        frames.append(jpg)
    # Contact sheet 4x3 at 320x180 tiles.
    cmd=['ffmpeg','-y']
    for f in frames: cmd += ['-i',f]
    parts=[]
    for i in range(12): parts.append(f'[{i}:v]scale=320:180[v{i}]')
    layout='|'.join([
        '0_0','320_0','640_0','960_0',
        '0_180','320_180','640_180','960_180',
        '0_360','320_360','640_360','960_360'])
    fc=';'.join(parts)+';'+''.join(f'[v{i}]' for i in range(12))+f'xstack=inputs=12:layout={layout}:fill=black[out]'
    sheet = ROOT / f'{name}_contact.jpg'
    run(cmd+['-filter_complex',fc,'-map','[out]','-frames:v','1',sheet])
    manifest[name]={'url':url,'duration':dur,'sheet':str(sheet)}

(ROOT/'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
print('DONE')
