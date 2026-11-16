"""Subtle stock-chart background in RZ teal: grid, candlesticks, rising line with glow, faint ticker numbers."""
import math, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont
DEEP, TEAL, LT, PALE, NIGHT = (43, 81, 85), (80, 146, 153), (105, 180, 189), (173, 213, 217), (16, 36, 39)
SEC = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/shalev/fonts/SecularOne.ttf'
def make_bg(W=1080, H=1350, seed=7):
    random.seed(seed); im = Image.new('RGB', (W, H), NIGHT); px = im.load()
    for y in range(H):
        for x in range(W):
            g = max(0, 1 - math.hypot((x - 760) / 900, (y - 380) / 900)); v = 1 - .3 * (y / H) ** 2
            px[x, y] = tuple(int((NIGHT[i] + (DEEP[i] - NIGHT[i]) * (.6 + .4 * g)) * v) for i in range(3))
    im = im.convert('RGBA'); lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for x in range(0, W, 90): d.line((x, 0, x, H), fill=PALE + (14,), width=1)
    for y in range(0, H, 90): d.line((0, y, W, y), fill=PALE + (14,), width=1)
    n = 34; step = W / n; price = 0.78; pts = []
    for i in range(n):
        o = price; price = max(.18, min(.9, price - random.uniform(-.035, .055) * 1.0 - .012)); c = price
        hi = min(o, c) - random.uniform(.005, .03); lo = max(o, c) + random.uniform(.005, .03)
        x = step * i + step / 2; yo, yc, yh, yl = [H * (.25 + .55 * v) for v in (o, c, hi, lo)]
        up = c < o; col = (LT if up else (200, 90, 90)) + (95,)
        d.line((x, yh, x, yl), fill=col, width=2); d.rectangle((x - step * .28, min(yo, yc), x + step * .28, max(yo, yc) + 2), fill=col)
        pts.append((x, yc))
    glow = Image.new('RGBA', (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow); gd.line(pts, fill=LT + (150,), width=14, joint='curve')
    lay.alpha_composite(glow.filter(ImageFilter.GaussianBlur(14))); d.line(pts, fill=PALE + (190,), width=4, joint='curve')
    f = ImageFont.truetype(SEC, 22)
    for k in range(9):
        y = 90 * (k + 1); d.text((W - 16, y - 12), f'{(9 - k) * 250:,}', font=f, fill=PALE + (45,), anchor='ra')
    for _ in range(14):
        d.text((random.randint(20, W - 160), random.randint(20, H - 40)), random.choice(['+2.4%', '+0.8%', '+1.6%', '-0.4%', '+5.2%']), font=f, fill=PALE + (40,))
    im.alpha_composite(lay); return im
if __name__ == '__main__': make_bg().convert('RGB').save('bg-preview.jpg', quality=90)
