from pathlib import Path
p=Path('career360/frontend/index.html')
s=p.read_text()
old='Enquanto você trabalha na sua carreira, seu agente trabalha na próxima oportunidade.'
new='Você confirma o que importa. O Career 360 organiza sua busca.'
if s.count(old)!=1:
    raise SystemExit(f'old auth copy count={s.count(old)}')
if s.count(new)!=0:
    raise SystemExit('new auth copy unexpectedly already present')
s=s.replace(old,new,1)
for pin in [
'6df7b4e63d7e52ce3c3f02247392b98f0393cbe8/career360/frontend/app-k.js',
'4283646143425e4a3156e44100aabb475df88d27/career360/frontend/app-l.js',
'719c15ebfe89d212a19473b70ea6e615174601d9/career360/frontend/app-m.js']:
    if pin not in s: raise SystemExit(f'missing canonical pin {pin}')
p.write_text(s)
print('V16_STATIC_AUTH_TRUTH_PATCH=PASS')
