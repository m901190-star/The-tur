"""Smotrich IG post (4:5), no party logo: Arutz 7 article (Bnei Menashe aliyah) + his line."""
import os, glob, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
KB = glob.glob('/root/.claude/skills/synced/*/pro-video-editing/assets/fonts/Karantina-Bold.ttf')[0]
RUB = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/fonts/Rubik-700.ttf'
W, H = 1080, 1350; DEEP, TEAL, LT, PALE = (43, 81, 85), (80, 146, 153), (105, 180, 189), (173, 213, 217)
def F(p, s): return ImageFont.truetype(p, s, layout_engine=ImageFont.Layout.RAQM)
bg = Image.new('RGB', (W, H)); px = bg.load()
for y in range(H):
    for x in range(W):
        g = max(0, 1 - math.hypot((x - 800) / 900, (y - 300) / 900)); v = 1 - .35 * (y / H) ** 2
        px[x, y] = tuple(int((DEEP[i] + (TEAL[i] - DEEP[i]) * g * .9) * v) for i in range(3))
im = bg.convert('RGBA'); d = ImageDraw.Draw(im)
src = Image.open(HERE + '/source-article.jpg').convert('RGB')
cw = 760; card = src.resize((cw, int(cw * src.height / src.width)), Image.LANCZOS)
m = Image.new('L', card.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, card.width - 1, card.height - 1), 28, fill=255)
sh = Image.new('L', (card.width + 80, card.height + 80), 0); sh.paste(m, (40, 52)); sh = sh.filter(ImageFilter.GaussianBlur(18))
X0 = (W - cw) // 2; TOP = 55; im.paste((0, 0, 0, 130), (X0 - 40, TOP - 40), sh); im.paste(card, (X0, TOP), m)
R = W - 90; y = TOP + card.height + 60
d.rectangle((R - 6, y + 8, R, y + 196), fill=LT)
for i, l in enumerate(['מימוש החזון הציוני', 'הלכה למעשה.']):
    d.text((R - 30, y + i * 96), l, font=F(KB, 104), fill=(255, 255, 255), anchor='ra', direction='rtl')
y2 = y + 2 * 96 + 36; f2 = F(KB, 96); t = 'ושבו בנים לגבולם.'; tw = d.textlength(t, font=f2, direction='rtl')
d.rounded_rectangle((R - tw - 60, y2 + 10, R + 6, y2 + 110), 14, fill=LT); d.text((R - 26, y2), t, font=f2, fill=DEEP, anchor='ra', direction='rtl')
im.convert('RGB').save(HERE + '/post.jpg', quality=95); print(y2 + 110)
