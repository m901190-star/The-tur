"""Bottom fade overlays (transparent -> colour) in RZ palette, same alpha curve as Moshe's black one. 1080x1080 PNG."""
import os, numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
ref = np.array(Image.open(HERE + '/reference-black.png').convert('RGBA'))[:, 250, 3].astype(np.float32)   # alpha per row, 500 rows
S = 1080; A = np.interp(np.linspace(0, 499, S), np.arange(500), ref)[:, None]
def hexc(h): return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], np.float32)
V = {'1-deep-teal': ('#2B5155', '#2B5155'), '2-night-teal': ('#16302F', '#0E2224'), '3-teal': ('#509299', '#3C7479'),
     '4-teal-to-deep': ('#509299', '#1B3A3D')}
sample = Image.open(HERE + '/sample-bg.jpg').convert('RGB').resize((S, S))
prev = []
for name, (c1, c2) in V.items():
    k = np.linspace(0, 1, S)[:, None, None] ** 1.2; col = hexc(c1) * (1 - k) + hexc(c2) * k
    img = np.zeros((S, S, 4), np.uint8); img[..., :3] = np.broadcast_to(col, (S, S, 3)); img[..., 3] = np.broadcast_to(A, (S, S)).astype(np.uint8)
    o = Image.fromarray(img, 'RGBA'); o.save(HERE + f'/fade-{name}.png')
    p = sample.convert('RGBA'); p.alpha_composite(o); prev.append(p.convert('RGB').resize((360, 360)))
sh = Image.new('RGB', (4 * 370, 370), (30, 30, 30))
for i, p in enumerate(prev): sh.paste(p, (5 + i * 370, 5))
sh.save(HERE + '/preview.jpg', quality=90)
