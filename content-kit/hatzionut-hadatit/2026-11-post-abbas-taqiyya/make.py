"""Smotrich IG post: Mansour Abbas's 'dramatic' declaration = taqiyya. Dictionary-entry layout, B&W portrait (unaltered face),
only exact phrases from Smotrich's text. 1080x1350."""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter, ImageEnhance
HERE = os.path.dirname(os.path.abspath(__file__)); KIT = os.path.abspath(HERE + '/../..')
HAIM = KIT + '/fonts/HaimClassicv2FM-Bold.ttf'
W, H = 1080, 1350
DEEP, TEAL, LT, PALE, NIGHT = (43, 81, 85), (80, 146, 153), (105, 180, 189), (173, 213, 217), (14, 26, 28)
def F(s): return ImageFont.truetype(HAIM, s, layout_engine=ImageFont.Layout.RAQM)
def tw(d, t, f): return d.textlength(t, font=f, direction='rtl')
def wrap(d, text, f, maxw):
    out, cur = [], ''
    for w in text.split():
        t = (cur + ' ' + w).strip()
        if tw(d, t, f) <= maxw: cur = t
        else: out.append(cur); cur = w
    return out + [cur]

im = Image.new('RGB', (W, H), NIGHT)
# subtle vertical gradient
g = np.linspace(0, 1, H)[:, None, None]
im = Image.fromarray((np.array(NIGHT) * (1 - g * .4) + np.array(DEEP) * (g * .4)).astype(np.uint8).repeat(W, 1))
d = ImageDraw.Draw(im)

# ---- portrait: B&W, film grain, left column ----
ph = Image.open(HERE + '/src/abbas.jpg').convert('L')
PW, PH = 500, 640
ph = ImageOps.fit(ph, (PW, PH), Image.LANCZOS, centering=(.5, .3))
ph = ImageEnhance.Contrast(ph).enhance(1.18).filter(ImageFilter.UnsharpMask(2, 60, 2))
rng = np.random.default_rng(4); a = np.asarray(ph).astype(np.float32) + rng.normal(0, 9, (PH, PW))
ph = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGB')
# fade the portrait's right edge into the background
xs = np.clip((PW - np.arange(PW)) / 160, 0, 1)[None, :]; ys = np.clip((PH - np.arange(PH)) / 140, 0, 1)[:, None]
m = Image.fromarray((255 * np.minimum(xs, ys) ** 1.3).astype(np.uint8))
PX, PY = 0, 380
im.paste(ph, (PX, PY), m)
d = ImageDraw.Draw(im)

# ---- top quote ----
R = W - 64; y = 70
f1 = F(54)
for line in ['מי שיתרשם מההכרזה ה״דרמטית״', 'של מנסור עבאס על חמאס – ארגון טרור,']:
    d.text((R, y), line, font=f1, fill='white', anchor='ra', direction='rtl'); y += 68
fh = F(60); t = 'פשוט לא מכיר את עבאס'
bb = d.textbbox((0, 0), t, font=fh, anchor='ls', direction='rtl'); w_ = bb[2] - bb[0]; h_ = bb[3] - bb[1]
d.rectangle((R - w_ - 36, y + 8, R + 4, y + 8 + h_ + 34), fill=LT)
d.text((R - 16, y + 8 + 17 - bb[1]), t, font=fh, fill=NIGHT, anchor='rs', direction='rtl')

# ---- dictionary entry (right column) ----
CR = W - 64; CL = 520; y = 420
fw = F(190)
d.text((CR, y), 'תקייה', font=fw, fill='white', anchor='ra', direction='rtl')
y += 215
fs = F(34)
d.text((CR, y), 'ש״ע  |  מונח באסלאם', font=F(36), fill=PALE, anchor='ra', direction='rtl')
y += 58
d.line((CL, y, CR, y), fill=LT, width=4); y += 30
fd = F(44)
defin = 'הסתרה ונכונות לשקר ולומר כל דבר שהצד השני רוצה לשמוע'
for i, line in enumerate(wrap(d, defin, fd, CR - CL)):
    d.text((CR, y), line, font=fd, fill='white', anchor='ra', direction='rtl'); y += 60
y += 10
for line in ['כדי לקבל את עמדות', 'הכח הרצויות.']:
    d.text((CR, y), line, font=F(38), fill=PALE, anchor='ra', direction='rtl'); y += 52

# ---- bottom stripe ----
SY = 1105
d.rectangle((0, SY, W, H), fill=TEAL); d.rectangle((0, SY, W, SY + 8), fill=LT)
ft = F(84); t = 'אסור ליפול למלכודת הזו'
d.text((W // 2, SY + 40), t, font=ft, fill='white', anchor='ma', direction='rtl')
fb = F(40)
d.text((W // 2, SY + 150), 'ולהקים ממשלת אסון שתישען על אויבי ישראל.', font=fb, fill=NIGHT, anchor='ma', direction='rtl')
out = HERE + '/post.jpg'; im.save(out, quality=95); print(out)
