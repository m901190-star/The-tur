"""Carousel slide 2 (4:5): the full letter incl. the State emblem, on the RZ teal background."""
import os, math
from PIL import Image, ImageDraw, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1350; DEEP, TEAL = (43, 81, 85), (80, 146, 153)
import sys; sys.path.insert(0, HERE); from bg import make_bg, credit
im = make_bg(W, H)
src = Image.open(HERE + '/source-letter.jpg').convert('RGB').crop((8, 0, 1312, 1814))
ch = H - 90; card = src.resize((int(ch * src.width / src.height), ch), Image.LANCZOS)
m = Image.new('L', card.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, card.width - 1, card.height - 1), 20, fill=255)
sh = Image.new('L', (card.width + 80, card.height + 80), 0); sh.paste(m, (40, 52)); sh = sh.filter(ImageFilter.GaussianBlur(18))
X0, TOP = (W - card.width) // 2, 45; im.paste((0, 0, 0, 120), (X0 - 40, TOP - 40), sh); im.paste(card, (X0, TOP), m)
credit(im); im.convert('RGB').save(HERE + '/slide2-letter.jpg', quality=95); print(card.size)
