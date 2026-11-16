"""Smotrich IG post (4:5), no party logo: the letter to MK Matan Kahana (crop: addressee -> the two conditions, highlighted) + his line. Full text in caption."""
import os, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
KB = HERE + '/../../fonts/HaimClassicv2FM-Bold.ttf'
W, H = 1080, 1350; DEEP, TEAL, LT, PALE = (43, 81, 85), (80, 146, 153), (105, 180, 189), (173, 213, 217)
def F(p, s): return ImageFont.truetype(p, s, layout_engine=ImageFont.Layout.RAQM)
import sys; sys.path.insert(0, HERE); from bg import make_bg, credit
im = make_bg(W, H); d = ImageDraw.Draw(im)
src = Image.open(HERE + '/source-letter.jpg').convert('RGB')
hl = Image.new('RGBA', src.size, (0, 0, 0, 0)); hd = ImageDraw.Draw(hl)
for x0, yc in [(185, 875), (185, 914), (415, 953), (185, 1030), (1030, 1068)]:      # the two conditions
    hd.rectangle((x0 - 6, yc - 19, 1094, yc + 19), fill=(120, 205, 214, 110))
src = Image.alpha_composite(src.convert('RGBA'), hl).convert('RGB')
crop = src.crop((150, 310, 1170, 1105))
cw = 900; card = crop.resize((cw, int(cw * crop.height / crop.width)), Image.LANCZOS)
m = Image.new('L', card.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, card.width - 1, card.height - 1), 24, fill=255)
sh = Image.new('L', (card.width + 80, card.height + 80), 0); sh.paste(m, (40, 52)); sh = sh.filter(ImageFilter.GaussianBlur(18))
TOP = 70; X0 = (W - cw) // 2; im.paste((0, 0, 0, 120), (X0 - 40, TOP - 40), sh); im.paste(card, (X0, TOP), m)
R = W - 90; y = TOP + card.height + 60
d.rectangle((R - 6, y + 6, R, y + 176), fill=LT)
fk = F(KB, 74)
for i, l in enumerate(['יש למתן אפשרות', 'להיבחר ברוב ציוני.']):
    d.text((R - 30, y + 8 + i * 86), l, font=fk, fill=(255, 255, 255), anchor='ra', direction='rtl')
y2 = y + 2 * 86 + 48; f2 = F(KB, 64); t = 'הבחירה בידיים שלו.'; tw = d.textlength(t, font=f2, direction='rtl')
d.rounded_rectangle((R - tw - 56, y2 - 4, R + 6, y2 + 86), 14, fill=LT); d.text((R - 26, y2 + 4), t, font=f2, fill=DEEP, anchor='ra', direction='rtl')
credit(im); im.convert('RGB').save(HERE + '/post.jpg', quality=95); print(y2 + 86)
