from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import math, subprocess

OUT=Path('public/ugi/editorial/2026-09-07')
OUT.mkdir(parents=True,exist_ok=True)
FB='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FR='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

def F(n,b=False): return ImageFont.truetype(FB if b else FR,n)
def bg(size,a,b):
    im=Image.new('RGB',size); d=ImageDraw.Draw(im); w,h=size
    for y in range(h):
        t=y/(h-1); c=tuple(int(a[i]*(1-t)+b[i]*t) for i in range(3)); d.line((0,y,w,y),fill=c)
    return im

def wrap(d,text,ff,mw):
    out=[]; line=''
    for word in text.split():
        test=(line+' '+word).strip()
        if d.textbbox((0,0),test,font=ff)[2] <= mw: line=test
        else:
            if line: out.append(line)
            line=word
    if line: out.append(line)
    return out

def block(d,text,x,y,mw,sz,bold=False,fill=(255,255,255),spacing=9):
    ff=F(sz,bold)
    for line in wrap(d,text,ff,mw):
        d.text((x,y),line,font=ff,fill=fill); y += d.textbbox((0,0),line,font=ff)[3]+spacing
    return y

def icon(d,k,cx,cy,a):
    if k=='bag':
        d.rounded_rectangle((cx-90,cy-60,cx+90,cy+110),25,fill='white'); d.arc((cx-50,cy-115,cx+50,cy-15),200,340,fill=a,width=10); d.line((cx-45,cy+20,cx+45,cy+20),fill=a,width=10)
    elif k=='chat':
        d.rounded_rectangle((cx-110,cy-70,cx+110,cy+70),25,fill='white'); d.polygon([(cx-50,cy+70),(cx-10,cy+70),(cx-30,cy+105)],fill='white'); d.line((cx-55,cy-10,cx-35,cy+45,cx+45,cy+45),fill=a,width=9); d.line((cx-35,cy,cx+50,cy),fill=a,width=7)
    elif k=='gauge':
        d.arc((cx-100,cy-100,cx+100,cy+100),200,340,fill='white',width=16); r=math.radians(305); d.line((cx,cy,cx+70*math.cos(r),cy+70*math.sin(r)),fill=a,width=9); d.ellipse((cx-10,cy-10,cx+10,cy+10),fill=a)
    elif k=='shield':
        d.polygon([(cx,cy-110),(cx+90,cy-65),(cx+70,cy+50),(cx,cy+110),(cx-70,cy+50),(cx-90,cy-65)],fill='white'); d.polygon([(cx,cy-35),(cx+35,cy),(cx,cy+35),(cx-35,cy)],fill=a)

def card(name,size,title,subtitle,stat,kind,kicker,colors,source=''):
    im=bg(size,*colors); d=ImageDraw.Draw(im); w,h=size
    d.rounded_rectangle((55,55,w-55,h-55),35,fill=(10,15,28),outline=(255,255,255),width=2)
    ac={'bag':(255,76,130),'chat':(70,225,180),'gauge':(0,205,255),'shield':(50,225,185)}[kind]
    d.ellipse((w-390,85,w-90,385),fill=tuple(int(x*.65) for x in ac)); icon(d,kind,w-240,235,ac)
    d.rounded_rectangle((85,100,520,160),18,fill=ac); d.text((110,116),kicker,font=F(23,True),fill=(10,15,28))
    y=220; y=block(d,title,85,y,w-170,56,True); y += 28
    if stat: d.text((85,y),stat,font=F(62,True),fill=ac); y += 88
    y=block(d,subtitle,85,y,w-170,31,False,(235,240,245))
    if source: d.text((85,h-145),source,font=F(17),fill=(165,177,193))
    d.text((70,h-95),'UGI',font=F(28,True),fill='white'); d.text((145,h-91),'Uma Gestão Inteligente',font=F(18),fill=(220,225,235))
    p=OUT/name; im.save(p,'JPEG',quality=94,optimize=True,subsampling=0); return p

chat_src='Fonte: Similarweb via EXAME • 06/09/2026'
tik_src='Fonte: TikTok / Mercado&Consumo • 06/09/2026'
roi_src='Fonte: Strand Partners/AWS via Folha • 05/09/2026'
pix_src='Fonte: UOL Economia • 02/09/2026'

card('ig-chatgpt-ads.jpg',(1080,1350),'A NOVA PRATELEIRA DO VAREJO ESTÁ DENTRO DA IA','Casas Bahia e Magazine Luiza já aparecem na corrida por anúncios dentro do ChatGPT. Para marcas, a disputa começa antes do clique.','330x','chat','VAREJO + IA',((12,18,32),(20,90,76)),chat_src)
card('ig-tiktok-shop.jpg',(1080,1350),'TIKTOK SHOP: QUANDO ENTRETENIMENTO VIRA CHECKOUT','Moda e beleza aceleram no Brasil. O consumidor descobre, considera e compra no mesmo ambiente.','+154% MODA','bag','SOCIAL COMMERCE',((20,14,31),(86,27,83)),tik_src)
card('linkedin-ai-roi.jpg',(1200,627),'IA SEM MÉTRICA É CUSTO. IA COM MÉTRICA VIRA GESTÃO.','Só 33% das empresas brasileiras dizem medir o ROI de IA com confiança. O próximo salto é provar valor.','33%','gauge','GESTÃO + IA',((12,20,33),(14,66,92)),roi_src)

stories=[
('story-01-chatgpt.jpg','A VITRINE MUDOU DE LUGAR.','Anúncios dentro do ChatGPT já começam a mudar a jornada de descoberta de produtos no Brasil.','330x','chat','08:15 • VAREJO + IA',chat_src),
('story-02-enquete-ia.jpg','VOCÊ COMPRARIA UM PRODUTO RECOMENDADO POR UMA IA?','SIM / AINDA NÃO',None,'chat','08:17 • ENQUETE',''),
('story-03-tiktok-shop.jpg','TIKTOK SHOP VIROU CANAL DE VENDA — NÃO SÓ MÍDIA.','Moda cresceu 154% e beleza 151% no 1º semestre de 2026 versus o semestre anterior.','+154% MODA','bag','11:30 • SOCIAL COMMERCE',tik_src),
('story-04-tiktok-insight.jpg','QUANDO CONTEÚDO E CHECKOUT VIRAM A MESMA EXPERIÊNCIA...','quem trata social apenas como mídia está olhando metade do negócio.',None,'bag','11:32 • INSIGHT UGI',''),
('story-05-roi.jpg','SUA EMPRESA USA IA. MAS SABE QUANTO ELA GERA?','Apenas 33% das empresas dizem medir com confiança o retorno de IA.','33%','gauge','15:00 • GESTÃO + IA',roi_src),
('story-06-enquete-roi.jpg','HOJE SUA EMPRESA MEDE ROI DE IA?','SIM / NÃO',None,'gauge','15:02 • ENQUETE',''),
('story-07-pix.jpg','IA JÁ ENTROU NO FLUXO FINANCEIRO.','Assistentes que executam Pix e pagamentos elevam a exigência de segurança, contingência e governança.',None,'shield','20:15 • TECNOLOGIA + RISCO',pix_src),
]
for s in stories: card(s[0],(1080,1920),*s[1:6],((13,18,32),(23,61,96)) if s[4] != 'bag' else ((24,14,35),(90,31,80)),s[6])

# Native 9:16 motion cards; no stretching/cropping of source images.
reel1=[
card('tmp-chat-1.jpg',(1080,1920),'A VITRINE DO VAREJO MUDOU DE LUGAR.','A descoberta de produtos começa a acontecer dentro de conversas com IA.',None,'chat','UGI • VAREJO + IA',((12,18,32),(20,90,76)),chat_src),
card('tmp-chat-2.jpg',(1080,1920),'O BRASIL ENTROU RÁPIDO NESSA CORRIDA.','Em três semanas, respostas do ChatGPT com publicidade no país passaram de pouco mais de 80 para mais de 27,7 mil.','330x','chat','DADO',((12,18,32),(20,90,76)),chat_src),
card('tmp-chat-3.jpg',(1080,1920),'A PERGUNTA DE GESTÃO MUDOU.','Sua marca está preparada para ser descoberta e escolhida dentro de uma resposta de IA?',None,'chat','INSIGHT UGI',((12,18,32),(20,90,76)),'')]
reel2=[
card('tmp-roi-1.jpg',(1080,1920),'USAR IA NÃO É O MESMO QUE GERAR VALOR.','Metade das empresas brasileiras já usa IA, mas medir retorno ainda é um gargalo.',None,'gauge','UGI • GESTÃO + IA',((12,20,33),(14,66,92)),roi_src),
card('tmp-roi-2.jpg',(1080,1920),'SÓ 33% DIZEM MEDIR O ROI COM CONFIANÇA.','Sem métrica, produtividade percebida pode não virar resultado comprovado.','33%','gauge','DADO',((12,20,33),(14,66,92)),roi_src),
card('tmp-roi-3.jpg',(1080,1920),'O PRÓXIMO SALTO É GOVERNANÇA.','Menos ferramentas soltas. Mais processo, dono, métrica e decisão.',None,'gauge','INSIGHT UGI',((12,20,33),(14,66,92)),'')]

def video(name,frames):
    lst=OUT/(name+'.txt')
    with open(lst,'w') as f:
        for p in frames:
            f.write("file '"+p.name+"'\nduration 5\n")
        f.write("file '"+frames[-1].name+"'\n")
    subprocess.run(['ffmpeg','-y','-f','concat','-safe','0','-i',str(lst),'-vf','fps=30,format=yuv420p','-c:v','libx264','-preset','medium','-crf','19','-movflags','+faststart',str(OUT/(name+'.mp4'))],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    lst.unlink()
video('reel-chatgpt-ads',reel1); video('tiktok-ai-roi',reel2)
for p in OUT.glob('tmp-*.jpg'): p.unlink()

# QA: exact target geometry, minimum byte size, no accidental low-res intermediates.
expected={'ig-chatgpt-ads.jpg':(1080,1350),'ig-tiktok-shop.jpg':(1080,1350),'linkedin-ai-roi.jpg':(1200,627)}
for i in range(1,8):
    n=list(sorted(OUT.glob(f'story-0{i}-*.jpg')))[0].name; expected[n]=(1080,1920)
for n,wh in expected.items():
    p=OUT/n
    with Image.open(p) as im: assert im.size==wh, (n,im.size,wh)
    assert p.stat().st_size > 70000, (n,p.stat().st_size)
for n in ['reel-chatgpt-ads.mp4','tiktok-ai-roi.mp4']:
    p=OUT/n; assert p.stat().st_size > 100000, (n,p.stat().st_size)
print('UGI_20260907_MEDIA_QA=PASS')
