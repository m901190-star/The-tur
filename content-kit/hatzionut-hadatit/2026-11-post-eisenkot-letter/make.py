"""Smotrich IG post (4:5), text only, no logo: Eisenkot's public letter."""
import os, glob, math
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
KB = glob.glob('/root/.claude/skills/synced/*/pro-video-editing/assets/fonts/Karantina-Bold.ttf')[0]
FD = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/fonts/'
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
lab = 'לגדי איזנקוט:'; fl = F(FD + 'Rubik-700.ttf', 44); lw = d.textlength(lab, font=fl, direction='rtl')
d.rounded_rectangle((R - lw - 44, 210, R, 282), 12, fill=LT); d.text((R - 22, 218), lab, font=fl, fill=DEEP, anchor='ra', direction='rtl')
body = 'איזנקוט היה רמטכ״ל והוא יודע מצוין שענייני ביטחון רגישים מנהלים בחדר הסגור ולא בכיכר העיר.'
f = F(FD + 'Rubik-700.ttf', 56); lines = wrap(d, body, f, W - 2 * M - 40); y0 = 350; lh = 80
d.rectangle((R - 6, y0 + 10, R, y0 + lh * len(lines) - 14), fill=LT)
for i, l in enumerate(lines): d.text((R - 34, y0 + i * lh), l, font=f, fill=(255, 255, 255), anchor='ra', direction='rtl')
yb = y0 + lh * len(lines) + 60; d.line((W - M - 220, yb, R, yb), fill=PALE, width=3)
fk = F(KB, 150)
for i, l in enumerate(['תוציא את צה״ל', 'מהפוליטיקה.']): d.text((R, yb + 40 + i * 140), l, font=fk, fill=(255, 255, 255), anchor='ra', direction='rtl')
ty = yb + 40 + 2 * 140 + 30
fh = F(KB, 150); fe = F(FD + 'Rubik-700.ttf', 104)
a = 'פשוט '; aw = d.textlength(a, font=fh, direction='rtl'); b = "Don't."; bw = d.textlength(b, font=fe)
x_right = R; x_left = R - aw - bw - 30
d.rounded_rectangle((x_left - 30, ty + 14, x_right + 10, ty + 170), 16, fill=LT)
d.text((x_right - 20, ty), a, font=fh, fill=DEEP, anchor='ra', direction='rtl'); d.text((x_right - 20 - aw - 8, ty + 40), b, font=fe, fill=DEEP, anchor='ra')
bg.save(HERE + '/post.jpg', quality=95); print(len(lines), ty + 170)
