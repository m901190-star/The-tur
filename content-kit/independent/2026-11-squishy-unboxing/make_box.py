"""Flat front artwork for 'המארז של גוש השינוי' squishy box (draft). Window area left empty for the squishies."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
KB = HERE + '/../../fonts/HaimClassicv2FM-Bold.ttf'
SEC = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/shalev/fonts/SecularOne.ttf'
W, H = 1800, 1100; NAVY, BLUE, LB, RED, WHITE = (24, 44, 104), (40, 90, 200), (110, 180, 240), (220, 40, 50), (255, 255, 255)
def F(p, s): return ImageFont.truetype(p, s, layout_engine=ImageFont.Layout.RAQM)
im = Image.new('RGBA', (W, H), WHITE); d = ImageDraw.Draw(im)
d.rectangle((0, 0, W, 250), fill=NAVY); d.rectangle((0, 250, W, 262), fill=LB)
d.text((W / 2, 30), 'המארז של גוש השינוי', font=F(KB, 140), fill=WHITE, anchor='ma', direction='rtl')
d.text((W / 2, 178), 'מארז סקווישים · 5 יחידות', font=F(SEC, 44), fill=LB, anchor='ma', direction='rtl')
# window
WX0, WY0, WX1, WY1 = 70, 300, W - 70, 830
d.rounded_rectangle((WX0, WY0, WX1, WY1), 30, fill=(232, 238, 246), outline=NAVY, width=10)
for i in range(5):
    x0 = WX0 + 30 + i * (WX1 - WX0 - 60) / 5; d.rounded_rectangle((x0 + 12, WY0 + 30, x0 + (WX1 - WX0 - 60) / 5 - 12, WY1 - 30), 24, outline=(190, 205, 225), width=5)
# badge
bx, by, r = W - 150, 210, 105
d.ellipse((bx - r, by - r + 60, bx + r, by + r + 60), fill=RED); d.text((bx, by + 60), 'חדש!', font=F(KB, 64), fill=WHITE, anchor='mm', direction='rtl')
# logos strip
d.rectangle((0, 860, W, H), fill=WHITE); d.rectangle((0, 852, W, 860), fill=LB)
logos = ['beyahad', 'yashar', 'democrats', 'israel-beytenu']; slot = (W - 140) / 4
for i, n in enumerate(logos):
    lg = Image.open(HERE + f'/logos/{n}.png').convert('RGBA')
    from PIL import ImageOps
    a = lg.getchannel('A'); g = ImageOps.invert(lg.convert('L')).point(lambda v: 255 if v > 20 else 0)
    bb = Image.composite(g, Image.new('L', lg.size, 0), a).getbbox(); lg = lg.crop(bb)
    s = min((slot - 80) / lg.width, 140 / lg.height); lg = lg.resize((int(lg.width * s), int(lg.height * s)), Image.LANCZOS)
    cx = W - 70 - slot * (i + .5); im.alpha_composite(lg, (int(cx - lg.width / 2), int(950 - lg.height / 2)))
d.text((W / 2, H - 30), 'הבטחות תקפות עד למוצאי הבחירות', font=F(SEC, 34), fill=NAVY, anchor='ms', direction='rtl')
im.convert('RGB').save(HERE + '/box-front.png'); print('ok')
