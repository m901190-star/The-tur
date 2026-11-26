"""Smotrich IG post (4:5): response to Liberman ('government with a Jewish majority'). Arutz 7 card + his exact words, RZ teal, Haim."""
import os, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
HAIM = os.path.abspath(os.path.join(HERE, '..', '..', 'fonts', 'HaimClassicv2FM-Bold.ttf'))
W, H = 1080, 1350; DEEP, TEAL, LT, PALE, NIGHT = (43, 81, 85), (80, 146, 153), (105, 180, 189), (173, 213, 217), (16, 36, 39)
def F(s): return ImageFont.truetype(HAIM, s, layout_engine=ImageFont.Layout.RAQM)
bg = Image.new('RGB', (W, H)); px = bg.load()
for y in range(H):
    for x in range(W):
        g = max(0, 1 - math.hypot((x - 800) / 900, (y - 300) / 900)); v = 1 - .35 * (y / H) ** 2
        px[x, y] = tuple(int((DEEP[i] + (TEAL[i] - DEEP[i]) * g * .9) * v) for i in range(3))
im = bg.convert('RGBA'); d = ImageDraw.Draw(im)
src = Image.open(HERE + '/source-article.jpg').convert('RGB').crop((30, 25, 968, 760))
cw = 780; card = src.resize((cw, int(cw * src.height / src.width)), Image.LANCZOS)
m = Image.new('L', card.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, card.width - 1, card.height - 1), 28, fill=255)
sh = Image.new('L', (card.width + 80, card.height + 80), 0); sh.paste(m, (40, 52)); sh = sh.filter(ImageFilter.GaussianBlur(18))
X0 = (W - cw) // 2; TOP = 60; im.paste((0, 0, 0, 130), (X0 - 40, TOP - 40), sh); im.paste(card, (X0, TOP), m)
R = W - 80; y = TOP + card.height + 60; f1 = F(100); lh = 100
lines = ['שום משחק מילים', 'לא ימחק']
d.rectangle((R - 6, y + 14, R, y + lh * len(lines) - 6), fill=LT)
for i, l in enumerate(lines): d.text((R - 28, y + i * lh), l, font=f1, fill='white', anchor='ra', direction='rtl')
y2 = y + lh * len(lines) + 28; t = 'את החרפה.'; f2 = F(100)
bb = d.textbbox((0, 0), t, font=f2, anchor='ls', direction='rtl'); tw = bb[2] - bb[0]; ih = bb[3] - bb[1]; pad = 22
d.rounded_rectangle((R - tw - 56, y2, R + 6, y2 + ih + 2 * pad), 14, fill=LT)
d.text((R - 24, y2 + pad - bb[1]), t, font=f2, fill=NIGHT, anchor='rs', direction='rtl')
y3 = y2 + ih + 2 * pad + 44; f3 = F(50)
for i, l in enumerate(['גם היום ישנה חלופה של ממשלת אחדות', 'לאומית יהודית רחבה ויציבה.']):
    d.text((R, y3 + i * 64), l, font=f3, fill=PALE, anchor='ra', direction='rtl')
print('bottom', y3 + 128)
im.convert('RGB').save(HERE + '/post.jpg', quality=95)
