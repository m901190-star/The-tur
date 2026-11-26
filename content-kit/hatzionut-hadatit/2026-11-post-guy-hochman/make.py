"""Smotrich IG post (4:5): meeting with Guy Hochman. Photo + headline in Haim, RZ teal."""
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageOps
HERE = os.path.dirname(os.path.abspath(__file__))
HAIM = os.path.abspath(os.path.join(HERE, '..', '..', 'fonts', 'HaimClassicv2FM-Bold.ttf'))
W, H = 1080, 1350; DEEP, TEAL, LT = (43, 81, 85), (80, 146, 153), (105, 180, 189)
L1 = sys.argv[1] if len(sys.argv) > 1 else 'שיחה פתוחה'
L2 = sys.argv[2] if len(sys.argv) > 2 else 'עם גיא הוכמן.'
def F(s): return ImageFont.truetype(HAIM, s, layout_engine=ImageFont.Layout.RAQM)
from PIL import ImageFilter
ph = Image.open(HERE + '/source-photo.jpg').convert('RGB').crop((130, 120, 1840, 1126))
top = ph.resize((W, int(W * ph.height / ph.width)), Image.LANCZOS); PH = top.height
bg = ImageOps.fit(ph, (W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(40))
bg = Image.blend(bg, Image.new('RGB', (W, H), DEEP), .72)
Y0 = 215
m = Image.new('L', (W, PH), 255); md = ImageDraw.Draw(m)
for i in range(70):
    v = int(255 * i / 70); md.line((0, i, W, i), fill=v); md.line((0, PH - 1 - i, W, PH - 1 - i), fill=v)
bg.paste(top, (0, Y0), m); im = bg
lo = Image.new('L', (1, H))
for yy in range(H): lo.putpixel((0, yy), int(230 * max(0, min(1, (yy - (Y0 + PH - 40)) / 160))))
im = Image.composite(Image.new('RGB', (W, H), DEEP), im, lo.resize((W, H)))
d = ImageDraw.Draw(im); R = W - 80; y = Y0 + PH + 90
f1 = F(118); d.rectangle((R - 6, y + 16, R, y + 120), fill=LT)
d.text((R - 30, y), L1, font=f1, fill='white', anchor='ra', direction='rtl')
f2 = F(104); y2 = y + 150; bb = d.textbbox((0, 0), L2, font=f2, anchor='ls', direction='rtl')
tw = bb[2] - bb[0]; ih = bb[3] - bb[1]; pad = 22
d.rounded_rectangle((R - tw - 56, y2, R + 6, y2 + ih + 2 * pad), 14, fill=LT)
d.text((R - 24, y2 + pad - bb[1]), L2, font=f2, fill=DEEP, anchor='rs', direction='rtl')
im.save(HERE + '/post.jpg', quality=95); print(y2 + ih + 2 * pad)
