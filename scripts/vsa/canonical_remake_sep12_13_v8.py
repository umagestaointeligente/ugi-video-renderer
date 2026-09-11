#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import pathlib
import urllib.parse
from PIL import Image, ImageDraw

import canonical_remake_sep12_13_v7 as v7

v6 = v7.v6
v4 = v7.v4
base = v7.base

# Final block labels are semantic promises. They must describe the actual narrated
# interval, not a nearby editorial idea.
base.BLOCK_LABELS['IBERE'] = [
    'pesquisa coloca Iberê no topo do ranking',
    'influência não é só número de seguidores',
    'confiança, inspiração e conexão também pesam',
    'ciência vira pergunta, demonstração e descoberta',
    'o público acompanha demonstrações e processos',
    'experiência concreta vira memória e compartilhamento',
    'credibilidade e explicação pesam além dos seguidores',
]
base.BLOCK_LABELS['ROOSEVELT'] = [
    '1912 • Milwaukee • antes do discurso',
    'a bala perde energia no estojo e no papel',
    'estojo e discurso absorvem parte da energia',
    'o projétil entra e permanece no peito',
    'Roosevelt carrega o projétil pelo resto da vida',
    'menos energia não significa ferimento seguro',
    'só depois do discurso vem o atendimento',
]
base.BLOCK_LABELS['FERNANDA_MONTENEGRO'] = [
    'pesquisa destaca confiança e inspiração',
    'postar o tempo inteiro não cria confiança',
    'décadas no teatro, cinema e televisão',
    'exposição repetida não é credibilidade',
    'consistência de trajetória gera confiança',
    'menos aparições podem manter força simbólica',
    'longevidade pode pesar mais que frequência',
]
base.BLOCK_LABELS['MARISKA_LONGEVITY'] = [
    'décadas como Olivia Benson',
    'mesmo papel não significa mesma personagem',
    'função, relações e contexto mudam',
    'de detetive a posições de liderança',
    'o público reconhece e acompanha novas fases',
    'familiaridade + renovação sustentam longevidade',
    'mudar sem perder identidade',
]
base.BLOCK_LABELS['EMICIDA_INFLUENCE'] = [
    'pesquisa destaca o engajamento de Emicida',
    'popularidade mede alcance; influência mede efeito',
    'influência muda conversa, reflexão e comportamento',
    'música, narrativa, identidade e temas formam uma voz',
    'a mensagem continua circulando após o lançamento',
    'ideias memoráveis são repetidas por outras pessoas',
    'audiência vira influência quando a mensagem continua',
]

# Replace unrelated public-event imagery with distinct real SVU set evidence.
v4.SOURCE_OVERRIDES['MARISKA_LONGEVITY'] = [
    (v4.commons_file('Mariska Hargitay on set of SVU season 12.jpg'), 'CC BY-SA 2.0 - Lori_NY'),
    (v4.commons_file('Law and Order SVU.png'), 'CC BY-SA 3.0 - Daniel P. Fleming / VRT'),
    (v4.commons_file('SVU crime scene set 2 season 12.jpg'), 'CC BY-SA 2.0 - Lori_NY'),
    (v4.commons_file('Mariska Hargitay 2025.jpg'), 'CC BY-SA 4.0 - Colleen Sturtevant'),
]


def fast_photo_documentary_clip(url: str, dest: pathlib.Path):
    """Generate the same documentary motion using H.264 in explicit Matroska.

    The destination keeps the historical .webm filename expected by the base
    renderer, but the muxer is explicitly Matroska, which validly supports H.264.
    FFmpeg probes container bytes downstream, so this is both fast and unambiguous.
    """
    parsed = urllib.parse.urlparse(url)
    suffix = pathlib.Path(urllib.parse.unquote(parsed.path)).suffix.lower()
    if suffix not in {'.jpg', '.jpeg', '.png', '.webp'}:
        suffix = '.jpg'
    raw = dest.with_suffix(suffix)
    base.run(['curl','-L','--fail','--retry','3','--retry-delay','2','-A','Mozilla/5.0',url,'-o',str(raw)])
    if raw.stat().st_size < 8000:
        raise RuntimeError(f'ARCHIVAL_IMAGE_DOWNLOAD_TOO_SMALL {url}')
    fc = (
        "color=c=0x031430:s=1280x720:r=30:d=24[bg];"
        "[0:v]scale=1120:630:force_original_aspect_ratio=decrease,"
        "pad=1180:670:(ow-iw)/2:(oh-ih)/2:color=0x081f3d[photo];"
        "[bg][photo]overlay=x='(W-w)/2+42*sin(t*0.55)':y='(H-h)/2+24*cos(t*0.43)'[m];"
        "[m]drawbox=x=85:y=655:w=1110:h=6:color=0x27c4ff@0.70:t=fill,"
        "drawbox=x='85+min(1110,46*t)':y=643:w=24:h=30:color=0xffc526:t=fill,"
        "drawbox=x=32:y=28:w=250:h=44:color=black@0.55:t=fill,"
        f"drawtext=fontfile={base.FONT_BOLD}:text='ARQUIVO REAL':fontcolor=white:fontsize=24:x=50:y=38,"
        "fps=30,format=yuv420p[v]"
    )
    base.run([
        'ffmpeg','-y','-loglevel','error','-loop','1','-i',str(raw),
        '-filter_complex',fc,'-map','[v]','-t','24','-an',
        '-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p',
        '-f','matroska',str(dest)
    ])
    raw.unlink(missing_ok=True)


v4._photo_documentary_clip = fast_photo_documentary_clip


def _header(label: str):
    im = Image.new('RGB',(976,844),base.NAVY)
    d = ImageDraw.Draw(im)
    d.rectangle((0,0,976,76),fill=(5,34,70))
    d.text((28,20),label,font=base.font(24),fill=base.WHITE)
    d.line((28,72,948,72),fill=base.CYAN,width=2)
    return im,d


def emicida_voice_frame(p: float, label: str):
    im,d=_header(label)
    center=(488,420)
    items=[('MÚSICA',(75,170)),('NARRATIVA',(650,170)),('IDENTIDADE',(75,615)),('TEMAS SOCIAIS',(650,615))]
    for j,(txt,(x,y)) in enumerate(items):
        q=max(0.0,min(1.0,p*1.7-j*.10))
        # whole evidence card moves toward the center, creating large-area motion
        tx=int(x+(center[0]-x-105)*q*.58); ty=int(y+(center[1]-y-30)*q*.58)
        d.rounded_rectangle((tx,ty,tx+210,ty+62),14,fill=(28,105,158),outline=base.GOLD if j%2 else base.CYAN,width=4)
        f=base.font(18); tw=d.textbbox((0,0),txt,font=f)[2]
        d.text((tx+105-tw/2,ty+20),txt,font=f,fill=base.WHITE)
        base.arrow(d,(tx+105,ty+31),center,base.GOLD if j%2 else base.CYAN,5)
    r=58+int(45*math.sin(p*math.pi)**2)
    d.ellipse((center[0]-r,center[1]-r,center[0]+r,center[1]+r),fill=(34,125,180),outline=base.WHITE,width=5)
    d.text((449,409),'VOZ',font=base.font(23),fill=base.WHITE)
    # visible outgoing reflection/behavior arrows reinforce influence as effect.
    for j,(x,y) in enumerate([(850,330),(820,500),(660,735),(315,735),(120,510),(120,330)]):
        q=max(0.0,min(1.0,(p-.25)*1.6-j*.04))
        ex=center[0]+int((x-center[0])*q); ey=center[1]+int((y-center[1])*q)
        base.arrow(d,center,(ex,ey),base.GOLD if j%2 else base.CYAN,4)
    return im


def emicida_memory_frame(p: float, label: str):
    im,d=_header(label)
    stages=[('IDEIA',130),('EMOÇÃO',345),('MEMÓRIA',560),('REPETIÇÃO',775)]
    y=420
    for j,(txt,x) in enumerate(stages):
        q=max(0.0,min(1.0,p*1.65-j*.16))
        r=28+int(22*q)
        d.ellipse((x-r,y-r,x+r,y+r),fill=(35,125,175),outline=base.GOLD if j>=2 else base.CYAN,width=4)
        f=base.font(17); tw=d.textbbox((0,0),txt,font=f)[2]
        d.text((x-tw/2,y-9),txt,font=f,fill=base.WHITE)
        if j<3:
            ex=x+int(160*q)
            base.arrow(d,(x+r,y),(ex,y),base.GOLD if j>=1 else base.CYAN,6)
    # repeated people appear around the final node over a wide area
    for j in range(8):
        ang=2*math.pi*j/8
        q=max(0,min(1,(p-.35)*1.55))
        rr=int(70+135*q)
        x=775+int(math.cos(ang)*rr); yy=420+int(math.sin(ang)*rr)
        d.ellipse((x-13,yy-13,x+13,yy+13),fill=(60,145,195),outline=base.WHITE,width=2)
    d.text((230,690),'A MENSAGEM CONTINUA DEPOIS DO CONTEÚDO',font=base.font(22),fill=base.GOLD)
    return im


def roosevelt_safety_frame(p: float, label: str):
    im,d=_header(label)
    d.text((230,120),'ENERGIA MENOR ≠ FERIMENTO SEGURO',font=base.font(27),fill=base.GOLD)
    factors=[('ESTOJO',110,250),('PAPEL',110,420),('ANATOMIA',110,590)]
    target=(690,420)
    for j,(txt,x,y) in enumerate(factors):
        q=max(0.0,min(1.0,p*1.65-j*.12))
        d.rounded_rectangle((x,y,x+185,y+62),14,fill=(30,105,155),outline=base.CYAN,width=4)
        d.text((x+35,y+20),txt,font=base.font(19),fill=base.WHITE)
        ex=x+185+int((target[0]-x-185)*q); ey=y+31+int((target[1]-y-31)*q)
        base.arrow(d,(x+185,y+31),(ex,ey),base.CYAN,6)
    # energy meter visibly shrinks while danger pulse grows
    w=int(320*(1-.60*p))
    d.rectangle((500,235,500+w,285),fill=base.GOLD,outline=base.WHITE,width=3)
    d.text((500,300),'ENERGIA',font=base.font(19),fill=base.WHITE)
    rr=55+int(75*p)
    d.ellipse((target[0]-rr,target[1]-rr,target[0]+rr,target[1]+rr),outline=(255,80,65),width=12)
    d.ellipse((target[0]-40,target[1]-40,target[0]+40,target[1]+40),fill=(175,45,48),outline=base.WHITE,width=4)
    d.text((615,650),'FERIMENTO AINDA REAL',font=base.font(22),fill=base.WHITE)
    return im


def anim_frame_v8(mode: str, idx: int, p: float, label: str):
    if mode=='message' and idx==3:
        return emicida_voice_frame(p,label)
    if mode=='message' and idx==5:
        return emicida_memory_frame(p,label)
    if mode=='ballistic' and idx==5:
        return roosevelt_safety_frame(p,label)
    return v7.anim_frame_v7(mode,idx,p,label)


def build_v8(topic,golden:pathlib.Path,outdir:pathlib.Path):
    v7.build_v7(topic,golden,outdir)
    video_id=topic['id']
    receipt_path=outdir/f'{video_id}_VSA_VISUAL_RELEASE_RECEIPT_V1.json'
    r=json.loads(receipt_path.read_text(encoding='utf-8'))
    r['repair_version']='V8_FINAL_SEMANTIC_LABEL_ALIGNMENT'
    r['status']='AWAITING_HUMAN_VISUAL_ALIGNMENT_REVIEW'
    r['human_review']['approved']=False
    r['release_eligible']=False
    r['schedule_mutated_before_gate']=False
    r['gates']['VISUAL_NARRATIVE_ALIGNMENT_PASS']=False
    r['v8_contract']={
        'visible_block_label_matches_actual_narration_interval': True,
        'archival_intermediates_use_h264_matroska_not_invalid_h264_webm': True,
        'mariska_real_evidence_is_svu_specific_before_current_longevity_close': video_id=='MARISKA_LONGEVITY',
        'roosevelt_energy_reduction_is_explicitly_not_safety': video_id=='ROOSEVELT',
        'emicida_influence_mechanisms_have_large_area_motion': video_id=='EMICIDA_INFLUENCE',
        'release_still_requires_human_approval': True
    }
    receipt_path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


base.anim_frame=anim_frame_v8
base.build=build_v8

if __name__=='__main__':
    base.main()
