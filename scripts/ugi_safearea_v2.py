from PIL import Image, ImageDraw, ImageFilter

# Conservative vertical safe zone for Reels/TikTok on narrow Android viewports.
SAFE_X = 140
SAFE_W = 800
HEAD_TOP = 175
VIS_TOP = 285
VIS_BOTTOM = 1215
CC_TOP = 1245
CC_BOTTOM = 1475
META_TOP = 1505


def _contain(path, max_w, max_h):
    with Image.open(path) as im:
        im = im.convert('RGB')
        scale = min(max_w / im.width, max_h / im.height)
        nw, nh = max(1, int(im.width * scale)), max(1, int(im.height * scale))
        return im.resize((nw, nh), Image.Resampling.LANCZOS)


def _center_lines(draw, lines, fnt, y, fill, canvas_w=1080, spacing=8):
    for line in lines:
        box = draw.textbbox((0, 0), line, font=fnt)
        tw = box[2] - box[0]
        draw.text(((canvas_w - tw) // 2, y), line, font=fnt, fill=fill)
        y += (box[3] - box[1]) + spacing
    return y


def install(module):
    def safe_video_frame(key, headline, caption, source_label):
        W, H = module.W, module.H
        src = module.source_path(key)

        # Full-frame blurred ambience; never relied on for legibility.
        bg = module.cover(src, W, VIS_BOTTOM + 20).filter(ImageFilter.GaussianBlur(20))
        shade = Image.new('RGBA', bg.size, (0, 0, 0, 105))
        bg = Image.alpha_composite(bg.convert('RGBA'), shade).convert('RGB')

        canvas = Image.new('RGB', (W, H), (13, 15, 18))
        canvas.paste(bg, (0, 0))
        d = ImageDraw.Draw(canvas)

        # Headline stays inside the central safe zone; never touches app chrome.
        hf = module.font(42, True)
        hlines = module.wrap(d, headline, hf, SAFE_W - 30, 2)
        _center_lines(d, hlines, hf, HEAD_TOP, 'white', W, 7)

        # Main photo is CONTAINED, not cover-cropped. This preserves faces/products/logos.
        panel_h = VIS_BOTTOM - VIS_TOP
        d.rounded_rectangle((SAFE_X, VIS_TOP, SAFE_X + SAFE_W, VIS_BOTTOM), radius=26, fill=(20, 22, 26))
        fg = _contain(src, SAFE_W - 24, panel_h - 24)
        px = SAFE_X + (SAFE_W - fg.width) // 2
        py = VIS_TOP + (panel_h - fg.height) // 2
        canvas.paste(fg, (px, py))

        # Dedicated caption band; max two lines; no overlap with the visual.
        d.rounded_rectangle((SAFE_X, CC_TOP, SAFE_X + SAFE_W, CC_BOTTOM), radius=24, fill=(18, 20, 24))
        cf = module.font(34, True)
        clines = module.wrap(d, caption, cf, SAFE_W - 70, 2)
        total = sum((d.textbbox((0, 0), x, font=cf)[3] - d.textbbox((0, 0), x, font=cf)[1]) for x in clines) + 10 * (len(clines) - 1)
        _center_lines(d, clines, cf, CC_TOP + (CC_BOTTOM - CC_TOP - total) // 2, 'white', W, 10)

        # Non-critical metadata is also centered; if platform chrome covers it, core content remains intact.
        mf = module.font(23, True)
        sf = module.font(18)
        d.text((SAFE_X, META_TOP), 'UGI  •  Uma Gestão Inteligente', font=mf, fill=(235, 235, 235))
        source_lines = module.wrap(d, source_label, sf, SAFE_W, 2)
        y = META_TOP + 42
        for line in source_lines:
            d.text((SAFE_X, y), line, font=sf, fill=(176, 181, 188))
            y += 26
        return canvas

    module.video_frame = safe_video_frame
    return module
