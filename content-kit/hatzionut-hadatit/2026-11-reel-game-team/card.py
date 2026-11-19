"""Game-loading-screen character card (sketch) over the illustrated art. Original styling (no GTA marks)."""
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
KB = HERE + '/../../fonts/HaimClassicv2FM-Bold.ttf'; SEC = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/shalev/fonts/SecularOne.ttf'
RUB = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/fonts/Rubik-900.ttf'
W, H = 1080, 1920; LT, NIGHT = (105, 180, 189), (12, 22, 26)
def F(p, s): return ImageFont.truetype(p, s, layout_engine=ImageFont.Layout.RAQM)
CH = {'smotrich': dict(art='gen/smotrich-art.png', name='בצלאל סמוטריץ׳', cls='FIGHTER',
       stats=['כלכלה חזקה במלחמה בשבע חזיתות', 'למעלה מ־100 יישובים', 'למעלה מ־140 חוות'])}
c = CH[sys.argv[1] if len(sys.argv) > 1 else 'smotrich']
art = Image.open(HERE + '/' + c['art']).convert('RGB'); s = max(W / art.width, H / art.height)
im = art.resize((int(art.width * s), int(art.height * s)), Image.LANCZOS); x0 = (im.width - W) // 2; im = im.crop((x0, 0, x0 + W, H)).convert('RGBA')
ov = Image.new('RGBA', (W, H)); od = ImageDraw.Draw(ov)
for y in range(H): od.line((0, y, W, y), fill=NIGHT + (int(235 * max(0, (y - 1180) / 740) ** 1.1),))
im.alpha_composite(ov); d = ImageDraw.Draw(im); R = W - 60
# class badge (slanted)
cls = c['cls']; fc = F(RUB, 64); cw = d.textlength(cls, font=fc)
b = Image.new('RGBA', (int(cw) + 80, 100), (0, 0, 0, 0)); bd = ImageDraw.Draw(b)
bd.polygon([(20, 0), (b.width, 0), (b.width - 20, 100), (0, 100)], fill=(214, 40, 40)); bd.text((b.width / 2, 50), cls, font=fc, fill='white', anchor='mm')
im.alpha_composite(b, (R - b.width, 1300))
# name with heavy outline
fn = F(KB, 120); y = 1520
d.text((R, y), c['name'], font=fn, fill='white', anchor='rs', direction='rtl', stroke_width=10, stroke_fill=NIGHT)
# stats
fs = F(SEC, 44); yy = 1560
for st in c['stats']:
    d.polygon([(R, yy + 14), (R - 22, yy + 26), (R, yy + 38)], fill=LT)
    d.text((R - 36, yy), st, font=fs, fill='white', anchor='ra', direction='rtl', stroke_width=3, stroke_fill=NIGHT); yy += 70
# corner tag
ft = F(RUB, 34); d.text((60, 70), 'הנבחרת', font=F(KB, 60), fill='white', anchor='la', direction='rtl', stroke_width=5, stroke_fill=NIGHT)
im.convert('RGB').save(HERE + f'/sketch-{sys.argv[1] if len(sys.argv) > 1 else "smotrich"}.jpg', quality=93)
