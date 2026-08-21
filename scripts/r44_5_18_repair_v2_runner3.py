import json
import re
import traceback
import scripts.r44_5_18_repair_v2 as job


def _move_block(text, begin, end, active_anchor):
    pat = r'\n?\s*' + re.escape(begin) + r'.*?' + re.escape(end) + r'\s*\n'
    m = re.search(pat, text, flags=re.S)
    if not m:
        raise RuntimeError('temporary block not found: ' + begin)
    block = m.group(0).strip('\n') + '\n\n'
    cleaned = re.sub(pat, '\n', text, count=1, flags=re.S)
    if cleaned.count(active_anchor) != 1:
        raise RuntimeError('active commerce anchor count=' + str(cleaned.count(active_anchor)))
    return cleaned.replace(active_anchor, block + active_anchor, 1)

_orig_diag = job.add_diag_route
_orig_repair = job.add_repair_route
_orig_parse = job.parse_diag


def _diag(source, path, token):
    out = _orig_diag(source, path, token)
    return _move_block(
        out,
        '// BEGIN_R44_5_18_DIAGNOSTIC',
        '// END_R44_5_18_DIAGNOSTIC',
        '      if (request.method === "GET" && path === "/priorizacao") {'
    )


def _repair(source, path, token, details):
    out = _orig_repair(source, path, token, details)
    return _move_block(
        out,
        '// BEGIN_R44_5_18_REPAIR_V2',
        '// END_R44_5_18_REPAIR_V2',
        '      if (request.method === "GET" && path === "/priorizacao") {'
    )


def _parse(diag):
    try:
        existing = job.STATUS.read_text(encoding='utf-8').splitlines() if job.STATUS.exists() else []
    except Exception:
        existing = []
    existing.append('DIAGNOSTIC_RAW=' + json.dumps(diag, ensure_ascii=False, separators=(',', ':'))[:16000])
    job.write(existing)
    return _orig_parse(diag)

job.add_diag_route = _diag
job.add_repair_route = _repair
job.parse_diag = _parse

if __name__ == '__main__':
    try:
        job.main()
    except BaseException as exc:
        try:
            existing = job.STATUS.read_text(encoding='utf-8').splitlines() if job.STATUS.exists() else []
        except Exception:
            existing = []
        existing += [
            'WRAPPER3_FAILURE=true',
            'ERROR_TYPE=' + type(exc).__name__,
            'ERROR=' + str(exc).replace('\n',' ')[:4000],
            'TRACE=' + traceback.format_exc().replace('\n',' | ')[:8000],
            'OK=false',
        ]
        job.write(existing)
        raise
