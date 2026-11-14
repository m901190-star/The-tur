"""Yesha IG post 1080x1350: full-bleed photo, dark fade on the bottom third, blue label + headline (Karantina, blue offset shadow), white logo top-right."""
import os, glob
from PIL import Image, ImageDraw, ImageFont
OUT = os.path.dirname(os.path.abspath(__file__))
KB = glob.glob('/root/.claude/skills/synced/*/pro-video-editing/assets/fonts/Karantina-Bold.ttf')[0]
LOGO = OUT + '/../../clients/yesha/logo_white.png'
S = 2; W, H = 1080, 1350
BLUE = (0x25, 0x66, 0xA2); NAVY = (0x17, 0x40, 0x68); WHITE = (255, 255, 255)
LABEL = 'לראשונה מאז הגירוש:'
HEAD = ['אושר תקציב למבני מעון יום', 'ביישובים החדשים גנים וכדים']
def F(s): return ImageFont.truetype(KB, int(s * S), layout_engine=ImageFont.Layout.RAQM)
src = Image.open(OUT + '/photo.jpg').convert('RGB')        # 1320x1737
cw = src.width; ch = int(cw * H / W); y0 = 60                # keep the billboard in the upper half
img = src.crop((0, y0, cw, y0 + ch)).resize((W * S, H * S), Image.LANCZOS)
ov = Image.new('RGBA', img.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
for y in range(H * S):
    t = y / (H * S); a = int(235 * min(1, max(0, (t - 0.55) / 0.3)) ** 1.2)
    if a: od.line([(0, y), (W * S, y)], fill=(5, 14, 28, a))
img.paste(ov, (0, 0), ov); d = ImageDraw.Draw(img)
lg = Image.open(LOGO).convert('RGBA'); lg = lg.crop(lg.getchannel('A').getbbox())
lw = 170; lg = lg.resize((lw * S, int(lw * S * lg.height / lg.width)), Image.LANCZOS); lg.putalpha(lg.getchannel('A').point(lambda v: int(v * .95)))
img.paste(lg, ((W - 60 - lw) * S, 60 * S), lg)
R = (W - 70) * S
fh = F(108); lh = 104; ytop = 1350 - 70 - lh * len(HEAD)
fl = F(58); lwid = d.textlength(LABEL, font=fl, direction='rtl')
ly = ytop - 96
d.rectangle((R - lwid - 44 * S, ly * S, R + 4 * S, (ly + 76) * S), fill=BLUE)
d.text((R - 20 * S, (ly + 8) * S), LABEL, font=fl, fill=WHITE, anchor='ra', direction='rtl')
for i, l in enumerate(HEAD):
    y = (ytop + i * lh) * S
    d.text((R + 5 * S, y + 5 * S), l, font=fh, fill=BLUE, anchor='ra', direction='rtl')
    d.text((R, y), l, font=fh, fill=WHITE, anchor='ra', direction='rtl')
img.resize((W, H), Image.LANCZOS).convert('RGB').save(OUT + '/yesha-post-maon-1080x1350.jpg', quality=95)
print('done')
