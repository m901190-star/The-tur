"""YouTube thumbnail 1280x720 - Smotrich, first faction meeting of the 26th Knesset. Headline = fragments of his exact quote. No party logo."""
import os, glob, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
KB = glob.glob('/root/.claude/skills/synced/*/pro-video-editing/assets/fonts/Karantina-Bold.ttf')[0]
RUB = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/fonts/Rubik-700.ttf'
W, H = 1280, 720; DEEP, TEAL, LT, PALE = (43, 81, 85), (80, 146, 153), (105, 180, 189), (173, 213, 217)
def F(p, s): return ImageFont.truetype(p, s, layout_engine=ImageFont.Layout.RAQM)
# the real frame from the event on the right (background kept), dimmed a little; fades into dark teal on the text side
from PIL import ImageEnhance
src = Image.open(HERE + '/source.jpg').convert('RGB'); sc = 760 / src.height; src = src.resize((int(src.width * sc), 760), Image.LANCZOS)
src = ImageEnhance.Brightness(ImageEnhance.Color(src).enhance(.9)).enhance(.82)
im = Image.new('RGBA', (W, H), (16, 36, 40, 255)); X = W - src.width + 330   # pushes him to the right third
im.paste(src, (X, -20))
fade = Image.new('RGBA', (W, H), (0, 0, 0, 0)); fd = ImageDraw.Draw(fade)
for x in range(W):
    a = int(255 * min(1, max(0, (760 - x) / 380)) ** 1.2) if x < 760 else 0
    fd.line((x, 0, x, H), fill=(16, 36, 40, a))
im.alpha_composite(fade)
vig = Image.new('RGBA', (W, H), (0, 0, 0, 0)); vd = ImageDraw.Draw(vig)
for y in range(H): vd.line((0, y, W, y), fill=(0, 0, 0, int(90 * (y / H) ** 2)))
im.alpha_composite(vig); d = ImageDraw.Draw(im)
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
