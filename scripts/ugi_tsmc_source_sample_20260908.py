from pathlib import Path
import subprocess, json, math

ROOT = Path('public/ugi/editorial/2026-09-08/tsmc-source-qa')
WORK = Path('/tmp/ugi_tsmc_source_sample')
ROOT.mkdir(parents=True, exist_ok=True)
WORK.mkdir(parents=True, exist_ok=True)

SOURCES = {
    'arizona_inside': 'https://www.youtube.com/watch?v=JO9CkKGbDBs',
    'arizona_journey': 'https://www.youtube.com/watch?v=eEsK-GJ9nBU',
    'moving_brilliance': 'https://www.youtube.com/watch?v=0LXVVgYFaCQ',
}

def run(cmd):
    print('RUN', ' '.join(str(x) for x in cmd))
    subprocess.run([str(x) for x in cmd], check=True)

for name, url in SOURCES.items():
    out = WORK / f'{name}.mp4'
    run([
        'yt-dlp', '--no-playlist',
        '-f', 'bv*[height<=480]+ba/b[height<=480]',
        '--merge-output-format', 'mp4',
        '-o', str(out), url,
    ])
    # Create a 5x6 contact sheet sampling one frame every 8 seconds.
    sheet = ROOT / f'{name}_contact.jpg'
    vf = "fps=1/8,scale=320:-2,tile=5x6:padding=4:margin=4:color=black"
    run(['ffmpeg','-y','-i',out,'-vf',vf,'-frames:v','1','-q:v','2',sheet])

(ROOT / 'README.txt').write_text(
    'QA ONLY — official TSMC YouTube sources sampled for editorial visual matching.\n'
    'arizona_inside: https://www.youtube.com/watch?v=JO9CkKGbDBs\n'
    'arizona_journey: https://www.youtube.com/watch?v=eEsK-GJ9nBU\n'
    'moving_brilliance: https://www.youtube.com/watch?v=0LXVVgYFaCQ\n',
    encoding='utf-8'
)
print('DONE')
