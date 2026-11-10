"""YouTube thumbnail 1280x720 - Smotrich, first faction meeting of the 26th Knesset. Headline = fragments of his exact quote. No party logo."""
import os, glob, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
KB = glob.glob('/root/.claude/skills/synced/*/pro-video-editing/assets/fonts/Karantina-Bold.ttf')[0]
RUB = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/fonts/Rubik-700.ttf'
W, H = 1280, 720; DEEP, TEAL, LT, PALE = (43, 81, 85), (80, 146, 153), (105, 180, 189), (173, 213, 217)
def F(p, s): return ImageFont.truetype(p, s, layout_engine=ImageFont.Layout.RAQM)
bg = Image.new('RGB', (W, H)); px = bg.load()
for y in range(H):
    for x in range(W):
        g = max(0, 1 - math.hypot((x - 980) / 700, (y - 300) / 600)); v = 1 - .45 * (1 - x / W) ** 1.5
        px[x, y] = tuple(int((DEEP[i] * .55 + (TEAL[i] - DEEP[i] * .55) * g) * v) for i in range(3))
im = bg.convert('RGBA')
# person: right side, bottom-aligned, teal rim glow
p = Image.open(HERE + '/cutout.png').convert('RGBA'); s = 700 / p.height; p = p.resize((int(p.width * s), 700), Image.LANCZOS)
x0 = W - p.width + 110; y0 = H - p.height + 30
a = p.getchannel('A'); glow = Image.new('RGBA', p.size, LT + (0,)); glow.putalpha(a.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v * .8)))
im.alpha_composite(glow, (x0, y0)); im.alpha_composite(p, (x0, y0))
# dark fade so the text side reads
fade = Image.new('RGBA', (W, H), (0, 0, 0, 0)); fd = ImageDraw.Draw(fade)
for x in range(W): fd.line((x, 0, x, H), fill=(10, 25, 28, int(170 * max(0, 1 - x / 640) ** 1.3)))
im.alpha_composite(fade); d = ImageDraw.Draw(im)
R = 640
lab = 'ישיבת הסיעה הראשונה · הכנסת ה־26'; f = F(RUB, 30); tw = d.textlength(lab, font=f, direction='rtl')
d.rounded_rectangle((R - tw - 36, 60, R, 112), 10, fill=(255, 255, 255)); d.text((R - 18, 68), lab, font=f, fill=DEEP, anchor='ra', direction='rtl')
def head(txt, y, size, fill=(255, 255, 255)):
    f = F(KB, size)
    d.text((R + 6, y + 7), txt, font=f, fill=(0, 0, 0, 160), anchor='ra', direction='rtl'); d.text((R, y), txt, font=f, fill=fill, anchor='ra', direction='rtl')
head('יו״ר כנסת', 135, 160)
head('בקולות אויבי ישראל', 292, 98)
f = F(KB, 180); t = 'לא לגיטימי'; tw = d.textlength(t, font=f, direction='rtl')
d.rectangle((R - tw - 50, 450, R + 14, 630), fill=LT); d.text((R - 18, 432), t, font=f, fill=DEEP, anchor='ra', direction='rtl')
d.text((R, 655), 'בצלאל סמוטריץ׳', font=F(RUB, 34), fill=PALE, anchor='ra', direction='rtl')
im.convert('RGB').save(HERE + '/thumbnail.jpg', quality=95); print('ok')
