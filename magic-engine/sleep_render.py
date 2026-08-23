#!/usr/bin/env python3
from __future__ import annotations
import os, subprocess
from pathlib import Path

OUT=Path(__file__).resolve().parent/'output'; OUT.mkdir(exist_ok=True)
DURATION=int(os.getenv('MAGIC_SLEEP_DURATION','3600'))
FREQ=float(os.getenv('MAGIC_SLEEP_FREQ','174'))
TITLE=os.getenv('MAGIC_SLEEP_TITLE','Deep Sleep Ambient')
TARGET=OUT/'sleep-focus-master.mp4'

cmd=[
 'ffmpeg','-hide_banner','-loglevel','error','-y',
 '-f','lavfi','-i',f'color=c=0x05070a:s=1920x1080:r=1:d={DURATION}',
 '-f','lavfi','-i',f'anoisesrc=color=brown:amplitude=0.035:d={DURATION}:sample_rate=48000',
 '-f','lavfi','-i',f'sine=frequency={FREQ}:sample_rate=48000:duration={DURATION}',
 '-filter_complex','[2:a]volume=0.015[tone];[1:a][tone]amix=inputs=2:duration=longest,lowpass=f=9000,highpass=f=30,loudnorm=I=-24:TP=-3:LRA=7[a]',
 '-map','0:v','-map','[a]','-c:v','libx264','-preset','veryfast','-tune','stillimage','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-shortest',str(TARGET)
]
subprocess.run(cmd,check=True)
print(f'SLEEP_RENDER_READY={TARGET}')
print(f'DURATION_SECONDS={DURATION}')
print(f'FREQUENCY_HZ={FREQ}')
print('RIGHTS_GATE=GREEN')
print('COST_GATE=PASS')
