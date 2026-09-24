#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, math, pathlib, re, subprocess, tempfile
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[2]
DEFAULT_REGISTRY = ROOT / "config/vsa/VSA_ASSISTED_ANIMATION_CAPABILITIES_V1.json"

VERBS = [
    (r"\b(expand\w*)\b","expandiu","mostrar expansão progressiva"),
    (r"\b(afund\w*|submerg\w*)\b","afundou","mostrar descida até submersão"),
    (r"\b(atravess\w*)\b","atravessou","mostrar deslocamento entre dois pontos"),
    (r"\b(esquent\w*|aquec\w*)\b","esquentou","mostrar aumento visual de temperatura"),
    (r"\b(rach\w*)\b","rachou","mostrar formação progressiva da rachadura"),
    (r"\b(gir\w*|rotacion\w*|orbit\w*)\b","girou","mostrar rotação ou órbita real"),
    (r"\b(cresc\w*|aument\w*)\b","cresceu","mostrar mudança de escala"),
    (r"\b(desab\w*|colaps\w*)\b","desabou","mostrar perda estrutural e queda"),
    (r"\b(vaporiz\w*|evapor\w*)\b","vaporizou","mostrar mudança de líquido para vapor"),
    (r"\b(curv\w*|refrat\w*)\b","curvou","mostrar trajetória mudando ao atravessar um meio"),
    (r"\b(divid\w*|separ\w*)\b","dividiu","mostrar bifurcação em dois caminhos"),
    (r"\b(flutu\w*|sustent\w*)\b","flutuou","mostrar sustentação sem contato"),
    (r"\b(desliz\w*)\b","deslizou","mostrar deslocamento lateral contínuo"),
]
ZSKY = {"máquina","motor","vapor","pressão","temperatura","órbita","planeta","lua","atmosfera","estrutura interna","anatomia","fenômeno","reconstrução","escala","mapa","física","calor","rachadura","vulcão","tsunami","laser"}
STEVE = {"léo","personagem","ilustrado","ilustrada","storyboard","linha do tempo","comparação","infográfico","2d","jovem","humor"}

def load(path): return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
def save(path,obj):
    p=pathlib.Path(path); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def sh(cmd): subprocess.run([str(x) for x in cmd],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
def out(cmd): return subprocess.check_output([str(x) for x in cmd],text=True,stderr=subprocess.STDOUT).strip()
def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1048576),b""): h.update(b)
    return h.hexdigest()
def split_text(text):
    text=re.sub(r"\s+"," ",text.strip())
    return [x.strip() for x in re.split(r"(?<=[.!?])\s+",text) if len(x.strip())>=20]
def verb(sentence):
    low=sentence.lower()
    for pat,name,action in VERBS:
        if re.search(pat,low,re.I): return name,action,4
    return "explica","mostrar causalmente o fenômeno sem cartão genérico",0
def hint(req,sentence):
    for h in req.get("scene_hints") or []:
        if str(h.get("match") or "").lower() in sentence.lower() and h.get("match"):
            return h
    return {}
def tool(req,sentence,h):
    if req.get("public_figure") is True or h.get("public_figure") is True: return "current_pipeline"
    if req.get("real_footage_available") is True or h.get("real_footage_available") is True: return "current_pipeline"
    forced=str(h.get("tool_candidate") or "")
    if forced in {"zsky","steve_ai","current_pipeline"}: return forced
    low=(sentence+" "+str(h.get("visual_tag") or "")).lower()
    if h.get("requires_leo") is True or any(x in low for x in STEVE): return "steve_ai"
    if any(x in low for x in ZSKY): return "zsky"
    return "current_pipeline"
def frames(v):
    pairs={
      "expandiu":("elemento compacto","mesmo elemento visivelmente expandido"),
      "afundou":("objeto acima da superfície","objeto submerso após a descida"),
      "atravessou":("objeto no ponto de origem","objeto no destino após cruzar o espaço"),
      "esquentou":("sistema frio ou neutro","mesmo sistema em temperatura maior"),
      "rachou":("estrutura íntegra","rachadura progressiva concluída"),
      "girou":("corpo na orientação inicial","mesmo corpo rotacionado com referência preservada"),
      "cresceu":("objeto na escala inicial","mesmo objeto maior com escala de referência"),
      "desabou":("estrutura sustentada","estrutura após a queda"),
      "vaporizou":("líquido antes da vaporização","vapor formado com líquido remanescente"),
      "curvou":("trajetória reta entrando no meio","trajetória saindo curvada"),
      "dividiu":("estrutura única","dois caminhos distintos"),
      "flutuou":("objeto próximo da superfície","objeto sustentado com separação visível"),
      "deslizou":("objeto no início da superfície","objeto deslocado lateralmente")
    }
    return pairs.get(v,("estado inicial imediatamente antes da ação","estado final mostrando a consequência"))
def neg(t):
    s="textos, letras, legendas, logotipos, marcas, interfaces, apresentadores, avatar falando, objetos flutuantes sem causa, anatomia deformada, mãos deformadas, movimentos impossíveis, câmera agitada, mudanças aleatórias, elementos sem relação com a narração, composição reutilizada"
    if t=="steve_ai": s+=", lip-sync e personagem falando para a câmera"
    return s
def prompt(scene,en=False):
    if en:
        return f"""Create a vertical 9:16 clip, {scene['duration_seconds']} seconds long, for a short educational documentary from Você Sabia Agora.

Narration excerpt:
{scene['narration_excerpt']}

Scene purpose:
{scene['visual_purpose']}

Main visual action:
{scene['visual_action']}

Scene:
{scene['scene_description']}

First frame:
{scene['first_frame']}

Development:
{scene['development']}

Last frame:
{scene['last_frame']}

Camera movement:
{scene['camera_motion']}

Style:
premium educational visual, phone-first vertical composition, natural causal motion, coherent lighting, sharp detail and physical continuity.

Preserve:
the central-lower caption safe area.

Do not include:
text, subtitles, logos, trademarks, interfaces, presenters, talking avatars, deformed anatomy, impossible motion, random scene changes or unrelated elements.

This is an educational visual representation and must not pretend to be authentic documentary footage."""
    return f"""Crie um clipe vertical 9:16, com {scene['duration_seconds']} segundos, para um vídeo documental curto do canal Você Sabia Agora.

Trecho da narração:
{scene['narration_excerpt']}

Objetivo da cena:
{scene['visual_purpose']}

Ação visual principal:
{scene['visual_action']}

Cena:
{scene['scene_description']}

Primeiro frame:
{scene['first_frame']}

Desenvolvimento:
{scene['development']}

Último frame:
{scene['last_frame']}

Movimento de câmera:
{scene['camera_motion']}

Estilo:
documental ou animação explicativa premium, educativa, vertical, movimento natural, iluminação coerente, detalhes nítidos e continuidade física.

Preservar:
área inferior e central necessária para as legendas.

Não incluir:
{scene['negative_prompt']}.

A cena deve funcionar como representação visual educativa e não deve se passar por gravação documental verdadeira."""
def plan(req,registry):
    if str(req.get("narration_status") or "").lower() not in {"approved","final","practically_final"}:
        raise ValueError("APPROVED_NARRATION_REQUIRED")
    ss=split_text(str(req.get("approved_script") or ""))
    if len(ss)<2: raise ValueError("AT_LEAST_TWO_VISUALIZABLE_SENTENCES_REQUIRED")
    ranked=[]
    for i,s in enumerate(ss):
        v,a,score=verb(s); h=hint(req,s); t=tool(req,s,h)
        ranked.append((score+(3 if t!="current_pipeline" else 0)+(2 if h else 0),i,s,v,a,h,t))
    chosen=sorted(sorted(ranked,key=lambda x:(-x[0],x[1]))[:4],key=lambda x:x[1])
    scenes=[]
    for n,(_,idx,s,v,a,h,t) in enumerate(chosen,1):
        first,last=frames(v); cap=registry["tools"][t]; d=max(3,min(int(h.get("duration_seconds") or 5),6))
        sc={
          "scene_id":f"vsa_scene_{n:02d}","source_sentence_index":idx,"narration_excerpt":s,
          "visual_purpose":str(h.get("visual_purpose") or f"Compreender visualmente a ação {v} e sua consequência."),
          "main_verb":v,"visual_action":a,"tool_candidate":t,
          "usage_mode":"manual_pilot_only" if t!="current_pipeline" else cap["usage_mode"],
          "production_route":t if cap.get("free_output_fit_for_vsa_production") else "current_pipeline",
          "candidate_current_blocker":cap.get("current_blocker"),"duration_seconds":d,"aspect_ratio":"9:16",
          "target_resolution":"1080x1920",
          "scene_description":str(h.get("scene_description") or f"Representação educativa específica de: {s}"),
          "first_frame":str(h.get("first_frame") or first),
          "development":str(h.get("development") or f"Executar {a} do estado inicial ao resultado final."),
          "last_frame":str(h.get("last_frame") or last),
          "camera_motion":str(h.get("camera_motion") or ("movimento suave de acompanhamento" if t=="zsky" else "câmera estável; movimento nos elementos explicativos")),
          "caption_safe_area":registry["format_contract"]["caption_safe_area"],
          "continuity_notes":str(h.get("continuity_notes") or "Entrar da evidência anterior e sair para footage ou prova real."),
          "negative_prompt":neg(t),"representation_disclosure":True,"publication_allowed":False
        }
        sc["prompt_pt"]=prompt(sc,False); sc["prompt_en"]=prompt(sc,True); scenes.append(sc)
    return {"schema":"VSA_ASSISTED_ANIMATION_VISUAL_PLAN_V1","stage":registry["stage_name"],
      "video_id":req.get("video_id"),"topic_title":req.get("topic_title"),"state":"draft_visual_plan",
      "usage_mode":"manual_pilot_only","production_enabled":False,"automatic_publication":False,
      "publication_allowed":False,"scene_count":len(scenes),"scenes":scenes,"fallback":"current_pipeline"}

def package(plan,registry):
    lines=[f"# Pacote manual — {plan.get('topic_title') or plan.get('video_id')}","","Estado: awaiting_manual_generation","Publicação: desabilitada","Custo máximo: R$ 0,00",""]
    for s in plan["scenes"]:
        cap=registry["tools"][s["tool_candidate"]]
        lines += [f"## {s['scene_id']} — {cap['label']}",f"Link oficial: {cap.get('official_url','pipeline interno')}",
          f"Rota efetiva hoje: {s['production_route']}",f"Blocker atual: {s.get('candidate_current_blocker')}",
          "Tentativas manuais máximas: 3","","### Prompt PT",s["prompt_pt"],"","### Prompt EN",s["prompt_en"],""]
    return "\n".join(lines)+"\n"
def probe(path):
    return json.loads(out(["ffprobe","-v","error","-show_streams","-show_format","-of","json",path]))
def ratio(v):
    if not v:return 0.0
    if "/" in v:
        a,b=v.split("/",1); return float(a)/float(b) if float(b) else 0.0
    return float(v)
def frame_metrics(asset,dur):
    from PIL import Image,ImageChops,ImageStat
    ts=[max(.05,dur*.08),dur*.5,max(.05,dur*.92)]; ims=[]; br=[]
    with tempfile.TemporaryDirectory() as td:
        for i,t in enumerate(ts):
            p=pathlib.Path(td)/f"{i}.png"; sh(["ffmpeg","-y","-loglevel","error","-ss",f"{t:.3f}","-i",asset,"-frames:v","1",p])
            im=Image.open(p).convert("L").resize((96,170)); ims.append(im.copy()); br.append(ImageStat.Stat(im).mean[0])
    dif=[ImageStat.Stat(ImageChops.difference(a,b)).mean[0] for a,b in zip(ims,ims[1:])]
    return br,dif
def validate(asset,scene,meta,registry,ledger=None):
    r={"schema":"VSA_ASSISTED_ANIMATION_VALIDATION_V1","asset":str(asset),"scene_id":scene.get("scene_id"),
       "tool":meta.get("generation_tool"),"state":"technical_validation","publication_allowed":False,
       "automatic_publication":False,"errors":[],"warnings":[],"checks":{}}
    e=r["errors"]
    if not asset.is_file() or not asset.stat().st_size:
        r["state"]="rejected_low_quality";e.append("ASSET_MISSING_OR_EMPTY");return r
    try:p=probe(asset)
    except Exception:
        r["state"]="rejected_low_quality";e.append("FFPROBE_FAIL");return r
    v=next((x for x in p.get("streams",[]) if x.get("codec_type")=="video"),None)
    if not v:r["state"]="rejected_low_quality";e.append("VIDEO_STREAM_MISSING");return r
    w,h=int(v.get("width") or 0),int(v.get("height") or 0); fps=ratio(v.get("avg_frame_rate") or v.get("r_frame_rate"))
    dur=float((p.get("format") or {}).get("duration") or 0); digest=sha(asset)
    aud=[x for x in p.get("streams",[]) if x.get("codec_type")=="audio"]
    r["checks"].update(width=w,height=h,fps=round(fps,3),duration_seconds=round(dur,3),codec=v.get("codec_name"),audio_streams=len(aud),sha256=digest)
    fmt=registry["format_contract"]
    if h<=w:e.append("ORIENTATION_NOT_VERTICAL")
    if w<int(fmt["minimum_input_width"]) or h<int(fmt["minimum_input_height"]):e.append("RESOLUTION_BELOW_MINIMUM")
    if dur<2.5 or dur>6.5:e.append("DURATION_OUT_OF_RANGE")
    if abs(fps-30)>0.6:r["warnings"].append("FPS_WILL_BE_NORMALIZED_TO_30")
    if aud:r["warnings"].append("UNEXPECTED_AUDIO_PRESENT_WILL_BE_STRIPPED")
    try:
        br,dif=frame_metrics(asset,dur);r["checks"]["sample_brightness"]=[round(x,2) for x in br];r["checks"]["sample_motion_delta"]=[round(x,2) for x in dif]
        if any(x<4 for x in br):e.append("BLACK_OR_NEAR_BLACK_FRAME")
        if max(dif or [0])<1.8:e.append("SCENE_WITHOUT_MEANINGFUL_MOTION")
    except Exception:e.append("FRAME_ANALYSIS_FAIL")
    for x in (ledger or {"entries":[]}).get("entries") or []:
        if x.get("sha256")==digest:
            e.append("DUPLICATE_ANIMATION_ACROSS_TOPICS" if str(x.get("video_id"))!=str(meta.get("video_id")) else "DUPLICATE_FILE");break
    t=str(meta.get("generation_tool") or ""); cap=registry["tools"].get(t)
    if not cap:e.append("GENERATION_TOOL_INVALID")
    if meta.get("watermark_present") is True:e.append("WATERMARK_PRESENT")
    if meta.get("rights_confirmed") is not True or meta.get("commercial_use_confirmed") is not True:e.append("RIGHTS_OR_COMMERCIAL_USE_NOT_CONFIRMED")
    if meta.get("download_allowed") is not True:e.append("DOWNLOAD_NOT_ALLOWED")
    try:cost=float(meta.get("cost_brl",0));credits=float(meta.get("credits_consumed",0))
    except Exception:cost=credits=math.inf
    if cost>0 or credits>0 or meta.get("payment_required") is True or meta.get("card_required") is True:e.append("ZERO_COST_POLICY_FAIL")
    if meta.get("trial_with_future_charge") is True:e.append("PAID_TRIAL_FORBIDDEN")
    if cap and cost==0 and cap.get("free_output_fit_for_vsa_production") is not True:e.append("TOOL_ZERO_COST_PRODUCTION_BLOCKED_BY_CURRENT_TERMS")
    if t=="zsky" and cap and cap.get("free_video_watermark_present") is True:e.append("ZSKY_FREE_WATERMARK_POLICY_BLOCK")
    if t=="steve_ai" and cap and (cap.get("free_downloadable_video") is not True or cap.get("commercial_use_free") is not True):e.append("STEVE_FREE_RIGHTS_OR_DOWNLOAD_POLICY_BLOCK")
    if meta.get("narration_visual_match") is not True:e.append("NARRATION_VISUAL_MISMATCH")
    if meta.get("continuity_ok") is not True:e.append("CONTINUITY_FAIL")
    if meta.get("physical_coherence") is not True or meta.get("historical_scientific_fidelity") is not True:e.append("FIDELITY_FAIL")
    if meta.get("deformed_characters_or_anatomy") is True or meta.get("generated_text_or_bad_text") is True:e.append("VISUAL_ARTIFACT_FAIL")
    decision=str(meta.get("human_decision") or "").upper()
    if e:
        if any("WATERMARK" in x for x in e):state="rejected_watermark"
        elif any("ZERO_COST" in x or "PAID_TRIAL" in x for x in e):state="rejected_cost"
        elif any("RIGHTS" in x or "DOWNLOAD" in x or "CURRENT_TERMS" in x for x in e):state="rejected_rights"
        elif any("DUPLICATE" in x for x in e):state="rejected_duplicate_animation"
        elif any("NARRATION" in x or "FIDELITY" in x or "VISUAL_ARTIFACT" in x for x in e):state="rejected_inaccurate"
        elif any("CONTINUITY" in x for x in e):state="rejected_discontinuity"
        else:state="rejected_low_quality"
        r.update(state=state,approved_for_editing=False,fallback="current_pipeline");return r
    if decision=="APROVAR PARA MONTAGEM":r.update(state="approved_for_editing",approved_for_editing=True)
    elif decision=="REFAZER":r.update(state="returned_for_regeneration",approved_for_editing=False)
    elif decision=="REJEITAR E USAR PIPELINE ATUAL":r.update(state="fallback_to_current_pipeline",approved_for_editing=False)
    else:r.update(state="editorial_review",approved_for_editing=False);r["warnings"].append("HUMAN_DECISION_REQUIRED")
    return r
def integrate(asset,scene,validation,outfile,patchfile):
    if validation.get("state")!="approved_for_editing" or validation.get("approved_for_editing") is not True:raise ValueError("HUMAN_APPROVED_ASSET_REQUIRED")
    outfile.parent.mkdir(parents=True,exist_ok=True)
    vf="scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,fps=30,format=yuv420p"
    sh(["ffmpeg","-y","-loglevel","error","-i",asset,"-an","-vf",vf,"-c:v","libx264","-preset","veryfast","-crf","19","-movflags","+faststart",outfile])
    p=probe(outfile);v=next(x for x in p["streams"] if x.get("codec_type")=="video")
    fmt={"width":int(v["width"]),"height":int(v["height"]),"fps":round(ratio(v.get("avg_frame_rate") or v.get("r_frame_rate")),3),"codec":v.get("codec_name"),"audio_streams":len([x for x in p["streams"] if x.get("codec_type")=="audio"])}
    if fmt!={"width":1080,"height":1920,"fps":30.0,"codec":"h264","audio_streams":0}:raise RuntimeError(f"NORMALIZATION_FAIL:{fmt}")
    patch={"schema":"VSA_ASSISTED_ANIMATION_TIMELINE_PATCH_V1","state":"integrated_into_timeline","scene_id":scene["scene_id"],
      "narration_excerpt":scene["narration_excerpt"],"main_verb":scene["main_verb"],"sync_rule":"alinhar a ação visual principal ao verbo narrado",
      "source_asset":str(asset),"normalized_asset":str(outfile),"normalized_sha256":sha(outfile),"format":fmt,
      "transition_in":"short_natural","transition_out":"short_natural","caption_safe_area":scene["caption_safe_area"],
      "preserve_existing_music_mix":True,"preserve_canonical_logo_and_cta":True,"preview_required":True,
      "final_qa_required":True,"human_approval_for_publication_required":True,"publication_allowed":False,"automatic_publication":False}
    save(patchfile,patch);return patch
def main():
    a=argparse.ArgumentParser();a.add_argument("--registry",default=str(DEFAULT_REGISTRY));sp=a.add_subparsers(dest="cmd",required=True)
    p=sp.add_parser("plan");p.add_argument("--request",required=True);p.add_argument("--out",required=True);p.add_argument("--package")
    v=sp.add_parser("validate");v.add_argument("--asset",required=True);v.add_argument("--scene",required=True);v.add_argument("--metadata",required=True);v.add_argument("--ledger");v.add_argument("--report",required=True)
    i=sp.add_parser("integrate");i.add_argument("--asset",required=True);i.add_argument("--scene",required=True);i.add_argument("--validation",required=True);i.add_argument("--out",required=True);i.add_argument("--patch",required=True)
    x=a.parse_args();reg=load(x.registry)
    if x.cmd=="plan":
        pl=plan(load(x.request),reg);pl["state"]="awaiting_manual_generation";save(x.out,pl)
        if x.package:pathlib.Path(x.package).write_text(package(pl,reg),encoding="utf-8")
        print(json.dumps({"status":"PLAN_READY","scenes":len(pl["scenes"]),"publication_allowed":False}));return 0
    if x.cmd=="validate":
        rr=validate(pathlib.Path(x.asset),load(x.scene),load(x.metadata),reg,load(x.ledger) if x.ledger else None);save(x.report,rr);print(json.dumps(rr));return 0 if rr.get("state")=="approved_for_editing" else 3
    pp=integrate(pathlib.Path(x.asset),load(x.scene),load(x.validation),pathlib.Path(x.out),pathlib.Path(x.patch));print(json.dumps({"status":"CLIP_NORMALIZED","publication_allowed":False,"state":pp["state"]}));return 0
if __name__=="__main__": raise SystemExit(main())
