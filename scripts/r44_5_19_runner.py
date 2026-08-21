# Trigger-safe wrapper for R44.5.19 after workflow registration.
import re
import scripts.r44_5_19_compact as job

_orig_subn = re.subn

def _safe_subn(pattern, repl, string, count=0, flags=0):
    if isinstance(repl, str) and 'function permanentCommercePublicationText' in repl:
        return _orig_subn(pattern, lambda _m: repl, string, count=count, flags=flags)
    return _orig_subn(pattern, repl, string, count=count, flags=flags)

job.re.subn = _safe_subn

if __name__ == '__main__':
    job.main()
