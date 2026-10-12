#!/usr/bin/env python3
from __future__ import annotations
import base64, hashlib, json, pathlib, subprocess, urllib.request, time

ROOT=pathlib.Path.cwd()
MANIFEST=ROOT/"ops/cena-certa-sep30/manifest.json"
WORK=ROOT/"tmp/cena-certa-sep30"
OUT=ROOT/"out/cena-certa-sep30"
LOGO_B64=ROOT/"assets/cena-certa-logo.png.b64"
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
CORE_URL="https://storage.soundinstants.com/core-sound-effect.mp3"

def run(cmd,check=True):
    p=subprocess.run(cmd,text=True,capture_output=True)
    if check and p.returncode:
        raise RuntimeError(f"FAIL {cmd[0]}\nSTDOUT={p.stdout[-3000:]}\nSTDERR={p.stderr[-6000:]}")
    return p

def duration(path):
    return float(run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",str(path)]).stdout.strip())

def probe(path):
    return json.loads(run(["ffprobe","-v","error","-show_streams","-show_format","-of","json",str(path)]).stdout)

def download(url,path):
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 CenaCerta/2.7"})
    with urllib.request.urlopen(req,timeout=120) as r, open(path,"wb") as f:
        while True:
            b=r.read(1024*1024)
            if not b: break
            f.write(b)

def esc(s):
    return s.replace("\\","\\\\").replace(":","\\:").replace("'","\\'").replace("%","\\%")

def validate(out):
    p=probe(out)
    v=next(s for s in p["streams"] if s["codec_type"]=="video")
    a=next(s for s in p["streams"] if s["codec_type"]=="audio")
    assert v["codec_name"]=="h264"
    assert (int(v["width"]),int(v["height"]))==(1080,1920)
    assert v["pix_fmt"]=="yuv420p"
    n,d=map(int,v["avg_frame_rate"].split("/"))
    assert abs(n/d-30)<0.05
    assert a["codec_name"]=="aac" and int(a["sample_rate"])==48000

    black=run(["ffmpeg","-hide_banner","-i",str(out),"-vf","blackdetect=d=1.0:pix_th=0.02","-an","-f","null","-"]).stderr or ""
    if "black_start" in black: raise RuntimeError("NO_BLACK_FAIL")

    fm=run(["ffmpeg","-v","error","-i",str(out),"-vf","fps=1","-f","framemd5","-"]).stdout
    hashes=[]
    for ln in fm.splitlines():
        if not ln or ln.startswith("#"): continue
        parts=[x.strip() for x in ln.split(",")]
        if len(parts)>=6: hashes.append(parts[-1])
    if len(set(hashes)) < min(5,max(3,len(hashes)//4)):
        raise RuntimeError("REAL_MOTION_FAIL")

    aud=run(["ffmpeg","-hide_banner","-i",str(out),"-af","silencedetect=n=-48dB:d=0.9","-vn","-f","null","-"]).stderr or ""
    dur=duration(out)
    events=[]
    for ln in aud.splitlines():
        if "silence_start:" in ln:
            try: events.append(("start",float(ln.split("silence_start:")[1].split()[0])))
            except Exception: pass
        if "silence_end:" in ln:
            try: events.append(("end",float(ln.split("silence_end:")[1].split()[0])))
            except Exception: pass
    tail_start = None
    silent_tail = False
    for event, timestamp in events:
        if event == "start":
            tail_start = timestamp
        elif tail_start is not None:
            if timestamp >= dur-0.1 and timestamp-tail_start > 0.8:
                silent_tail = True
            tail_start = None
    if silent_tail or (tail_start is not None and dur-tail_start > 0.8):
        raise RuntimeError("SILENT_TAIL_FAIL")
    return p

def download_source(item,wd):
    last=None
    for attempt in range(1,5):
        try:
            run([
              "yt-dlp","--write-info-json","--no-warnings","--retries","5","--fragment-retries","5","--retry-sleep","3",
              "-f","bv*+ba/b","--merge-output-format","mp4","-o",str(wd/"source.%(ext)s"),item["source"]
            ])
            last=None; break
        except Exception as exc:
            last=exc; time.sleep(4*attempt)
    if last is not None: raise last
    return next(p for p in wd.glob("source.*") if p.suffix != ".json")

def render(item,src,logo,core):
    src_d=duration(src)
    kind=item["kind"]
    if kind=="micro":
        clip_d=src_d
    elif kind=="humor":
        clip_d=min(src_d,58.0)
    elif item["network"]=="instagram":
        clip_d=min(src_d,60.0)
    elif item["network"]=="facebook":
        clip_d=min(src_d,60.0)
    else:
        clip_d=min(src_d,60.0)

    core_d=0.731 if kind=="humor" else 0.0
    total=clip_d+core_d
    hook=esc(item["hook"])
    cta=esc(item.get("cta",""))
    delay=int(round(clip_d*1000))
    out=OUT/f"{item['id']}.mp4"

    # network-specific text behavior
    if item["network"]=="youtube":
        hook_enable="lt(t,1.15)"
        hook_size=44
    elif item["network"]=="instagram":
        hook_enable="lt(t,2.0)"
        hook_size=46
    else:
        hook_enable="lt(t,2.6)"
        hook_size=48

    fc=(
      f"[0:v]trim=duration={clip_d:.3f},setpts=PTS-STARTPTS,split=2[bg][fg];"
      "[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=28,eq=brightness=-0.22:saturation=0.86[bgv];"
      "[fg]scale=1040:1800:force_original_aspect_ratio=decrease[fgv];"
      "[bgv][fgv]overlay=(W-w)/2:(H-h)/2[base];"
      "[1:v]scale=132:-1[logo];"
      "[base][logo]overlay=W-w-24:24[branded];"
      f"[branded]drawtext=fontfile={FONT}:text='{hook}':fontcolor=white:fontsize={hook_size}:borderw=3:bordercolor=black@0.82:box=1:boxcolor=black@0.42:boxborderw=14:x=(w-text_w)/2:y=150:enable='{hook_enable}'[hooked];"
    )

    if kind=="humor":
      fc += (
        f"[hooked]tpad=stop_mode=clone:stop_duration={core_d:.3f},"
        f"drawtext=fontfile={FONT}:text='{cta}':fontcolor=white:fontsize=40:borderw=3:bordercolor=black@0.85:box=1:boxcolor=black@0.50:boxborderw=14:x=(w-text_w)/2:y=h-230:enable='gte(t,{max(0,clip_d-1.4):.3f})'[v];"
        f"[0:a]atrim=duration={clip_d:.3f},asetpts=PTS-STARTPTS,loudnorm=I=-16:TP=-2:LRA=7[orig];"
        f"[2:a]atrim=duration={core_d:.3f},asetpts=PTS-STARTPTS,adelay={delay}|{delay},volume=0.74[core];"
        "[orig][core]amix=inputs=2:duration=longest:dropout_transition=0,loudnorm=I=-15.5:TP=-1.5:LRA=7[a]"
      )
    else:
      if not cta:
        fc += (
          "[hooked]copy[v];"
          f"[0:a]atrim=duration={clip_d:.3f},asetpts=PTS-STARTPTS,loudnorm=I=-16:TP=-2:LRA=7[a]"
        )
      else:
        fc += (
          f"[hooked]drawtext=fontfile={FONT}:text='{cta}':fontcolor=white:fontsize=38:borderw=3:bordercolor=black@0.85:box=1:boxcolor=black@0.48:boxborderw=12:x=(w-text_w)/2:y=h-230:enable='gte(t,{max(0,clip_d-1.8):.3f})'[v];"
          f"[0:a]atrim=duration={clip_d:.3f},asetpts=PTS-STARTPTS,loudnorm=I=-16:TP=-2:LRA=7[a]"
        )

    cmd=["ffmpeg","-y","-i",str(src),"-loop","1","-i",str(logo)]
    if kind=="humor": cmd += ["-i",str(core)]
    cmd += [
      "-filter_complex",fc,"-map","[v]","-map","[a]","-t",f"{total:.3f}","-r","30",
      "-c:v","libx264","-preset","veryfast","-crf","18","-pix_fmt","yuv420p",
      "-c:a","aac","-b:a","192k","-ar","48000","-movflags","+faststart",str(out)
    ]
    run(cmd)
    validate(out)
    return out,clip_d,total

def main():
    WORK.mkdir(parents=True,exist_ok=True); OUT.mkdir(parents=True,exist_ok=True)
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
    logo=WORK/"logo.png"; logo.write_bytes(base64.b64decode("".join(LOGO_B64.read_text().split())))
    core=WORK/"core.mp3"; download(CORE_URL,core)
    summary={"schema":"CENA_CERTA_SEP30_DELIVERY_V1","items":[]}

    for item in manifest["items"]:
        wd=WORK/item["id"]; wd.mkdir(parents=True,exist_ok=True)
        item = dict(item)
        item.setdefault("cta", "QUAL CENA VOCÊ QUER VER AQUI?")
        src=download_source(item,wd)
        source_duration = duration(src)
        metadata = json.loads((wd/"source.info.json").read_text())
        (OUT/f"{item['id']}-source.json").write_text(json.dumps(metadata,ensure_ascii=False,indent=2))
        if str(metadata.get("id")) != str(item["source_id"]):
            raise RuntimeError("SOURCE_ID_MISMATCH")
        out,clip_d,total=render(item,src,logo,core)
        sha=hashlib.sha256(out.read_bytes()).hexdigest()
        rec={
          "id":item["id"],"network":item["network"],"slot":item["slot"],"title":item["title"],"kind":item["kind"],
          "source":item["source"],"source_id":item["source_id"],"source_start_sec":0.0,"source_end_sec":round(clip_d,3),
          "duration_sec":round(total,3),"source_duration_sec":source_duration,"sha256":sha,
          "technical_status":"PASS", "editorial_status":"NOT_VERIFIED",
          "publication_status":"NOT_VERIFIED",
          "gates":{
            "SOURCE_ID_MATCH": True,
            "RIGHTS_USAGE_CHECK":"NOT_VERIFIED",
            "ANTI_REPEAT_60D_PASS":"NOT_VERIFIED",
            "SCENE_FINGERPRINT_PASS":"NOT_VERIFIED",
            "EDITORIAL_PASS":"NOT_VERIFIED",
            "CTA_RENDERED":bool(item.get("cta")),
            "CTA_INSPECTED":"NOT_VERIFIED",
            "TECHNICAL_QA_PASS":True
          }
        }
        (OUT/f"{item['id']}.json").write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding="utf-8")
        summary["items"].append(rec)
        print("MASTER_TECHNICAL_PASS",item["id"],sha)
    (OUT/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
    print("PACK_TECHNICAL_PASS",len(summary["items"]))

if __name__=="__main__":
    main()

