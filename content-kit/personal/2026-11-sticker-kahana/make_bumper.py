"""Private joke: wide thin yellow bumper-sticker style 'כהנא חי' with Matan Kahana cutout. No Kach emblem (no star, no fist)."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); KB = HERE + '/../../fonts/HaimClassicv2FM-Bold.ttf'
W, H = 1500, 420; Y, K = (255, 222, 0), (0, 0, 0)
def F(s): return ImageFont.truetype(KB, s, layout_engine=ImageFont.Layout.RAQM)
im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
d.rounded_rectangle((0, 0, W - 1, H - 1), 26, fill=Y + (255,)); d.rounded_rectangle((14, 14, W - 15, H - 15), 18, outline=K, width=6)
cut = Image.open(HERE + '/kahana-cut.png').convert('RGBA'); a = cut.getchannel('A').point(lambda v: 255 if v > 150 else 0); cut.putalpha(a); cut = cut.crop(a.getbbox())
s = (H - 40) / cut.height; cut = cut.resize((int(cut.width * s), H - 40), Image.LANCZOS)
m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).rounded_rectangle((20, 20, W - 21, H - 21), 14, fill=255)
lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); lay.alpha_composite(cut, (40, H - 20 - cut.height))
im.alpha_composite(Image.composite(lay, Image.new('RGBA', (W, H), (0, 0, 0, 0)), m))
d = ImageDraw.Draw(im); xr = W - 70
d.text((xr, H / 2 + 8), 'כהנא חי', font=F(280), fill=K, anchor='rm', direction='rtl')
im.save(HERE + '/bumper.png'); im.convert('RGB').save(HERE + '/bumper.jpg', quality=95); print('ok')
