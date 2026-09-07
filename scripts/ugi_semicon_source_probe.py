from pathlib import Path
import subprocess

OUT = Path('public/ugi/editorial/2026-09-08/semicon_probe')
OUT.mkdir(parents=True, exist_ok=True)
VIDEO_URL = 'https://www.youtube.com/watch?v=qflhGjypjYk'

clients = ['web_safari','web_embedded','tv_simply']
report=[]
for client in clients:
    cmd=['yt-dlp','--js-runtimes','node','--extractor-args',f'youtube:player_client={client}','--list-formats',VIDEO_URL]
    p=subprocess.run(cmd,capture_output=True,text=True)
    report.append(f'=== {client} rc={p.returncode} ===\nSTDOUT\n{p.stdout}\nSTDERR\n{p.stderr}\n')
    print(client,p.returncode)
(OUT/'client_probe.txt').write_text('\n'.join(report),encoding='utf-8')
