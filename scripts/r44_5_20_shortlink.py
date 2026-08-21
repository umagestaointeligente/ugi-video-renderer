from pathlib import Path
import requests

TARGET='https://lola-operacional-ugi.umagestaointeligente.workers.dev/materiais'
ALIASES=['MateriaisUGI','UGIMateriais','Materiais_UGI']
OUT=Path('cloudflare/status/r44-5-20-shortlink.txt')
OUT.parent.mkdir(parents=True,exist_ok=True)
lines=['SHORTLINK_STAGE=CREATE','TARGET='+TARGET]
created=None
for alias in ALIASES:
    try:
        r=requests.get('https://is.gd/create.php',params={'format':'simple','url':TARGET,'shorturl':alias},timeout=20)
        body=r.text.strip()
        lines += [f'ALIAS_ATTEMPT={alias}',f'ALIAS_HTTP={r.status_code}',f'ALIAS_RESPONSE={body[:300]}']
        if r.status_code==200 and body.startswith('https://is.gd/'):
            created=body
            break
    except Exception as e:
        lines += [f'ALIAS_ERROR={alias}:{type(e).__name__}:{str(e)[:220]}']

if not created:
    raise SystemExit('No short link could be created')

# Validate short link redirects to the permanent UGI commerce hub.
r=requests.get(created,timeout=20,allow_redirects=False,headers={'User-Agent':'UGI-Shortlink-Smoke/1.0'})
loc=r.headers.get('location','')
lines += ['SHORT_URL='+created,f'SHORT_REDIRECT_HTTP={r.status_code}','SHORT_REDIRECT_LOCATION='+loc]
if r.status_code not in (301,302,303,307,308) or TARGET not in loc:
    raise SystemExit('Short link redirect validation failed')

# Validate destination page remains live.
p=requests.get(TARGET,timeout=20)
if p.status_code!=200 or 'Materiais práticos' not in p.text:
    raise SystemExit('Commerce hub target validation failed')
lines += ['TARGET_HTTP_200=true','SHORTLINK_READY=true','OK=true']
OUT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(created)
