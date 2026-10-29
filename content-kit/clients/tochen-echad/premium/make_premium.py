"""Tochen Echad Premium logo: three directions built on the original mark and wordmark (transparent PNGs + presentation sheet)."""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
FB = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/pro-video-editing/assets/fonts/Karantina-Bold.ttf'
FR = FB.replace('Bold', 'Regular')
SPLIT = 2089
INK = (0x14, 0x18, 0x1D); YEL = (0xFF, 0xE4, 0x19); WHITE = (255, 255, 255)
GOLD = [(0x8A, 0x63, 0x1E), (0xD9, 0xAE, 0x4F), (0xF7, 0xE3, 0x9C), (0xC8, 0x95, 0x3A), (0x8E, 0x66, 0x22)]

logo = Image.open(HERE + '/../logo.png').convert('RGBA'); A = np.array(logo)
yel = A[:, :, 2] < 120; mark = np.zeros(yel.shape, bool); mark[:, SPLIT:] = True
def part(m): b = A.copy(); b[~m, 3] = 0; return Image.fromarray(b, 'RGBA')
MY, MW, WORD, TAG = part(yel & mark), part(~yel & mark), part(yel & ~mark), part(~yel & ~mark)

def gold_fill(alpha):
    """Brushed-gold gradient (diagonal) clipped to an alpha mask."""
    w, h = alpha.size; yy, xx = np.mgrid[0:h, 0:w]; u = ((xx / w) * .55 + (yy / h) * .45)
    stops = np.linspace(0, 1, len(GOLD)); out = np.zeros((h, w, 3))
    for c in range(3): out[..., c] = np.interp(u, stops, [g[c] for g in GOLD])
    out += (np.random.default_rng(2).standard_normal((h, w)) * 3)[..., None] + 6 * np.sin(yy / h * 40)[..., None]
    im = Image.fromarray(out.clip(0, 255).astype(np.uint8)).convert('RGBA'); im.putalpha(alpha); return im
def recolor(layer, col): im = Image.new('RGBA', layer.size, col + (0,)); im.putalpha(layer.getchannel('A')); return im
def comp(*ls):
    out = Image.new('RGBA', ls[0].size, (0, 0, 0, 0))
    for l in ls: out.alpha_composite(l)
    return out
def crop(im): return im.crop(im.getchannel('A').getbbox())
def text_layer(s, size, col, font=FB, track=0):
    f = ImageFont.truetype(font, size); d = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
    w = int(d.textlength(s, font=f, direction='rtl')) + 20; im = Image.new('RGBA', (w + track * len(s), int(size * 1.4)), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((im.width - 10, size * .7), s, font=f, fill=col, anchor='rm', direction='rtl'); return crop(im)
W0, H0 = logo.size
wordmark_h = int(np.argwhere(np.array(WORD.getchannel('A')).any(1))[-1][0])         # bottom of "תוכן אחד"
tag_x1 = int(np.argwhere(np.array(TAG.getchannel('A')).any(0))[-1][0])

def lockup(mark_y, mark_w, word, under, under_gap=40, under_h=None):
    """Mark + wordmark from the original, replacing the white tagline with `under` (right-aligned to the tagline's right edge)."""
    base = comp(mark_y, mark_w, word)
    H = max(base.height, wordmark_h + under_gap + under.height + 20)
    c = Image.new('RGBA', (base.width, H), (0, 0, 0, 0)); c.alpha_composite(base)
    c.alpha_composite(under, (tag_x1 - under.width, wordmark_h + under_gap)); return crop(c)

# A. Gold: whole logo in gold foil, "פרימיום" in spaced gold
gold_all = gold_fill(comp(MY, MW, WORD).getchannel('A'))
gm_y = gold_fill(MY.getchannel('A')); gm_w = recolor(MW, (0xF7, 0xE3, 0x9C)); gw = gold_fill(WORD.getchannel('A'))
a = lockup(gm_y, gm_w, gw, gold_fill(text_layer('פ ר י מ י ו ם', 230, WHITE, FR).getchannel('A')))
# B. Classic + gold badge: original yellow/white kept, a gold "PREMIUM" plate under the wordmark
plate_txt = text_layer('פרימיום', 200, INK)
plate = Image.new('RGBA', (plate_txt.width + 120, plate_txt.height + 70), (0, 0, 0, 0))
m = Image.new('L', plate.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, plate.width - 1, plate.height - 1), 26, fill=255)
plate = gold_fill(m); plate.alpha_composite(plate_txt, (60, 35))
b = lockup(MY, MW, WORD, plate)
# C. Black & gold: mark in gold, wordmark white, thin gold rule + "פרימיום"
rule_txt = gold_fill(text_layer('פ ר י מ י ו ם', 200, WHITE, FR).getchannel('A'))
under = Image.new('RGBA', (tag_x1 - 40, rule_txt.height), (0, 0, 0, 0)); under.alpha_composite(rule_txt, (under.width - rule_txt.width, 0))
rl = Image.new('L', under.size, 0); ImageDraw.Draw(rl).rectangle((0, under.height // 2 - 4, under.width - rule_txt.width - 50, under.height // 2 + 4), fill=255)
under.alpha_composite(gold_fill(rl))
c = lockup(gm_y, recolor(MW, (0xF7, 0xE3, 0x9C)), recolor(WORD, WHITE), under)

for name, im in (('A-gold', a), ('B-classic-badge', b), ('C-black-gold', c)):
    im.save(HERE + f'/tochen-echad-premium-{name}.png')

# presentation sheet
SW, SH = 1800, 2100; sheet = Image.new('RGB', (SW, SH), INK); d = ImageDraw.Draw(sheet)
f = ImageFont.truetype(FB, 64); f2 = ImageFont.truetype(FR, 40)
for k, (lbl, sub, im) in enumerate((('א. זהב', 'כל הלוגו בזהב, ״פרימיום״ במרווח רחב', a), ('ב. קלאסי + תג', 'הלוגו המקורי, ותג זהב מתחת', b), ('ג. שחור וזהב', 'סמל זהב, טקסט לבן, קו זהב דק', c))):
    y = 60 + k * 680
    d.rounded_rectangle((60, y, SW - 60, y + 620), 36, fill=(0x1B, 0x20, 0x26))
    t = im.copy(); t.thumbnail((1150, 380)); sheet.paste(t, ((SW - t.width) // 2, y + 70), t)
    d.text((SW - 110, y + 480), lbl, font=f, fill=(0xF7, 0xE3, 0x9C), anchor='ra', direction='rtl')
    d.text((SW - 110, y + 555), sub, font=f2, fill=(0x8A, 0x92, 0x9B), anchor='ra', direction='rtl')
sheet.save(HERE + '/premium-options.png'); print('ok')
