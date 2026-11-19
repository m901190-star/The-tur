"""Closer 'game-cover' homage: tilted square gradient panel (sunset pink->violet->blue), stacked lowercase heavy outlined words. Own font/shape; no VI mark."""
import os, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); W, H = 1080, 1920
FONT = '/usr/share/fonts/opentype/inter/InterDisplay-Black.otf'
S = 640
yy, xx = np.mgrid[0:S, 0:S].astype(np.float32) / S
t = (yy * .65 + (1 - xx) * .35)
stops = [(0, (255, 170, 60)), (.35, (250, 70, 140)), (.7, (150, 60, 230)), (1, (60, 80, 230))]
g = np.zeros((S, S, 3), np.float32)
for (a, ca), (b, cb) in zip(stops, stops[1:]):
    m = (t >= a) & (t <= b); k = ((t - a) / (b - a))[..., None]; g = np.where(m[..., None], np.array(ca) + (np.array(cb) - np.array(ca)) * k, g)
panel = Image.fromarray(g.clip(0, 255).astype(np.uint8)).convert('RGBA')
# glossy diagonal light bands
gl = Image.new('RGBA', (S, S), (0, 0, 0, 0)); gd = ImageDraw.Draw(gl)
for o, a in ((.15, 45), (.32, 25)): gd.polygon([(S * o, 0), (S * (o + .12), 0), (S * (o - .25), S), (S * (o - .37), S)], fill=(255, 255, 255, a))
panel.alpha_composite(gl)
card = Image.new('RGBA', (S + 40, S + 40), (0, 0, 0, 0)); card.paste(panel, (20, 20))
d = ImageDraw.Draw(card); d.rectangle((14, 14, S + 25, S + 25), outline=(20, 12, 40), width=12); d.rectangle((26, 26, S + 13, S + 13), outline=(255, 255, 255), width=5)
words = ['bezalel', 'smotrich']; f = ImageFont.truetype(FONT, 170)
for i, w in enumerate(words):
    fw = f
    while d.textlength(w, font=fw) > S - 70: fw = ImageFont.truetype(FONT, fw.size - 6)
    d.text((S / 2 + 20, 210 + i * 190), w, font=fw, fill='white', anchor='mm', stroke_width=12, stroke_fill=(15, 10, 30))
card = card.rotate(-7, resample=Image.BICUBIC, expand=True)
bg = ImageOps.fit(Image.open(HERE + '/gen/aerial.png').convert('RGB'), (W, H), Image.LANCZOS).convert('RGBA')
shd = Image.new('RGBA', card.size, (0, 0, 0, 0)); shd.putalpha(card.getchannel('A').point(lambda v: int(v * .6))); shd = shd.filter(ImageFilter.GaussianBlur(22))
x, y = (W - card.width) // 2, int(H * .40 - card.height / 2)
bg.alpha_composite(shd, (x + 16, y + 26)); bg.alpha_composite(card, (x, y))
bg.convert('RGB').save(HERE + '/sketch5b-title.jpg', quality=92)
