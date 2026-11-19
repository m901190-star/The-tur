"""Closest legal homage to the game-cover look: big gradient-filled letter block (own glyph 'S', not the VI mark) + stacked lowercase heavy outlined words (OFL fonts, not Pricedown)."""
import os, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); W, H = 1080, 1920
BIG = HERE + '/fonts/BowlbyOne.ttf'; WORD = HERE + '/fonts/BowlbyOne.ttf'
CW, CH = 980, 1000
def grad(w, h):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32); t = (yy / h) * .75 + (xx / w) * .25
    stops = [(0, (255, 214, 90)), (.3, (255, 120, 80)), (.55, (240, 60, 150)), (.8, (150, 60, 220)), (1, (70, 90, 235))]
    g = np.zeros((h, w, 3), np.float32)
    for (a, ca), (b, cb) in zip(stops, stops[1:]):
        m = (t >= a) & (t <= b); k = ((t - a) / (b - a))[..., None]; g = np.where(m[..., None], np.array(ca) + (np.array(cb) - np.array(ca)) * k, g)
    return Image.fromarray(g.clip(0, 255).astype(np.uint8)).convert('RGBA')
card = Image.new('RGBA', (CW, CH), (0, 0, 0, 0)); d = ImageDraw.Draw(card)
fb = ImageFont.truetype(BIG, 980)
mask = Image.new('L', (CW, CH), 0); md = ImageDraw.Draw(mask); md.text((CW * .62, CH * .48), 'S', font=fb, fill=255, anchor='mm')
outer = mask.filter(ImageFilter.MaxFilter(41)); mid = mask.filter(ImageFilter.MaxFilter(23))
card.paste((15, 10, 30, 255), (0, 0), outer); card.paste((255, 255, 255, 255), (0, 0), mid)
g = grad(CW, CH); gl = Image.new('RGBA', (CW, CH), (0, 0, 0, 0)); gd = ImageDraw.Draw(gl)
for o, a in ((.45, 55), (.62, 30)): gd.polygon([(CW * o, 0), (CW * (o + .1), 0), (CW * (o - .3), CH), (CW * (o - .4), CH)], fill=(255, 255, 255, a))
g.alpha_composite(gl); card.paste(g, (0, 0), mask)
fw = ImageFont.truetype(WORD, 128)
for i, w in enumerate(['bezalel', 'smotrich']):
    d.text((40, 520 + i * 150), w, font=fw, fill='white', anchor='ls', stroke_width=14, stroke_fill=(15, 10, 30))
card = card.rotate(4, resample=Image.BICUBIC, expand=True)
bg = ImageOps.fit(Image.open(HERE + '/gen/aerial.png').convert('RGB'), (W, H), Image.LANCZOS).convert('RGBA')
shd = Image.new('RGBA', card.size, (0, 0, 0, 0)); shd.putalpha(card.getchannel('A').point(lambda v: int(v * .55))); shd = shd.filter(ImageFilter.GaussianBlur(24))
x, y = (W - card.width) // 2, int(H * .42 - card.height / 2)
bg.alpha_composite(shd, (x + 16, y + 26)); bg.alpha_composite(card, (x, y))
bg.convert('RGB').save(HERE + '/sketch5c-title.jpg', quality=92)
