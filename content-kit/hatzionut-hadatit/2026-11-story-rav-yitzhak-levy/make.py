"""Smotrich IG story (9:16): funeral of Rabbi Yitzhak Levy z"l (former NRP chairman and minister). Sombre B&W, no party branding."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter, ImageEnhance
HERE = os.path.dirname(os.path.abspath(__file__))
HAIM = os.path.abspath(os.path.join(HERE, '..', '..', 'fonts', 'HaimClassicv2FM-Bold.ttf'))
W, H = 1080, 1920; INK = (14, 16, 18); SOFT = (205, 208, 210)
def F(s): return ImageFont.truetype(HAIM, s, layout_engine=ImageFont.Layout.RAQM)
def bw(im, c=1.08, b=1.0): return ImageEnhance.Brightness(ImageEnhance.Contrast(ImageOps.grayscale(im).convert('RGB')).enhance(c)).enhance(b)
im = Image.new('RGB', (W, H), INK)
# bottom: Smotrich at the lectern, B&W, fading up into black
eu = bw(Image.open(HERE + '/eulogy.jpg').convert('RGB'), 1.05, .72)
eu = ImageOps.fit(eu, (W, 760), Image.LANCZOS, centering=(.47, .4))
m = Image.new('L', (1, 760))
for y in range(760): m.putpixel((0, y), int(255 * min(1, y / 320) ** 1.4))
im.paste(eu, (0, H - 760), m.resize((W, 760)))
# portrait, framed
pr = Image.open(HERE + '/rav-levy.jpg').convert('RGB')
pr = pr.resize((pr.width * 2, pr.height * 2), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 50, 2))
pw, ph = 420, 560; pr = bw(ImageOps.fit(pr, (pw, ph), Image.LANCZOS, centering=(.5, .3)), 1.05, .95)
px, py = (W - pw) // 2, 230
d = ImageDraw.Draw(im)
d.rectangle((px - 14, py - 14, px + pw + 13, py + ph + 13), outline=SOFT, width=3)
im.paste(pr, (px, py))
y = py + ph + 70
def ctr(t, f, y, fill):
    d.text((W / 2, y), t, font=f, fill=fill, anchor='ma', direction='rtl')
ctr('הרב יצחק לוי ז״ל', F(104), y, (255, 255, 255))
ctr('יו״ר המפד״ל ושר בממשלות ישראל', F(50), y + 135, SOFT)
d.line((W / 2 - 70, y + 225, W / 2 + 70, y + 225), fill=SOFT, width=2)
ctr('יהי זכרו ברוך', F(64), y + 255, (255, 255, 255))
im.save(HERE + '/story.jpg', quality=95); print(y + 330)
