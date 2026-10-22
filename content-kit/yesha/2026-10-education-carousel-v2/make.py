"""Yesha Council – education achievements carousel (9 slides, 1080x1350)."""
import os
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.dirname(os.path.abspath(__file__))
FONTS = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/pro-video-editing/assets/fonts/'
LOGO = '/root/.claude/uploads/1a5819ee-0cc0-5045-b086-4a8a80216453/6f71e693-image.png'  # original, untouched

S = 2                      # supersampling factor
W, H = 1080, 1350
M = 80                     # side margin
TOTAL = 8
NAVY = (0x17, 0x40, 0x68); BLUE = (0x25, 0x66, 0xA2); MID = (0x25, 0x87, 0xBE)
LB = (0x27, 0xA4, 0xD1); ICE = (0xE8, 0xF2, 0xF8); WHITE = (255, 255, 255)
DEEP = (0x0E, 0x2A, 0x47); TRACK = (0xD3, 0xE4, 0xF0); SOFT = (0xB8, 0xD4, 0xE8)

SRC_EDU = 'מקור: משרד החינוך, תמונה חינוכית רשותית תשפ״ה'
SRC_SERVICE = 'מקור: משרד החינוך, תמונה חינוכית רשותית תשפ״ה · נתוני שירות: תשפ״ב'


def F(size, bold=True):
    return ImageFont.truetype(FONTS + ('Karantina-Bold.ttf' if bold else 'Karantina-Regular.ttf'), int(size * S))


def P(*v):
    return [int(x * S) for x in v]


def text(d, xy, s, size, fill, anchor='ra', bold=True, rtl=True, shadow=None):
    kw = dict(font=F(size, bold), anchor=anchor, direction='rtl' if rtl else 'ltr')
    if shadow:
        d.text((int((xy[0] + shadow[0]) * S), int((xy[1] + shadow[1]) * S)), s, fill=shadow[2], **kw)
    d.text((int(xy[0] * S), int(xy[1] * S)), s, fill=fill, **kw)


def tw(d, s, size, bold=True, rtl=True):
    return d.textlength(s, font=F(size, bold), direction='rtl' if rtl else 'ltr') / S


def canvas(dark):
    if not dark:
        img = Image.new('RGB', (W * S, H * S), ICE)
        ImageDraw.Draw(img).rectangle(P(0, 0, W, 12), fill=NAVY)
        return img
    img = Image.new('RGB', (W * S, H * S)); d = ImageDraw.Draw(img)
    for y in range(H * S):
        t = y / (H * S)
        d.line([(0, y), (W * S, y)], fill=tuple(int(DEEP[i] + (BLUE[i] - DEEP[i]) * t) for i in range(3)))
    return img


def arcs(img, cx, cy, alpha=38, n=3, r0=400, step=74, width=36):
    """Curved stripes echoing the logo's arcs."""
    ov = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for i in range(n):
        r = r0 + i * step
        d.arc(P(cx - r, cy - r, cx + r, cy + r), start=200, end=340, fill=LB + (alpha,), width=width * S)
    img.paste(ov, (0, 0), ov)


def logo(img, w, x_right, y, plate):
    """Original logo, aspect ratio kept. On dark slides it sits on a white plate."""
    lg = Image.open(LOGO).convert('RGBA')
    if plate:  # dark slide: same artwork, recoloured white (shape and proportions untouched)
        a = lg.getchannel('A').point(lambda v: 0 if v < 40 else v)  # drop faint edge specks
        lg = Image.new('RGBA', lg.size, WHITE + (0,)); lg.putalpha(a)
    lg = lg.crop(lg.getchannel('A').getbbox())
    h = w * lg.height / lg.width
    lg = lg.resize((int(w * S), int(h * S)), Image.LANCZOS)
    x = x_right - w
    img.paste(lg, (int(x * S), int(y * S)), lg)
    return h


def chrome(img, n, dark, source=None, on_photo=False):
    d = ImageDraw.Draw(img)
    logo(img, 150 if (dark or on_photo) else 170, W - M, 62, plate=dark or on_photo)
    text(d, (M, 72), f'{n}/{TOTAL}', 36, WHITE if on_photo else (LB if dark else MID), anchor='la', rtl=False)
    if source:
        d.rectangle(P(M, H - 104, W - M, H - 102), fill=(0x4A, 0x6E, 0x94) if dark else (0xC9, 0xDB, 0xE8))
        text(d, (W - M, H - 84), source, 30, SOFT if dark else BLUE, bold=False)
    return d


UP = '/root/.claude/uploads/1a5819ee-0cc0-5045-b086-4a8a80216453/'
PHOTO_COVER = UP + '9dadb569-image.jpg'
PHOTO_EFRAT = UP + '6168c27e-image.jpg'
PHOTO_SHOMRON = UP + '76ebff00-image.jpg'


def bg_at(y):
    """Colour of the dark slide gradient at height y, so photos fade into it seamlessly."""
    t = y / H
    return tuple(int(DEEP[i] + (BLUE[i] - DEEP[i]) * t) for i in range(3))


def photo(img, path, h, focus_y, fade_to, fade_from=0.55, caption=None, top_dark=150):
    """Cover-crop a photo into the top band (W x h) and fade its bottom into the slide colour."""
    ph = Image.open(path).convert('RGB')
    sc = max(W * S / ph.width, h * S / ph.height)
    ph = ph.resize((round(ph.width * sc), round(ph.height * sc)), Image.LANCZOS)
    top = int(min(max(focus_y * ph.height - h * S / 2, 0), ph.height - h * S))
    left = (ph.width - W * S) // 2
    ph = ph.crop((left, top, left + W * S, top + int(h * S)))
    img.paste(ph, (0, 0))
    ov = Image.new('RGBA', (W * S, int(h * S)), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    for y in range(int(h * S)):
        t = y / (h * S)
        a_top = int(top_dark * max(0, 1 - t / (130 / h)))                       # keeps logo/counter legible
        a_bot = int(255 * max(0, (t - fade_from) / (1 - fade_from)) ** 1.1)
        col = bg_at(y / S) if fade_to is None else fade_to
        if a_top: od.line([(0, y), (W * S, y)], fill=DEEP + (a_top,))
        if a_bot: od.line([(0, y), (W * S, y)], fill=col + (a_bot,))
    img.paste(ov, (0, 0), ov)
    if caption:
        d = ImageDraw.Draw(img)
        w = tw(d, caption, 34)
        y = h * fade_from - 20
        d.rounded_rectangle(P(W - M - w - 36, y, W - M, y + 54), radius=27 * S, fill=NAVY)
        text(d, (W - M - 18, y + 9), caption, 34, WHITE)


def tag(d, y, s, size=42, bg=BLUE):
    padx, pady = 22, 10
    w = tw(d, s, size)
    d.rectangle(P(W - M - w - 2 * padx, y, W - M, y + size * 1.05 + 2 * pady), fill=bg)
    text(d, (W - M - padx, y + pady - 2), s, size, WHITE)
    return size * 1.05 + 2 * pady


def pill(d, x_right, y, s, size=36, bg=NAVY, fg=WHITE):
    w = tw(d, s, size)
    d.rounded_rectangle(P(x_right - w - 40, y, x_right, y + size + 22), radius=(size + 22) / 2 * S, fill=bg)
    text(d, (x_right - 20, y + 9), s, size, fg)
    return w + 40


def bar_row(d, y, name, pct, rank, dark=False, strong=False):
    """Name + rank pill (right), percentage (left), bar on a fixed 0–100% scale."""
    fg = WHITE if dark else NAVY
    text(d, (W - M, y), name, 72, fg)
    pill(d, W - M - tw(d, name, 72) - 24, y + 16, f'מקום {rank} בארץ', 36,
         bg=LB if dark else NAVY)
    text(d, (M, y + 2), f'{pct:.1f}%', 72, LB if dark else NAVY, anchor='la', rtl=False)
    by = y + 104; full = W - 2 * M
    d.rounded_rectangle(P(M, by, W - M, by + 26), radius=13 * S, fill=(0x2E, 0x55, 0x80) if dark else TRACK)
    fill_w = full * pct / 100.0                                # proportional, zero-based
    d.rounded_rectangle(P(W - M - fill_w, by, W - M, by + 26), radius=13 * S,
                        fill=LB if (dark or not strong) else BLUE)


def check(d, cx, cy, r, bg=LB):
    d.ellipse(P(cx - r, cy - r, cx + r, cy + r), fill=bg)
    d.line(P(cx - r * 0.45, cy + r * 0.02, cx - r * 0.1, cy + r * 0.38, cx + r * 0.48, cy - r * 0.35),
           fill=WHITE, width=int(r * 0.26 * S), joint='curve')


def save(img, n):
    img.resize((W, H), Image.LANCZOS).save(os.path.join(OUT, f'{n:02d}.png'))


# 1 — cover
def s1():
    img = canvas(True)
    photo(img, PHOTO_COVER, 740, 0.45, None, fade_from=0.40, top_dark=200)
    arcs(img, 980, 1420, alpha=34, n=4, r0=400, step=80, width=40)
    d = ImageDraw.Draw(img)
    logo(img, 220, W - M, 60, plate=True)
    text(d, (M, 72), f'1/{TOTAL}', 36, WHITE, anchor='la', rtl=False)
    tag(d, 612, 'התמונה החינוכית תשפ״ה', 42, bg=BLUE)
    # campaign-style headline: name on top, the claim in one line on a solid blue block,
    # with a light-blue stroke under the key word
    text(d, (W - M, 688), 'יהודה ושומרון', 220, WHITE, shadow=(8, 8, DEEP))
    line, key = 'מובילה בחינוך', 'בחינוך'
    padx = 34
    size = 205
    while tw(d, line, size) > W - 2 * M - 2 * padx:
        size -= 2
    lw = tw(d, line, size)
    bx1 = W - M; bx0 = bx1 - lw - 2 * padx
    by0 = 905; by1 = by0 + size * 1.0 + 26
    d.rectangle(P(bx0, by0, bx1, by1), fill=NAVY)
    d.rectangle(P(bx1 - 12, by0, bx1, by1), fill=LB)
    text(d, (bx1 - padx, by0 + 4), line, size, WHITE)
    # the key word is the leftmost part of the RTL line
    kx0 = bx1 - padx - lw; kx1 = kx0 + tw(d, key, size)
    sy = by1 - 34
    d.polygon(P(kx1 + 6, sy, kx0 - 4, sy + 4, kx0 - 10, sy + 22, kx1 + 2, sy + 18), fill=LB)
    text(d, (W - M, H - 112), 'החליקו לנתונים ←', 46, SOFT, bold=False)
    save(img, 1)


# 2 — matriculation eligibility
def s2():
    img = canvas(True); arcs(img, 120, 1320, n=3, r0=380)
    d = chrome(img, 2, True, SRC_EDU)
    tag(d, 270, 'זכאות לבגרות', 44)
    text(d, (W / 2, 590), '100%', 330, WHITE, anchor='mm', rtl=False, shadow=(10, 10, BLUE))
    text(d, (W / 2, 820), 'זכאות לבגרות באלקנה', 84, LB, anchor='mm')
    d.rounded_rectangle(P(170, 920, W - 170, 1040), radius=24 * S, fill=WHITE)
    text(d, (W / 2, 980), 'מקום ראשון בארץ — במשותף', 64, NAVY, anchor='mm')
    text(d, (W / 2, 1110), 'בקרב תלמידי י״ב במוסדות המגישים לבגרות ברשות.', 36, SOFT, anchor='mm', bold=False)
    save(img, 2)


# 3 — excellent matriculation
def s3():
    img = canvas(False); d = chrome(img, 3, False, SRC_EDU)
    tag(d, 250, 'בגרות מצטיינת', 42)
    text(d, (W - M, 335), 'המצטיינים של הארץ', 104, NAVY)
    text(d, (W - M, 465), 'שיעור הזכאים לבגרות מצטיינת מקרב התלמידים', 46, BLUE, bold=False)
    for i, (nm, pct, rk) in enumerate([('גוש עציון', 36.7, 6), ('אלקנה', 26.9, 16), ('אפרת', 26.3, 19)]):
        bar_row(d, 600 + i * 205, nm, pct, rk, strong=(i == 0))
    save(img, 3)


# 4 — 5 units math & English
def s4():
    img = canvas(False); d = chrome(img, 4, False, SRC_EDU)
    tag(d, 250, '5 יחידות לימוד', 42)
    text(d, (W - M, 335), 'מובילים ב־5 יחידות', 104, NAVY)

    def section(y, title):
        text(d, (W - M, y), title, 60, BLUE)
        d.rectangle(P(M, y + 40, W - M - tw(d, title, 60) - 24, y + 43), fill=(0xB5, 0xCF, 0xE3))

    section(480, 'מתמטיקה')
    bar_row(d, 570, 'אלקנה', 35.8, 6, strong=True)
    bar_row(d, 750, 'אפרת', 32.5, 12)
    section(950, 'אנגלית')
    bar_row(d, 1040, 'אלקנה', 82.1, 8, strong=True)
    save(img, 4)


# 5 — technological education (two separate cards, no shared chart)
def s5():
    img = canvas(False); d = chrome(img, 5, False, SRC_EDU)
    tag(d, 250, 'בגרות־טק וחינוך טכנולוגי', 42)
    text(d, (W - M, 335), 'הישגים בחינוך הטכנולוגי', 96, NAVY)

    def card(y, h, name, big, label, sub, rank_tag, note):
        d.rounded_rectangle(P(M, y, W - M, y + h), radius=28 * S, fill=WHITE)
        d.rounded_rectangle(P(W - M - 14, y, W - M, y + h), radius=7 * S, fill=LB)
        x = W - M - 50
        text(d, (x, y + 24), name, 72, NAVY)
        text(d, (x, y + 100), big, 104, LB, rtl=False)
        text(d, (x - tw(d, big, 104, rtl=False) - 22, y + 136), label, 52, NAVY)
        yy = y + 226
        if sub:
            text(d, (x, yy), sub, 44, BLUE, bold=False); yy += 62
        pill(d, x, yy, rank_tag, 36); yy += 76
        for line in note or []:
            text(d, (x, yy), line, 36, MID, bold=False); yy += 46

    card(445, 400, 'אלקנה', '24.4%', 'זכאות לבגרות־טק', None, 'מקום 12 בארץ בזכאות לבגרות־טק',
         ['בגרות הכוללת 5 יחידות במתמטיקה, באנגלית', 'ובפיזיקה או במדעי המחשב.'])
    card(862, 370, 'אורנית', '91.4%', 'זכאות לבגרות', 'בקרב הלומדים במגמות טכנולוגיות',
         'מקום 15 בארץ בזכאות לבגרות במגמות טכנולוגיות', None)
    save(img, 5)


# 6 — exam integrity (no ranking)
def s6():
    img = canvas(True); arcs(img, 980, 1320, n=3, r0=400)
    d = chrome(img, 6, True, SRC_EDU)
    tag(d, 250, 'טוהר הבחינות', 42, bg=LB)
    text(d, (W - M, 335), 'אפס מחברות', 120, WHITE, shadow=(6, 6, BLUE))
    text(d, (W - M, 470), 'בגרות פסולות', 120, LB, shadow=(6, 6, DEEP))
    names = ['קריית ארבע', 'אורנית', 'עמנואל', 'מעלה אפרים', 'ערבות הירדן']
    y = 660
    for nm in names:
        d.rounded_rectangle(P(M, y, W - M, y + 82), radius=18 * S, fill=WHITE)
        check(d, W - M - 50, y + 41, 24)
        text(d, (W - M - 96, y + 14), nm, 56, NAVY)
        y += 100
    save(img, 6)


# 7 — IDF enlistment, men (2022 cohort data)
def s7():
    img = canvas(False); d = chrome(img, 6, False, SRC_SERVICE)
    tag(d, 250, 'גיוס לצה״ל · בנים', 42)
    text(d, (W - M, 335), 'בחזית השירות', 104, NAVY)
    text(d, (W - M, 465), 'שיעור הגיוס לצה״ל — בנים | נתוני תשפ״ב', 46, BLUE, bold=False)
    for i, (nm, pct, rk) in enumerate([('אריאל', 98.7, 2), ('אלקנה', 95.8, 9), ('אפרת', 94.2, 17)]):
        bar_row(d, 600 + i * 205, nm, pct, rk, strong=(i == 0))
    save(img, 6)


# 8 — national service, women (2022 cohort data)
def s8():
    img = canvas(True); arcs(img, 120, 1340, n=3, r0=400)
    photo(img, PHOTO_SHOMRON, 430, 0.0, None, fade_from=0.62, caption='שומרון', top_dark=180)
    d = chrome(img, 7, True, SRC_SERVICE, on_photo=True)
    tag(d, 425, 'שירות לאומי · בנות', 40, bg=LB)
    text(d, (W - M, 490), 'שלושת המקומות הראשונים בארץ', 84, WHITE)
    text(d, (W - M, 592), 'שירות לאומי / אזרחי — נשים | נתוני תשפ״ב', 40, SOFT, bold=False)
    rows = [('שומרון', 88.7, 1), ('בית אל', 87.6, 2), ('קריית ארבע', 85.1, 3)]
    for i, (nm, pct, rk) in enumerate(rows):
        y = 670 + i * 112
        text(d, (W - M, y + 8), f'מקום {rk}', 40, LB)
        text(d, (W - M - 130, y - 4), nm, 56, WHITE)
        text(d, (M, y - 2), f'{pct:.1f}%', 56, WHITE, anchor='la', rtl=False)
        by = y + 66; full = W - 2 * M
        d.rounded_rectangle(P(M, by, W - M, by + 18), radius=9 * S, fill=(0x2E, 0x55, 0x80))
        d.rounded_rectangle(P(W - M - full * pct / 100, by, W - M, by + 18), radius=9 * S, fill=LB)
    # also in the top 20
    y = 1015
    d.rounded_rectangle(P(M, y, W - M, y + 205), radius=22 * S, fill=(0x1E, 0x4A, 0x75))
    text(d, (W - M - 30, y + 18), 'גם בין 20 המובילות:', 40, LB)
    others = [('ערבות הירדן', 74.5, 6), ('קדומים', 73.3, 7), ('מטה בנימין', 63.8, 15)]
    colw = (W - 2 * M - 60) / 3
    for i, (nm, pct, rk) in enumerate(others):
        xr = W - M - 30 - i * colw
        text(d, (xr, y + 76), nm, 46, WHITE)
        text(d, (xr, y + 136), f'{pct:.1f}% | מקום {rk}', 40, SOFT, bold=False)
    save(img, 7)


# 9 — closing
def s9():
    img = canvas(True); arcs(img, 540, 1520, alpha=50, n=4, r0=440, step=80, width=40)
    d = ImageDraw.Draw(img)
    text(d, (M, 72), f'8/{TOTAL}', 36, LB, anchor='la', rtl=False)
    text(d, (W / 2, 290), 'גאווה בחינוך.', 140, WHITE, anchor='mm')
    text(d, (W / 2, 440), 'גאווה בדור הבא.', 140, LB, anchor='mm', shadow=(7, 7, DEEP))
    for i, line in enumerate(['תודה לתלמידות ולתלמידים,', 'לצוותי החינוך ולרשויות המקומיות', 'על ההשקעה, ההתמדה וההישגים.']):
        text(d, (W / 2, 600 + i * 70), line, 54, SOFT, anchor='mm', bold=False)
    lw = 320
    logo(img, lw, (W + lw) / 2, 900, plate=True)
    save(img, 8)


for f in (s1, s2, s3, s4, s5, s7, s8, s9):
    f()
sheet = Image.new('RGB', (372 * 4, 462 * 2), WHITE)
for k in range(8):
    sheet.paste(Image.open(os.path.join(OUT, f'{k + 1:02d}.png')).resize((360, 450)), ((k % 4) * 372, (k // 4) * 462))
sheet.save(os.path.join(OUT, 'sheet.png'))
print('done')
