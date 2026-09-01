#!/usr/bin/env bash
set -euo pipefail

output_path="${1:?output path required}"

ffmpeg -hide_banner -loglevel warning -y \
  -f lavfi -i "color=c=0x10131a:s=1080x1920:r=30:d=3" \
  -vf "drawtext=text='ORBIT TEST':fontcolor=white:fontsize=72:x=(w-text_w)/2:y=(h-text_h)/2" \
  -c:v libx264 -preset veryfast -crf 23 -pix_fmt yuv420p \
  -movflags +faststart "$output_path"
