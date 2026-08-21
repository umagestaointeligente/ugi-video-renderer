import time
import traceback
import scripts.r44_5_18_repair_v2_runner3 as r3

job = r3.job
_orig_wait = job.wait_health

def _wait_with_propagation():
    result = _orig_wait()
    time.sleep(10)
    return result

job.wait_health = _wait_with_propagation

if __name__ == '__main__':
    try:
        job.main()
    except BaseException as exc:
        try:
            existing = job.STATUS.read_text(encoding='utf-8').splitlines() if job.STATUS.exists() else []
        except Exception:
            existing = []
        existing += [
            'WRAPPER4_FAILURE=true',
            'ERROR_TYPE=' + type(exc).__name__,
            'ERROR=' + str(exc).replace('\n',' ')[:4000],
            'TRACE=' + traceback.format_exc().replace('\n',' | ')[:8000],
            'OK=false',
        ]
        job.write(existing)
        raise
