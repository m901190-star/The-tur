"""Carousel v2, slide 1: the real ynet headline as a torn clipping on a dark concrete texture,
yellow marker on 'חמאס הוא ארגון טרור', hand-drawn ring on 'בגוש השינוי'. Text = Smotrich's exact words."""
import os, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
HAIM = os.path.abspath(os.path.join(HERE, '..', '..', 'fonts', 'HaimClassicv2FM-Bold.ttf'))
W, H = 1080, 1350
DEEP, TEAL, LT, PALE, NIGHT = (43, 81, 85), (80, 146, 153), (105, 180, 189), (173, 213, 217), (14, 26, 28)
RED = (204, 34, 46)
YEL = np.array((255, 222, 0), np.float32) / 255
def F(s): return ImageFont.truetype(HAIM, s, layout_engine=ImageFont.Layout.RAQM)
rng = np.random.default_rng(11)

def concrete():
    n = sum(np.asarray(Image.fromarray((rng.random((H // s + 1, W // s + 1)) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), np.float32) * w
            for s, w in [(4, .25), (16, .35), (64, .4)])
    n = (n - n.mean()) / n.std()
    base = np.array(NIGHT, np.float32)[None, None] * (1 + .10 * n[..., None]) + np.array(DEEP, np.float32)[None, None] * .25
    yy, xx = np.mgrid[0:H, 0:W]; v = 1 - .55 * (((xx - W / 2) / W) ** 2 + ((yy - H * .45) / H) ** 2) * 2.2
    return Image.fromarray(np.clip(base * v[..., None], 0, 255).astype(np.uint8))

def torn(card, seed):
    r = np.random.default_rng(seed); w, h = card.size
    m = Image.new('L', (w, h), 255); d = ImageDraw.Draw(m)
    for edge in ('top', 'bot'):
        xs = np.arange(0, w + 10, 10); ys = np.clip(np.cumsum(r.normal(0, 2.4, len(xs))), -8, 8); ys = ys - ys.mean() + 10
        pts = [(x, y if edge == 'top' else h - y) for x, y in zip(xs, ys)]
        d.polygon(pts + ([(w, 0), (0, 0)] if edge == 'top' else [(w, h), (0, h)]), fill=0)
    out = Image.new('RGBA', (w + 140, h + 140), (0, 0, 0, 0))
    sh = Image.new('L', out.size, 0); sh.paste(m, (70 + 16, 70 + 26)); sh = sh.filter(ImageFilter.GaussianBlur(20))
    out.paste(Image.new('RGBA', out.size, (0, 0, 0, 255)), (0, 0), sh.point(lambda v: int(v * .7)))
    c = card.convert('RGBA'); c.putalpha(m); out.alpha_composite(c, (70, 70)); return out

# ---- clipping with marker + ring (drawn in source pixels, then scaled) ----
clip = Image.open(HERE + '/src/h_ynet.jpg').convert('RGB')
a = np.asarray(clip).astype(np.float32) / 255
for (x0, y0, x1, y1) in [(150, 246, 388, 322), (748, 344, 1274, 432)]:       # "חמאס" / "הוא ארגון טרור"
    a[y0:y1, x0:x1] *= YEL
clip = Image.fromarray((a * 255).astype(np.uint8))
cd = ImageDraw.Draw(clip)
# hand-drawn ring around "בגוש השינוי" (two slightly offset strokes)
for k, (dx, dy, wdt) in enumerate([(0, 0, 9), (6, -4, 6)]):
    pts = []
    for t in np.linspace(0, 2 * np.pi * 1.08, 90):
        rx, ry = 238 + 7 * np.sin(3 * t), 50 + 4 * np.cos(2 * t)
        pts.append((710 + dx + rx * np.cos(t), 490 + dy + ry * np.sin(t)))
    cd.line(pts, fill=RED, width=wdt, joint='curve')
CW = 980; clip = clip.resize((CW, int(clip.height * CW / clip.width)), Image.LANCZOS)
card = torn(clip, 5).rotate(-2.2, resample=Image.BICUBIC, expand=True)

im = concrete().convert('RGBA'); d = ImageDraw.Draw(im); R = W - 70
# kicker + giant ironic word
d.text((R, 95), 'מי שיתרשם מההכרזה', font=F(76), fill='white', anchor='ra', direction='rtl')
fz = F(205); t = 'ה״דרמטית״'
while d.textlength(t, font=fz, direction='rtl') > W - 150: fz = F(fz.size - 5)
d.text((R + 6, 190 + 8), t, font=fz, fill=(0, 0, 0, 160), anchor='ra', direction='rtl')
d.text((R, 190), t, font=fz, fill=RED, anchor='ra', direction='rtl')
im.alpha_composite(card, ((W - card.width) // 2, 410))
# bottom punch
fb = F(84); t = 'פשוט לא מכיר את עבאס'
while d.textlength(t, font=fb, direction='rtl') > W - 220: fb = F(fb.size - 3)
bb = d.textbbox((0, 0), t, font=fb, anchor='ls', direction='rtl'); tw, ih = bb[2] - bb[0], bb[3] - bb[1]
y = 1005; d.rectangle((R - tw - 52, y, R + 6, y + ih + 50), fill=LT)
d.text((R - 24, y + 25 - bb[1]), t, font=fb, fill=NIGHT, anchor='rs', direction='rtl')
d.text((R, y + ih + 80), 'ואת השיטה של האחים המוסלמים', font=F(52), fill='white', anchor='ra', direction='rtl')
d.text((70, H - 48), '←', font=F(60), fill=RED, anchor='lm')
im.convert('RGB').save(HERE + '/slide1.jpg', quality=95); print('ok')
