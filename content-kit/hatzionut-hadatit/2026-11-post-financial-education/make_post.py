"""Smotrich IG post (4:5), no party logo: C14 article card with embedded photo + his words."""
import os, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
KB = HERE + '/../../fonts/HaimClassicv2FM-Bold.ttf'
W, H = 1080, 1350; DEEP, TEAL, LT = (43, 81, 85), (80, 146, 153), (105, 180, 189)
def F(s): return ImageFont.truetype(KB, s, layout_engine=ImageFont.Layout.RAQM)
bg = Image.new('RGB', (W, H), DEEP); px = bg.load()
for y in range(H):
    for x in range(W):
        g = max(0, 1 - math.hypot((x - 800) / 900, (y - 300) / 900)); v = 1 - .35 * (y / H) ** 2
        px[x, y] = tuple(int((DEEP[i] + (TEAL[i] - DEEP[i]) * g * .9) * v) for i in range(3))
im = bg.convert('RGBA'); d = ImageDraw.Draw(im)
src = Image.open(HERE + '/article-with-photo.jpg').convert('RGB')
cw = 760; card = src.resize((cw, int(cw * src.height / src.width)), Image.LANCZOS)
m = Image.new('L', card.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, card.width - 1, card.height - 1), 26, fill=255)
sh = Image.new('L', (card.width + 80, card.height + 80), 0); sh.paste(m, (40, 52)); sh = sh.filter(ImageFilter.GaussianBlur(18))
TOP = 45; X0 = (W - cw) // 2; im.paste((0, 0, 0, 120), (X0 - 40, TOP - 40), sh); im.paste(card, (X0, TOP), m)
R = W - 90; y = TOP + card.height + 45
d.rectangle((R - 6, y + 6, R, y + 84), fill=LT)
d.text((R - 30, y + 4), 'ממשיכים לעבוד בכל הכוח.', font=F(72), fill=(255, 255, 255), anchor='ra', direction='rtl')
y2 = y + 112; f2 = F(58); t = 'לכל אזרח, בכל גיל.'; tw = d.textlength(t, font=f2, direction='rtl')
if tw > 860: f2 = F(int(58 * 860 / tw)); tw = d.textlength(t, font=f2, direction='rtl')
d.rounded_rectangle((R - tw - 56, y2 - 4, R + 6, y2 + 80), 14, fill=LT); d.text((R - 26, y2 + 4), t, font=f2, fill=DEEP, anchor='ra', direction='rtl')
im.convert('RGB').save(HERE + '/post.jpg', quality=95); print(y2 + 80)
