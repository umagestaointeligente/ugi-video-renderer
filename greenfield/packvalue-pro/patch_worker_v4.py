from __future__ import annotations
import argparse, pathlib, subprocess, sys, tempfile

OLD_LINE = 'headers.set("Content-Disposition", `attachment; filename="${String(grant.fileName || "material-ugi").replace(/[\\"\\\\]/g, "-")}"`);'
NEW_LINE = 'headers.set("Content-Disposition", grant.productId === "packvalue-pro-r1" ? `attachment; filename="packvalue-pro.html"` : `attachment; filename="${String(grant.fileName || "material-ugi").replace(/[\\"\\\\]/g, "-")}"`); // includes("html") ? "html"'
ROUTE_MARKER = '// LSI PackValue PRO — fixed public SKU only; no admin capability.'
ADMIN_ANCHOR = 'if (request.method === "POST" && path === "/api/commerce/checkout") {'
PUBLIC_HEALTH_TOKEN = 'path === "/api/health"'
OLD_PUBLIC_NS = '/api/greenfield/packvalue-pro'
NEW_PUBLIC_NS = '/greenfield/packvalue-pro'
V2_IMAGE_EXPR = 'imageBase64: String(product.checkoutImageBase64 || UGI_CHECKOUT_IMAGE_BASE64)'
GREENFIELD_SAFE_IMAGE_EXPR = 'imageBase64: product?.greenfield === true ? undefined : UGI_CHECKOUT_IMAGE_BASE64'


def move_greenfield_routes_to_public_scope(text: str) -> str:
    if text.count(ROUTE_MARKER) != 1:
        raise SystemExit(f'PACKVALUE_ROUTE_MARKER_COUNT_{text.count(ROUTE_MARKER)}')
    if text.count(PUBLIC_HEALTH_TOKEN) != 1:
        raise SystemExit(f'PACKVALUE_PUBLIC_HEALTH_TOKEN_COUNT_{text.count(PUBLIC_HEALTH_TOKEN)}')
    marker = text.index(ROUTE_MARKER)
    admin = text.index(ADMIN_ANCHOR, marker)
    if marker >= admin:
        raise SystemExit('PACKVALUE_ROUTE_BLOCK_ORDER_INVALID')
    route_block = text[marker:admin]
    without = text[:marker] + text[admin:]
    health = without.index(PUBLIC_HEALTH_TOKEN)
    line_start = without.rfind('\n', 0, health) + 1
    moved = without[:line_start] + route_block + without[line_start:]
    if moved.index(ROUTE_MARKER) > moved.index(PUBLIC_HEALTH_TOKEN):
        raise SystemExit('PACKVALUE_PUBLIC_ROUTE_MOVE_FAILED')
    return moved


def migrate_public_namespace(text: str) -> str:
    n = text.count(OLD_PUBLIC_NS)
    if n < 5:
        raise SystemExit(f'PACKVALUE_OLD_PUBLIC_NAMESPACE_COUNT_{n}')
    migrated = text.replace(OLD_PUBLIC_NS, NEW_PUBLIC_NS)
    if OLD_PUBLIC_NS in migrated:
        raise SystemExit('PACKVALUE_OLD_PUBLIC_NAMESPACE_REMAINS')
    return migrated


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
    if out.count(V2_IMAGE_EXPR) != 1:
        raise SystemExit(f'PACKVALUE_V2_IMAGE_EXPR_COUNT_{out.count(V2_IMAGE_EXPR)}')
    out=out.replace(V2_IMAGE_EXPR,GREENFIELD_SAFE_IMAGE_EXPR,1)
    out=move_greenfield_routes_to_public_scope(out)
    out=migrate_public_namespace(out)
    out_path.write_text(out,encoding='utf-8')
    if out.count('grant.productId === "packvalue-pro-r1" ? `attachment; filename="packvalue-pro.html"`')!=1: raise SystemExit('PACKVALUE_DELIVERY_OVERRIDE_MISSING')
    if out.count(ADMIN_ANCHOR)!=1: raise SystemExit('PACKVALUE_ADMIN_ANCHOR_CHANGED')
    if out.count(PUBLIC_HEALTH_TOKEN)!=1: raise SystemExit('PACKVALUE_PUBLIC_HEALTH_TOKEN_CHANGED')
    if out.index(ROUTE_MARKER) > out.index(PUBLIC_HEALTH_TOKEN): raise SystemExit('PACKVALUE_ROUTE_NOT_PUBLIC_SCOPE')
    if out.count(NEW_PUBLIC_NS) < 5: raise SystemExit('PACKVALUE_NEW_PUBLIC_NAMESPACE_MISSING')
    if out.count(GREENFIELD_SAFE_IMAGE_EXPR)!=1: raise SystemExit('PACKVALUE_GREENFIELD_IMAGE_OMISSION_MISSING')
    if out.count('imageBase64: UGI_CHECKOUT_IMAGE_BASE64')!=0: raise SystemExit('PACKVALUE_LEGACY_IMAGE_ANCHOR_UNEXPECTED')
    print('PATCH_V4_DELIVERY_ADAPTER=PASS')
    print('PATCH_V4_PUBLIC_ROUTE_SCOPE=PASS')
    print('PATCH_V4_PUBLIC_NAMESPACE=PASS')
    print('PATCH_V4_GREENFIELD_OPTIONAL_IMAGE_OMITTED=PASS')

if __name__=='__main__': main()
