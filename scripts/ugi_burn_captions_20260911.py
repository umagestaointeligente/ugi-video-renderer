from __future__ import annotations

import json,re,subprocess
from pathlib import Path

OUT=Path('public/ugi/editorial/2026-09-11')
TEXTS={
 'reel-faa-1015.mp4':'A FAA quer atacar atrasos de voo antes de eles virarem caos no aeroporto. O novo sistema SMART cruza programação das companhias, clima, capacidade dos aeroportos, espaço aéreo e outras restrições para antecipar gargalos. A ideia é coordenar mudanças antes da decolagem, em vez de reagir quando a fila já se formou. Isso parece aviação, mas é gestão operacional pura. Empresas normalmente descobrem seus gargalos olhando para o retrovisor: pedido atrasado, estoque rompido, fila crescendo. A lógica mais madura é transformar sinais antecipados em decisão. Prever não significa acertar tudo. Significa ganhar tempo para mudar rota antes que o custo do problema fique maior.',
 'tiktok-kojima-1130.mp4':'PHYSINT, o novo projeto de Hideo Kojima, mudou de parceiro. Depois do fim da parceria com a PlayStation, a Kojima Productions anunciou o Xbox como novo parceiro de publicação. O ponto de gestão não é transformar isso em briga de marcas. É observar o que acontece quando um projeto importante perde o patrocinador ou parceiro original. Um projeto bom não precisa morrer junto com a primeira relação. Primeiro você preserva o núcleo de valor. Depois separa o que dependia do parceiro antigo. E então procura um novo encaixe capaz de financiar, distribuir ou acelerar a proposta. Resiliência estratégica também é saber trocar a rota sem abandonar o destino.',
 'tiktok-primark-1945.mp4':'A Primark passou anos resistindo à entrega em casa. A lógica fazia sentido para um varejista de preço baixo: proteger margem, gerar tráfego na loja e evitar o custo caro da última milha. Agora a empresa decidiu lançar home delivery no Reino Unido e comprou um centro automatizado de noventa milhões de libras. O aprendizado não é que a estratégia antiga estava errada. É que uma boa estratégia pode perder validade quando tecnologia, comportamento do cliente e economia do canal mudam. Apego ao modelo que funcionou ontem pode virar custo amanhã. Estratégia madura não é defender uma escolha para sempre. É saber qual evidência justifica mudar.'
}

def duration(path):
    j=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','json',str(path)],text=True)); return float(j['format']['duration'])

def chunks(text):
    sentences=[x.strip() for x in re.split(r'(?<=[.!?])\s+',text.strip()) if x.strip()]; out=[]
    for s in sentences:
        words=s.split()
        if len(words)<=12: out.append(s)
        else:
            cut=max(6,len(words)//2); out.extend([' '.join(words[:cut]),' '.join(words[cut:])])
    return out

def ts(sec):
    h=int(sec//3600); sec-=h*3600; m=int(sec//60); sec-=m*60; s=int(sec); ms=int(round((sec-s)*1000));
    if ms>=1000: s+=1; ms-=1000
    return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'

def make_srt(text,dur,path):
    parts=chunks(text); weights=[max(1,len(x.split())) for x in parts]; total=sum(weights); cur=0.; lines=[]
    for i,(part,w) in enumerate(zip(parts,weights),1):
        end=min(dur,cur+dur*w/total); lines += [str(i),f'{ts(cur)} --> {ts(end)}',part,'']; cur=end
    path.write_text('\n'.join(lines),encoding='utf-8')

def burn(name,text):
    src=OUT/name
    if not src.exists(): raise SystemExit(f'MISSING:{src}')
    dur=duration(src); srt=OUT/(src.stem+'.srt'); make_srt(text,dur,srt); tmp=OUT/(src.stem+'.captioned.mp4')
    style='FontName=DejaVu Sans,FontSize=16,PrimaryColour=&H00FFFFFF,OutlineColour=&HCC000000,BorderStyle=3,Outline=1,Shadow=0,Alignment=2,MarginV=170'
    subprocess.run(['ffmpeg','-y','-i',str(src),'-vf',f"subtitles={srt.as_posix()}:force_style='{style}'",'-c:v','libx264','-preset','medium','-crf','19','-c:a','copy','-movflags','+faststart',str(tmp)],check=True)
    tmp.replace(src); print(f'CAPTION_PASS {name} duration={dur:.2f}s cues={len(chunks(text))}')

def main():
    for n,t in TEXTS.items(): burn(n,t)

if __name__=='__main__': main()
