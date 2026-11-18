"""Yesha IG post 1080x1350: Eretz Israel Caucus (26th Knesset) kickoff. Photo top, navy body, Haim headline with blue offset, exact Hagai Tam quote. White logo, no '!'."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
KB = HERE + '/../../fonts/HaimClassicv2FM-Bold.ttf'; SEC = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/shalev/fonts/SecularOne.ttf'
LOGO = HERE + '/../../clients/yesha/logo_white.png'
W, H = 1080, 1350; NAVY, BLUE, LB, WHITE = (23, 64, 104), (37, 102, 162), (39, 164, 209), (255, 255, 255); DK = (12, 32, 56)
def F(p, s): return ImageFont.truetype(p, s, layout_engine=ImageFont.Layout.RAQM)
im = Image.new('RGBA', (W, H), DK + (255,))
# navy radial body
bg = Image.new('RGB', (W, H), DK); bd = ImageDraw.Draw(bg)
for r in range(900, 0, -6): bd.ellipse((W * .7 - r, H * .82 - r, W * .7 + r, H * .82 + r), fill=tuple(int(DK[i] + (BLUE[i] - DK[i]) * (1 - r / 900) * .55) for i in range(3)))
im.paste(bg.filter(ImageFilter.GaussianBlur(40)))
PH = 780
ph = ImageOps.fit(Image.open(HERE + '/source-photo.jpg').convert('RGB'), (W, PH), Image.LANCZOS, centering=(.5, .62))
m = Image.new('L', (W, PH), 255); md = ImageDraw.Draw(m)
for y in range(PH - 260, PH): md.line((0, y, W, y), fill=int(255 * (PH - y) / 260))
im.paste(ph, (0, 0), m)
top = Image.new('RGBA', (W, 260)); td = ImageDraw.Draw(top)
for y in range(260): td.line((0, y, W, y), fill=DK + (int(170 * (1 - y / 260)),))
im.alpha_composite(top)
lg = Image.open(LOGO).convert('RGBA'); lg = lg.crop(lg.getchannel('A').getbbox()); lg = lg.resize((150, int(150 * lg.height / lg.width)), Image.LANCZOS)
im.alpha_composite(lg, (W - 60 - lg.width, 40))
d = ImageDraw.Draw(im); R = W - 80
def runs(y, parts, fill=WHITE, shadow=BLUE, off=5):
    # parts: list of (text, font) in reading order (RTL), drawn right to left
    x = R
    for t, f in parts:
        w = d.textlength(t, font=f, direction='rtl')
        d.text((x + off, y + off), t, font=f, fill=shadow, anchor='rs', direction='rtl'); d.text((x, y), t, font=f, fill=fill, anchor='rs', direction='rtl'); x -= w
y0 = 700
fh = F(KB, 112); runs(y0, [('שדולת ארץ ישראל', fh)])
f2 = F(KB, 84); f2n = F(SEC, 80); runs(y0 + 100, [('בכנסת ה־', f2), ('26', f2n), (' יוצאת לדרך', f2)], fill=LB, shadow=NAVY)
y = y0 + 170
lab = 'עו״ד חגי תם, מ״מ מנכ״ל מועצת יש״ע:'; fl = F(KB, 40); lw = d.textlength(lab, font=fl, direction='rtl')
d.rectangle((R - lw - 40, y, R + 4, y + 62), fill=BLUE); d.text((R - 18, y + 31), lab, font=fl, fill=WHITE, anchor='rm', direction='rtl')
fq = F(KB, 58); y += 100
for i, l in enumerate(['״לפנינו משימות רבות, ובראשן', 'המשך תנופת הבנייה והפיתוח', 'ביהודה ושומרון״']):
    d.text((R, y + i * 68), l, font=fq, fill=WHITE, anchor='ra', direction='rtl')
fn = F(KB, 30); names = 'ח״כ שמחה רוטמן · ח״כ טליק גואילי · עו״ד חגי תם · מאיר דויטש, רגבים'
d.text((R, H - 62), names, font=fn, fill=(170, 200, 225), anchor='rs', direction='rtl')
im.convert('RGB').save(HERE + '/post.jpg', quality=95); print('ok')
