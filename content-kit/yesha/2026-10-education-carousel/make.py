import math, sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
OUT = os.path.dirname(os.path.abspath(__file__))
FONTS = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/pro-video-editing/assets/fonts/'
LOGO = '/home/user/The-tur/content-kit/clients/yesha/'
S = 2                      # supersample
W, H = 1080, 1350
NAVY=(0x17,0x40,0x68); BLUE=(0x25,0x66,0xA2); MID=(0x25,0x87,0xBE); LB=(0x27,0xA4,0xD1); ICE=(0xE8,0xF2,0xF8); WHITE=(255,255,255)
DEEP=(0x0E,0x2A,0x47)
TOTAL = 9
def F(size, bold=True): return ImageFont.truetype(FONTS+('Karantina-Bold.ttf' if bold else 'Karantina-Regular.ttf'), int(size*S))
def P(*v): return [int(x*S) for x in v]

def gradient(c1, c2, angle_down=True):
    g = Image.new('RGB', (W*S, H*S)); d = ImageDraw.Draw(g)
    for y in range(H*S):
        t = y/(H*S); d.line([(0,y),(W*S,y)], fill=tuple(int(c1[i]+(c2[i]-c1[i])*t) for i in range(3)))
    return g

def arcs(img, cx, cy, color, alpha=40, n=3, r0=380, step=70, width=34):
    """Decorative concentric arcs echoing the logo's curved stripes."""
    ov = Image.new('RGBA', img.size, (0,0,0,0)); d = ImageDraw.Draw(ov)
    for i in range(n):
        r = r0 + i*step
        d.arc(P(cx-r, cy-r, cx+r, cy+r), start=200, end=340, fill=color+(alpha,), width=width*S)
    img.paste(ov, (0,0), ov)

def logo(img, white, w, x, y):
    lg = Image.open(LOGO + ('logo_white.png' if white else 'logo.png')).convert('RGBA')
    lg = lg.resize((int(w*S), int(w*S*lg.height/lg.width)), Image.LANCZOS)
    img.paste(lg, (int(x*S), int(y*S)), lg)
    return lg.height/S

def text(d, xy, s, size, fill, anchor='ra', bold=True, rtl=True, shadow=None, stroke=0, stroke_fill=None):
    f = F(size, bold)
    kw = dict(font=f, anchor=anchor, direction='rtl' if rtl else 'ltr')
    if shadow:
        d.text((int((xy[0]+shadow[0])*S), int((xy[1]+shadow[1])*S)), s, fill=shadow[2], **kw)
    d.text((int(xy[0]*S), int(xy[1]*S)), s, fill=fill, stroke_width=int(stroke*S), stroke_fill=stroke_fill, **kw)

def tw(d, s, size, bold=True, rtl=True):
    return d.textlength(s, font=F(size,bold), direction='rtl' if rtl else 'ltr')/S

def chrome(img, d, n, dark):
    """Shared frame: logo top-right, slide counter top-left, source line at bottom."""
    fg = WHITE if dark else NAVY
    logo(img, dark, 150, W-60-150, 52)
    text(d, (60, 70), f'{n}/{TOTAL}', 34, LB if dark else MID, anchor='la', rtl=False)
    d.rectangle(P(60, H-92, W-60, H-90), fill=(255,255,255) if dark else (0xC9,0xDB,0xE8))
    text(d, (W-60, H-72), 'מקור: משרד החינוך, תמונה חינוכית רשותית תשפ"ה', 26, (0xB8,0xD4,0xE8) if dark else BLUE, bold=False)

def label(d, x_right, y, s, size=40, bg=BLUE, fg=WHITE, padx=22, pady=10):
    w = tw(d, s, size); h = size*1.05
    d.rectangle(P(x_right-w-2*padx, y, x_right, y+h+2*pady), fill=bg)
    text(d, (x_right-padx, y+pady-2), s, size, fg)
    return h+2*pady

def rank_badge(d, cx, cy, rank, r=62, bg=LB, fg=WHITE, small='מקום'):
    d.ellipse(P(cx-r, cy-r, cx+r, cy+r), fill=bg)
    text(d, (cx, cy-r*0.45), small, r*0.44, fg, anchor='mm', bold=False)
    text(d, (cx, cy+r*0.18), str(rank), r*0.95, fg, anchor='mm', rtl=False)

def save(img, name):
    img = img.resize((W, H), Image.LANCZOS)
    img.save(os.path.join(OUT, name), quality=95)
    print('saved', name)

# ---------- 1. Cover ----------
def cover():
    img = gradient(DEEP, BLUE); arcs(img, 980, 1250, LB, alpha=55, n=4, r0=420, step=78, width=40)
    d = ImageDraw.Draw(img)
    logo(img, True, 240, W-80-240, 80)
    y = 430
    h = label(d, W-80, y, 'תשפ"ה · הנתונים הרשמיים', 42, bg=LB)
    text(d, (W-80, y+h+30), 'יהודה ושומרון', 190, WHITE, shadow=(8, 8, BLUE))
    text(d, (W-80, y+h+240), 'בצמרת', 190, LB, shadow=(8, 8, NAVY))
    text(d, (W-80, y+h+450), 'החינוך בישראל', 120, WHITE)
    text(d, (W-80, H-150), 'החליקו לנתונים ←', 46, (0xB8,0xD4,0xE8), bold=False)
    save(img, '01.png')

# ---------- 2. 100% Elkana ----------
def bagrut():
    img = gradient(NAVY, DEEP); arcs(img, 120, 1300, LB, alpha=35, n=3, r0=360)
    d = ImageDraw.Draw(img); chrome(img, d, 2, True)
    label(d, W-60, 250, 'זכאות לבגרות', 44)
    text(d, (W/2, 560), '100%', 330, WHITE, anchor='mm', rtl=False, shadow=(10, 10, BLUE))
    text(d, (W/2, 790), 'מתלמידי אלקנה זכאים לבגרות', 74, LB, anchor='mm')
    # rank strip
    d.rounded_rectangle(P(150, 900, W-150, 1060), radius=24*S, fill=(255,255,255))
    text(d, (W/2, 945), 'מקום 4 בארץ', 70, NAVY, anchor='mm')
    text(d, (W/2, 1015), 'מכל הרשויות המקומיות בישראל', 40, BLUE, anchor='mm', bold=False)
    save(img, '02.png')

# ---------- generic bar slide (light) ----------
def bars(n, tag, title, sub, rows, unit_max, name):
    img = Image.new('RGB', (W*S, H*S), ICE); d = ImageDraw.Draw(img)
    d.rectangle(P(0, 0, W, 14), fill=NAVY)
    chrome(img, d, n, False)
    label(d, W-60, 230, tag, 44)
    text(d, (W-60, 320), title, 100, NAVY, shadow=(5, 5, (0xC9,0xDB,0xE8)))
    text(d, (W-60, 440), sub, 44, BLUE, bold=False)
    y = 560; rowh = (H-92-60-y)/len(rows)
    for (place, rank, pct, note) in rows:
        cy = y + rowh/2
        rank_badge(d, W-60-58, cy, rank, r=58)
        text(d, (W-60-140, cy-50), place, 64, NAVY)
        if note: text(d, (W-60-140-tw(d, place, 64)-18, cy-40), note, 42, MID, bold=False)
        # bar from right to left
        x0 = W-60-140; maxw = x0-60-170
        bw = maxw*pct/unit_max
        d.rounded_rectangle(P(x0-maxw, cy+28, x0, cy+52), radius=12*S, fill=(0xD3,0xE4,0xF0))
        d.rounded_rectangle(P(x0-bw, cy+28, x0, cy+52), radius=12*S, fill=LB if rank>3 else BLUE)
        text(d, (60, cy+40), f'{pct:.1f}%'.replace('.0%','%'), 64, NAVY, anchor='lm', rtl=False)
        y += rowh
    save(img, name)

# ---------- 5. Zero disqualified exams ----------
def integrity():
    img = gradient(NAVY, DEEP); arcs(img, 980, 1300, LB, alpha=35, n=3, r0=380)
    d = ImageDraw.Draw(img); chrome(img, d, 5, True)
    label(d, W-60, 230, 'טוהר הבחינות', 44)
    text(d, (W-60, 315), '0', 300, LB, rtl=False, shadow=(8, 8, BLUE))
    text(d, (W-60-150, 360), 'מחברות', 110, WHITE)
    text(d, (W-60-150, 470), 'בגרות פסולות', 110, WHITE)
    text(d, (W-60, 610), '5 רשויות ביהודה ושומרון ב-20 המקומות הראשונים בארץ', 42, (0xB8,0xD4,0xE8), bold=False)
    names = ['קרית ארבע', 'אורנית', 'עמנואל', 'מעלה אפרים', 'ערבות הירדן']
    y = 700
    for i, nm in enumerate(names):
        x_r = W-60 if i % 2 == 0 else W/2-15
        if i % 2 == 0 and i: y += 120
        d.rounded_rectangle(P(x_r-(W/2-75), y, x_r, y+96), radius=18*S, fill=(255,255,255))
        d.ellipse(P(x_r-70, y+28, x_r-30, y+68), fill=LB)
        text(d, (x_r-90, y+20), nm, 54, NAVY)
    text(d, (W/2, 1135), 'ובית אל במקום 18 בארץ', 46, LB, anchor='mm')
    save(img, '05.png')

# ---------- 6. Technology ----------
def tech():
    img = Image.new('RGB', (W*S, H*S), ICE); d = ImageDraw.Draw(img)
    d.rectangle(P(0, 0, W, 14), fill=NAVY); chrome(img, d, 6, False)
    label(d, W-60, 230, 'חינוך טכנולוגי', 44)
    text(d, (W-60, 320), 'מצוינות טכנולוגית', 100, NAVY, shadow=(5, 5, (0xC9,0xDB,0xE8)))
    def card(y, place, big, desc, rank):
        d.rounded_rectangle(P(60, y, W-60, y+330), radius=28*S, fill=WHITE)
        d.rounded_rectangle(P(W-60-14, y, W-60, y+330), radius=7*S, fill=LB)
        text(d, (W-110, y+40), place, 80, NAVY)
        text(d, (W-110, y+150), desc, 42, BLUE, bold=False)
        text(d, (W-110, y+215), desc2[place], 42, BLUE, bold=False)
        text(d, (110, y+165), big, 150, LB, anchor='lm', rtl=False)
        lab = f'מקום {rank} בארץ'
        w = tw(d, lab, 38)
        d.rounded_rectangle(P(110, y+40, 110+w+40, y+40+60), radius=30*S, fill=NAVY)
        text(d, (110+20+w, y+48), lab, 38, WHITE)
    global desc2
    desc2 = {'אורנית': 'מבין הלומדים במגמות טכנולוגיות', 'אלקנה': 'מכלל תלמידי י"ב ברשות'}
    card(470, 'אורנית', '91%', 'זכאות לבגרות', 15)
    card(840, 'אלקנה', '24%', 'זכאות לבגרות טק', 12)
    save(img, '06.png')

# ---------- 7. National service (women) podium ----------
def service():
    img = gradient(NAVY, DEEP); arcs(img, 100, 1320, LB, alpha=35, n=3, r0=380)
    d = ImageDraw.Draw(img); chrome(img, d, 7, True)
    label(d, W-60, 230, 'שירות לאומי · בנות', 44)
    text(d, (W-60, 315), 'שלושת המקומות', 100, WHITE)
    text(d, (W-60, 420), 'הראשונים בארץ', 100, LB, shadow=(6, 6, BLUE))
    # podium: 2 | 1 | 3  (RTL reading: 1 in middle)
    pods = [('בית אל', 2, 87.6, 250), ('שומרון', 1, 88.7, 330), ('קרית ארבע', 3, 85.1, 190)]
    base = 1080; pw = 290; gap = 25; x = W-60
    for nm, rk, pct, h in pods:
        x0 = x-pw
        d.rectangle(P(x0, base-h, x, base), fill=WHITE if rk == 1 else (0xC9,0xDB,0xE8))
        text(d, ((x0+x)/2, base-h+60), str(rk), 110, BLUE if rk == 1 else NAVY, anchor='mm', rtl=False)
        text(d, ((x0+x)/2, base-h+150), f'{pct}%', 56, NAVY, anchor='mm', rtl=False) if h > 200 else text(d, ((x0+x)/2, base-h+140), f'{pct}%', 50, NAVY, anchor='mm', rtl=False)
        text(d, ((x0+x)/2, base-h-55), nm, 56, WHITE, anchor='mm')
        x = x0-gap
    text(d, (W/2, 1150), 'ובטופ 20 גם: ערבות הירדן (6), קדומים (7), מטה בנימין (15)', 38, (0xB8,0xD4,0xE8), anchor='mm', bold=False)
    save(img, '07.png')

# ---------- 9. Closing ----------
def closing():
    img = gradient(DEEP, BLUE); arcs(img, 540, 1500, LB, alpha=50, n=4, r0=430, step=80, width=40)
    d = ImageDraw.Draw(img)
    text(d, (W/2, 330), 'מצוינות.', 150, WHITE, anchor='mm')
    text(d, (W/2, 490), 'ערכים.', 150, LB, anchor='mm', shadow=(7, 7, NAVY))
    text(d, (W/2, 650), 'שליחות.', 150, WHITE, anchor='mm')
    text(d, (W/2, 790), 'גאים בתלמידי ובמחנכי יהודה ושומרון', 56, (0xB8,0xD4,0xE8), anchor='mm', bold=False)
    lw = 300; logo(img, True, lw, (W-lw)/2, 900)
    save(img, '09.png')

cover(); bagrut()
bars(3, 'בגרות מצטיינת', 'המצטיינים של הארץ', 'אחוז הזכאים לבגרות מצטיינת מהלומדים',
     [('גוש עציון', 6, 36.7, ''), ('אלקנה', 16, 26.9, ''), ('אפרת', 19, 26.3, '')], 100, '03.png')
bars(4, '5 יחידות', 'מתמטיקה ואנגלית', 'אחוז הזכאים ברמת 5 יחידות מהלומדים',
     [('אלקנה', 6, 35.8, '· מתמטיקה'), ('אפרת', 12, 32.5, '· מתמטיקה'), ('אלקנה', 8, 82.1, '· אנגלית')], 100, '04.png')
integrity(); tech(); service()
bars(8, 'גיוס לצה"ל · בנים', 'בחזית השירות', 'אחוז הגיוס לשירות צבאי, מחזור תשפ"ב',
     [('אריאל', 2, 98.7, ''), ('אלקנה', 9, 95.8, ''), ('אפרת', 17, 94.2, '')], 100, '08.png')
closing()
