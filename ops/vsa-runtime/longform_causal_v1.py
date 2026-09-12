#!/usr/bin/env python3
"""Internal 16:9 causal animation generator for VSA longform.

Every family represents a different physical mechanism. Frames are generated
locally with Pillow and encoded with FFmpeg; no external visual asset is used.
"""
from __future__ import annotations

import math
import pathlib
import subprocess
from PIL import Image, ImageChops, ImageDraw, ImageFont

W, H, FPS = 1280, 720, 30
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FAMILIES = {
    "approach",
    "shield_cross_section",
    "solar_panel_retraction",
    "water_cooling_loop",
    "temperature_vs_heat",
    "autonomy_attitude_correction",
    "venus_gravity_assist",
    "solar_wind_to_earth",
    "wispr_geometry",
}

def _font(size: int, bold: bool = False):
    return ImageFont.truetype(BOLD if bold else FONT, size)

def _base(label: str):
    im = Image.new("RGB", (W, H), (4, 13, 32))
    d = ImageDraw.Draw(im, "RGBA")
    d.rounded_rectangle((42, 34, 780, 102), radius=18, fill=(2, 17, 43, 220), outline=(40, 190, 245, 180), width=2)
    d.text((68, 52), label[:46], font=_font(30, True), fill=(250, 252, 255, 255))
    return im, d

def _sun(d, x, y, r):
    d.ellipse((x-r, y-r, x+r, y+r), fill=(250, 112, 20, 255), outline=(255, 205, 50, 255), width=6)
    for k in range(8):
        a = k * math.pi / 4
        x1, y1 = x + math.cos(a) * (r + 15), y + math.sin(a) * (r + 15)
        x2, y2 = x + math.cos(a) * (r + 45), y + math.sin(a) * (r + 45)
        d.line((x1, y1, x2, y2), fill=(255, 190, 40, 180), width=4)

def _craft(d, cx, cy, scale=1.0, angle=0.0, panels=True):
    body_w, body_h = 130*scale, 70*scale
    shield_x = cx + 75*scale
    d.rounded_rectangle((cx-body_w/2, cy-body_h/2, cx+body_w/2, cy+body_h/2), radius=int(14*scale), fill=(35, 110, 175, 255), outline=(130, 220, 255, 255), width=max(2, int(3*scale)))
    d.rectangle((shield_x-7*scale, cy-95*scale, shield_x+7*scale, cy+95*scale), fill=(244, 244, 238, 255))
    if panels:
        d.rectangle((cx-160*scale, cy-58*scale, cx-60*scale, cy-38*scale), fill=(30, 125, 95, 255), outline=(100, 245, 190, 255), width=2)
        d.rectangle((cx-160*scale, cy+38*scale, cx-60*scale, cy+58*scale), fill=(30, 125, 95, 255), outline=(100, 245, 190, 255), width=2)
    return shield_x

def frame(family: str, q: float, label: str) -> Image.Image:
    if family not in FAMILIES:
        raise ValueError("UNKNOWN_CAUSAL_FAMILY:" + family)
    im, d = _base(label)
    cyan=(65,215,255,255); gold=(255,194,61,255); white=(248,250,255,255); blue=(55,135,220,255); red=(255,80,70,255); green=(60,210,145,255)

    if family == "approach":
        _sun(d, 1080, 360, 130)
        x = 220 + 560*(q*q*(3-2*q))
        _craft(d, x, 360, 1.0)
        for y in (260, 360, 460):
            d.line((930, y, x+90, y), fill=(255,190,35,170), width=5)
        d.text((70, 625), "aproximação → fluxo de energia aumenta", font=_font(27), fill=white)

    elif family == "shield_cross_section":
        layers=[(560, (245,245,238,255), "revestimento"),(590,(85,95,105,255),"carbono"),(650,(35,50,65,255),"espuma"),(760,(65,110,150,255),"placa traseira")]
        for x,col,_ in layers:
            d.rectangle((x,155,x+35,565),fill=col)
        ray_end=540
        for y in (230,360,490):
            start=1140; moving=start-(start-ray_end)*min(1,q*1.6)
            d.line((start,y,moving,y),fill=(255,205,40,230),width=7)
        heat=int(255*(0.3+0.7*q))
        d.rectangle((535,135,580,585),outline=(255,100,30,heat),width=8)
        d.polygon([(800,160),(1180,120),(1180,600),(800,560)],fill=(15,45,75,90))
        d.text((820,585),"sombra térmica",font=_font(30,True),fill=cyan)

    elif family == "solar_panel_retraction":
        _sun(d,1080,360,125)
        cx=510; _craft(d,cx,360,1.15,panels=False)
        exposed=1.0-0.72*(q*q*(3-2*q))
        length=250*exposed
        for yy in (270,430):
            d.rectangle((cx-50-length,yy-17,cx-50,yy+17),fill=(25,120,90,255),outline=(95,245,180,255),width=3)
        d.text((76,620),f"área exposta: {int(exposed*100)}%",font=_font(29,True),fill=white)
        d.line((690,190,690,530),fill=(245,245,238,255),width=14)

    elif family == "water_cooling_loop":
        d.rounded_rectangle((90,200,390,520),radius=28,fill=(20,115,85,190),outline=green,width=4)
        d.text((158,334),"PAINÉIS",font=_font(30,True),fill=white)
        d.rounded_rectangle((890,200,1190,520),radius=28,fill=(65,70,88,190),outline=white,width=4)
        d.text((948,334),"RADIADOR",font=_font(30,True),fill=white)
        path=[(390,270),(890,270),(890,450),(390,450),(390,270)]
        d.line(path,fill=(85,180,220,255),width=18,joint="curve")
        seg=q*4; idx=int(seg)%4; t=seg-idx
        a=path[idx]; b=path[idx+1]
        x=a[0]+(b[0]-a[0])*t; y=a[1]+(b[1]-a[1])*t
        col=blue if idx in (0,3) else red
        d.ellipse((x-18,y-18,x+18,y+18),fill=col,outline=white,width=3)
        d.text((410,585),"absorve calor → transporta → dissipa",font=_font(27),fill=white)

    elif family == "temperature_vs_heat":
        d.rectangle((55,145,605,575),outline=(245,125,35,255),width=4)
        d.rectangle((675,145,1225,575),outline=(60,150,235,255),width=4)
        d.text((130,165),"CORONA: energia alta, baixa densidade",font=_font(24,True),fill=(255,170,70,255))
        d.text((735,165),"MEIO DENSO: muitas colisões",font=_font(24,True),fill=(100,190,255,255))
        for i in range(8):
            x=115+((i*79+q*310*(1+i%3))%430); y=245+((i*101+q*190*(1+i%2))%260)
            d.ellipse((x-8,y-8,x+8,y+8),fill=gold)
        for r in range(5):
            for c in range(8):
                x=725+c*60+8*math.sin(q*8+r); y=245+r*58+8*math.cos(q*7+c)
                d.ellipse((x-7,y-7,x+7,y+7),fill=white)
        d.text((400,620),"temperatura ≠ taxa de transferência de calor",font=_font(28,True),fill=cyan)

    elif family == "autonomy_attitude_correction":
        _sun(d,1080,360,110)
        cx,cy=560,360
        tilt=8*math.sin(q*math.pi)
        shield=_craft(d,cx,cy,1.2,panels=True)
        sensor_y=260 if q<0.5 else 460
        alert=min(1, max(0,(q-0.18)*3))*(1-min(1,max(0,(q-0.7)*4)))
        d.ellipse((shield-15,sensor_y-15,shield+15,sensor_y+15),fill=(255,int(80+100*(1-alert)),70,255),outline=white,width=2)
        d.text((78,585),"sensor detecta luz",font=_font(28,True),fill=red if alert>0.2 else white)
        d.text((460,585),"computador calcula",font=_font(28,True),fill=gold)
        d.text((850,585),"atitude corrigida",font=_font(28,True),fill=green if q>0.65 else white)
        d.arc((430,190,760,530),200,200+int(120*q),fill=cyan,width=7)

    elif family == "venus_gravity_assist":
        sx,sy=640,360; _sun(d,sx,sy,65)
        d.ellipse((190,-90,1090,810),outline=(60,130,220,150),width=3)
        d.ellipse((340,60,940,660),outline=(255,190,55,210),width=3)
        venus=(1040,360); d.ellipse((venus[0]-28,venus[1]-28,venus[0]+28,venus[1]+28),fill=(90,145,230,255)); d.text((1000,400),"VÊNUS",font=_font(22,True),fill=white)
        if q<0.52:
            a=-math.pi/2 + (q/0.52)*math.pi/2
            x=sx+450*math.cos(a); y=sy+450*math.sin(a)
        else:
            a=((q-0.52)/0.48)*1.45
            x=sx+300*math.cos(a); y=sy+300*math.sin(a)
        d.ellipse((x-13,y-13,x+13,y+13),fill=white,outline=gold,width=3)
        d.text((315,620),"encontro com Vênus → nova órbita mais interna",font=_font(28,True),fill=cyan)

    elif family == "solar_wind_to_earth":
        _sun(d,145,360,95)
        earth=(1100,360); d.ellipse((earth[0]-45,earth[1]-45,earth[0]+45,earth[1]+45),fill=(45,125,220,255),outline=white,width=3)
        d.ellipse((earth[0]-95,earth[1]-125,earth[0]+95,earth[1]+125),outline=(80,240,175,190),width=5)
        for i in range(18):
            x=255+((i*61+q*930*(1+(i%4)*0.04))%760); y=250+(i*67)%220+20*math.sin(q*8+i)
            d.ellipse((x-6,y-6,x+6,y+6),fill=gold)
        d.text((385,620),"partículas + campo magnético → magnetosfera",font=_font(28,True),fill=white)

    elif family == "wispr_geometry":
        _sun(d,1080,360,115)
        cx=500; shield=_craft(d,cx,360,1.2,panels=False)
        d.polygon([(shield+10,220),(1030,120),(1030,600),(shield+10,500)],fill=(255,190,45,35))
        d.polygon([(cx-35,330),(230,160),(230,560),(cx-35,390)],fill=(80,200,255,55),outline=(70,210,255,170))
        cam=(cx-20,360); d.ellipse((cam[0]-18,cam[1]-18,cam[0]+18,cam[1]+18),fill=cyan)
        sweep=180+170*q
        d.line((cam[0],cam[1],230,sweep),fill=cyan,width=5)
        d.text((80,610),"escudo bloqueia o Sol direto; WISPR observa lateralmente",font=_font(27,True),fill=white)

    return im

def render_causal(family: str, label: str, duration: float, out: pathlib.Path):
    if family not in FAMILIES:
        raise ValueError("UNKNOWN_CAUSAL_FAMILY:" + family)
    frames=max(2,int(duration*FPS))
    proc=subprocess.Popen([
        "ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-an",
        "-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt","yuv420p",str(out)
    ],stdin=subprocess.PIPE)
    first=last=None
    for n in range(frames):
        q=n/max(1,frames-1)
        im=frame(family,q,label)
        if n==0: first=im.copy()
        if n==frames-1: last=im.copy()
        proc.stdin.write(im.tobytes())
    proc.stdin.close()
    rc=proc.wait()
    if rc:
        raise RuntimeError("CAUSAL_RENDER_FAIL:"+family)
    if ImageChops.difference(first,last).getbbox() is None:
        raise RuntimeError("STATIC_CAUSAL_SCENE:"+family)

if __name__ == "__main__":
    raise SystemExit("Use through longform_renderer_v1.py")
