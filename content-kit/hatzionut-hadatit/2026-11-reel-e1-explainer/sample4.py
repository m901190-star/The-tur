"""More colourful variant samples (frames 3, 5, 6) to compare with v3."""
import os; os.environ['E1_VIVID'] = '1'
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(HERE + '/sketch3.py').read(); exec(src[:src.index('OUT = ' + '[]')])
def finish2(im): return finish(im, .18)
def flag(d, x, y, s=1.0):
    d.line((x, y, x, y - 70 * s), fill=WHITE, width=4); fx, fy = x + 2, y - 70 * s
    d.rectangle((fx, fy, fx + 56 * s, fy + 40 * s), fill=WHITE); d.rectangle((fx, fy + 5 * s, fx + 56 * s, fy + 10 * s), fill=(0, 56, 184)); d.rectangle((fx, fy + 30 * s, fx + 56 * s, fy + 35 * s), fill=(0, 56, 184))
    cx, cy, r = fx + 28 * s, fy + 20 * s, 9 * s
    for a0 in (90, 270):
        import math; pts = [(cx + r * math.cos(math.radians(a0 + k * 120)), cy - r * math.sin(math.radians(a0 + k * 120))) for k in range(3)]; d.polygon(pts, outline=(0, 56, 184), width=2)
def pin(d, v, lat, lon, col, r=16):
    x, y = v.xy(lat, lon); d.ellipse((x - r - 8, y - r - 8, x + r + 8, y + r + 8), fill=col + (90,)); d.ellipse((x - r, y - r, x + r, y + r), fill=col, outline=WHITE, width=4); return x, y
def chipbar(d, y, items):
    x = W - 60
    for t, col, fg in items:
        f = hf(t, 40) if any(c.isdigit() for c in t) else F(RUB, 38); tw = d.textlength(t, font=f, direction='rtl')
        d.rounded_rectangle((x - tw - 44, y - 32, x, y + 32), 32, fill=col); T(d, (x - 22 - tw / 2, y), t, f, fill=fg, sh=False); x -= tw + 64
def paflag(d, x, y, s=1.0):
    d.line((x, y, x, y - 70 * s), fill=WHITE, width=4); fx, fy = x + 2, y - 70 * s; w, h = 56 * s, 40 * s
    d.rectangle((fx, fy, fx + w, fy + h / 3), fill=(0, 0, 0)); d.rectangle((fx, fy + h / 3, fx + w, fy + 2 * h / 3), fill=WHITE); d.rectangle((fx, fy + 2 * h / 3, fx + w, fy + h), fill=(0, 122, 61))
    d.polygon([(fx, fy), (fx + w * .42, fy + h / 2), (fx, fy + h)], fill=(206, 17, 38)); d.rectangle((fx, fy, fx + w, fy + h), outline=(255, 255, 255), width=1)
ABBAS = HERE + '/src/abbas.jpg'
def abbas_badge(d, x, y, r=46):
    cx, cy = x + 70, y - 60
    if os.path.exists(ABBAS):
        ph = ImageOps.fit(Image.open(ABBAS).convert('RGB'), (2 * r, 2 * r), Image.LANCZOS, centering=(.5, .3)); m = Image.new('L', (2 * r, 2 * r), 0); ImageDraw.Draw(m).ellipse((0, 0, 2 * r, 2 * r), fill=255)
        d._image.paste(ph, (int(cx - r), int(cy - r)), m)
    else:
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(60, 60, 60)); T(d, (cx, cy), 'אבו\nמאזן', F(RUB, 22), sh=False, align='center')
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=RED, width=6)
def pa_zone(im, v, lat, lon, rad_px):
    x, y = v.xy(lat, lon); lay = Image.new('RGBA', (W, H)); ld = ImageDraw.Draw(lay)
    ld.ellipse((x - rad_px, y - rad_px, x + rad_px, y + rad_px), fill=RED + (70,)); lay = lay.filter(ImageFilter.GaussianBlur(rad_px * .35)); im.alpha_composite(lay)
OUT = []
# 3 vivid
v = View(31.787, 35.262, 1.75); im = mapbase(v); d = ImageDraw.Draw(im)
path(im, v, ROUTE1, (255, 255, 255, 240), 8, glow=False); poly(im, v, E1, GOLD + (170,), WHITE, 6)
lay = Image.new('RGBA', (W, H)); ld = ImageDraw.Draw(lay); ld.polygon([v.xy(*p) for p in E1], fill=GOLD + (120,)); lay = lay.filter(ImageFilter.GaussianBlur(30)); im.alpha_composite(lay); poly(im, v, E1, GOLD + (170,), WHITE, 6); d = ImageDraw.Draw(im)
cx = sum(v.xy(*p)[0] for p in E1) / 5; cy = sum(v.xy(*p)[1] for p in E1) / 5; T(d, (cx, cy), 'E1', F(SEC, 110), fill=NIGHT, sh=False)
x, y = pin(d, v, *PL['ירושלים'], GOLD); flag(d, x + 6, y - 14, .9); label(d, v, *PL['ירושלים'], 'ירושלים', 'b', 54, dot=False)
x, y = pin(d, v, *PL['מעלה אדומים'], LT); flag(d, x + 6, y - 14, .9); label(d, v, *PL['מעלה אדומים'], 'מעלה אדומים', 'b', 54, dot=False, dx=-90)
pin(d, v, *PL['הר הצופים'], WHITE, 10); label(d, v, *PL['הר הצופים'], 'הר הצופים', 'top', 40, dot=False)
x, y = v.xy(31.792, 35.300); T(d, (x + 20, y - 40), 'כביש 1', F(SEC, 34), fill=WHITE, stroke_width=4, stroke_fill=NIGHT)
headline(d, [('השטח הריק בין ירושלים', WHITE), ('למעלה אדומים', GOLD)], 180, 84, hl=1)
chipbar(d, 1650, [('מחבר את מעלה אדומים לירושלים', TEAL, WHITE)])
OUT.append(('03', finish2(im)))
# 4 vivid: corridor with PA
def mapPA(v, cut):
    im = mapbase(v, .05)
    for n in ('רמאללה', 'בית לחם'): pa_zone(im, v, *PL[n], 120)
    if cut: path(im, v, CORR[:3], RED + (255,), 18); path(im, v, CORR[4:], RED + (255,), 18)
    else: path(im, v, CORR, RED + (255,), 18)
    d = ImageDraw.Draw(im); return im, d
v = View(31.80, 35.25, .78)
im, d = mapPA(v, False); P = [v.xy(*p) for p in CORR]; (xa, ya), (xb, yb) = P[-2], P[-1]; import math; a = math.atan2(yb - ya, xb - xa); L = 54
d.polygon([(xb + 12 * math.cos(a), yb + 12 * math.sin(a)), (xb - L * math.cos(a - .5), yb - L * math.sin(a - .5)), (xb - L * math.cos(a + .5), yb - L * math.sin(a + .5))], fill=RED)
def places(d, v):
    for n, c, s_ in [('רמאללה', RED, 'l'), ('בית לחם', RED, 'l'), ('ירושלים', GOLD, 'l'), ('מעלה אדומים', LT, 'b')]:
        x, y = pin(d, v, *PL[n], c, 13); label(d, v, *PL[n], n, s_, 46, dot=False)
        if c == RED: abbas_badge(d, x, y)
        else: flag(d, x + 4, y - 12, .8)
places(d, v); headline(d, [('בלי E1', RED), ('רצף פלסטיני', WHITE)], 150, 84)
lower(d, 'רצף מרמאללה עד בית לחם:\nבדיוק מה שמדינה פלסטינית צריכה'); OUT.append(('04', finish2(im)))
# 5 vivid
im, d = mapPA(v, True)
lay = Image.new('RGBA', (W, H)); ld = ImageDraw.Draw(lay); ld.polygon([v.xy(*p) for p in E1], fill=GOLD + (200,)); lay = lay.filter(ImageFilter.GaussianBlur(40)); im.alpha_composite(lay); poly(im, v, E1, GOLD + (240,), WHITE, 6); d = ImageDraw.Draw(im)
cx = sum(v.xy(*p)[0] for p in E1) / 5; cy = sum(v.xy(*p)[1] for p in E1) / 5
d.rounded_rectangle((cx - 160, cy - 50, cx + 160, cy + 50), 50, fill=GOLD, outline=WHITE, width=5); T(d, (cx, cy), 'נחסם', F(KB, 66), fill=NIGHT, sh=False)
places(d, v); headline(d, [('עם E1', GOLD), ('הרצף נחתך', WHITE)], 150, 84, hl=1)
lower(d, 'לכן קוראים לזה "בולם":\nזה בולם מדינה פלסטינית'); OUT.append(('05', finish2(im)))
# 6 vivid: houses
v = View(31.80, 35.28, 1.6); im = mapbase(v, .35); d = ImageDraw.Draw(im)
s_ = Image.open(HERE + '/src/smotrich-cut.png').convert('RGBA'); s_ = s_.resize((int(s_.width * 1150 / s_.height), 1150), Image.LANCZOS)
glow = Image.new('RGBA', (W, H)); gd = ImageDraw.Draw(glow); gd.ellipse((W - 760, 520, W + 100, 1420), fill=LT + (160,)); glow = glow.filter(ImageFilter.GaussianBlur(90)); im.alpha_composite(glow)
im.alpha_composite(s_, (W - s_.width + 160, 420)); d = ImageDraw.Draw(im)
fade = Image.new('RGBA', (W, H)); fd = ImageDraw.Draw(fade)
for y in range(1250, H): fd.line((0, y, W, y), fill=NIGHT + (int(240 * min(1, (y - 1250) / 300)),))
im.alpha_composite(fade); d = ImageDraw.Draw(im)
headline(d, [('שר האוצר', LT), ('קידם את התוכנית', WHITE)], 170, 100, hl=1)
def house(d, x, y, s, col):
    d.polygon([(x, y - s * .55), (x - s * .55, y - s * .05), (x + s * .55, y - s * .05)], fill=col); d.rectangle((x - s * .4, y - s * .05, x + s * .4, y + s * .45), fill=col); d.rectangle((x - s * .1, y + s * .15, x + s * .1, y + s * .45), fill=NIGHT)
k = 0
for r in range(4):
    for c in range(7):
        col = GOLD if k < 24 else (GOLD[0], GOLD[1], GOLD[2]); house(d, 90 + c * 62, 1400 + r * 70, 46, GOLD if (r + c) % 3 else (255, 230, 150)); k += 1
T(d, (W - 80, 1440), '⁦3,401⁩', F(SEC, 160), fill=GOLD, anchor='rm'); T(d, (W - 80, 1570), 'יחידות דיור ב־E1', F(SEC, 56), anchor='rm')
chipbar(d, 1690, [('אישור סופי · אוגוסט ⁦2025⁩', TEAL, WHITE)]); OUT.append(('06', finish2(im)))
os.makedirs(HERE + '/sample4', exist_ok=True)
old = {'03': '03-zoom-e1', '04': '04-corridor', '05': '05-blocked', '06': '06-smotrich'}
fw, fh = 360, 640; sheet = Image.new('RGB', (4 * (2 * fw + 30) + 40, fh + 110), (8, 10, 12)); sd = ImageDraw.Draw(sheet)
for i, (n, im) in enumerate(OUT):
    im.save(HERE + f'/sample4/{n}.jpg', quality=90); x = sheet.width - (i + 1) * (2 * fw + 30) - 10
    sheet.paste(Image.open(HERE + f'/sketch3/{old[n]}.jpg').resize((fw, fh)), (x + fw + 10, 50)); sheet.paste(im.resize((fw, fh)), (x, 50))
    T(sd, (x + fw + 10 + fw / 2, 25), 'לפני', F(RUB, 28), sh=False); T(sd, (x + fw / 2, 25), 'צבעוני', F(RUB, 28), fill=GOLD, sh=False)
sheet.save(HERE + '/sample4-compare.jpg', quality=88); print('ok')
