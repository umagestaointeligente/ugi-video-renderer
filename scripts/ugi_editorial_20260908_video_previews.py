from pathlib import Path
import subprocess, textwrap, urllib.request, os, json, math

ROOT = Path('public/ugi/editorial/2026-09-08')
WORK = Path('/tmp/ugi_20260908')
ROOT.mkdir(parents=True, exist_ok=True)
WORK.mkdir(parents=True, exist_ok=True)

NVIDIA_SRC = 'https://blogs.nvidia.com/wp-content/uploads/2026/05/JHH_booth-tour_sequence_16x9.mp4'
JLR_SRC1 = 'https://media.production.jlrms.com/2020-10-21/video/e3e1104f-42e2-4674-986b-8ba7f8b565b0/JLR%20Corporate%20-%20With%20Text%20_0.mp4?VersionId=yV9VI3SMEy4d.GxW1HbLxqOicreL9ZIo'
JLR_SRC2 = 'https://media.production.jlrms.com/2020-05-12/video/afd1b9cd-990c-4f9f-a5a9-aeee90959ddc/Visor%20Manufacture%20%26%20Assembly_V5.mp4?VersionId=UB0asixOMPj5bR8I.7osNVKEZuUjmZDj'


def run(cmd):
    print('RUN', ' '.join(cmd))
    subprocess.run(cmd, check=True)


def dl(url, name):
    p = WORK / name
    if not p.exists():
        req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=180) as r, open(p,'wb') as f:
            while True:
                b = r.read(1024*1024)
                if not b: break
                f.write(b)
        print(name, p.stat().st_size)
    return p


def srt_time(t):
    ms = int(round((t-int(t))*1000)); s=int(t)%60; m=(int(t)//60)%60; h=int(t)//3600
    return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'


def make_srt(lines, out):
    with open(out,'w',encoding='utf-8') as f:
        for i,(a,b,txt) in enumerate(lines,1):
            f.write(f'{i}\n{srt_time(a)} --> {srt_time(b)}\n{txt}\n\n')


def tts(text, out):
    run(['edge-tts','--voice','pt-BR-AntonioNeural','--rate','+2%','--text',text,'--write-media',str(out)])


def duration(path):
    p=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(path)],capture_output=True,text=True,check=True)
    return float(p.stdout.strip())


def build(name, sources, script, captions, headline, accent):
    audio=WORK/f'{name}.mp3'; tts(script,audio)
    dur=duration(audio)
    srt=WORK/f'{name}.srt'; make_srt(captions,srt)
    clips=[]
    per=max(6.0, dur/len(sources))
    for i,src in enumerate(sources):
        clip=WORK/f'{name}_clip{i}.mp4'
        run(['ffmpeg','-y','-stream_loop','-1','-i',str(src),'-t',str(per+1),
             '-filter_complex',
             "[0:v]split=2[bg][fg];[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=30,eq=brightness=-0.35[bg2];[fg]scale=1010:568:force_original_aspect_ratio=decrease[fg2];[bg2][fg2]overlay=(W-w)/2:250[v]",
             '-map','[v]','-an','-r','30','-c:v','libx264','-preset','veryfast','-crf','20',str(clip)])
        clips.append(clip)
    concat=WORK/f'{name}_concat.txt'
    concat.write_text(''.join(f"file '{p}'\n" for p in clips),encoding='utf-8')
    base=WORK/f'{name}_base.mp4'
    run(['ffmpeg','-y','-f','concat','-safe','0','-i',str(concat),'-t',str(dur+0.3),'-c','copy',str(base)])
    ass_style="FontName=DejaVu Sans,FontSize=23,PrimaryColour=&H00FFFFFF,OutlineColour=&H90000000,BorderStyle=1,Outline=2,Shadow=0,Alignment=2,MarginV=300"
    vf=(f"drawbox=x=0:y=0:w=1080:h=190:color=black@0.58:t=fill,"
        f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='{headline}':fontcolor=white:fontsize=43:x=55:y=65,"
        f"drawbox=x=0:y=1810:w=1080:h=110:color=black@0.45:t=fill,"
        f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='UGI  •  Uma Gestão Inteligente':fontcolor=white:fontsize=25:x=50:y=1845,"
        f"subtitles={srt}:force_style='{ass_style}'")
    out=ROOT/f'{name}.mp4'
    run(['ffmpeg','-y','-i',str(base),'-i',str(audio),'-vf',vf,'-map','0:v','-map','1:a','-t',str(dur),
         '-c:v','libx264','-preset','medium','-crf','19','-c:a','aac','-b:a','160k','-movflags','+faststart',str(out)])
    run(['ffprobe','-v','error','-show_entries','stream=width,height,codec_name','-show_entries','format=duration,size','-of','json',str(out)])
    return out

nvidia = dl(NVIDIA_SRC,'nvidia_gtc_taipei_booth_tour.mp4')
jlr1 = dl(JLR_SRC1,'jlr_corporate.mp4')
jlr2 = dl(JLR_SRC2,'jlr_assembly.mp4')

nvidia_script = ('A NVIDIA ainda lidera o mercado de chips de inteligência artificial. Mas, na China, essa vantagem começou a ser pressionada. '
'Concorrentes locais ganharam escala e a participação da companhia caiu para cerca de cinquenta e cinco por cento. '
'Para a gestão, o ponto mais interessante não é apostar em quem vence essa corrida. É entender o risco de depender de um fornecedor que parece insubstituível. '
'Quando alternativas ficam mais compatíveis e ganham escala, muda o poder de negociação, muda o custo e muda o risco da operação. '
'A pergunta UGI é simples: se o seu fornecedor dominante perdesse força amanhã, sua empresa teria um plano B?')
nvidia_caps=[
(0,6,'A NVIDIA ainda lidera o mercado de chips de IA.'),(6,12,'Mas, na China, essa vantagem começou a ser pressionada.'),
(12,20,'Concorrentes locais ganharam escala.'),(20,27,'A participação caiu para cerca de 55%.'),
(27,35,'O ponto para a gestão é o risco de dependência.'),(35,43,'Alternativas mudam poder de negociação, custo e risco.'),
(43,51,'Se o fornecedor dominante perdesse força amanhã, você teria plano B?')]

jlr_script = ('A Jaguar Land Rover anunciou uma reestruturação que deve eliminar cerca de quatro mil postos. '
'A meta é reduzir custos e aproximar a operação do ponto de equilíbrio. Mas existe um detalhe importante: a empresa mantém entre quinze e dezoito bilhões de libras em investimentos em eletrificação, digital e manufatura. '
'Isso parece contraditório, mas não precisa ser. Em gestão, cortar estrutura e proteger investimento futuro podem fazer parte da mesma decisão. '
'O erro é tratar todo corte como eficiência e todo investimento como crescimento. A pergunta correta é: onde cada real ou libra ainda cria vantagem competitiva?')
jlr_caps=[
(0,7,'A JLR anunciou uma reestruturação de cerca de 4.000 postos.'),(7,14,'A meta é reduzir custos e aproximar a operação do equilíbrio.'),
(14,23,'Mas mantém £15–18 bi em eletrificação, digital e manufatura.'),(23,31,'Cortar estrutura e proteger o futuro podem coexistir.'),
(31,40,'Nem todo corte é eficiência. Nem todo investimento é crescimento.'),(40,49,'Onde o capital ainda cria vantagem competitiva?')]

build('video-nvidia-company-preview-v1',[nvidia],nvidia_script,nvidia_caps,'NVIDIA: quando o fornecedor dominante perde força','#76B900')
build('video-jlr-strategy-preview-v1',[jlr1,jlr2],jlr_script,jlr_caps,'JLR: cortar estrutura sem cortar o futuro','#FFB454')

(Path(ROOT/'PREVIEW_ONLY.txt')).write_text('PREVIEW ONLY — NOT APPROVED — DO NOT PUBLISH OR SCHEDULE\n',encoding='utf-8')
print('DONE', list(ROOT.glob('*.mp4')))

# trigger: 2026-09-07T16:30-03:00
