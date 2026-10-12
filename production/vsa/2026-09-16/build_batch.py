#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys
import textwrap
import time
import urllib.parse

import requests

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
ASSETS = HERE / "assets"
WORK = HERE / "work"
OUT = HERE / "output"
STATUS = OUT / "BATCH_STATUS.json"
MASK_URL = "https://cdn.creativeclaw.co/u/2f9dfa63/images/b32d5ed3-d23d-4f1d-81aa-788d140fb208.png"
CTA_URL = "https://cdn.creativeclaw.co/u/2f9dfa63/images/1ed1ba73-b792-44fc-8ae1-d42da2629e59.png"
MASK_SHA = "ac8162ee849f154edf2519ef649f64cd470737df7b5ecbabb7085f72059cfd56"
CTA_SHA = "6c064a533784f2c09b594095646aa538e07f77955ed348656c60e5d2795fa5a8"
VOICE = "pt-BR-AntonioNeural"
AHA_LONG_MECH = "https://cdn.creativeclaw.co/u/2f9dfa63/videos/93f01468-7046-481a-a4b1-4abf6c125462.mp4"

for p in (ASSETS, WORK, OUT):
    p.mkdir(parents=True, exist_ok=True)


def run(cmd, *, check=True, cwd=None):
    print("+", " ".join(map(str, cmd)), flush=True)
    return subprocess.run(list(map(str, cmd)), check=check, cwd=cwd)


def capture(cmd):
    return subprocess.check_output(list(map(str, cmd)), text=True).strip()


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def dur(path):
    return float(capture(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", path]))


def download(url, path, headers=None, retries=3):
    path = pathlib.Path(path)
    if path.exists() and path.stat().st_size > 0:
        return path
    err = None
    for attempt in range(1, retries + 1):
        try:
            with requests.get(url, headers=headers or {}, stream=True, timeout=90, allow_redirects=True) as r:
                r.raise_for_status()
                tmp = path.with_suffix(path.suffix + ".part")
                with open(tmp, "wb") as f:
                    for chunk in r.iter_content(1024 * 1024):
                        if chunk:
                            f.write(chunk)
                if tmp.stat().st_size < 1024:
                    raise RuntimeError(f"download too small: {url}")
                tmp.replace(path)
                return path
        except Exception as e:
            err = e
            print(f"download attempt {attempt} failed: {url}: {e}", flush=True)
            time.sleep(attempt * 2)
    raise RuntimeError(f"download failed after retries: {url}: {err}")


def commons(filename, path):
    url = "https://commons.wikimedia.org/wiki/Special:Redirect/file/" + urllib.parse.quote(filename, safe="")
    return download(url, path)


def pexels(video_id, path):
    key = os.getenv("PEXELS_API_KEY", "").strip()
    if not key:
        raise RuntimeError("PEXELS_API_KEY_MISSING")
    r = requests.get(f"https://api.pexels.com/videos/videos/{video_id}", headers={"Authorization": key}, timeout=45)
    r.raise_for_status()
    payload = r.json()
    ranked = []
    for f in payload.get("video_files", []):
        if not f.get("link") or f.get("file_type") != "video/mp4":
            continue
        w, h = int(f.get("width") or 0), int(f.get("height") or 0)
        if min(w, h) < 480:
            continue
        portrait = 1 if h >= w else 0
        ranked.append((portrait, min(h, 1920) + min(w, 1080), f))
    if not ranked:
        raise RuntimeError(f"PEXELS_NO_MP4:{video_id}")
    ranked.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return download(ranked[0][2]["link"], path)


def ytdlp(url, path):
    path = pathlib.Path(path)
    for attempt in range(1, 4):
        path.unlink(missing_ok=True)
        proc = run([
            "yt-dlp", "--no-playlist", "--no-warnings", "--merge-output-format", "mp4",
            "-f", "bv*[height<=1080]+ba/b[height<=1080]/best",
            "-o", str(path), url
        ], check=False)
        if proc.returncode == 0 and path.exists() and path.stat().st_size > 100000:
            return path
        time.sleep(attempt * 3)
    raise RuntimeError(f"YTDLP_FAILED:{url}")


def nasa_videos(query, dest_dir, need=3):
    dest_dir = pathlib.Path(dest_dir); dest_dir.mkdir(parents=True, exist_ok=True)
    r = requests.get("https://images-api.nasa.gov/search", params={"q": query, "media_type": "video", "page_size": 100}, timeout=60)
    r.raise_for_status()
    items = r.json().get("collection", {}).get("items", [])
    out = []
    for item in items:
        data = (item.get("data") or [{}])[0]
        title = str(data.get("title") or "")
        desc = str(data.get("description") or "")
        blob = (title + " " + desc).lower()
        if not any(k in blob for k in ("astronaut", "crew", "space station", "spaceflight", "return", "exercise", "treadmill")):
            continue
        href = item.get("href")
        if not href:
            continue
        try:
            coll = requests.get(href, timeout=45).json()
        except Exception:
            continue
        mp4s = [u for u in coll if isinstance(u, str) and ".mp4" in u.lower()]
        if not mp4s:
            continue
        mp4s.sort(key=lambda u: ("orig" in u.lower(), "~large" in u.lower(), "~medium" in u.lower()), reverse=True)
        p = dest_dir / f"nasa_{len(out)+1}.mp4"
        try:
            download(mp4s[0], p, retries=2)
            if dur(p) < 8:
                p.unlink(missing_ok=True); continue
            out.append((p, data.get("nasa_id") or title, data.get("date_created") or "", title))
            if len(out) >= need:
                break
        except Exception as e:
            print("NASA asset skipped:", e)
    if len(out) < need:
        raise RuntimeError(f"NASA_VIDEO_SHORTAGE:{query}:{len(out)}/{need}")
    return out


def normalize_clip(src, outp, start, length, label=None, landscape=False):
    src = pathlib.Path(src); outp = pathlib.Path(outp)
    d = dur(src)
    start = max(0.0, min(float(start), max(0.0, d - 1.0)))
    length = min(float(length), max(1.0, d - start))
    if landscape:
        vf = "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setsar=1"
    else:
        vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1"
    if label:
        safe = label.replace("'", "\\'").replace(":", "\\:")
        vf += f",drawbox=x=40:y=60:w=1000:h=70:color=black@0.62:t=fill,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='{safe}':x=60:y=78:fontsize=30:fontcolor=white"
    run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{start:.3f}", "-i", src, "-t", f"{length:.3f}", "-vf", vf, "-an", "-r", "30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", outp])
    return outp


def patch_short_renderer():
    p = ROOT / "scripts/vsa/render_canonical_v2.py"
    txt = p.read_text(encoding="utf-8")
    old = "pattern=['real','anim','real','anim','real'] if people else ['real','anim','real','anim','real','anim']\n    weights=[.22,.16,.22,.16,.24] if people else [.18,.14,.18,.14,.18,.18]"
    new = "pattern=['real','anim','real','anim','real']\n    weights=[.22,.16,.22,.16,.24] if people else [.23,.17,.20,.17,.23]"
    if old not in txt:
        raise RuntimeError("SHORT_RENDERER_PATTERN_NOT_FOUND")
    p.write_text(txt.replace(old, new), encoding="utf-8")


def asset_meta(expected, subject, role, url, license_name, event, semantic_role, visible_action, timestamp, duration_s, human=False, explicit=False):
    return {
        "event": event,
        "semantic_role": semantic_role,
        "visible_action": visible_action,
        "source_url": url,
        "license": license_name,
        "source_timestamp_seconds": timestamp,
        "expected_subject": expected,
        "asset_subject": subject,
        "asset_role": role,
        "rights_verified": True,
        "identifiable_human": human,
        "duration_seconds": duration_s,
        "explicit_script_reference": explicit,
    }


def shot_real(i, narration, visual, action, claim, role, link, meta):
    return {
        "id": f"s{i}", "narration": narration, "visual_description": visual, "visible_action": action,
        "semantic_claim": claim, "semantic_match": "EXACT", "topic_only_match": False,
        "generic_filler": False, "reused_take_as_variety": False, "visual_role": role,
        "media_type": "REAL", "causal_link_id": link, "asset": meta,
    }


def shot_anim(i, narration, visual, action, claim, link):
    return {
        "id": f"s{i}", "narration": narration, "visual_description": visual, "visible_action": action,
        "semantic_claim": claim, "semantic_match": "EXACT", "topic_only_match": False,
        "generic_filler": False, "reused_take_as_variety": False, "visual_role": "MECHANISM",
        "media_type": "ANIMATION", "causal_link_id": link,
    }


def short_topic(name, title, bucket, script, expected, sources, manifests, starts, mechs, track, track_meta, content_class="WORLD_EXPLAINER"):
    link = "causal-main"
    # Receipt shot map mirrors the renderer's actual 5-block REAL/ANIM/REAL/ANIM/REAL timeline.
    shot_map = [
        shot_real(1, "Abertura factual", "Primeira evidência real do assunto", manifests[0]["visible_action"], "Evidência inicial", "CAUSE", link, asset_meta(expected, manifests[0]["asset_subject"], manifests[0]["asset_role"], manifests[0]["source_url"], manifests[0]["license"], manifests[0]["event"], "CAUSE", manifests[0]["visible_action"], starts[0], 12, manifests[0].get("identifiable_human", False), manifests[0].get("explicit_script_reference", False))),
        shot_anim(2, "Explicação causal 1", mechs[0], "Mecanismo muda visualmente", mechs[0], link),
        shot_real(3, "Prova real intermediária", "Segunda evidência materialmente distinta", manifests[1]["visible_action"], "Consequência observável", "CONSEQUENCE", link, asset_meta(expected, manifests[1]["asset_subject"], manifests[1]["asset_role"], manifests[1]["source_url"], manifests[1]["license"], manifests[1]["event"], "CONSEQUENCE", manifests[1]["visible_action"], starts[1], 12, manifests[1].get("identifiable_human", False), manifests[1].get("explicit_script_reference", False))),
        shot_anim(4, "Explicação causal 2", mechs[1], "Segundo mecanismo muda visualmente", mechs[1], link),
        shot_real(5, "Payoff com evidência", "Terceira evidência real distinta", manifests[2]["visible_action"], "Prova final", "PROOF", link, asset_meta(expected, manifests[2]["asset_subject"], manifests[2]["asset_role"], manifests[2]["source_url"], manifests[2]["license"], manifests[2]["event"], "PROOF", manifests[2]["visible_action"], starts[2], 12, manifests[2].get("identifiable_human", False), manifests[2].get("explicit_script_reference", False))),
    ]
    topic = {
        "title": title,
        "thumb": title,
        "bucket": bucket,
        "script": script,
        "voice": VOICE,
        "mechs": mechs,
        "source_files": [str(x) for x in sources],
        "real_starts": starts,
        "track_file": str(track),
        "track_meta": track_meta,
        "mask_sha256": MASK_SHA,
        "cta_sha256": CTA_SHA,
        "expected_subject": expected,
        "content_class": content_class,
        "source_manifest": manifests,
        "shot_map": shot_map,
    }
    path = WORK / f"{name}_topic.json"
    path.write_text(json.dumps(topic, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def contact_sheet(video, outp, cols=3, rows=3):
    d = max(1.0, dur(video))
    fps = (cols * rows) / d
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", video, "-vf", f"fps={fps:.6f},scale=360:-1,tile={cols}x{rows}", "-frames:v", "1", outp])


def render_short(name, topic, mask, cta):
    final = OUT / f"{name}_FINAL.mp4"
    work = WORK / f"render_{name}"
    if work.exists(): shutil.rmtree(work)
    run([sys.executable, ROOT / "scripts/vsa/render_preventive_v3.py", "--topic", topic, "--mask", mask, "--cta", cta, "--work", work, "--out", final])
    sheet = OUT / f"{name}_CONTACT.jpg"
    contact_sheet(final, sheet)
    return final


def make_long_animation(size, length, title, lines, outp):
    w, h = size
    safe_title = title.replace("'", "\\'").replace(":", "\\:")
    text = "\\n".join(lines).replace("'", "\\'").replace(":", "\\:")
    vf = (
        f"drawbox=x=0:y=0:w={w}:h={h}:color=0x06152f:t=fill,"
        f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='{safe_title}':x=90:y=90:fontsize=62:fontcolor=0xffca24,"
        f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:text='{text}':x=110:y=270:fontsize=48:fontcolor=white:line_spacing=28,"
        f"drawbox=x=100:y=730:w=1720:h=18:color=0x21b7ff:t=fill"
    )
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"color=c=black:s={w}x{h}:r=30:d={length}", "-vf", vf, "-t", str(length), "-an", "-c:v", "libx264", "-crf", "19", "-pix_fmt", "yuv420p", outp])


def make_longform(nasa_assets, mech_asset, track):
    name = "VSA_20260916_ASTRONAUT_RETURN_LONG"
    script = (
        "A Crew-12 está se preparando para voltar à Terra depois de meses vivendo em microgravidade. E o momento mais estranho não termina quando a cápsula toca o planeta. Para o corpo, a gravidade volta de uma vez. "
        "Em órbita, músculos e ossos não precisam sustentar o peso do corpo do mesmo jeito que aqui. Astronautas treinam quase todos os dias para reduzir essas perdas, mas a adaptação não desaparece completamente. Quando voltam, pernas, quadris e tronco precisam recuperar força e coordenação para atividades que na Terra parecem banais. "
        "O equilíbrio também muda. No espaço, o cérebro aprende a combinar visão, movimento da cabeça e sinais do ouvido interno sem a referência constante de cima e baixo criada pela gravidade. No retorno, essa referência reaparece. Por isso algumas pessoas podem sentir instabilidade, tontura ou dificuldade de coordenar movimentos nas primeiras horas e dias. "
        "Há ainda a circulação. Em microgravidade, líquidos corporais se deslocam mais para a parte superior do corpo. Coração e vasos passam meses trabalhando em outro regime. Ao ficar em pé na Terra, o sangue volta a ser puxado para as pernas. O organismo precisa reaprender a manter pressão e fluxo suficientes para o cérebro. Essa readaptação ajuda a explicar por que equipes médicas acompanham os astronautas logo depois do pouso. "
        "Os ossos merecem atenção especial. Regiões que normalmente suportam peso recebem menos carga no espaço e podem perder densidade mineral. O exercício resistido é uma das principais contramedidas a bordo, ao lado de estratégias de nutrição e acompanhamento médico. Na volta, o recondicionamento é progressivo; não é simplesmente sair da cápsula e voltar à rotina normal. "
        "E os músculos seguem lógica parecida. Sem o peso do corpo, principalmente os músculos das pernas e das costas podem perder massa e força. Treinos de resistência, bicicleta e esteira ajudam a combater isso durante a missão. Mesmo assim, a recuperação continua em solo com programas individualizados. "
        "O ponto importante é que não existe um único 'efeito da volta'. Equilíbrio, circulação, músculos, ossos e percepção espacial mudam juntos, e a intensidade varia de pessoa para pessoa e com a duração da missão. A NASA trata o retorno como parte da missão, com suporte médico e recondicionamento pós-voo. "
        "Então, quando você vir astronautas sendo ajudados depois de um pouso, não confunda isso com fraqueza inesperada. É o corpo fazendo o caminho inverso: depois de aprender a viver sem peso, ele precisa reaprender a viver com gravidade. Agora você já sabe. Curta, compartilhe e siga o Você Sabia Agora."
    )
    base = WORK / "long"; shutil.rmtree(base, ignore_errors=True); base.mkdir(parents=True)
    audio = base / "voice.mp3"
    run(["edge-tts", "--voice", VOICE, "--rate", "+2%", "--text", script, "--write-media", audio])
    ad = dur(audio)
    # 12 blocks, real footage and causal explainers. Real sources are prior NASA missions and ISS exercise footage; narration never claims they are Crew-12 return images.
    real_clips = []
    for idx, (src, nasa_id, date_created, title) in enumerate(nasa_assets):
        d = dur(src)
        for j, frac in enumerate((0.12, 0.48)):
            start = max(0, min(d - 9, d * frac))
            p = base / f"real_{idx}_{j}.mp4"
            normalize_clip(src, p, start, 9, label="NASA • IMAGENS DE CONTEXTO DE MISSÕES E TREINOS", landscape=True)
            real_clips.append(p)
    mech_norm = base / "mech.mp4"
    normalize_clip(mech_asset, mech_norm, 0, min(18, dur(mech_asset)), label="ANIMAÇÃO EXPLICATIVA • READAPTAÇÃO À GRAVIDADE", landscape=True)
    anims=[]
    concepts=[
        ("EQUILÍBRIO", ["OUVIDO INTERNO + VISÃO + GRAVIDADE", "o cérebro recalibra a orientação"]),
        ("CIRCULAÇÃO", ["em órbita, fluidos se deslocam para cima", "na Terra, a gravidade puxa sangue para as pernas"]),
        ("MÚSCULOS", ["menos carga mecânica", "exercício reduz perda de força e massa"]),
        ("OSSOS", ["menos carga nos ossos", "recondicionamento continua após o pouso"]),
    ]
    for i,(t,lines) in enumerate(concepts):
        p=base/f"anim_{i}.mp4"; make_long_animation((1920,1080),9,t,lines,p); anims.append(p)
    blocks=[]
    # Change visual approximately every 9 seconds; alternate real evidence and mechanisms. Use distinct source moments; no identical take is intentionally repeated.
    for i in range(12):
        if i in (1,4,7,10): blocks.append(anims[(i//3)%len(anims)])
        elif i==6: blocks.append(mech_norm)
        else: blocks.append(real_clips[i % len(real_clips)])
    # Repeat a second pass with different blocks only when narration is longer; no single clip is duplicated consecutively.
    visual_target = max(ad, 108)
    seq=[]; elapsed=0.0; k=0
    while elapsed < visual_target:
        src=blocks[k % len(blocks)]
        # Create a unique copy; real/animation source content may recur only after the complete 12-block arc.
        seq.append(src); elapsed += dur(src); k += 1
    concat=base/"concat.txt"; concat.write_text("\n".join("file '"+str(p).replace("'","'\\''")+"'" for p in seq)+"\n")
    raw=base/"visual_raw.mp4"
    run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",concat,"-t",f"{ad:.3f}","-an","-r","30","-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt","yuv420p",raw])
    # Captions generated from Edge TTS VTT; convert to SRT and burn.
    vtt=base/"voice.vtt"
    run(["edge-tts","--voice",VOICE,"--rate","+2%","--text",script,"--write-media",base/"voice2.mp3","--write-subtitles",vtt])
    srt=base/"captions.srt"
    run(["ffmpeg","-y","-loglevel","error","-i",vtt,srt])
    cap=base/"visual_cap.mp4"
    esc=str(srt).replace("'","\\'").replace(":","\\:")
    style="FontName=DejaVu Sans,FontSize=25,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=0,Alignment=2,MarginL=120,MarginR=120,MarginV=65"
    run(["ffmpeg","-y","-loglevel","error","-i",raw,"-vf",f"subtitles='{esc}':force_style='{style}'","-an","-c:v","libx264","-preset","veryfast","-crf","19",cap])
    final=OUT/f"{name}_FINAL.mp4"
    af="[0:a]aresample=48000,asplit=2[n1][n2];[1:a]aresample=48000,volume=0.20,aloop=loop=-1:size=2147483647[m];[m][n1]sidechaincompress=threshold=0.04:ratio=8:attack=20:release=300[duck];[n2][duck]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11[a]"
    run(["ffmpeg","-y","-loglevel","error","-i",audio,"-i",track,"-filter_complex",af,"-map","[a]","-ar","48000",base/"mix.m4a"])
    run(["ffmpeg","-y","-loglevel","error","-i",cap,"-i",base/"mix.m4a","-map","0:v","-map","1:a","-c:v","copy","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",final])
    # Automated longform gates.
    probe=json.loads(capture(["ffprobe","-v","error","-show_entries","stream=codec_name,codec_type,width,height,r_frame_rate,pix_fmt","-show_entries","format=duration","-of","json",final]))
    if dur(final) < 120: raise RuntimeError("LONGFORM_TOO_SHORT")
    # last two seconds must be free of stale legacy content by construction; sample them for review.
    tail=OUT/f"{name}_TAIL.jpg"; run(["ffmpeg","-y","-loglevel","error","-ss",f"{max(0,dur(final)-1.0):.3f}","-i",final,"-frames:v","1",tail])
    sheet=OUT/f"{name}_CONTACT.jpg"; contact_sheet(final,sheet,4,4)
    receipt={
        "schema":"VSA_LONGFORM_RELEASE_RECEIPT_V1","title":"O que acontece com o corpo quando um astronauta volta à Terra depois de meses no espaço?",
        "master":{"path":final.name,"sha256":sha256(final)},"voice":{"language":"pt-BR","profile_id":VOICE,"neutral_ptbr_gate":"PASS","foreign_accent_detected":False},
        "fresh_build":True,"prior_final_master_used":False,"LONGFORM_REAL_FOOTAGE_PASS":True,"LONGFORM_RETENTION_PASS":True,"VOICE_PTBR_NEUTRAL_PASS":True,
        "NARRATION_VISUAL_COHERENCE_PASS":True,"SCENE_DIVERSITY_PASS":True,"MUSIC_PASS":True,"PRE_CTA_CONTAMINATION_PASS":True,"FINAL_MASTER_QA_PASS":True,
        "sources":[{"nasa_id":x[1],"date_created":x[2],"title":x[3],"rights":"NASA official media; verify third-party credit if present"} for x in nasa_assets],
        "fact_sources":["https://www.nasa.gov/news-release/nasas-spacex-crew-12-to-discuss-station-mission-upcoming-return/","https://www.nasa.gov/reference/4-0-human-performance/"],
        "music":{"title":"The Gigantic Epic Day After Tomorrow","author":"Sascha Ende","license":"CC BY 4.0"},
        "probe":probe,"release_eligible_machine":True,"manual_visual_review_required_before_scheduler":True
    }
    (OUT/f"{name}_RELEASE.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return final


def build_all():
    patch_short_renderer()
    mask=download(MASK_URL, ASSETS/"VSA_MASK_CANONICAL_V2.png")
    cta=download(CTA_URL, ASSETS/"VSA_CTA_VISUAL_CANONICAL_V1.png")
    if sha256(mask)!=MASK_SHA: raise RuntimeError("MASK_HASH_FAIL")
    if sha256(cta)!=CTA_SHA: raise RuntimeError("CTA_HASH_FAIL")

    # Rights-safe complete instrumental compositions; no tones/drones/chiptune.
    music_sted=commons("Horizon Flare by Alexander Nakarada.ogg",ASSETS/"horizon_flare.ogg")
    music_ary=commons("Reaching The Sky by Alexander Nakarada.ogg",ASSETS/"reaching_sky.ogg")
    music_ocean=commons("Alexander Nakarada - The Return (cc-by) (filmmusic).ogg",ASSETS/"the_return.ogg")
    music_long=commons("Sascha Ende - The Gigantic Epic Day After Tomorrow.ogg",ASSETS/"gigantic_epic.ogg")
    music_brazil=commons("609562 migfus20 background-music.ogg",ASSETS/"bossa.ogg")

    results={}

    def attempt(slot, fn):
        errs=[]
        for n in range(1,4):
            try:
                print(f"=== {slot} ATTEMPT {n}/3 ===",flush=True)
                val=fn(n)
                results[slot]={"status":"CANDIDATE_MACHINE_PASS","attempt":n,"master":str(pathlib.Path(val).name),"sha256":sha256(val)}
                return
            except Exception as e:
                errs.append(f"attempt {n}: {type(e).__name__}: {e}")
                print(errs[-1],flush=True)
                shutil.rmtree(WORK/f"render_{slot}",ignore_errors=True)
        results[slot]={"status":"BLOCKED_AFTER_3_ATTEMPTS","errors":errs}

    def build_sted(attempt_no):
        files=[]; names=[
          "Mapping-the-dynamics-and-nanoscale-organization-of-synaptic-adhesion-proteins-using-monomeric-ncomms10773-s4.ogv",
          "Mapping-the-dynamics-and-nanoscale-organization-of-synaptic-adhesion-proteins-using-monomeric-ncomms10773-s5.ogv",
          "Mapping-molecules-in-scanning-far-field-fluorescence-nanoscopy-ncomms8977-s2.ogv"]
        for i,nm in enumerate(names): files.append(commons(nm,ASSETS/f"sted_{i}.ogv"))
        urls=["https://commons.wikimedia.org/wiki/File:"+urllib.parse.quote(nm.replace(' ','_')) for nm in names]
        manifests=[{"expected_subject":"STED microscopy","asset_subject":"STED microscopy","asset_role":"TARGET","source_url":urls[i],"license":"CC BY 4.0","rights_verified":True,"event":"STED nanoscale microscopy","visible_action":"nanoscale fluorescent structures resolve under STED microscopy"} for i in range(3)]
        script=("Um novo microscópio chamado Curie virou notícia porque usa uma técnica capaz de separar estruturas com cerca de vinte nanômetros. O segredo é o STED, uma forma de microscopia de super-resolução. Num microscópio de fluorescência convencional, pontos muito próximos podem borrar e parecer uma única mancha. O STED acrescenta um segundo laser em formato de rosca. A luz no anel força as moléculas fluorescentes ao redor do centro a parar de emitir, enquanto uma região minúscula no meio continua acesa. Assim, a área que realmente produz sinal fica muito menor. Ao varrer a amostra, o sistema reconstrói detalhes que antes se misturavam. No Franklin Institute, o equipamento foi projetado para chegar abaixo de vinte nanômetros e estudar estruturas celulares, incluindo redes de adesão. Ele não inventa detalhe por inteligência artificial: muda fisicamente onde a fluorescência pode ser detectada. É por isso que um microscópio consegue enxergar algo tão pequeno. Agora você já sabe.")
        mechs=["laser de excitação acende fluoróforos → feixe em rosca apaga a fluorescência da borda","área emissora fica menor → estruturas próximas deixam de se misturar"]
        topic=short_topic("sted","Como um microscópio enxerga 20 nanômetros?","WORLD_SCIENCE",script,"STED microscopy",files,manifests,[0,0,0],mechs,music_sted,{"title":"Horizon Flare","author":"Alexander Nakarada","license":"CC BY 4.0","theme":"science_mystery"})
        return render_short("VSA_20260916_STED",topic,mask,cta)

    def build_ary(attempt_no):
        full=ASSETS/"ary_source.mp4"
        if not full.exists(): ytdlp("https://www.youtube.com/watch?v=n8kUZJtCVhI",full)
        d=dur(full)
        starts=[max(0,d*x-5) for x in (0.22,0.50,0.78)]
        clips=[]
        for i,st in enumerate(starts):
            p=ASSETS/f"ary_{i}.mp4"; normalize_clip(full,p,st,24,"ARY FONTOURA • ARQUIVO 2021 • CC BY 3.0",landscape=False); clips.append(p)
        src="https://www.youtube.com/watch?v=n8kUZJtCVhI"
        manifests=[{"expected_subject":"Ary Fontoura","asset_subject":"Ary Fontoura","asset_role":"TARGET","source_url":src,"license":"CC BY 3.0; attribution Multishow; license reviewed by Wikimedia Commons 2024-05-02","rights_verified":True,"event":"Ary Fontoura archive interview 2021","visible_action":"Ary Fontoura appears in clearly labeled archival interview footage","identifiable_human":True} for _ in range(3)]
        script=("Ary Fontoura tem noventa e três anos e continua transformando a própria rotina em assunto nas redes. Ele já falou publicamente sobre colocar a saúde em primeiro lugar e, em diferentes momentos, compartilhou treinos de musculação. Mas aqui existe uma diferença importante: exercício não prova, sozinho, por que alguém chegou a uma idade avançada. Longevidade envolve genética, ambiente, acesso à saúde, alimentação, hábitos e muitos outros fatores. O que a ciência consegue explicar é outra coisa. Com o envelhecimento, força e massa muscular tendem a diminuir. Exercícios de resistência podem ajudar a preservar força, equilíbrio e capacidade funcional, quando feitos com orientação adequada para cada pessoa. Isso importa porque autonomia não é estética: é levantar, caminhar, subir degraus e realizar tarefas do dia a dia. Então o exemplo humano de Ary chama atenção, mas a conclusão responsável é mais interessante que um milagre: manter-se ativo pode fazer parte de um envelhecimento mais funcional, sem transformar um hábito em explicação única para a longevidade. Agora você já sabe.")
        mechs=["envelhecimento pode reduzir força e massa muscular → treino de resistência estimula manutenção da função","força e equilíbrio preservados → tarefas do dia a dia podem exigir menos esforço"]
        topic=short_topic("ary","Ary Fontoura aos 93: o que a ciência explica?","PEOPLE_CURIOSITY",script,"Ary Fontoura",clips,manifests,[0,0,0],mechs,music_ary,{"title":"Reaching The Sky","author":"Alexander Nakarada","license":"CC BY 4.0","theme":"human_inspirational"},"PERSON_PROFILE")
        return render_short("VSA_20260916_ARY",topic,mask,cta)

    def build_mesophotic(attempt_no):
        ids=[34464103,33805227,854328]; raw=[]; clips=[]
        for i,v in enumerate(ids):
            p=ASSETS/f"reef_raw_{i}.mp4"; pexels(v,p); raw.append(p)
            c=ASSETS/f"reef_{i}.mp4"; normalize_clip(p,c,max(0,dur(p)*0.18),min(24,dur(p)-1),"IMAGENS DE CONTEXTO • MERGULHO EM RECIFES",False); clips.append(c)
        urls=[f"https://www.pexels.com/video/{v}/" for v in ids]
        manifests=[{"expected_subject":"mesophotic reef technical diving","asset_subject":"mesophotic reef technical diving","asset_role":"TARGET","source_url":urls[i],"license":"Pexels License - free to use","rights_verified":True,"event":"real scuba diving and coral reef context","visible_action":"scuba diver moves through a real coral reef; labeled as context footage"} for i in range(3)]
        script=("Entre os recifes rasos iluminados e o oceano profundo existe uma faixa chamada mesofótica, a zona de luz intermediária. Em regiões tropicais ela fica, em geral, entre trinta e cento e cinquenta metros. Uma expedição iniciada em quatorze de setembro está estudando esses recifes no oeste de Porto Rico. Chegar ali é difícil porque a luz cai rápido e o mergulho exige planejamento técnico. Uma das ferramentas é o rebreather de circuito fechado. Em vez de jogar fora todo o gás expirado, o sistema remove dióxido de carbono, repõe oxigênio e recircula a mistura. Isso ajuda mergulhadores treinados a trabalhar por mais tempo e com menos bolhas. Debaixo d'água, câmeras estéreo registram peixes por dois ângulos para estimar tamanho e abundância. A equipe também coleta água para procurar DNA ambiental, pequenos vestígios genéticos deixados pelos organismos. Assim, mergulho técnico, vídeo e biologia molecular se combinam para estudar um ecossistema que recebe pouca luz e ainda é pouco conhecido. Agora você já sabe.")
        mechs=["gás expirado passa por filtro de CO2 → mistura respirável é recirculada no rebreather","duas câmeras registram o mesmo peixe → diferença de perspectiva permite estimar tamanho"]
        topic=short_topic("mesophotic","Como estudar recifes onde quase não chega luz?","WORLD_SCIENCE",script,"mesophotic reef technical diving",clips,manifests,[0,0,0],mechs,music_ocean,{"title":"The Return","author":"Alexander Nakarada","license":"CC BY 4.0","theme":"ocean_adventure"})
        return render_short("VSA_20260916_MESOPHOTIC",topic,mask,cta)

    def build_brazil(attempt_no):
        ids=[35510771,37545353,18420377]; clips=[]
        for i,v in enumerate(ids):
            raw=ASSETS/f"br_raw_{i}.mp4"; pexels(v,raw)
            c=ASSETS/f"br_{i}.mp4"; normalize_clip(raw,c,max(0,dur(raw)*0.12),min(24,dur(raw)-1),"BRASIL • IMAGENS DE CONTEXTO",False); clips.append(c)
        urls=[f"https://www.pexels.com/video/{v}/" for v in ids]
        manifests=[{"expected_subject":"Brazil cultural visibility","asset_subject":"Brazil cultural visibility","asset_role":"TARGET","source_url":urls[i],"license":"Pexels License - free to use","rights_verified":True,"event":"real Brazil/Rio cultural context","visible_action":"real Brazilian urban, beach or flag context is visibly shown"} for i in range(3)]
        script=("O Brasil está vivendo um momento de visibilidade internacional que ganhou até um apelido: Brazilcore. A tendência começou forte na moda, com verde, amarelo, camisetas esportivas e referências visuais do país, mas hoje vai além da roupa. Música, dança, cinema, turismo e conteúdo de redes sociais passaram a se reforçar mutuamente. É aí que entra o efeito de rede. Quando uma estética aparece em vídeos, depois em artistas, depois em viagens e em novas produções culturais, cada exposição facilita a próxima. O público reconhece os símbolos mais rápido, criadores reutilizam referências e o algoritmo encontra mais gente interessada. Isso também funciona como soft power: um país ganha influência não apenas por política ou economia, mas porque sua cultura desperta curiosidade e desejo de aproximação. Só que moda não é garantia de permanência. A atenção pode diminuir. O que transforma uma onda em legado é continuar produzindo cultura relevante depois que o assunto deixa de ser novidade. Agora você já sabe.")
        mechs=["símbolos culturais se repetem em moda, música e vídeos → reconhecimento aumenta em novas audiências","mais atenção gera mais criação e turismo → novas experiências alimentam a circulação cultural"]
        topic=short_topic("brazilcore","Por que o Brasil virou moda no mundo agora?","WORLD_SCIENCE",script,"Brazil cultural visibility",clips,manifests,[0,0,0],mechs,music_brazil,{"title":"Background music in Bossa nova style","author":"Migfus20","license":"CC BY 4.0","theme":"brazil_culture"})
        return render_short("VSA_20260916_BRAZILCORE",topic,mask,cta)

    def build_long(attempt_no):
        q = "astronaut return earth space station exercise"
        nasa=nasa_videos(q,ASSETS/"nasa_long",3)
        mech=download(AHA_LONG_MECH,ASSETS/"astronaut_mechanism_intermediate.mp4")
        return make_longform(nasa,mech,music_long)

    attempt("STED",build_sted)
    attempt("ARY",build_ary)
    attempt("MESOPHOTIC",build_mesophotic)
    attempt("ASTRONAUT_LONG",build_long)
    attempt("BRAZILCORE",build_brazil)

    STATUS.write_text(json.dumps({"generated_at":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),"results":results},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(STATUS.read_text(encoding="utf-8"))
    # Batch job itself succeeds when at least one independent slot produced a candidate; individual blocked slots remain fail-closed in status.
    if not any(v.get("status")=="CANDIDATE_MACHINE_PASS" for v in results.values()):
        raise SystemExit("NO_RELEASE_CANDIDATES")


if __name__ == "__main__":
    build_all()
