#!/usr/bin/env python3
from __future__ import annotations
import json, math, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output'; OUT.mkdir(exist_ok=True)
STATE=OUT/'learning-state.json'

DEFAULT={"version":1,"channels":{},"formats":{},"topics":{},"observations":0}

def load_state():
    if STATE.exists():
        try:return json.loads(STATE.read_text(encoding='utf-8'))
        except Exception:pass
    return DEFAULT.copy()

def clamp(v,lo=0,hi=1): return max(lo,min(hi,float(v)))

def reward(m):
    retention=clamp(m.get('retention_rate',0))
    completion=clamp(m.get('completion_rate',0))
    engagement=clamp(m.get('engagement_rate',0)*5)
    ctr=clamp(m.get('ctr',0)*10)
    rpm=clamp(float(m.get('rpm',0))/20.0)
    rights=1.0 if m.get('rights_ok',True) else 0.0
    return round((0.32*retention+0.25*completion+0.20*engagement+0.13*ctr+0.10*rpm)*rights,4)

def update_bucket(bucket,key,r):
    x=bucket.setdefault(key,{"n":0,"mean_reward":0.0,"wins":0})
    x['n']+=1
    x['mean_reward']=round(x['mean_reward']+(r-x['mean_reward'])/x['n'],4)
    if r>=0.62:x['wins']+=1

def ingest(metrics):
    st=load_state()
    for m in metrics:
        r=reward(m); m['reward']=r
        update_bucket(st['channels'],m.get('channel','unknown'),r)
        update_bucket(st['formats'],m.get('format','unknown'),r)
        update_bucket(st['topics'],m.get('topic_cluster','unknown'),r)
        st['observations']+=1
    STATE.write_text(json.dumps(st,ensure_ascii=False,indent=2),encoding='utf-8')
    return st

def main():
    if len(sys.argv)<2:
        print(json.dumps(load_state(),ensure_ascii=False,indent=2)); return 0
    p=Path(sys.argv[1]); payload=json.loads(p.read_text(encoding='utf-8'))
    metrics=payload if isinstance(payload,list) else payload.get('metrics',[])
    st=ingest(metrics)
    print(json.dumps({"observations":st['observations'],"channels":st['channels']},ensure_ascii=False))
    return 0

if __name__=='__main__': raise SystemExit(main())
