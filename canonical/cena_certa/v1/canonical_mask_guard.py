#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, tempfile
from pathlib import Path
import numpy as np
from PIL import Image

def fail(msg): raise SystemExit("CANONICAL_MASK_FAIL: "+msg)

def ratios(arr):
    a=arr.astype(np.int16); mx=a.max(axis=2); mn=a.min(axis=2)
    gold=(a[:,:,0]>=110)&(a[:,:,1]>=60)&(a[:,:,0]>=a[:,:,2]*1.12)&((a[:,:,0]-a[:,:,1])<=150)
    white=(mx>=160)&((mx-mn)<=70); black=mx<=35
    return {"gold":float(gold.mean()),"white":float(white.mean()),"black":float(black.mean())}

def in_range(v,rng): return float(rng[0]) <= v <= float(rng[1])

def check_fp(name,frame,spec):
    x,y,w,h=spec["region"]; roi=frame[y:y+h,x:x+w]
    if roi.shape[:2] != (h,w): fail(f"{name} ROI out of bounds")
    r=ratios(roi); print("MASK_FP",name,r)
    for k in ("gold","white","black"):
        rng=spec[k+"_ratio"]
        if not in_range(r[k],rng): fail(f"{name} {k}={r[k]:.4f} outside {rng}")

def extract(video,t,out):
    subprocess.run(["ffmpeg","-loglevel","error","-y","-ss",f"{t:.3f}","-i",str(video),"-frames:v","1",str(out)],check=True)

def duration(video):
    p=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",str(video)],capture_output=True,text=True,check=True)
    return float(p.stdout.strip())

def load(path): return np.asarray(Image.open(path).convert("RGB"))

def border_gold(frame,rect):
    x,y,w,h=rect
    bands={"top":frame[max(0,y-3):y+4,x:x+w],"bottom":frame[y+h-4:y+h+3,x:x+w],"left":frame[y:y+h,max(0,x-3):x+4],"right":frame[y:y+h,x+w-4:x+w+3]}
    return {k:ratios(v)["gold"] for k,v in bands.items()}

def validate_contract(c):
    if c.get("schema")!="ORBIT_CENA_CERTA_CANONICAL_MASK_V1": fail("wrong schema")
    if c.get("status")!="HARD_LOCK_SOURCE_OF_TRUTH" or not c.get("fail_closed"): fail("hard lock disabled")
    if c.get("canvas")!={"width":1080,"height":1920,"fps":30}: fail("canvas changed")
    allow=set(c["dynamic_slots"]["allowed"]); exp={"TITLE_TEXT","YEAR_TEXT","CC_TEXT","FILM_CONTENT","BLURRED_FILM_BACKGROUND","NARRATION","MUSIC"}
    if allow!=exp: fail("dynamic allowlist changed")
    if c["geometry"]["master_1080x1920"]["film_window"] != [16,664,1046,602]: fail("film window changed")
    if c["geometry"]["master_1080x1920"]["story_logo"] != [910,371,99,168]: fail("story logo moved")
    if c["geometry"]["master_1080x1920"]["footer"] != [42,1666,995,201]: fail("footer moved")
    if c["cc_rules"]["max_lines"] != 2: fail("CC line lock changed")
    if c["cta_rules"]["spoken_line"] != "Siga, curta e compartilhe o Cena Certa.": fail("CTA voice changed")
    if c["audio_rules"]["max_internal_speech_gap_seconds"] > 0.5: fail("speech-gap tolerance loosened")
    if c["audio_rules"]["story_to_cta_gap_max_seconds"] > 0.2: fail("story-to-CTA tolerance loosened")
    print("CANONICAL_MASK_CONTRACT_PASS")

def validate_candidate(c,video,story_second):
    video=Path(video); d=duration(video)
    with tempfile.TemporaryDirectory() as td:
        td=Path(td); s=td/"story.png"; q=td/"cta.png"
        extract(video,story_second,s); extract(video,max(story_second+0.1,d-2.0),q)
        sf=load(s); cf=load(q)
        if sf.shape[:2]!=(1920,1080) or cf.shape[:2]!=(1920,1080): fail("candidate is not 1080x1920")
        fps=c["visual_fingerprints"]
        for n in ("story_title_static_anchor","story_logo","story_footer"): check_fp(n,sf,fps[n])
        br=border_gold(sf,c["geometry"]["master_1080x1920"]["film_window"]); print("MASK_FILM_BORDER",br)
        m=float(c["film_border_gold_ratio_min"])
        if any(v<m for v in br.values()): fail(f"film-window border moved/changed: {br}")
        for n in ("cta_full","cta_logo_top","cta_copy","cta_actions","cta_comment"): check_fp(n,cf,fps[n])
    print("CANONICAL_MASK_CANDIDATE_PASS")

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--contract",default="canonical/cena_certa/v1/contract_cena_certa_canonical_mask_v1.json"); ap.add_argument("--candidate"); ap.add_argument("--story-second",type=float,default=2.0); a=ap.parse_args()
    c=json.loads(Path(a.contract).read_text(encoding="utf-8")); validate_contract(c)
    if a.candidate: validate_candidate(c,a.candidate,a.story_second)

if __name__=="__main__": main()
