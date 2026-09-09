from __future__ import annotations

import hashlib
import json
import math
import random
import struct
import subprocess
import time
import wave
from pathlib import Path
from urllib.parse import quote

import requests
from PIL import Image, ImageDraw, ImageEnhance, ImageFont

OUT = Path('public/ugi/editorial/2026-09-09')
SRC = OUT / 'sources'
OUT.mkdir(parents=True, exist_ok=True)
SRC.mkdir(parents=True, exist_ok=True)
UA = {'User-Agent': 'UGI-Editorial/1.1 (contact: umagestaointeligente@gmail.com)'}

SOURCES = {
    'apple': {
        'filename': 'Apple Park - October 2018 - 8809.jpg',
        'width': 3840,
        'license': 'CC BY-SA 4.0',
        'author': 'Gregory Varnum',
        'page': 'https://commons.wikimedia.org/wiki/File:Apple_Park_-_October_2018_-_8809.jpg',
    },
    'qualcomm': {
        'filename': 'Qualcomm headquarters.jpg',
        'width': 2930,
        'license': 'CC BY-SA 3.0 / GFDL',
        'author': 'Coolcaesar',
        'page': 'https://commons.wikimedia.org/wiki/File:Qualcomm_headquarters.jpg',
    },
    'datacenter_inside': {
        'filename': 'Hardware interno de servidor data center HostDime.jpg',
        'width': 3840,
        'license': 'CC BY 4.0',
        'author': 'EditorTech20',
        'page': 'https://commons.wikimedia.org/wiki/File:Hardware_interno_de_servidor_data_center_HostDime.jpg',
    },
    'datacenter_energy': {
        'filename': 'Sala de energia Data Center HostDime Brasil.jpg',
        'width': 1920,
        'license': 'CC BY 4.0',
        'author': 'EditorTech20',
        'page': 'https://commons.wikimedia.org/wiki/File:Sala_de_energia_Data_Center_HostDime_Brasil.jpg',
    },
    'mistral': {
        'filename': 'Prime Minister of Bharat, Shri Narendra Damodardas Modi with the Co-Founder and CEO of Mistral AI, Mr. Arthur Mensch.jpg',
        'width': 2200,
        'license': 'GODL-India',
        'author': "Prime Minister's Office (India) / Press Information Bureau",
        'page': 'https://commons.wikimedia.org/wiki/File:Prime_Minister_of_Bharat,_Shri_Narendra_Damodardas_Modi_with_the_Co-Founder_and_CEO_of_Mistral_AI,_Mr._Arthur_Mensch.jpg',
    },
}


def commons_url(spec):
    return 'https://commons.wikimedia.org/wiki/Special:Redirect/file/' + quote(spec['filename'], safe='') + f"?width={spec['width']}"


def download(key):
    spec = SOURCES[key]
    p = SRC / spec['filename']
    if p.exists() and p.stat().st_size > 100_000:
        return p
    url = commons_url(spec)
    for attempt in range(2):
        r = requests.get(url, headers=UA, timeout=90, allow_redirects=True)
        if r.status_code == 429 and attempt == 0:
            retry_after = r.headers.get('Retry-After')
            delay = min(30, max(12, int(retry_after) if retry_after and retry_after.isdigit() else 12))
            print(f'{key}: HTTP 429; respecting cooldown for {delay}s before one recovery attempt')
            time.sleep(delay)
            continue
        r.raise_for_status()
        if 'image' not in r.headers.get('content-type', ''):
            raise RuntimeError(f"{key}: invalid content type {r.headers.get('content-type')}")
        p.write_bytes(r.content)
        if p.stat().st_size < 100_000:
            raise RuntimeError(f'{key}: source below 100KB')
        print(f'{key}: downloaded {p.stat().st_size} bytes from {r.url}')
        time.sleep(2.5)
        return p
    raise RuntimeError(f'{key}: rate-limit recovery exhausted')


def fnt(size, bold=False):
    name = 'DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'
    return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/' + name, size)


def cover(src, target):
    src = src.convert('RGB')
    tw, th = target
    iw, ih = src.size
    scale = max(tw / iw, th / ih)
    if scale > 1.0:
        raise RuntimeError(f'upscale forbidden: {iw}x{ih} -> {tw}x{th}')
    nw, nh = round(iw * scale), round(ih * scale)
    src = src.resize((nw, nh), Image.Resampling.LANCZOS)
    x = (nw - tw) // 2
    y = (nh - th) // 2
    return src.crop((x, y, x + tw, y + th))


def gradient(img):
    w, h = img.size
    alpha = Image.new('L', (1, h))
    ap = alpha.load()
    for y in range(h):
        t = max(0.0, min(1.0, (y / h - 0.45) / 0.48))
        ap[0, y] = int(200 * t * t)
    alpha = alpha.resize((w, h))
    ov = Image.new('RGBA', (w, h), (0, 0, 0, 255))
    ov.putalpha(alpha)
    return Image.alpha_composite(img.convert('RGBA'), ov).convert('RGB')


def wrap(draw, text, font, maxw):
    words = text.split()
    lines, cur = [], ''
    for word in words:
        trial = word if not cur else cur + ' ' + word
        box = draw.textbbox((0, 0), trial, font=font)
        if box[2] - box[0] <= maxw:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def render(key, name, size, headline, sub):
    spec = SOURCES[key]
    img = cover(Image.open(download(key)), size)
    img = ImageEnhance.Contrast(img).enhance(1.04)
    img = ImageEnhance.Color(img).enhance(0.96)
    img = gradient(img)
    d = ImageDraw.Draw(img)
    w, h = size
    m = int(w * 0.07)
    maxw = w - 2 * m
    hf = fnt(70 if h >= 1500 else 48, True)
    sf = fnt(35 if h >= 1500 else 27)
    bf = fnt(23 if h >= 1500 else 18, True)
    cf = fnt(16 if h >= 1500 else 13)
    hl = wrap(d, headline, hf, maxw)
    sl = wrap(d, sub, sf, maxw)
    lh = int(hf.size * 1.16)
    sh = int(sf.size * 1.32)
    total = len(hl) * lh + 20 + len(sl) * sh
    y = h - int(h * 0.1) - total - 80
    for line in hl:
        d.text((m + 2, y + 3), line, font=hf, fill='black')
        d.text((m, y), line, font=hf, fill='white')
        y += lh
    y += 16
    for line in sl:
        d.text((m + 1, y + 2), line, font=sf, fill='black')
        d.text((m, y), line, font=sf, fill=(240, 240, 240))
        y += sh
    d.text((m, h - 65), 'UGI • Uma Gestão Inteligente', font=bf, fill='white')
    credit = f"Imagem: {spec['author']} • {spec['license']}"
    cb = d.textbbox((0, 0), credit, font=cf)
    d.text((w - m - (cb[2]-cb[0]), h - 56), credit, font=cf, fill=(210, 210, 210))
    out = OUT / name
    img.save(out, 'JPEG', quality=94, subsampling=0, optimize=True)
    if out.stat().st_size < 120_000:
        raise RuntimeError(f'{name}: final JPEG unexpectedly small')
    return out


def music(path, seconds=8.0, sr=48000):
    chords = [[130.81,164.81,196.0,261.63],[110.0,130.81,164.81,220.0],[87.31,130.81,174.61,261.63],[98.0,146.83,196.0,293.66]]
    rng = random.Random(20260909)
    with wave.open(str(path), 'w') as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(sr)
        for i in range(int(seconds*sr)):
            t = i/sr; local=t%2.0; ch=chords[int(t//2)%4]; freq=ch[int(local/0.25)%4]
            env=math.exp(-3.2*(local%0.25)); v=0.13*env*math.sin(2*math.pi*freq*t)
            v += sum(0.024*math.sin(2*math.pi*f*t) for f in ch)
            beat=t%0.5
            if beat<0.08: v += 0.09*math.exp(-35*beat)*math.sin(2*math.pi*68*t)
            off=(t+0.25)%0.5
            if off<0.025: v += 0.014*math.exp(-90*off)*(rng.random()*2-1)
            fade=max(0.0,min(1.0,t/0.35,(seconds-t)/0.45)); v=max(-0.8,min(0.8,v*fade))
            s=int(v*32767); wf.writeframesraw(struct.pack('<hh',s,s))


def mp4(jpg, name):
    wav = OUT / 'ugi-original-story-bed.wav'
    if not wav.exists(): music(wav)
    out=OUT/name
    subprocess.run(['ffmpeg','-y','-loop','1','-framerate','30','-i',str(jpg),'-i',str(wav),'-t','8','-c:v','libx264','-profile:v','high','-level','4.1','-pix_fmt','yuv420p','-r','30','-c:a','aac','-b:a','160k','-ar','48000','-movflags','+faststart','-shortest',str(out)],check=True)
    if out.stat().st_size<300_000: raise RuntimeError(f'{name}: MP4 unexpectedly small')
    return out


def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for c in iter(lambda:f.read(1024*1024),b''): h.update(c)
    return h.hexdigest()


def main():
    # Fetch deliberately before rendering so Wikimedia requests are spaced and auditable.
    for key in SOURCES: download(key)

    a1=render('apple','story-apple-0900.jpg',(1080,1920),'Hoje a Apple enfrenta um teste de execução.','Hardware, IA e liderança sob expectativa.')
    a2=render('apple','story-apple-0907.jpg',(1080,1920),'Liderança herda mais do que uma marca.','Herda expectativas — e precisa transformá-las em entrega.')
    mp4(a1,'story-apple-0900.mp4'); mp4(a2,'story-apple-0907.mp4')

    render('qualcomm','feed-qualcomm-amazon-1230.jpg',(1080,1350),'Qualcomm + Amazon: até US$ 60 bi em infraestrutura de IA','O movimento é sobre diversificação — não apenas chips.')
    render('datacenter_inside','linkedin-digital-resilience-1400.jpg',(1200,627),'Seu negócio sobreviveria sem um fornecedor crítico?','Infraestrutura digital virou risco de gestão.')

    d1=render('datacenter_energy','story-resilience-1800.jpg',(1080,1920),'Dependência tecnológica virou risco de gestão.','Cloud, dados e IA também exigem plano de continuidade.')
    d2=render('datacenter_inside','story-resilience-1812.jpg',(1080,1920),'Eficiência busca o melhor caminho.','Resiliência garante um segundo caminho quando o primeiro falha.')
    mp4(d1,'story-resilience-1800.mp4'); mp4(d2,'story-resilience-1812.mp4')

    render('mistral','feed-mistral-1915.jpg',(1080,1350),'Mistral AI chega a cerca de US$ 24 bi em valuation','Em IA, posicionamento estratégico também vira valor.')

    finals=[p for p in OUT.iterdir() if p.is_file() and p.suffix.lower() in {'.jpg','.mp4'}]
    manifest={'schema':'UGI_EDITORIAL_ASSET_PROVENANCE_V1','date':'2026-09-09','state':'FINAL_ASSETS_BUILT_PENDING_EXACT_PREVIEW_APPROVAL','rules':{'ai_generated_subject_substitution':False,'upscale_low_resolution':False,'rights_manifest_required':True,'story_music':'original UGI four-chord instrumental baked into MP4','preview_must_match_publish_media':True},'sources':SOURCES,'finals':[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(finals)]}
    (OUT/'asset-provenance.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(manifest,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
