"""Smotrich IG post (4:5): hypocrisy of 'anyone but Bibi' camp / Haredim joining left. Split portraits Goldknopf | Eisenkot + exact-quote headline."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter, ImageEnhance
HERE = os.path.dirname(os.path.abspath(__file__))
HAIM = os.path.abspath(os.path.join(HERE, '..', '..', 'fonts', 'HaimClassicv2FM-Bold.ttf'))
W, H = 1080, 1350; DEEP, TEAL, LT, PALE, NIGHT = (43, 81, 85), (80, 146, 153), (105, 180, 189), (173, 213, 217), (16, 36, 39)
def F(s): return ImageFont.truetype(HAIM, s, layout_engine=ImageFont.Layout.RAQM)
PH = 800
def portrait(path, cen, w):
    im = Image.open(path).convert('RGB')
    if im.width < 600: im = im.resize((im.width * 3, im.height * 3), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 60, 2))
    im = ImageOps.fit(im, (w, PH), Image.LANCZOS, centering=cen)
    im = ImageOps.grayscale(im).convert('RGB'); im = ImageEnhance.Contrast(im).enhance(1.15); return ImageEnhance.Brightness(im).enhance(.9)
base = Image.new('RGB', (W, H), NIGHT)
L = portrait(HERE + '/eisenkot.jpg', (.5, .35), 640)      # left
R = portrait(HERE + '/goldknopf.jpg', (.5, .25), 640)     # right
base.paste(L, (-60, 0))
m = Image.new('L', (W, PH), 0); ImageDraw.Draw(m).polygon([(560, 0), (W, 0), (W, PH), (480, PH)], fill=255)
rr = Image.new('RGB', (W, PH)); rr.paste(R, (W - 640 + 40, 0)); base.paste(rr, (0, 0), m)
d = ImageDraw.Draw(base)
d.line([(560, 0), (480, PH)], fill=LT, width=10)
g = Image.new('L', (1, 420))
for y in range(420): g.putpixel((0, y), int(255 * (y / 420) ** 1.3))
base.paste(Image.new('RGB', (W, 420), NIGHT), (0, PH - 420 + 40), g.resize((W, 420)))
base.paste(Image.new('RGB', (W, H - PH - 40), NIGHT), (0, PH + 40))
d = ImageDraw.Draw(base); Rr = W - 70; y = 800
f1 = F(96); lines = ['הצביעות של מחנה', 'רק לא ביבי']
d.rectangle((Rr - 6, y + 14, Rr, y + 96 * len(lines) - 6), fill=LT)
for i, l in enumerate(lines): d.text((Rr - 28, y + i * 96), l, font=f1, fill='white', anchor='ra', direction='rtl')
y2 = y + 96 * len(lines) + 26; t = 'נחשפת בשיא מערומיה.'; f2 = F(88)
bb = d.textbbox((0, 0), t, font=f2, anchor='ls', direction='rtl'); tw = bb[2] - bb[0]; ih = bb[3] - bb[1]; pad = 22
d.rounded_rectangle((Rr - tw - 56, y2, Rr + 6, y2 + ih + 2 * pad), 14, fill=LT)
d.text((Rr - 24, y2 + pad - bb[1]), t, font=f2, fill=NIGHT, anchor='rs', direction='rtl')
y3 = y2 + ih + 2 * pad + 46; f3 = F(50)
for i, l in enumerate(['הישענות על תומכי טרור אנטי ציוניים', 'כמו רע״מ תהיה פשע שלא יסולח.']):
    d.text((Rr, y3 + i * 64), l, font=f3, fill=PALE, anchor='ra', direction='rtl')
print('bottom', y3 + 2 * 64)
base.save(HERE + '/post.jpg', quality=95)
