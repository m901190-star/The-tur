"""Smotrich IG post (4:5), no party logo: the N12 frame (cropped from the screenshot, no Telegram UI) + his closing line. Full text goes in the caption."""
import os, glob, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
FD = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/fonts/'
KB = glob.glob('/root/.claude/skills/synced/*/pro-video-editing/assets/fonts/Karantina-Bold.ttf')[0]
W, H = 1080, 1350; DEEP, TEAL, LT, PALE, MIST = (43, 81, 85), (80, 146, 153), (105, 180, 189), (173, 213, 217), (234, 242, 243)
def F(p, s): return ImageFont.truetype(p, s, layout_engine=ImageFont.Layout.RAQM)
bg = Image.new('RGB', (W, H), DEEP); px = bg.load()
for y in range(H):
    for x in range(W):
        g = max(0, 1 - math.hypot((x - 800) / 900, (y - 300) / 900)); v = 1 - .35 * (y / H) ** 2
        px[x, y] = tuple(int((DEEP[i] + (TEAL[i] - DEEP[i]) * g * .9) * v) for i in range(3))
im = bg.convert('RGBA'); d = ImageDraw.Draw(im)
full = Image.open(HERE + '/source-screenshot.jpg').convert('RGB')
# keep the Telegram look so it's clear this was posted on Amit Segal's channel: channel header + the post (video frame + text);
# drop the unrelated pinned-message bar and the reactions/views row
hdr = full.crop((0, 0, full.width, 150)); post = full.crop((0, 300, full.width, 1062))
src = Image.new('RGB', (full.width, hdr.height + post.height), (0, 0, 0)); src.paste(hdr, (0, 0)); src.paste(post, (0, hdr.height))
cw = 880; card = src.resize((cw, int(cw * src.height / src.width)), Image.LANCZOS)
m = Image.new('L', card.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, card.width - 1, card.height - 1), 30, fill=255)
sh = Image.new('L', (card.width + 80, card.height + 80), 0); sh.paste(m, (40, 52)); sh = sh.filter(ImageFilter.GaussianBlur(18))
TOP = 60; X0 = (W - cw) // 2; im.paste((0, 0, 0, 120), (X0 - 40, TOP - 40), sh); im.paste(card, (X0, TOP), m)
d.text((X0 + cw - 6, TOP + card.height + 16), 'פורסם בערוץ הטלגרם של עמית סגל', font=F(FD + 'Rubik-700.ttf', 32), fill=PALE, anchor='ra', direction='rtl')
R = W - 90; y = TOP + card.height + 85
d.rectangle((R - 6, y + 6, R, y + 196), fill=LT)
fk = F(KB, 96)
for i, l in enumerate(['חייבים לתקן את', 'מערכת המשפט הישראלית.']):
    d.text((R - 30, y + i * 92), l, font=fk, fill=(255, 255, 255), anchor='ra', direction='rtl')
y2 = y + 2 * 92 + 34; f2 = F(KB, 96); t = 'פשוט חייבים. זה בנפשנו.'; tw = d.textlength(t, font=f2, direction='rtl')
d.rounded_rectangle((R - tw - 60, y2 + 10, R + 6, y2 + 110), 14, fill=LT); d.text((R - 26, y2), t, font=f2, fill=DEEP, anchor='ra', direction='rtl')
im.convert('RGB').save(HERE + '/post.jpg', quality=95); print(y2 + 138)
