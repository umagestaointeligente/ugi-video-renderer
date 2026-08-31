from __future__ import annotations
import argparse, pathlib

DENSITY_VERSION='ranked-source-set-2026-08-31'

def one(text, old, new, label):
    n=text.count(old)
    if n!=1: raise SystemExit(f'R3_{label}_COUNT_{n}')
    return text.replace(old,new,1)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--source',required=True); ap.add_argument('--output',required=True); a=ap.parse_args()
    src=pathlib.Path(a.source).read_text(encoding='utf-8')
    required_live=['RADAR_COMMERCE_PERF_R2','parallel-official-data-2026-08-31','/greenfield/brazil-opportunity-radar/source-health','CHECKOUT_PAID','ASAAS_WEBHOOK_TOKEN','RADAR_PRICE_BRL = 19.90','application/ld+json']
    for x in required_live:
        if x not in src: raise SystemExit('R3_LIVE_PREREQ_MISSING:'+x)
    if 'RADAR_COMMERCE_DENSITY_R3' in src: raise SystemExit('R3_ALREADY_LIVE')

    src=one(src,
      'const RADAR_COMMERCE_PERF_R2 = "parallel-official-data-2026-08-31";',
      'const RADAR_COMMERCE_PERF_R2 = "parallel-official-data-2026-08-31";\nconst RADAR_COMMERCE_DENSITY_R3 = "'+DENSITY_VERSION+'";',
      'CONST')
    src=one(src,'const timeoutMs=5500;','const timeoutMs=5000;','TIMEOUT')
    src=one(src,'from.setUTCDate(from.getUTCDate()-30);','from.setUTCDate(from.getUTCDate()-90);','WINDOW')
    src=one(src,'const directTasks=["8","6","4"].map(async modality=>{','const directTasks=["5","4"].map(async modality=>{','PNCP_SET')
    src=one(src,'const comprasTasks=["4","6","8"].map(async modality=>{','const comprasTasks=["5","6"].map(async modality=>{','COMPRAS_SET')
    src=one(src,
      'return {ok:true,version:RADAR_COMMERCE_EXTENSION_VERSION,performanceVersion:RADAR_COMMERCE_PERF_R2,provider:"PNCP + Compras.gov.br",',
      'return {ok:true,version:RADAR_COMMERCE_EXTENSION_VERSION,performanceVersion:RADAR_COMMERCE_PERF_R2,densityVersion:RADAR_COMMERCE_DENSITY_R3,provider:"PNCP + Compras.gov.br",',
      'RETURN_VERSION')
    src=one(src,
      'return json({ok:true,performanceVersion:x.performanceVersion,count:x.count,upstream:x.upstream,elapsedMs:x.elapsedMs,upstreamTimeoutMs:x.upstreamTimeoutMs})',
      'return json({ok:true,performanceVersion:x.performanceVersion,densityVersion:x.densityVersion,count:x.count,upstream:x.upstream,elapsedMs:x.elapsedMs,upstreamTimeoutMs:x.upstreamTimeoutMs})',
      'SOURCE_HEALTH')

    invariants=['CHECKOUT_PAID','ASAAS_WEBHOOK_TOKEN','/api/commerce/webhook/asaas','/greenfield/brazil-opportunity-radar/checkout','/greenfield/packvalue-pro/checkout','RADAR_PRICE_BRL = 19.90','RADAR_ACCESS_TTL_MS = 30 * 24 * 60 * 60 * 1000','application/ld+json']
    for x in invariants:
        if x not in src: raise SystemExit('R3_INVARIANT_MISSING:'+x)
    if DENSITY_VERSION not in src: raise SystemExit('R3_DENSITY_MARKER_MISSING')
    pathlib.Path(a.output).write_text(src,encoding='utf-8')
    print('R3_SOURCE_RANKING_PATCH=PASS')
    print('R3_WINDOW_DAYS=90')
    print('R3_PNCP_MODALITIES=5,4')
    print('R3_COMPRAS_MODALITIES=5,6')
    print('R3_TIMEOUT_MS=5000')

if __name__=='__main__': main()
