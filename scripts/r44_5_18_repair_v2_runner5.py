import time
import traceback
import scripts.r44_5_18_repair_v2_runner3 as r3

job = r3.job
_orig_get = job.requests.get
_orig_post = job.requests.post


def _get(url, *args, **kwargs):
    if '/__ugi_diag_slot02_' not in str(url):
        return _orig_get(url, *args, **kwargs)
    last = None
    for _ in range(20):
        last = _orig_get(url, *args, **kwargs)
        try:
            data = last.json()
            if isinstance(data, dict) and isinstance(data.get('results'), dict):
                return last
        except Exception:
            pass
        time.sleep(3)
    return last


def _post(url, *args, **kwargs):
    if '/__ugi_repair_slot02_v2_' not in str(url):
        return _orig_post(url, *args, **kwargs)
    last = None
    for _ in range(20):
        last = _orig_post(url, *args, **kwargs)
        try:
            data = last.json()
            if isinstance(data, dict) and isinstance(data.get('results'), list):
                return last
        except Exception:
            pass
        time.sleep(3)
    return last

job.requests.get = _get
job.requests.post = _post

if __name__ == '__main__':
    try:
        job.main()
    except BaseException as exc:
        try:
            existing = job.STATUS.read_text(encoding='utf-8').splitlines() if job.STATUS.exists() else []
        except Exception:
            existing = []
        existing += [
            'WRAPPER5_FAILURE=true',
            'ERROR_TYPE=' + type(exc).__name__,
            'ERROR=' + str(exc).replace('\n',' ')[:5000],
            'TRACE=' + traceback.format_exc().replace('\n',' | ')[:9000],
            'OK=false',
        ]
        job.write(existing)
        raise
