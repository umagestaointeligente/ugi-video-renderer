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
    # Diagnostic-only extraction. Capture wider neighborhoods around the live
    # Buffer GraphQL helpers and platform-publish route so LinkedIn text-only
    # support can be repaired without guessing the deployed contract.
    patterns=[
        r'platformMetadataGraphQL', r'createBufferPlatformVideoPost',
        r'bufferCreatePost', r'bufferCreateWithAssets', r'bufferData',
        r'bufferGraphQL', r'/api/buffer/channels', r'platform-publish',
        r'publication-status', r'createPost\(', r'updatePost\(', r'deletePost\('
    ]
    lines=source.splitlines()
    selected=[]
    intervals=[]
    for i,line in enumerate(lines):
        if any(re.search(p,line,re.I) for p in patterns):
            intervals.append((max(0,i-35), min(len(lines),i+85)))
    # Merge overlapping intervals for coherent source neighborhoods.
    intervals.sort()
    merged=[]
    for a,b in intervals:
        if merged and a <= merged[-1][1] + 3:
            merged[-1]=(merged[-1][0], max(merged[-1][1],b))
        else:
            merged.append((a,b))
    for a,b in merged:
        selected.append(f'--- lines {a+1}-{b} ---')
        for j in range(a,b):
            s=lines[j]
            s=re.sub(r'Bearer\s+[A-Za-z0-9._-]+','Bearer ***',s,flags=re.I)
            selected.append(f'{j+1}: {s}')
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text('\n'.join(selected)+'\n',encoding='utf-8')
    print(f'EXTRACT_SECTIONS={len(merged)}')

if __name__=='__main__': main()
