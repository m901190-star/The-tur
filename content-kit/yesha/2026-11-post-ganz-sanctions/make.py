"""Yesha IG post 1080x1350: Ganz on the UK sanctions. Photo (small source) shown full-width on a blurred extension; blue label + exact quote."""
import os, glob
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
HERE = os.path.dirname(os.path.abspath(__file__))
KB = glob.glob('/root/.claude/skills/synced/*/pro-video-editing/assets/fonts/Karantina-Bold.ttf')[0]
SEC = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/shalev/fonts/SecularOne.ttf'
LOGO = HERE + '/../../clients/yesha/logo_white.png'
W, H = 1080, 1350; BLUE = (0x25, 0x66, 0xA2); NAVY = (0x17, 0x40, 0x68); WHITE = (255, 255, 255); SOFT = (0xD6, 0xE4, 0xEF)
def F(p, s): return ImageFont.truetype(p, s, layout_engine=ImageFont.Layout.RAQM)
src = Image.open(HERE + '/photo.jpg').convert('RGB')
bg = src.resize((int(src.width * H / src.height), H), Image.LANCZOS); x0 = (bg.width - W) // 2
bg = ImageEnhance.Brightness(bg.crop((x0, 0, x0 + W, H)).filter(ImageFilter.GaussianBlur(28))).enhance(.45)
im = bg.convert('RGBA')
fg = src.resize((W, int(W * src.height / src.width)), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 80, 2))
im.paste(fg, (0, 0))
ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
for y in range(H):
    a = int(235 * min(1, max(0, (y - 560) / 300)) ** 1.1)
    if a: od.line((0, y, W, y), fill=(6, 16, 30, a))
im.alpha_composite(ov); d = ImageDraw.Draw(im)
lg = Image.open(LOGO).convert('RGBA'); lg = lg.crop(lg.getchannel('A').getbbox()); lg = lg.resize((170, int(170 * lg.height / lg.width)), Image.LANCZOS)
im.alpha_composite(lg, (W - 60 - lg.width, 60))
R = W - 70
k = '13 תובעים כלליים בארה״ב דורשים מבריטניה לבטל את הסנקציות'; f = F(SEC, 36)
d.text((R, 800), k, font=f, fill=SOFT, anchor='ra', direction='rtl')
lab = 'ישראל גנץ, יו״ר מועצת יש״ע:'; fl = F(SEC, 50); lw = d.textlength(lab, font=fl, direction='rtl')
d.rectangle((R - lw - 44, 862, R + 4, 938), fill=BLUE); d.text((R - 20, 870), lab, font=fl, fill=WHITE, anchor='ra', direction='rtl')
fh = F(KB, 112)
for i, l in enumerate(['״נמשיך לפעול בנחישות', 'לביטול הסנקציות ולחיזוק', 'ההתיישבות ביהודה ושומרון״']):
    y = 975 + i * 112
    d.text((R + 5, y + 5), l, font=fh, fill=BLUE, anchor='ra', direction='rtl'); d.text((R, y), l, font=fh, fill=WHITE, anchor='ra', direction='rtl')
im.convert('RGB').save(HERE + '/yesha-post-ganz-sanctions-1080x1350.jpg', quality=95)
print(max(d.textlength(l, font=fh, direction='rtl') for l in ['לביטול הסנקציות ולחיזוק', 'ההתיישבות ביהודה ושומרון״']), d.textlength(k, font=f, direction='rtl'))
