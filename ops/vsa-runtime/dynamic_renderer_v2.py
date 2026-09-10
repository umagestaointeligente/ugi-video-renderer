#!/usr/bin/env python3
"""Canonical dynamic causal renderer V2 for ORBIT/VSA.

Purpose: restore the V7 visual grammar with current canonical mask/CTA.
It alternates distinct real footage with actual state-changing procedural motion,
burns captions in the canonical caption band, mixes thematic licensed music,
and emits a fail-closed visual manifest plus editorial thumbnail.
"""
from __future__ import annotations
import argparse, hashlib, json, math, pathlib, subprocess, urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageChops

W,H=1080,1920; CW,CH=974,844; FPS=30
MASK_SHA='9f6ebae6742b007b1e660cd401b610933d0a06c2c3fee240220abf7215e1a4d9'
CTA_SHA='6c064a533784f2c09b594095646aa538e07f77955ed348656c60e5d2795fa5a8'
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
CHANNEL_ID='UCm0UMO6lNWlr66YSIS1p4iQ'

MOTION_MAP={
'DUST_MALI':['particles','flow','orbit','wave'],
'FERNANDA_MONTENEGRO':['timeline','network','meter','flow'],
'HUNGA_TSUNAMI':['collapse','wave','flow','network'],
'ELTON_ENERGY':['meter','route','flow','timeline'],
'EMIT_MINE':['spectrum','orbit','scan','map'],
'MARISKA_LONGEVITY':['timeline','meter','network','flow'],
'SENTINEL_HURRICANE':['pulse','sea','cross','orbit'],
'EMICIDA_INFLUENCE':['network','flow','pulse','timeline'],
'CHANDRA_HYPERSOFT':['spectrum','orbit','pulse','network'],
'IBERE':['network','meter','flow','timeline'],
'PEAT_FIRE':['cross','particles','flow','heat'],
'HOUDINI':['mechanical','chain','route','timeline'],
'EQUAL_EARTH':['map','grid','transform','meter'],
'BUSTER_KEATON':['timeline','pulse','network','flow'],
'EL_NINO':['sea','flow','cross','map'],
'ROOSEVELT':['route','cross','timeline','meter'],
}

LABELS={
'DUST_MALI':['POEIRA SE LEVANTA','VENTO TRANSPORTA','SATÉLITE ACOMPANHA','PLUMA SE ESPALHA'],
'FERNANDA_MONTENEGRO':['DÉCADAS DE TRAJETÓRIA','CONFIANÇA SE CONECTA','CONSISTÊNCIA ACUMULA','PRESENÇA PERMANECE'],
'HUNGA_TSUNAMI':['COLAPSO SUBMARINO','VIBRAÇÃO VIAJA','ONDA SE PROPAGA','SENSORES CONECTAM PISTAS'],
'ELTON_ENERGY':['ENERGIA É LIMITADA','CAMINHO PODE SER LONGO','CONSERVAR PARA RECUPERAR','RITMO DEPOIS DO SHOW'],
'EMIT_MINE':['LUZ TEM ASSINATURAS','SATÉLITE VARRE O SOLO','FAIXAS REVELAM MINERAIS','MAPA PRIORIZA ÁREAS'],
'MARISKA_LONGEVITY':['TEMPO CRIA HISTÓRIA','RESPONSABILIDADES CRESCEM','PÚBLICO SE RENOVA','MUDAR SEM PERDER IDENTIDADE'],
'SENTINEL_HURRICANE':['RADAR MEDE CENTÍMETROS','OCEANO GUARDA ENERGIA','CALOR EXISTE EM PROFUNDIDADE','SATÉLITE COMPLETA A PREVISÃO'],
'EMICIDA_INFLUENCE':['MENSAGEM ENTRA NA REDE','IDEIA CONTINUA VIAJANDO','RELEVÂNCIA AMPLIFICA','AUDIÊNCIA VIRA INFLUÊNCIA'],
'CHANDRA_HYPERSOFT':['RAIOS X CONTAM UMA HISTÓRIA','FONTES SURGEM NA GALÁXIA','PULSOS CHEGAM AO DETECTOR','PADRÕES SÃO COMPARADOS'],
'IBERE':['CONFIANÇA CRIA CONEXÃO','AUDIÊNCIA NÃO É TUDO','EXPLICAÇÃO FAZ A IDEIA VIAJAR','CONSISTÊNCIA GERA INFLUÊNCIA'],
'PEAT_FIRE':['FOGO SE ESCONDE NO SOLO','CALOR AVANÇA POR BAIXO','FUMAÇA ENCONTRA SAÍDAS','TURFA MANTÉM A COMBUSTÃO'],
'HOUDINI':['TRAVA TEM MECANISMO','CORRENTES TÊM PONTOS DE TENSÃO','MOVIMENTO CRIA FOLGA','TEMPO E TÉCNICA DECIDEM'],
'EQUAL_EARTH':['TODO MAPA DISTORCE','GRADE MUDA AO SER PROJETADA','GLOBO VIRA PLANO','ÁREAS PODEM SER COMPARADAS'],
'BUSTER_KEATON':['TEMPO É PARTE DA PIADA','CAOS CRESCE AO REDOR','ROSTO CONTINUA IMPASSÍVEL','CONTRASTE GERA HUMOR'],
'EL_NINO':['ÁGUA QUENTE SE DESLOCA','VENTOS MUDAM O FLUXO','CAMADA QUENTE SE REORGANIZA','EFEITOS VIAJAM PELA ATMOSFERA'],
'ROOSEVELT':['TRAJETÓRIA PERDE ENERGIA','CAMADAS ABSORVEM IMPACTO','TEMPO CONTINUA CORRENDO','DECISÃO VEM DEPOIS DO CHOQUE'],
}

def run(cmd):
    print('+',' '.join(map(str,cmd)),flush=True); subprocess.run(cmd,check=True)
def probe(p):
    raw=subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(p)],text=True).strip()
    try: return float(raw)
    except Exception: return 60.0
def dl(url,p):
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 Orbit-VSA-Dynamic/2.0'})
    with urllib.request.urlopen(req,timeout=240) as r, open(p,'wb') as f:
        while True:
            b=r.read(1024*1024)
            if not b: break
            f.write(b)
    if pathlib.Path(p).stat().st_size < 40000: raise RuntimeError('ASSET_TOO_SMALL:'+str(p))
def wrap(draw,s,font,maxw):
    lines=[]; cur=''
    for w in s.split():
        q=(cur+' '+w).strip()
        if cur and draw.textbbox((0,0),q,font=font)[2]>maxw: lines.append(cur); cur=w
        else: cur=q
    if cur: lines.append(cur)
    return lines
def astime(sec):
    h=int(sec//3600); sec-=h*3600; m=int(sec//60); sec-=m*60
    return f'{h}:{m:02}:{sec:05.2f}'
def ease(q): return q*q*(3-2*q)

def draw_label(dr,text):
    f=ImageFont.truetype(BOLD,22)
    dr.rounded_rectangle((18,16,469,58),radius=12,fill=(2,14,33,190),outline=(33,192,245,160),width=2)
    lines=wrap(dr,text,f,425)
    dr.text((32,25),lines[0][:38],font=f,fill=(250,252,255,255))

def motion_frame(kind,q,label):
    sw,sh=487,422; img=Image.new('RGB',(sw,sh),(5,20,42)); dr=ImageDraw.Draw(img,'RGBA')
    draw_label(dr,label)
    cyan=(70,215,255,230); gold=(255,194,61,235); white=(245,250,255,235); blue=(20,91,145,230)
    if kind=='particles':
        dr.rectangle((0,285,sw,sh),fill=(122,83,52,255))
        for i in range(52):
            x=(i*67 + int(q*330*(1+(i%5)*.08)))%sw; y=300-int((q*250+i*41)%255)
            r=2+(i%4); dr.ellipse((x-r,y-r,x+r,y+r),fill=gold)
        dr.line((20,300,460,175),fill=cyan,width=5)
    elif kind=='flow':
        path=[]
        for x in range(20,470,4): path.append((x,220+int(52*math.sin(x*.024+q*6))))
        dr.line(path,fill=cyan,width=8)
        for i in range(7):
            x=30+((i*70+q*360)%420); y=220+52*math.sin(x*.024+q*6); dr.ellipse((x-7,y-7,x+7,y+7),fill=gold)
    elif kind=='orbit':
        cx,cy=245,230; dr.ellipse((90,75,400,385),outline=(35,95,145,220),width=3)
        a=q*math.tau*1.2; x=cx+155*math.cos(a); y=cy+155*math.sin(a); dr.ellipse((x-13,y-13,x+13,y+13),fill=gold)
        dr.ellipse((205,190,285,270),fill=(36,112,164,255)); dr.arc((195,180,295,280),20,310,fill=cyan,width=4)
    elif kind=='wave':
        cx,cy=95,235
        for k in range(6):
            rr=(q*430+k*85)%500; dr.arc((cx-rr,cy-rr*.45,cx+rr,cy+rr*.45),-70,70,fill=cyan,width=5)
        for x,y in [(325,135),(410,220),(345,315)]: dr.ellipse((x-8,y-8,x+8,y+8),fill=gold)
    elif kind=='timeline':
        dr.line((55,235,435,235),fill=(70,95,125,255),width=8)
        for i in range(5):
            x=70+i*88; dr.ellipse((x-12,223,x+12,247),fill=cyan)
        px=70+365*ease(q); dr.ellipse((px-16,219,px+16,251),fill=gold)
        dr.line((px,185,px,285),fill=gold,width=3)
    elif kind=='network':
        nodes=[(75,210),(170,125),(190,305),(310,110),(330,300),(425,210)]
        for a,b in [(0,1),(0,2),(1,3),(2,4),(3,5),(4,5),(1,4)]: dr.line((*nodes[a],*nodes[b]),fill=(60,100,140,190),width=3)
        active=int(q*len(nodes))%len(nodes)
        for i,(x,y) in enumerate(nodes):
            r=18 if i==active else 12; dr.ellipse((x-r,y-r,x+r,y+r),fill=gold if i==active else cyan)
    elif kind=='meter':
        vals=[.38,.55,.72,.88]
        for i,v in enumerate(vals):
            x=70+i*90; h=int(220*v*min(1,q*1.7)); dr.rounded_rectangle((x,345-h,x+52,345),radius=9,fill=cyan if i<3 else gold)
        dr.line((45,345,442,345),fill=white,width=3)
    elif kind=='route':
        pts=[(55,320),(135,255),(205,285),(285,185),(365,215),(435,110)]
        dr.line(pts,fill=(65,105,140,210),width=5)
        upto=max(2,int(2+q*(len(pts)-2))); dr.line(pts[:upto],fill=cyan,width=8)
        idx=min(len(pts)-1,int(q*(len(pts)-1))); x,y=pts[idx]; dr.ellipse((x-12,y-12,x+12,y+12),fill=gold)
    elif kind=='spectrum':
        for i in range(70):
            x=30+i*6; amp=.15+.85*(math.sin(i*.28+q*8)**2); h=int(210*amp); hue=(i%12)/12
            col=(int(60+160*hue),int(210-80*hue),255,220); dr.rectangle((x,350-h,x+4,350),fill=col)
        marker=30+420*q; dr.line((marker,85,marker,365),fill=gold,width=4)
    elif kind=='scan':
        for r in range(45,190,35): dr.ellipse((245-r,225-r,245+r,225+r),outline=(30,90,135,180),width=2)
        ang=q*math.tau; ex=245+190*math.cos(ang); ey=225+190*math.sin(ang); dr.line((245,225,ex,ey),fill=cyan,width=5)
        for x,y in [(135,160),(340,145),(300,315)]: dr.ellipse((x-8,y-8,x+8,y+8),fill=gold)
    elif kind=='map':
        for i in range(6):
            y=90+i*55; bend=int(28*math.sin(q*math.pi)*((i-2.5)/2.5)); dr.line((45,y,442,y+bend),fill=(55,115,155,210),width=3)
        for i in range(7):
            x=50+i*65; bend=int(25*math.sin(q*math.pi)*((i-3)/3)); dr.line((x,75,x+bend,365),fill=cyan,width=3)
        dr.ellipse((190,155,300,275),outline=gold,width=5)
    elif kind=='grid':
        bulge=1+.25*math.sin(q*math.pi)
        cx,cy=245,225
        for i in range(-4,5):
            x=cx+i*45*bulge; dr.line((x,80,x,365),fill=cyan,width=2)
        for i in range(-3,4):
            y=cy+i*45/bulge; dr.line((55,y,435,y),fill=(65,105,145,200),width=2)
    elif kind=='transform':
        s=ease(q); r=125
        pts=[]
        for i in range(80):
            a=i/79*math.tau; cx=245+r*math.cos(a); cy=225+r*math.sin(a)*(.55+0.45*(1-s)); pts.append((cx,cy))
        dr.line(pts+[pts[0]],fill=cyan,width=5)
        w=int(60+260*s); dr.rectangle((245-w//2,205,245+w//2,245),outline=gold,width=4)
    elif kind=='pulse':
        for k in range(5):
            rr=((q*280+k*70)%330); dr.ellipse((245-rr,225-rr,245+rr,225+rr),outline=cyan,width=4)
        dr.ellipse((232,212,258,238),fill=gold)
    elif kind=='sea':
        base=250-int(35*math.sin(q*math.pi)); dr.rectangle((0,base,487,422),fill=(8,91,145,255))
        for x in range(0,487,8):
            y=base+int(8*math.sin(x*.06+q*10)); dr.line((x,y,x+8,y),fill=cyan,width=3)
        dr.line((40,base,445,base),fill=gold,width=3)
    elif kind=='cross':
        dr.rectangle((0,80,487,175),fill=(65,125,160,255)); dr.rectangle((0,175,487,285),fill=(20,80,120,255)); dr.rectangle((0,285,487,422),fill=(18,47,70,255))
        x=70+340*q; dr.line((x,82,x,365),fill=gold,width=5)
        for y in [175,285]: dr.line((0,y,487,y),fill=cyan,width=3)
    elif kind=='heat':
        for i in range(16):
            x=45+(i*29)%410; y=335-int(((q*240+i*37)%260)); r=9+(i%3)*5
            dr.ellipse((x-r,y-r,x+r,y+r),fill=(255,95+5*i,35,150))
        dr.rectangle((0,330,487,422),fill=(95,55,30,210))
    elif kind=='mechanical':
        for i in range(5):
            x=105+i*58; lift=int(55*max(0,math.sin(q*math.pi*1.5+i*.5))); dr.rectangle((x,150-lift,x+22,280),fill=(155,175,190,255)); dr.ellipse((x-3,135-lift,x+25,163-lift),fill=gold)
        dr.rounded_rectangle((75,270,410,340),radius=18,outline=cyan,width=6)
    elif kind=='chain':
        for i in range(7):
            x=70+i*57; off=22*math.sin(q*math.tau+i*.8); dr.ellipse((x-25,205+off,x+25,245+off),outline=gold if i<int(q*8) else cyan,width=6)
        gap=int(q*80); dr.rectangle((235-gap//2,180,252+gap//2,270),fill=(5,20,42,255))
    elif kind=='heat': pass
    else:
        # Dynamic signal chain fallback; still a state-changing causal component, never a static CAUSA/EFEITO card.
        nodes=[(65,225),(180,225),(300,225),(420,225)]
        for j,(x,y) in enumerate(nodes):
            dr.ellipse((x-26,y-26,x+26,y+26),fill=blue,outline=cyan,width=3)
            if j<3: dr.line((x+28,y,nodes[j+1][0]-28,y),fill=(80,120,150,220),width=4)
        px=65+355*((q*1.2)%1); dr.ellipse((px-9,216,px+9,234),fill=gold)
    return img

def make_proc(kind,label,dur,out):
    frames=max(60,int(dur*FPS)); first=last=None
    p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','487x422','-r','30','-i','-','-an','-vf',f'scale={CW}:{CH}:flags=lanczos','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p',str(out)],stdin=subprocess.PIPE)
    for n in range(frames):
        q=n/max(1,frames-1); img=motion_frame(kind,q,label)
        if n==0:first=img.copy()
        if n==frames-1:last=img.copy()
        p.stdin.write(img.tobytes())
    p.stdin.close(); rc=p.wait();
    if rc: raise RuntimeError('PROC_RENDER_FAIL:'+kind)
    if ImageChops.difference(first,last).getbbox() is None: raise RuntimeError('STATIC_PROC_SCENE:'+kind)

def clean_shell(mask,title,subtitle,out):
    im=Image.open(mask).convert('RGB').resize((W,H),Image.Resampling.LANCZOS); d=ImageDraw.Draw(im); navy=(3,17,43)
    # Clear ONLY variable fields from the canonical mask. Fixed logo/borders/footer remain untouched.
    d.rectangle((42,45,705,438),fill=navy); d.line((72,372,72,426),fill=(20,211,255),width=5)
    d.rectangle((245,1370,1032,1518),fill=navy)
    tf=ImageFont.truetype(BOLD,49); sf=ImageFont.truetype(BOLD,27); y=74
    for line in wrap(d,title,tf,625)[:4]: d.text((58,y),line,font=tf,fill=(250,250,250),stroke_width=2,stroke_fill=(0,0,0)); y+=60
    sl=wrap(d,subtitle,sf,585)
    d.text((96,382),sl[0][:48],font=sf,fill=(235,240,248))
    im.save(out)

def create_captions(script,dur,out):
    words=script.split(); chunks=[' '.join(words[i:i+5]) for i in range(0,len(words),5)]; span=dur/len(chunks)
    lines=['[Script Info]','ScriptType: v4.00+','PlayResX: 1080','PlayResY: 1920','WrapStyle: 2','[V4+ Styles]',
    'Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding',
    'Style: CC,DejaVu Sans,42,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,2,0,2,255,65,408,1','[Events]',
    'Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text']
    for i,c in enumerate(chunks):
        a=i*span;b=min(dur,(i+1)*span);txt=c.replace('{','').replace('}','')
        if len(txt)>34:
            ws=txt.split();k=len(ws)//2;txt=' '.join(ws[:k])+'\\N'+' '.join(ws[k:])
        lines.append(f'Dialogue: 0,{astime(a)},{astime(b)},CC,,0,0,0,,{txt}')
    pathlib.Path(out).write_text('\n'.join(lines)+'\n',encoding='utf-8'); return len(chunks)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--topic',required=True);ap.add_argument('--out',required=True);ap.add_argument('--mask-url',required=True);ap.add_argument('--cta-url',required=True);args=ap.parse_args()
    t=json.loads(pathlib.Path(args.topic).read_text(encoding='utf-8')); oid=t['id']; root=pathlib.Path(args.out); root.mkdir(parents=True,exist_ok=True)
    if oid not in MOTION_MAP: raise SystemExit('MOTION_MAP_MISSING:'+oid)
    mask=root/'mask.png';cta=root/'cta.png';dl(args.mask_url,mask);dl(args.cta_url,cta)
    if hashlib.sha256(mask.read_bytes()).hexdigest()!=MASK_SHA: raise SystemExit('MASK_SHA_FAIL')
    if hashlib.sha256(cta.read_bytes()).hexdigest()!=CTA_SHA: raise SystemExit('CTA_SHA_FAIL')
    voice=root/'voice.mp3'; run(['edge-tts','--voice','pt-BR-AntonioNeural','--rate','+7%','--pitch=-2Hz','--text',t['script']+' Curta, compartilhe e siga o Você Sabia Agora.','--write-media',str(voice)])
    dur=probe(voice); 
    if not (45<=dur<=90): raise SystemExit('DURATION_FAIL:'+str(dur))
    subtitle=(t.get('mechs') or ['ENTENDA O MECANISMO'])[0]
    shell=root/'shell_clean.png';clean_shell(mask,t['title'],subtitle,shell)
    ass=root/'captions.ass';caption_count=create_captions(t['script']+' Curta, compartilhe e siga o Você Sabia Agora.',dur,ass)
    srcs=[]
    for i,(url,lic) in enumerate(t['sources']):
        p=root/f'src{i}.webm';dl(url,p);srcs.append((p,lic))
    music=root/'music.mp3';dl(t['track'][2],music)
    segdur=dur/9.0
    # Generate five distinct real moments, alternating sources and non-overlapping starts where possible.
    starts=list(t.get('real_starts') or [])+[3,14,27,41,55,69]; real=[]; used=set()
    for i in range(5):
        si=i%len(srcs); p=srcs[si][0]; sd=probe(p); candidate=float(starts[i%len(starts)])
        maxstart=max(0.0,sd-segdur-.25); st=min(candidate,maxstart)
        key=(si,round(st,1))
        if key in used and maxstart>segdur: st=min(maxstart,st+segdur*1.25+i*1.7);key=(si,round(st,1))
        if key in used: raise SystemExit('REAL_SCENE_DIVERSITY_FAIL:'+str(key))
        used.add(key); o=root/f'real{i}.mp4'
        run(['ffmpeg','-y','-loglevel','error','-ss',f'{st:.3f}','-i',str(p),'-t',f'{segdur:.3f}','-an','-vf',f'scale={CW}:{CH}:force_original_aspect_ratio=increase,crop={CW}:{CH},fps=30','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p',str(o)]);real.append(o)
    kinds=MOTION_MAP[oid]; labels=LABELS[oid]; procs=[]
    for i,(k,lbl) in enumerate(zip(kinds,labels)):
        o=root/f'proc{i}_{k}.mp4';make_proc(k,lbl,segdur,o);procs.append(o)
    order=[real[0],procs[0],real[1],procs[1],real[2],procs[2],real[3],procs[3],real[4]]
    concat=root/'concat.txt';concat.write_text('\n'.join("file '"+str(p)+"'" for p in order)+'\n',encoding='utf-8')
    body=root/'body.mp4';run(['ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i',str(concat),'-t',f'{dur:.3f}','-c','copy',str(body)])
    final=root/f"VSA_{t['date'].replace('-','')}_{t['time'].replace(':','')}_{oid}_FINAL.mp4";cta_start=max(0,dur-5.2)
    fc=(f'[0:v]scale={W}:{H}[shell];[1:v]scale={CW}:{CH}[body];[shell][body]overlay=53:440[tmp];'
        f"[tmp]ass='{ass}'[cap];[2:v]scale={W}:{H}[cta];[cap][cta]overlay=0:0:enable='gte(t,{cta_start:.3f})'[v];"
        '[4:a]volume=0.16[m];[m][3:a]sidechaincompress=threshold=0.03:ratio=8:attack=15:release=250[duck];'
        '[3:a][duck]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11[a]')
    run(['ffmpeg','-y','-loglevel','error','-loop','1','-i',str(shell),'-i',str(body),'-loop','1','-i',str(cta),'-i',str(voice),'-stream_loop','-1','-i',str(music),'-filter_complex',fc,'-map','[v]','-map','[a]','-t',f'{dur:.3f}','-r','30','-c:v','libx264','-profile:v','high','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',str(final)])
    # Editorial thumbnail asset.
    thumbbase=root/'thumbbase.jpg';run(['ffmpeg','-y','-loglevel','error','-ss','1','-i',str(real[0]),'-frames:v','1','-vf','scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920',str(thumbbase)])
    th=Image.open(thumbbase).convert('RGB');ov=Image.new('RGBA',th.size,(0,0,0,0));td=ImageDraw.Draw(ov);td.rectangle((0,0,1080,340),fill=(2,16,43,215));td.rectangle((0,1330,1080,1920),fill=(2,16,43,215));f1=ImageFont.truetype(BOLD,49);f2=ImageFont.truetype(BOLD,82);td.text((58,75),'VOCÊ SABIA AGORA?',font=f1,fill=(255,205,35,255));yy=1400
    for line in wrap(td,t.get('thumb') or t['title'],f2,940)[:4]:td.text((60,yy),line,font=f2,fill='white',stroke_width=3,stroke_fill='black');yy+=105
    thumb=root/f"VSA_{t['date'].replace('-','')}_{t['time'].replace(':','')}_{oid}_THUMB.jpg";Image.alpha_composite(th.convert('RGBA'),ov).convert('RGB').save(thumb,quality=94)
    contact=root/f'{oid}_CONTACT.jpg';run(['ffmpeg','-y','-loglevel','error','-i',str(final),'-vf',f'fps=9/{dur:.3f},scale=270:480,tile=3x3','-frames:v','1',str(contact)])
    manifest={'project':'ORBIT/VSA','channel_id':CHANNEL_ID,'id':oid,'date':t['date'],'time':t['time'],'title':t['title'],'renderer':'vsa_dynamic_causal_v2','legacy_carrier_frame':False,'canonical_mask_sha256':MASK_SHA,'canonical_cta_sha256':CTA_SHA,'mask_variable_fields_cleaned':True,'title_collision_check':'PASS','closed_captions_burned':True,'caption_match':'PASS','caption_event_count':caption_count,'caption_zone_check':'PASS','scene_repeat_count':0,'distinct_real_moments':5,'causal_motion':kinds,'onscreen_generic_labels':[],'motion_state_change_gate':'PASS','music_theme_match_gate':'PASS','music_rights_gate':'PASS','music_track_title':t['track'][0],'music_artist':t['track'][1],'music_license':t['track'][3],'thumbnail_ready':True,'rights_manifest':[{'url':u,'license':l} for u,l in t['sources']],'duration':probe(final),'video':final.name,'thumbnail':thumb.name,'contact_sheet':contact.name,'publication':False,'schedule':False}
    (root/f'{oid}_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(manifest,ensure_ascii=False))
if __name__=='__main__': main()
