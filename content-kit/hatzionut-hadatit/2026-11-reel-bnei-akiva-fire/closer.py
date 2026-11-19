"""Closing card: 'שבת ארגון מוצלחת!' + RZ logo, 3s, 720x1280, embers rising."""
import os, subprocess, random, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.abspath(os.path.join(HERE, '..', '..'))
FONT = os.path.join(KIT, 'fonts', 'HaimClassicv2FM-Bold.ttf')
LOGO = os.path.join(KIT, 'clients', 'hatzionut-hadatit', 'logo.png')
OUT = os.path.join(HERE, 'shots', 'shot8_closer.mp4')

W, H, FPS, DUR = 720, 1280, 30, 3.0
DEEP, TEAL, LT = (43, 81, 85), (80, 146, 153), (105, 180, 189)
DARK = (14, 28, 30)

random.seed(7)
embers = [dict(x=random.uniform(0, W), y=random.uniform(H * 0.3, H * 1.2),
               v=random.uniform(40, 120), r=random.uniform(1.5, 4.0),
               ph=random.uniform(0, 6.28), a=random.uniform(0.5, 1.0)) for _ in range(70)]

# background: radial-ish gradient DEEP centre -> DARK edges, warm glow at bottom
bg = Image.new('RGB', (W, H), DARK)
d = ImageDraw.Draw(bg)
for i in range(60, 0, -1):
    t = i / 60
    c = tuple(int(DARK[k] + (DEEP[k] - DARK[k]) * (1 - t)) for k in range(3))
    d.ellipse([W / 2 - W * t * 1.1, H * 0.42 - H * t * 0.75, W / 2 + W * t * 1.1, H * 0.42 + H * t * 0.75], fill=c)
glow = Image.new('RGB', (W, H), (0, 0, 0))
ImageDraw.Draw(glow).ellipse([-200, H - 260, W + 200, H + 300], fill=(150, 60, 10))
glow = glow.filter(ImageFilter.GaussianBlur(120))
bg = Image.blend(bg, Image.eval(glow, lambda v: v), 0.0)
bg = Image.composite(bg, bg, Image.new('L', (W, H), 255))
bg_arr = bg
from PIL import ImageChops
bg = ImageChops.add(bg, glow.point(lambda v: int(v * 0.55)))

# text layer
font = ImageFont.truetype(FONT, 92)
txt = 'שבת ארגון מוצלחת!'
tl = Image.new('RGBA', (W, H), (0, 0, 0, 0))
td = ImageDraw.Draw(tl)
bb = td.textbbox((0, 0), txt, font=font, direction='rtl', language='he')
tw = bb[2] - bb[0]
if tw > W - 80:
    font = ImageFont.truetype(FONT, int(92 * (W - 80) / tw))
    bb = td.textbbox((0, 0), txt, font=font, direction='rtl', language='he')
    tw = bb[2] - bb[0]
ty = int(H * 0.36)
td.text(((W - tw) / 2 - bb[0], ty), txt, font=font, fill=(255, 255, 255, 255), direction='rtl', language='he')
# underline accent
lw = 140
td.rectangle([(W - lw) / 2, ty + (bb[3] - bb[1]) + 40, (W + lw) / 2, ty + (bb[3] - bb[1]) + 46], fill=LT + (255,))
shadow = tl.filter(ImageFilter.GaussianBlur(10))

logo = Image.open(LOGO).convert('RGBA')
lw_ = 420
logo = logo.resize((lw_, int(logo.height * lw_ / logo.width)), Image.LANCZOS)
ly = int(H * 0.56)

def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)

frames_dir = os.path.join(HERE, 'shots', '_closer_frames')
os.makedirs(frames_dir, exist_ok=True)
n = int(DUR * FPS)
for f in range(n):
    t = f / FPS
    im = bg.copy().convert('RGBA')
    # embers
    el = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ed = ImageDraw.Draw(el)
    for e in embers:
        y = (e['y'] - e['v'] * t) % (H * 1.2) - H * 0.1
        x = e['x'] + 14 * math.sin(e['ph'] + t * 2.2)
        fl = 0.6 + 0.4 * math.sin(e['ph'] * 3 + t * 9)
        a = int(255 * e['a'] * fl * min(1, max(0, (y / H))))
        r = e['r']
        ed.ellipse([x - r, y - r, x + r, y + r], fill=(255, 150, 50, a))
    el_glow = el.filter(ImageFilter.GaussianBlur(4))
    im = Image.alpha_composite(im, el_glow)
    im = Image.alpha_composite(im, el)
    # text fade-in + slight rise
    a1 = ease((t - 0.3) / 0.7)
    if a1 > 0:
        off = int((1 - a1) * 24)
        layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        sh = shadow.copy(); sh.putalpha(sh.getchannel('A').point(lambda v: int(v * 0.8 * a1)))
        layer.alpha_composite(sh, (0, off + 4))
        tx = tl.copy(); tx.putalpha(tx.getchannel('A').point(lambda v: int(v * a1)))
        layer.alpha_composite(tx, (0, off))
        im = Image.alpha_composite(im, layer)
    a2 = ease((t - 0.9) / 0.7)
    if a2 > 0:
        lg = logo.copy(); lg.putalpha(lg.getchannel('A').point(lambda v: int(v * a2)))
        im.alpha_composite(lg, ((W - lw_) // 2, ly + int((1 - a2) * 20)))
    # fade from black at start
    fb = 1 - ease(t / 0.35)
    if fb > 0:
        im = Image.blend(im, Image.new('RGBA', (W, H), (0, 0, 0, 255)), fb)
    im.convert('RGB').save(os.path.join(frames_dir, f'{f:04d}.png'))

subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', str(FPS), '-i', os.path.join(frames_dir, '%04d.png'),
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', os.path.join(HERE, 'shots', '_closer_v.mp4')], check=True)
print('ok')
