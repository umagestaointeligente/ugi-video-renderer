from __future__ import annotations

import json, re, subprocess
from pathlib import Path

OUT=Path('public/ugi/editorial/2026-09-10')

TEXTS={
 'reel-kpop-1015.mp4': 'Pela primeira vez em 41 anos, o Rock in Rio terá um dia inteiro dedicado ao K-pop no Palco Mundo. NEXZ, Hwasa e Stray Kids ocupam a programação de sexta-feira, e a data já está esgotada. Até os lightsticks, parte importante da cultura dos fãs de K-pop, foram incorporados à experiência do festival. Isso mostra uma mudança maior do que o line-up. Um nicho deixa de ser nicho quando ganha comunidade organizada, capacidade de mobilização e disposição para pagar por uma experiência própria. Para gestão, a lição é simples: novos mercados raramente aparecem do nada. Eles crescem primeiro nas bordas, criam linguagem, comportamento e comunidade, e só depois obrigam as grandes marcas a redesenhar produto, experiência e comunicação. Quem percebe cedo está aprendendo a reconhecer demanda antes que ela vire consenso.',
 'tiktok-lockedin-1130.mp4': 'O TikTok colocou o locked in entre os sinais culturais de 2026. A lógica é simples: pessoas assumem um compromisso em público, mostram o processo e usam a comunidade como cobrança e motivação. Mas no trabalho existe uma diferença importante. Foco não é encher a agenda, responder tudo rápido ou passar o dia em reunião. Foco é escolher o que merece energia e conseguir provar avanço. Se você terminou o dia cansado, mas não consegue dizer qual resultado moveu, talvez você não estivesse focado. Talvez estivesse só ocupado. A pergunta útil para amanhã é: qual entrega, se avançar de verdade, muda o seu resultado? Comece por ela.',
 'tiktok-essilor-1945.mp4': 'A EssilorLuxottica, dona da Ray-Ban, virou um caso interessante de governança. Leonardo Maria Del Vecchio, filho do fundador, criticou publicamente a liderança e pediu mais transparência e mudanças estratégicas. O conselho respondeu de forma unânime: reafirmou confiança no CEO Francesco Milleri e na direção da empresa. O ponto aqui não é escolher um lado. É entender que família, propriedade, conselho e gestão são papéis diferentes. Ter sobrenome, participação econômica ou legado não significa controlar sozinho a decisão executiva. E um conselho que existe só para concordar também não cumpre seu papel. Governança funciona quando as regras de poder estão claras antes do conflito. Porque, quando a crise chega, descobrir quem decide já é tarde demais.'
}

def duration(path: Path) -> float:
    raw=subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','json',str(path)],text=True)
    return float(json.loads(raw)['format']['duration'])

def chunks(text: str) -> list[str]:
    s=[x.strip() for x in re.split(r'(?<=[.!?])\s+',text.strip()) if x.strip()]
    out=[]
    for sentence in s:
        words=sentence.split()
        if len(words)<=13:
            out.append(sentence); continue
        cut=max(7,len(words)//2)
        out.append(' '.join(words[:cut])); out.append(' '.join(words[cut:]))
    return out

def ts(sec: float) -> str:
    sec=max(0.0,sec); h=int(sec//3600); sec-=h*3600; m=int(sec//60); sec-=m*60; s=int(sec); ms=int(round((sec-s)*1000))
    if ms>=1000: s+=1; ms-=1000
    return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'

def make_srt(text: str, dur: float, path: Path):
    parts=chunks(text); weights=[max(1,len(p.split())) for p in parts]; total=sum(weights); cur=0.0; lines=[]
    for i,(part,w) in enumerate(zip(parts,weights),1):
        span=dur*w/total; end=min(dur,cur+span)
        lines += [str(i), f'{ts(cur)} --> {ts(end)}', part, '']
        cur=end
    path.write_text('\n'.join(lines),encoding='utf-8')

def burn(name: str,text: str):
    src=OUT/name
    if not src.exists(): raise SystemExit(f'MISSING_VIDEO:{src}')
    dur=duration(src); srt=OUT/(src.stem+'.srt'); make_srt(text,dur,srt)
    tmp=OUT/(src.stem+'.captioned.mp4')
    style='FontName=DejaVu Sans,FontSize=16,PrimaryColour=&H00FFFFFF,OutlineColour=&HCC000000,BorderStyle=3,Outline=1,Shadow=0,Alignment=2,MarginV=170'
    filt=f"subtitles={srt.as_posix()}:force_style='{style}'"
    subprocess.run(['ffmpeg','-y','-i',str(src),'-vf',filt,'-c:v','libx264','-preset','medium','-crf','19','-c:a','copy','-movflags','+faststart',str(tmp)],check=True)
    tmp.replace(src)
    print(f'CAPTION_PASS {name} duration={dur:.2f}s cues={len(chunks(text))}')

def main():
    for name,text in TEXTS.items(): burn(name,text)

if __name__=='__main__': main()
