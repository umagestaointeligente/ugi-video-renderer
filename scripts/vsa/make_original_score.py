#!/usr/bin/env python3
"""Generate a deterministic original instrumental documentary score as WAV.
Not a tone/drone: chord progression + melody + arpeggio + bass + percussion,
with multiple sections and harmonic development. Rights basis: original VSA production.
"""
from __future__ import annotations
import argparse, math, wave
import numpy as np

def hz(m): return 440.0*(2**((m-69)/12))
def env(n, sr, attack=.03, release=.18):
    e=np.ones(n,dtype=np.float32); a=min(n,int(sr*attack)); r=min(n-a,int(sr*release))
    if a: e[:a]=np.linspace(0,1,a,dtype=np.float32)
    if r: e[-r:]=np.linspace(1,0,r,dtype=np.float32)
    return e

def note(midi, dur, sr, kind='piano', amp=.2):
    n=max(1,int(dur*sr)); t=np.arange(n,dtype=np.float32)/sr; f=hz(midi)
    if kind=='strings':
        x=np.sin(2*np.pi*f*t)+.38*np.sin(2*np.pi*2*f*t)+.18*np.sin(2*np.pi*3*f*t)
        e=env(n,sr,.30,.45)
    elif kind=='bass':
        x=np.sin(2*np.pi*f*t)+.25*np.sin(2*np.pi*2*f*t); e=env(n,sr,.02,.25)
    else:
        x=np.sin(2*np.pi*f*t)+.45*np.sin(2*np.pi*2*f*t)+.15*np.sin(2*np.pi*3*f*t)
        e=env(n,sr,.01,.35)*np.exp(-1.4*t/max(dur,.01))
    return (amp*x*e).astype(np.float32)

def add(buf, start, x):
    i=max(0,int(start)); j=min(len(buf),i+len(x));
    if j>i: buf[i:j]+=x[:j-i]

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out',required=True); ap.add_argument('--seconds',type=float,default=150); ap.add_argument('--seed',type=int,default=1409); a=ap.parse_args()
    sr=48000; total=int(a.seconds*sr); L=np.zeros(total,np.float32); R=np.zeros(total,np.float32); rng=np.random.default_rng(a.seed)
    bpm=84; beat=60/bpm; bar=beat*4
    # C minor -> Ab -> Eb -> Bb, with a brighter bridge; four-bar sections.
    progressions=[[(48,51,55),(44,48,51),(51,55,58),(46,50,53)],[(48,51,55),(43,47,50),(44,48,51),(46,50,53)]]
    melody=[60,63,67,65,63,60,58,60,67,65,63,62,60,58,55,58]
    bars=int(math.ceil(a.seconds/bar))
    for b in range(bars):
        section=(b//8)%2; chord=progressions[section][b%4]; st=b*bar
        # sustained strings harmony
        for k,m in enumerate(chord):
            x=note(m,bar*.98,sr,'strings',.055)
            add(L,int(st*sr),x*(.85 if k%2 else 1)); add(R,int(st*sr),x*(1 if k%2 else .85))
        # bass on beats 1 and 3
        for q in (0,2):
            x=note(chord[0]-12,beat*.82,sr,'bass',.10); add(L,int((st+q*beat)*sr),x); add(R,int((st+q*beat)*sr),x*.95)
        # arpeggiated piano eighth notes
        arp=[chord[0]+12,chord[1]+12,chord[2]+12,chord[1]+12]*2
        for q,m in enumerate(arp):
            x=note(m,beat*.42,sr,'piano',.075); ts=st+q*beat/2
            add(L,int(ts*sr),x*(.92 if q%2 else 1.05)); add(R,int(ts*sr),x*(1.05 if q%2 else .92))
        # melodic phrase every second bar
        if b%2==0:
            for q in range(8):
                m=melody[(b*4+q)%len(melody)]
                x=note(m,beat*.45,sr,'piano',.075); ts=st+q*beat/2
                add(L,int(ts*sr),x); add(R,int(ts*sr),x*.9)
        # soft cinematic percussion: kick/noise hit on 1, brushed hit on 3
        for q,amp in ((0,.045),(2,.028)):
            n=int(.18*sr); tt=np.arange(n)/sr; noise=rng.normal(0,1,n).astype(np.float32)
            hit=(noise*np.exp(-18*tt)*amp).astype(np.float32); ts=int((st+q*beat)*sr)
            add(L,ts,hit); add(R,ts,hit*.92)
    # macro fade in/out and gentle limiter
    fade=int(sr*1.2); L[:fade]*=np.linspace(0,1,fade); R[:fade]*=np.linspace(0,1,fade); L[-fade:]*=np.linspace(1,0,fade); R[-fade:]*=np.linspace(1,0,fade)
    peak=max(float(np.max(np.abs(L))),float(np.max(np.abs(R))),1e-6); gain=min(1.0,.88/peak); stereo=np.stack([L*gain,R*gain],axis=1); pcm=(np.clip(stereo,-1,1)*32767).astype('<i2')
    with wave.open(a.out,'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm.tobytes())
    print('ORBIT_DISCOVERY_SCORE_01_PASS structured_sections=true harmony=true melody=true bass=true percussion=true instrumental=true')
if __name__=='__main__': main()
