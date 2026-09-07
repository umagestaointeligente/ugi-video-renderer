from pathlib import Path
import subprocess, urllib.request

ROOT = Path('public/ugi/editorial/2026-09-08')
WORK = Path('/tmp/ugi_20260908_v2')
ROOT.mkdir(parents=True, exist_ok=True)
WORK.mkdir(parents=True, exist_ok=True)

# Official company/event footage only.
NVIDIA_GTC_ROBOTS = 'https://blogs.nvidia.com/wp-content/uploads/2026/04/GTC26-Robots_16x9_v3-2-1.mp4'
NVIDIA_BUILD_A_CLAW = 'https://blogs.nvidia.com/wp-content/uploads/2026/05/build-a-claw-13mb.mp4'
NVIDIA_CONFIDENTIAL = 'https://blogs.nvidia.com/wp-content/uploads/2026/05/confidential-computing-demo_16x9_15MB.mp4'
JLR_CORPORATE = 'https://media.production.jlrms.com/2020-10-21/video/e3e1104f-42e2-4674-986b-8ba7f8b565b0/JLR%20Corporate%20-%20With%20Text%20_0.mp4?VersionId=yV9VI3SMEy4d.GxW1HbLxqOicreL9ZIo'
JLR_ASSEMBLY = 'https://media.production.jlrms.com/2020-05-12/video/afd1b9cd-990c-4f9f-a5a9-aeee90959ddc/Visor%20Manufacture%20%26%20Assembly_V5.mp4?VersionId=UB0asixOMPj5bR8I.7osNVKEZuUjmZDj'


def run(cmd):
    print('RUN', ' '.join(cmd))
    subprocess.run(cmd, check=True)


def dl(url, name):
    p = WORK / name
    req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=240) as r, open(p,'wb') as f:
        while True:
            b = r.read(1024*1024)
            if not b: break
            f.write(b)
    print(name, p.stat().st_size)
    return p


def dur(path):
    p = subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(path)],capture_output=True,text=True,check=True)
    return float(p.stdout.strip())


def tts(text, out):
    run(['edge-tts','--voice','pt-BR-AntonioNeural','--rate','+1%','--text',text,'--write-media',str(out)])


def srt_time(t):
    ms = int(round((t-int(t))*1000)); s=int(t)%60; m=(int(t)//60)%60; h=int(t)//3600
    return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'


def make_srt(lines, out):
    with open(out,'w',encoding='utf-8') as f:
        for i,(a,b,txt) in enumerate(lines,1):
            f.write(f'{i}\n{srt_time(a)} --> {srt_time(b)}\n{txt}\n\n')


def prep_scene(src, start, seconds, out):
    # Preserve the whole 16:9 company frame. No destructive zoom/crop.
    fc = "[0:v]split=2[bg][fg];[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=28,eq=brightness=-0.40[bg2];[fg]scale=1010:568:force_original_aspect_ratio=decrease[fg2];[bg2][fg2]overlay=(W-w)/2:235[v]"
    run(['ffmpeg','-y','-ss',str(start),'-i',str(src),'-t',str(seconds),'-filter_complex',fc,'-map','[v]','-an','-r','30','-c:v','libx264','-preset','veryfast','-crf','19',str(out)])


def build(name, scene_specs, script, captions, headline):
    audio = WORK/f'{name}.mp3'; tts(script,audio)
    audio_dur = dur(audio)
    srt = WORK/f'{name}.srt'; make_srt(captions,srt)

    clips=[]
    for i,(src,start,seconds) in enumerate(scene_specs):
        c = WORK/f'{name}_scene_{i}.mp4'
        prep_scene(src,start,seconds,c)
        clips.append(c)
    concat=WORK/f'{name}_concat.txt'
    concat.write_text(''.join(f"file '{p}'\n" for p in clips),encoding='utf-8')
    base=WORK/f'{name}_base.mp4'
    run(['ffmpeg','-y','-f','concat','-safe','0','-i',str(concat),'-t',str(audio_dur+0.2),'-c','copy',str(base)])

    style="FontName=DejaVu Sans,FontSize=22,PrimaryColour=&H00FFFFFF,OutlineColour=&H90000000,BorderStyle=1,Outline=2,Shadow=0,Alignment=2,MarginV=310"
    vf=(f"drawbox=x=0:y=0:w=1080:h=182:color=black@0.58:t=fill,"
        f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='{headline}':fontcolor=white:fontsize=41:x=52:y=62,"
        f"drawbox=x=0:y=1810:w=1080:h=110:color=black@0.48:t=fill,"
        f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='UGI  •  Uma Gestão Inteligente':fontcolor=white:fontsize=24:x=48:y=1845,"
        f"subtitles={srt}:force_style='{style}'")
    out=ROOT/f'{name}.mp4'
    run(['ffmpeg','-y','-i',str(base),'-i',str(audio),'-vf',vf,'-map','0:v','-map','1:a','-t',str(audio_dur),'-c:v','libx264','-preset','medium','-crf','18','-c:a','aac','-b:a','160k','-movflags','+faststart',str(out)])
    run(['ffprobe','-v','error','-show_entries','stream=width,height,codec_name','-show_entries','format=duration,size','-of','json',str(out)])
    return out

nv1=dl(NVIDIA_GTC_ROBOTS,'nvidia_gtc_robots.mp4')
nv2=dl(NVIDIA_BUILD_A_CLAW,'nvidia_build_a_claw.mp4')
nv3=dl(NVIDIA_CONFIDENTIAL,'nvidia_confidential.mp4')
jlr1=dl(JLR_CORPORATE,'jlr_corporate.mp4')
jlr2=dl(JLR_ASSEMBLY,'jlr_assembly.mp4')

nvidia_script = ('A NVIDIA continua sendo a referência global em chips de inteligência artificial. '
'Em eventos oficiais como a GTC, a companhia mostra como está expandindo seu ecossistema de computação, software e infraestrutura. '
'Mas, na China, essa vantagem começou a ser pressionada: concorrentes locais ganharam escala e a participação da NVIDIA caiu para cerca de cinquenta e cinco por cento. '
'Para a gestão, o aprendizado vai além de tecnologia. Quando um fornecedor dominante deixa de ser praticamente insubstituível, muda o poder de negociação, muda o custo e muda o risco da operação. '
'A pergunta UGI é simples: sua empresa conhece hoje o custo real de substituir o fornecedor que parece impossível trocar?')
nvidia_caps=[
(0,6,'A NVIDIA continua sendo referência global em chips de IA.'),
(6,13,'Na GTC, a empresa mostra seu ecossistema de computação e infraestrutura.'),
(13,21,'Na China, concorrentes locais ganharam escala.'),
(21,28,'A participação da NVIDIA caiu para cerca de 55%.'),
(28,36,'Quando o dominante deixa de ser insubstituível, o poder muda.'),
(36,44,'Mudam negociação, custo e risco operacional.'),
(44,52,'Sua empresa conhece o custo real de trocar seu fornecedor crítico?')]

# Five distinct, non-repeating official NVIDIA scenes.
nvidia_scenes=[
(nv1,0,10),
(nv1,10,9),
(nv2,0,10),
(nv2,10,9),
(nv3,0,14),
]

jlr_script = ('A JLR, Jaguar Land Rover, anunciou uma reestruturação que deve eliminar cerca de quatro mil postos. '
'Antes de olhar apenas para os carros, vale lembrar que estamos falando de uma companhia industrial global, com fábricas, tecnologia, engenharia e milhares de pessoas na operação. '
'A meta é reduzir custos e aproximar a empresa do ponto de equilíbrio. Mas a JLR mantém entre quinze e dezoito bilhões de libras em investimentos em eletrificação, digital e manufatura. '
'Na gestão, cortar estrutura e proteger investimento futuro podem fazer parte da mesma decisão. '
'A pergunta é: onde o capital ainda cria vantagem competitiva e onde virou apenas custo?')
jlr_caps=[
(0,7,'A JLR (Jaguar Land Rover) anunciou uma reestruturação de cerca de 4.000 postos.'),
(7,15,'É uma companhia industrial global — não apenas uma marca de carros.'),
(15,23,'A meta é reduzir custos e aproximar a operação do equilíbrio.'),
(23,32,'Mesmo assim, mantém £15–18 bi em eletrificação, digital e manufatura.'),
(32,41,'Cortar estrutura e proteger o futuro podem fazer parte da mesma decisão.'),
(41,50,'Onde o capital ainda cria vantagem — e onde virou apenas custo?')]

# Corporate context first, manufacturing second. No ad-like vehicle opening.
jlr_scenes=[
(jlr1,0,11),
(jlr1,11,10),
(jlr2,0,10),
(jlr2,10,10),
(jlr1,21,11),
]

build('video-nvidia-company-preview-v2',nvidia_scenes,nvidia_script,nvidia_caps,'NVIDIA: quando a vantagem começa a ser pressionada')
build('video-jlr-company-preview-v2',jlr_scenes,jlr_script,jlr_caps,'JLR (Jaguar Land Rover): cortar sem perder o futuro')

(ROOT/'PREVIEW_ONLY.txt').write_text('PREVIEW ONLY — NOT APPROVED — DO NOT PUBLISH OR SCHEDULE\n',encoding='utf-8')
print('DONE V2')
