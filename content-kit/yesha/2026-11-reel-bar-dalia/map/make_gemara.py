"""Gemara beat (9:16): parchment-toned page, slow push, gold highlighter sweeps across 'אנשי בר דליה' (both mentions)."""
import os, sys, glob, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
HERE = os.path.dirname(os.path.abspath(__file__))
SEC = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/shalev/fonts/SecularOne.ttf'
W, H, FPS = 1080, 1920, 30; BLUE = (0x25, 0x66, 0xA2); WHITE = (255, 255, 255)
def F(p, s): return ImageFont.truetype(p, s, layout_engine=ImageFont.Layout.RAQM)
def eo(x): x = max(0., min(1., x)); return 1 - (1 - x) ** 3
src = ImageOps.grayscale(Image.open(HERE + '/source-gemara.jpg'))
page = ImageOps.colorize(src, black=(52, 34, 18), white=(238, 224, 192))          # ink on parchment
n = (np.random.default_rng(3).normal(0, 7, (page.height, page.width, 1))).astype(np.int16)
page = Image.fromarray(np.clip(np.asarray(page).astype(np.int16) + n, 0, 255).astype('uint8'))
vig = Image.new('L', page.size, 0); vd = ImageDraw.Draw(vig)
for k in range(60): vd.rectangle((k * 4, k * 4, page.width - k * 4, page.height - k * 4), outline=int(120 * (1 - k / 60)))
page = Image.composite(Image.new('RGB', page.size, (90, 60, 30)), page, vig.filter(ImageFilter.GaussianBlur(30)))
HL = [(430, 52, 765, 118), (54, 160, 170, 216), (1040, 238, 1275, 302)]     # 'אנשי בר דליה' (line 1), 'אנשי' + 'בר דליה' (lines 2-3)
S = W / 1320; PGs = page.resize((W, int(page.height * S)), Image.LANCZOS)
CANVAS = Image.new('RGB', (W, H), (40, 28, 16)); CANVAS.paste(PGs, (0, (H - PGs.height) // 2)); OY = (H - PGs.height) // 2
def frame(t, T=5.4):
    k1 = eo(t / 2.6) * .12; k2 = eo((t - 2.6) / (T - 2.6)) if t > 2.6 else 0
    z = 1.0 + k1 + .55 * k2
    tx, ty = 600 * S, 85 * S + OY                                              # final focus: line 1
    cx = W / 2 + (tx - W / 2) * k2; cy = H / 2 + (ty + 260 - H / 2) * k2
    w, h = W / z, H / z; cx = min(max(cx, w / 2), W - w / 2); cy = min(max(cy, h / 2), H - h / 2)
    im = CANVAS.crop((int(cx - w / 2), int(cy - h / 2), int(cx + w / 2), int(cy + h / 2))).resize((W, H), Image.BILINEAR).convert('RGBA')
    def sp(x, y): return (W / 2 + (x * S - cx) * z, H / 2 + (y * S + OY - cy) * z)
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for i, (x0, y0, x1, y1) in enumerate(HL):
        st = .5 + i * .55; p = eo((t - st) / .5)
        if p <= 0: continue
        a = sp(x0, y0); b = sp(x1, y1); xr = b[0]; xl = xr - (b[0] - a[0]) * p
        d.rounded_rectangle((xl - 5, a[1] + 3, xr + 5, b[1] + 2), 7, fill=(255, 205, 60, 120))
    im.alpha_composite(lay)
    lab = 'תלמוד ירושלמי'; f = F(SEC, 54); dd = ImageDraw.Draw(im); tw = dd.textlength(lab, font=f, direction='rtl')
    L = Image.new('RGBA', (int(tw) + 60, 90), (0, 0, 0, 0)); ld = ImageDraw.Draw(L); ld.rounded_rectangle((0, 0, L.width - 1, 89), 14, fill=BLUE); ld.text((L.width / 2, 12), lab, font=f, fill=WHITE, anchor='ma', direction='rtl')
    L.putalpha(L.getchannel('A').point(lambda v: int(v * eo((t - .2) / .4)))); im.alpha_composite(L, (int(W / 2 - L.width / 2), 260))
    return im.convert('RGB')
if __name__ == '__main__':
    if 'stills' in sys.argv:
        ims = [frame(x).resize((270, 480)) for x in [.3, 1.4, 2.6, 5.2]]; sh = Image.new('RGB', (4 * 274, 480), WHITE)
        for i, x in enumerate(ims): sh.paste(x, (i * 274, 0))
        sh.save(HERE + '/gemara-stills.jpg'); sys.exit()
