from pathlib import Path
import subprocess

OUT = Path('public/ugi/editorial/2026-09-08/semicon_probe')
OUT.mkdir(parents=True, exist_ok=True)
VIDEO_URL = 'https://www.youtube.com/watch?v=cjlfQCk82Bg'
video = OUT / 'source.mp4'


def run(cmd):
    print('RUN', ' '.join(str(x) for x in cmd))
    subprocess.run([str(x) for x in cmd], check=True)

run(['yt-dlp','-f','bv*[height<=720]+ba/b[height<=720]','--merge-output-format','mp4','-o',str(video),VIDEO_URL])

# Extract 20 evenly spaced frames for editorial relevance review.
probe = subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(video)],capture_output=True,text=True,check=True)
dur = float(probe.stdout.strip())
times = [dur*(i+1)/21 for i in range(20)]
frames=[]
for i,t in enumerate(times):
    p=OUT/f'f_{i:02d}.jpg'
    run(['ffmpeg','-y','-ss',f'{t:.3f}','-i',str(video),'-frames:v','1','-vf','scale=360:-2','-q:v','2',str(p)])
    frames.append(p)

inputs=[]
filters=[]
for i,p in enumerate(frames):
    inputs += ['-i',str(p)]
    filters.append(f'[{i}:v]scale=360:202[v{i}]')
layout=[]
for i in range(len(frames)):
    x=(i%4)*360; y=(i//4)*202
    layout.append(f'{x}_{y}')
filter_complex=';'.join(filters)+';'+''.join(f'[v{i}]' for i in range(len(frames)))+f'xstack=inputs={len(frames)}:layout='+'|'.join(layout)+':fill=black[out]'
contact=OUT/'contact.jpg'
run(['ffmpeg','-y',*inputs,'-filter_complex',filter_complex,'-map','[out]','-frames:v','1',str(contact)])
(OUT/'README.txt').write_text(f'SOURCE={VIDEO_URL}\nDURATION={dur:.2f}\nTIMES=' + ','.join(f'{t:.2f}' for t in times) + '\n',encoding='utf-8')
print('DONE', contact)
