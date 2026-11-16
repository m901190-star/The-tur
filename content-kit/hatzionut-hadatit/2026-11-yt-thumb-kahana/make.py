"""YouTube thumbnail 1280x720 - Smotrich faction-meeting speech on Matan Kahana / Knesset speaker. Headline = fragments of his exact words. No party logo added; Knesset99 bug hidden by the fade."""
import os, glob, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
KB = glob.glob('/root/.claude/skills/synced/*/pro-video-editing/assets/fonts/Karantina-Bold.ttf')[0]
RUB = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/fonts/Rubik-700.ttf'
W, H = 1280, 720; DEEP, TEAL, LT, PALE = (43, 81, 85), (80, 146, 153), (105, 180, 189), (173, 213, 217)
def F(p, s): return ImageFont.truetype(p, s, layout_engine=ImageFont.Layout.RAQM)
HF = HERE + '/../../fonts/HaimClassicv2FM-Bold.ttf'; OUTN = os.environ.get('OUTN', 'thumbnail.jpg')
def fit(txt, size, maxw):
    f = F(HF, size); dd = ImageDraw.Draw(Image.new('RGB', (1, 1)))
    while dd.textlength(txt, font=f, direction='rtl') > maxw and size > 30: size -= 4; f = F(HF, size)
    return f
# the real frame from the event on the right (background kept), dimmed a little; fades into dark teal on the text side
from PIL import ImageEnhance
src = Image.open(HERE + '/source.jpg').convert('RGB'); sc = 745 / src.height; src = src.resize((int(src.width * sc), 745), Image.LANCZOS)
src = ImageEnhance.Brightness(ImageEnhance.Color(src).enhance(.9)).enhance(.82)
im = Image.new('RGBA', (W, H), (16, 36, 40, 255)); X = 300   # pushes him to the right third
im.paste(src, (X, 0))
fade = Image.new('RGBA', (W, H), (0, 0, 0, 0)); fd = ImageDraw.Draw(fade)
for x in range(W):
    a = int(255 * min(1, max(0, (880 - x) / 330)) ** 1.1) if x < 880 else 0
    fd.line((x, 0, x, H), fill=(16, 36, 40, a))
im.alpha_composite(fade)
vig = Image.new('RGBA', (W, H), (0, 0, 0, 0)); vd = ImageDraw.Draw(vig)
for y in range(H): vd.line((0, y, W, y), fill=(0, 0, 0, int(90 * (y / H) ** 2)))
im.alpha_composite(vig); d = ImageDraw.Draw(im)
R = 690
lab = 'ישיבת סיעת הציונות הדתית'; f = F(RUB, 30); tw = d.textlength(lab, font=f, direction='rtl')
d.rounded_rectangle((R - tw - 36, 60, R, 112), 10, fill=(255, 255, 255)); d.text((R - 18, 68), lab, font=f, fill=DEEP, anchor='ra', direction='rtl')
def head(txt, y, size, fill=(255, 255, 255)):
    f = fit(txt, size, 610)
    d.text((R + 6, y + 7), txt, font=f, fill=(0, 0, 0, 160), anchor='ra', direction='rtl'); d.text((R, y), txt, font=f, fill=fill, anchor='ra', direction='rtl')
head('להתמנות בקולותיהם', 170, 96)
head('של תומכי טרור', 262, 104)
t = 'זה קו אדום'; f = fit(t, 132, 600); tw = d.textlength(t, font=f, direction='rtl')
d.rectangle((R - tw - 50, 430, R + 14, 590), fill=(214, 40, 40)); d.text((R - 22, 444), t, font=f, fill=(255, 255, 255), anchor='ra', direction='rtl')
d.text((R, 655), 'בצלאל סמוטריץ׳', font=F(RUB, 34), fill=PALE, anchor='ra', direction='rtl')
im.convert('RGB').save(HERE + '/' + OUTN, quality=95); print('ok')
