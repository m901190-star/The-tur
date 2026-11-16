"""Private joke WhatsApp sticker (512x512, transparent): Matan Kahana cutout + 'כהנא חי!' / '(מתן, לא מאיר)'. No Kach emblem."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); KB = HERE + '/../../fonts/HaimClassicv2FM-Bold.ttf'
S = 512; NAVY, RED = (24, 44, 104), (214, 40, 40)
def F(s): return ImageFont.truetype(KB, s, layout_engine=ImageFont.Layout.RAQM)
def outline(img, r, col=(255, 255, 255, 255)):
    a = img.getchannel('A').filter(ImageFilter.MaxFilter(r * 2 + 1)); o = Image.new('RGBA', img.size, col); o.putalpha(a); o.alpha_composite(img); return o
cut = Image.open(HERE + '/kahana-cut.png').convert('RGBA'); a = cut.getchannel('A').point(lambda v: 255 if v > 150 else 0); cut.putalpha(a); cut = cut.crop(a.getbbox())
s = 330 / cut.height; cut = cut.resize((int(cut.width * s), 330), Image.LANCZOS)
pad = Image.new('RGBA', (cut.width + 30, cut.height + 30), (0, 0, 0, 0)); pad.paste(cut, (15, 15)); cut = outline(pad, 8)
st = Image.new('RGBA', (S, S), (0, 0, 0, 0)); st.alpha_composite(cut, ((S - cut.width) // 2, S - cut.height - 4))
t = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(t)
d.text((S / 2, 14), 'כהנא חי!', font=F(118), fill=NAVY + (255,), anchor='ma', direction='rtl')
d.rounded_rectangle((S / 2 - 150, 400, S / 2 + 150, 462), 31, fill=RED + (255,))
d.text((S / 2, 431), '(מתן, לא מאיר)', font=F(40), fill=(255, 255, 255, 255), anchor='mm', direction='rtl')
st.alpha_composite(outline(t, 6))
st.save(HERE + '/sticker.png'); st.save(HERE + '/sticker.webp', 'WEBP', quality=90)
prev = Image.new('RGBA', (S, S), (200, 220, 200, 255)); prev.alpha_composite(st); prev.convert('RGB').save('/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/sticker_prev.png')
