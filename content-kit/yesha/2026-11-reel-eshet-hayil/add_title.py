"""Yesha reel (blurred cut): side name-title while Avishag speaks at the start —
'אבישג / בעלת חווה ביהודה ושומרון' + the Farms Union logo (src/igud_hachavot.png when provided). Yesha palette, no '!'."""
import os, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); KIT = os.path.abspath(HERE + '/../..')
HAIM = KIT + '/fonts/HaimClassicv2FM-Bold.ttf'
SRC = HERE + '/yesha-eshet-hayil-blurred.mp4'; OUT = HERE + '/yesha-eshet-hayil-blurred-title.mp4'
LOGO = HERE + '/src/igud_hachavot.png'
W, H, FPS = 1080, 1920, 30
NAVY, BLUE, LB = (23, 64, 104), (37, 102, 162), (39, 164, 209)
T_IN, T_OUT = 0.5, 9.2                      # Avishag's opening shot runs 0 -> 9.56
def F(s): return ImageFont.truetype(HAIM, s, layout_engine=ImageFont.Layout.RAQM)
def ease(t): t = max(0., min(1., t)); return 1 - (1 - t) ** 3

def build_tag():
    d0 = ImageDraw.Draw(Image.new('RGB', (1, 1)))
    f1, f2 = F(84), F(44)
    n, r = 'אבישג', 'בעלת חווה ביהודה ושומרון'
    w1, w2 = d0.textlength(n, font=f1, direction='rtl'), d0.textlength(r, font=f2, direction='rtl')
    logo = Image.open(LOGO).convert('RGBA') if os.path.exists(LOGO) else None
    LS = 150 if logo else 0
    bw = int(max(w1, w2) + 70); h1, h2 = 112, 70
    tag = Image.new('RGBA', (bw + LS + (16 if logo else 0), h1 + h2), (0, 0, 0, 0)); d = ImageDraw.Draw(tag)
    x0 = tag.width - bw
    d.rectangle((x0, 0, tag.width, h1), fill=NAVY + (240,))
    d.rectangle((tag.width - 10, 0, tag.width, h1), fill=LB + (255,))
    d.text((tag.width - 38, h1 // 2 + 4), n, font=f1, fill='white', anchor='rm', direction='rtl')
    d.rectangle((x0, h1, x0 + int(w2 + 60), h1 + h2), fill=LB + (255,))
    d.text((x0 + int(w2 + 60) - 30, h1 + h2 // 2 + 2), r, font=f2, fill='white', anchor='rm', direction='rtl')
    if logo:   # logo on a white rounded square to the left of the tag
        box = Image.new('RGBA', (LS, LS), (0, 0, 0, 0)); ImageDraw.Draw(box).rounded_rectangle((0, 0, LS - 1, LS - 1), 18, fill=(255, 255, 255, 245))
        lg = logo.copy(); lg.thumbnail((LS - 24, LS - 24), Image.LANCZOS)
        box.alpha_composite(lg, ((LS - lg.width) // 2, (LS - lg.height) // 2)); tag.alpha_composite(box, (0, (h1 + h2 - LS) // 2))
    return tag
TAG = build_tag(); TX, TY = W - 40 - TAG.width, 920     # right side, above the caption stripe, below the face

p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', SRC, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', SRC,
                        '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-pix_fmt', 'yuv420p',
                        '-c:a', 'copy', '-movflags', '+faststart', '-shortest', OUT], stdin=subprocess.PIPE)
i = 0
while True:
    b = p.stdout.read(W * H * 3)
    if len(b) < W * H * 3: break
    t = i / FPS
    if T_IN <= t <= T_OUT + .4:
        im = Image.frombytes('RGB', (W, H), b).convert('RGBA')
        e = ease((t - T_IN) / .45) * (1 - ease((t - T_OUT) / .35))
        tg = TAG.copy(); tg.putalpha(tg.getchannel('A').point(lambda v: int(v * e)))
        im.alpha_composite(tg, (TX + int((1 - e) * 160), TY))
        b = im.convert('RGB').tobytes()
    enc.stdin.write(b); i += 1
enc.stdin.close(); enc.wait(); print('done', i, 'logo' if os.path.exists(LOGO) else 'NO LOGO YET')
