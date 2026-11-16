"""Yesha squishy kit - flat box front (draft). Yesha palette, white logo, Haim headline, no '!'."""
import os
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
KB = HERE + '/../../fonts/HaimClassicv2FM-Bold.ttf'; SEC = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/shalev/fonts/SecularOne.ttf'
LOGO = HERE + '/../../clients/yesha/logo_white.png'
W, H = 1800, 1100; NAVY, BLUE, LB, WHITE = (23, 64, 104), (37, 102, 162), (39, 164, 209), (255, 255, 255)
def F(p, s): return ImageFont.truetype(p, s, layout_engine=ImageFont.Layout.RAQM)
TITLE = os.environ.get('TITLE', 'מועכים את התעמולה'); SUB = 'ערכת סקווישים · 4 יחידות'
im = Image.new('RGBA', (W, H), WHITE); d = ImageDraw.Draw(im)
d.rectangle((0, 0, W, 270), fill=NAVY); d.rectangle((0, 270, W, 284), fill=LB)
d.text((W / 2 + 110, 40), TITLE, font=F(KB, 124), fill=WHITE, anchor='ma', direction='rtl')
d.text((W / 2 + 110, 190), SUB, font=F(SEC, 44), fill=LB, anchor='ma', direction='rtl')
lg = Image.open(LOGO).convert('RGBA'); lg = lg.crop(lg.getchannel('A').getbbox()); lg = lg.resize((200, int(200 * lg.height / lg.width)), Image.LANCZOS)
im.alpha_composite(lg, (60, (270 - lg.height) // 2))
WX0, WY0, WX1, WY1 = 70, 320, W - 70, 960
d.rounded_rectangle((WX0, WY0, WX1, WY1), 30, fill=(232, 238, 246), outline=NAVY, width=10)
for i in range(4):
    x0 = WX0 + 30 + i * (WX1 - WX0 - 60) / 4; d.rounded_rectangle((x0 + 12, WY0 + 30, x0 + (WX1 - WX0 - 60) / 4 - 12, WY1 - 30), 24, outline=(190, 205, 225), width=5)
d.rectangle((0, 990, W, H), fill=BLUE)
d.text((W / 2, 1045), 'מועצת יש״ע · יהודה ושומרון', font=F(SEC, 40), fill=WHITE, anchor='mm', direction='rtl')
im.convert('RGB').save(HERE + '/box-front.png'); print('ok')
