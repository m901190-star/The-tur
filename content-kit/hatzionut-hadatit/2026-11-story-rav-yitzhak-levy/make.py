"""Smotrich IG story (9:16): funeral of Rabbi Yitzhak Levy z"l (former NRP chairman and minister). Sombre B&W, no party branding."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter, ImageEnhance
HERE = os.path.dirname(os.path.abspath(__file__))
HAIM = os.path.abspath(os.path.join(HERE, '..', '..', 'fonts', 'HaimClassicv2FM-Bold.ttf'))
W, H = 1080, 1920; INK = (14, 16, 18); SOFT = (205, 208, 210)
def F(s): return ImageFont.truetype(HAIM, s, layout_engine=ImageFont.Layout.RAQM)
def bw(im, c=1.08, b=1.0): return ImageEnhance.Brightness(ImageEnhance.Contrast(ImageOps.grayscale(im).convert('RGB')).enhance(c)).enhance(b)
im = Image.new('RGB', (W, H), INK)
# bottom: two stacked B&W strips — Smotrich eulogizing, then the crowd — fading up into black
def strip(path, h, cen, br):
    p = bw(Image.open(HERE + '/' + path).convert('RGB'), 1.05, br); return ImageOps.fit(p, (W, h), Image.LANCZOS, centering=cen)
SH = 430; GAP = 8; Y0 = H - 2 * SH - GAP
im.paste(strip('eulogy.jpg', SH, (.47, .35), .78), (0, Y0))
im.paste(strip('crowd.jpg', SH, (.5, .62), 1.05), (0, Y0 + SH + GAP))
m = Image.new('L', (1, 260))
for y in range(260): m.putpixel((0, y), int(255 * (1 - y / 260) ** 1.2))
im.paste(Image.new('RGB', (W, 260), INK), (0, Y0), m.resize((W, 260)))
# portrait, framed
pr = Image.open(HERE + '/rav-levy.jpg').convert('RGB')
pr = pr.resize((pr.width * 2, pr.height * 2), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 50, 2))
pw, ph = 330, 440; pr = bw(ImageOps.fit(pr, (pw, ph), Image.LANCZOS, centering=(.5, .3)), 1.05, .95)
px, py = (W - pw) // 2, 150
d = ImageDraw.Draw(im)
d.rectangle((px - 14, py - 14, px + pw + 13, py + ph + 13), outline=SOFT, width=3)
im.paste(pr, (px, py))
y = py + ph + 55
def ctr(t, f, y, fill):
    d.text((W / 2, y), t, font=f, fill=fill, anchor='ma', direction='rtl')
ctr('הרב יצחק לוי ז״ל', F(104), y, (255, 255, 255))
ctr('יו״ר המפד״ל ושר לשעבר', F(50), y + 135, SOFT)
d.line((W / 2 - 70, y + 225, W / 2 + 70, y + 225), fill=SOFT, width=2)
ctr('יהי זכרו ברוך', F(64), y + 255, (255, 255, 255))
im.save(HERE + '/story.jpg', quality=95); print(y + 330)
