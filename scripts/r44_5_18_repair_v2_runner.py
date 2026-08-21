from pathlib import Path
import traceback
import scripts.r44_5_18_repair_v2 as job

if __name__ == '__main__':
    try:
        job.main()
    except BaseException as exc:
        p = job.STATUS
        try:
            existing = p.read_text(encoding='utf-8').splitlines() if p.exists() else []
        except Exception:
            existing = []
        existing += [
            'WRAPPER_FAILURE=true',
            'ERROR_TYPE=' + type(exc).__name__,
            'ERROR=' + str(exc).replace('\n',' ')[:3000],
            'TRACE=' + traceback.format_exc().replace('\n',' | ')[:6000],
            'OK=false',
        ]
        job.write(existing)
        raise
