"""Smotrich IG post (4:5): Mansour Abbas. House style — photo on top, headline in Haim (white line + teal pill).
Headline is an exact phrase from Smotrich's text. Portrait in B&W (face unaltered)."""
import os, sys, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter, ImageEnhance
HERE = os.path.dirname(os.path.abspath(__file__))
HAIM = os.path.abspath(os.path.join(HERE, '..', '..', 'fonts', 'HaimClassicv2FM-Bold.ttf'))
W, H = 1080, 1350; DEEP, TEAL, LT = (43, 81, 85), (80, 146, 153), (105, 180, 189)
L1 = sys.argv[1] if len(sys.argv) > 1 else 'עבאס רוצה להיכנס לממשלה'
L2 = sys.argv[2] if len(sys.argv) > 2 else 'כדי לחסל את ישראל מבפנים'
def F(s): return ImageFont.truetype(HAIM, s, layout_engine=ImageFont.Layout.RAQM)
src = Image.open(HERE + '/src/abbas.jpg').convert('L')
PH = 1040
ph = src.resize((W, int(W * src.height / src.width)), Image.LANCZOS).crop((0, 0, W, PH))
ph = ImageEnhance.Contrast(ph).enhance(1.15).filter(ImageFilter.UnsharpMask(3, 70, 2))
a = np.asarray(ph).astype(np.float32) + np.random.default_rng(3).normal(0, 7, (PH, W))
ph = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGB')
im = Image.new('RGB', (W, H), DEEP); im.paste(ph, (0, 0))
lo = Image.new('L', (1, H))
for yy in range(H): lo.putpixel((0, yy), int(255 * max(0, min(1, (yy - (PH - 260)) / 240)) ** 1.2))
im = Image.composite(Image.new('RGB', (W, H), DEEP), im, lo.resize((W, H)))
d = ImageDraw.Draw(im); R = W - 70; y = PH - 30
f1 = F(96)
while d.textlength(L1, font=f1, direction='rtl') > W - 160: f1 = F(f1.size - 4)
d.rectangle((R - 6, y + 14, R, y + 100), fill=LT)
d.text((R - 28, y), L1, font=f1, fill='white', anchor='ra', direction='rtl')
f2 = F(88)
while d.textlength(L2, font=f2, direction='rtl') > W - 200: f2 = F(f2.size - 4)
y2 = y + 135; bb = d.textbbox((0, 0), L2, font=f2, anchor='ls', direction='rtl')
tw = bb[2] - bb[0]; ih = bb[3] - bb[1]; pad = 22
d.rounded_rectangle((R - tw - 56, y2, R + 6, y2 + ih + 2 * pad), 14, fill=LT)
d.text((R - 24, y2 + pad - bb[1]), L2, font=f2, fill=DEEP, anchor='rs', direction='rtl')
im.save(HERE + '/post.jpg', quality=95); print('bottom', y2 + ih + 2 * pad)
