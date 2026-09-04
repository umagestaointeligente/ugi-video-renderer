from __future__ import annotations

import os
import re
from pathlib import Path
import requests
import r45_instagram_multiformat_deploy as base

OUT = Path('control-plane/recovery/UGI_20260904_LIVE_WORKER_BUFFER_EXTRACT.txt')

def main():
    token=os.environ.get('CF_API_TOKEN','')
    account=os.environ.get('CF_ACCOUNT_ID','')
    if not token or not account:
        raise SystemExit('Cloudflare credentials missing')
    headers=base.api_headers(token)
    api_base=f'https://api.cloudflare.com/client/v4/accounts/{account}/workers/scripts/{base.WORKER_NAME}'
    r=requests.get(api_base+'/content/v2',headers=headers,timeout=45)
    r.raise_for_status()
    source=base.extract_worker_source(r)
    # Extract only source neighborhoods around routing/Buffer mutation anchors.
    patterns=[
        r'instagramStory', r'shouldShareToFeed', r'createPost\(', r'updatePost\(',
        r'deletePost\(', r'cancel', r'bufferGraphQL', r'platform-publish', r'publication-status'
    ]
    lines=source.splitlines()
    selected=[]
    seen=set()
    for i,line in enumerate(lines):
        if any(re.search(p,line,re.I) for p in patterns):
            a=max(0,i-8); b=min(len(lines),i+14)
            key=(a,b)
            if key in seen: continue
            seen.add(key)
            selected.append(f'--- lines {a+1}-{b} ---')
            for j in range(a,b):
                s=lines[j]
                # Redact obvious bearer/token literals defensively.
                s=re.sub(r'Bearer\s+[A-Za-z0-9._-]+','Bearer ***',s,flags=re.I)
                selected.append(f'{j+1}: {s}')
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text('\n'.join(selected)+'\n',encoding='utf-8')
    print(f'EXTRACT_SECTIONS={len(seen)}')

if __name__=='__main__': main()
