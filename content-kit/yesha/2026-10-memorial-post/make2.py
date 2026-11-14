"""Yesha memorial post in the client's existing style: full-bleed photos, dark fade, names with blue offset shadow."""
import os
from PIL import Image, ImageDraw, ImageFont
OUT = os.path.dirname(os.path.abspath(__file__))
FONTS = OUT + '/../pro-video-editing/assets/fonts/'
LOGO = '/root/.claude/uploads/1a5819ee-0cc0-5045-b086-4a8a80216453/6f71e693-image.png'   # original blue logo
SRC = '/root/.claude/uploads/1a5819ee-0cc0-5045-b086-4a8a80216453/d7526711-image.jpg'
S = 2; W, H = 1080, 1350
BLUE = (0x25, 0x66, 0xA2); WHITE = (255, 255, 255); SOFT = (0xD6, 0xE4, 0xEF)
def F(s, b=True): return ImageFont.truetype(FONTS + ('Karantina-Bold.ttf' if b else 'Karantina-Regular.ttf'), int(s * S))

img = Image.new('RGB', (W * S, H * S), (0, 0, 0))
src = Image.open(SRC).convert('RGB')
halves = [src.crop((0, 0, 655, 1130)), src.crop((665, 0, 1320, 1130))]
cw, ch = W // 2, 930                       # photo band; below it the fade turns fully black
for k, im in enumerate(halves):
    s = max(cw / im.width, ch / im.height)
    im = im.resize((int(im.width * s * S), int(im.height * s * S)), Image.LANCZOS)
    cx = (im.width - cw * S) // 2
    img.paste(im.crop((cx, 0, cx + cw * S, ch * S)), (k * cw * S, 0))
d = ImageDraw.Draw(img)
d.rectangle((cw * S - 3 * S, 0, cw * S + 3 * S, ch * S), fill=(0, 0, 0))   # thin separator
ov = Image.new('RGBA', img.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
for y in range(H * S):
    t = y / (H * S)
    a = int(255 * min(1, max(0, (t - 0.42) / 0.28)) ** 1.15)
    if a: od.line([(0, y), (W * S, y)], fill=(0, 0, 0, a))
img.paste(ov, (0, 0), ov)

# original logo, top-right, on the light wall of the right-hand photo
lg = Image.open(LOGO).convert('RGBA'); lg = lg.crop(lg.getchannel('A').getbbox())
lw = 140; lg = lg.resize((lw * S, int(lw * S * lg.height / lg.width)), Image.LANCZOS)
img.paste(lg, ((W - 24 - lw) * S, 22 * S), lg)

d = ImageDraw.Draw(img)
def name(y, s, size=104):
    f = F(size)
    d.text(((W / 2 + 7) * S, (y + 7) * S), s, font=f, fill=BLUE, anchor='ma', direction='rtl')
    d.text((W / 2 * S, y * S), s, font=f, fill=WHITE, anchor='ma', direction='rtl')
def sub(y, s):
    d.text((W / 2 * S, y * S), s, font=F(44, False), fill=SOFT, anchor='ma', direction='rtl')
name(880, 'סמ״ר רון יונתן רויטמן הי״ד'); sub(990, 'בן 23 מאשקלון')
name(1060, 'סמל יובל שי סוילם הי״ד'); sub(1170, 'בן 20 מהוד השרון')
d.text((W / 2 * S, 1255 * S), 'יהי זכרם ברוך', font=F(56), fill=WHITE, anchor='ma', direction='rtl')
img.resize((W, H), Image.LANCZOS).save(OUT + '/yesha-memorial-1080x1350.png')
print('done')
