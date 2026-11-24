"""Smotrich IG story (9:16): funeral of Rabbi Yitzhak Levy z"l. Creative memorial: crowd at night full-bleed in B&W with the street lamp
kept warm like a memorial candle, the Rabbi's portrait as a soft double exposure in the night sky, Smotrich at the lectern as a framed inset."""
import os, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter, ImageEnhance, ImageChops
HERE = os.path.dirname(os.path.abspath(__file__))
HAIM = os.path.abspath(os.path.join(HERE, '..', '..', 'fonts', 'HaimClassicv2FM-Bold.ttf'))
W, H = 1080, 1920; INK = (10, 11, 13); SOFT = (210, 212, 214); AMBER = (255, 196, 110)
def F(s): return ImageFont.truetype(HAIM, s, layout_engine=ImageFont.Layout.RAQM)
# background: crowd, scaled so the crowd fills the lower half and the lamp sits on the right third
cr = Image.open(HERE + '/crowd.jpg').convert('RGB')
sc = 1500 / cr.height; cr = cr.resize((int(cr.width * sc), 1500), Image.LANCZOS)
x0 = int(1310 * sc) - 760; cr = cr.crop((x0, 0, x0 + W, 1500))
gray = ImageOps.grayscale(cr); gray = ImageEnhance.Contrast(gray.convert('RGB')).enhance(1.1)
# keep only the lamp warm: mask = bright & near the lamp head
a = np.asarray(cr.convert('L'), np.float32) / 255
yy, xx = np.mgrid[0:cr.height, 0:cr.width]
lx, ly = int(1310 * sc) - x0, int(10 * sc)
near = np.exp(-(((xx - lx) / 260) ** 2 + ((yy - ly) / 260) ** 2))
mask = Image.fromarray((np.clip((a - .55) / .3, 0, 1) * near * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6))
warm = Image.blend(cr, Image.new('RGB', cr.size, AMBER), .35)
bgc = Image.composite(warm, gray, mask)
bg = Image.new('RGB', (W, H), INK); bg.paste(ImageEnhance.Brightness(bgc).enhance(.82), (0, H - 1500))
# soft lamp halo
halo = Image.new('L', (W, H), 0); ImageDraw.Draw(halo).ellipse((lx - 160, H - 1500 + ly - 160, lx + 160, H - 1500 + ly + 160), fill=80)
halo = halo.filter(ImageFilter.GaussianBlur(70)); bg = Image.composite(Image.new('RGB', (W, H), AMBER), bg, halo)
# fade top of the photo into the night
m = Image.new('L', (1, H))
for y in range(H): m.putpixel((0, y), int(255 * max(0, min(1, (H - 1500 + 200 - y) / 200)) ** 1.1))
bg = Image.composite(Image.new('RGB', (W, H), INK), bg, m.resize((W, H)))
# portrait double exposure in the sky
pr = Image.open(HERE + '/rav-levy.jpg').convert('RGB'); pr = pr.resize((pr.width * 3, pr.height * 3), Image.LANCZOS)
pr = ImageOps.fit(ImageOps.grayscale(pr), (760, 1010), Image.LANCZOS, centering=(.5, .3))
pr = ImageEnhance.Contrast(pr.convert('RGB')).enhance(1.25)
pm = Image.new('L', pr.size, 0); ImageDraw.Draw(pm).ellipse((150, 90, pr.width - 150, pr.height + 60), fill=255); pm = pm.filter(ImageFilter.GaussianBlur(95))
fb = Image.new('L', (1, pr.height))
for y in range(pr.height): fb.putpixel((0, y), int(255 * min(1, (pr.height - y) / 420)))
pm = ImageChops.multiply(pm, fb.resize(pr.size)).point(lambda v: int(v * .72))
px, py = (W - pr.width) // 2 - 70, 40
region = bg.crop((px, py, px + pr.width, py + pr.height))
bg.paste(Image.composite(ImageChops.screen(region, pr), region, pm), (px, py))
im = bg.convert('RGBA'); d = ImageDraw.Draw(im)
# text block over a gentle dark band
band = Image.new('RGBA', (W, H), (0, 0, 0, 0)); bd = ImageDraw.Draw(band)
for y in range(980, 1420): bd.line((0, y, W, y), fill=INK + (int(215 * (1 - abs(y - 1200) / 220) ** .6),))
im.alpha_composite(band); d = ImageDraw.Draw(im)
R = W - 80
d.text((R, 1035), 'הרב יצחק לוי ז״ל', font=F(112), fill='white', anchor='ra', direction='rtl')
d.text((R, 1170), 'יו״ר המפד״ל ושר לשעבר', font=F(54), fill=SOFT, anchor='ra', direction='rtl')
d.line((R - 150, 1262, R, 1262), fill=AMBER, width=3)
d.text((R, 1288), 'יהי זכרו ברוך', font=F(66), fill='white', anchor='ra', direction='rtl')
# Smotrich at the lectern: small framed inset, slightly tilted like a print
eu = Image.open(HERE + '/eulogy.jpg').convert('RGB')
eu = ImageOps.fit(ImageOps.grayscale(eu).convert('RGB'), (360, 256), Image.LANCZOS, centering=(.47, .35))
card = Image.new('RGBA', (384, 280), (240, 240, 238, 255)); card.paste(eu, (12, 12))
sh = Image.new('RGBA', (card.width + 60, card.height + 60), (0, 0, 0, 0)); sh.paste((0, 0, 0, 160), (30, 36, 30 + card.width, 36 + card.height))
sh = sh.filter(ImageFilter.GaussianBlur(14)); sh.alpha_composite(card, (30, 30)); sh = sh.rotate(-4, resample=Image.BICUBIC, expand=True)
im.alpha_composite(sh, (36, 1500))
im.convert('RGB').save(HERE + '/story.jpg', quality=95); print('ok')
