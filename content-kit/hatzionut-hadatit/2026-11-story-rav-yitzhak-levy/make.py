"""Smotrich IG story (9:16): funeral of Rabbi Yitzhak Levy z"l (former NRP chairman and minister). Sombre B&W, no party branding."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter, ImageEnhance
HERE = os.path.dirname(os.path.abspath(__file__))
HAIM = os.path.abspath(os.path.join(HERE, '..', '..', 'fonts', 'HaimClassicv2FM-Bold.ttf'))
W, H = 1080, 1920; INK = (14, 16, 18); SOFT = (205, 208, 210)
def F(s): return ImageFont.truetype(HAIM, s, layout_engine=ImageFont.Layout.RAQM)
def bw(im, c=1.08, b=1.0): return ImageEnhance.Brightness(ImageEnhance.Contrast(ImageOps.grayscale(im).convert('RGB')).enhance(c)).enhance(b)
im = Image.new('RGB', (W, H), INK)
# bottom: the crowd full-bleed in B&W fading up into black; Smotrich at the lectern framed like the portrait, sitting on the seam
cr = bw(Image.open(HERE + '/crowd.jpg').convert('RGB'), 1.08, .9)
CH = 900; cr = ImageOps.fit(cr, (W, CH), Image.LANCZOS, centering=(.42, .62))
m = Image.new('L', (1, CH))
for y in range(CH): m.putpixel((0, y), int(255 * min(1, y / 420) ** 1.5))
im.paste(cr, (0, H - CH), m.resize((W, CH)))
eu = bw(Image.open(HERE + '/eulogy.jpg').convert('RGB'), 1.08, .82)
EW, EH = 620, 380; eu = ImageOps.fit(eu, (EW, EH), Image.LANCZOS, centering=(.47, .33))
ex, ey = (W - EW) // 2, 1075
sh = Image.new('L', (EW + 120, EH + 120), 0); ImageDraw.Draw(sh).rectangle((60, 70, 60 + EW, 70 + EH), fill=200); sh = sh.filter(ImageFilter.GaussianBlur(25))
im.paste(Image.new('RGB', sh.size, (0, 0, 0)), (ex - 60, ey - 60), sh)
im.paste(eu, (ex, ey))
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
ImageDraw.Draw(im).rectangle((ex - 14, ey - 14, ex + EW + 13, ey + EH + 13), outline=SOFT, width=3)
im.save(HERE + '/story.jpg', quality=95); print(y + 330)
