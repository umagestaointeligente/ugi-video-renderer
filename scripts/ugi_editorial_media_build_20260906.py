from __future__ import annotations

import html
import json
import re
import shlex
import subprocess
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "public" / "ugi" / "editorial" / "2026-09-06"
TMP = ROOT / ".tmp-ugi-editorial-20260906"
OUT.mkdir(parents=True, exist_ok=True)
TMP.mkdir(parents=True, exist_ok=True)

VOICE = "pt-BR-AntonioNeural"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

ROCK_VIDEO = "https://controle.expressorio.com.br/wp-content/uploads/2026/09/video_2026-09-05_14-16-31.mp4"
ROBERTA_ARTICLE = "https://gshow.globo.com/festivais/rock-in-rio/2026/noticia/e-hoje-roberta-medina-fala-sobre-expectativa-para-o-rock-in-rio-2026.ghtml"
FOXCONN_VIDEO = "https://blogs.nvidia.com/wp-content/uploads/2026/05/5172573_RoboticFactory_V27_BlogPost_Foxconn_Caption_v02.mp4"
RETAIL_AI_VIDEO = "https://blogs.nvidia.com/wp-content/uploads/2025/04/NVIDIA-AI-Blueprint-for-Retail-Shopping-Assistants-Fashion-Demo-SM-202504.mp4"

ITEMS = {
    "rock-linkedin": {
        "kind": "image",
        "headline": "ROCK IN RIO\nO QUE 700 MIL PESSOAS\nENSINAM SOBRE GESTÃO?",
        "credit": "Imagem: gshow / Rock in Rio | Arte editorial: UGI",
    },
    "rock-instagram": {
        "kind": "video",
        "source": ROCK_VIDEO,
        "source_label": "Expresso Rio — registro do Rock in Rio 2026, 5 set. 2026",
        "narration": "Você olha para o Rock in Rio e vê música. Um gestor deveria enxergar uma operação para cerca de setecentas mil pessoas. São mais de noventa empresas, cem ativações de marca, mobilidade, segurança, tecnologia e milhares de decisões acontecendo ao mesmo tempo. O Centro de Operações Rio usa centenas de câmeras para acompanhar os fluxos ao redor da Cidade do Rock. E uma experiência no festival usa visão computacional e sensores para transformar a reação do público em dados. A lição é simples: escala sem visibilidade vira caos. Gestão é reduzir a distância entre o que está acontecendo e a decisão que precisa ser tomada. Você colocaria tecnologia onde primeiro?",
        "hook": "ROCK IN RIO: O SHOW É SÓ A PONTA",
        "credit": "Imagens: Expresso Rio | Dados: Rock in Rio, COR-Rio, UOL, O Globo",
    },
    "rock-tiktok": {
        "kind": "video",
        "source": ROCK_VIDEO,
        "source_label": "Expresso Rio — registro do Rock in Rio 2026, 5 set. 2026",
        "narration": "Rock in Rio não é só festival. É uma operação temporária que precisa coordenar centenas de milhares de pessoas, dezenas de empresas, marcas, segurança, transporte e tecnologia. O público vê o palco. A gestão precisa enxergar fluxo, gargalo, risco e decisão em tempo real. Quando sensores e câmeras transformam comportamento em dado, a pergunta muda: não é ter mais informação, é decidir mais rápido e melhor. Esse é o verdadeiro bastidor de uma operação gigante.",
        "hook": "FESTIVAL OU OPERAÇÃO GIGANTE?",
        "credit": "Imagens: Expresso Rio | Dados: COR-Rio, UOL, O Globo",
    },
    "foxconn-story": {
        "kind": "video",
        "source": FOXCONN_VIDEO,
        "source_label": "NVIDIA — Foxconn AI factory operations",
        "narration": "A Foxconn acabou de sinalizar um terceiro trimestre acima das expectativas com a demanda por inteligência artificial puxando o negócio. Em agosto, a receita avançou mais de cinquenta por cento sobre um ano antes. O ponto de gestão é simples: IA não está mudando apenas software. Está mudando capacidade industrial, investimento e velocidade de operação. Quem trata IA só como ferramenta de escritório está enxergando apenas uma parte da transformação.",
        "hook": "IA JÁ ESTÁ MUDANDO A FÁBRICA",
        "credit": "Imagens: NVIDIA / Foxconn | Informação: Reuters",
    },
    "retail-ai-tiktok": {
        "kind": "video",
        "source": RETAIL_AI_VIDEO,
        "source_label": "NVIDIA — AI retail shopping assistant demo",
        "narration": "Uma mudança silenciosa já começou no varejo. Na John Lewis, buscas que chegam por agentes de inteligência artificial passaram de zero vírgula três por cento para dois vírgula cinco por cento em um ano. Parece pequeno, mas é mais de oito vezes o nível anterior. Se o consumidor começa a pedir para uma IA escolher, comparar e recomendar produtos, a disputa deixa de acontecer só na prateleira ou no Google. A próxima pergunta do varejo é: sua marca está preparada para ser escolhida por uma máquina?",
        "hook": "QUANDO A IA COMEÇA A ESCOLHER POR VOCÊ",
        "credit": "Demonstração visual: NVIDIA | Dado John Lewis: Reuters",
    },
}


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    print("+", " ".join(shlex.quote(x) for x in cmd), flush=True)
    return subprocess.run(cmd, check=True, text=True)


def fetch(url: str, path: Path) -> Path:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 UGI-Editorial/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r, path.open("wb") as f:
        while True:
            chunk = r.read(1024 * 1024)
            if not chunk:
                break
            f.write(chunk)
    if path.stat().st_size < 1024:
        raise RuntimeError(f"asset muito pequeno: {url}")
    return path


def download_video(name: str, item: dict) -> tuple[Path, str]:
    src = fetch(item["source"], TMP / f"{name}-download")
    target = TMP / f"{name}-source.mp4"
    run(["ffmpeg", "-y", "-i", str(src), "-c:v", "libx264", "-preset", "veryfast", "-crf", "24", "-c:a", "aac", "-movflags", "+faststart", str(target)])
    return target, item["source_label"]


def download_roberta_image() -> tuple[Path, str]:
    req = urllib.request.Request(ROBERTA_ARTICLE, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=45) as r:
        page = r.read().decode("utf-8", errors="ignore")
    patterns = [
        r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']',
    ]
    image_url = None
    for pattern in patterns:
        m = re.search(pattern, page, flags=re.I)
        if m:
            image_url = html.unescape(m.group(1))
            break
    if not image_url:
        raise RuntimeError("og:image da matéria de Roberta Medina não encontrado")
    return fetch(image_url, TMP / "roberta-medina-source.jpg"), f"gshow — {ROBERTA_ARTICLE}"


def make_tts(name: str, text: str) -> Path:
    out = TMP / f"{name}-voice.mp3"
    run(["edge-tts", "--voice", VOICE, "--rate=-2%", "--text", text, "--write-media", str(out)])
    return out


def duration(path: Path) -> float:
    cp = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)], check=True, capture_output=True, text=True)
    return float(cp.stdout.strip())


def esc_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace("'", "’").replace(":", "\\:").replace("%", "\\%")


def make_vertical_video(name: str, src: Path, voice: Path, hook: str, credit: str) -> Path:
    out = OUT / f"{name}.mp4"
    dur = max(8.0, duration(voice) + 0.6)
    src_dur = max(1.0, duration(src))
    seg = max(3.0, dur / 3.0)
    starts = [0.0, max(0.0, src_dur * 0.33), max(0.0, src_dur * 0.66)]
    cuts = []
    for i, start in enumerate(starts):
        p = TMP / f"{name}-cut-{i}.mp4"
        vf = "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,setsar=1"
        run(["ffmpeg", "-y", "-stream_loop", "-1", "-ss", f"{start:.2f}", "-i", str(src), "-t", f"{seg:.2f}", "-an", "-vf", vf, "-r", "30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "29", "-pix_fmt", "yuv420p", str(p)])
        cuts.append(p)
    concat = TMP / f"{name}-concat.txt"
    concat.write_text("".join(f"file '{p.as_posix()}'\n" for p in cuts), encoding="utf-8")
    base = TMP / f"{name}-base.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat), "-t", f"{dur:.2f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "29", "-pix_fmt", "yuv420p", str(base)])
    hook_text = esc_text(hook)
    credit_text = esc_text(credit)
    vf = (
        "drawbox=x=28:y=48:w=664:h=138:color=black@0.56:t=fill,"
        f"drawtext=fontfile={FONT}:text='{hook_text}':fontcolor=white:fontsize=32:x=(w-text_w)/2:y=88,"
        "drawbox=x=20:y=h-112:w=w-40:h=76:color=black@0.52:t=fill,"
        f"drawtext=fontfile={FONT_REG}:text='{credit_text}':fontcolor=white:fontsize=14:x=34:y=h-88"
    )
    run(["ffmpeg", "-y", "-i", str(base), "-i", str(voice), "-filter_complex", f"[0:v]{vf}[v]", "-map", "[v]", "-map", "1:a:0", "-t", f"{dur:.2f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "28", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(out)])
    return out


def make_linkedin_image(src: Path, headline: str, credit: str) -> Path:
    out = OUT / "rock-linkedin.jpg"
    lines = headline.split("\n")
    filters = ["scale=1200:627:force_original_aspect_ratio=increase,crop=1200:627", "drawbox=x=0:y=0:w=1200:h=627:color=black@0.42:t=fill"]
    for line, y, fs in zip(lines, [104, 202, 296], [58, 50, 50]):
        filters.append(f"drawtext=fontfile={FONT}:text='{esc_text(line)}':fontcolor=white:fontsize={fs}:x=(w-text_w)/2:y={y}")
    filters += ["drawbox=x=0:y=548:w=1200:h=79:color=black@0.58:t=fill", f"drawtext=fontfile={FONT_REG}:text='{esc_text(credit)}':fontcolor=white:fontsize=17:x=36:y=582"]
    run(["ffmpeg", "-y", "-i", str(src), "-vf", ",".join(filters), "-q:v", "2", str(out)])
    return out


def main() -> None:
    manifest = {"schema": "ugi.editorial.media-pack.v1", "date": "2026-09-06", "items": {}}
    roberta_src, roberta_label = download_roberta_image()
    for name, item in ITEMS.items():
        if item["kind"] == "image":
            output = make_linkedin_image(roberta_src, item["headline"], item["credit"])
            source_label = roberta_label
        else:
            src, source_label = download_video(name, item)
            voice = make_tts(name, item["narration"])
            output = make_vertical_video(name, src, voice, item["hook"], item["credit"])
        manifest["items"][name] = {"file": output.relative_to(ROOT).as_posix(), "source": source_label, "credit": item["credit"], "kind": item["kind"]}
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
