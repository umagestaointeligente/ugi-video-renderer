#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import pathlib
from PIL import Image, ImageDraw

import canonical_remake_sep12_13_v6 as v6

v4 = v6.v4
base = v6.base

# Reorder real evidence so each real block continues the narration instead of
# merely showing the correct person/topic.
v4.SOURCE_OVERRIDES['IBERE'] = [
    ('https://commons.wikimedia.org/wiki/Special:Redirect/file/-SomosLivres_-_Iber%C3%AA_Then%C3%B3rio.webm', 'CC BY 3.0 - Repórter Brasil'),
    (v4.commons_file('CPBR14 (52531831354).jpg'), 'CC BY-SA 2.0 - Campus Party Brasil'),
    (v4.commons_file('Iberê Thenório e Mariana Fulfaro no Campus Party Brasil 2015.jpg'), 'CC BY-SA 2.0 - Campus Party Brasil'),
    (v4.commons_file('CPBR14 (52529437047).jpg'), 'CC BY-SA 2.0 - Campus Party Brasil'),
]

v4.SOURCE_OVERRIDES['MARISKA_LONGEVITY'] = [
    (v4.commons_file('Mariska Hargitay on set of SVU season 12.jpg'), 'CC BY-SA 2.0 - Lori_NY'),
    (v4.commons_file('MariskaHargitay.jpg'), 'CC BY 2.0 - Veronica Romm'),
    (v4.commons_file('Mariska Hargitay Reads "Oh! The Places You\'ll Go!".webm'), 'Public domain - White House'),
    (v4.commons_file('Mariska Hargitay 2025.jpg'), 'CC BY-SA 4.0 - Colleen Sturtevant'),
]

v4.SOURCE_OVERRIDES['EMICIDA_INFLUENCE'] = [
    ('https://commons.wikimedia.org/wiki/Special:Redirect/file/Campus_Party-_Rapper_Emicida_x_Ecad.webm', 'CC BY 3.0 - EBC na Rede, reviewed'),
    (v4.commons_file('Emicida no Campus Party Brasil 2012.jpg'), 'CC BY-SA 2.0 - Campus Party Brasil'),
    (v4.commons_file('Emicida en MICA 2023.jpg'), 'CC BY-SA 2.0 - Ministerio de Cultura de la Nación'),
    (v4.commons_file('Emicida.jpg'), 'CC BY 2.0 - Patricia Oliveira'),
]


def _header(label: str):
    im = Image.new('RGB', (976, 844), base.NAVY)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 976, 76), fill=(5, 34, 70))
    d.text((28, 20), label, font=base.font(26), fill=base.WHITE)
    d.line((28, 72, 948, 72), fill=base.CYAN, width=2)
    return im, d


def _pill(d, box, text, active=True, fontsize=20):
    fill = (30, 118, 168) if active else (30, 48, 70)
    outline = base.GOLD if active else (80, 100, 120)
    d.rounded_rectangle(box, 14, fill=fill, outline=outline, width=3)
    x0, y0, x1, y1 = box
    f = base.font(fontsize)
    tw = d.textbbox((0, 0), text, font=f)[2]
    d.text(((x0 + x1 - tw) / 2, y0 + (y1-y0-fontsize)/2 - 2), text, font=f, fill=base.WHITE)


def _fernanda_frame(idx: int, p: float, label: str):
    im, d = _header(label)
    if idx == 1:
        # Actual narration: success/trust does not depend on posting all the time.
        d.text((98, 135), 'POSTAR MAIS', font=base.font(28), fill=base.WHITE)
        d.text((610, 135), 'CONFIANÇA', font=base.font(28), fill=base.GOLD)
        # Fast-moving post cards on the left.
        for j in range(5):
            y = 210 + j * 92
            shift = int(((p * 260 + j * 45) % 300) - 150)
            x = 90 + shift
            d.rounded_rectangle((x, y, x+300, y+58), 10, fill=(30, 95, 145), outline=base.CYAN, width=3)
            d.line((x+22, y+20, x+210, y+20), fill=base.WHITE, width=4)
            d.line((x+22, y+38, x+150, y+38), fill=(150,185,210), width=3)
        # Trust stays strong and grows even though posting cards move independently.
        cx, cy = 735, 430
        r = 90 + int(28 * math.sin(p * math.pi) ** 2)
        d.ellipse((cx-r, cy-r, cx+r, cy+r), fill=(34, 130, 180), outline=base.GOLD, width=7)
        d.text((655, 416), 'CONFIANÇA', font=base.font(24), fill=base.WHITE)
        d.text((565, 650), 'FREQUÊNCIA ≠ CREDIBILIDADE', font=base.font(23), fill=base.GOLD)
    elif idx == 3:
        # Actual narration: repeated exposure is not credibility; consistency builds trust.
        d.text((75, 125), 'EXPOSIÇÃO', font=base.font(27), fill=base.WHITE)
        d.text((580, 125), 'CREDIBILIDADE', font=base.font(27), fill=base.GOLD)
        exposure = int(330 * (0.25 + 0.75 * abs(math.sin(p * math.pi * 2))))
        d.rectangle((90, 220, 90+exposure, 290), fill=(45, 135, 185), outline=base.WHITE, width=3)
        d.text((100, 310), 'aparecer muito', font=base.font(20), fill=(165,190,210))
        stages = [('TRAJETÓRIA', 560, 250), ('COMPETÊNCIA', 610, 390), ('CONSISTÊNCIA', 560, 530)]
        target = (790, 420)
        for j,(txt,x,y) in enumerate(stages):
            q = max(0.0, min(1.0, p*1.6-j*.16))
            _pill(d,(x-85,y-28,x+105,y+32),txt,True,18)
            ex = int(x + (target[0]-x)*q); ey = int(y + (target[1]-y)*q)
            base.arrow(d,(x+105,y+2),(ex,ey),base.CYAN if j<2 else base.GOLD,5)
        rr = 45 + int(30*p)
        d.ellipse((target[0]-rr,target[1]-rr,target[0]+rr,target[1]+rr),fill=base.GOLD,outline=base.WHITE,width=4)
        d.text((744,410),'CONFIA',font=base.font(19),fill=base.NAVY)
        d.text((235, 720), 'EXPOSIÇÃO ≠ CREDIBILIDADE', font=base.font(26), fill=base.GOLD)
    elif idx == 5:
        # Actual narration: fewer appearances can preserve symbolic strength; longevity compounds it.
        d.text((80, 130), 'MENOS APARIÇÕES', font=base.font(26), fill=base.WHITE)
        d.text((590, 130), 'FORÇA SIMBÓLICA', font=base.font(26), fill=base.GOLD)
        for j in range(4):
            q = max(0.0, min(1.0, p*1.7-j*.22))
            x = 110 + j*110
            y = 280 + int(190*q)
            d.rounded_rectangle((x,y,x+80,y+95),12,fill=(30,105,155),outline=base.CYAN,width=3)
        cx,cy=730,405
        rays = 10
        for j in range(rays):
            ang=2*math.pi*j/rays
            rr=int(95+100*p)
            x=cx+int(math.cos(ang)*rr); y=cy+int(math.sin(ang)*rr)
            d.line((cx,cy,x,y),fill=base.GOLD,width=4)
        r=68+int(22*math.sin(p*math.pi)**2)
        d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(35,125,175),outline=base.WHITE,width=5)
        d.text((670,395),'PRESENÇA',font=base.font(21),fill=base.WHITE)
        d.rounded_rectangle((290,680,700,748),16,fill=(28,90,138),outline=base.GOLD,width=4)
        d.rectangle((305,695,305+int(380*p),733),fill=(48,155,205))
        d.text((405,699),'LONGEVIDADE',font=base.font(20),fill=base.WHITE)
    return im


def _emicida_popularity_frame(p: float, label: str):
    im, d = _header(label)
    d.text((75, 125), 'POPULARIDADE', font=base.font(27), fill=base.WHITE)
    d.text((600, 125), 'INFLUÊNCIA', font=base.font(27), fill=base.GOLD)
    # Large audience count grows vertically on left.
    for j in range(10):
        col=j%5; row=j//5
        x=85+col*72; y0=600-row*105
        travel=int(150*p)
        y=y0-travel
        r=22+int(7*math.sin((p+j*.09)*math.pi)**2)
        d.ellipse((x-r,y-r,x+r,y+r),fill=(60,145,195),outline=base.WHITE,width=3)
    d.rectangle((70,680,430,725),outline=base.CYAN,width=4)
    d.rectangle((75,685,75+int(345*p),720),fill=(45,145,195))
    # Influence is a message that visibly travels through a network over a much larger area.
    source=(650,420)
    d.rounded_rectangle((565,365,735,475),18,fill=(35,95,145),outline=base.GOLD,width=5)
    d.text((585,405),'MENSAGEM',font=base.font(22),fill=base.WHITE)
    nodes=[(830,210),(835,390),(820,610),(620,690),(505,590),(500,245)]
    for j,(x,y) in enumerate(nodes):
        q=max(0.0,min(1.0,p*1.65-j*.09))
        ex=source[0]+int((x-source[0])*q); ey=source[1]+int((y-source[1])*q)
        base.arrow(d,source,(ex,ey),base.GOLD if j%2 else base.CYAN,6)
        rr=12+int(15*q)
        d.ellipse((x-rr,y-rr,x+rr,y+rr),fill=(34,130,180),outline=base.WHITE,width=3)
    d.text((165, 770), 'SER VISTO', font=base.font(22), fill=(170,190,210))
    d.text((650, 770), 'FAZER A IDEIA VIAJAR', font=base.font(22), fill=base.GOLD)
    return im


def _roosevelt_wound_frame(p: float, label: str):
    im, d = _header(label)
    d.text((250, 120), 'O FERIMENTO CONTINUA REAL', font=base.font(28), fill=base.WHITE)
    # Large torso and moving bullet path so motion is visible across a broad region.
    d.rounded_rectangle((340,180,690,735),80,fill=(24,78,118),outline=(145,185,215),width=7)
    d.line((515,220,515,680),fill=(90,145,185),width=6)
    start=(95,415); end=(520,415)
    q=min(1.0,p*1.25)
    bx=int(start[0]+(end[0]-start[0])*q)
    # swept trajectory behind projectile
    d.line((start[0],start[1],bx,start[1]),fill=base.GOLD,width=16)
    d.ellipse((bx-18,397,bx+18,433),fill=(255,190,45),outline=base.WHITE,width=3)
    # wound response expands/contracts over large area after impact
    if q>.65:
        local=(q-.65)/.35
        rr=int(35+150*local)
        d.ellipse((515-rr,415-rr,515+rr,415+rr),outline=(255,90,70),width=12)
        d.ellipse((485,385,545,445),fill=(180,45,48),outline=base.WHITE,width=5)
    # retained projectile marker moves down slightly then stops
    if p>.58:
        stop_y=415+int(95*min(1,(p-.58)/.32))
        d.ellipse((548,stop_y-14,576,stop_y+14),fill=base.GOLD,outline=base.WHITE,width=3)
        d.text((610, stop_y-14),'PROJÉTIL RETIDO',font=base.font(20),fill=base.GOLD)
    d.text((90, 735), 'TRAJETÓRIA', font=base.font(21), fill=base.GOLD)
    d.text((600, 735), 'ATENDIMENTO AINDA NECESSÁRIO', font=base.font(19), fill=base.WHITE)
    return im


def anim_frame_v7(mode: str, idx: int, p: float, label: str):
    if mode == 'credibility' and idx in {1,3,5}:
        return _fernanda_frame(idx,p,label)
    if mode == 'message' and idx == 1:
        return _emicida_popularity_frame(p,label)
    if mode == 'ballistic' and idx == 3:
        return _roosevelt_wound_frame(p,label)
    return v6.narrative_anim_frame_v6(mode,idx,p,label)


def build_v7(topic, golden: pathlib.Path, outdir: pathlib.Path):
    v6.build_v6(topic,golden,outdir)
    video_id=topic['id']
    receipt_path=outdir/f'{video_id}_VSA_VISUAL_RELEASE_RECEIPT_V1.json'
    r=json.loads(receipt_path.read_text(encoding='utf-8'))
    r['repair_version']='V7_TARGETED_SEMANTIC_MOTION'
    r['status']='AWAITING_HUMAN_VISUAL_ALIGNMENT_REVIEW'
    r['human_review']['approved']=False
    r['release_eligible']=False
    r['schedule_mutated_before_gate']=False
    r['gates']['VISUAL_NARRATIVE_ALIGNMENT_PASS']=False
    r['v7_repair_scope']={
        'real_asset_order_bound_to_narration': video_id in {'IBERE','MARISKA_LONGEVITY','EMICIDA_INFLUENCE'},
        'animation_semantics_retimed': video_id == 'FERNANDA_MONTENEGRO',
        'motion_gate_strengthened_without_threshold_reduction': video_id in {'ROOSEVELT','EMICIDA_INFLUENCE'},
        'human_alignment_gate_required': True
    }
    receipt_path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


base.anim_frame=anim_frame_v7
base.build=build_v7

if __name__=='__main__':
    base.main()
