"""Smotrich IG post (4:5), no party logo: Liberman's tweet (as posted) + Smotrich's reply, 'אתה' emphasised."""
import os, glob, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
KB = glob.glob('/root/.claude/skills/synced/*/pro-video-editing/assets/fonts/Karantina-Bold.ttf')[0]
W, H = 1080, 1350; DEEP, TEAL, LT = (43, 81, 85), (80, 146, 153), (105, 180, 189)
def F(p, s): return ImageFont.truetype(p, s, layout_engine=ImageFont.Layout.RAQM)
bg = Image.new('RGB', (W, H)); px = bg.load()
for y in range(H):
    for x in range(W):
        g = max(0, 1 - math.hypot((x - 800) / 900, (y - 300) / 900)); v = 1 - .35 * (y / H) ** 2
        px[x, y] = tuple(int((DEEP[i] + (TEAL[i] - DEEP[i]) * g * .9) * v) for i in range(3))
im = bg.convert('RGBA'); d = ImageDraw.Draw(im)
src = Image.open(HERE + '/source-tweet.jpg').convert('RGB').crop((0, 20, 1080, 1060))   # the tweet as posted
cw = 760; card = src.resize((cw, int(cw * src.height / src.width)), Image.LANCZOS)
m = Image.new('L', card.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, card.width - 1, card.height - 1), 28, fill=255)
sh = Image.new('L', (card.width + 80, card.height + 80), 0); sh.paste(m, (40, 52)); sh = sh.filter(ImageFilter.GaussianBlur(18))
X0 = (W - cw) // 2; TOP = 60; im.paste((0, 0, 0, 130), (X0 - 40, TOP - 40), sh); im.paste(card, (X0, TOP), m)
R = W - 90; y = TOP + card.height + 70
d.rectangle((R - 6, y + 8, R, y + 330), fill=LT)
d.text((R - 30, y), 'איווט,', font=F(KB, 120), fill=(255, 255, 255), anchor='ra', direction='rtl')
f = F(KB, 120); a = 'איתם '; aw = d.textlength(a, font=f, direction='rtl'); y2 = y + 112
d.text((R - 30, y2), a, font=f, fill=(255, 255, 255), anchor='ra', direction='rtl')
b = 'אתה'; bw = d.textlength(b, font=f, direction='rtl'); bx = R - 30 - aw
d.rounded_rectangle((bx - bw - 22, y2 + 14, bx + 10, y2 + 122), 12, fill=(214, 40, 48)); d.text((bx - 6, y2), b, font=f, fill=(255, 255, 255), anchor='ra', direction='rtl')
d.text((R - 30, y2 + 112), 'רוצה למנות יו״ר כנסת?', font=f, fill=(255, 255, 255), anchor='ra', direction='rtl')
im.convert('RGB').save(HERE + '/post.jpg', quality=95); print(y2 + 112 + 120)
