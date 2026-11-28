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
    f1, f2 = F(60), F(34)
    n, r = 'אבישג', 'בעלת חווה ביהודה ושומרון'
    w1, w2 = d0.textlength(n, font=f1, direction='rtl'), d0.textlength(r, font=f2, direction='rtl')
    logo = None   # client: the union logo belongs in the co-branding, not in the name title
    LS = 210 if logo else 0   # box width (logo is wide)
    bw = int(max(w1, w2) + 54); h1, h2 = 82, 52
    tag = Image.new('RGBA', (bw + LS + (16 if logo else 0), h1 + h2), (0, 0, 0, 0)); d = ImageDraw.Draw(tag)
    x0 = tag.width - bw
    d.rectangle((x0, 0, tag.width, h1), fill=NAVY + (240,))
    d.rectangle((tag.width - 8, 0, tag.width, h1), fill=LB + (255,))
    d.text((tag.width - 28, h1 // 2 + 4), n, font=f1, fill='white', anchor='rm', direction='rtl')
    d.rectangle((x0, h1, x0 + int(w2 + 44), h1 + h2), fill=LB + (255,))
    d.text((x0 + int(w2 + 44) - 22, h1 + h2 // 2 + 2), r, font=f2, fill='white', anchor='rm', direction='rtl')
    if logo:   # logo on a white rounded square to the left of the tag
        BH = h1 + h2
        box = Image.new('RGBA', (LS, BH), (0, 0, 0, 0)); ImageDraw.Draw(box).rounded_rectangle((0, 0, LS - 1, BH - 1), 14, fill=(255, 255, 255, 248))
        lg = logo.copy(); lg.thumbnail((LS - 20, BH - 16), Image.LANCZOS)
        box.alpha_composite(lg, ((LS - lg.width) // 2, (BH - lg.height) // 2)); tag.alpha_composite(box, (0, 0))
    return tag
import cv2
from PIL import ImageFilter
def build_cobrand():
    """white, transparent co-branding: [Farms Union] | [Yesha] — both white like the Yesha logo already in the cut"""
    LH = 112
    ye = Image.open(KIT + '/clients/yesha/logo_white.png').convert('RGBA'); ye = ye.crop(ye.getbbox())
    un = Image.open(HERE + '/src/igud_hachavot_white.png').convert('RGBA'); un = un.crop(un.getbbox())
    ye = ye.resize((int(ye.width * LH / ye.height), LH), Image.LANCZOS)
    un = un.resize((int(un.width * (LH + 6) / un.height), LH + 6), Image.LANCZOS)
    gap = 44; Wc = un.width + gap * 2 + 3 + ye.width; Hc = LH + 6
    c = Image.new('RGBA', (Wc + 40, Hc + 40), (0, 0, 0, 0))
    c.alpha_composite(un, (20, 20)); c.alpha_composite(ye, (20 + un.width + gap * 2 + 3, 20 + 3))   # RTL: Yesha right, union left
    ImageDraw.Draw(c).rectangle((20 + un.width + gap, 20 + 14, 20 + un.width + gap + 2, 20 + Hc - 14), fill=(255, 255, 255, 220))
    sh = c.getchannel('A').filter(ImageFilter.GaussianBlur(7)).point(lambda v: int(v * .45))
    out = Image.new('RGBA', c.size, (0, 0, 0, 0)); out.paste((0, 0, 0, 255), (0, 0), sh)
    out = Image.composite(c, out, c.getchannel('A')) if False else out
    out.alpha_composite(c); return out
def remove_baked_logo(im):
    """the cut has the white Yesha logo baked in at ~(468-615, 160-270): inpaint it so the pair can be centred"""
    a = np.asarray(im.convert('RGB')).copy(); x0, y0, x1, y1 = 430, 130, 660, 300
    reg = a[y0:y1, x0:x1].astype(np.int16); mx, mn = reg.max(2), reg.min(2)
    m = ((mx > 215) & (mx - mn < 40)).astype(np.uint8) * 255
    m = cv2.dilate(m, np.ones((7, 7), np.uint8))
    mask = np.zeros(a.shape[:2], np.uint8); mask[y0:y1, x0:x1] = m
    a = cv2.inpaint(a, mask, 9, cv2.INPAINT_TELEA)
    return Image.fromarray(a)
COB = build_cobrand(); CX, CY = (W - COB.width) // 2, 140
C_IN = 44.99                                  # closing shot (where the Yesha logo appears) -> end
TAG = build_tag(); TX, TY = W - 40 - TAG.width, 960     # right side, above the caption stripe, below the face

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
    if t >= C_IN:
        im = remove_baked_logo(Image.frombytes('RGB', (W, H), b)).convert('RGBA')
        im.alpha_composite(COB, (CX, CY))
        b = im.convert('RGB').tobytes()
    enc.stdin.write(b); i += 1
enc.stdin.close(); enc.wait(); print('done', i, 'logo' if os.path.exists(LOGO) else 'NO LOGO YET')
