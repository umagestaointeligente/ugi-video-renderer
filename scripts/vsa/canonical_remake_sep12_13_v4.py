#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import pathlib
import urllib.parse
from PIL import Image, ImageDraw

import canonical_remake_sep12_13_v3 as v3

v2 = v3.v2
base = v2.base

_ORIGINAL_LOAD_TOPICS = base.load_topics
_ORIGINAL_DOWNLOAD = base.download
_ORIGINAL_ANIM_FRAME = base.anim_frame
_ORIGINAL_BUILD = base.build

TARGETS = {
    'IBERE',
    'ROOSEVELT',
    'FERNANDA_MONTENEGRO',
    'MARISKA_LONGEVITY',
    'EMICIDA_INFLUENCE',
}


def commons_file(name: str) -> str:
    return 'https://commons.wikimedia.org/wiki/Special:Redirect/file/' + urllib.parse.quote(
        name, safe="()'-,._"
    )


SOURCE_OVERRIDES = {
    'IBERE': [
        ('https://commons.wikimedia.org/wiki/Special:Redirect/file/-SomosLivres_-_Iber%C3%AA_Then%C3%B3rio.webm', 'CC BY 3.0 - Repórter Brasil'),
        (commons_file('Iberê Thenório e Mariana Fulfaro no Campus Party Brasil 2015.jpg'), 'CC BY-SA 2.0 - Campus Party Brasil'),
        (commons_file('CPBR14 (52531831354).jpg'), 'CC BY-SA 2.0 - Campus Party Brasil'),
        (commons_file('CPBR14 (52529437047).jpg'), 'CC BY-SA 2.0 - Campus Party Brasil'),
    ],
    'ROOSEVELT': [
        ('https://commons.wikimedia.org/wiki/Special:Redirect/file/Theodore_Roosevelt_at_Sagamore_Hill_%281916%29.webm', 'Public domain'),
        (commons_file('TR Assassination Bullet Damage.jpg'), 'CC BY-SA 3.0 / GFDL - Richard W. Allen'),
        (commons_file('Theodore Roosevelt after he was shot 1912.jpg'), 'Public domain - pre-1931 publication'),
        (commons_file("Mercy Hospital - Roosevelt's rooms LCCN2014690905.jpg"), 'Public domain - Library of Congress'),
    ],
    'FERNANDA_MONTENEGRO': [
        ('https://commons.wikimedia.org/wiki/Special:Redirect/file/Campanha_pela_Mem%C3%B3ria_e_pela_Verdade_OAB_RJ_Fernanda_Montenegro.webm', 'Wikimedia Commons reviewed media'),
        (commons_file('BR RJANRIO PH 0 FOT 34783 020.jpg'), 'Public domain - Arquivo Nacional do Brasil'),
        (commons_file('A atriz Fernanda Montenegro em 2012.jpg'), 'CC BY 2.0 - André Luiz D. Takahashi'),
        (commons_file('Fernanda Montenegro2019.jpg'), 'CC BY 3.0 - VIVA / reviewed Commons source'),
    ],
    'MARISKA_LONGEVITY': [
        (commons_file('Mariska Hargitay Reads "Oh! The Places You\'ll Go!".webm'), 'Public domain - White House'),
        (commons_file('MariskaHargitay.jpg'), 'CC BY 2.0 - Veronica Romm'),
        (commons_file('Mariska Hargitay on set of SVU season 12.jpg'), 'CC BY-SA 2.0 - Lori_NY'),
        (commons_file('Mariska Hargitay 2025.jpg'), 'CC BY-SA 4.0 - Colleen Sturtevant'),
    ],
    'EMICIDA_INFLUENCE': [
        ('https://commons.wikimedia.org/wiki/Special:Redirect/file/Campus_Party-_Rapper_Emicida_x_Ecad.webm', 'CC BY 3.0 - EBC na Rede, reviewed'),
        (commons_file('Emicida.jpg'), 'CC BY 2.0 - Patricia Oliveira'),
        (commons_file('Emicida no Campus Party Brasil 2012.jpg'), 'CC BY-SA 2.0 - Campus Party Brasil'),
        (commons_file('Emicida en MICA 2023.jpg'), 'CC BY-SA 2.0 - Ministerio de Cultura de la Nación'),
    ],
}


base.HYBRID.update({'IBERE', 'FERNANDA_MONTENEGRO', 'MARISKA_LONGEVITY', 'EMICIDA_INFLUENCE'})
base.ANIM_MODE.update({
    'IBERE': 'influence',
    'FERNANDA_MONTENEGRO': 'credibility',
    'MARISKA_LONGEVITY': 'timeline',
    'EMICIDA_INFLUENCE': 'message',
})

base.BLOCK_LABELS['IBERE'] = [
    'Iberê explica uma ideia ao público',
    'seguidores não medem influência sozinhos',
    'demonstração torna a ideia concreta',
    'confiança cresce quando a explicação funciona',
    'o público acompanha o processo',
    'experiência vira memória e compartilhamento',
    'credibilidade faz a ideia continuar viajando',
]
base.BLOCK_LABELS['FERNANDA_MONTENEGRO'] = [
    'Fernanda constrói presença desde o teatro',
    'décadas acumulam repertório e reconhecimento',
    'carreira atravessa palco, cinema e televisão',
    'consistência transforma competência em confiança',
    'a presença pública continua reconhecível',
    'tempo reforça uma trajetória coerente',
    'longevidade vira parte da credibilidade',
]
base.BLOCK_LABELS['MARISKA_LONGEVITY'] = [
    'Mariska inicia uma longa trajetória pública',
    'os anos avançam sem congelar a personagem',
    'novas fases mantêm a presença reconhecível',
    'responsabilidades crescem com o tempo',
    'a carreira chega a uma nova fase',
    'familiaridade e renovação caminham juntas',
    'longevidade nasce de mudança com identidade',
]
base.BLOCK_LABELS['EMICIDA_INFLUENCE'] = [
    'Emicida constrói uma voz reconhecível',
    'popularidade e influência não são a mesma coisa',
    'música e narrativa carregam uma mensagem',
    'identidade conecta ideia, emoção e contexto',
    'a mensagem alcança públicos em novos momentos',
    'pessoas repetem e redistribuem a ideia',
    'atenção vira influência quando a mensagem continua',
]


def load_topics_v4():
    topics = _ORIGINAL_LOAD_TOPICS()
    for video_id, sources in SOURCE_OVERRIDES.items():
        topics[video_id]['sources'] = sources
    return topics


def _photo_documentary_clip(url: str, dest: pathlib.Path):
    parsed = urllib.parse.urlparse(url)
    suffix = pathlib.Path(urllib.parse.unquote(parsed.path)).suffix.lower()
    if suffix not in {'.jpg', '.jpeg', '.png', '.webp'}:
        suffix = '.jpg'
    raw = dest.with_suffix(suffix)
    base.run(['curl', '-L', '--fail', '--retry', '3', '--retry-delay', '2', '-A', 'Mozilla/5.0', url, '-o', str(raw)])
    if raw.stat().st_size < 8000:
        raise RuntimeError(f'ARCHIVAL_IMAGE_DOWNLOAD_TOO_SMALL {url}')

    # Documentary motion, not a static card or zoom: the photograph travels across
    # a fixed canvas while a timeline rail and evidence marker move independently.
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
        'ffmpeg', '-y', '-loglevel', 'error', '-loop', '1', '-i', str(raw),
        '-filter_complex', fc, '-map', '[v]', '-t', '24', '-an',
        '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', str(dest)
    ])
    raw.unlink(missing_ok=True)


def download_v4(url: str, dest: pathlib.Path):
    path = urllib.parse.unquote(urllib.parse.urlparse(url).path).lower()
    if path.endswith(('.jpg', '.jpeg', '.png', '.webp')):
        _photo_documentary_clip(url, dest)
        return
    _ORIGINAL_DOWNLOAD(url, dest)


def _header(im: Image.Image, label: str):
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 976, 76), fill=(5, 34, 70))
    d.text((28, 20), label, font=base.font(26), fill=base.WHITE)
    d.line((28, 72, 948, 72), fill=base.CYAN, width=2)
    return d


def narrative_anim_frame(mode: str, idx: int, p: float, label: str) -> Image.Image:
    if mode not in {'influence', 'credibility', 'timeline', 'message'}:
        return _ORIGINAL_ANIM_FRAME(mode, idx, p, label)

    im = Image.new('RGB', (976, 844), base.NAVY)
    d = _header(im, label)

    if mode == 'influence':
        cx, cy = 470, 420
        pulse = 36 + int(12 * math.sin(p * math.pi * 4) ** 2)
        d.ellipse((cx-pulse, cy-pulse, cx+pulse, cy+pulse), fill=base.GOLD, outline=base.WHITE, width=4)
        d.text((cx-47, cy-13), 'IDEIA', font=base.font(22), fill=base.NAVY)
        nodes = [(160,210),(300,175),(675,190),(805,275),(180,610),(330,690),(655,680),(810,565)]
        reach = min(1.0, p * 1.25)
        for j,(x,y) in enumerate(nodes):
            ex = cx + int((x-cx)*reach)
            ey = cy + int((y-cy)*reach)
            base.arrow(d, (cx,cy), (ex,ey), base.CYAN if j%2==0 else base.GOLD, 4)
            r = 15 + int(7*((p+j*.08)%1))
            d.ellipse((x-r,y-r,x+r,y+r), fill=(28,105,165), outline=base.WHITE, width=3)
        demo_x = 160 + int(560*p)
        d.rounded_rectangle((demo_x,760,demo_x+160,810),12,fill=(20,90,135),outline=base.GOLD,width=3)
        d.text((demo_x+18,771),'DEMO',font=base.font(20),fill=base.WHITE)

    elif mode == 'credibility':
        y = 450
        x0, x1 = 110, 860
        d.line((x0,y,x1,y), fill=(70,110,150), width=9)
        progress = x0 + int((x1-x0)*p)
        d.line((x0,y,progress,y), fill=base.GOLD, width=12)
        years = ['1967','1980','2000','2012','2019','2026']
        for j,year in enumerate(years):
            x = x0 + int((x1-x0)*j/(len(years)-1))
            active = p >= j/(len(years)-1)
            r = 17 if active else 11
            d.ellipse((x-r,y-r,x+r,y+r), fill=base.GOLD if active else (55,80,105), outline=base.WHITE, width=3)
            d.text((x-28,y+34),year,font=base.font(18),fill=base.WHITE)
        trust = int(620*p)
        d.rounded_rectangle((165,610,810,690),18,outline=base.CYAN,width=4)
        d.rounded_rectangle((177,622,177+trust,678),12,fill=(42,150,205))
        d.text((330,635),'CONFIANÇA',font=base.font(25),fill=base.WHITE)

    elif mode == 'timeline':
        d.line((110,610,860,610), fill=base.CYAN, width=8)
        years = [('1999',150),('2007',350),('2011',520),('2025',760)]
        for j,(year,x) in enumerate(years):
            on = p >= j/4
            lift = int(75*max(0,min(1,p*4-j)))
            d.line((x,610,x,500-lift), fill=base.GOLD if on else (70,90,115), width=5)
            d.ellipse((x-18,482-lift,x+18,518-lift), fill=base.GOLD if on else (65,85,110), outline=base.WHITE,width=3)
            d.text((x-28,645),year,font=base.font(20),fill=base.WHITE)
        level = int(4*p)
        for j,name in enumerate(['DETETIVE','REFERÊNCIA','LIDERANÇA','NOVA FASE']):
            yy=150+j*78
            active=j<=level
            d.rounded_rectangle((250,yy,730,yy+54),14,fill=(35,120,170) if active else (30,48,70),outline=base.GOLD if active else (80,100,120),width=3)
            d.text((355,yy+13),name,font=base.font(22),fill=base.WHITE)

    elif mode == 'message':
        cx, cy = 475, 405
        for r in [70,125,185,250]:
            rr = int(r*(0.35+0.65*p))
            d.ellipse((cx-rr,cy-rr,cx+rr,cy+rr), outline=base.CYAN if r%2 else base.GOLD, width=4)
        d.rounded_rectangle((350,350,600,455),24,fill=(35,92,135),outline=base.WHITE,width=4)
        d.text((385,382),'MENSAGEM',font=base.font(27),fill=base.WHITE)
        nodes=[(140,180),(810,190),(150,650),(820,650),(475,735)]
        for j,(x,y) in enumerate(nodes):
            q=max(0,min(1,(p-j*.07)*1.4))
            ex=cx+int((x-cx)*q); ey=cy+int((y-cy)*q)
            base.arrow(d,(cx,cy),(ex,ey),base.GOLD if j%2 else base.CYAN,4)
            d.ellipse((x-18,y-18,x+18,y+18),fill=(30,120,170),outline=base.WHITE,width=3)

    return im


def build_v4(topic, golden: pathlib.Path, outdir: pathlib.Path):
    video_id = topic['id']
    if video_id not in TARGETS:
        raise RuntimeError(f'V4_TARGET_NOT_ALLOWED {video_id}')
    _ORIGINAL_BUILD(topic, golden, outdir)

    receipt_path = outdir / f'{video_id}_VSA_VISUAL_RELEASE_RECEIPT_V1.json'
    receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
    receipt['repair_version'] = 'V4_TARGETED_NARRATIVE_DIVERSITY'
    receipt['prior_human_visual_block'] = True
    receipt['human_review']['approved'] = False
    receipt['release_eligible'] = False
    receipt['status'] = 'AWAITING_HUMAN_REVIEW_AFTER_TARGETED_REPAIR'
    for shot in receipt.get('shot_map', []):
        asset = shot.get('asset') or {}
        src = urllib.parse.unquote(str(asset.get('source_url','')).lower())
        if src.endswith(('.jpg','.jpeg','.png','.webp')):
            shot['media_type'] = 'ARCHIVAL_IMAGE_ANIMATED'
            shot['visual_role'] = 'ARCHIVAL_EVIDENCE'
            shot['archival_motion'] = 'PAN_PLUS_TIMELINE_MARKER_NO_STATIC_ZOOM'
            shot['reused_take_as_variety'] = False
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


base.load_topics = load_topics_v4
base.download = download_v4
base.anim_frame = narrative_anim_frame
base.build = build_v4

if __name__ == '__main__':
    base.main()
