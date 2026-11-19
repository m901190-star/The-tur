"""Yesha Council memorial post, 1080x1350."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
OUT = os.path.dirname(os.path.abspath(__file__))
FONTS = OUT + '/../pro-video-editing/assets/fonts/'
LOGO = '/root/.claude/uploads/1a5819ee-0cc0-5045-b086-4a8a80216453/6f71e693-image.png'
SRC = '/root/.claude/uploads/1a5819ee-0cc0-5045-b086-4a8a80216453/d7526711-image.jpg'
S = 2; W, H = 1080, 1350
DEEP = (0x0B, 0x1B, 0x2C); NAVY = (0x17, 0x40, 0x68); LB = (0x27, 0xA4, 0xD1); SOFT = (0xB8, 0xD4, 0xE8); WHITE = (255, 255, 255)
def F(s, b=True): return ImageFont.truetype(FONTS + ('Karantina-Bold.ttf' if b else 'Karantina-Regular.ttf'), int(s * S))
def P(*v): return [int(x * S) for x in v]
def text(d, xy, s, size, fill, anchor='ma', bold=True):
    d.text((int(xy[0] * S), int(xy[1] * S)), s, font=F(size, bold), fill=fill, anchor=anchor, direction='rtl')

img = Image.new('RGB', (W * S, H * S)); d = ImageDraw.Draw(img)
for y in range(H * S):
    t = y / (H * S); d.line([(0, y), (W * S, y)], fill=tuple(int(DEEP[i] + (NAVY[i] - DEEP[i]) * t * 0.6) for i in range(3)))

# logo (white version of the original artwork), small and quiet
lg = Image.open(LOGO).convert('RGBA'); a = lg.getchannel('A').point(lambda v: 0 if v < 40 else v)
lg = Image.new('RGBA', lg.size, WHITE + (0,)); lg.putalpha(a); lg = lg.crop(lg.getchannel('A').getbbox())
lw = 130; lg = lg.resize((lw * S, int(lw * S * lg.height / lg.width)), Image.LANCZOS)
lg.putalpha(lg.getchannel('A').point(lambda v: int(v * 0.85)))
img.paste(lg, ((W - lw) // 2 * S, 50 * S), lg)

text(d, (W / 2, 165), 'הלב נשבר', 110, WHITE)

# the two portraits, untouched, side by side
src = Image.open(SRC).convert('RGB')
halves = [src.crop((0, 0, 655, 1130)), src.crop((665, 0, 1320, 1130))]
pw, ph = 430, 560; gap = 40; x0 = (W - 2 * pw - gap) / 2; y0 = 300
for k, im in enumerate(halves):
    s = max(pw / im.width, ph / im.height)
    im = im.resize((int(im.width * s * S), int(im.height * s * S)), Image.LANCZOS)
    cx = (im.width - pw * S) // 2; im = im.crop((cx, 0, cx + pw * S, ph * S))
    m = Image.new('L', im.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0) + (im.width - 1, im.height - 1), radius=24 * S, fill=255)
    x = x0 + k * (pw + gap)
    d.rounded_rectangle(P(x - 4, y0 - 4, x + pw + 4, y0 + ph + 4), radius=28 * S, fill=SOFT)
    img.paste(im, (int(x * S), int(y0 * S)), m)

# names together, not tied to a specific portrait until confirmed
y = 905
text(d, (W / 2, y), 'סמ״ר רון יונתן רויטמן ז״ל', 64, WHITE); text(d, (W / 2, y + 70), 'בן 23 מאשקלון', 40, SOFT, bold=False)
text(d, (W / 2, y + 135), 'סמל יובל שי סוילם ז״ל', 64, WHITE); text(d, (W / 2, y + 205), 'בן 20 מהוד השרון', 40, SOFT, bold=False)
d.rectangle(P(W / 2 - 60, 1180, W / 2 + 60, 1184), fill=LB)
text(d, (W / 2, 1200), 'אנו אבלים וכואבים יחד עם משפחותיהם וקרוביהם', 40, SOFT, bold=False)
text(d, (W / 2, 1255), 'יהי זכרם ברוך', 62, WHITE)
img.resize((W, H), Image.LANCZOS).save(OUT + '/yesha-memorial-1080x1350.png')
print('done')
