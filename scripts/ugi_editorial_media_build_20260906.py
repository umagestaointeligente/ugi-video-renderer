from __future__ import annotations

import json
import os
import shlex
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "public" / "ugi" / "editorial" / "2026-09-06"
TMP = ROOT / ".tmp-ugi-editorial-20260906"
OUT.mkdir(parents=True, exist_ok=True)
TMP.mkdir(parents=True, exist_ok=True)

VOICE = "pt-BR-AntonioNeural"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

ROCK_URL = "https://www.youtube.com/watch?v=CC1q6ZwPDWM"

ITEMS = {
    "rock-linkedin": {
        "kind": "image",
        "source": ROCK_URL,
        "headline": "ROCK IN RIO\nO QUE 700 MIL PESSOAS\nENSINAM SOBRE GESTÃO?",
        "credit": "Imagem-base: Rock in Rio — canal oficial",
    },
    "rock-instagram": {
        "kind": "video",
        "source": ROCK_URL,
        "search": None,
        "narration": "Você olha para o Rock in Rio e vê música. Um gestor deveria enxergar uma operação para cerca de setecentas mil pessoas. São mais de noventa empresas, cem ativações de marca, mobilidade, segurança, tecnologia e milhares de decisões acontecendo ao mesmo tempo. O Centro de Operações Rio usa centenas de câmeras para acompanhar os fluxos ao redor da Cidade do Rock. E uma experiência no festival usa visão computacional e sensores para transformar a reação do público em dados. A lição é simples: escala sem visibilidade vira caos. Gestão é reduzir a distância entre o que está acontecendo e a decisão que precisa ser tomada. Você colocaria tecnologia onde primeiro?",
        "hook": "ROCK IN RIO: O SHOW É SÓ A PONTA",
        "credit": "Imagens: Rock in Rio — canal oficial | Dados: Rock in Rio, COR-Rio, UOL, O Globo",
    },
    "rock-tiktok": {
        "kind": "video",
        "source": ROCK_URL,
        "search": None,
        "narration": "Rock in Rio não é só festival. É uma operação temporária que precisa coordenar centenas de milhares de pessoas, dezenas de empresas, marcas, segurança, transporte e tecnologia. O público vê o palco. A gestão precisa enxergar fluxo, gargalo, risco e decisão em tempo real. Quando sensores e câmeras transformam comportamento em dado, a pergunta muda: não é ter mais informação, é decidir mais rápido e melhor. Esse é o verdadeiro bastidor de uma operação gigante.",
        "hook": "FESTIVAL OU OPERAÇÃO GIGANTE?",
        "credit": "Imagens: Rock in Rio — canal oficial | Dados: COR-Rio, UOL, O Globo",
    },
    "bytedance-story": {
        "kind": "video",
        "source": None,
        "search": "ytsearch5:ByteDance AI data center office technology official",
        "narration": "A ByteDance levantou quase trinta bilhões de dólares em financiamento enquanto acelera investimentos ligados à inteligência artificial. O número chama atenção, mas a pergunta de gestão é outra: quando a tecnologia muda tão rápido, capital sozinho cria vantagem? Ou a vantagem está em transformar investimento em capacidade, produto e velocidade de execução? IA está mudando o tamanho da aposta. Gestão define o retorno.",
        "hook": "US$ 29,6 BI PARA ACELERAR A IA",
        "credit": "Imagens: fonte audiovisual pública identificada no pacote | Informação: Reuters",
    },
    "johnlewis-tiktok": {
        "kind": "video",
        "source": None,
        "search": "ytsearch5:John Lewis Partnership store shopping official",
        "narration": "Uma mudança silenciosa já começou no varejo. Na John Lewis, buscas que chegam por agentes de inteligência artificial passaram de zero vírgula três por cento para dois vírgula cinco por cento em um ano. Parece pequeno, mas é mais de oito vezes o nível anterior. Se o consumidor começa a pedir para uma IA escolher, comparar e recomendar produtos, a disputa deixa de acontecer só na prateleira ou no Google. A próxima pergunta do varejo é: sua marca está preparada para ser escolhida por uma máquina?",
        "hook": "QUANDO A IA COMEÇA A ESCOLHER POR VOCÊ",
        "credit": "Imagens: fonte audiovisual pública identificada no pacote | Informação: Reuters",
    },
}


def run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess:
    print("+", " ".join(shlex.quote(x) for x in cmd), flush=True)
    return subprocess.run(cmd, check=check, text=True)


def download(name: str, item: dict) -> tuple[Path, str]:
    target = TMP / f"{name}-source.mp4"
    info = TMP / f"{name}-source-info.json"
    query = item.get("source") or item.get("search")
    if not query:
        raise RuntimeError(f"source ausente para {name}")
    cmd = [
        "yt-dlp", query,
        "--no-playlist", "--max-downloads", "1",
        "--merge-output-format", "mp4",
        "-f", "bv*[height<=720]+ba/b[height<=720]/best",
        "--write-info-json",
        "--output", str(TMP / f"{name}-source.%(ext)s"),
    ]
    run(cmd)
    # yt-dlp may keep a non-mp4 container despite merge fallback; normalize.
    candidates = [p for p in TMP.glob(f"{name}-source.*") if p.suffix.lower() in {".mp4", ".webm", ".mkv", ".mov"}]
    if not candidates:
        raise RuntimeError(f"download sem mídia para {name}")
    src = candidates[0]
    if src != target:
        run(["ffmpeg", "-y", "-i", str(src), "-c:v", "libx264", "-c:a", "aac", "-movflags", "+faststart", str(target)])
    infos = list(TMP.glob(f"{name}-source.info.json")) + list(TMP.glob(f"{name}-source*.info.json"))
    source_label = query
    if infos:
        try:
            meta = json.loads(infos[0].read_text(encoding="utf-8"))
            source_label = f"{meta.get('uploader') or meta.get('channel') or 'fonte audiovisual'} — {meta.get('webpage_url') or query}"
        except Exception:
            pass
    return target, source_label


def make_tts(name: str, text: str) -> Path:
    out = TMP / f"{name}-voice.mp3"
    run(["edge-tts", "--voice", VOICE, "--rate=-2%", "--text", text, "--write-media", str(out)])
    return out


def duration(path: Path) -> float:
    cp = subprocess.run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)
    ], check=True, capture_output=True, text=True)
    return float(cp.stdout.strip())


def make_vertical_video(name: str, src: Path, voice: Path, hook: str, credit: str) -> Path:
    out = OUT / f"{name}.mp4"
    dur = max(8.0, duration(voice) + 0.5)
    # A continuously moving, multi-cut treatment from real source footage. We use three
    # temporal windows from the source to avoid a static/editorial look.
    seg = max(3.0, dur / 3.0)
    cuts = []
    for i, start in enumerate((0.0, 6.0, 12.0)):
        p = TMP / f"{name}-cut-{i}.mp4"
        vf = "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,setsar=1"
        run(["ffmpeg", "-y", "-ss", f"{start:.2f}", "-i", str(src), "-t", f"{seg:.2f}", "-an", "-vf", vf,
             "-r", "30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "28", "-pix_fmt", "yuv420p", str(p)])
        cuts.append(p)
    concat = TMP / f"{name}-concat.txt"
    concat.write_text("".join(f"file '{p.as_posix()}'\n" for p in cuts), encoding="utf-8")
    base = TMP / f"{name}-base.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat), "-t", f"{dur:.2f}",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "28", "-pix_fmt", "yuv420p", str(base)])
    safe_hook = hook.replace("'", "’").replace(":", "\\:")
    safe_credit = credit.replace("'", "’").replace(":", "\\:")
    vf = (
        f"drawbox=x=32:y=54:w=656:h=132:color=black@0.58:t=fill,"
        f"drawtext=fontfile={FONT}:text='{safe_hook}':fontcolor=white:fontsize=35:"
        "x=(w-text_w)/2:y=82:box=0:line_spacing=6,"
        "drawbox=x=24:y=h-112:w=w-48:h=76:color=black@0.48:t=fill,"
        f"drawtext=fontfile={FONT_REG}:text='{safe_credit}':fontcolor=white:fontsize=15:"
        "x=40:y=h-89"
    )
    run(["ffmpeg", "-y", "-i", str(base), "-i", str(voice), "-filter_complex", f"[0:v]{vf}[v]",
         "-map", "[v]", "-map", "1:a:0", "-t", f"{dur:.2f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "27",
         "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(out)])
    return out


def make_linkedin_image(src: Path, headline: str, credit: str) -> Path:
    frame = TMP / "linkedin-frame.jpg"
    run(["ffmpeg", "-y", "-ss", "4", "-i", str(src), "-frames:v", "1", "-vf", "scale=1200:627:force_original_aspect_ratio=increase,crop=1200:627", str(frame)])
    out = OUT / "rock-linkedin.jpg"
    # Break headline into three explicit lines to keep it editorial and instantly readable.
    lines = headline.split("\n")
    filters = ["drawbox=x=0:y=0:w=1200:h=627:color=black@0.45:t=fill"]
    ys = [120, 210, 300]
    sizes = [58, 54, 54]
    for line, y, fs in zip(lines, ys, sizes):
        esc = line.replace("'", "’").replace(":", "\\:")
        filters.append(f"drawtext=fontfile={FONT}:text='{esc}':fontcolor=white:fontsize={fs}:x=(w-text_w)/2:y={y}")
    c = credit.replace("'", "’").replace(":", "\\:")
    filters.append("drawbox=x=0:y=548:w=1200:h=79:color=black@0.55:t=fill")
    filters.append(f"drawtext=fontfile={FONT_REG}:text='{c}':fontcolor=white:fontsize=18:x=42:y=580")
    run(["ffmpeg", "-y", "-i", str(frame), "-vf", ",".join(filters), "-q:v", "2", str(out)])
    return out


def main() -> None:
    manifest = {"schema": "ugi.editorial.media-pack.v1", "date": "2026-09-06", "items": {}}
    downloaded: dict[str, tuple[Path, str]] = {}
    # Reuse the Rock in Rio official source across all Rock outputs.
    rock_src, rock_label = download("rock-shared", {"source": ROCK_URL})
    downloaded["rock-shared"] = (rock_src, rock_label)

    for name, item in ITEMS.items():
        if name.startswith("rock-"):
            src, source_label = rock_src, rock_label
        else:
            src, source_label = download(name, item)
        if item["kind"] == "image":
            output = make_linkedin_image(src, item["headline"], item["credit"])
        else:
            voice = make_tts(name, item["narration"])
            effective_credit = item["credit"].replace("fonte audiovisual pública identificada no pacote", source_label.split(" — ")[0][:70])
            output = make_vertical_video(name, src, voice, item["hook"], effective_credit)
        manifest["items"][name] = {
            "file": output.relative_to(ROOT).as_posix(),
            "source": source_label,
            "credit": item["credit"],
            "kind": item["kind"],
        }
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
