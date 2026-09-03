from __future__ import annotations

import ugi_20260903_content_recovery as recovery

for item in recovery.ITEMS:
    item.setdefault("result_support", "Aplicação prática UGI")

if __name__ == "__main__":
    raise SystemExit(recovery.main())
