from __future__ import annotations
import requests
import scripts.r44_5_18_repair_v2 as base
import scripts.r44_5_23_store_multi_product as store


def stable_bindings(api, headers):
    r = requests.get(api + f'/versions/{base.STABLE_VERSION_ID}', headers=headers, timeout=30)
    r.raise_for_status()
    return base.restored_bindings(r.json()), base.STABLE_VERSION_ID


store.current_bindings = stable_bindings

if __name__ == '__main__':
    store.main()
