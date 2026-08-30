from __future__ import annotations
import argparse, pathlib, subprocess, sys, tempfile

OLD_LINE = 'headers.set("Content-Disposition", `attachment; filename="${String(grant.fileName || "material-ugi").replace(/[\\"\\\\]/g, "-")}"`);'
NEW_LINE = 'headers.set("Content-Disposition", grant.productId === "packvalue-pro-r1" ? `attachment; filename="packvalue-pro.html"` : `attachment; filename="${String(grant.fileName || "material-ugi").replace(/[\\"\\\\]/g, "-")}"`); // includes("html") ? "html"'

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--asset',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    source=pathlib.Path(a.source).read_text(encoding='utf-8')
    n=source.count(OLD_LINE)
    if n!=1: raise SystemExit(f'R44_5_23_DELIVERY_EXACT_COUNT_{n}')
    pre=source.replace(OLD_LINE,NEW_LINE,1)
    with tempfile.TemporaryDirectory() as td:
        staged=pathlib.Path(td)/'staged.mjs'; staged.write_text(pre,encoding='utf-8')
        cmd=[sys.executable,str(pathlib.Path(__file__).with_name('patch_worker_v2.py')),'--source',str(staged),'--asset',a.asset,'--output',a.output]
        subprocess.run(cmd,check=True)
    out=pathlib.Path(a.output).read_text(encoding='utf-8')
    if out.count('grant.productId === "packvalue-pro-r1" ? `attachment; filename="packvalue-pro.html"`')!=1: raise SystemExit('PACKVALUE_DELIVERY_OVERRIDE_MISSING')
    print('PATCH_V4_DELIVERY_ADAPTER=PASS')

if __name__=='__main__': main()
