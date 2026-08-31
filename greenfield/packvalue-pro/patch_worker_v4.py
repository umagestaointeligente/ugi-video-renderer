from __future__ import annotations
import argparse, pathlib, subprocess, sys, tempfile

OLD_LINE = 'headers.set("Content-Disposition", `attachment; filename="${String(grant.fileName || "material-ugi").replace(/[\\"\\\\]/g, "-")}"`);'
NEW_LINE = 'headers.set("Content-Disposition", grant.productId === "packvalue-pro-r1" ? `attachment; filename="packvalue-pro.html"` : `attachment; filename="${String(grant.fileName || "material-ugi").replace(/[\\"\\\\]/g, "-")}"`); // includes("html") ? "html"'
ROUTE_MARKER = '// LSI PackValue PRO — fixed public SKU only; no admin capability.'
ADMIN_ANCHOR = 'if (request.method === "POST" && path === "/api/commerce/checkout") {'
PUBLIC_HEALTH_ANCHOR = 'if (request.method === "GET" && path === "/api/health") {'


def move_greenfield_routes_to_public_scope(text: str) -> str:
    if text.count(ROUTE_MARKER) != 1:
        raise SystemExit(f'PACKVALUE_ROUTE_MARKER_COUNT_{text.count(ROUTE_MARKER)}')
    marker = text.index(ROUTE_MARKER)
    admin = text.index(ADMIN_ANCHOR, marker)
    health = text.index(PUBLIC_HEALTH_ANCHOR)
    if not (marker < admin):
        raise SystemExit('PACKVALUE_ROUTE_BLOCK_ORDER_INVALID')
    route_block = text[marker:admin]
    without = text[:marker] + text[admin:]
    health2 = without.index(PUBLIC_HEALTH_ANCHOR)
    # Keep the original route indentation and place it beside the already-public health route,
    # outside the commerce-admin guard. Admin checkout itself remains untouched/protected.
    moved = without[:health2] + route_block + without[health2:]
    if moved.index(ROUTE_MARKER) > moved.index(PUBLIC_HEALTH_ANCHOR):
        raise SystemExit('PACKVALUE_PUBLIC_ROUTE_MOVE_FAILED')
    return moved


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
    out_path=pathlib.Path(a.output)
    out=out_path.read_text(encoding='utf-8')
    out=move_greenfield_routes_to_public_scope(out)
    out_path.write_text(out,encoding='utf-8')
    if out.count('grant.productId === "packvalue-pro-r1" ? `attachment; filename="packvalue-pro.html"`')!=1: raise SystemExit('PACKVALUE_DELIVERY_OVERRIDE_MISSING')
    if out.count(ADMIN_ANCHOR)!=1: raise SystemExit('PACKVALUE_ADMIN_ANCHOR_CHANGED')
    if out.count(PUBLIC_HEALTH_ANCHOR)!=1: raise SystemExit('PACKVALUE_PUBLIC_HEALTH_ANCHOR_CHANGED')
    if out.index(ROUTE_MARKER) > out.index(PUBLIC_HEALTH_ANCHOR): raise SystemExit('PACKVALUE_ROUTE_NOT_PUBLIC_SCOPE')
    print('PATCH_V4_DELIVERY_ADAPTER=PASS')
    print('PATCH_V4_PUBLIC_ROUTE_SCOPE=PASS')

if __name__=='__main__': main()
