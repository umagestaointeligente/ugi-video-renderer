import json
import traceback
import scripts.r44_5_18_repair_v2 as job

_orig = job.parse_diag

def _logged(diag):
    try:
        existing = job.STATUS.read_text(encoding='utf-8').splitlines() if job.STATUS.exists() else []
    except Exception:
        existing = []
    existing.append('DIAGNOSTIC_RAW=' + json.dumps(diag, ensure_ascii=False, separators=(',', ':'))[:12000])
    job.write(existing)
    return _orig(diag)

job.parse_diag = _logged

if __name__ == '__main__':
    try:
        job.main()
    except BaseException as exc:
        try:
            existing = job.STATUS.read_text(encoding='utf-8').splitlines() if job.STATUS.exists() else []
        except Exception:
            existing = []
        existing += [
            'WRAPPER2_FAILURE=true',
            'ERROR_TYPE=' + type(exc).__name__,
            'ERROR=' + str(exc).replace('\n',' ')[:3000],
            'TRACE=' + traceback.format_exc().replace('\n',' | ')[:6000],
            'OK=false',
        ]
        job.write(existing)
        raise
