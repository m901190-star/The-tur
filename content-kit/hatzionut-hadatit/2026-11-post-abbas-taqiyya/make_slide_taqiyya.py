"""Carousel middle slide: 'הכירו את שיטת ה״תקייה״' + Smotrich's own definition (exact text), key words marked."""
import os, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
HAIM = os.path.abspath(os.path.join(HERE, '..', '..', 'fonts', 'HaimClassicv2FM-Bold.ttf'))
W, H = 1080, 1350; DEEP, TEAL, LT, PALE, NIGHT = (43, 81, 85), (80, 146, 153), (105, 180, 189), (173, 213, 217), (14, 26, 28)
def F(s): return ImageFont.truetype(HAIM, s, layout_engine=ImageFont.Layout.RAQM)
# background: the portrait, blurred + darkened (continuity with slides 1/3)
bg = ImageOps.fit(Image.open(HERE + '/src/abbas.jpg').convert('L'), (W, H), Image.LANCZOS, centering=(.5, .35)).filter(ImageFilter.GaussianBlur(30)).convert('RGB')
im = Image.blend(bg, Image.new('RGB', (W, H), NIGHT), .82)
d = ImageDraw.Draw(im); R = W - 80
# header
y = 170
d.text((R, y), 'הכירו את', font=F(78), fill='white', anchor='ra', direction='rtl')
y += 120; f = F(150); t = 'שיטת ה״תקייה״'
while d.textlength(t, font=f, direction='rtl') > W - 230: f = F(f.size - 4)
bb = d.textbbox((0, 0), t, font=f, anchor='ls', direction='rtl'); tw, ih = bb[2] - bb[0], bb[3] - bb[1]
d.rounded_rectangle((R - tw - 60, y, R + 8, y + ih + 56), 18, fill=LT)
d.text((R - 28, y + 28 - bb[1]), t, font=f, fill=NIGHT, anchor='rs', direction='rtl')
y += ih + 56 + 90
d.rectangle((R - 6, y + 8, R, y + 6 * 94 - 20), fill=LT)
# body: exact words, marked keywords get a teal marker underlay
fb = F(62); lh = 94; L = 150
lines = [[('שמבוססת על', 0), ('הסתרה', 1)],
         [('ונכונות', 0), ('לשקר', 1)],
         [('ולומר כל דבר שהצד השני', 0)],
         [('רוצה לשמוע', 0)],
         [('כדי לקבל את עמדות', 0)],
         [('הכח הרצויות.', 0)]]
for k, parts in enumerate(lines):
    x = R - 30; yy = y + k * lh
    for (txt, mark) in parts:
        w_ = d.textlength(txt, font=fb, direction='rtl')
        if mark: d.rectangle((x - w_ - 10, yy + 26, x + 6, yy + 64), fill=TEAL)
        d.text((x, yy), txt, font=fb, fill='white' if k < 4 else PALE, anchor='ra', direction='rtl')
        x -= w_ + d.textlength(' ', font=fb)
d.text((W // 2, H - 42), 'החליקו לשקופית הבאה ←', font=F(40), fill=PALE, anchor='mm', direction='rtl')
im.save(HERE + '/slide2.jpg', quality=95); print('ok')
