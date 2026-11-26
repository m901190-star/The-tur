"""Yesha IG post 1080x1350: Arutz 7 article card (UK sanctions) + Ganz exact quote. White logo, Haim headline with blue offset shadow, no '!'."""
import os, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
KB = HERE + '/../../fonts/HaimClassicv2FM-Bold.ttf'; SEC = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/shalev/fonts/SecularOne.ttf'
LOGO = HERE + '/../../clients/yesha/logo_white.png'
W, H = 1080, 1350; NAVY, BLUE, LB, WHITE = (23, 64, 104), (37, 102, 162), (39, 164, 209), (255, 255, 255)
def F(p, s): return ImageFont.truetype(p, s, layout_engine=ImageFont.Layout.RAQM)
bg = Image.new('RGB', (W, H)); px = bg.load(); DK = (10, 28, 48)
for y in range(H):
    for x in range(W):
        g = max(0, 1 - math.hypot((x - 760) / 900, (y - 330) / 850)); v = 1 - .3 * (y / H) ** 2
        px[x, y] = tuple(int((DK[i] + (BLUE[i] - DK[i]) * g * .75) * v) for i in range(3))
im = bg.convert('RGBA'); d = ImageDraw.Draw(im)
lg = Image.open(LOGO).convert('RGBA'); lg = lg.crop(lg.getchannel('A').getbbox()); lg = lg.resize((150, int(150 * lg.height / lg.width)), Image.LANCZOS)
im.alpha_composite(lg, (W - 60 - lg.width, 40))
src = Image.open(HERE + '/source-article.jpg').convert('RGB')
cw = 860; card = src.resize((cw, int(cw * src.height / src.width)), Image.LANCZOS)
m = Image.new('L', card.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, card.width - 1, card.height - 1), 26, fill=255)
sh = Image.new('L', (card.width + 80, card.height + 80), 0); sh.paste(m, (40, 52)); sh = sh.filter(ImageFilter.GaussianBlur(18))
TOP = 40 + lg.height + 30; X0 = (W - cw) // 2; im.paste((0, 0, 0, 140), (X0 - 40, TOP - 40), sh); im.paste(card, (X0, TOP), m)
R = W - 90; y = TOP + card.height + 50
lab = 'ישראל גנץ, יו״ר מועצת יש״ע:'; fl = F(SEC, 44); lw = d.textlength(lab, font=fl, direction='rtl')
d.rectangle((R - lw - 40, y, R + 4, y + 68), fill=BLUE); d.text((R - 18, y + 8), lab, font=fl, fill=WHITE, anchor='ra', direction='rtl')
fh = F(KB, 90); y += 96
for i, l in enumerate(['״בריטניה הכריזה', 'מלחמה כלכלית', 'נגד ישראל״']):
    yy = y + i * 94; d.text((R + 5, yy + 5), l, font=fh, fill=BLUE, anchor='ra', direction='rtl'); d.text((R, yy), l, font=fh, fill=WHITE, anchor='ra', direction='rtl')
im.convert('RGB').save(HERE + '/post.jpg', quality=95); print(TOP, y + 200)
