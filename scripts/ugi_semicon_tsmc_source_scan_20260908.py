from pathlib import Path
import subprocess

OUT = Path('public/ugi/editorial/2026-09-08/semicon-tsmc-scan')
SRC = Path('/tmp/ugi_semicon_tsmc_sources')
OUT.mkdir(parents=True, exist_ok=True)
SRC.mkdir(parents=True, exist_ok=True)

VIDEOS = {
    'rd': 'https://www.youtube.com/watch?v=-Al6hyXnqVg',
    'arizona': 'https://www.youtube.com/watch?v=JO9CkKGbDBs',
    'fab': 'https://www.youtube.com/watch?v=divOKxuYklM',
}

def run(cmd):
    print('RUN', ' '.join(map(str, cmd)), flush=True)
    subprocess.run([str(x) for x in cmd], check=True)

for key, url in VIDEOS.items():
    target = SRC / f'{key}.mp4'
    if not target.exists():
        run(['yt-dlp','--no-playlist','-f','bv*[height<=1080]+ba/b[height<=1080]','--merge-output-format','mp4','-o',str(target),url])

    # Contact sheet: 12 frames from first ~110 seconds, enough to map branded/company moments.
    frames=[]
    for i,t in enumerate([0,5,10,15,20,30,40,50,60,75,90,105]):
        f = SRC / f'{key}_{i:02d}.jpg'
        run(['ffmpeg','-y','-ss',str(t),'-i',str(target),'-frames:v','1','-vf','scale=480:-2','-q:v','2',str(f)])
        frames.append(f)
    args=[]
    for f in frames:
        args += ['-i', str(f)]
    filter_parts=[]
    for i in range(len(frames)):
        filter_parts.append(f'[{i}:v]scale=480:270:force_original_aspect_ratio=decrease,pad=480:270:(ow-iw)/2:(oh-ih)/2:black[v{i}]')
    layout='|'.join([
        '0_0','480_0','960_0','1440_0',
        '0_270','480_270','960_270','1440_270',
        '0_540','480_540','960_540','1440_540'
    ])
    fc=';'.join(filter_parts)+';'+''.join(f'[v{i}]' for i in range(len(frames)))+f'xstack=inputs={len(frames)}:layout={layout}:fill=black[out]'
    sheet=OUT / f'{key}_contact.jpg'
    run(['ffmpeg','-y',*args,'-filter_complex',fc,'-map','[out]','-frames:v','1',str(sheet)])

(OUT/'README.txt').write_text('SOURCE SCAN ONLY — official TSMC videos for UGI editorial. Not for publication.\n', encoding='utf-8')
print('DONE')
