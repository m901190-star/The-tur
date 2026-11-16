"""Smotrich IG story (9:16): faction-meeting photo + teal bottom fade + Haim title. No party logo added."""
import os
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
KB = HERE + '/../../fonts/HaimClassicv2FM-Bold.ttf'
W, H = 1080, 1920; DEEP, LT, PALE, NIGHT = (43, 81, 85), (105, 180, 189), (173, 213, 217), (16, 36, 39)
def F(s): return ImageFont.truetype(KB, s, layout_engine=ImageFont.Layout.RAQM)
ph = Image.open(HERE + '/photo.jpg').convert('RGB'); s = max(W / ph.width, H / ph.height)
ph = ph.resize((int(ph.width * s), int(ph.height * s)), Image.LANCZOS); x0 = (ph.width - W) // 2; ph = ph.crop((x0, 0, x0 + W, H))
im = ph.convert('RGBA')
g = Image.new('RGBA', (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
for y in range(H):
    a = max(0, (y - 1050) / (H - 1050)); gd.line((0, y, W, y), fill=NIGHT + (int(245 * min(1, a * 1.5) ** 1.3),))
    if y < 260: gd.line((0, y, W, y), fill=NIGHT + (int(120 * (1 - y / 260)),))
im.alpha_composite(g); d = ImageDraw.Draw(im)
R = W - 80; y = 1395
pill = 'משכן הכנסת'; pf = F(50); tw = d.textlength(pill, font=pf, direction='rtl')
d.rounded_rectangle((R - tw - 56, y, R, y + 78), 39, fill=LT); d.text((R - 28, y + 13), pill, font=pf, fill=NIGHT, anchor='ra', direction='rtl')
y += 112; d.rectangle((R - 6, y + 6, R, y + 196), fill=LT)
for i, l in enumerate(['ישיבת סיעת', 'הציונות הדתית']):
    d.text((R - 30 + 5, y + 8 + i * 98 + 5), l, font=F(92), fill=DEEP, anchor='ra', direction='rtl')
    d.text((R - 30, y + 8 + i * 98), l, font=F(92), fill=(255, 255, 255), anchor='ra', direction='rtl')
im.convert('RGB').save(HERE + '/story.jpg', quality=95)
