"""Carousel v2, slide 3 (punch): the one Abbas portrait as a dark teal duotone with grain, headline with a yellow marker,
closing stripe 'אסור ליפול למלכודת הזו'. All text = Smotrich's exact words."""
import os, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
HERE = os.path.dirname(os.path.abspath(__file__))
HAIM = os.path.abspath(os.path.join(HERE, '..', '..', 'fonts', 'HaimClassicv2FM-Bold.ttf'))
W, H = 1080, 1350
DEEP, TEAL, LT, PALE, NIGHT = (43, 81, 85), (80, 146, 153), (105, 180, 189), (173, 213, 217), (14, 26, 28)
RED = (204, 34, 46)
YEL = (255, 222, 0)
def F(s): return ImageFont.truetype(HAIM, s, layout_engine=ImageFont.Layout.RAQM)
src = Image.open(HERE + '/src/abbas.jpg').convert('L')
PH = 900
ph = src.resize((W, int(W * src.height / src.width)), Image.LANCZOS).crop((0, 40, W, 40 + PH))
ph = ImageEnhance.Contrast(ph).enhance(1.25).filter(ImageFilter.UnsharpMask(3, 70, 2))
g = np.asarray(ph).astype(np.float32) / 255
g = np.clip(g + np.random.default_rng(3).normal(0, .03, g.shape), 0, 1)[..., None]
duo = np.array(NIGHT, np.float32) * (1 - g) + np.array((225, 240, 241), np.float32) * g     # teal duotone
im = Image.new('RGB', (W, H), NIGHT); im.paste(Image.fromarray(duo.astype(np.uint8)), (0, 0))
fade = np.clip((np.arange(H) - (PH - 300)) / 300, 0, 1) ** 1.1
im = Image.composite(Image.new('RGB', (W, H), NIGHT), im, Image.fromarray((fade[:, None] * 255).repeat(W, 1).astype(np.uint8)))
d = ImageDraw.Draw(im); R = W - 70
# headline
y = 790
f1 = F(88); t1 = 'עבאס רוצה להיכנס לממשלה'
while d.textlength(t1, font=f1, direction='rtl') > W - 150: f1 = F(f1.size - 3)
d.text((R + 4, y + 5), t1, font=f1, fill=(0, 0, 0), anchor='ra', direction='rtl')
d.text((R, y), t1, font=f1, fill='white', anchor='ra', direction='rtl')
y += 120
f2 = F(88); a2, b2 = 'כדי', 'לחסל את ישראל מבפנים'
wa = d.textlength(a2 + ' ', font=f2, direction='rtl')
while wa + d.textlength(b2, font=f2, direction='rtl') > W - 150: f2 = F(f2.size - 3); wa = d.textlength(a2 + ' ', font=f2, direction='rtl')
d.text((R, y), a2, font=f2, fill='white', anchor='ra', direction='rtl')
wb = d.textlength(b2, font=f2, direction='rtl'); xr = R - wa
bb = d.textbbox((xr, y), b2, font=f2, anchor='ra', direction='rtl')
d.polygon([(xr + 14, bb[1] - 14), (xr - wb - 18, bb[1] - 8), (xr - wb - 12, bb[3] + 16), (xr + 18, bb[3] + 10)], fill=RED)   # hand-laid marker
d.text((xr, y), b2, font=f2, fill='white', anchor='ra', direction='rtl')
# closing stripe
SY = 1080
d.rectangle((0, SY, W, H), fill=TEAL); d.rectangle((0, SY, W, SY + 10), fill=RED)
ft = F(92); t = 'אסור ליפול למלכודת הזו'
while d.textlength(t, font=ft, direction='rtl') > W - 120: ft = F(ft.size - 3)
d.text((W // 2, SY + 48), t, font=ft, fill='white', anchor='ma', direction='rtl')
d.text((W // 2, SY + 175), 'ולהקים ממשלת אסון שתישען על אויבי ישראל.', font=F(42), fill=NIGHT, anchor='ma', direction='rtl')
im.save(HERE + '/slide3.jpg', quality=95); print('ok')
