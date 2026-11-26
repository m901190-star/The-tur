"""Yesha Council – education achievements carousel (8 slides, 1080x1350)."""
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

SRC_EDU = 'מקור: משרד החינוך, התמונה החינוכית הרשותית · תשפ״ה (2025)'
SRC_SERVICE = 'מקור: משרד החינוך, התמונה החינוכית הרשותית · נתוני שירות: תשפ״ב'


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
PHOTO_ELKANA = UP + '177480c4-image.jpg'
PHOTO_ARMY = UP + 'ac7bf51a-image.jpg'
PHOTO_EXCEL = UP + '08871fa1-image.jpg'
PHOTO_TECH = UP + 'd29592b6-image.jpg'


def bg_at(y):
    """Colour of the dark slide gradient at height y, so photos fade into it seamlessly."""
    t = y / H
    return tuple(int(DEEP[i] + (BLUE[i] - DEEP[i]) * t) for i in range(3))


def photo(img, path, h, focus_y, fade_to, fade_from=0.55, caption=None, top_dark=150, caption_top=False):
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
        if caption_top:   # top-left, over the sky, so no one in the photo is covered
            x1, y = M + w + 36, 125
        else:
            x1, y = W - M, h * fade_from - 20
        d.rounded_rectangle(P(x1 - w - 36, y, x1, y + 54), radius=27 * S, fill=NAVY)
        text(d, (x1 - 18, y + 9), caption, 34, WHITE)


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


def bar_row(d, y, name, pct, rank_label, dark=False, strong=False, k=1.0):
    """Name + rank pill (right), percentage (left), bar on a fixed 0–100% scale. k scales the row."""
    fg = WHITE if dark else NAVY
    text(d, (W - M, y), name, 72 * k, fg)
    pill(d, W - M - tw(d, name, 72 * k) - 24, y + 16 * k, rank_label, 36 * k,
         bg=LB if dark else NAVY)
    text(d, (M, y + 2), f'{pct:.1f}%', 72 * k, LB if dark else NAVY, anchor='la', rtl=False)
    by = y + 104 * k; full = W - 2 * M; bh = 26 * k
    d.rounded_rectangle(P(M, by, W - M, by + bh), radius=bh / 2 * S, fill=(0x2E, 0x55, 0x80) if dark else TRACK)
    fill_w = full * pct / 100.0                                # proportional, zero-based
    d.rounded_rectangle(P(W - M - fill_w, by, W - M, by + bh), radius=bh / 2 * S,
                        fill=LB if (dark or not strong) else BLUE)


def check(d, cx, cy, r, bg=LB):
    d.ellipse(P(cx - r, cy - r, cx + r, cy + r), fill=bg)
    d.line(P(cx - r * 0.45, cy + r * 0.02, cx - r * 0.1, cy + r * 0.38, cx + r * 0.48, cy - r * 0.35),
           fill=WHITE, width=int(r * 0.26 * S), joint='curve')


def save(img, n):
    img.resize((W, H), Image.LANCZOS).save(os.path.join(OUT, f'{n:02d}.png'))


def wrap(d, s, size, width, bold=False):
    words, lines, cur = s.split(), [], ''
    for w_ in words:
        t = (cur + ' ' + w_).strip()
        if tw(d, t, size, bold) <= width or not cur:
            cur = t
        else:
            lines.append(cur); cur = w_
    return lines + [cur]


def headline_block(d, line, key, y, max_size=205):
    """One-line claim on a navy block, light-blue stroke under the key word (key = first word of the line)."""
    padx = 34; size = max_size
    while tw(d, line, size) > W - 2 * M - 2 * padx - 12:
        size -= 2
    lw = tw(d, line, size)
    bx1 = W - M; bx0 = bx1 - lw - 2 * padx - 12
    by1 = y + size * 1.0 + 26
    d.rectangle(P(bx0, y, bx1, by1), fill=NAVY)
    d.rectangle(P(bx1 - 12, y, bx1, by1), fill=LB)
    text(d, (bx1 - 12 - padx, y + 4), line, size, WHITE)
    kx1 = bx1 - 12 - padx; kx0 = kx1 - tw(d, key, size)      # key word is the rightmost (first) word
    sy = by1 - 34 * size / 205
    d.polygon(P(kx1 + 6, sy, kx0 - 4, sy + 4, kx0 - 10, sy + 20, kx1 + 2, sy + 16), fill=LB)


# 1 — cover
def s1():
    img = canvas(True)
    photo(img, PHOTO_COVER, 740, 0.45, None, fade_from=0.40, top_dark=200)
    arcs(img, 980, 1420, alpha=34, n=4, r0=400, step=80, width=40)
    d = ImageDraw.Draw(img)
    logo(img, 220, W - M, 60, plate=True)
    text(d, (M, 72), f'1/{TOTAL}', 36, WHITE, anchor='la', rtl=False)
    tag(d, 612, 'התמונה החינוכית תשפ״ה (2025)', 42, bg=BLUE)
    text(d, (W - M, 688), 'יהודה ושומרון', 220, WHITE, shadow=(8, 8, DEEP))
    headline_block(d, 'בצמרת החינוך בישראל', 'בצמרת', 905)
    text(d, (W - M, H - 112), 'החליקו לנתונים ←', 46, SOFT, bold=False)
    save(img, 1)


# 2 — matriculation eligibility
GOLD = (0xF2, 0xC1, 0x4E); GOLD_D = (0xC9, 0x95, 0x2B)


def medal(d, cx, cy, r):
    """First-place medal: ribbon + gold disc with '1'."""
    d.polygon(P(cx - r * 0.75, cy - r * 2.0, cx - r * 0.15, cy - r * 2.0, cx + r * 0.25, cy - r * 0.6, cx - r * 0.35, cy - r * 0.6), fill=BLUE)
    d.polygon(P(cx + r * 0.75, cy - r * 2.0, cx + r * 0.15, cy - r * 2.0, cx - r * 0.25, cy - r * 0.6, cx + r * 0.35, cy - r * 0.6), fill=LB)
    d.ellipse(P(cx - r, cy - r, cx + r, cy + r), fill=GOLD_D)
    d.ellipse(P(cx - r * 0.84, cy - r * 0.84, cx + r * 0.84, cy + r * 0.84), fill=GOLD)
    text(d, (cx, cy + r * 0.06), '1', r * 1.25, NAVY, anchor='mm', rtl=False)


def s2():
    img = canvas(True)
    photo(img, PHOTO_ELKANA, 700, 0.5, None, fade_from=0.84, caption='אלקנה', top_dark=170, caption_top=True)
    arcs(img, 120, 1400, n=3, r0=380)
    d = chrome(img, 2, True, SRC_EDU, on_photo=True)
    tag(d, 662, 'זכאות לבגרות באלקנה', 40)
    # headline: first place in the country (tied), as large as the width allows next to the medal
    line1, line2 = 'מקום ראשון', 'בארץ'
    text(d, (W - M, 722), line1, 200, WHITE, shadow=(8, 8, BLUE))
    text(d, (W - M, 905), line2, 200, LB, shadow=(8, 8, DEEP))
    medal(d, M + 120, 1000, 100)
    text(d, (W - M, 1112), '100% זכאות לבגרות — במשותף עם רשויות נוספות', 44, WHITE)
    text(d, (W - M, 1172), 'בקרב תלמידי י״ב במוסדות המגישים לבגרות ברשות.', 32, SOFT, bold=False)
    save(img, 2)


# 3 — excellent matriculation
def s3():
    img = canvas(False)
    photo(img, PHOTO_EXCEL, 625, 0.52, ICE, fade_from=0.92, top_dark=120)
    d = chrome(img, 3, False, SRC_EDU, on_photo=True)
    tag(d, 640, 'בגרות מצטיינת', 38)
    text(d, (W - M, 698), 'המצטיינים של הארץ', 84, NAVY)
    text(d, (W - M, 798), 'שיעור הזכאים לבגרות מצטיינת מקרב התלמידים', 40, BLUE, bold=False)
    rows = [('גוש עציון', 36.7, 'מקום 6 ברשימה הארצית'), ('אלקנה', 26.9, 'מקום 16'), ('אפרת', 26.3, 'מקום 19')]
    for i, (nm, pct, rk) in enumerate(rows):
        bar_row(d, 875 + i * 118, nm, pct, rk, strong=(i == 0), k=0.78)
    save(img, 3)


# 4 — 5 units math & English
def s4():
    img = canvas(False)
    photo(img, PHOTO_EFRAT, 600, 0.0, ICE, fade_from=0.82, caption='אפרת', top_dark=170)
    d = chrome(img, 4, False, SRC_EDU, on_photo=True)
    tag(d, 585, '5 יחידות לימוד', 38)
    text(d, (W - M, 642), 'מובילים ב־5 יחידות', 80, NAVY)
    text(d, (W - M, 732), 'שיעור הזכאות ב־5 יחידות מקרב התלמידים', 34, BLUE, bold=False)

    def section(y, title):
        text(d, (W - M, y), title, 46, BLUE)
        d.rectangle(P(M, y + 30, W - M - tw(d, title, 46) - 24, y + 33), fill=(0xB5, 0xCF, 0xE3))

    section(790, 'מתמטיקה')
    bar_row(d, 842, 'אלקנה', 35.8, 'מקום 6', strong=True, k=0.78)
    bar_row(d, 958, 'אפרת', 32.5, 'מקום 12', k=0.78)
    section(1080, 'אנגלית')
    bar_row(d, 1130, 'אלקנה', 82.1, 'מקום 8', strong=True, k=0.78)
    save(img, 4)


# 5 — technological education (two separate metrics, no shared chart)
def s5():
    img = canvas(False)
    photo(img, PHOTO_TECH, 665, 0.0, ICE, fade_from=0.9, top_dark=150)
    d = chrome(img, 5, False, SRC_EDU, on_photo=True)
    tag(d, 672, 'בגרות־טק וחינוך טכנולוגי', 38)
    text(d, (W - M, 726), 'הישגים בחינוך הטכנולוגי', 72, NAVY)

    # two separate metrics side by side: never one shared chart
    gap = 24; cw = (W - 2 * M - gap) / 2; y0, h = 815, 410

    def card(x_right, name, big, metric, sub, rank_tag, note):
        d.rounded_rectangle(P(x_right - cw, y0, x_right, y0 + h), radius=24 * S, fill=WHITE)
        d.rounded_rectangle(P(x_right - 12, y0, x_right, y0 + h), radius=6 * S, fill=LB)
        x = x_right - 36; inner = cw - 60
        text(d, (x, y0 + 18), name, 58, NAVY)
        text(d, (x, y0 + 82), big, 92, LB, rtl=False)
        text(d, (x, y0 + 186), metric, 40, NAVY)
        yy = y0 + 240
        for ln in wrap(d, sub, 32, inner) if sub else []:
            text(d, (x, yy), ln, 32, NAVY, bold=False); yy += 40
        pill(d, x, yy + 6, rank_tag, 32); yy += 74
        for ln in wrap(d, note, 30, inner) if note else []:
            text(d, (x, yy), ln, 30, BLUE, bold=False); yy += 38

    card(W - M, 'אלקנה', '24.4%', 'זכאות לבגרות־טק', None, 'מקום 12',
         'הגדרה: זכאות לבגרות הכוללת היבחנות ב־5 יחידות במתמטיקה, באנגלית ובפיזיקה או במדעי המחשב.')
    card(W - M - cw - gap, 'אורנית', '91.4%', 'זכאות לבגרות', 'בקרב הלומדים במגמות טכנולוגיות',
         'מקום 15 במדד זה', None)
    save(img, 5)


def year_badge(d, x_right, y, dark):
    """Prominent 'service data year' marker."""
    return pill(d, x_right, y, 'נתוני תשפ״ב', 42, bg=LB if dark else BLUE)


# 6 — IDF enlistment, men (2022 cohort data)
def s6():
    img = canvas(False)
    photo(img, PHOTO_ARMY, 625, 0.0, ICE, fade_from=0.90, top_dark=175)
    d = chrome(img, 6, False, SRC_SERVICE, on_photo=True)
    tag(d, 640, 'גיוס לצה״ל · בנים', 38)
    text(d, (W - M, 698), 'בחזית השירות', 84, NAVY)
    sub = 'שיעור הגיוס לצה״ל — בנים'
    text(d, (W - M, 798), sub, 42, BLUE, bold=False)
    year_badge(d, W - M - tw(d, sub, 42, False) - 24, 792, False)
    rows = [('אריאל', 98.7, 'מקום 2'), ('אלקנה', 95.8, 'מקום 9'), ('אפרת', 94.2, 'מקום 17')]
    for i, (nm, pct, rk) in enumerate(rows):
        bar_row(d, 875 + i * 118, nm, pct, rk, strong=(i == 0), k=0.78)
    save(img, 6)


# 7 — national service, women (2022 cohort data)
def s7():
    img = canvas(True); arcs(img, 120, 1340, n=3, r0=400)
    photo(img, PHOTO_SHOMRON, 560, 0.0, None, fade_from=0.80, caption='שומרון', top_dark=180)
    d = chrome(img, 7, True, SRC_SERVICE, on_photo=True)
    tag(d, 548, 'שירות לאומי · בנות', 38, bg=LB)
    text(d, (W - M, 606), 'שלושת המקומות הראשונים בארץ', 76, WHITE)
    sub = 'שירות לאומי / אזרחי — נשים'
    text(d, (W - M, 696), sub, 40, SOFT, bold=False)
    year_badge(d, W - M - tw(d, sub, 40, False) - 24, 690, True)
    rows = [('שומרון', 88.7, 1), ('בית אל', 87.6, 2), ('קריית ארבע', 85.1, 3)]
    for i, (nm, pct, rk) in enumerate(rows):
        y = 768 + i * 88
        text(d, (W - M, y + 6), f'מקום {rk}', 36, LB)
        text(d, (W - M - 118, y - 4), nm, 48, WHITE)
        text(d, (M, y - 2), f'{pct:.1f}%', 48, WHITE, anchor='la', rtl=False)
        by = y + 56; full = W - 2 * M
        d.rounded_rectangle(P(M, by, W - M, by + 18), radius=9 * S, fill=(0x2E, 0x55, 0x80))
        d.rounded_rectangle(P(W - M - full * pct / 100, by, W - M, by + 18), radius=9 * S, fill=LB)
    y = 1042
    d.rounded_rectangle(P(M, y, W - M, y + 182), radius=22 * S, fill=(0x1E, 0x4A, 0x75))
    text(d, (W - M - 30, y + 14), 'גם בין 20 המובילות:', 38, LB)
    others = [('בקעת הירדן', 74.5, 6), ('קדומים', 73.3, 7), ('מטה בנימין', 63.8, 15)]
    colw = (W - 2 * M - 60) / 3
    for i, (nm, pct, rk) in enumerate(others):
        xr = W - M - 30 - i * colw
        text(d, (xr, y + 66), nm, 44, WHITE)
        text(d, (xr, y + 122), f'{pct:.1f}% | מקום {rk}', 38, SOFT, bold=False)
    save(img, 7)


# 8 — closing
def s8():
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


for f in (s1, s2, s3, s4, s5, s6, s7, s8):
    f()
sheet = Image.new('RGB', (372 * 4, 462 * 2), WHITE)
for k in range(8):
    sheet.paste(Image.open(os.path.join(OUT, f'{k + 1:02d}.png')).resize((360, 450)), ((k % 4) * 372, (k // 4) * 462))
sheet.save(os.path.join(OUT, 'sheet.png'))
print('done')
