import os,re
from email.parser import BytesParser
from email.policy import default
from pathlib import Path
import requests

account=os.environ['CF_ACCOUNT_ID']; token=os.environ['CF_API_TOKEN']
base=f'https://api.cloudflare.com/client/v4/accounts/{account}/workers/scripts/lola-operacional-ugi/content/v2'
r=requests.get(base,headers={'Authorization':f'Bearer {token}'},timeout=30); r.raise_for_status()
ctype=r.headers.get('content-type',''); body=r.content
if 'multipart/' in ctype.lower():
    env=(f'Content-Type: {ctype}\r\nMIME-Version: 1.0\r\n\r\n'.encode()+body)
    msg=BytesParser(policy=default).parsebytes(env); cand=[]
    for part in msg.iter_parts():
        ptype=(part.get_content_type() or '').lower(); fn=(part.get_filename() or '').lower(); payload=part.get_payload(decode=True) or b''
        if 'javascript' in ptype or fn.endswith(('.js','.mjs')): cand.append(payload)
    src=max(cand,key=len).decode('utf-8')
else: src=body.decode('utf-8')
patterns=['path === "/priorizacao"','if (path === "/approve")','async function fetch','return json({','new URL(request.url)']
out=['LIVE_SOURCE_CONTEXT_DIAGNOSTIC']
for pat in patterns:
    out.append(f'PATTERN={pat} COUNT={src.count(pat)}')
    pos=src.find(pat)
    if pos>=0:
        snippet=src[max(0,pos-1800):min(len(src),pos+2600)].replace('\n','\\n')
        out.append('SNIPPET='+snippet)
Path('cloudflare/status/r44-5-18-context.txt').write_text('\n'.join(out)+'\n',encoding='utf-8')
