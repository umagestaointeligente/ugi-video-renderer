from pathlib import Path

p = Path('career360/frontend/index.html')
s = p.read_text(encoding='utf-8')
old = '@0a2ea38883094ccf9be4c5fde9ea4efa14617b65/career360/frontend/app-i.js'
new = '@90a795bf1a371be66fd8f907c8a76501f8a5421c/career360/frontend/app-i.js'
if new in s and old not in s:
    print('APP_I_PIN_ALREADY_CURRENT=1')
else:
    count = s.count(old)
    if count != 1:
        raise SystemExit(f'EXPECTED_EXACTLY_ONE_OLD_APP_I_PIN_FOUND_{count}')
    s = s.replace(old, new)
    p.write_text(s, encoding='utf-8')
    print('APP_I_PIN_PATCHED=1')
