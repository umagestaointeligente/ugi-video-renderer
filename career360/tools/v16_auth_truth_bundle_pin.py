from pathlib import Path
p=Path('career360/frontend/index.html')
s=p.read_text()
old='@3cd06d176f81e07c6f4dba1f7fb962f73be4ce34/career360/frontend/app-m.js'
new='@719c15ebfe89d212a19473b70ea6e615174601d9/career360/frontend/app-m.js'
if s.count(old)!=1:
    raise SystemExit(f'old app-m pin count={s.count(old)}')
if 'career360/frontend/app-m.js' not in s:
    raise SystemExit('app-m reference missing')
s=s.replace(old,new,1)
if s.count('career360/frontend/app-m.js')!=1:
    raise SystemExit('app-m cardinality invalid')
p.write_text(s)
print('V16_AUTH_TRUTH_BUNDLE_PIN=PASS')
