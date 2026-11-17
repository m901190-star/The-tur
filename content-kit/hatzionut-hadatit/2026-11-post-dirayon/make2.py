"""V2 – RZ style: teal duotone Kahana photo, context pill, big Haim 'לדיראון / עולם.' with teal bar, Smotrich attribution. No logo."""
import os, numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); W, H = 1080, 1350
KB = HERE + '/../../fonts/HaimClassicv2FM-Bold.ttf'; RUB = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/fonts/Rubik-700.ttf'
DEEP, TEAL, LT, PALE, NIGHT = (43, 81, 85), (80, 146, 153), (105, 180, 189), (173, 213, 217), (14, 32, 35)
def F(p, s): return ImageFont.truetype(p, s, layout_engine=ImageFont.Layout.RAQM)
ph = Image.open(HERE + '/kahana.jpg').convert('RGB').filter(ImageFilter.GaussianBlur(2.2))
ph = ImageOps.fit(ph, (W, 900), Image.LANCZOS, centering=(.5, .25))
g = np.array(ImageOps.autocontrast(ImageOps.grayscale(ph), cutoff=1)).astype(np.float32) / 255
lo, hi = np.array(NIGHT, np.float32), np.array(PALE, np.float32)
duo = (lo + (hi - lo) * g[..., None] ** 1.1).clip(0, 255).astype(np.uint8)
im = Image.new('RGBA', (W, H), NIGHT + (255,)); im.paste(Image.fromarray(duo), (0, 0))
ov = Image.new('RGBA', (W, H)); od = ImageDraw.Draw(ov)
for y in range(H): od.line((0, y, W, y), fill=NIGHT + (int(255 * min(1, max(0, (y - 520) / 380)) ** 1.2),))
for y in range(160): od.line((0, y, W, y), fill=NIGHT + (int(120 * (1 - y / 160)),))
im.alpha_composite(ov); d = ImageDraw.Draw(im)
R = W - 80
pill = 'מתן כהנא נבחר ליו״ר הכנסת'; fp = F(RUB, 38); pw = d.textlength(pill, font=fp, direction='rtl')
d.rounded_rectangle((R - pw - 50, 60, R, 124), 32, fill=(255, 255, 255)); d.text((R - 25, 92), pill, font=fp, fill=DEEP, anchor='rm', direction='rtl')
fh = F(KB, 210); y = 860
d.text((R + 8, y + 8), 'לדיראון', font=fh, fill=DEEP, anchor='rs', direction='rtl'); d.text((R, y), 'לדיראון', font=fh, fill=(255, 255, 255), anchor='rs', direction='rtl')
t = 'עולם.'; tw = d.textlength(t, font=fh, direction='rtl')
d.rectangle((R - tw - 60, y + 40, R + 20, y + 270), fill=LT); d.text((R - 22, y + 245), t, font=fh, fill=NIGHT, anchor='rs', direction='rtl')
d.rectangle((R - 4, y + 320, R, y + 380), fill=LT)
d.text((R - 22, y + 350), 'בצלאל סמוטריץ׳', font=F(RUB, 40), fill=(255, 255, 255), anchor='rm', direction='rtl')
im.convert('RGB').save(HERE + '/post-v2.jpg', quality=95)
