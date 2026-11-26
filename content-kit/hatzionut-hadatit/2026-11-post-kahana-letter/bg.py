"""Dimmed, teal-tinted Knesset plenum photo background (4:5) + photo credit."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
HERE = os.path.dirname(os.path.abspath(__file__))
SEC = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/shalev/fonts/SecularOne.ttf'
CREDIT = 'צילום: נועם מושקוביץ / דני שם טוב, דוברות הכנסת'
def make_bg(W=1080, H=1350):
    ph = Image.open(HERE + '/knesset-bg.jpg').convert('RGB'); s = H / ph.height
    ph = ph.resize((int(ph.width * s), H), Image.LANCZOS); x0 = int((ph.width - W) * .62); ph = ph.crop((x0, 0, x0 + W, H))
    ph = ImageEnhance.Color(ph).enhance(.35)
    tint = Image.new('RGB', (W, H), (20, 48, 52)); im = Image.blend(ph, tint, .72)
    g = Image.new('L', (1, H)); [g.putpixel((0, y), int(110 * (y / H) ** 1.6)) for y in range(H)]
    im.paste((10, 28, 30), (0, 0), g.resize((W, H)))
    return im.convert('RGBA')
def credit(im):
    d = ImageDraw.Draw(im); f = ImageFont.truetype(SEC, 24, layout_engine=ImageFont.Layout.RAQM)
    d.text((im.width - 40, im.height - 28), CREDIT, font=f, fill=(173, 213, 217, 200), anchor='rs', direction='rtl')
