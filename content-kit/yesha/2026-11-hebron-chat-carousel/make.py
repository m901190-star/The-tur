"""Yesha Council carousel sample: 'a cave for sale in Hebron' — Abraham & Ephron (Gen 23) as a chat. 1080x1350."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
OUT = os.path.dirname(os.path.abspath(__file__))
FD = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/'
KB = FD + 'pro-video-editing/assets/fonts/Karantina-Bold.ttf'; KR = KB.replace('Bold', 'Regular')
RR, RB = FD + 'fonts/Rubik-400.ttf', FD + 'fonts/Rubik-700.ttf'
EMO = '/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'
S = 2; W, H = 1080, 1350
NAVY = (0x17, 0x40, 0x68); BLUE = (0x25, 0x66, 0xA2); MID = (0x25, 0x87, 0xBE); LB = (0x27, 0xA4, 0xD1); ICE = (0xE8, 0xF2, 0xF8)
DEEP = (0x0E, 0x2A, 0x47); WHITE = (255, 255, 255); INK = (0x1B, 0x2B, 0x3A); GREY = (0x6B, 0x7C, 0x8C); SOFT = (0xB8, 0xD4, 0xE8)
WL = Image.open(OUT + '/../../clients/yesha/logo_white.png').convert('RGBA'); WL = WL.crop(WL.getchannel('A').getbbox())
LG = Image.open(OUT + '/../../clients/yesha/logo.png').convert('RGBA'); LG = LG.crop(LG.getchannel('A').getbbox())
_f = {}
def F(path, size):
    k = (path, int(size * S))
    if k not in _f: _f[k] = ImageFont.truetype(path, int(size * S))
    return _f[k]
def P(*v): return tuple(int(x * S) for x in v)
def T(d, xy, s, font, size, fill, anchor='ra'): d.text(P(*xy), s, font=F(font, size), fill=fill, anchor=anchor, direction='rtl')
def TW(d, s, font, size): return d.textlength(s, font=F(font, size), direction='rtl') / S
def emoji(img, ch, x, y, size):
    f = ImageFont.truetype(EMO, 109); e = Image.new('RGBA', (150, 150), (0, 0, 0, 0))
    ImageDraw.Draw(e).text((10, 10), ch, font=f, embedded_color=True); e = e.crop(e.getchannel('A').getbbox()).resize((int(size * S), int(size * S)), Image.LANCZOS)
    img.alpha_composite(e, (int(x * S), int(y * S)))
def wrap(d, s, font, size, width):
    out, cur = [], ''
    for w in s.split():
        t = (cur + ' ' + w).strip()
        if TW(d, t, font, size) > width and cur: out.append(cur); cur = w
        else: cur = t
    return out + [cur]
def canvas(bg):
    img = Image.new('RGBA', (W * S, H * S), bg + (255,)); return img, ImageDraw.Draw(img)
def counter(d, n, total=6, dark=True, y=40):
    T(d, (50, y), f'{n}/{total}', RB, 26, SOFT if dark else GREY, anchor='la')
def save(img, n): img.convert('RGB').resize((W, H), Image.LANCZOS).save(OUT + f'/slide-{n}.png')


import math
PHOTO = OUT + '/hebron.jpg'           # the Chayei Sarah photo from the client; slides 1 and 5 use it when present
HAVE = os.path.exists(PHOTO)
def cover(im, w, h, fy=.5):
    s_ = max(w / im.width, h / im.height); im = im.resize((int(im.width * s_) + 1, int(im.height * s_) + 1), Image.LANCZOS)
    y0 = int((im.height - h) * fy); x0 = (im.width - w) // 2; return im.crop((x0, y0, x0 + w, y0 + h))
def illustration(pw, phh):
    pim = Image.new('RGBA', (pw, phh)); pd = ImageDraw.Draw(pim)
    for y in range(phh): pd.line([(0, y), (pw, y)], fill=(int(0xF6 - 30 * y / phh), int(0xD9 - 40 * y / phh), int(0xA0 - 30 * y / phh)))
    for k, col in enumerate([(0xC9, 0xA0, 0x6A), (0xA8, 0x7E, 0x4E), (0x86, 0x60, 0x3A)]):
        base = phh * (.55 + k * .14); pts = [(0, phh)] + [(x, base - 40 * S * (.6 * math.sin(x / (120 * S) + k) + .4 * math.sin(x / (53 * S) + k * 2))) for x in range(0, pw + 8, 8)] + [(pw, phh)]
        pd.polygon(pts, fill=col)
    pd.ellipse((pw * .56, phh * .66, pw * .76, phh * .98), fill=(0x3A, 0x26, 0x18)); pd.ellipse((pw * .62, phh * .70, pw * .82, phh * 1.02), fill=(0x2A, 0x1A, 0x10))
    return pim

# ---- 1: the listing, in the look of an Israeli classifieds site (orange/white; no site name or logo) ----
ORANGE = (0xFF, 0x71, 0x00); LINE = (0xE6, 0xE6, 0xE6); TXT = (0x36, 0x36, 0x36); SUB = (0x8A, 0x8A, 0x8A)
def s1():
    img, d = canvas((0xF2, 0xF2, 0xF2))
    d.rectangle(P(0, 0, W, 170), fill=ORANGE)
    lw = 150; lg = WL.resize((lw * S, int(lw * S * WL.height / WL.width)), Image.LANCZOS); img.alpha_composite(lg, (int((W - 50 - lw) * S), 30 * S)); d = ImageDraw.Draw(img)
    d.rounded_rectangle(P(50, 52, 640, 118), 33 * S, fill=WHITE); T(d, (610, 85), 'נדל״ן · מכירה · חברון', RR, 28, SUB, anchor='rm')
    d.ellipse(P(72, 67, 104, 99), outline=SUB, width=3 * S); d.line(P(100, 95, 112, 107), fill=SUB, width=4 * S)
    counter(d, 1, y=195, dark=False)
    x0, y0, x1, y1 = 50, 250, W - 50, 1200
    d.rounded_rectangle(P(x0, y0, x1, y1), 24 * S, fill=WHITE, outline=LINE, width=2 * S)
    ph = (x0, y0, x1, y0 + 520); pw, phh = int((ph[2] - ph[0]) * S), int((ph[3] - ph[1]) * S)
    pim = cover(Image.open(OUT + '/cave.jpg').convert('RGB'), pw, phh, fy=.45).convert('RGBA')
    m = Image.new('L', (pw, phh), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, pw - 1, phh + 40 * S), 24 * S, fill=255)
    img.paste(pim, P(ph[0], ph[1]), m); d = ImageDraw.Draw(img)
    d.rounded_rectangle(P(x1 - 230, y0 + 24, x1 - 24, y0 + 74), 8 * S, fill=ORANGE); T(d, (x1 - 127, y0 + 49), 'מודעה חדשה', RB, 26, WHITE, anchor='mm')
    for k in range(5): d.ellipse(P(W / 2 - 52 + k * 24, ph[3] - 30, W / 2 - 40 + k * 24, ph[3] - 18), fill=WHITE if k == 0 else (255, 255, 255, 150))
    y = ph[3] + 36; xr = x1 - 44
    T(d, (x0 + 44, y - 6), '400 שקל', RB, 60, TXT, anchor='la')
    T(d, (xr, y), 'שדה + מערה כפולה', RB, 46, TXT); y += 66
    T(d, (xr, y), 'חברון', RR, 32, SUB); y += 70
    d.line(P(x0 + 44, y, x1 - 44, y), fill=LINE, width=2 * S); y += 34
    cw = (x1 - x0 - 88) / 3
    for k, (a, b) in enumerate((('מצב', 'חדש'), ('כולל', 'שדה ועצים'), ('בעלים', 'עפרון בן צחר'))):
        cx = xr - cw * k - cw / 2; T(d, (cx, y), b, RB, 34, TXT, anchor='ma'); T(d, (cx, y + 52), a, RR, 26, SUB, anchor='ma')
    y += 130
    d.rounded_rectangle(P(x0 + 44, y, x1 - 44, y + 90), 12 * S, fill=ORANGE); T(d, (W / 2, y + 45), 'הצגת מספר טלפון', RB, 36, WHITE, anchor='mm')
    T(d, (W / 2 + 22, 1250), 'החליקו לשיחה', RB, 34, TXT, anchor='ma')
    ax = W / 2 - TW(d, 'החליקו לשיחה', RB, 34) / 2 - 20; d.line(P(ax, 1271, ax - 36, 1271), fill=TXT, width=5 * S); d.polygon(P(ax - 48, 1271, ax - 30, 1259, ax - 30, 1283), fill=TXT)
    save(img, 1)

# ---- 2-3: the chat, in WhatsApp colours (no app name or logo) ----
WA_HEAD = (0x00, 0x80, 0x69); WA_BG = (0xEF, 0xEA, 0xE2); WA_OUT = (0xD9, 0xFD, 0xD3); WA_TICK = (0x53, 0xBD, 0xEB); WA_DOT = (0xE4, 0xDC, 0xD0)
CHAT = [('A', 'היי, ראיתי את המודעה על המערה. עוד רלוונטי?', '10:02'),
        ('E', 'אדוני, בשבילך? קח במתנה, באמת', '10:03', '😊'),
        ('A', 'תודה, אבל לא. אני רוצה לשלם מחיר מלא.', '10:03'),
        ('E', '400 שקל, ביני ובינך מה הוא?', '10:05', '😉'),
        ('A', 'סגור. משלם לך עכשיו. רק שיהיה מול כולם, בשער העיר.', '10:06', '🤝'),
        ('E', 'למה מול כולם?', '10:06'),
        ('A', 'כדי שאף אחד לא יגיד בעוד 4,000 שנה שלקחתי בכוח.', '10:07')]
def chat(msgs, n, typing=False):
    img, d = canvas(WA_BG)
    for k in range(0, W * S, 40 * S):
        for j in range(0, H * S, 40 * S): o = (j // (40 * S)) % 2 * 20 * S; d.ellipse((k + o, j, k + o + 5 * S, j + 5 * S), fill=WA_DOT)
    d.rectangle(P(0, 0, W, 150), fill=WA_HEAD)
    d.ellipse(P(W - 150, 35, W - 70, 115), fill=(0xC9, 0xA0, 0x6A)); emoji(img, '🌾', W - 132, 53, 44); d = ImageDraw.Draw(img)
    T(d, (W - 175, 48), 'עפרון בן צחר', RB, 36, WHITE); T(d, (W - 175, 96), 'מחובר/ת · חברון', RR, 24, (0xD7, 0xF0, 0xEA))
    for k in range(3): d.ellipse(P(70, 52 + k * 20, 80, 62 + k * 20), fill=WHITE)
    d.rounded_rectangle(P(W / 2 - 50, 172, W / 2 + 50, 212), 12 * S, fill=WHITE); T(d, (W / 2, 192), 'היום', RR, 24, SUB, anchor='mm')
    counter(d, n, y=178, dark=False)
    y = 250
    for msg in msgs:
        who, txt, tm = msg[:3]; em = msg[3] if len(msg) > 3 else None
        me = who == 'A'
        lines = wrap(d, txt, RR, 36, 640); bw = max(max(TW(d, l, RR, 36) for l in lines) + (54 if em else 0) + 50, 210); bh = len(lines) * 50 + 66
        x0 = 50 if me else W - 50 - bw; x1 = x0 + bw
        d.rounded_rectangle(P(x0, y, x1, y + bh), 18 * S, fill=WA_OUT if me else WHITE)
        for i, l in enumerate(lines): T(d, (x1 - 25, y + 18 + i * 50), l, RR, 36, (0x11, 0x1B, 0x21))
        if em: emoji(img, em, x0 + 22, y + 18 + (len(lines) - 1) * 50, 38); d = ImageDraw.Draw(img)
        T(d, (x0 + 22 + (36 if me else 0), y + bh - 34), tm, RR, 20, (0x66, 0x77, 0x81), anchor='la')
        if me:
            for o in (0, 9): d.line(P(x0 + 22 + o, y + bh - 22, x0 + 27 + o, y + bh - 17), fill=WA_TICK, width=2 * S); d.line(P(x0 + 27 + o, y + bh - 17, x0 + 37 + o, y + bh - 29), fill=WA_TICK, width=2 * S)
        y += bh + 24
    if typing:
        d.rounded_rectangle(P(W - 190, y, W - 50, y + 70), 18 * S, fill=WHITE)
        for k in range(3): d.ellipse(P(W - 155 + k * 32, y + 27, W - 139 + k * 32, y + 43), fill=SUB)
    save(img, n)

# ---- 4: the transfer, in the colours of a payment app (no app name or logo) ----
BIT1 = (0x00, 0x9F, 0xD4); BIT2 = (0x00, 0xC2, 0xB5)
def receipt():
    img, d = canvas(BIT1)
    for y in range(H * S):
        t = y / (H * S); d.line([(0, y), (W * S, y)], fill=tuple(int(BIT1[i] + (BIT2[i] - BIT1[i]) * t) for i in range(3)))
    counter(d, 4, y=50)
    T(d, (W / 2, 150), 'ההעברה בוצעה', RB, 64, WHITE, anchor='ma')
    d.ellipse(P(W / 2 - 80, 270, W / 2 + 80, 430), fill=WHITE)
    d.line(P(W / 2 - 38, 352, W / 2 - 8, 382), fill=BIT1, width=16 * S); d.line(P(W / 2 - 8, 382, W / 2 + 44, 320), fill=BIT1, width=16 * S)
    T(d, (W / 2, 470), '400 שקל', RB, 130, WHITE, anchor='ma')
    T(d, (W / 2, 640), 'הועברו לעפרון בן צחר', RR, 40, WHITE, anchor='ma')
    x0, y0, x1, y1 = 90, 760, W - 90, 1150
    d.rounded_rectangle(P(x0, y0, x1, y1), 30 * S, fill=WHITE)
    y = y0 + 40
    for k_, v_ in (('מאת', 'אברהם'), ('עבור', 'השדה והמערה אשר בו'), ('עדים', 'כל באי שער עירו'), ('אסמכתא', 'בראשית כ״ג, ט״ז')):
        T(d, (x1 - 44, y), k_, RR, 32, SUB); T(d, (x0 + 44, y), v_, RB, 32, TXT, anchor='la'); y += 82
        if y < y1 - 60: d.line(P(x0 + 44, y - 22, x1 - 44, y - 22), fill=LINE, width=2 * S)
    T(d, (W / 2, 1210), 'קבלה. בתוקף מאז.', RB, 46, WHITE, anchor='ma')
    save(img, 4)

def dark(n):
    img, d = canvas(DEEP)
    for y in range(H * S): d.line([(0, y), (W * S, y)], fill=tuple(int(DEEP[i] + (NAVY[i] - DEEP[i]) * y / (H * S)) for i in range(3)))
    counter(d, n, y=50); return img, ImageDraw.Draw(img)
def s5():
    img, d = dark(5)
    if HAVE:
        ph = cover(Image.open(PHOTO).convert('RGB'), W * S, 820 * S).convert('RGBA')
        fade = Image.new('L', ph.size, 255); fd = ImageDraw.Draw(fade)
        for y in range(ph.height): fd.line([(0, y), (ph.width, y)], fill=int(255 * min(1, (ph.height - y) / (260 * S))))
        img.paste(ph, (0, 0), fade); d = ImageDraw.Draw(img); d.rounded_rectangle(P(36, 40, 112, 82), 21 * S, fill=(14, 42, 71, 200)); counter(d, 5, y=48)
        T(d, (W - 30, 770), 'צילום: מחדשי היישוב היהודי בחברון', RR, 20, SOFT, anchor='ra')
    else:
        d.rounded_rectangle(P(70, 120, W - 70, 780), 36 * S, fill=(0x1E, 0x45, 0x6E), outline=LB, width=3 * S)
        T(d, (W / 2, 450), 'כאן: התמונה מחיי שרה', RB, 44, SOFT, anchor='mm')
    T(d, (W / 2, 850), '3,800 שנה עברו.', KB, 130, WHITE, anchor='ma')
    tx = TW(d, 'הקבלה עדיין אצלנו.', KB, 130); d.rectangle(P(W / 2 - tx / 2 - 30, 1010, W / 2 + tx / 2 + 30, 1150), fill=LB)
    T(d, (W / 2, 1000), 'הקבלה עדיין אצלנו.', KB, 130, DEEP, anchor='ma'); save(img, 5)
def s6():
    img, d = canvas(DEEP)
    bg = cover(Image.open(OUT + '/machpela-night.jpg').convert('RGB'), W * S, H * S, fy=.15).convert('RGBA')
    img.alpha_composite(bg)
    sh = Image.new('RGBA', img.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
    for y in range(H * S):                                   # dark at the top for the text, warm-dark at the bottom for the Shabbat card
        t = y / (H * S); a = int(235 * max(0, 1 - t / .42) ** 1.2 + 230 * max(0, (t - .55) / .45) ** 1.3)
        sd.line([(0, y), (W * S, y)], fill=DEEP + (min(235, a),))
    img.alpha_composite(sh); d = ImageDraw.Draw(img)
    lw = 190; lg = WL.resize((lw * S, int(lw * S * WL.height / WL.width)), Image.LANCZOS); img.alpha_composite(lg, (int((W - lw) / 2 * S), 60 * S)); d = ImageDraw.Draw(img)
    counter(d, 6, y=50)
    for tx_, y_, col in (('השבת, חיי שרה', 250, WHITE), ('כולנו בעיר האבות', 400, LB)):
        T(d, (W / 2 + 5, y_ + 5), tx_, KB, 140, DEEP, anchor='ma'); T(d, (W / 2, y_), tx_, KB, 140, col, anchor='ma')
    # Shabbat table card
    cw, ch = 760, 330; cx0, cy0 = (W - cw) / 2, 860
    card = cover(Image.open(OUT + '/shabbat.jpg').convert('RGB'), int(cw * S), int(ch * S), fy=.05).convert('RGBA')
    m = Image.new('L', card.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, card.width - 1, card.height - 1), 30 * S, fill=255)
    shadow = Image.new('RGBA', img.size, (0, 0, 0, 0)); ImageDraw.Draw(shadow).rounded_rectangle(P(cx0 + 8, cy0 + 18, cx0 + cw + 8, cy0 + ch + 18), 30 * S, fill=(0, 0, 0, 140))
    img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(20 * S)))
    d = ImageDraw.Draw(img); d.rounded_rectangle(P(cx0 - 6, cy0 - 6, cx0 + cw + 6, cy0 + ch + 6), 34 * S, fill=WHITE)
    img.paste(card, P(cx0, cy0), m); d = ImageDraw.Draw(img)
    tw_ = TW(d, 'מחכים לכם', RB, 60); sw = d.textlength(':)', font=F(RB, 60)) / S; x = W / 2 + (tw_ + 16 + sw) / 2
    T(d, (x, 1225), 'מחכים לכם', RB, 60, WHITE, anchor='ra')
    d.text(P(x - tw_ - 16 - sw, 1225), ':)', font=F(RB, 60), fill=WHITE, anchor='la'); save(img, 6)

for f in os.listdir(OUT):
    if f.startswith('slide-'): os.remove(OUT + '/' + f)
s1()
chat(CHAT[:4], 2)
chat(CHAT[4:] + [('A', 'שלחתי 400 שקל. תאשר קבלה', '10:08')], 3, typing=True)
receipt(); s5(); s6()
sheet = Image.new('RGB', (3 * 442 + 10, 2 * 550 + 10), (240, 240, 240))
for k in range(6):
    im = Image.open(OUT + f'/slide-{k + 1}.png').resize((432, 540)); sheet.paste(im, (10 + (2 - k % 3) * 442, 10 + (k // 3) * 550))
sheet.save(OUT + '/all-slides.jpg', quality=90); print('ok')
