"""Original game-style HUD over a still: top-left mission text, bottom-left round minimap (outline of Israel area, generic), objective marker. No GTA marks."""
import os, sys, math
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
KB = HERE + '/../../fonts/HaimClassicv2FM-Bold.ttf'; SEC = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/shalev/fonts/SecularOne.ttf'
W, H = 1080, 1920; LT = (105, 180, 189)
def F(p, s): return ImageFont.truetype(p, s, layout_engine=ImageFont.Layout.RAQM)
def hud(src, out, mission, sub=None, done=False):
    im = ImageOps.fit(Image.open(src).convert('RGB'), (W, H), Image.LANCZOS).convert('RGBA')
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    # mission box top-right (RTL)
    fm = F(SEC, 30); fh = F('/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/fonts/Rubik-700.ttf', 46); x1 = W - 40; y = 90
    if mission:
      d.text((x1, y), 'משימה', font=fm, fill=LT + (255,), anchor='ra', direction='rtl')
      tw = d.textlength(mission, font=fh, direction='rtl')
      d.rectangle((x1 - tw - 30, y + 44, x1 + 10, y + 120), fill=(0, 0, 0, 120))
      d.text((x1 - 10, y + 50), mission, font=fh, fill='white', anchor='ra', direction='rtl')
    if sub: d.text((x1 - 10, y + 132), sub, font=F(SEC, 32), fill=(255, 255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0, 255), anchor='ra', direction='rtl')
    # minimap bottom-left
    cx, cy, r = 150, H - 230, 105
    mm = Image.new('RGBA', (2 * r, 2 * r), (0, 0, 0, 0)); md = ImageDraw.Draw(mm)
    md.ellipse((0, 0, 2 * r - 1, 2 * r - 1), fill=(40, 52, 48, 210))
    for i in range(-3, 4): md.line((r + i * 30 - 60, 0, r + i * 30 + 60, 2 * r), fill=(90, 100, 90, 160), width=6)
    md.line((20, r + 20, 2 * r - 20, r - 30), fill=(200, 200, 190, 200), width=5)
    md.polygon([(r, r - 18), (r - 12, r + 14), (r, r + 6), (r + 12, r + 14)], fill='white')
    md.ellipse((r + 45, r - 70, r + 65, r - 50), fill=LT + (255,))
    m = Image.new('L', (2 * r, 2 * r), 0); ImageDraw.Draw(m).ellipse((0, 0, 2 * r - 1, 2 * r - 1), fill=255)
    lay.paste(mm, (cx - r, cy - r), m)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(255, 255, 255, 230), width=5)
    d.arc((cx - r - 14, cy - r - 14, cx + r + 14, cy + r + 14), 120, 240, fill=(80, 200, 120, 255), width=7)
    d.arc((cx - r - 14, cy - r - 14, cx + r + 14, cy + r + 14), 300, 60, fill=LT + (255,), width=7)
    if done:
        fd = F(KB, 110); t = 'משימה הושלמה ✓'
        d.rectangle((0, H / 2 - 90, W, H / 2 + 90), fill=(0, 0, 0, 140))
        d.text((W / 2, H / 2), 'משימה הושלמה', font=fd, fill=(255, 210, 60, 255), anchor='mm', direction='rtl', stroke_width=4, stroke_fill=(0, 0, 0, 255))
    im.alpha_composite(lay); im.convert('RGB').save(out, quality=92)
if __name__ == '__main__':
    G = HERE + '/gen/'
    S = [('c-scene1.png', 'כלכלה חזקה במלחמה בשבע חזיתות', None, False),
         ('c-scene2-cu.png', 'מרכיבי ביטחון', None, False),
         ('c-scene3.png', 'למעלה מ־\u2066100\u2069 יישובים', 'הניחו את הקרוואן', False),
         ('c-scene4.png', 'למעלה מ־\u2066140\u2069 חוות', None, False)]
    outs = []
    for i, (f, m, sub, done) in enumerate(S, 1):
        if os.path.exists(G + f): o = HERE + f'/sketch3-{i}.jpg'; hud(G + f, o, m, sub, done); outs.append(o)
    if outs:
        sheet = Image.new('RGB', (len(outs) * 365, 640), 'white')
        for i, o in enumerate(outs): sheet.paste(Image.open(o).resize((360, 640)), (i * 365, 0))
        sheet.save(HERE + '/sketch3-sheet.jpg', quality=90)
