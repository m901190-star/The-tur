"""Character-select overlay (original design): name, class, stat bars, AI label."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps
HERE = os.path.dirname(os.path.abspath(__file__))
KB = HERE + '/../../fonts/HaimClassicv2FM-Bold.ttf'; RUB = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/fonts/Rubik-700.ttf'
SEC = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/shalev/fonts/SecularOne.ttf'
W, H = 1080, 1920; LT = (105, 180, 189); GOLD = (255, 205, 70)
def F(p, s): return ImageFont.truetype(p, s, layout_engine=ImageFont.Layout.RAQM)
im = ImageOps.fit(Image.open(HERE + '/gen/select.png').convert('RGB'), (W, H), Image.LANCZOS).convert('RGBA')
ov = Image.new('RGBA', (W, H)); od = ImageDraw.Draw(ov)
for y in range(H): od.line((0, y, W, y), fill=(8, 10, 16, int(230 * max(0, (y - 1150) / 770) ** 1.1)))
im.alpha_composite(ov); d = ImageDraw.Draw(im); R = W - 60
d.text((R, 70), 'בחר דמות', font=F(RUB, 40), fill='white', anchor='ra', direction='rtl', stroke_width=3, stroke_fill='black')
d.polygon([(60, 70), (110, 95), (60, 120)], fill='white'); d.polygon([(130, 70), (180, 95), (130, 120)], fill=(255, 255, 255, 120))
d.text((R, 1440), 'בצלאל סמוטריץ׳', font=F(KB, 112), fill='white', anchor='rs', direction='rtl', stroke_width=6, stroke_fill='black')
cls = 'FIGHTER'; fc = F(RUB, 42); cw = d.textlength(cls, font=fc)
d.rectangle((R - cw - 36, 1460, R, 1520), fill=(214, 40, 40)); d.text((R - 18, 1490), cls, font=fc, fill='white', anchor='rm')
stats = [('כלכלה', 1.0), ('התיישבות', 1.0), ('עמידות', .95)]
y = 1570
for name, v in stats:
    d.text((R, y), name, font=F(SEC, 40), fill='white', anchor='ra', direction='rtl')
    bx0, bx1 = 120, R - 220
    for k in range(10):
        x0 = bx1 - (k + 1) * (bx1 - bx0) / 10 + 6; x1 = bx1 - k * (bx1 - bx0) / 10
        d.rectangle((x0, y + 10, x1, y + 44), fill=(GOLD if k < round(v * 10) else (70, 70, 70)))
    y += 90
d.text((60, H - 50), 'נוצר ב-AI', font=F(SEC, 26), fill=(255, 255, 255, 200), anchor='ls', direction='rtl')
im.convert('RGB').save(HERE + '/sketch4-select.jpg', quality=92)
