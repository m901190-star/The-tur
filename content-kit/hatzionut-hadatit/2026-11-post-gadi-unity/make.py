"""Smotrich IG post (4:5), text only, no logo - 'גדי, הגיע הזמן' (same series look as the 'אחים. יהודים. זמן אחדות' post)."""
import os, glob, math
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
KB = glob.glob('/root/.claude/skills/synced/*/pro-video-editing/assets/fonts/Karantina-Bold.ttf')[0]
RUB = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/fonts/Rubik-700.ttf'
W, H = 1080, 1350; DEEP, TEAL, LT, PALE, MIST = (43, 81, 85), (80, 146, 153), (105, 180, 189), (173, 213, 217), (234, 242, 243)
def F(p, s): return ImageFont.truetype(p, s, layout_engine=ImageFont.Layout.RAQM)
def wrap(d, text, font, maxw):
    lines, cur = [], ''
    for w in text.split():
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=font, direction='rtl') <= maxw: cur = t
        else: lines.append(cur); cur = w
    return lines + [cur]
bg = Image.new('RGB', (W, H)); px = bg.load()
for y in range(H):
    for x in range(W):
        g = max(0, 1 - math.hypot((x - 820) / 900, (y - 260) / 900)); v = 1 - .35 * (y / H) ** 2
        px[x, y] = tuple(int((DEEP[i] + (TEAL[i] - DEEP[i]) * g * .9) * v) for i in range(3))
tex = Image.new('L', (W, H), 0); td = ImageDraw.Draw(tex)
for k in range(-H, W, 26): td.line((k, 0, k + H, H), fill=10, width=1)
bg = Image.composite(Image.new('RGB', (W, H), MIST), bg, tex); d = ImageDraw.Draw(bg)
M = 96; R = W - M
from PIL import ImageFilter
tw_ = Image.open(HERE + '/source-tweet.jpg').convert('RGB'); cw = 960; card = tw_.resize((cw, int(cw * tw_.height / tw_.width)), Image.LANCZOS)
m = Image.new('L', card.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, card.width - 1, card.height - 1), 30, fill=255)
sh = Image.new('L', (card.width + 80, card.height + 80), 0); sh.paste(m, (40, 52)); sh = sh.filter(ImageFilter.GaussianBlur(20))
X0 = (W - cw) // 2; TOP = (H - (card.height + 70 + 162)) // 2; bgA = bg.convert('RGBA'); bgA.paste((0, 0, 0, 150), (X0 - 40, TOP - 40), sh); bgA.paste(card, (X0, TOP), m)
od = ImageDraw.Draw(bgA); od.rounded_rectangle((X0, TOP, X0 + cw - 1, TOP + card.height - 1), 30, outline=(105, 180, 189, 160), width=3)
bg = bgA.convert('RGB'); d = ImageDraw.Draw(bg)
y = TOP + card.height + 70
fk = F(KB, 150); d.text((R, y), 'גדי,', font=fk, fill=(255, 255, 255), anchor='ra', direction='rtl')
gw = d.textlength('גדי, ', font=fk, direction='rtl'); t2 = 'הגיע הזמן.'; tw2 = d.textlength(t2, font=fk, direction='rtl')
x2 = R - gw; d.rounded_rectangle((x2 - tw2 - 40, y + 18, x2 + 14, y + 162), 16, fill=LT); d.text((x2 - 10, y), t2, font=fk, fill=DEEP, anchor='ra', direction='rtl')
print(y + 162)
bg.save(HERE + '/post.jpg', quality=95)
