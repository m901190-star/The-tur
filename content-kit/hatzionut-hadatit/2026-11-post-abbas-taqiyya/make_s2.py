"""Carousel v2, slide 2: 'הכירו את שיטת ה״תקייה״' — a speech-bubble sticker ('חמאס הוא ארגון טרור', the ynet wording)
peeling off to reveal Smotrich's words underneath. No photo (the only Abbas portrait is used once, on slide 3)."""
import os, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
HAIM = os.path.abspath(os.path.join(HERE, '..', '..', 'fonts', 'HaimClassicv2FM-Bold.ttf'))
W, H = 1080, 1350
DEEP, TEAL, LT, PALE, NIGHT = (43, 81, 85), (80, 146, 153), (105, 180, 189), (173, 213, 217), (14, 26, 28)
YEL = (255, 222, 0)
def F(s): return ImageFont.truetype(HAIM, s, layout_engine=ImageFont.Layout.RAQM)
rng = np.random.default_rng(11)
def concrete():
    n = sum(np.asarray(Image.fromarray((rng.random((H // s + 1, W // s + 1)) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), np.float32) * w
            for s, w in [(4, .25), (16, .35), (64, .4)])
    n = (n - n.mean()) / n.std()
    base = np.array(NIGHT, np.float32)[None, None] * (1 + .10 * n[..., None]) + np.array(DEEP, np.float32)[None, None] * .25
    yy, xx = np.mgrid[0:H, 0:W]; v = 1 - .55 * (((xx - W / 2) / W) ** 2 + ((yy - H * .45) / H) ** 2) * 2.2
    return Image.fromarray(np.clip(base * v[..., None], 0, 255).astype(np.uint8))

im = concrete().convert('RGBA'); d = ImageDraw.Draw(im); R = W - 70
# header
d.text((R, 80), 'הכירו את', font=F(70), fill='white', anchor='ra', direction='rtl')
fh = F(150); t = 'שיטת ה״תקייה״'
while d.textlength(t, font=fh, direction='rtl') > W - 150: fh = F(fh.size - 4)
d.text((R + 6, 160 + 8), t, font=fh, fill=(0, 0, 0, 160), anchor='ra', direction='rtl')
d.text((R, 160), t, font=fh, fill=LT, anchor='ra', direction='rtl')

# ---- bubble geometry ----
BX0, BY0, BX1, BY1 = 110, 420, 970, 880
def bubble_mask():
    m = Image.new('L', (W, H), 0); md = ImageDraw.Draw(m)
    md.rounded_rectangle((BX0, BY0, BX1, BY1), 46, fill=255)
    md.polygon([(BX1 - 210, BY1 - 10), (BX1 - 60, BY1 + 120), (BX1 - 110, BY1 - 10)], fill=255)   # tail
    return m
bm = bubble_mask()
# underlayer: what is really underneath (Smotrich's words), visible where the sticker has peeled
under = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ud = ImageDraw.Draw(under)
ud.rounded_rectangle((BX0, BY0, BX1, BY1), 46, fill=TEAL + (255,))
fu = F(96)
while ud.textlength('לשקר', font=fu, direction='rtl') > 215: fu = F(fu.size - 2)
ud.text((350, 800), 'לשקר', font=fu, fill=YEL, anchor='ra', direction='rtl')
under.putalpha(Image.fromarray(np.minimum(np.asarray(under.getchannel('A')), np.asarray(bm))))
# sticker: white bubble with the headline wording
stk = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(stk)
stk.paste((250, 250, 248, 255), (0, 0), bm)
fs = F(96)
sd.text((BX1 - 60, BY0 + 70), 'חמאס הוא', font=fs, fill=NIGHT, anchor='ra', direction='rtl')
sd.text((BX1 - 60, BY0 + 185), 'ארגון טרור', font=fs, fill=NIGHT, anchor='ra', direction='rtl')
# peel: everything on the lower-left side of the fold line is lifted off
P0, P1 = np.array([BX0 - 10, BY0 + 215.]), np.array([BX0 + 450, BY1 + 10.])
nrm = np.array([P1[1] - P0[1], -(P1[0] - P0[0])]); nrm /= np.linalg.norm(nrm)
yy, xx = np.mgrid[0:H, 0:W]
side = (xx - P0[0]) * nrm[0] + (yy - P0[1]) * nrm[1]          # >0 : peeled region (lower-left)
if ((BX0 + 20 - P0[0]) * nrm[0] + (BY1 - 20 - P0[1]) * nrm[1]) < 0: side = -side
keep = Image.fromarray(((side <= 0) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(.8))
a = np.minimum(np.asarray(stk.getchannel('A')), np.asarray(keep)); stk.putalpha(Image.fromarray(a))
# flap: the peeled part reflected over the fold, curled (scaled toward the fold), back side of the paper
peel = (side > 0) & (np.asarray(bm) > 0)
ys, xs = np.nonzero(peel); dist = (xs - P0[0]) * nrm[0] + (ys - P0[1]) * nrm[1]
curl = .55
fx = xs - nrm[0] * dist * (1 + curl); fy = ys - nrm[1] * dist * (1 + curl)
flap = np.zeros((H, W, 4), np.float32)
fxi, fyi = np.clip(fx.astype(int), 0, W - 1), np.clip(fy.astype(int), 0, H - 1)
shade = 205 + 40 * np.clip(1 - dist / (dist.max() + 1e-6), 0, 1)                 # lighter near the fold
flap[fyi, fxi, :3] = shade[:, None]; flap[fyi, fxi, 3] = 255
flap_im = Image.fromarray(flap.astype(np.uint8), 'RGBA').filter(ImageFilter.MaxFilter(3))
fsh = flap_im.getchannel('A').filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * .55))
# compose: drop shadow of the sticker, underlayer, sticker, flap shadow, flap
sh = Image.fromarray(np.maximum(np.asarray(bm) * 0, a)).filter(ImageFilter.GaussianBlur(18)).point(lambda v: int(v * .6))
im.paste((0, 0, 0, 255), (12, 22), sh)
im.alpha_composite(under); im.alpha_composite(stk)
shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0)); shadow.putalpha(fsh); im.alpha_composite(shadow, (8, 12))
im.alpha_composite(flap_im)
# rest of his sentence under the bubble
d = ImageDraw.Draw(im); y = BY1 + 140
for line, col in [('הסתרה ונכונות לשקר ולומר כל דבר', 'white'), ('שהצד השני רוצה לשמוע', 'white'), ('כדי לקבל את עמדות הכח הרצויות.', PALE)]:
    d.text((R, y), line, font=F(54), fill=col, anchor='ra', direction='rtl'); y += 72
d.text((70, H - 48), '←', font=F(60), fill=PALE, anchor='lm')
im.convert('RGB').save(HERE + '/slide2.jpg', quality=95); print('ok')
