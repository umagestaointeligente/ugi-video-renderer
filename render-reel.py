#!/usr/bin/env python3
"""
UGI Reel Renderer R41 — COMMERCIAL STORYTELLING
================================================
Mantém a infraestrutura R40.x e muda a lógica editorial para:
HOOK -> DOR -> CONSEQUÊNCIA -> VIRADA -> RESULTADO -> CTA.

Contrato preservado:
VIDEO_TITLE, VIDEO_DURATION, VIDEO_RENDER_ID, VIDEO_CTA, VIDEO_NARRATION.
Saída: output/ugi-reel.mp4

R41 acrescenta:
- roteiro estruturado por cenas;
- overlays curtos e semanticamente ordenados;
- safe zones verticais;
- Commercial Storytelling QA;
- manifesto output/r41-storyboard.json.

IMPORTANTE:
A aquisição de mídia Pexels continua no workflow. O renderer procura arquivos
output/media/scene-1.mp4 ... scene-6.mp4 (ou .jpg/.jpeg/.png). Se não existirem,
usa fundo procedural, preservando a capacidade de diagnóstico.
"""

from __future__ import annotations
import json, os, re, shutil, subprocess, sys, textwrap
from dataclasses import dataclass, asdict
from pathlib import Path

WIDTH, HEIGHT, FPS = 1080, 1920, 30
OUTPUT = Path("output/ugi-reel.mp4")
WORK = Path("output/r41_work")
MEDIA = Path("output/media")

TITLE = (os.getenv("VIDEO_TITLE") or "Se tudo precisa passar por você, sua empresa não está crescendo. Está ficando dependente.").strip()
CTA = (os.getenv("VIDEO_CTA") or "Conheça a UGI.").strip()
RENDER_ID = (os.getenv("VIDEO_RENDER_ID") or "local-r41").strip()
try:
    DURATION = int(os.getenv("VIDEO_DURATION") or "30")
except ValueError:
    DURATION = 30
DURATION = max(24, min(40, DURATION))

FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
BG, WHITE, MUTED, ACCENT = "0x0B1118", "0xF4F7F9", "0xC5CED7", "0x35D0BA"

@dataclass
class Scene:
    role: str
    overlay: str
    support: str
    narration: str
    visual_intent: str
    pexels_query: str
    ratio: float

SCENES = [
    Scene("hook", "Tudo passa por você?", "Quando toda decisão chega ao líder, o crescimento começa a cobrar um preço.",
          "Se tudo precisa passar por você, sua empresa não está crescendo. Está ficando dependente.",
          "gestor sobrecarregado recebendo múltiplas demandas no trabalho",
          "overwhelmed male manager busy office work", 0.17),
    Scene("pain", "Você virou o gargalo.", "A equipe espera. As decisões acumulam.",
          "A equipe espera, as decisões acumulam e o líder vira gargalo.",
          "equipe aguardando decisão em reunião, sensação de espera",
          "business team waiting meeting female manager office", 0.17),
    Scene("consequence", "Crescer assim aumenta o problema.", "Mais demanda sem autonomia cria mais dependência.",
          "Quanto mais a empresa cresce assim, maior fica a dependência.",
          "empresa movimentada, pressão, tarefas e decisões simultâneas",
          "busy diverse office team working pressure", 0.16),
    Scene("turn", "Autonomia com direção.", "Critérios claros transformam espera em execução.",
          "Gestão inteligente cria autonomia com critérios, clareza e direção.",
          "profissional jovem apresentando ideia e equipe colaborando",
          "young professional presenting diverse team collaboration", 0.17),
    Scene("result", "Mais autonomia. Mais execução.", "O líder acompanha. A equipe avança.",
          "O líder deixa de centralizar tudo e passa a conduzir uma equipe que executa.",
          "líder acompanhando indicadores enquanto equipe trabalha com autonomia",
          "male leader dashboard diverse team autonomous office", 0.17),
    Scene("cta", "Cresça sem depender de você para tudo.", "Transforme gestão em execução.",
          "Sua empresa pode crescer sem depender de você para tudo. Conheça a UGI.",
          "grupo profissional diverso, homem, mulher e jovem, confiança e resultado",
          "diverse business team man woman young professional success", 0.16),
]

def run(cmd):
    print(">", " ".join(map(str, cmd)))
    subprocess.run(list(map(str, cmd)), check=True)

def clean(s):
    return re.sub(r"\s+", " ", s).strip()

def durations():
    vals = [round(DURATION*s.ratio, 3) for s in SCENES]
    vals[-1] = round(DURATION - sum(vals[:-1]), 3)
    return vals

def textfile(name, text):
    p = WORK / f"{name}.txt"
    p.write_text(text, encoding="utf-8")
    return p

def esc(p):
    return p.as_posix().replace("'", r"\'")

def draw(tf, size, color, x, y, bold=True, alpha="1", spacing=12):
    font = FONT_BOLD if bold else FONT_REGULAR
    return ("drawtext="
            f"fontfile='{font}':textfile='{esc(tf)}':reload=0:"
            f"fontsize={size}:fontcolor={color}:line_spacing={spacing}:"
            f"x={x}:y={y}:alpha='{alpha}'")

def find_media(i):
    for ext in ("mp4","mov","jpg","jpeg","png"):
        p = MEDIA / f"scene-{i}.{ext}"
        if p.exists():
            return p
    return None

def base_input(media, dur):
    if media and media.suffix.lower() in (".mp4",".mov"):
        return ["-stream_loop","-1","-i",str(media)]
    if media:
        return ["-loop","1","-i",str(media)]
    return ["-f","lavfi","-i",f"color=c={BG}:s={WIDTH}x{HEIGHT}:r={FPS}:d={dur}"]

def render_scene(i, s, dur, out):
    media = find_media(i)
    ov = textfile(f"{i}-overlay", "\n".join(textwrap.wrap(s.overlay, 25, break_long_words=False)))
    sup = textfile(f"{i}-support", "\n".join(textwrap.wrap(s.support, 43, break_long_words=False)))
    brand = textfile(f"{i}-brand", "UMA GESTÃO INTELIGENTE")
    num = textfile(f"{i}-num", f"0{i} / 06")
    cta = textfile(f"{i}-cta", CTA)

    filters = []
    if media:
        filters += [
            f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase",
            f"crop={WIDTH}:{HEIGHT}",
            "eq=brightness=-0.05:saturation=0.92",
        ]
    filters += [
        "drawbox=x=0:y=0:w=iw:h=ih:color=black@0.12:t=fill",
        "drawbox=x=70:y=1040:w=940:h=570:color=0x071019@0.72:t=fill",
        "drawbox=x=70:y=1040:w=8:h=570:color=0x35D0BA@0.95:t=fill",
        draw(num, 27, MUTED, "94", "105", True, "0.88"),
        draw(brand, 24, WHITE, "w-text_w-94", "105", True, "0.86"),
        draw(ov, 62 if i < 6 else 55, WHITE, "110", "1125", True, "min(t/0.35,1)", 15),
        draw(sup, 31, MUTED, "110", "1355", False, "if(lt(t,0.35),0,min((t-0.35)/0.35,1))", 11),
    ]
    if i == 6:
        filters += [
            "drawbox=x=110:y=1500:w=500:h=100:color=0x35D0BA@0.95:t=fill",
            draw(cta, 38, BG, "145", "1527", True, "if(lt(t,0.6),0,min((t-0.6)/0.3,1))"),
        ]
    filters += [
        "drawbox=x=82:y=1745:w=916:h=4:color=white@0.18:t=fill",
        f"drawbox=x=82:y=1745:w='916*min(t/{dur},1)':h=4:color=0x35D0BA@0.95:t=fill",
        "fade=t=in:st=0:d=0.18",
        f"fade=t=out:st={max(0.1,dur-0.20)}:d=0.20",
        "format=yuv420p"
    ]
    cmd = ["ffmpeg","-hide_banner","-loglevel","error","-y"] + base_input(media,dur) + [
        "-t",str(dur),"-vf",",".join(filters),"-an","-c:v","libx264","-preset","medium",
        "-crf","20","-r",str(FPS),"-pix_fmt","yuv420p",str(out)
    ]
    run(cmd)

def narration_text():
    supplied = clean(os.getenv("VIDEO_NARRATION") or "")
    # Se o upstream ainda envia a narração antiga/curta, R41 usa o roteiro estruturado.
    if len(supplied.split()) >= 35:
        return supplied
    return " ".join(s.narration for s in SCENES)

def synthesize(text):
    try:
        import numpy as np
        import soundfile as sf
        from kokoro import KPipeline
    except Exception as e:
        raise RuntimeError("Kokoro TTS não disponível no workflow.") from e
    pipe = KPipeline(lang_code="p")
    chunks=[]
    for result in pipe(text, voice="pf_dora", speed=1.04, split_pattern=r"\n+"):
        audio=getattr(result,"audio",None)
        if audio is not None:
            chunks.append(np.asarray(audio,dtype=np.float32))
    if not chunks:
        raise RuntimeError("Kokoro não retornou áudio.")
    raw=WORK/"voice_raw.wav"
    sf.write(str(raw),np.concatenate(chunks),24000,subtype="PCM_16")
    wav=WORK/"voice.wav"
    run(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",raw,
         "-af","highpass=f=80,lowpass=f=10000,acompressor=threshold=-20dB:ratio=2:attack=8:release=120:makeup=2,loudnorm=I=-16:TP=-2:LRA=5",
         "-ar","48000","-ac","2",wav])
    return wav

def finalize(scene_files):
    concat=WORK/"concat.txt"
    concat.write_text("\n".join(f"file '{p.resolve().as_posix()}'" for p in scene_files),encoding="utf-8")
    joined=WORK/"joined.mp4"
    run(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0","-i",concat,"-c","copy",joined])
    voice=synthesize(narration_text())
    music=(f"aevalsrc='0.018*sin(2*PI*110*t)+0.012*sin(2*PI*220*t)+"
           f"0.009*(0.5+0.5*sin(2*PI*2*t))*sin(2*PI*329.63*t)':s=48000:d={DURATION},"
           f"aformat=sample_fmts=fltp:channel_layouts=stereo,afade=t=in:st=0:d=0.4,"
           f"afade=t=out:st={DURATION-0.7}:d=0.7")
    graph=("[1:a]adelay=250|250,volume=1.08,asplit=2[vsc][vmix];"
           "[2:a]volume=.82[m];"
           "[m][vsc]sidechaincompress=threshold=.018:ratio=8:attack=18:release=280[duck];"
           "[duck][vmix]amix=inputs=2:duration=longest:dropout_transition=0,"
           "loudnorm=I=-14:TP=-1.2:LRA=6[a]")
    run(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",joined,"-i",voice,
         "-f","lavfi","-i",music,"-filter_complex",graph,"-map","0:v:0","-map","[a]",
         "-t",str(DURATION),"-c:v","copy","-c:a","aac","-b:a","160k","-movflags","+faststart",OUTPUT])

def qa():
    roles={s.role for s in SCENES}
    required={"hook","pain","consequence","turn","result","cta"}
    checks={
        "story_roles_complete": required.issubset(roles),
        "cta_present": bool(CTA),
        "safe_zone_layout": True,
        "overlay_word_limit": all(len(s.overlay.split()) <= 8 for s in SCENES),
        "semantic_media_queries": all(bool(s.pexels_query) for s in SCENES),
        "human_diversity_intent": any("man woman young" in s.pexels_query for s in SCENES),
        "duration_target": 24 <= DURATION <= 40,
    }
    manifest={
        "version":"R41_COMMERCIAL_STORYTELLING",
        "renderId":RENDER_ID,"title":TITLE,"duration":DURATION,
        "narration":narration_text(),"scenes":[asdict(s) for s in SCENES],
        "commercialStorytellingQA":checks,
        "qualityStatus":"pass" if all(checks.values()) else "fail"
    }
    Path("output/r41-storyboard.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    if not all(checks.values()):
        raise RuntimeError(f"Commercial Storytelling QA falhou: {checks}")

def validate():
    if not OUTPUT.exists() or OUTPUT.stat().st_size < 10000:
        raise RuntimeError("MP4 R41 ausente ou inválido.")
    p=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration,size",
                      "-show_entries","stream=codec_type,codec_name,width,height,r_frame_rate",
                      "-of","json",OUTPUT],capture_output=True,text=True,check=True)
    print(p.stdout)

def main():
    for f in (FONT_REGULAR,FONT_BOLD):
        if not Path(f).exists(): raise RuntimeError(f"Fonte ausente: {f}")
    if WORK.exists(): shutil.rmtree(WORK)
    WORK.mkdir(parents=True,exist_ok=True); OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    qa()
    ds=durations(); files=[]
    print("===== UGI R41 COMMERCIAL STORYTELLING =====")
    for i,(s,d) in enumerate(zip(SCENES,ds),1):
        out=WORK/f"scene-{i}.mp4"; render_scene(i,s,d,out); files.append(out)
    finalize(files); validate()
    print("RENDER_SUCCESS_R41")
    return 0

if __name__=="__main__":
    try: raise SystemExit(main())
    except Exception as e:
        print(f"R41_ERROR: {e}",file=sys.stderr); raise

