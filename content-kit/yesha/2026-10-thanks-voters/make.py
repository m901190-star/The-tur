"""Yesha Council: thanks to the voters who chose to continue the settlement revolution (post 1080x1350 + story 1080x1920).
Number = Likud + Religious Zionism + Otzma Yehudit, near-final count (29.10.2026), stated as a safe lower bound."""
import os
SRC = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/carousel2/make.py'
code = open(SRC).read(); exec(code[:code.index('# 1 — cover')])     # brand helpers (W, S, M, colours, text, tw, arcs...)
from PIL import Image, ImageDraw
OUT = os.path.dirname(os.path.abspath(__file__))
WL = Image.open(OUT + '/../../clients/yesha/logo_white.png').convert('RGBA'); WL = WL.crop(WL.getchannel('A').getbbox())

def make(H, name, y0):
    img = Image.new('RGB', (W * S, H * S)); d = ImageDraw.Draw(img)
    for y in range(H * S):
        t = y / (H * S); d.line([(0, y), (W * S, y)], fill=tuple(int(NAVY[i] + (DEEP[i] - NAVY[i]) * t) for i in range(3)))
    arcs(img, 540, H + 380, alpha=40, n=5, r0=380, step=84, width=40)
    d = ImageDraw.Draw(img)
    lw = 230 * S; lg = WL.resize((lw, int(lw * WL.height / WL.width)), Image.LANCZOS); img.paste(lg, ((W * S - lw) // 2, (y0 - 20) * S), lg)
    c = W / 2; y = y0 + 300
    text(d, (c, y), 'תודה ליותר מ־', 96, SOFT, anchor='ma', bold=True); y += 85
    num = '1,750,000'
    text(d, (c + 8, y + 8), num, 250, BLUE, anchor='ma', bold=True, rtl=False)       # blue offset shadow, like the memorial names
    text(d, (c, y), num, 250, WHITE, anchor='ma', bold=True, rtl=False); y += 270
    text(d, (c, y), 'אזרחים שבחרו', 96, WHITE, anchor='ma'); y += 110
    tx = tw(d, 'בהמשך מהפכת ההתיישבות', 96); d.rectangle(P(c - tx / 2 - 30, y - 6, c + tx / 2 + 30, y + 112), fill=LB)
    text(d, (c, y), 'בהמשך מהפכת ההתיישבות', 96, DEEP, anchor='ma'); y += 190
    d.rectangle(P(c - 70, y, c + 70, y + 5), fill=LB); y += 50
    text(d, (c, y), 'שבת שלום', 110, WHITE, anchor='ma')
    text(d, (c, H - 70), 'לפי ספירת ועדת הבחירות, 29.10.2026 · הליכוד, הציונות הדתית ועוצמה יהודית', 30, SOFT, anchor='ma', bold=False)
    img.resize((W, H), Image.LANCZOS).save(OUT + f'/{name}.png')

make(1350, 'yesha-thanks-post', 110)
make(1920, 'yesha-thanks-story', 330)
print('ok')
