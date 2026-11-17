"""RZ IG post 4:5 (same style as 'לדיראון עולם'): teal duotone photo (Kahana with Abbas; photo: Moti Kastel/14, watermark kept), Haim headline. No logo."""
import os, numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); W, H = 1080, 1350
KB = HERE + '/../../fonts/HaimClassicv2FM-Bold.ttf'
DEEP, LT, PALE, NIGHT = (43, 81, 85), (105, 180, 189), (173, 213, 217), (14, 32, 35)
def F(s): return ImageFont.truetype(KB, s, layout_engine=ImageFont.Layout.RAQM)
ph = Image.open(HERE + '/photo.jpg').convert('RGB').filter(ImageFilter.UnsharpMask(2, 50, 2))
ph = ImageOps.fit(ph, (W, 900), Image.LANCZOS, centering=(.5, .1))
g = np.array(ImageOps.autocontrast(ImageOps.grayscale(ph), cutoff=1)).astype(np.float32) / 255
lo, hi = np.array(NIGHT, np.float32), np.array(PALE, np.float32)
im = Image.new('RGBA', (W, H), NIGHT + (255,)); im.paste(Image.fromarray((lo + (hi - lo) * g[..., None] ** 1.1).clip(0, 255).astype(np.uint8)), (0, 0))
ov = Image.new('RGBA', (W, H)); od = ImageDraw.Draw(ov)
for y in range(H): od.line((0, y, W, y), fill=NIGHT + (int(255 * min(1, max(0, (y - 560) / 360)) ** 1.2),))
im.alpha_composite(ov); d = ImageDraw.Draw(im); R = W - 70
fh = F(118); y = 870
RED = (226, 54, 54)
def seg(x, yy, t, col):
    d.text((x + 6, yy + 6), t, font=fh, fill=DEEP, anchor='rs', direction='rtl'); d.text((x, yy), t, font=fh, fill=col, anchor='rs', direction='rtl')
    return x - d.textlength(t, font=fh, direction='rtl')
seg(R, y, 'כהנא בחר', (255, 255, 255))
x = seg(R, y + 120, 'באחים ', (255, 255, 255)); seg(x, y + 120, 'המוסלמים', RED)
t = 'על פני האחים שלו'; fb = F(104); tw = d.textlength(t, font=fb, direction='rtl'); yb = y + 150
d.rectangle((R - tw - 50, yb, R + 18, yb + 150), fill=LT); d.text((R - 20, yb + 120), t, font=fb, fill=NIGHT, anchor='rs', direction='rtl')
im.convert('RGB').save(HERE + '/post.jpg', quality=95); print(tw, d.textlength('באחים המוסלמים', font=fh, direction='rtl'))
