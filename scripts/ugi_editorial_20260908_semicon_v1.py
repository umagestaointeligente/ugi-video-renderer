from pathlib import Path
import subprocess

ROOT = Path('public/ugi/editorial/2026-09-08')
SRC = ROOT / 'semicon_probe/source.mp4'
WORK = Path('/tmp/ugi_semicon_v1')
WORK.mkdir(parents=True, exist_ok=True)
OUT = ROOT / 'video-semicon-taiwan-preview-v1.mp4'
QA = ROOT / 'video-semicon-taiwan-preview-v1-qa.jpg'


def run(cmd):
    print('RUN', ' '.join(str(x) for x in cmd))
    subprocess.run([str(x) for x in cmd], check=True)

# Only real SEMICON Taiwan 2026 moving footage. No reporter/talking-head filler.
# 18-30: exhibition floor + physical SEMICON branding
# 36-42: opening ceremony
# 42-48: Ajit Manocha, SEMI CEO, on official event stage
# 57-63 and 69-75: opening leadership/industry ceremony
# 96-102: Taiwan Premier at official SEMICON podium
# 110-116: physical SEMICON sign + attendees
segments = [
    (18.0, 6.0),
    (24.0, 6.0),
    (36.0, 6.0),
    (42.0, 6.0),
    (57.0, 6.0),
    (69.0, 6.0),
    (96.0, 6.0),
    (110.0, 6.0),
]
clips=[]
for i,(start,length) in enumerate(segments):
    out=WORK/f'clip_{i:02d}.mp4'
    vf=(
        '[0:v]split=2[bg][fg];'
        '[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,'
        'gblur=sigma=24,eq=brightness=-0.38[bg2];'
        '[fg]scale=1080:608:force_original_aspect_ratio=decrease[fg2];'
        '[bg2][fg2]overlay=(W-w)/2:300[v]'
    )
    run(['ffmpeg','-y','-ss',str(start),'-i',str(SRC),'-t',str(length),
         '-filter_complex',vf,'-map','[v]','-an','-r','30','-c:v','libx264','-preset','veryfast','-crf','19',str(out)])
    clips.append(out)
concat=WORK/'concat.txt'
concat.write_text(''.join(f"file '{p}'\n" for p in clips),encoding='utf-8')
base=WORK/'base.mp4'
run(['ffmpeg','-y','-f','concat','-safe','0','-i',str(concat),'-c','copy',str(base)])

script=(
    'Uma feira em Taipei ajuda a entender por que Taiwan continua no centro da corrida global por chips. '
    'A SEMICON Taiwan 2026 reuniu mais de mil e trezentos expositores, com empresas, governos e líderes da indústria discutindo inteligência artificial, produção avançada e novas cadeias de suprimento. '
    'Mas existe um paradoxo de gestão aqui. A concentração que transformou Taiwan em peça indispensável da tecnologia mundial também criou um risco que clientes e governos tentam reduzir. '
    'Quanto mais crítica é uma capacidade, mais perigoso é depender de um único lugar. '
    'Para empresas, a lição é simples: vantagem competitiva e dependência podem nascer da mesma fonte. '
    'Sua cadeia está preparada para essa concentração?'
)
audio=WORK/'narration.mp3'
run(['edge-tts','--voice','pt-BR-AntonioNeural','--rate','+11%','--text',script,'--write-media',str(audio)])

# Captions: semantic blocks, max 2 lines each. Timings fit the 48s source bed.
srt=WORK/'captions.srt'
def ts(s):
    ms=int(round((s-int(s))*1000)); x=int(s); return f'{x//3600:02d}:{(x//60)%60:02d}:{x%60:02d},{ms:03d}'
items=[
    (0.0,5.5,'Uma feira em Taipei mostra por que Taiwan\nsegue no centro da corrida global por chips.'),
    (5.5,12.0,'A SEMICON Taiwan 2026 reuniu\nmais de 1.300 expositores.'),
    (12.0,18.5,'Empresas, governos e líderes discutem IA,\nprodução avançada e novas cadeias.'),
    (18.5,25.5,'Mas existe um paradoxo de gestão\npor trás dessa concentração.'),
    (25.5,33.0,'O que tornou Taiwan indispensável\ntambém criou um risco que o mundo tenta reduzir.'),
    (33.0,39.5,'Quanto mais crítica é uma capacidade,\nmais perigoso é depender de um único lugar.'),
    (39.5,45.0,'Vantagem competitiva e dependência\npodem nascer da mesma fonte.'),
    (45.0,48.0,'Sua cadeia está preparada\npara essa concentração?'),
]
with srt.open('w',encoding='utf-8') as f:
    for i,(a,b,t) in enumerate(items,1):
        f.write(f'{i}\n{ts(a)} --> {ts(b)}\n{t}\n\n')

style='FontName=DejaVu Sans,FontSize=24,PrimaryColour=&H00FFFFFF,OutlineColour=&H90000000,BorderStyle=1,Outline=2,Shadow=0,Alignment=2,MarginV=285'
vf=(
    "drawbox=x=0:y=0:w=1080:h=190:color=black@0.62:t=fill,"
    "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='SEMICON TAIWAN 2026':fontcolor=white:fontsize=46:x=54:y=46,"
    "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:text='CHIPS • CADEIA DE SUPRIMENTO • GESTÃO':fontcolor=white:fontsize=25:x=56:y=112,"
    "drawbox=x=0:y=1770:w=1080:h=150:color=black@0.60:t=fill,"
    "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='UGI  •  Uma Gestão Inteligente':fontcolor=white:fontsize=27:x=54:y=1815,"
    "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:text='Fonte visual: TaiwanPlus • SEMICON Taiwan 2026':fontcolor=white:fontsize=19:x=54:y=1860,"
    f"subtitles={srt}:force_style='{style}'"
)
run(['ffmpeg','-y','-i',str(base),'-i',str(audio),'-vf',vf,'-map','0:v','-map','1:a',
     '-t','48','-c:v','libx264','-preset','medium','-crf','19','-c:a','aac','-b:a','160k','-movflags','+faststart',str(OUT)])

# QA sample exact final render at 4, 10, 16, 22, 28, 34, 40, 46s.
frames=[]
for i,t in enumerate([4,10,16,22,28,34,40,46]):
    p=WORK/f'qa_{i}.jpg'
    run(['ffmpeg','-y','-ss',str(t),'-i',str(OUT),'-frames:v','1','-q:v','2',str(p)])
    frames.append(p)
inputs=[]; filters=[]; layout=[]
for i,p in enumerate(frames):
    inputs += ['-i',str(p)]
    filters.append(f'[{i}:v]scale=270:480[v{i}]')
    layout.append(f'{(i%4)*270}_{(i//4)*480}')
fc=';'.join(filters)+';'+''.join(f'[v{i}]' for i in range(len(frames)))+f'xstack=inputs={len(frames)}:layout='+'|'.join(layout)+':fill=black[out]'
run(['ffmpeg','-y',*inputs,'-filter_complex',fc,'-map','[out]','-frames:v','1',str(QA)])
(ROOT/'PREVIEW_ONLY.txt').write_text('PREVIEW ONLY — NVIDIA V2 APPROVED BY USER; SEMICON TAIWAN V1 AWAITING APPROVAL — NOTHING NEW MAY BE SCHEDULED WITHOUT EXPLICIT USER APPROVAL\n',encoding='utf-8')
print('DONE',OUT,OUT.stat().st_size,QA)
