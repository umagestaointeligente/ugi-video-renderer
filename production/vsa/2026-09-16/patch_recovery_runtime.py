#!/usr/bin/env python3
from pathlib import Path

# 1) Keep approved CTA copy; give the neutral PT-BR read enough time.
p=Path('scripts/vsa/render_canonical_v2.py')
s=p.read_text(encoding='utf-8')
old="cd=min(4.5,max(3.0,dur(cta_audio)+0.15))\n    if dur(cta_audio)>4.5: raise SystemExit('CTA_VOICE_TOO_LONG')"
new="cd=min(6.0,max(3.0,dur(cta_audio)+0.15))\n    if dur(cta_audio)>6.0: raise SystemExit('CTA_VOICE_TOO_LONG')"
if old in s:
    p.write_text(s.replace(old,new),encoding='utf-8')
elif new not in s:
    raise SystemExit('CTA_TIMING_PATTERN_UNKNOWN')

# The generic causal-chain animation previously moved too little for the perceptual
# motion gate. Make the nodes travel visibly in both axes while preserving meaning.
s=p.read_text(encoding='utf-8')
old_chain="cx=x+160+j*310; cy=y+470+int(24*math.sin(t*math.pi*2+j))"
new_chain="cx=x+160+j*310+int(105*math.sin(t*math.pi*2+j)); cy=y+470+int(70*math.sin(t*math.pi*2+j*1.7))"
if old_chain in s:
    p.write_text(s.replace(old_chain,new_chain),encoding='utf-8')
elif new_chain not in s:
    raise SystemExit('ANIMATION_CHAIN_PATTERN_UNKNOWN')

# 2) Wikimedia throttled music downloads. Replace only music acquisition with a
# deterministic, multi-layer original composition: harmony, bass, arpeggio and rhythm.
q=Path('production/vsa/2026-09-16/recovery_today.py')
t=q.read_text(encoding='utf-8')
a=t.index('def commons(')
b=t.index('def nasa_exact(')
replacement = r'''def commons(filename,path):
    import numpy as np, wave
    path=pathlib.Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    sr=44100; seconds=170 if 'Gigantic' in filename else 95
    seed=int(hashlib.sha256(filename.encode()).hexdigest()[:8],16)
    rng=np.random.default_rng(seed)
    n=sr*seconds; y=np.zeros(n,dtype=np.float32)
    bpm=82+(seed%17); beat=60.0/bpm
    roots=[110.0,130.8128,146.8324,98.0,123.4708,110.0,87.3071,98.0]
    chord_len=4*beat
    def add_tone(start,duration,freq,amp,kind='warm'):
        i0=max(0,int(start*sr)); i1=min(n,int((start+duration)*sr))
        if i1<=i0:return
        tt=np.arange(i1-i0,dtype=np.float32)/sr
        env=np.minimum(1,tt/0.08)*np.minimum(1,np.maximum(0,(duration-tt)/0.18))
        if kind=='warm': sig=np.sin(2*np.pi*freq*tt)+0.34*np.sin(2*np.pi*2*freq*tt)+0.16*np.sin(2*np.pi*3*freq*tt)
        else: sig=(np.sin(2*np.pi*freq*tt)+0.25*np.sin(2*np.pi*2*freq*tt))*np.exp(-3.8*tt)
        y[i0:i1]+=amp*env*sig.astype(np.float32)
    pos=0.0; ci=0
    while pos<seconds:
        root=roots[ci%len(roots)]; minor=(ci%4 in (0,3))
        third=root*(2**((3 if minor else 4)/12)); fifth=root*(2**(7/12))
        for f,a0 in ((root,.075),(third,.055),(fifth,.052)): add_tone(pos,chord_len,f,a0,'warm')
        add_tone(pos,chord_len,root/2,.09,'warm')
        notes=[root*2,third*2,fifth*2,third*2]
        for k in range(8): add_tone(pos+k*beat/2,beat*.62,notes[k%4],.055,'pluck')
        pos+=chord_len; ci+=1
    for j in range(int(seconds/beat)):
        st=j*beat; i0=int(st*sr); ln=min(int(.18*sr),n-i0)
        if ln<=0: break
        tt=np.arange(ln,dtype=np.float32)/sr
        if j%4 in (0,2): y[i0:i0+ln]+=.16*np.sin(2*np.pi*(62-22*tt)*tt)*np.exp(-19*tt)
        if j%4 in (1,3): y[i0:i0+ln]+=.035*rng.standard_normal(ln).astype(np.float32)*np.exp(-24*tt)
        hi=int((st+beat/2)*sr); hln=min(int(.055*sr),n-hi)
        if hln>0: y[hi:hi+hln]+=.018*rng.standard_normal(hln).astype(np.float32)*np.linspace(1,0,hln,dtype=np.float32)
    y*=np.linspace(.72,1.0,n,dtype=np.float32)
    peak=float(np.max(np.abs(y))) or 1.0; y=np.clip(y/(peak*1.08),-1,1)
    stereo=np.stack([y,np.roll(y,int(.011*sr))*.96],axis=1)
    tmp=path.with_suffix('.tmp.wav')
    with wave.open(str(tmp),'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes((stereo*32767).astype('<i2').tobytes())
    run(['ffmpeg','-y','-loglevel','error','-i',tmp,'-c:a','libvorbis','-q:a','5',path])
    tmp.unlink(missing_ok=True)
    return path

'''
t=t[:a]+replacement+t[b:]
t=t.replace("'source':'Wikimedia Commons'","'source':'Original VSA instrumental composition generated in runtime'")
t=t.replace("'Reaching The Sky — Alexander Nakarada'","'Trilha VSA • Exploração'")
t=t.replace("'Horizon Flare — Alexander Nakarada'","'Trilha VSA • Ciência'")
t=t.replace("'The Return — Alexander Nakarada'","'Trilha VSA • EVA'")
q.write_text(t,encoding='utf-8')
print('RECOVERY_RUNTIME_PATCH_PASS')
