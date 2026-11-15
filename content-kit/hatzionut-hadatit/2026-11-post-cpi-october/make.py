"""Smotrich IG post (4:5), no party logo: the CPI article headline card with 'הפתיע' struck through, plus his correction (exact words). Full text goes in the caption."""
import os, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
KB = HERE + '/../../fonts/HaimClassicv2FM-Bold.ttf'
W, H = 1080, 1350; DEEP, TEAL, LT, PALE = (43, 81, 85), (80, 146, 153), (105, 180, 189), (173, 213, 217); RED = (214, 48, 49)
def F(p, s): return ImageFont.truetype(p, s, layout_engine=ImageFont.Layout.RAQM)
bg = Image.new('RGB', (W, H), DEEP); px = bg.load()
for y in range(H):
    for x in range(W):
        g = max(0, 1 - math.hypot((x - 800) / 900, (y - 300) / 900)); v = 1 - .35 * (y / H) ** 2
        px[x, y] = tuple(int((DEEP[i] + (TEAL[i] - DEEP[i]) * g * .9) * v) for i in range(3))
im = bg.convert('RGBA'); d = ImageDraw.Draw(im)
src = Image.open(HERE + '/source-article.jpg').convert('RGB')
pad = Image.new('RGB', (src.width + 80, src.height + 70), (255, 255, 255)); pad.paste(src, (40, 40))
ds = ImageDraw.Draw(pad)                                   # red strike over 'הפתיע' (source x 385-590, y 20-85)
ds.line((40 + 358, 40 + 58, 40 + 572, 40 + 50), fill=RED, width=12)
cw = 900; s = cw / pad.width; card = pad.resize((cw, int(pad.height * s)), Image.LANCZOS)
m = Image.new('L', card.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, card.width - 1, card.height - 1), 28, fill=255)
sh = Image.new('L', (card.width + 80, card.height + 80), 0); sh.paste(m, (40, 52)); sh = sh.filter(ImageFilter.GaussianBlur(18))
TOP = 70; X0 = (W - cw) // 2; im.paste((0, 0, 0, 120), (X0 - 40, TOP - 40), sh); im.paste(card, (X0, TOP), m)
# 'תיקון' tag pinned on the card's top edge, above the struck word
tf = F(KB, 54); tw = d.textlength('תיקון', font=tf, direction='rtl'); tx = X0 + (40 + 460) * s
d.rounded_rectangle((tx - tw / 2 - 26, TOP - 34, tx + tw / 2 + 26, TOP + 40), 14, fill=RED)
d.text((tx, TOP - 30), 'תיקון', font=tf, fill=(255, 255, 255), anchor='ma', direction='rtl')
R = W - 90; y = TOP + card.height + 60
d.rectangle((R - 6, y + 6, R, y + 262), fill=LT)
fk = F(KB, 74)
for i, l in enumerate(['לא מדובר בהפתעה', 'אלא במדיניות', 'ברורה ועיקשת.']):
    d.text((R - 30, y + 8 + i * 86), l, font=fk, fill=(255, 255, 255), anchor='ra', direction='rtl')
y2 = y + 3 * 86 + 48; f2 = F(KB, 62); t = 'גאה להיות חלק מהעם הזה.'; tw = d.textlength(t, font=f2, direction='rtl')
d.rounded_rectangle((R - tw - 56, y2 - 4, R + 6, y2 + 84), 14, fill=LT); d.text((R - 26, y2 + 4), t, font=f2, fill=DEEP, anchor='ra', direction='rtl')
im.convert('RGB').save(HERE + '/post.jpg', quality=95); print(y2 + 84)
