"""Yesha IG post 1080x1350 v2: full-bleed photo, stacked white headline blocks, giant '26', quote without marks/label. White logo, no '!'."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
KB = HERE + '/../../fonts/HaimClassicv2FM-Bold.ttf'; SEC = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/shalev/fonts/SecularOne.ttf'
LOGO = HERE + '/../../clients/yesha/logo_white.png'
W, H = 1080, 1350; NAVY, BLUE, LB, WHITE = (23, 64, 104), (37, 102, 162), (39, 164, 209), (255, 255, 255); DK = (10, 30, 54)
def F(p, s): return ImageFont.truetype(p, s, layout_engine=ImageFont.Layout.RAQM)
PH = 820
ph = ImageOps.fit(Image.open(HERE + '/source-photo.jpg').convert('RGB'), (W, PH), Image.LANCZOS, centering=(.5, .7))
bg = Image.new('RGB', (W, H), DK); bd = ImageDraw.Draw(bg)
for r in range(1000, 0, -8): bd.ellipse((W * .25 - r, H - r * .9, W * .25 + r, H + r * .9), fill=tuple(int(DK[i] + (BLUE[i] - DK[i]) * (1 - r / 1000) * .6) for i in range(3)))
im = bg.filter(ImageFilter.GaussianBlur(30)).convert('RGBA')
m = Image.new('L', (W, PH), 0); ImageDraw.Draw(m).polygon([(0, 0), (W, 0), (W, PH - 150), (0, PH)], fill=255)
im.paste(ph, (0, 0), m)
top = Image.new('RGBA', (W, 230)); td = ImageDraw.Draw(top)
for y in range(230): td.line((0, y, W, y), fill=DK + (int(150 * (1 - y / 230)),))
im.alpha_composite(top)
band = Image.new('RGBA', (W, H)); bd2 = ImageDraw.Draw(band)
bd2.polygon([(0, PH), (W, PH - 150), (W, PH - 128), (0, PH + 22)], fill=LB + (255,))
im.alpha_composite(band)
wm = Image.new('RGBA', (W, H)); ImageDraw.Draw(wm).text((40, 1340), '26', font=F(SEC, 420), fill=(255, 255, 255, 26), anchor='ls'); im.alpha_composite(wm)
d = ImageDraw.Draw(im)
lg = Image.open(LOGO).convert('RGBA'); lg = lg.crop(lg.getchannel('A').getbbox()); lg = lg.resize((150, int(150 * lg.height / lg.width)), Image.LANCZOS)
im.alpha_composite(lg, (W - 60 - lg.width, 40)); d = ImageDraw.Draw(im)
R = W - 70
def block(y, parts, bg, fg, pad=26, h=None):
    fs = [f for _, f in parts]; tw = sum(d.textlength(t, font=f, direction='rtl') for t, f in parts); hh = h or int(fs[0].size * 1.12)
    d.rectangle((R - tw - pad * 2, y, R, y + hh), fill=bg); x = R - pad
    for t, f in parts:
        d.text((x, y + hh / 2 + 4), t, font=f, fill=fg, anchor='rm', direction='rtl'); x -= d.textlength(t, font=f, direction='rtl')
    return y + hh
y = 760
y = block(y, [('שדולת ארץ ישראל', F(KB, 104))], WHITE, NAVY)
y = block(y + 10, [('בכנסת ה־', F(KB, 74)), ('26', F(SEC, 70)), (' יוצאת לדרך', F(KB, 74))], BLUE, WHITE)
fq = F(KB, 58); yq = 1085
for i, l in enumerate(['לפנינו משימות רבות, ובראשן', 'המשך תנופת הבנייה והפיתוח', 'ביהודה ושומרון']):
    d.text((R - 28, yq + i * 72), l, font=fq, fill=WHITE, anchor='ra', direction='rtl')
d.rectangle((R - 8, yq + 8, R, yq + 3 * 72 - 10), fill=LB)
im.convert('RGB').save(HERE + '/post.jpg', quality=95); print('ok')
