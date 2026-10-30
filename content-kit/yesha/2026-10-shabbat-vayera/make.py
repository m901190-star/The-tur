"""Yesha Council Shabbat post, parashat Vayera (31.10.2026): Abraham at Elonei Mamre in Hebron (Gen 18:1, 13:18).
Post 1080x1350 + story 1080x1920. Typographic, with layered Judean hills at dusk."""
import os, math
import numpy as np
SRC = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/carousel2/make.py'
code = open(SRC).read(); exec(code[:code.index('# 1 — cover')])     # brand helpers
from PIL import Image, ImageDraw, ImageFilter
OUT = os.path.dirname(os.path.abspath(__file__))
WL = Image.open(OUT + '/../../clients/yesha/logo_white.png').convert('RGBA'); WL = WL.crop(WL.getchannel('A').getbbox())
DUSK = (0xF2, 0xC1, 0x7A)

def hills(img, H, top):
    """Four ridges of Judean hills, far (light, hazy) to near (deep navy), plus a warm glow above the horizon."""
    w, h = W * S, H * S
    glow = Image.new('L', (w, h), 0); gd = ImageDraw.Draw(glow)
    gd.ellipse((w * .15, (top - 260) * S, w * .85, (top + 260) * S), fill=150); glow = glow.filter(ImageFilter.GaussianBlur(160 * S))
    img.paste(Image.new('RGB', (w, h), DUSK), (0, 0), glow.point(lambda v: int(v * .55)))
    cols = [(0x4E, 0x86, 0xB4), (0x2E, 0x6A, 0x9E), (0x1C, 0x4C, 0x7C), (0x0E, 0x2A, 0x47)]
    for k, col in enumerate(cols):
        base = top + 40 + k * (80 if H < 1500 else 110); amp = 38 + k * 16; ph = k * 1.7
        pts = [(0, h)]
        for x in range(0, W + 10, 10):
            y = base - amp * (.55 * math.sin(x / 210 + ph) + .3 * math.sin(x / 97 + ph * 2.1) + .15 * math.sin(x / 41 + ph * 3))
            pts.append((x * S, y * S))
        pts.append((w, h)); ImageDraw.Draw(img).polygon(pts, fill=col)

def make(H, name, y0, hill_top):
    img = Image.new('RGB', (W * S, H * S)); d = ImageDraw.Draw(img)
    for y in range(H * S):
        t = y / (H * S); d.line([(0, y), (W * S, y)], fill=tuple(int(DEEP[i] + (BLUE[i] - DEEP[i]) * min(1, t * 1.3)) for i in range(3)))
    # a few stars in the upper sky (Shabbat is coming in)
    rng = np.random.default_rng(3); d = ImageDraw.Draw(img)
    for _ in range(40):
        x, y, r = rng.random() * W, rng.random() * (hill_top - 300), .8 + rng.random() * 1.6
        d.ellipse(P(x - r, y - r, x + r, y + r), fill=(255, 255, 255))
    hills(img, H, hill_top); d = ImageDraw.Draw(img)
    lw = 190 * S; lg = WL.resize((lw, int(lw * WL.height / WL.width)), Image.LANCZOS); img.paste(lg, ((W * S - lw) // 2, (y0) * S), lg)
    c = W / 2; y = y0 + 300
    tx = tw(d, 'פרשת וירא', 50); d.rectangle(P(c - tx / 2 - 34, y - 6, c + tx / 2 + 34, y + 66), fill=LB)
    text(d, (c, y), 'פרשת וירא', 50, DEEP, anchor='ma'); y += 120
    text(d, (c + 6, y + 6), '״וירא אליו ה׳', 150, BLUE, anchor='ma'); text(d, (c, y), '״וירא אליו ה׳', 150, WHITE, anchor='ma'); y += 160
    text(d, (c + 6, y + 6), 'באלני ממרא״', 150, BLUE, anchor='ma'); text(d, (c, y), 'באלני ממרא״', 150, WHITE, anchor='ma'); y += 185
    text(d, (c, y), 'אלוני ממרא אשר בחברון.', 62, SOFT, anchor='ma', bold=False); y += 76
    text(d, (c, y), 'שם ישב אברהם אבינו, ושם אנחנו גם היום.', 62, SOFT, anchor='ma', bold=False)
    text(d, (c, H - (150 if H < 1500 else 260)), 'שבת שלום', 120, WHITE, anchor='ma')
    img.resize((W, H), Image.LANCZOS).save(OUT + f'/{name}.png')

make(1350, 'yesha-shabbat-vayera-post', 70, 1010)
make(1920, 'yesha-shabbat-vayera-story', 260, 1400)
print('ok')
