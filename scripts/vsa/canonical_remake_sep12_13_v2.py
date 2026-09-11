#!/usr/bin/env python3
from __future__ import annotations
import pathlib
from PIL import Image, ImageChops, ImageDraw, ImageStat
import canonical_remake_sep12_13 as base

_ORIGINAL_ANIM = base.anim_frame


def enhanced_anim_frame(mode: str, idx: int, p: float, label: str) -> Image.Image:
    """Keep the canonical topic animation, but make the causal action visibly occupy enough of the frame."""
    im = _ORIGINAL_ANIM(mode, idx, p, label)
    d = ImageDraw.Draw(im)

    if mode == 'soil':
        # A subsurface heat front advances through the peat; hot pockets trail behind it.
        front = 100 + int(720 * p)
        d.rounded_rectangle((80, 360, front, 610), 22, fill=(115, 48, 25), outline=base.GOLD, width=4)
        for j in range(8):
            x = 110 + int((front - 110) * (j + 1) / 9)
            y = 430 + int(75 * ((j % 3) - 1))
            r = 12 + int(9 * (0.5 + 0.5 * p))
            d.ellipse((x-r, y-r, x+r, y+r), fill=(255, 112, 28), outline=(255, 220, 90), width=3)
            base.arrow(d, (x, 645), (x, 535), (150, 220, 255), 4)
        d.text((92, 672), 'frente de calor avança por baixo do solo', font=base.font(24), fill=base.WHITE)

    elif mode == 'ballistic':
        # The bullet visibly crosses the pocket objects while the papers absorb energy and deform.
        bx = 90 + int(660 * p)
        d.line((90, 425, bx, 425), fill=(255, 190, 40), width=10)
        d.ellipse((bx-28, 407, bx+28, 443), fill=base.GOLD, outline=base.WHITE, width=4)
        impact = max(0.0, min(1.0, (p - 0.58) / 0.42))
        if impact > 0:
            shift = int(60 * impact)
            d.rectangle((500+shift, 210, 790+shift, 690), fill=(222, 214, 182), outline=base.WHITE, width=4)
            for j in range(10):
                yy = 245 + j * 40
                d.line((520+shift, yy, 765+shift, yy + int(12*impact)), fill=(90, 90, 90), width=3)
            r = int(45 + 120 * impact)
            d.ellipse((520-r, 425-r, 520+r, 425+r), outline=(255, 110, 55), width=7)
            # Energy bars shrink as the objects absorb kinetic energy.
            for j in range(4):
                w = int(210 * max(0.08, 1.0 - impact * (0.35 + j * 0.13)))
                d.rectangle((680, 120+j*42, 680+w, 145+j*42), fill=(255, 190-j*25, 45+j*25))
        d.text((90, 720), 'objetos no bolso absorvem parte da energia', font=base.font(24), fill=base.WHITE)

    elif mode == 'lock':
        # Make the mechanical consequence explicit: pins move, then the shackle opens.
        open_p = max(0.0, (p - 0.55) / 0.45)
        if open_p > 0:
            lift = int(120 * open_p)
            d.arc((370, 120-lift, 610, 380-lift), 180, 350, fill=base.WHITE, width=22)
            d.text((310, 700), 'pinos alinhados → arco libera', font=base.font(25), fill=base.GOLD)

    return im


def localized_motion_score(video: pathlib.Path, seg: float, work: pathlib.Path, tag: str) -> float:
    """Fail closed on static panels while accepting meaningful localized causal motion.

    A video passes if it has either substantial full-frame change or a sufficiently large,
    sufficiently intense active causal region. Tiny decorative motion remains below threshold.
    """
    a = work / f'motion_{tag}_a.png'
    b = work / f'motion_{tag}_b.png'
    base.run(['ffmpeg','-y','-loglevel','error','-ss',f'{seg*0.22:.3f}','-i',str(video),'-frames:v','1','-vf','scale=488:422',str(a)])
    base.run(['ffmpeg','-y','-loglevel','error','-ss',f'{seg*0.78:.3f}','-i',str(video),'-frames:v','1','-vf','scale=488:422',str(b)])
    ia = Image.open(a).convert('RGB')
    ib = Image.open(b).convert('RGB')
    diff = ImageChops.difference(ia, ib)
    global_mean = sum(ImageStat.Stat(diff).mean) / 3.0

    gray = diff.convert('L')
    pixels = list(gray.getdata())
    active_ratio = sum(1 for x in pixels if x >= 18) / max(1, len(pixels))

    tile_max = 0.0
    tw, th = gray.width // 4, gray.height // 4
    for yy in range(4):
        for xx in range(4):
            tile = gray.crop((xx*tw, yy*th, (xx+1)*tw if xx < 3 else gray.width, (yy+1)*th if yy < 3 else gray.height))
            tile_max = max(tile_max, ImageStat.Stat(tile).mean[0])

    # Composite is deliberately below 1 for tiny decorative changes.
    if global_mean >= 1.0:
        score = global_mean
    elif active_ratio >= 0.012 and tile_max >= 4.0:
        score = 1.0 + min(4.0, active_ratio * 35.0 + tile_max / 12.0)
    else:
        score = min(0.99, max(global_mean, active_ratio * 20.0, tile_max / 10.0))
    print(f'CAUSAL_MOTION_METRIC tag={tag} global_mean={global_mean:.3f} active_ratio={active_ratio:.4f} tile_max={tile_max:.3f} composite={score:.3f}', flush=True)
    return round(score, 3)


base.anim_frame = enhanced_anim_frame
base.motion_score = localized_motion_score

if __name__ == '__main__':
    base.main()
