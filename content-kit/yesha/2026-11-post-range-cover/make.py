"""Yesha humorous post: action-game 'box cover' collage of women's range training (inspired by the GTA6 trend, no IP used). 1080x1350."""
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); A = HERE + '/art/'
HAIM = os.path.abspath(os.path.join(HERE, '..', '..', 'fonts', 'HaimClassicv2FM-Bold.ttf'))
LOGO = os.path.abspath(os.path.join(HERE, '..', '..', 'clients', 'yesha', 'logo_white.png'))
W, H = 1080, 1350; G = 12  # gutter
NAVY, BLUE, LB = (23, 64, 104), (37, 102, 162), (39, 164, 209)
TITLE = sys.argv[1] if len(sys.argv) > 1 else 'השומרות'
SUB = sys.argv[2] if len(sys.argv) > 2 else 'מהדורת המטווח'
def F(s): return ImageFont.truetype(HAIM, s, layout_engine=ImageFont.Layout.RAQM)

im = Image.new('RGB', (W, H), (12, 12, 16))
# panel layout (x0,y0,x1,y1): big hero right, stack left, wide strip bottom
P = {
    1: (W // 2 + G // 2, G, W - G, 860),            # hero (floral headscarf, low angle)
    2: (G, G, W // 2 - G // 2, 300),                # red scarf smile
    3: (G, 300 + G, W // 2 - G // 2, 580),          # focused young woman
    4: (G, 580 + G, W // 2 - G // 2, 860),          # pink scarf + bucket hat
    5: (G, 860 + G, W - G, H - G),                  # line of shooters
}
FOC = {1: (.5, .3), 2: (.6, .3), 3: (.4, .35), 4: (.55, .35), 5: (.5, .45)}
for k, (x0, y0, x1, y1) in P.items():
    p = A + f'{k}.png'
    if not os.path.exists(p): continue
    tile = ImageOps.fit(Image.open(p).convert('RGB'), (x1 - x0, y1 - y0), Image.LANCZOS, centering=FOC[k])
    im.paste(tile, (x0, y0))

d = ImageDraw.Draw(im, 'RGBA')
# bottom title block over the wide strip
grad = Image.new('L', (1, 420))
for y in range(420): grad.putpixel((0, y), int(235 * (y / 420) ** 1.3))
im.paste(Image.new('RGB', (W, 420), (10, 10, 14)), (0, H - 420), grad.resize((W, 420)))
d = ImageDraw.Draw(im, 'RGBA')
ft = F(190); t = TITLE
tw = d.textlength(t, font=ft, direction='rtl')
if tw > W - 80: ft = F(int(190 * (W - 80) / tw)); tw = d.textlength(t, font=ft, direction='rtl')
ty = H - 300
d.text((W / 2 + tw / 2 + 8, ty + 8), t, font=ft, fill=(0, 0, 0, 200), anchor='ra', direction='rtl')
d.text((W / 2 + tw / 2, ty), t, font=ft, fill='white', anchor='ra', direction='rtl', stroke_width=6, stroke_fill='black')
fs = F(58); sw = d.textlength(SUB, font=fs, direction='rtl')
bx0, by0 = W / 2 - sw / 2 - 26, ty - 70
bb = d.textbbox((0, 0), SUB, font=fs, anchor='ls', direction='rtl'); ih = bb[3] - bb[1]
d.rectangle((bx0, by0, W / 2 + sw / 2 + 26, by0 + ih + 30), fill=LB)
d.text((W / 2 + sw / 2, by0 + 15 - bb[1]), SUB, font=fs, fill='white', anchor='rs', direction='rtl')
# corner joke tags
def tag(x, y, lines, anchor_right=True, size=30, bg=(255, 255, 255), fg=(0, 0, 0)):
    f = F(size); lw = max(d.textlength(l, font=f, direction='rtl') for l in lines); lh = size + 6
    x0 = x - lw - 24 if anchor_right else x; d.rectangle((x0, y, x0 + lw + 24, y + lh * len(lines) + 14), fill=bg, outline='black', width=3)
    for i, l in enumerate(lines): d.text((x0 + lw + 12, y + 8 + i * lh), l, font=f, fill=fg, anchor='ra', direction='rtl')
tag(W - 30, H - 82, ['זמין עכשיו', 'ביהודה ושומרון'], size=28, bg=LB, fg=(255, 255, 255))
d.rectangle((30, H - 132, 130, H - 30), fill='white', outline='black', width=4)
d.text((80, H - 118), '18', font=F(56), fill='black', anchor='ma')
d.text((80, H - 62), '+', font=F(26), fill='black', anchor='ma')
# Yesha logo top-left of hero area, AI tag
if os.path.exists(LOGO):
    lg = Image.open(LOGO).convert('RGBA'); lg = lg.resize((170, int(170 * lg.height / lg.width)), Image.LANCZOS)
    sh = Image.new('RGBA', lg.size, (0, 0, 0, 0)); sh.putalpha(lg.getchannel('A').point(lambda v: v * .6)); sh = sh.filter(ImageFilter.GaussianBlur(6))
    im.paste((0, 0, 0), (W - 200 + 3, 34 + 3), sh); im.paste(lg, (W - 200, 34), lg)
d.text((W - 24, 845), 'נוצר ב-AI', font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 22, layout_engine=ImageFont.Layout.RAQM), fill=(255, 255, 255, 220), anchor='rs', direction='rtl')
out = HERE + '/post.jpg'; im.save(out, quality=94); print(out)
