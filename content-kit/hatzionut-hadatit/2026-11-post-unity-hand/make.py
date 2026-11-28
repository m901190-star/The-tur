"""Smotrich IG post (4:5): unity call. Podium photo, then 'not this -> this': the minority government (red, struck through)
vs. 'להושיט יד חזרה לאחים / ולהקים ממשלת אחדות לאומית רחבה'. Exact phrases from his text only."""
import os, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter, ImageEnhance
HERE = os.path.dirname(os.path.abspath(__file__))
HAIM = os.path.abspath(os.path.join(HERE, '..', '..', 'fonts', 'HaimClassicv2FM-Bold.ttf'))
W, H = 1080, 1350
DEEP, TEAL, LT, PALE, NIGHT = (43, 81, 85), (80, 146, 153), (105, 180, 189), (173, 213, 217), (14, 26, 28)
RED, REDT = (204, 34, 46), (236, 70, 78)
def F(s): return ImageFont.truetype(HAIM, s, layout_engine=ImageFont.Layout.RAQM)
def fit(d, t, size, maxw):
    f = F(size)
    while d.textlength(t, font=f, direction='rtl') > maxw: f = F(f.size - 2)
    return f
ph = Image.open(HERE + '/src/smotrich_podium.jpg').convert('RGB')
ph = ImageOps.fit(ph, (W, 1040), Image.LANCZOS, centering=(.5, .12))
ph = ImageEnhance.Contrast(ph).enhance(1.06)
im = Image.new('RGB', (W, H), NIGHT); im.paste(ph, (0, 0))
fade = np.clip((np.arange(H) - 600) / 300, 0, 1) ** 1.0
im = Image.composite(Image.new('RGB', (W, H), NIGHT), im, Image.fromarray((fade[:, None] * 255).repeat(W, 1).astype(np.uint8)))
d = ImageDraw.Draw(im); R = W - 64
y = 862
# kicker
k = 'אני קורא לגדי איזנקוט ולכל חברי הכנסת הציוניים בשמאל'
fk = fit(d, k, 40, W - 150)
d.rectangle((R - 5, y + 6, R, y + 50), fill=LT)
d.text((R - 20, y), k, font=fk, fill='white', anchor='ra', direction='rtl')
y += 76
# NOT this: struck-through in red
n = 'ממשלת מיעוט שנשענת על אויבי ישראל'
fn = fit(d, n, 52, W - 160)
bb = d.textbbox((R, y), n, font=fn, anchor='ra', direction='rtl')
d.text((R, y), n, font=fn, fill=REDT, anchor='ra', direction='rtl')
my = (bb[1] + bb[3]) // 2 + 2
d.line((bb[0] - 10, my + 6, bb[2] + 10, my - 6), fill='white', width=5)
y += 92
# THIS
a, b = 'להושיט יד חזרה', 'לאחים'
fh = F(104)
while d.textlength(a + ' ' + b, font=fh, direction='rtl') > W - 130: fh = F(fh.size - 2)
d.text((R + 5, y + 6), a, font=fh, fill=(0, 0, 0), anchor='ra', direction='rtl')
d.text((R, y), a, font=fh, fill='white', anchor='ra', direction='rtl')
xa = R - d.textlength(a + ' ', font=fh, direction='rtl')
d.text((xa + 5, y + 6), b, font=fh, fill=(0, 0, 0), anchor='ra', direction='rtl')
d.text((xa, y), b, font=fh, fill=LT, anchor='ra', direction='rtl')
y += 132
p = 'ולהקים ממשלת אחדות לאומית רחבה'
fp = fit(d, p, 70, W - 190)
bb = d.textbbox((0, 0), p, font=fp, anchor='ls', direction='rtl'); tw, ih = bb[2] - bb[0], bb[3] - bb[1]
d.rounded_rectangle((R - tw - 52, y, R + 6, y + ih + 44), 14, fill=LT)
d.text((R - 24, y + 22 - bb[1]), p, font=fp, fill=NIGHT, anchor='rs', direction='rtl')
im.save(HERE + '/post.jpg', quality=95); print('bottom', y + ih + 44)
