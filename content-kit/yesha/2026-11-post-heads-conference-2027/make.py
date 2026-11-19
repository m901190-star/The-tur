"""Yesha IG post 1080x1350: heads of authorities conference (Ariel). Wide group photo at the bottom, its clear sky extended upward to carry the text."""
import os, glob
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
KB = glob.glob('/root/.claude/skills/synced/*/pro-video-editing/assets/fonts/Karantina-Bold.ttf')[0]
SEC = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/shalev/fonts/SecularOne.ttf'
LOGO = HERE + '/../../clients/yesha/logo_white.png'
W, H = 1080, 1350; BLUE = (0x25, 0x66, 0xA2); NAVY = (0x17, 0x40, 0x68); WHITE = (255, 255, 255)
def F(p, s): return ImageFont.truetype(p, s, layout_engine=ImageFont.Layout.RAQM)
src = Image.open(HERE + '/photo.jpg').convert('RGB')          # 2000x1002, clear sky on top
ph = src.resize((W, int(W * src.height / src.width)), Image.LANCZOS)  # 1080x541
im = Image.new('RGB', (W, H)); top = H - ph.height
import numpy as np
c_mid = tuple(int(v) for v in np.asarray(ph)[0:3, 300:800].reshape(-1, 3).mean(0)); c_top = tuple(int(v * .78) for v in c_mid)
d = ImageDraw.Draw(im)
for y in range(H):
    k = min(1, y / top) ** 1.5; d.line((0, y, W, y), fill=tuple(int(c_top[i] * (1 - k) + c_mid[i] * k) for i in range(3)))
m = Image.new('L', ph.size, 255); md = ImageDraw.Draw(m)
for y in range(60): md.line((0, y, W, y), fill=int(255 * y / 60))
im.paste(ph, (0, top), m); im = im.convert('RGBA'); d = ImageDraw.Draw(im)
lg = Image.open(LOGO).convert('RGBA'); lg = lg.crop(lg.getchannel('A').getbbox()); lg = lg.resize((170, int(170 * lg.height / lg.width)), Image.LANCZOS)
im.alpha_composite(lg, (W - 60 - lg.width, 60))
R = W - 70
lab = 'כנס ראשי הרשויות · אוגדת יהודה ושומרון'; fl = F(SEC, 44); lw = d.textlength(lab, font=fl, direction='rtl')
d.rectangle((R - lw - 40, 300, R + 4, 370), fill=BLUE); d.text((R - 18, 307), lab, font=fl, fill=WHITE, anchor='ra', direction='rtl')
fh = F(KB, 150)
for i, l in enumerate(['חיזוק הביטחון', 'וההיערכות לשנת 2027']):
    y = 400 + i * 145; d.text((R + 6, y + 6), l, font=fh, fill=NAVY, anchor='ra', direction='rtl'); d.text((R, y), l, font=fh, fill=WHITE, anchor='ra', direction='rtl')
d.text((R, 715), 'בהובלת הגמ״ר איו״ש ומועצת יש״ע', font=F(SEC, 40), fill=WHITE, anchor='ra', direction='rtl')
# location: pin + 'אריאל', top-left (opposite the logo)
f50 = F(SEC, 52); aw = d.textlength('אריאל', font=f50, direction='rtl'); X0 = 62
d.text((X0, 92), 'אריאל', font=f50, fill=WHITE, anchor='la', direction='rtl')
px, py = X0 + aw + 30, 128
d.ellipse((px - 19, py - 31, px + 19, py + 7), fill=WHITE); d.polygon([(px - 17, py - 5), (px + 17, py - 5), (px, py + 26)], fill=WHITE); d.ellipse((px - 8, py - 20, px + 8, py - 4), fill=BLUE)
im.convert('RGB').save(HERE + '/yesha-post-conference-1080x1350.jpg', quality=95); print(top, d.textlength('וההיערכות לשנת 2027', font=fh, direction='rtl'))
