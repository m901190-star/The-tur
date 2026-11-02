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
def counter(d, n, total=7, dark=True, y=40):
    T(d, (50, y), f'{n}/{total}', RB, 26, SOFT if dark else GREY, anchor='la')
def save(img, n): img.convert('RGB').resize((W, H), Image.LANCZOS).save(OUT + f'/slide-{n}.png')

# ---- 1: the listing ----
def s1():
    img, d = canvas(ICE)
    for y in range(H * S):                                     # soft top band
        if y < 380 * S: d.line([(0, y), (W * S, y)], fill=tuple(int(NAVY[i] + (BLUE[i] - NAVY[i]) * y / (380 * S)) for i in range(3)))
    lw = 170; lg = WL.resize((lw * S, int(lw * S * WL.height / WL.width)), Image.LANCZOS); img.alpha_composite(lg, (int((W - 60 - lw) * S), 50 * S))
    counter(d, 1, y=230)
    T(d, (60, 130), 'מודעה חדשה', RB, 34, WHITE, anchor='la')
    T(d, (60, 176), 'לפני כ־3,800 שנה', RR, 28, SOFT, anchor='la')
    # card
    x0, y0, x1, y1 = 70, 290, W - 70, 1200
    sh = Image.new('RGBA', img.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle(P(x0 + 6, y0 + 16, x1 + 6, y1 + 16), 40 * S, fill=(14, 42, 71, 90))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(22 * S))); d = ImageDraw.Draw(img)
    d.rounded_rectangle(P(x0, y0, x1, y1), 40 * S, fill=WHITE)
    # "photo" area: illustrated hills + cave mouth
    ph = (x0 + 30, y0 + 30, x1 - 30, y0 + 400)
    pim = Image.new('RGBA', (int((ph[2] - ph[0]) * S), int((ph[3] - ph[1]) * S))); pd = ImageDraw.Draw(pim); pw, phh = pim.size
    for y in range(phh): pd.line([(0, y), (pw, y)], fill=(int(0xF6 - 30 * y / phh), int(0xD9 - 40 * y / phh), int(0xA0 - 30 * y / phh)))
    import math
    for k, col in enumerate([(0xC9, 0xA0, 0x6A), (0xA8, 0x7E, 0x4E), (0x86, 0x60, 0x3A)]):
        base = phh * (.55 + k * .14); pts = [(0, phh)] + [(x, base - 40 * S * (.6 * math.sin(x / (120 * S) + k) + .4 * math.sin(x / (53 * S) + k * 2))) for x in range(0, pw + 8, 8)] + [(pw, phh)]
        pd.polygon(pts, fill=col)
    pd.ellipse((pw * .56, phh * .66, pw * .76, phh * .98), fill=(0x3A, 0x26, 0x18)); pd.ellipse((pw * .62, phh * .70, pw * .82, phh * 1.02), fill=(0x2A, 0x1A, 0x10))
    m = Image.new('L', pim.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, pw - 1, phh - 1), 26 * S, fill=255)
    img.paste(pim, P(ph[0], ph[1]), m); d = ImageDraw.Draw(img)
    d.rounded_rectangle(P(ph[2] - 160, ph[1] + 20, ph[2] - 20, ph[1] + 66), 23 * S, fill=LB); T(d, (ph[2] - 90, ph[1] + 43), 'למכירה', RB, 26, WHITE, anchor='mm')
    y = ph[3] + 40; xr = x1 - 50
    T(d, (xr, y), 'שדה + מערה כפולה', RB, 54, INK); y += 80
    emoji(img, '📍', xr - 34, y + 2, 30); T(d, (xr - 46, y), 'חברון · ממרא', RR, 32, GREY); y += 62
    d.line(P(x0 + 50, y, x1 - 50, y), fill=(0xE1, 0xE8, 0xEE), width=2 * S); y += 30
    for k_, v_ in (('מצב', 'מעולה, כולל עצים'), ('מתאים ל', 'אחוזת קבר משפחתית'), ('בעלים', 'עפרון בן צחר')):
        T(d, (xr, y), k_, RR, 30, GREY); T(d, (x0 + 50, y), v_, RB, 30, INK, anchor='la'); y += 54
    y += 20
    T(d, (xr, y), 'מחיר', RR, 30, GREY); T(d, (x0 + 50, y - 12), '400 שקל כסף', RB, 52, BLUE, anchor='la')
    T(d, (W / 2 + 22, 1250), 'החליקו לשיחה', RB, 34, NAVY, anchor='ma')
    ax = W / 2 - TW(d, 'החליקו לשיחה', RB, 34) / 2 - 20; d.line(P(ax, 1271, ax - 36, 1271), fill=NAVY, width=5 * S); d.polygon(P(ax - 48, 1271, ax - 30, 1259, ax - 30, 1283), fill=NAVY)
    save(img, 1)

# ---- 2: the chat ----
CHAT = [('A', 'היי, ראיתי את המודעה על המערה. עוד רלוונטי?', '10:02'),
        ('E', 'אדוני, בשבילך? קח במתנה, באמת', '10:03', '😊'),
        ('A', 'תודה, אבל לא. אני רוצה לשלם מחיר מלא.', '10:03'),
        ('E', '״ארץ ארבע מאות שקל כסף, ביני ובינך מה הוא?״', '10:05', '😉'),
        ('A', 'סגור. שוקל לך עכשיו. רק שיהיה מול כולם, בשער העיר.', '10:06', '🤝'),
        ('E', 'למה מול כולם?', '10:06'),
        ('A', 'כדי שאף אחד לא יגיד בעוד 4,000 שנה שלקחתי בכוח.', '10:07')]
def chat(msgs, n, typing=False):
    img, d = canvas((0xDD, 0xE9, 0xF2))
    for k in range(0, W * S, 46 * S):                                   # faint chat wallpaper
        for j in range(0, H * S, 46 * S): d.ellipse((k + (j // (46 * S)) % 2 * 23 * S, j, k + (j // (46 * S)) % 2 * 23 * S + 4 * S, j + 4 * S), fill=(0xCF, 0xDE, 0xEA))
    d.rectangle(P(0, 0, W, 150), fill=NAVY)
    d.ellipse(P(W - 150, 35, W - 70, 115), fill=(0xC9, 0xA0, 0x6A)); emoji(img, '🌾', W - 132, 53, 44)
    T(d, (W - 175, 48), 'עפרון בן צחר', RB, 36, WHITE); T(d, (W - 175, 96), 'מחובר/ת עכשיו · שער חברון', RR, 24, SOFT)
    for k in range(3): d.ellipse(P(70, 52 + k * 20, 80, 62 + k * 20), fill=WHITE)
    d = ImageDraw.Draw(img)
    T(d, (W / 2, 180), 'היום', RR, 24, GREY, anchor='ma')
    counter(d, n, y=168)
    y = 240
    for msg in msgs:
        who, txt, tm = msg[:3]; em = msg[3] if len(msg) > 3 else None
        me = who == 'A'                                                   # Abraham = me (left in RTL chats)
        lines = wrap(d, txt, RR, 34, 640); bw = max(TW(d, l, RR, 34) for l in lines) + (52 if em else 0) + 50; bh = len(lines) * 48 + 64
        bw = max(bw, 200)
        x0 = 50 if me else W - 50 - bw; x1 = x0 + bw
        d.rounded_rectangle(P(x0, y, x1, y + bh), 28 * S, fill=(0xD2, 0xEA, 0xF7) if me else WHITE)
        for i, l in enumerate(lines): T(d, (x1 - 25, y + 18 + i * 48), l, RR, 34, INK)
        if em: emoji(img, em, x0 + 22, y + 18 + (len(lines) - 1) * 48, 36); d = ImageDraw.Draw(img)
        T(d, (x0 + 22 + (34 if me else 0), y + bh - 34), tm, RR, 20, GREY, anchor='la')
        if me:                                                            # read ticks
            for o in (0, 9): d.line(P(x0 + 22 + o, y + bh - 22, x0 + 27 + o, y + bh - 17), fill=MID, width=2 * S); d.line(P(x0 + 27 + o, y + bh - 17, x0 + 37 + o, y + bh - 29), fill=MID, width=2 * S)
        y += bh + 22
    if typing:
        d.rounded_rectangle(P(W - 190, y, W - 50, y + 70), 28 * S, fill=WHITE)
        for k in range(3): d.ellipse(P(W - 155 + k * 32, y + 27, W - 139 + k * 32, y + 43), fill=GREY)
    save(img, n)

# ---- 5: the receipt ----
def receipt():
    img, d = canvas(DEEP)
    for y in range(H * S): d.line([(0, y), (W * S, y)], fill=tuple(int(DEEP[i] + (NAVY[i] - DEEP[i]) * y / (H * S)) for i in range(3)))
    counter(d, 4, y=50)
    x0, y0, x1, y1 = 140, 210, W - 140, 1120
    d.rounded_rectangle(P(x0, y0, x1, y1), 44 * S, fill=WHITE)
    d.ellipse(P(W / 2 - 70, y0 + 60, W / 2 + 70, y0 + 200), fill=(0x2E, 0xB8, 0x6B))
    d.line(P(W / 2 - 34, y0 + 132, W / 2 - 8, y0 + 158), fill=WHITE, width=14 * S); d.line(P(W / 2 - 8, y0 + 158, W / 2 + 40, y0 + 104), fill=WHITE, width=14 * S)
    T(d, (W / 2, y0 + 240), 'העסקה הושלמה', RB, 52, INK, anchor='ma')
    T(d, (W / 2, y0 + 315), '400 שקל כסף', RB, 84, BLUE, anchor='ma')
    T(d, (W / 2, y0 + 425), '״עובר לסוחר״', RR, 32, GREY, anchor='ma')
    y = y0 + 500; d.line(P(x0 + 50, y, x1 - 50, y), fill=(0xE1, 0xE8, 0xEE), width=2 * S); y += 34
    for k_, v_ in (('מ־', 'אברהם העברי'), ('אל', 'עפרון החתי'), ('נכס', 'השדה והמערה אשר בו'), ('עדים', 'כל באי שער עירו')):
        T(d, (x1 - 50, y), k_, RR, 30, GREY); T(d, (x0 + 50, y), v_, RB, 30, INK, anchor='la'); y += 58
    T(d, (W / 2, y1 - 70), 'בראשית כ״ג, ט״ז–י״ח', RR, 26, GREY, anchor='ma')
    T(d, (W / 2, 1200), 'קבלה. בתוקף מאז.', RB, 44, WHITE, anchor='ma')
    save(img, 4)


def dark(n):
    img, d = canvas(DEEP)
    for y in range(H * S): d.line([(0, y), (W * S, y)], fill=tuple(int(DEEP[i] + (NAVY[i] - DEEP[i]) * y / (H * S)) for i in range(3)))
    counter(d, n, y=50); return img, ImageDraw.Draw(img)
def para(d, s, font, size, y, col, width=860, lh=1.35):
    for l in wrap(d, s, font, size, width): T(d, (W / 2, y), l, font, size, col, anchor='ma'); y += size * lh
    return y
def s5():
    img, d = dark(5)
    T(d, (W / 2, 260), 'למה אברהם', KB, 120, SOFT, anchor='ma'); T(d, (W / 2, 390), 'התעקש לשלם?', KB, 150, WHITE, anchor='ma')
    d.rectangle(P(W / 2 - 80, 600, W / 2 + 80, 606), fill=LB)
    y = para(d, 'לפי המדרש, יש שלושה מקומות בארץ ישראל שאי אפשר לומר עליהם ״גזולים הם בידכם״:', RR, 40, 660, SOFT)
    y += 30
    for k, p in enumerate(('מערת המכפלה', 'הר הבית', 'קבר יוסף')):
        d.rounded_rectangle(P(240, y, W - 240, y + 86), 43 * S, fill=BLUE); T(d, (W / 2, y + 43), p, RB, 40, WHITE, anchor='mm'); y += 106
    T(d, (W / 2, 1250), 'בראשית רבה ע״ט, ז׳', RR, 26, SOFT, anchor='ma'); save(img, 5)
def s6():
    img, d = dark(6)
    d.rounded_rectangle(P(70, 120, W - 70, 780), 36 * S, fill=(0x1E, 0x45, 0x6E), outline=LB, width=3 * S)
    T(d, (W / 2, 430), 'כאן: תמונה אמיתית מחברון', RB, 44, SOFT, anchor='mm'); T(d, (W / 2, 490), '(משבת חיי שרה, מהמועצה)', RR, 30, SOFT, anchor='mm')
    T(d, (W / 2, 850), '3,800 שנה עברו.', KB, 130, WHITE, anchor='ma')
    tx = TW(d, 'הקבלה עדיין אצלנו.', KB, 130); d.rectangle(P(W / 2 - tx / 2 - 30, 1010, W / 2 + tx / 2 + 30, 1150), fill=LB)
    T(d, (W / 2, 1000), 'הקבלה עדיין אצלנו.', KB, 130, DEEP, anchor='ma'); save(img, 6)
def s7():
    img, d = dark(7)
    lw = 300; lg = WL.resize((lw * S, int(lw * S * WL.height / WL.width)), Image.LANCZOS); img.alpha_composite(lg, (int((W - lw) / 2 * S), 200 * S)); d = ImageDraw.Draw(img)
    T(d, (W / 2, 620), 'שבת חיי שרה', KB, 150, WHITE, anchor='ma'); T(d, (W / 2, 790), 'בחברון', KB, 150, LB, anchor='ma')
    T(d, (W / 2, 1000), 'מחכים לכם', RB, 56, SOFT, anchor='ma'); save(img, 7)

s1()
chat(CHAT[:4], 2)
chat(CHAT[4:] + [('A', 'שלחתי 400 שקל כסף. תאשר קבלה', '10:08')], 3, typing=True)
receipt(); s5(); s6(); s7(); print('ok')


