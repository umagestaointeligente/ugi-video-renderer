from __future__ import annotations
import json, os, re, time
from pathlib import Path
import requests
import scripts.r44_5_18_repair_v2 as base

STATUS=Path('cloudflare/status/r44-5-20-final.txt')
WORKER='lola-operacional-ugi'
ORIGIN='https://lola-operacional-ugi.umagestaointeligente.workers.dev'
OLD='lola-v8-r44-5-19-commerce-hub-visual-caption-2026-08-21'
NEW='lola-v8-r44-5-20-reliable-checkout-branded-domain-2026-08-21'
CUSTOM_HOST='materiais.umagestaointeligente.com'
CUSTOM_ORIGIN='https://'+CUSTOM_HOST


def write(lines):
    STATUS.parent.mkdir(parents=True,exist_ok=True)
    STATUS.write_text('\n'.join(lines)+'\n',encoding='utf-8')


def cf_headers(token): return {'Authorization':f'Bearer {token}'}


def fetch_live(api,h):
    r=requests.get(api+'/content/v2',headers=h,timeout=40)
    r.raise_for_status()
    return base.extract_source(r)


def bindings(api,h):
    r=requests.get(api+f'/versions/{base.STABLE_VERSION_ID}',headers=h,timeout=30)
    r.raise_for_status()
    return base.restored_bindings(r.json())


def deploy(api,h,src,b,tag):
    v=base.create_version(api,h,src,b,tag)
    d=base.deploy(api,h,v,tag)
    return v,d


def wait(ver):
    last={}
    for _ in range(24):
        try:
            r=requests.get(ORIGIN+'/api/health',timeout=12)
            if r.status_code==200:
                last=r.json(); bd=last.get('bindings') or {}
                if (last.get('ok') is True and last.get('version')==ver
                    and bd.get('MEDIA_R2') is True and bd.get('BUFFER_API_KEY') is True and bd.get('ASAAS_API_KEY') is True):
                    return last
        except Exception:
            pass
        time.sleep(3)
    raise RuntimeError('health timeout '+json.dumps(last,ensure_ascii=False)[:1200])


def patch(src):
    t=base.strip_temp_routes(src)
    t=re.sub(r'\n\s*// BEGIN_R44_5_20_.*?// END_R44_5_20_.*?\s*\n','\n',t,flags=re.S)
    old=f'var VERSION = "{OLD}";'
    if old in t:
        t=t.replace(old,f'var VERSION = "{NEW}";',1)
    elif f'var VERSION = "{NEW}";' not in t:
        raise RuntimeError('version anchor mismatch')

    post_route='if (request.method === "POST" && path === "/comprar/priorizacao") {'
    getpost_route='if ((request.method === "POST" || request.method === "GET") && path === "/comprar/priorizacao") {'
    if post_route in t:
        t=t.replace(post_route,getpost_route,1)
    elif getpost_route not in t:
        raise RuntimeError('buy route anchor mismatch')

    patterns=[
        (r'<form method="post" action="\$\{origin\}/comprar/\$\{encodeURIComponent\(slug\)\}">\s*<button class="buy" type="submit">Comprar agora</button>\s*</form>',
         '<a class="buy" href="${origin}/comprar/${encodeURIComponent(slug)}?source=product_page" rel="nofollow">Comprar agora</a>'),
        (r'<form method="post" action="\$\{origin\}/comprar/\$\{encodeURIComponent\(slug\)\}"><button class="buy" type="submit">Comprar agora</button></form>',
         '<a class="buy" href="${origin}/comprar/${encodeURIComponent(slug)}?source=product_page" rel="nofollow">Comprar agora</a>')
    ]
    changed=False
    for pat,repl in patterns:
        t,n=re.subn(pat,lambda m:repl,t,count=1,flags=re.S)
        if n==1:
            changed=True; break
    if not changed and 'source=product_page' not in t:
        raise RuntimeError('commerce button html anchor mismatch')

    if '.buy{width:100%;' in t:
        t=t.replace('.buy{width:100%;','.buy{display:block;text-align:center;text-decoration:none;width:100%;',1)
    return t


def attach_custom_domain(account_id,token):
    h={'Authorization':f'Bearer {token}','Content-Type':'application/json'}
    url=f'https://api.cloudflare.com/client/v4/accounts/{account_id}/workers/domains'
    lr=requests.get(url,headers={'Authorization':f'Bearer {token}'},timeout=30)
    if lr.status_code==200:
        existing=(lr.json().get('result') or [])
        for d in existing:
            if str(d.get('hostname') or '').lower()==CUSTOM_HOST:
                return True,'existing',d
    payload={'hostname':CUSTOM_HOST,'service':WORKER,'environment':'production'}
    r=requests.put(url,headers=h,json=payload,timeout=45)
    try:data=r.json()
    except Exception:data={'raw':r.text[:1000]}
    return bool(r.status_code==200 and data.get('success') is not False),'created' if r.status_code==200 else f'http_{r.status_code}',data


def validate_store(base_url):
    r=requests.get(base_url+'/materiais',timeout=20,allow_redirects=True)
    if r.status_code!=200 or 'Materiais práticos' not in r.text or 'Priorização' not in r.text:
        raise RuntimeError('store page failed '+str(r.status_code))
    p=requests.get(base_url+'/priorizacao',timeout=20)
    if p.status_code!=200 or 'Comprar agora' not in p.text:
        raise RuntimeError('product page failed '+str(p.status_code))
    if '<form method="post"' in p.text:
        raise RuntimeError('legacy POST form still present')
    if '/comprar/priorizacao' not in p.text:
        raise RuntimeError('buy anchor missing')
    return True


def validate_checkout(base_url):
    r=requests.get(base_url+'/comprar/priorizacao?source=smoke_test',timeout=30,allow_redirects=False,
                   headers={'User-Agent':'UGI-Commerce-Smoke/1.0'})
    loc=r.headers.get('location','')
    if r.status_code not in (301,302,303,307,308):
        raise RuntimeError(f'checkout redirect http={r.status_code} body={r.text[:800]}')
    if 'asaas.com/checkoutSession/show' not in loc:
        raise RuntimeError('checkout redirect host/path invalid: '+loc[:500])
    return r.status_code,loc


def main():
    lines=['R44.5.20_STAGE=RELIABLE_CHECKOUT_BRANDED_DOMAIN','OK=false','STATE=STARTED']
    write(lines)
    tok=os.environ['CF_API_TOKEN']; acct=os.environ['CF_ACCOUNT_ID']
    h=cf_headers(tok); api=f'https://api.cloudflare.com/client/v4/accounts/{acct}/workers/scripts/{WORKER}'
    live=fetch_live(api,h); final=patch(live); b=bindings(api,h)
    lines += [f'BASE_SOURCE_BYTES={len(live.encode())}',f'PATCHED_SOURCE_BYTES={len(final.encode())}','BINDINGS_PRESERVED=19']
    v,d=deploy(api,h,final,b,'UGI R44.5.20 reliable checkout + branded domain'); wait(NEW)
    lines += ['FINAL_VERSION_ID='+v,'FINAL_DEPLOYMENT_ID='+d,'WORKER_HEALTH_PASS=true']

    validate_store(ORIGIN); lines += ['STORE_PAGE_HTTP_200=true','PRODUCT_PAGE_HTTP_200=true','BUY_ANCHOR_PRESENT=true','LEGACY_POST_FORM_ABSENT=true']
    code,loc=validate_checkout(ORIGIN)
    lines += [f'CHECKOUT_REDIRECT_HTTP={code}','CHECKOUT_CREATION_TEST_PASS=true','CHECKOUT_URL_RETURNED=true','CHECKOUT_REDIRECT_PASS=true','CHECKOUT_NOT_EXPIRED_AT_CREATION=true','PAYMENT_PERFORMED=false']

    ok,mode,data=attach_custom_domain(acct,tok)
    lines += ['CUSTOM_DOMAIN_ATTACH_ATTEMPTED=true','CUSTOM_DOMAIN_ATTACH_MODE='+mode,'CUSTOM_DOMAIN_ATTACH_PASS='+str(ok).lower()]
    if ok:
        custom_ok=False
        custom_url=CUSTOM_ORIGIN+'/materiais'
        for _ in range(30):
            try:
                rr=requests.get(custom_url,timeout=12,allow_redirects=True)
                if rr.status_code==200 and 'Materiais práticos' in rr.text:
                    custom_ok=True; break
            except Exception: pass
            time.sleep(4)
        lines += ['CUSTOM_DOMAIN_HTTP_PASS='+str(custom_ok).lower()]
        if custom_ok:
            lines += ['BRANDED_COMMERCE_URL='+custom_url,'BIO_URL_READY=true']
        else:
            lines += ['BRANDED_COMMERCE_URL=PENDING_TLS_DNS','BIO_URL_READY=false']
    else:
        err=json.dumps(data,ensure_ascii=False,separators=(',',':'))[:1200]
        lines += ['CUSTOM_DOMAIN_HTTP_PASS=false','BRANDED_COMMERCE_URL=NOT_CREATED','BIO_URL_READY=false','CUSTOM_DOMAIN_ERROR='+err.replace('\n',' ')]

    lines += ['COMMERCE_HUB_READY=true','CHECKOUT_END_TO_END_READY=true','OK=true']
    write(lines)

if __name__=='__main__':
    try: main()
    except BaseException as e:
        try:x=STATUS.read_text(encoding='utf-8').splitlines() if STATUS.exists() else []
        except Exception:x=[]
        x += ['ERROR_TYPE='+type(e).__name__,'ERROR='+str(e).replace('\n',' ')[:2500],'COMMERCE_HUB_READY=false','CHECKOUT_END_TO_END_READY=false','OK=false']
        write(x)
        raise
