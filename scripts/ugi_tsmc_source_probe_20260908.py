from pathlib import Path
import subprocess

ROOT = Path('public/ugi/editorial/2026-09-08/tsmc_source_probe')
ROOT.mkdir(parents=True, exist_ok=True)
SOURCES = [
    ROOT / 'tsmc_arizona.mp4',
    ROOT / 'tsmc_corporate.mp4',
]


def run(cmd):
    print('RUN', ' '.join(str(x) for x in cmd))
    subprocess.run([str(x) for x in cmd], check=True)


def duration(path):
    p = subprocess.run([
        'ffprobe','-v','error','-show_entries','format=duration',
        '-of','default=nw=1:nk=1',str(path)
    ], capture_output=True, text=True, check=True)
    return float(p.stdout.strip())

for src in SOURCES:
    d = duration(src)
    # 12 evenly spaced samples, avoid first/last seconds.
    times = [max(1.0, (i + 1) * d / 13.0) for i in range(12)]
    frames = []
    for i, t in enumerate(times):
        out = ROOT / f'{src.stem}_qa_{i:02d}.jpg'
        run(['ffmpeg','-y','-ss',f'{t:.2f}','-i',str(src),'-frames:v','1','-q:v','2',str(out)])
        frames.append(out)

    inputs=[]
    filters=[]
    layout=[]
    for i,p in enumerate(frames):
        inputs += ['-i',str(p)]
        filters.append(f'[{i}:v]scale=320:180[v{i}]')
        layout.append(f'{(i%4)*320}_{(i//4)*180}')
    fc=';'.join(filters)+';'+''.join(f'[v{i}]' for i in range(len(frames)))+f'xstack=inputs={len(frames)}:layout='+'|'.join(layout)+':fill=black[out]'
    sheet = ROOT / f'{src.stem}_contact.jpg'
    run(['ffmpeg','-y',*inputs,'-filter_complex',fc,'-map','[out]','-frames:v','1',str(sheet)])

print('TSMC source probe complete')
