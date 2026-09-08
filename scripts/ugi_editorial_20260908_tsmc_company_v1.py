from pathlib import Path
import subprocess, urllib.parse, math, json

ROOT = Path('public/ugi/editorial/2026-09-08')
WORK = Path('/tmp/ugi_tsmc_company_v1')
ROOT.mkdir(parents=True, exist_ok=True)
WORK.mkdir(parents=True, exist_ok=True)

SOURCES = {
    'whitehouse': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/' + urllib.parse.quote('President Trump Makes an Investment Announcement.webm', safe=''),
    'japan': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/' + urllib.parse.quote('TSMC及び地元中小企業との車座 岸田総理.webm', safe=''),
    'arizona': 'https://d34w7g4gy10iej.cloudfront.net/video/2212/DOD_109358136/DOD_109358136.mp4',
}

LICENSES = {
    'whitehouse': 'The White House / U.S. federal government work — public domain via Wikimedia Commons',
    'japan': 'Prime Minister’s Office of Japan — CC BY 3.0 via Wikimedia Commons',
    'arizona': 'White House Communications Agency / DVIDS Video 866988 — public domain',
}

def run(cmd, check=True):
    print('RUN', ' '.join(map(str, cmd)), flush=True)
    return subprocess.run([str(x) for x in cmd], check=check)

# Download only licensed/public-domain company-context motion footage.
local={}
for key,url in SOURCES.items():
    ext='.mp4' if '.mp4' in url else '.webm'
    p=WORK/f'{key}{ext}'
    run(['curl','-L','--fail','--retry','2','-A','Mozilla/5.0','-o',p,url])
    local[key]=p

# Company-first shot list. No generic chip stock, no influencer, no product-ad footage.
# Every source is a real TSMC corporate/government event or visit involving TSMC.
shots = [
    # C.C. Wei, TSMC chairman/CEO, at the White House investment announcement.
    ('whitehouse', 287.0, 5.8, 'CEO / investment announcement'),
    # TSMC-related official factory visit in Japan: executives/facility context.
    ('japan', 0.0, 5.8, 'TSMC Japan visit / company context'),
    # TSMC Arizona event, public-domain White House Communications Agency footage.
    ('arizona', 0.0, 5.8, 'TSMC Arizona / company event'),
    ('whitehouse', 300.0, 5.8, 'C.C. Wei speaking / TSMC'),
    ('japan', 16.0, 5.8, 'TSMC factory visit / wafer & facility context'),
    ('arizona', 240.0, 5.8, 'TSMC Arizona event / manufacturing expansion'),
    ('japan', 40.0, 5.8, 'TSMC Japan / people and operation context'),
    ('whitehouse', 330.0, 5.8, 'C.C. Wei / global expansion'),
    ('arizona', 600.0, 5.8, 'TSMC Arizona / closing company context'),
]

clips=[]
for i,(key,start,length,label) in enumerate(shots):
    src=local[key]
    out=WORK/f'clip_{i:02d}.mp4'
    # Preserve the full 16:9 company frame in the foreground; use the same moving footage
    # as a dark blurred extension. This avoids destructive vertical crop and keeps signage/people.
    fc=(
        '[0:v]split=2[bg][fg];'
        '[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,'
        'gblur=sigma=36,eq=brightness=-0.43:saturation=0.72[bg2];'
        '[fg]scale=1020:574:force_original_aspect_ratio=decrease,eq=contrast=1.03:saturation=1.04[fg2];'
        '[bg2][fg2]overlay=(W-w)/2:286[v]'
    )
    run(['ffmpeg','-y','-ss',str(start),'-i',src,'-t',str(length),'-filter_complex',fc,
         '-map','[v]','-an','-r','30','-c:v','libx264','-preset','veryfast','-crf','18',out])
    clips.append(out)

concat=WORK/'concat.txt'
concat.write_text(''.join(f"file '{p}'\n" for p in clips), encoding='utf-8')
base=WORK/'base.mp4'
run(['ffmpeg','-y','-f','concat','-safe','0','-i',concat,'-c','copy',base])

narration=(
    'Duzentos e sessenta e cinco bilhões de dólares. Esse é o tamanho do plano de investimento da TSMC no Arizona. '
    'A empresa que virou peça central da cadeia global de chips está ampliando capacidade fora de Taiwan sem tirar da ilha o coração da tecnologia. '
    'E isso não é só expansão industrial. É gestão de risco geopolítico. '
    'A TSMC atende empresas que dependem dos seus chips e, ao mesmo tempo, governos que querem produção mais perto de casa. '
    'Quanto mais indispensável ela fica, maior o poder de negociação — e maior o custo de uma ruptura. '
    'Para a gestão, a lição é direta: concentração pode gerar vantagem, mas também vulnerabilidade. '
    'Diversificar não é abandonar o core. É reduzir risco sem perder eficiência. '
    'A pergunta é: se um ativo seu se tornasse crítico para o mercado, você saberia expandi-lo sem diluir aquilo que o torna único?'
)

audio=WORK/'narration.mp3'
run(['edge-tts','--voice','pt-BR-AntonioNeural','--rate','+8%','--text',narration,'--write-media',audio])

def duration(path):
    r=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(path)],capture_output=True,text=True,check=True)
    return float(r.stdout.strip())

aud_dur=duration(audio)
base_dur=duration(base)
print('AUDIO_DURATION',aud_dur,'BASE_DURATION',base_dur)

# If narration is longer than available motion footage, slow the visual sequence very slightly,
# never freeze a frame. If shorter, final output trims with -shortest.
video_for_mix=base
if aud_dur > base_dur - 0.4:
    factor=aud_dur/(base_dur-0.2)
    stretched=WORK/'base_stretched.mp4'
    run(['ffmpeg','-y','-i',base,'-vf',f'setpts={factor:.6f}*PTS','-an','-r','30','-c:v','libx264','-preset','veryfast','-crf','18',stretched])
    video_for_mix=stretched

# Caption blocks aligned by proportional word weight to the actual TTS duration.
caption_texts=[
    'US$ 265 bilhões: esse é o plano de investimento da TSMC no Arizona.',
    'A empresa está ampliando capacidade fora de Taiwan.',
    'Sem tirar da ilha o coração da tecnologia.',
    'Isso não é só expansão industrial. É gestão de risco geopolítico.',
    'Clientes dependem dos chips. Governos querem produção mais perto de casa.',
    'Quanto mais indispensável, maior o poder de negociação — e o risco de ruptura.',
    'Concentração pode gerar vantagem. E também vulnerabilidade.',
    'Diversificar é reduzir risco sem perder eficiência.',
    'Sua empresa saberia expandir um ativo crítico sem diluir o que o torna único?'
]
weights=[len(x.split()) for x in caption_texts]
total=sum(weights)
starts=[0.0]
for w in weights[:-1]: starts.append(starts[-1]+aud_dur*w/total)
ends=starts[1:]+[aud_dur]

def srt_time(t):
    ms=int(round((t-int(t))*1000)); s=int(t)%60; m=(int(t)//60)%60; h=int(t)//3600
    return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'

srt=WORK/'captions.srt'
with open(srt,'w',encoding='utf-8') as f:
    for i,(a,b,txt) in enumerate(zip(starts,ends,caption_texts),1):
        f.write(f'{i}\n{srt_time(a)} --> {srt_time(b)}\n{txt}\n\n')

# UGI editorial overlay: text is explanatory, while company identity remains visible in real footage.
style='FontName=DejaVu Sans,FontSize=22,PrimaryColour=&H00FFFFFF,OutlineColour=&HAA000000,BorderStyle=1,Outline=2,Shadow=0,Alignment=2,MarginV=265'
vf=(
    "drawbox=x=0:y=0:w=1080:h=220:color=black@0.54:t=fill,"
    "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='TSMC: quando capacidade vira poder estratégico':fontcolor=white:fontsize=39:x=52:y=58,"
    "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:text='UGI  •  ESTRATÉGIA + OPERAÇÃO':fontcolor=0xE7E7E7:fontsize=22:x=52:y=128,"
    "drawbox=x=0:y=1800:w=1080:h=120:color=black@0.48:t=fill,"
    "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='UGI  •  Uma Gestão Inteligente':fontcolor=white:fontsize=24:x=48:y=1830,"
    "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:text='Dados: Reuters • 07/09/2026':fontcolor=0xD0D0D0:fontsize=17:x=48:y=1870,"
    f"subtitles={srt}:force_style='{style}'"
)

out=ROOT/'video-tsmc-company-preview-v1.mp4'
run(['ffmpeg','-y','-i',video_for_mix,'-i',audio,'-vf',vf,'-map','0:v','-map','1:a','-shortest',
     '-c:v','libx264','-preset','medium','-crf','18','-c:a','aac','-b:a','160k','-movflags','+faststart',out])

# Final-file QA evidence: sample exact final output at nine positions.
final_dur=duration(out)
qa_times=[max(0.1, final_dur*i/10) for i in range(1,10)]
frames=[]
for i,t in enumerate(qa_times):
    p=WORK/f'qa_{i:02d}.jpg'
    run(['ffmpeg','-y','-ss',f'{t:.3f}','-i',out,'-frames:v','1','-q:v','2',p])
    frames.append(p)
args=[]
for p in frames: args += ['-i',p]
parts=[]
for i in range(len(frames)): parts.append(f'[{i}:v]scale=270:480[v{i}]')
layout='|'.join(['0_0','270_0','540_0','0_480','270_480','540_480','0_960','270_960','540_960'])
fc=';'.join(parts)+';'+''.join(f'[v{i}]' for i in range(len(frames)))+f'xstack=inputs={len(frames)}:layout={layout}:fill=black[out]'
qa=ROOT/'video-tsmc-company-preview-v1-qa.jpg'
run(['ffmpeg','-y',*args,'-filter_complex',fc,'-map','[out]','-frames:v','1',qa])

# Machine-readable QA + source ledger.
probe=subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate','-show_entries','format=duration,size','-of','json',str(out)],capture_output=True,text=True,check=True)
qa_data=json.loads(probe.stdout)
qa_data['sources']=LICENSES
qa_data['shot_labels']=[s[3] for s in shots]
qa_data['status']='PREVIEW_ONLY_AWAITING_HUMAN_APPROVAL'
(ROOT/'video-tsmc-company-preview-v1-qa.json').write_text(json.dumps(qa_data,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'PREVIEW_ONLY.txt').write_text('PREVIEW ONLY — NVIDIA V2 APPROVED; TSMC V1 AWAITING APPROVAL — DO NOT SCHEDULE UNTIL EXPLICIT HUMAN APPROVAL.\n',encoding='utf-8')
print('DONE',out,'duration',final_dur,'size',out.stat().st_size)
