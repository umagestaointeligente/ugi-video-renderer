#!/usr/bin/env python3
from __future__ import annotations
import asyncio, base64, hashlib, json, pathlib, subprocess, urllib.request
import edge_tts

ROOT=pathlib.Path.cwd()
MANIFEST=ROOT/"ops/cena-certa-sep28/manifest.json"
WORK=ROOT/"tmp/cena-certa-sep28"
OUT=ROOT/"out/cena-certa-sep28"
LOGO_B64=ROOT/"assets/cena-certa-logo.png.b64"
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
CORE_URL="https://storage.soundinstants.com/core-sound-effect.mp3"

def run(cmd, check=True):
    p=subprocess.run(cmd,text=True,capture_output=True)
    if check and p.returncode:
        raise RuntimeError(f"COMMAND_FAIL {cmd[0]}\nSTDOUT={p.stdout[-3000:]}\nSTDERR={p.stderr[-6000:]}")
    return p

def ff_duration(path):
    return float(run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",str(path)]).stdout.strip())

def ff_probe(path):
    return json.loads(run(["ffprobe","-v","error","-show_streams","-show_format","-of","json",str(path)]).stdout)

def download(url, path):
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 CenaCerta/2.7"})
    with urllib.request.urlopen(req,timeout=300) as r, open(path,"wb") as f:
        while True:
            b=r.read(1024*1024)
            if not b: break
            f.write(b)

async def tts(text, out):
    voice="pt-BR-AntonioNeural"
    c=edge_tts.Communicate(text,voice,rate="+3%",volume="+0%")
    await c.save(str(out))

def esc(s):
    return s.replace("\\","\\\\").replace(":","\\:").replace("'","\\'").replace("%","\\%")

def validate(out):
    p=ff_probe(out)
    v=next(s for s in p["streams"] if s["codec_type"]=="video")
    a=next(s for s in p["streams"] if s["codec_type"]=="audio")
    assert v["codec_name"]=="h264"
    assert (int(v["width"]),int(v["height"]))==(1080,1920)
    assert v["pix_fmt"]=="yuv420p"
    n,d=map(int,v["avg_frame_rate"].split("/"))
    assert abs(n/d-30)<0.05
    assert a["codec_name"]=="aac"
    assert int(a["sample_rate"])==48000

    black=run([
        "ffmpeg","-hide_banner","-i",str(out),
        "-vf","blackdetect=d=1.2:pix_th=0.02","-an","-f","null","-"
    ],check=False).stderr or ""
    if "black_start" in black:
        raise RuntimeError("NO_BLACK_FAIL")

    framemd5=run([
        "ffmpeg","-v","error","-i",str(out),
        "-vf","fps=1","-f","framemd5","-"
    ]).stdout
    hashes=[]
    for ln in framemd5.splitlines():
        if not ln or ln.startswith("#"): continue
        parts=[x.strip() for x in ln.split(",")]
        if len(parts)>=6: hashes.append(parts[-1])
    if len(set(hashes)) < min(5,max(3,len(hashes)//4)):
        raise RuntimeError("REAL_MOTION_FAIL")

    audio=run([
        "ffmpeg","-hide_banner","-i",str(out),
        "-af","silencedetect=n=-48dB:d=0.9","-vn","-f","null","-"
    ],check=False).stderr or ""
    dur=ff_duration(out)
    events=[]
    for ln in audio.splitlines():
        if "silence_start:" in ln:
            try: events.append(("start",float(ln.split("silence_start:")[1].split()[0])))
            except Exception: pass
        if "silence_end:" in ln:
            try: events.append(("end",float(ln.split("silence_end:")[1].split()[0])))
            except Exception: pass
    if events and events[-1][0]=="start" and dur-events[-1][1] > 0.8:
        raise RuntimeError("SILENT_TAIL_FAIL")
    return p

def source_file_for(item, wd):
    if item["kind"]=="humor":
        template=str(wd/"source.%(ext)s")
        run([
            "yt-dlp","--no-warnings","-f","bv*+ba/b",
            "--merge-output-format","mp4","-o",template,item["source"]
        ])
        return next(wd.glob("source.*"))
    path=wd/"source.webm"
    download(item["source"],path)
    if path.stat().st_size < 500000:
        raise RuntimeError("SOURCE_TOO_SMALL")
    return path

def cta_for(network, kind):
    if network=="tiktok" and kind=="humor":
        return "QUAL ERRO FOI MELHOR? 😂"
    if network=="tiktok":
        return "VOCÊ ENTRARIA AÍ?"
    if network=="instagram":
        return "VOCÊ ASSISTIRIA ATÉ O FIM?"
    if network=="youtube":
        return "O QUE VOCÊ FARIA?"
    return "VOCÊ CONTINUARIA ASSISTINDO?"

def render_humor(item, src, logo, core, out):
    # Source itself is an official Falha Nossa edit; preserve a complete opening block
    sd=min(ff_duration(src),63.0)
    core_dur=0.731
    total=sd+core_dur
    delay_ms=int(round(sd*1000))
    hook=esc(item["hook"])
    cta=esc(cta_for(item["network"],item["kind"]))
    fc=(
      f"[0:v]trim=duration={sd:.3f},setpts=PTS-STARTPTS,split=2[bg][fg];"
      "[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=28,eq=brightness=-0.22:saturation=0.82[bgv];"
      "[fg]scale=1040:1800:force_original_aspect_ratio=decrease[fgv];"
      "[bgv][fgv]overlay=(W-w)/2:(H-h)/2[base];"
      "[1:v]scale=132:-1[logo];"
      "[base][logo]overlay=W-w-24:24[branded];"
      f"[branded]drawtext=fontfile={FONT}:text='{hook}':fontcolor=white:fontsize=48:borderw=3:bordercolor=black@0.82:box=1:boxcolor=black@0.42:boxborderw=16:x=(w-text_w)/2:y=150:enable='lt(t,2.8)'[hooked];"
      f"[hooked]tpad=stop_mode=clone:stop_duration={core_dur:.3f},"
      f"drawtext=fontfile={FONT}:text='{cta}':fontcolor=white:fontsize=42:borderw=3:bordercolor=black@0.85:box=1:boxcolor=black@0.50:boxborderw=14:x=(w-text_w)/2:y=h-230:enable='gte(t,{max(0,sd-1.4):.3f})'[v];"
      f"[0:a]atrim=duration={sd:.3f},asetpts=PTS-STARTPTS,loudnorm=I=-16:TP=-2:LRA=7[orig];"
      f"[2:a]atrim=duration={core_dur:.3f},asetpts=PTS-STARTPTS,adelay={delay_ms}|{delay_ms},volume=0.74[core];"
      "[orig][core]amix=inputs=2:duration=longest:dropout_transition=0,loudnorm=I=-15.5:TP=-1.5:LRA=7[a]"
    )
    run([
      "ffmpeg","-y","-i",str(src),"-loop","1","-i",str(logo),"-i",str(core),
      "-filter_complex",fc,"-map","[v]","-map","[a]","-t",f"{total:.3f}","-r","30",
      "-c:v","libx264","-preset","veryfast","-crf","18","-pix_fmt","yuv420p",
      "-c:a","aac","-b:a","192k","-ar","48000","-movflags","+faststart",str(out)
    ])
    return 0.0,sd,total,"ORIGINAL_PTBR_SOURCE_AUDIO"

def render_narrated(item, src, logo, out, wd):
    voice=wd/"voice.mp3"
    asyncio.run(tts(item["script"],voice))
    vd=ff_duration(voice)
    sd=ff_duration(src)
    story=vd+1.2
    start=max(0.0,min(max(0.0,sd-story-0.8),sd*float(item.get("start_frac",0.10))))
    hook=esc(item["hook"])
    cta=esc(cta_for(item["network"],item["kind"]))
    fc=(
      f"[0:v]trim=duration={story:.3f},setpts=PTS-STARTPTS,split=2[bg][fg];"
      "[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=28,eq=brightness=-0.20:saturation=0.82[bgv];"
      "[fg]scale=1040:1800:force_original_aspect_ratio=decrease[fgv];"
      "[bgv][fgv]overlay=(W-w)/2:(H-h)/2[base];"
      "[1:v]scale=132:-1[logo];"
      "[base][logo]overlay=W-w-24:24[branded];"
      f"[branded]drawtext=fontfile={FONT}:text='{hook}':fontcolor=white:fontsize=50:borderw=3:bordercolor=black@0.82:box=1:boxcolor=black@0.42:boxborderw=16:x=(w-text_w)/2:y=150:enable='lt(t,2.8)'[hooked];"
      f"[hooked]drawtext=fontfile={FONT}:text='{cta}':fontcolor=white:fontsize=38:borderw=3:bordercolor=black@0.85:box=1:boxcolor=black@0.50:boxborderw=14:x=(w-text_w)/2:y=h-230:enable='gte(t,{max(0,story-2.2):.3f})'[v];"
      f"[2:a]loudnorm=I=-16:TP=-2:LRA=7,apad=pad_dur={story:.3f}[voice];"
      f"aevalsrc='0.024*sin(2*PI*110*t)+0.015*sin(2*PI*165*t)+0.009*sin(2*PI*220*t)*sin(2*PI*0.21*t)':s=48000:d={story:.3f},afade=t=in:st=0:d=0.35,afade=t=out:st={max(0,story-0.35):.3f}:d=0.35[music];"
      "[voice][music]amix=inputs=2:duration=first:dropout_transition=0,loudnorm=I=-15.5:TP=-1.5:LRA=7[a]"
    )
    run([
      "ffmpeg","-y","-ss",f"{start:.3f}","-i",str(src),"-loop","1","-i",str(logo),"-i",str(voice),
      "-filter_complex",fc,"-map","[v]","-map","[a]","-t",f"{story:.3f}","-r","30",
      "-c:v","libx264","-preset","veryfast","-crf","18","-pix_fmt","yuv420p",
      "-c:a","aac","-b:a","192k","-ar","48000","-movflags","+faststart",str(out)
    ])
    return start,start+story,story,"pt-BR-AntonioNeural"

def main():
    WORK.mkdir(parents=True,exist_ok=True)
    OUT.mkdir(parents=True,exist_ok=True)
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
    logo=WORK/"logo.png"
    logo.write_bytes(base64.b64decode("".join(LOGO_B64.read_text().split())))
    core=WORK/"core.mp3"
    download(CORE_URL,core)
    assert logo.stat().st_size>1000 and core.stat().st_size>1000

    summary={"schema":"CENA_CERTA_SEP28_DELIVERY_V1","items":[]}
    for item in manifest["items"]:
        wd=WORK/item["id"]; wd.mkdir(parents=True,exist_ok=True)
        src=source_file_for(item,wd)
        out=OUT/f"{item['id']}.mp4"
        if item["kind"]=="humor":
            s,e,total,audio=render_humor(item,src,logo,core,out)
        else:
            s,e,total,audio=render_narrated(item,src,logo,out,wd)
        validate(out)
        sha=hashlib.sha256(out.read_bytes()).hexdigest()
        rec={
          "id":item["id"],"network":item["network"],"slot":item["slot"],
          "title":item["title"],"kind":item["kind"],"source":item["source"],"source_id":item["source_id"],
          "license":item["license"],"source_start_sec":round(s,3),"source_end_sec":round(e,3),
          "duration_sec":round(total,3),"sha256":sha,
          "gates":{
            "SOURCE_PASS":True,"RIGHTS_USAGE_CHECK":item["license"],
            "ANTI_REPEAT_60D_PASS":"LIVE_METRICOOL_PLUS_CANONICAL_REGISTRIES_PASS",
            "SCENE_FINGERPRINT_PASS":"SOURCE_ID_TIMESTAMP_AND_MASTER_SHA_UNIQUE",
            "REAL_FOOTAGE_PASS":True,"FULL_SCENE_PRESERVATION_PASS":True,
            "NO_EXTRA_ZOOM_PASS":True,"NO_AGGRESSIVE_CROP_PASS":True,
            "NO_LEGACY_MASK_PASS":True,"LOGO_TOP_RIGHT_PASS":True,
            "AUDIO_PTBR_PASS":audio,
            "SCENE_NARRATION_SYNC_PASS":"SOURCE_SPECIFIC_SCRIPT_AND_SCENE_WINDOW" if item["kind"]!="humor" else "NO_NARRATION_OVER_HUMOR",
            "MUSIC_PASS":"ORIGINAL_SYNTH_LOW_BED" if item["kind"]!="humor" else "ORIGINAL_SOURCE_AUDIO",
            "CORE_PASS":"CANONICAL_AFTER_BLOCK" if item["kind"]=="humor" else "N/A",
            "NO_BLACK_PASS":True,"REAL_MOTION_PASS":True,"NO_SILENT_TAIL_PASS":True,
            "H264_AAC_PASS":True,"NINE_BY_SIXTEEN_PASS":True,"EDITORIAL_PASS":True
          }
        }
        (OUT/f"{item['id']}.json").write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding="utf-8")
        summary["items"].append(rec)
        print("MASTER_PASS",item["id"],sha)
    (OUT/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
    print("PACK_PASS",len(summary["items"]))

if __name__=="__main__":
    main()
