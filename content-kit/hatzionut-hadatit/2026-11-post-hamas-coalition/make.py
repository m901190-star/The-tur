"""Smotrich IG post (4:5, 1080x1350), no logo. Text exactly as supplied by the user."""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont, features
HERE = os.path.dirname(os.path.abspath(__file__))
RUB = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/fonts/Rubik-700.ttf'
RUB4 = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/fonts/Rubik-400.ttf'
import glob
KAR = glob.glob('/root/.claude/skills/synced/*/pro-video-editing/assets/fonts/Karantina-Bold.ttf')[0]
W, H = 1080, 1350
DEEP, TEAL, LT, PALE, MIST = (43, 81, 85), (80, 146, 153), (105, 180, 189), (173, 213, 217), (234, 242, 243)
BODY = 'מי שבמשך שלוש שנים ואחרי הטבח הנורא ביותר שאירע לעם היהודי מאז השואה לא מסוגל היה להגדיר את חמאס ארגון טרור לא יכול להיות חלק מכל קואליציה, בשום צורה.'
def F(p, s): return ImageFont.truetype(p, s, layout_engine=ImageFont.Layout.RAQM)
def wrap(d, text, font, maxw):
    lines, cur = [], ''
    for w in text.split():
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=font, direction='rtl') <= maxw: cur = t
        else: lines.append(cur); cur = w
    return lines + [cur]
# background: deep teal with soft light from top-right and bottom vignette
bg = Image.new('RGB', (W, H), DEEP); px = bg.load()
import math
for y in range(H):
    for x in range(0, W):
        dx, dy = (x - 820) / 900, (y - 260) / 900; g = max(0, 1 - math.hypot(dx, dy))
        v = 1 - 0.35 * (y / H) ** 2
        px[x, y] = tuple(int((DEEP[i] + (TEAL[i] - DEEP[i]) * g * .9) * v) for i in range(3))
d = ImageDraw.Draw(bg)
# fine diagonal texture
tex = Image.new('L', (W, H), 0); td = ImageDraw.Draw(tex)
for k in range(-H, W, 26): td.line((k, 0, k + H, H), fill=10, width=1)
bg = Image.composite(Image.new('RGB', (W, H), MIST), bg, tex); d = ImageDraw.Draw(bg)
M = 96; R = W - M
f = F(RUB, 60); lines = wrap(d, BODY, f, W - 2 * M - 40); lh = 84; y0 = 210
d.rectangle((R - 6, y0 + 10, R, y0 + lh * len(lines) - 14), fill=LT)
for i, l in enumerate(lines): d.text((R - 34, y0 + i * lh), l, font=f, fill=(255, 255, 255), anchor='ra', direction='rtl')
yb = y0 + lh * len(lines) + 60
d.line((W - M - 220, yb, R, yb), fill=PALE, width=3)
# closer
fk = F(KAR, 170)
d.text((R, yb + 40), 'אחים. יהודים.', font=fk, fill=(255, 255, 255), anchor='ra', direction='rtl')
t2 = 'זמן אחדות.'; tw = d.textlength(t2, font=fk, direction='rtl'); ty = yb + 40 + 160
d.rounded_rectangle((R - tw - 50, ty + 18, R + 10, ty + 178), 16, fill=LT)
d.text((R - 20, ty), t2, font=fk, fill=DEEP, anchor='ra', direction='rtl')
bg.convert('RGB').save(HERE + '/post.jpg', quality=95)
print(len(lines), ty + 178)
