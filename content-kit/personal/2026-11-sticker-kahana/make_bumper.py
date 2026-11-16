"""Private joke: wide thin yellow bumper sticker 'כהנא חי' with a large B&W Matan Kahana portrait. No Kach emblem."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance
HERE = os.path.dirname(os.path.abspath(__file__)); KB = HERE + '/../../fonts/HaimClassicv2FM-Bold.ttf'
W, H = 1500, 420; Y, K = (255, 222, 0), (0, 0, 0)
def F(s): return ImageFont.truetype(KB, s, layout_engine=ImageFont.Layout.RAQM)
base = Image.new('RGBA', (W, H), Y + (255,))
cut = Image.open(HERE + '/kahana-cut.png').convert('RGBA'); from PIL import ImageFilter; a = cut.getchannel('A').point(lambda v: 255 if v > 150 else 0).filter(ImageFilter.GaussianBlur(1.2)); cut.putalpha(a); cut = cut.crop(a.getbbox())
cut = cut.crop((0, 0, cut.width, int(cut.height * .62)))                      # head + shoulders only
g = ImageEnhance.Contrast(ImageOps.grayscale(cut.convert('RGB'))).enhance(1.35)
cut = Image.merge('RGBA', (g, g, g, cut.getchannel('A')))
s = (H + 40) / cut.height; cut = cut.resize((int(cut.width * s), int(cut.height * s)), Image.LANCZOS)
base.alpha_composite(cut, (10, H - cut.height + 40))
d = ImageDraw.Draw(base); xr = W - 60
d.text((xr, H / 2 + 6), 'כהנא חי', font=F(232), fill=K, anchor='rm', direction='rtl')
d.rectangle((0, 0, W - 1, H - 1), outline=K, width=10)
m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, W - 1, H - 1), 22, fill=255)
out = Image.new('RGBA', (W, H), (0, 0, 0, 0)); out.paste(base, (0, 0), m)
out.save(HERE + '/bumper.png'); out.convert('RGB').save(HERE + '/bumper.jpg', quality=95); print('ok', cut.size)
