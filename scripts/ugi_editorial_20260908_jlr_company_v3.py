from pathlib import Path
import subprocess, urllib.request

ROOT = Path('public/ugi/editorial/2026-09-08')
WORK = Path('/tmp/ugi_jlr_v3')
ROOT.mkdir(parents=True, exist_ok=True)
WORK.mkdir(parents=True, exist_ok=True)

OPEN_INNOVATION = 'https://media.production.jlrms.com/2022-04-25/video/cf29bd6d-c0a2-43c2-87b7-46e7a453162d/JLR_Open_Innovation_Film_Clean_270422.mp4?VersionId=iYAyDM_OP8.nZ5sEQjti3pvIhDZFo3Pf'
NAIC = 'https://media.production.jlrms.com/2020-02-26/video/7bf06db1-201d-4647-b476-eb8bb7fcb2c4/J905428_LR_NAIC_SocialFilm_90s.mp4?VersionId=zX3_U2F9yZciSVeAHWfNQKdSfS8yomgg'
ASSEMBLY = 'https://media.production.jlrms.com/2020-05-12/video/afd1b9cd-990c-4f9f-a5a9-aeee90959ddc/Visor%20Manufacture%20%26%20Assembly_V5.mp4?VersionId=UB0asixOMPj5bR8I.7osNVKEZuUjmZDj'


def run(cmd):
    print('RUN', ' '.join(str(x) for x in cmd))
    subprocess.run([str(x) for x in cmd], check=True)


def dl(url, name):
    p = WORK / name
    if not p.exists():
        req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=180) as r, open(p, 'wb') as f:
            while True:
                b = r.read(1024 * 1024)
                if not b:
                    break
                f.write(b)
    print(name, p.stat().st_size)
    return p


def dur(path):
    p = subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(path)], capture_output=True, text=True, check=True)
    return float(p.stdout.strip())


def ts(t):
    ms = int(round((t-int(t))*1000)); s=int(t)%60; m=(int(t)//60)%60; h=int(t)//3600
    return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'


def make_srt(items, path):
    with open(path,'w',encoding='utf-8') as f:
        for i,(a,b,text) in enumerate(items,1):
            f.write(f'{i}\n{ts(a)} --> {ts(b)}\n{text}\n\n')


def tts(text, out):
    run(['edge-tts','--voice','pt-BR-AntonioNeural','--rate','+2%','--text',text,'--write-media',out])

open_video = dl(OPEN_INNOVATION, 'jlr_open_innovation.mp4')
naic_video = dl(NAIC, 'jlr_naic.mp4')
assembly_video = dl(ASSEMBLY, 'jlr_assembly.mp4')

# Company-first sequence: corporate innovation, engineering centre and manufacturing.
# No driving shots and no generic auto-ad B-roll.
segments = [
    (open_video, 0, 6.5, 'open0'),
    (naic_video, 6, 6.0, 'naic0'),
    (open_video, 14, 6.5, 'open1'),
    (naic_video, 24, 6.0, 'naic1'),
    (assembly_video, 3, 6.5, 'assembly0'),
    (open_video, 30, 6.5, 'open2'),
    (naic_video, 42, 6.0, 'naic2'),
    (open_video, 52, 6.0, 'open3'),
]

clips = []
for src, start, length, tag in segments:
    out = WORK / f'{tag}.mp4'
    vf = (
        "[0:v]split=2[bg][fg];"
        "[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=28,eq=brightness=-0.38[bg2];"
        "[fg]scale=1020:574:force_original_aspect_ratio=decrease[fg2];"
        "[bg2][fg2]overlay=(W-w)/2:215[v]"
    )
    run(['ffmpeg','-y','-ss',start,'-i',src,'-t',length,'-filter_complex',vf,'-map','[v]','-an','-r','30','-c:v','libx264','-preset','veryfast','-crf','19',out])
    clips.append(out)

concat = WORK / 'concat.txt'
concat.write_text(''.join(f"file '{p}'\n" for p in clips), encoding='utf-8')
base = WORK / 'base.mp4'
run(['ffmpeg','-y','-f','concat','-safe','0','-i',concat,'-c','copy',base])

script = (
    'A JLR, Jaguar Land Rover, anunciou uma reestruturação que deve eliminar cerca de quatro mil postos. '
    'A companhia reúne as marcas Jaguar e Land Rover e opera centros de engenharia, inovação e manufatura. '
    'O ponto importante é que ela não está simplesmente encolhendo. Quer reduzir custos e aproximar a operação do ponto de equilíbrio, enquanto mantém entre quinze e dezoito bilhões de libras em investimentos em eletrificação, digital e manufatura. '
    'É por isso que este caso é mais sobre alocação de capital do que sobre demissões. '
    'Em gestão, cortar estrutura e proteger capacidade de inovação podem fazer parte da mesma decisão. '
    'A pergunta é: sua empresa sabe diferenciar redução de custo de reposicionamento estratégico?'
)
audio = WORK / 'jlr_v3.mp3'
tts(script, audio)
audio_dur = dur(audio)

# Caption windows are normalized dynamically to the actual narration duration so the final question is never left without CC.
caption_texts = [
    'A JLR — Jaguar Land Rover — anunciou uma reestruturação.',
    'A companhia reúne Jaguar e Land Rover e opera engenharia, inovação e manufatura.',
    'Cerca de 4.000 postos devem ser eliminados.',
    'Mas a companhia não está simplesmente encolhendo.',
    'Ela busca reduzir custos e aproximar a operação do equilíbrio.',
    'E mantém £15–18 bi em eletrificação, digital e manufatura.',
    'O caso é sobre alocação de capital — não só sobre demissões.',
    'Sua empresa diferencia corte de custo de reposicionamento estratégico?',
]
step = audio_dur / len(caption_texts)
caps = [(i*step, min((i+1)*step, audio_dur), text) for i,text in enumerate(caption_texts)]
srt = WORK / 'jlr_v3.srt'
make_srt(caps, srt)

style = 'FontName=DejaVu Sans,FontSize=23,PrimaryColour=&H00FFFFFF,OutlineColour=&H90000000,BorderStyle=1,Outline=2,Shadow=0,Alignment=2,MarginV=270'
vf = (
    "drawbox=x=0:y=0:w=1080:h=170:color=black@0.55:t=fill,"
    "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='JLR (Jaguar Land Rover): corte + reinvestimento':fontcolor=white:fontsize=38:x=52:y=58,"
    "drawbox=x=0:y=1810:w=1080:h=110:color=black@0.44:t=fill,"
    "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='UGI  •  Uma Gestão Inteligente':fontcolor=white:fontsize=25:x=50:y=1845,"
    f"subtitles={srt}:force_style='{style}'"
)

out = ROOT / 'video-jlr-company-preview-v3.mp4'
run(['ffmpeg','-y','-i',base,'-i',audio,'-vf',vf,'-map','0:v','-map','1:a','-shortest','-c:v','libx264','-preset','medium','-crf','19','-c:a','aac','-b:a','160k','-movflags','+faststart',out])
final_dur = dur(out)

# Build QA contact sheet from seven valid points spread across the actual final render.
frames = []
for i,ratio in enumerate([0.05,0.18,0.31,0.44,0.57,0.72,0.90]):
    t = max(0.2, min(final_dur-0.5, final_dur*ratio))
    p = WORK / f'qa_{i}.jpg'
    run(['ffmpeg','-y','-ss',f'{t:.2f}','-i',out,'-frames:v','1','-update','1','-q:v','2',p])
    frames.append(p)

inputs=[]
for p in frames:
    inputs += ['-i', p]
filter_parts=[f'[{i}:v]scale=270:480[v{i}]' for i in range(len(frames))]
layout = '|'.join(['0_0','270_0','540_0','810_0','0_480','270_480','540_480'])
filter_complex = ';'.join(filter_parts) + ';' + ''.join(f'[v{i}]' for i in range(len(frames))) + f'xstack=inputs={len(frames)}:layout={layout}:fill=black[out]'
contact = ROOT / 'video-jlr-company-preview-v3-qa.jpg'
run(['ffmpeg','-y',*inputs,'-filter_complex',filter_complex,'-map','[out]','-frames:v','1','-update','1',contact])

(ROOT / 'PREVIEW_ONLY.txt').write_text('PREVIEW ONLY — NVIDIA V2 APPROVED BY USER; JLR V3 AWAITING APPROVAL — DO NOT SCHEDULE UNTIL EDITORIAL PACKAGE IS RELEASED\n', encoding='utf-8')
print('DONE', out, out.stat().st_size, 'duration', final_dur)
