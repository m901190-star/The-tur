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
d.text((R, 120), 'גדי,', font=F(KB, 190), fill=(255, 255, 255), anchor='ra', direction='rtl')
f2 = F(KB, 190); t2 = 'הגיע הזמן.'; tw = d.textlength(t2, font=f2, direction='rtl')
d.rounded_rectangle((R - tw - 50, 320, R + 10, 500), 16, fill=LT); d.text((R - 20, 300), t2, font=f2, fill=DEEP, anchor='ra', direction='rtl')
body = 'אני מייחל לכך שידו המושטת של ראש הממשלה תפגוש יד אחות. הציונות הדתית תהיה בשדה הפוליטי בדיוק מה שהיא בשדה הקרב - ראש חץ של אחדות ואחריות לאומית.'
f = F(RUB, 46); lines = wrap(d, body, f, W - 2 * M - 40); y0 = 580; lh = 68
d.rectangle((R - 6, y0 + 8, R, y0 + lh * len(lines) - 12), fill=LT)
for i, l in enumerate(lines): d.text((R - 30, y0 + i * lh), l, font=f, fill=(255, 255, 255), anchor='ra', direction='rtl')
yb = y0 + lh * len(lines) + 50; d.line((W - M - 220, yb, R, yb), fill=PALE, width=3)
fk = F(KB, 140); d.text((R, yb + 30), 'אחים, יהודים.', font=fk, fill=(255, 255, 255), anchor='ra', direction='rtl')
t3 = 'זמן אחדות.'; tw3 = d.textlength(t3, font=fk, direction='rtl'); ty = yb + 30 + 140
d.rounded_rectangle((R - tw3 - 50, ty + 16, R + 10, ty + 150), 16, fill=LT); d.text((R - 20, ty), t3, font=fk, fill=DEEP, anchor='ra', direction='rtl')
bg.save(HERE + '/post.jpg', quality=95); print(len(lines), ty + 150)
