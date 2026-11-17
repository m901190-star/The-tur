"""Smotrich IG post 4:5: Kahana (speaker) photo, B&W darkened (hides TV moire), with Smotrich's tweet 'לדיראון עולם.' embedded. No logo."""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageEnhance
HERE = os.path.dirname(os.path.abspath(__file__)); W, H = 1080, 1350; DEEP = (16, 36, 39)
ph = Image.open(HERE + '/kahana.jpg').convert('RGB').filter(ImageFilter.GaussianBlur(2.2))
ph = ImageOps.fit(ph, (W, H), Image.LANCZOS, centering=(.5, .3))
g = ImageEnhance.Contrast(ImageOps.grayscale(ph)).enhance(1.15)
ph = Image.merge('RGB', (g, g, g)); ph = ImageEnhance.Brightness(ph).enhance(.8)
im = Image.blend(ph, Image.new('RGB', (W, H), DEEP), .25).convert('RGBA')
ov = Image.new('RGBA', (W, H)); od = ImageDraw.Draw(ov)
for y in range(H): od.line((0, y, W, y), fill=(8, 18, 20, int(235 * max(0, (y - 650) / 700) ** 1.1)))
im.alpha_composite(ov)
tw = Image.open(HERE + '/tweet.jpg').convert('RGB').crop((20, 60, 1320, 380))
cw = 900; card = tw.resize((cw, int(cw * tw.height / tw.width)), Image.LANCZOS)
m = Image.new('L', card.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, card.width - 1, card.height - 1), 28, fill=255)
sh = Image.new('L', (card.width + 80, card.height + 80), 0); sh.paste(m, (40, 50)); sh = sh.filter(ImageFilter.GaussianBlur(20))
X0, Y0 = (W - cw) // 2, H - card.height - 120
im.paste((0, 0, 0, 170), (X0 - 40, Y0 - 40), sh); im.paste(card, (X0, Y0), m)
ImageDraw.Draw(im).rounded_rectangle((X0, Y0, X0 + cw - 1, Y0 + card.height - 1), 28, outline=(70, 80, 85), width=2)
im.convert('RGB').save(HERE + '/post.jpg', quality=95); print(card.size)
