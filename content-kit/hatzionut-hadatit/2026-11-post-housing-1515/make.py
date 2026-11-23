"""Smotrich IG post (4:5): 1,515 housing units approved in J&S. C14 article card over the settlement photo + his exact line."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
HERE = os.path.dirname(os.path.abspath(__file__))
HAIM = os.path.abspath(os.path.join(HERE, '..', '..', 'fonts', 'HaimClassicv2FM-Bold.ttf'))
W, H = 1080, 1350
DEEP, TEAL, LT, PALE = (43, 81, 85), (80, 146, 153), (105, 180, 189), (173, 213, 217)
def F(s): return ImageFont.truetype(HAIM, s, layout_engine=ImageFont.Layout.RAQM)

# background: settlement photo (houses + hills), tinted into the party teal, darker toward the text
ph = Image.open(HERE + '/settlement.jpg').convert('RGB').crop((0, 380, 1600, 1200))
bg = ImageOps.fit(ph, (W, H), Image.LANCZOS, centering=(.5, .35))
tint = Image.new('RGB', (W, H), DEEP)
bg = Image.blend(bg, tint, .38)
grad = Image.new('L', (1, H))
for y in range(H):
    t = y / H
    grad.putpixel((0, y), int(255 * min(1, max(0, (t - .40) / .30)) ** 1.2 * .93))
grad = grad.resize((W, H))
bg = Image.composite(Image.new('RGB', (W, H), DEEP), bg, grad)
top = Image.new('L', (1, H))
for y in range(H):
    top.putpixel((0, y), int(150 * max(0, 1 - y / 300)))
bg = Image.composite(Image.new('RGB', (W, H), (20, 40, 43)), bg, top.resize((W, H)))
im = bg.convert('RGBA'); d = ImageDraw.Draw(im)

# article card: C14 header + headline + byline + lead
src = Image.open(HERE + '/source-article.jpg').convert('RGB').crop((0, 0, 1080, 715))
cw = 820; card = src.resize((cw, int(cw * src.height / src.width)), Image.LANCZOS)
m = Image.new('L', card.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, card.width - 1, card.height - 1), 28, fill=255)
sh = Image.new('L', (card.width + 80, card.height + 80), 0); sh.paste(m, (40, 52)); sh = sh.filter(ImageFilter.GaussianBlur(20))
X0 = (W - cw) // 2; TOP = 70
im.paste((0, 0, 0, 150), (X0 - 40, TOP - 40), sh); im.paste(card, (X0, TOP), m)

# his exact words
R = W - 80; y = H - 75 - (86 * 3 + 30 + 106)
lines = ['יהודה ושומרון כבר לא', 'החצר האחורית של', 'מדינת ישראל,']
f1 = F(84); lh = 86
d.rectangle((R - 6, y + 14, R, y + lh * len(lines) - 4), fill=LT)
for i, l in enumerate(lines):
    d.text((R - 30, y + i * lh), l, font=f1, fill=(255, 255, 255), anchor='ra', direction='rtl')
y2 = y + lh * len(lines) + 30; f2 = F(80); t = 'אלא לב הארץ והמדינה.'
tw = d.textlength(t, font=f2, direction='rtl')
bb = d.textbbox((0, 0), t, font=f2, anchor='ls', direction='rtl')  # ink box relative to baseline
ink_h = bb[3] - bb[1]; pad = 22; p0, p1 = y2 + 10, y2 + 10 + ink_h + 2 * pad
d.rounded_rectangle((R - tw - 56, p0, R + 6, p1), 14, fill=LT)
d.text((R - 24, p0 + pad - bb[1]), t, font=f2, fill=DEEP, anchor='rs', direction='rtl')
print('bottom', p1)
im.convert('RGB').save(HERE + '/post.jpg', quality=95)
