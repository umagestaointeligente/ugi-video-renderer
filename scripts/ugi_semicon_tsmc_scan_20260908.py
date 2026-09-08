from pathlib import Path
import subprocess, re, shutil

SRC = Path('public/ugi/editorial/2026-09-08/semicon_probe/source.mp4')
OUTDIR = Path('public/ugi/editorial/2026-09-08/tsmc_semicon_scan')
TMP = Path('/tmp/ugi_tsmc_scan')
OUTDIR.mkdir(parents=True, exist_ok=True)
TMP.mkdir(parents=True, exist_ok=True)

def run(cmd, **kw):
    return subprocess.run([str(x) for x in cmd], check=True, **kw)

def duration(path):
    p=run(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',path],capture_output=True,text=True)
    return float(p.stdout.strip())

d=duration(SRC)
hits=[]
for sec in range(0, int(d)+1):
    frame=TMP/f'f_{sec:04d}.jpg'
    subprocess.run(['ffmpeg','-loglevel','error','-y','-ss',str(sec),'-i',str(SRC),'-frames:v','1','-vf','scale=1280:-2',str(frame)],check=True)
    p=subprocess.run(['tesseract',str(frame),'stdout','--psm','11'],capture_output=True,text=True)
    text=(p.stdout or '').upper()
    compact=re.sub(r'[^A-Z0-9]+','',text)
    if 'TSMC' in compact or 'T5MC' in compact or 'TSM' in compact:
        hits.append((sec, re.sub(r'\s+',' ',text).strip()[:220]))

windows=[]
for sec,text in hits:
    if not windows or sec-windows[-1][1]>3:
        windows.append([sec,sec,[text]])
    else:
        windows[-1][1]=sec
        windows[-1][2].append(text)

report=OUTDIR/'scan_report.txt'
with report.open('w',encoding='utf-8') as f:
    f.write(f'DURATION={d:.2f}s\n')
    f.write(f'HIT_SECONDS={len(hits)}\n')
    for a,b,texts in windows:
        f.write(f'WINDOW {a}-{b}: {" | ".join(texts[:3])}\n')

selected=[]
for sec,_ in hits[:24]:
    src=TMP/f'f_{sec:04d}.jpg'
    dst=OUTDIR/f'hit_{sec:04d}.jpg'
    shutil.copy2(src,dst)
    selected.append(dst)

if len(selected)==1:
    shutil.copy2(selected[0], OUTDIR/'tsmc_hits_contact.jpg')
elif len(selected)>1:
    inputs=[]; filters=[]; layout=[]
    cols=4; w=320; h=180
    for i,p in enumerate(selected):
        inputs += ['-i',str(p)]
        filters.append(f'[{i}:v]scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2[v{i}]')
        layout.append(f'{(i%cols)*w}_{(i//cols)*h}')
    fc=';'.join(filters)+';'+''.join(f'[v{i}]' for i in range(len(selected)))+f'xstack=inputs={len(selected)}:layout='+'|'.join(layout)+':fill=black[out]'
    subprocess.run(['ffmpeg','-loglevel','error','-y',*inputs,'-filter_complex',fc,'-map','[out]','-frames:v','1',str(OUTDIR/'tsmc_hits_contact.jpg')],check=True)
print(report.read_text(encoding='utf-8'))
