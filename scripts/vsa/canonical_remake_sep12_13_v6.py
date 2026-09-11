#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import pathlib
from PIL import Image, ImageChops, ImageDraw, ImageStat

import canonical_remake_sep12_13_v5 as v5

v4 = v5.v4
base = v5.base

# Roosevelt: replace the misleading 1916 opening with event-matched Milwaukee imagery
# from Oct. 14, 1912. All four assets are archival evidence, not reenactments.
v4.SOURCE_OVERRIDES['ROOSEVELT'] = [
    (v4.commons_file('Theodore Roosevelt speaking from a car in Milwaukee Wisconsin on Oct. 14, 1912.webp'), 'Public domain - pre-1931 U.S. publication / Wikimedia Commons'),
    (v4.commons_file('TR Assassination Bullet Damage.jpg'), 'CC BY-SA 3.0 / GFDL - Richard W. Allen'),
    (v4.commons_file('Theodore Roosevelt after he was shot 1912.jpg'), 'Public domain - pre-1931 publication'),
    (v4.commons_file("Mercy Hospital - Roosevelt's rooms LCCN2014690905.jpg"), 'Public domain - Library of Congress'),
]

_CAPTURED_WORDS = []
_ORIGINAL_BUILD_ASS = base.build_ass


def _capture_build_ass(words, ass):
    global _CAPTURED_WORDS
    _CAPTURED_WORDS = [dict(w) for w in words]
    return _ORIGINAL_BUILD_ASS(words, ass)


base.build_ass = _capture_build_ass


def _header(label: str):
    im = Image.new('RGB', (976, 844), base.NAVY)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 976, 76), fill=(5, 34, 70))
    d.text((28, 20), label, font=base.font(26), fill=base.WHITE)
    d.line((28, 72, 948, 72), fill=base.CYAN, width=2)
    return im, d


def _pill(d, box, text, active=True):
    fill = (30, 118, 168) if active else (30, 48, 70)
    outline = base.GOLD if active else (80, 100, 120)
    d.rounded_rectangle(box, 14, fill=fill, outline=outline, width=3)
    x0, y0, x1, y1 = box
    tw = d.textbbox((0, 0), text, font=base.font(20))[2]
    d.text(((x0 + x1 - tw) / 2, y0 + 12), text, font=base.font(20), fill=base.WHITE)


def narrative_anim_frame_v6(mode: str, idx: int, p: float, label: str) -> Image.Image:
    if mode not in {'influence', 'credibility', 'timeline', 'message', 'ballistic'} or idx not in {1, 3, 5}:
        return v4.narrative_anim_frame(mode, idx, p, label)

    im, d = _header(label)

    if mode == 'influence':
        if idx == 1:
            # Followers != influence: audience count on the left, trust/connection factors on right.
            d.text((85, 150), 'SEGUIDORES', font=base.font(24), fill=base.WHITE)
            d.text((620, 150), 'INFLUÊNCIA', font=base.font(24), fill=base.WHITE)
            for j in range(8):
                x = 95 + (j % 4) * 72
                y = 230 + (j // 4) * 85
                r = 16 + int(5 * math.sin((p + j * .08) * math.pi) ** 2)
                d.ellipse((x-r, y-r, x+r, y+r), fill=(62, 135, 185), outline=base.WHITE, width=2)
            factors = [('CONFIANÇA', 580, 250), ('INSPIRAÇÃO', 675, 390), ('CONEXÃO', 575, 535)]
            cx, cy = 785, 420
            d.ellipse((cx-42, cy-42, cx+42, cy+42), fill=base.GOLD, outline=base.WHITE, width=4)
            for j, (txt, x, y) in enumerate(factors):
                q = max(0.0, min(1.0, p * 1.4 - j * .15))
                ex = int(x + (cx-x) * q); ey = int(y + (cy-y) * q)
                _pill(d, (x-70, y-26, x+90, y+28), txt, True)
                base.arrow(d, (x+90, y), (ex, ey), base.CYAN, 4)
            d.text((130, 700), 'QUANTIDADE', font=base.font(22), fill=(160, 185, 210))
            d.text((665, 700), 'EFEITO REAL', font=base.font(22), fill=base.GOLD)
        elif idx == 3:
            # Explanation -> demonstration -> understanding -> trust.
            xs = [90, 300, 520, 745]
            names = ['PERGUNTA', 'DEMO', 'ENTENDE', 'CONFIA']
            for j, (x, name) in enumerate(zip(xs, names)):
                q = max(0.0, min(1.0, p * 1.6 - j * .18))
                y = 395 - int(38 * math.sin(q * math.pi))
                _pill(d, (x, y, x+150, y+64), name, q > .05)
                if j < 3:
                    base.arrow(d, (x+150, y+32), (xs[j+1]-12, y+32), base.CYAN if j < 2 else base.GOLD, 5)
            meter = int(650 * p)
            d.rounded_rectangle((160, 620, 815, 692), 18, outline=base.CYAN, width=4)
            d.rounded_rectangle((172, 632, 172+meter, 680), 12, fill=(40, 150, 200))
            d.text((355, 642), 'CONFIANÇA', font=base.font(23), fill=base.WHITE)
        else:
            # Experience -> memory -> share cascade.
            centers = [(180, 420), (470, 420), (760, 420)]
            names = ['EXPERIÊNCIA', 'MEMÓRIA', 'COMPARTILHA']
            for j, ((x, y), name) in enumerate(zip(centers, names)):
                r = 52 + int(10 * math.sin((p + j * .12) * math.pi) ** 2)
                d.ellipse((x-r, y-r, x+r, y+r), fill=(32, 108, 160), outline=base.GOLD if j == 1 else base.CYAN, width=4)
                tw = d.textbbox((0,0), name, font=base.font(19))[2]
                d.text((x-tw/2, y-10), name, font=base.font(19), fill=base.WHITE)
                if j < 2:
                    q = max(.12, min(1.0, p * 1.5 - j * .2))
                    base.arrow(d, (x+58, y), (x+58+int(165*q), y), base.GOLD, 5)
            for j in range(7):
                ang = 2*math.pi*j/7
                q = max(0.0, min(1.0, (p-.25)*1.5))
                x = 760 + int(math.cos(ang)*150*q); y = 420 + int(math.sin(ang)*150*q)
                d.ellipse((x-12, y-12, x+12, y+12), fill=(72,150,205), outline=base.WHITE, width=2)

    elif mode == 'credibility':
        if idx == 1:
            # Decades accumulate repertoire.
            x0, x1, y = 115, 860, 490
            d.line((x0, y, x1, y), fill=(70, 110, 150), width=8)
            years = ['1967','1980','2000','2012','2019','2026']
            for j, year in enumerate(years):
                x = x0 + int((x1-x0)*j/(len(years)-1))
                q = max(0, min(1, p*1.25-j*.12))
                r = 10 + int(9*q)
                d.ellipse((x-r,y-r,x+r,y+r), fill=base.GOLD if q>.4 else (55,80,105), outline=base.WHITE, width=2)
                d.text((x-27,y+34), year, font=base.font(17), fill=base.WHITE)
            d.text((245, 235), 'TEMPO + REPERTÓRIO', font=base.font(30), fill=base.GOLD)
            d.rounded_rectangle((205, 620, 770, 690), 18, outline=base.CYAN, width=4)
            d.rounded_rectangle((217,632,217+int(540*p),678), 12, fill=(45,145,198))
        elif idx == 3:
            # Consistency triangle -> trust.
            pts = [(220, 590), (488, 180), (755, 590)]
            names = ['TRAJETÓRIA', 'COMPETÊNCIA', 'COMPORTAMENTO']
            center = (488, 455)
            for j, (pt, name) in enumerate(zip(pts, names)):
                _pill(d, (pt[0]-95, pt[1]-35, pt[0]+105, pt[1]+28), name, True)
                q=max(0,min(1,p*1.4-j*.13)); ex=int(pt[0]+(center[0]-pt[0])*q); ey=int(pt[1]+(center[1]-pt[1])*q)
                base.arrow(d, pt, (ex,ey), base.CYAN, 4)
            r = 36 + int(18*p)
            d.ellipse((center[0]-r,center[1]-r,center[0]+r,center[1]+r), fill=base.GOLD, outline=base.WHITE, width=4)
            d.text((425,445),'CONFIANÇA',font=base.font(18),fill=base.NAVY)
        else:
            # Longevity compounds into credibility.
            d.text((300, 165), 'LONGEVIDADE', font=base.font(30), fill=base.WHITE)
            for j in range(5):
                q=max(0,min(1,p*1.5-j*.12))
                x=170+j*135; h=int(90+260*q)
                d.rounded_rectangle((x,690-h,x+95,690),12,fill=(28+10*j,90+12*j,140+10*j),outline=base.GOLD if j==4 else base.CYAN,width=3)
            base.arrow(d,(180,735),(785,735),base.GOLD,6)
            d.text((300, 760), 'CREDIBILIDADE ACUMULADA', font=base.font(24), fill=base.GOLD)

    elif mode == 'timeline':
        if idx == 1:
            # Same role evolves through distinct phases.
            roles = [('DETETIVE',170),('REFERÊNCIA',330),('LIDERANÇA',490),('NOVA FASE',650)]
            for j,(name,y) in enumerate(roles):
                q=max(0,min(1,p*1.5-j*.16)); _pill(d,(280,y,695,y+65),name,q>.05)
                if j<3: base.arrow(d,(488,y+65),(488,y+125),base.CYAN,5)
            d.text((290, 110), 'A PERSONAGEM MUDA', font=base.font(30), fill=base.GOLD)
        elif idx == 3:
            # Responsibility ladder.
            d.text((255, 145), 'RESPONSABILIDADE', font=base.font(30), fill=base.WHITE)
            for j in range(5):
                q=max(0,min(1,p*1.6-j*.12)); x=170+j*135; y=675-j*105
                d.rectangle((x, y, x+110, 735), fill=(30, 90+20*j, 145+12*j), outline=base.GOLD if q>.55 else base.CYAN, width=3)
                if q>.15: d.ellipse((x+42,y-34,x+68,y-8), fill=base.GOLD)
            base.arrow(d,(135,720),(845,215),base.GOLD,6)
        else:
            # Familiarity + renewal merge into longevity.
            _pill(d,(90,250,350,320),'FAMILIARIDADE',True)
            _pill(d,(90,560,350,630),'RENOVAÇÃO',True)
            target=(750,440)
            q=max(.1,min(1,p*1.35))
            base.arrow(d,(350,285),(350+int(360*q),285+int(155*q)),base.CYAN,6)
            base.arrow(d,(350,595),(350+int(360*q),595-int(155*q)),base.GOLD,6)
            r=48+int(18*p)
            d.ellipse((target[0]-r,target[1]-r,target[0]+r,target[1]+r),fill=(34,130,180),outline=base.WHITE,width=4)
            d.text((680,430),'LONGEVIDADE',font=base.font(19),fill=base.WHITE)

    elif mode == 'message':
        if idx == 1:
            # Popularity vs influence.
            d.text((95,150),'POPULARIDADE',font=base.font(26),fill=base.WHITE)
            d.text((620,150),'INFLUÊNCIA',font=base.font(26),fill=base.WHITE)
            for j in range(14):
                x=95+(j%5)*55; y=240+(j//5)*70
                d.ellipse((x-11,y-11,x+11,y+11),fill=(75,145,195),outline=base.WHITE,width=2)
            q=max(.1,min(1,p*1.25));
            for j,(x,y) in enumerate([(655,260),(820,250),(700,520),(840,560)]):
                base.arrow(d,(720,410),(720+int((x-720)*q),410+int((y-410)*q)),base.GOLD if j%2 else base.CYAN,5)
                d.ellipse((x-15,y-15,x+15,y+15),fill=(35,120,170),outline=base.WHITE,width=2)
            d.rounded_rectangle((635,365,805,455),18,fill=(35,90,135),outline=base.GOLD,width=4)
            d.text((660,395),'MENSAGEM',font=base.font(24),fill=base.WHITE)
        elif idx == 3:
            # Music + narrative + identity + social themes -> one recognizable message.
            items=[('MÚSICA',(105,220)),('NARRATIVA',(650,220)),('IDENTIDADE',(105,590)),('TEMAS',(650,590))]
            center=(485,420)
            for j,(name,(x,y)) in enumerate(items):
                _pill(d,(x,y,x+220,y+62),name,True)
                q=max(0,min(1,p*1.45-j*.1)); base.arrow(d,(x+110,y+62 if y<420 else y),(int(x+110+(center[0]-x-110)*q),int((y+62 if y<420 else y)+(center[1]-(y+62 if y<420 else y))*q)),base.CYAN if j%2==0 else base.GOLD,4)
            d.ellipse((425,360,545,480),fill=(30,105,160),outline=base.WHITE,width=4)
            d.text((446,407),'VOZ',font=base.font(24),fill=base.WHITE)
        else:
            # Message propagation beyond the launch moment.
            center=(180,420)
            d.rounded_rectangle((95,365,265,475),18,fill=(35,95,145),outline=base.GOLD,width=4)
            d.text((116,405),'MENSAGEM',font=base.font(22),fill=base.WHITE)
            nodes=[(460,220),(470,420),(455,620),(760,170),(785,350),(770,560),(610,710)]
            for j,(x,y) in enumerate(nodes):
                q=max(0,min(1,p*1.55-j*.08)); ex=center[0]+int((x-center[0])*q); ey=center[1]+int((y-center[1])*q)
                base.arrow(d,center,(ex,ey),base.GOLD if j%2 else base.CYAN,4)
                d.ellipse((x-14,y-14,x+14,y+14),fill=(38,125,175),outline=base.WHITE,width=2)

    elif mode == 'ballistic':
        if idx == 1:
            # Bullet -> metal case -> folded speech; visible loss of speed/energy.
            d.rectangle((405,220,525,640),fill=(115,125,135),outline=base.WHITE,width=3)
            d.rectangle((545,180,760,680),fill=(232,225,198),outline=base.WHITE,width=3)
            for j in range(10): d.line((565,225+j*38,735,225+j*38),fill=(120,115,105),width=2)
            x=95+int(590*p); r=11
            d.ellipse((x-r,420-r,x+r,420+r),fill=base.GOLD,outline=base.WHITE,width=2)
            if x>390: d.arc((355,345,605,595),200,340,fill=(255,95,70),width=5)
            energy=int(600*(1-.65*p)); d.rectangle((170,735,170+energy,765),fill=base.GOLD)
            d.text((170,782),'ENERGIA RESTANTE',font=base.font(18),fill=base.WHITE)
        elif idx == 3:
            # Wound remains real; projectile stops in the body.
            d.ellipse((345,150,630,735),outline=(130,170,205),width=7)
            d.line((488,210,488,650),fill=(100,140,175),width=5)
            x=145+int(375*p)
            d.ellipse((x-10,390-10,x+10,390+10),fill=base.GOLD,outline=base.WHITE,width=2)
            d.arc((385,300,590,505),0,360,fill=(255,95,75),width=6)
            if p>.58:
                d.ellipse((505,378,529,402),fill=(255,80,65),outline=base.WHITE,width=2)
                d.text((580,370),'PROJÉTIL RETIDO',font=base.font(21),fill=base.GOLD)
        else:
            # Event order: shot -> speech -> hospital.
            xs=[145,485,820]; names=['TIRO','DISCURSO','HOSPITAL']
            d.line((145,430,820,430),fill=(65,110,150),width=8)
            for j,(x,name) in enumerate(zip(xs,names)):
                q=max(0,min(1,p*1.5-j*.18)); r=13+int(10*q)
                d.ellipse((x-r,430-r,x+r,430+r),fill=base.GOLD if q>.5 else (55,80,105),outline=base.WHITE,width=3)
                _pill(d,(x-95,520,x+95,582),name,q>.05)
            marker=145+int((820-145)*p)
            d.polygon([(marker,340),(marker-18,385),(marker+18,385)],fill=base.CYAN)
            d.text((295,175),'ELE ESCOLHE FALAR ANTES',font=base.font(29),fill=base.GOLD)

    return im


def _word_times(word):
    st = float(word.get('offset', 0))/10000000
    en = st + float(word.get('duration', 0))/10000000
    return st, en


def _animation_distinctness(video_id: str, body: float, nblocks: int):
    work = pathlib.Path('/tmp') / ('vsa_remake_' + video_id)
    seg = body / nblocks
    frames = []
    for i in (1, 3, 5):
        src = work / f'block_{i:02}.mp4'
        p = work / f'v6_anim_mid_{i}.png'
        base.run(['ffmpeg','-y','-loglevel','error','-ss',f'{seg*.5:.3f}','-i',str(src),'-frames:v','1',str(p)])
        frames.append(Image.open(p).convert('L').resize((244,211)))
    diffs = []
    for a, b in zip(frames, frames[1:]):
        diff = ImageChops.difference(a, b)
        score = float(ImageStat.Stat(diff).mean[0])
        diffs.append(round(score, 3))
    if min(diffs) < 7.0:
        raise RuntimeError(f'ANIMATION_DISTINCTNESS_FAIL {video_id} {diffs}')
    return diffs


def build_v6(topic, golden: pathlib.Path, outdir: pathlib.Path):
    global _CAPTURED_WORDS
    _CAPTURED_WORDS = []
    video_id = topic['id']
    v4.build_v4(topic, golden, outdir)

    receipt_path = outdir / f'{video_id}_VSA_VISUAL_RELEASE_RECEIPT_V1.json'
    receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
    body = max(1.0, float(receipt['master']['duration']) - 4.2)
    nblocks = len(receipt['shot_map'])
    seg = body / nblocks

    if not _CAPTURED_WORDS:
        raise RuntimeError('NARRATION_BOUNDARY_CAPTURE_EMPTY')

    for i, shot in enumerate(receipt['shot_map']):
        lo, hi = i*seg, (i+1)*seg
        tokens = []
        for w in _CAPTURED_WORDS:
            st, en = _word_times(w)
            mid = (st + en) / 2
            if lo <= mid < hi:
                txt = str(w.get('text','')).strip()
                if txt:
                    tokens.append(txt)
        quote = ' '.join(tokens).strip()
        if len(quote.split()) < 3:
            raise RuntimeError(f'NARRATION_BOUNDARY_TOO_SHORT block={i+1} quote={quote!r}')
        editorial = shot.get('narration','')
        shot['editorial_visual_requirement'] = editorial
        shot['narration'] = quote
        shot['narration_quote'] = quote
        shot['semantic_claim'] = quote
        shot['narration_alignment_source'] = 'EDGE_TTS_WORD_BOUNDARIES'
        if shot.get('media_type') == 'ANIMATION':
            shot['animation_variant'] = f'{base.ANIM_MODE.get(video_id, "custom")}_block_{i+1}'

    diffs = _animation_distinctness(video_id, body, nblocks)
    receipt['visual_proof']['animation_distinctness_midframe_mean_abs_diff'] = diffs
    receipt['gates']['NARRATION_BOUNDARY_PASS'] = True
    receipt['gates']['ANIMATION_DISTINCTNESS_PASS'] = True
    # Semantic alignment is intentionally not auto-approved anymore. It remains a
    # human gate and therefore cannot silently become release-eligible.
    receipt['gates']['VISUAL_NARRATIVE_ALIGNMENT_PASS'] = False
    receipt['repair_version'] = 'V6_NARRATION_BOUND_DISTINCT_ANIMATION'
    receipt['human_review']['approved'] = False
    receipt['release_eligible'] = False
    receipt['schedule_mutated_before_gate'] = False
    receipt['status'] = 'AWAITING_HUMAN_VISUAL_ALIGNMENT_REVIEW'
    receipt['qa_contract'] = {
        'narration_quote_bound_to_render_timing': True,
        'three_animation_blocks_must_be_visually_distinct': True,
        'visual_narrative_alignment_requires_human_approval': True,
        'generic_label_alone_can_never_release': True,
    }
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


base.anim_frame = narrative_anim_frame_v6
base.build = build_v6

if __name__ == '__main__':
    base.main()
