"""Smotrich IG story (9:16): funeral of Rabbi Yitzhak Levy z"l (former NRP chairman and minister). Sombre B&W, no party branding."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter, ImageEnhance
HERE = os.path.dirname(os.path.abspath(__file__))
HAIM = os.path.abspath(os.path.join(HERE, '..', '..', 'fonts', 'HaimClassicv2FM-Bold.ttf'))
W, H = 1080, 1920; INK = (14, 16, 18); SOFT = (205, 208, 210)
def F(s): return ImageFont.truetype(HAIM, s, layout_engine=ImageFont.Layout.RAQM)
def bw(im, c=1.08, b=1.0): return ImageEnhance.Brightness(ImageEnhance.Contrast(ImageOps.grayscale(im).convert('RGB')).enhance(c)).enhance(b)
im = Image.new('RGB', (W, H), INK)
# bottom: Smotrich at the lectern and the crowd, same full width and height, stacked with soft feathered seams (nothing covered)
BH = 470; Y1 = H - 2 * BH + 60
eu = ImageOps.fit(bw(Image.open(HERE + '/eulogy.jpg').convert('RGB'), 1.05, .68), (W, BH), Image.LANCZOS, centering=(.5, .3))
cr = ImageOps.fit(bw(Image.open(HERE + '/crowd.jpg').convert('RGB'), 1.05, .62), (W, BH), Image.LANCZOS, centering=(.45, .55))
def vmask(h, top, bot):
    m = Image.new('L', (1, h))
    for y in range(h):
        v = 1.0
        if top: v = min(v, y / top)
        if bot: v = min(v, (h - 1 - y) / bot)
        m.putpixel((0, y), int(255 * max(0, v) ** 1.3))
    return m.resize((W, h))
im.paste(eu, (0, Y1), vmask(BH, 160, 60))
im.paste(cr, (0, Y1 + BH - 60), vmask(BH, 60, 0))
# portrait, framed
pr = Image.open(HERE + '/rav-levy.jpg').convert('RGB')
pr = pr.resize((pr.width * 2, pr.height * 2), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 50, 2))
pw, ph = 330, 440; src_r = pr.width / pr.height; ph = int(pw / src_r); pr = bw(pr.resize((pw, ph), Image.LANCZOS), 1.05, .95)
px, py = (W - pw) // 2, 150
d = ImageDraw.Draw(im)
d.rectangle((px - 14, py - 14, px + pw + 13, py + ph + 13), outline=SOFT, width=3)
im.paste(pr, (px, py))
y = py + ph + 55
def ctr(t, f, y, fill):
    d.text((W / 2, y), t, font=f, fill=fill, anchor='ma', direction='rtl')
ctr('הרב יצחק לוי ז״ל', F(104), y, (255, 255, 255))
ctr('יו״ר המפד״ל ושר החינוך לשעבר', F(50), y + 135, SOFT)
d.line((W / 2 - 70, y + 225, W / 2 + 70, y + 225), fill=SOFT, width=2)
ctr('יהי זכרו ברוך', F(64), y + 255, (255, 255, 255))
im.save(HERE + '/story.jpg', quality=95); print(y + 330)
