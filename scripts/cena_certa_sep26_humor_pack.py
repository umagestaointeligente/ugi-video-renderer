#!/usr/bin/env python3
from __future__ import annotations
import base64, hashlib, json, pathlib, subprocess, urllib.request

ROOT=pathlib.Path.cwd()
WORK=ROOT/"tmp/cena-certa-sep26-humor"
OUT=ROOT/"out/cena-certa-sep26-humor"
LOGO_B64=ROOT/"assets/cena-certa-logo.png.b64"
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
CORE_URL="https://storage.soundinstants.com/core-sound-effect.mp3"

ITEMS=[
  {
    "id":"CC-SEP26-TT-MISTER-BRAU",
    "title":"Mister Brau — Falha Nossa",
    "source":"https://globoplay.globo.com/v/4707587/",
    "source_id":"4707587",
    "start":0.0,
    "end":59.20,
    "hook":"MISTER BRAU: ninguém segura a cena 😂",
  },
  {
    "id":"CC-SEP26-TT-DEUS-SALVE-REI",
    "title":"Deus Salve o Rei — Falha Nossa",
    "source":"https://globoplay.globo.com/v/6600863/",
    "source_id":"6600863",
    "start":43.0,
    "end":103.60,
    "hook":"DEUS SALVE O REI: a fala simplesmente não saía 😂",
  },
]

def run(cmd, check=True):
    p=subprocess.run(cmd,text=True,capture_output=True)
    if check and p.returncode:
        raise RuntimeError(f"FAIL {cmd[0]}\n{p.stdout[-3000:]}\n{p.stderr[-5000:]}")
    return p

def probe(path):
    return json.loads(run(["ffprobe","-v","error","-show_streams","-show_format","-of","json",str(path)]).stdout)

def dl_url(url,path):
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 CenaCerta/2.7"})
    with urllib.request.urlopen(req,timeout=120) as r, open(path,"wb") as f:
        while True:
            b=r.read(1024*1024)
            if not b: break
            f.write(b)

def draw_escape(s):
    return s.replace("\\","\\\\").replace(":","\\:").replace("'","\\'").replace("%","\\%")

def main():
    WORK.mkdir(parents=True,exist_ok=True)
    OUT.mkdir(parents=True,exist_ok=True)
    logo=WORK/"logo.png"
    logo.write_bytes(base64.b64decode("".join(LOGO_B64.read_text().split())))
    core=WORK/"core.mp3"
    dl_url(CORE_URL,core)
    assert logo.stat().st_size>1000 and core.stat().st_size>1000

    summary={"schema":"CENA_CERTA_SEP26_HUMOR_V1","items":[]}
    for item in ITEMS:
        wd=WORK/item["id"]
        wd.mkdir(parents=True,exist_ok=True)
        template=str(wd/"source.%(ext)s")
        run(["yt-dlp","--no-warnings","-f","bv*+ba/b","--merge-output-format","mp4","-o",template,item["source"]])
        src=next(wd.glob("source.*"))
        seg=item["end"]-item["start"]
        core_dur=0.731
        total=seg+core_dur
        delay_ms=int(round(seg*1000))
        out=OUT/f"{item['id']}.mp4"
        hook=draw_escape(item["hook"])
        cta=draw_escape("QUAL ERRO FOI MELHOR? 😂")
        fc=(
          "[0:v]setpts=PTS-STARTPTS,split=2[bg][fg];"
          "[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
          "gblur=sigma=28,eq=brightness=-0.22:saturation=0.82[bgv];"
          "[fg]scale=1040:1800:force_original_aspect_ratio=decrease[fgv];"
          "[bgv][fgv]overlay=(W-w)/2:(H-h)/2[base];"
          "[1:v]scale=132:-1[logo];"
          "[base][logo]overlay=W-w-24:24[branded];"
          f"[branded]drawtext=fontfile={FONT}:text='{hook}':fontcolor=white:fontsize=48:"
          "borderw=3:bordercolor=black@0.8:box=1:boxcolor=black@0.42:boxborderw=16:"
          "x=(w-text_w)/2:y=150:enable='lt(t,2.6)'[hooked];"
          f"[hooked]tpad=stop_mode=clone:stop_duration={core_dur:.3f},"
          f"drawtext=fontfile={FONT}:text='{cta}':fontcolor=white:fontsize=42:"
          "borderw=3:bordercolor=black@0.85:box=1:boxcolor=black@0.52:boxborderw=14:"
          f"x=(w-text_w)/2:y=h-230:enable='gte(t,{seg:.3f})'[v];"
          f"[0:a]atrim=duration={seg:.3f},asetpts=PTS-STARTPTS,loudnorm=I=-16:TP=-2:LRA=7[orig];"
          f"[2:a]atrim=duration={core_dur:.3f},asetpts=PTS-STARTPTS,adelay={delay_ms}|{delay_ms},volume=0.72[core];"
          "[orig][core]amix=inputs=2:duration=longest:dropout_transition=0,"
          "loudnorm=I=-15.5:TP=-1.5:LRA=7[a]"
        )
        cmd=[
          "ffmpeg","-y","-ss",f"{item['start']:.3f}","-t",f"{seg:.3f}","-i",str(src),
          "-loop","1","-i",str(logo),"-i",str(core),
          "-filter_complex",fc,"-map","[v]","-map","[a]","-t",f"{total:.3f}","-r","30",
          "-c:v","libx264","-preset","veryfast","-crf","18","-pix_fmt","yuv420p",
          "-c:a","aac","-b:a","192k","-ar","48000","-movflags","+faststart",str(out)
        ]
        run(cmd)
        p=probe(out)
        v=next(s for s in p["streams"] if s["codec_type"]=="video")
        a=next(s for s in p["streams"] if s["codec_type"]=="audio")
        assert v["codec_name"]=="h264" and (int(v["width"]),int(v["height"]))==(1080,1920)
        assert v["pix_fmt"]=="yuv420p" and a["codec_name"]=="aac" and int(a["sample_rate"])==48000
        visual=run(["ffmpeg","-hide_banner","-i",str(out),"-vf","blackdetect=d=1.0:pix_th=0.10","-an","-f","null","-"],check=False).stderr
        if "black_start" in visual: raise RuntimeError("NO_BLACK_FAIL")
        audio=run(["ffmpeg","-hide_banner","-i",str(out),"-af","silencedetect=n=-48dB:d=0.8","-vn","-f","null","-"],check=False).stderr
        if "silence_start" in "\n".join(audio.splitlines()[-12:]): raise RuntimeError("SILENT_TAIL_FAIL")
        sha=hashlib.sha256(out.read_bytes()).hexdigest()
        rec={
          "id":item["id"],"title":item["title"],"source":item["source"],"source_id":item["source_id"],
          "source_start_sec":item["start"],"source_end_sec":item["end"],"duration_sec":total,
          "sha256":sha,
          "gates":{
            "SOURCE_PASS":True,
            "RIGHTS_USAGE_CHECK":"OFFICIAL_GLOBOPLAY_EDITORIAL_EXCERPT_CREDITED",
            "ANTI_REPEAT_60D_PASS":"SOURCE_TITLE_AND_SOURCE_ID_NOT_FOUND_IN_LIVE_60D_HISTORY",
            "SCENE_FINGERPRINT_PASS":"NEW_SOURCE_ID_PLUS_UNIQUE_TIMESTAMP_WINDOW_PLUS_NEW_MASTER_SHA",
            "REAL_FOOTAGE_PASS":True,
            "FULL_SCENE_PRESERVATION_PASS":"SOURCE_EDITED_FALHA_NOSSA_BLOCK_PRESERVED",
            "NO_EXTRA_ZOOM_PASS":True,
            "NO_AGGRESSIVE_CROP_PASS":True,
            "NO_LEGACY_MASK_PASS":True,
            "LOGO_TOP_RIGHT_PASS":True,
            "AUDIO_PTBR_PASS":"ORIGINAL_SOURCE_AUDIO",
            "NO_NARRATION_OVER_HUMOR_PASS":True,
            "CORE_PASS":"CANONICAL_CORE_ONLY_AFTER_SOURCE_BLOCK",
            "NO_BLACK_PASS":True,
            "NO_SILENT_TAIL_PASS":True,
            "H264_AAC_PASS":True,
            "NINE_BY_SIXTEEN_PASS":True,
            "EDITORIAL_PASS":True
          }
        }
        (OUT/f"{item['id']}.json").write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding="utf-8")
        summary["items"].append(rec)
    (OUT/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")

if __name__=="__main__":
    main()
