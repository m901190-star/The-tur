"""E1 explainer v2 sketches: real hillshade relief map (Terrarium DEM) in RZ teal, real place names, kinetic type, no UK/AU."""
import os, re, math, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance
from relief import View
HERE = os.path.dirname(os.path.abspath(__file__))
KB = HERE + '/../../fonts/HaimClassicv2FM-Bold.ttf'
SEC = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/shalev/fonts/SecularOne.ttf'
RUB = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/fonts/Rubik-700.ttf'
W, H = 1080, 1920
DEEP, TEAL, LT, PALE, NIGHT = (43, 81, 85), (80, 146, 153), (105, 180, 189), (173, 213, 217), (14, 32, 36)
RED, GOLD, WHITE = (226, 70, 60), (244, 200, 90), (255, 255, 255)
def F(p, s): return ImageFont.truetype(p, s, layout_engine=ImageFont.Layout.RAQM)
def hf(t, s): return F(SEC, int(s * .88)) if re.search(r'[A-Za-z0-9]', t) else F(KB, s)
def T(d, xy, t, f, fill=WHITE, anchor='mm', sh=True, **k):
    if sh: d.text((xy[0] + 3, xy[1] + 5), t, font=f, fill=(0, 0, 0, 150), anchor=anchor, direction='rtl', **k)
    d.text(xy, t, font=f, fill=fill, anchor=anchor, direction='rtl', **k)
rng = np.random.default_rng(3); GRAIN = Image.fromarray((rng.normal(128, 22, (H, W))).clip(0, 255).astype(np.uint8))
def finish(im, vign=.55):
    im = im.convert('RGB'); g = Image.merge('RGB', [GRAIN] * 3); im = Image.blend(im, Image.blend(im, g, .5), .12)
    m = Image.new('L', (W, H), 0); md = ImageDraw.Draw(m)
    for i in range(60): md.ellipse((-W * .25 + i * 6, -H * .12 + i * 6, W * 1.25 - i * 6, H * 1.12 - i * 6), fill=int(255 * i / 60))
    m = m.filter(ImageFilter.GaussianBlur(80)); dark = Image.new('RGB', (W, H), (4, 12, 14))
    return Image.composite(im, Image.blend(im, dark, vign), m)
def marker(d, x0, x1, y, col=LT, h=26): d.rounded_rectangle((x0, y - h / 2, x1, y + h / 2), h / 2, fill=col)
def headline(d, lines, y, size=118, hl=None):
    # lines: list of (text, colour); hl = index of line to put a teal marker under
    for k, (t, c) in enumerate(lines):
        f = hf(t, size); yy = y + k * (size + 14)
        if hl == k:
            tw = d.textlength(t, font=f, direction='rtl'); marker(d, W / 2 - tw / 2 - 20, W / 2 + tw / 2 + 20, yy + size * .32, LT + (230,), size * .42)
        T(d, (W / 2, yy), t, f, fill=c)
def lower(d, t, y=1660):
    f = F(RUB, 50)
    for k, l in enumerate(t.split('\n')): T(d, (W / 2, y + k * 70), l, f, stroke_width=2, stroke_fill=(0, 0, 0))
def label(d, v, lat, lon, name, side='l', size=46, col=WHITE, dot=True, dx=0, dy=0):
    x, y = v.xy(lat, lon)
    if dot: d.ellipse((x - 11, y - 11, x + 11, y + 11), fill=col, outline=NIGHT, width=4)
    f = F(KB, size); off = 22
    if side == 'l': T(d, (x - off + dx, y + dy), name, f, fill=col, anchor='rm', stroke_width=4, stroke_fill=NIGHT)
    elif side == 'r': T(d, (x + off + dx, y + dy), name, f, fill=col, anchor='lm', stroke_width=4, stroke_fill=NIGHT)
    elif side == 'b': T(d, (x + dx, y + 44 + dy), name, f, fill=col, stroke_width=4, stroke_fill=NIGHT)
    else: T(d, (x + dx, y - 44 + dy), name, f, fill=col, stroke_width=4, stroke_fill=NIGHT)
PL = {'ירושלים': (31.778, 35.225), 'הר הצופים': (31.794, 35.244), 'מעלה אדומים': (31.775, 35.300), 'עזריה': (31.771, 35.262), 'אבו דיס': (31.760, 35.258),
      'רמאללה': (31.903, 35.204), 'בית לחם': (31.705, 35.202), 'יריחו': (31.857, 35.444)}
ROUTE1 = [(31.783, 35.235), (31.789, 35.255), (31.792, 35.275), (31.790, 35.300), (31.800, 35.330), (31.815, 35.370), (31.835, 35.410), (31.850, 35.440)]
E1 = [(31.808, 35.258), (31.814, 35.283), (31.801, 35.297), (31.787, 35.291), (31.790, 35.266)]
CORR = [(31.893, 35.212), (31.860, 35.250), (31.825, 35.278), (31.800, 35.280), (31.770, 35.272), (31.740, 35.245), (31.715, 35.212)]
def poly(im, v, pts, fill, outline=WHITE, w=5):
    lay = Image.new('RGBA', (W, H)); ld = ImageDraw.Draw(lay); P = [v.xy(*p) for p in pts]
    ld.polygon(P, fill=fill); ld.line(P + [P[0]], fill=outline, width=w, joint='curve'); im.alpha_composite(lay)
def path(im, v, pts, col, w, glow=True, dash=False):
    lay = Image.new('RGBA', (W, H)); ld = ImageDraw.Draw(lay); P = [v.xy(*p) for p in pts]
    if glow:
        ld.line(P, fill=col[:3] + (120,), width=w * 3, joint='curve'); lay = lay.filter(ImageFilter.GaussianBlur(w)); ld = ImageDraw.Draw(lay)
    ld.line(P, fill=col, width=w, joint='curve'); im.alpha_composite(lay); return P
def mapbase(v, dim=0):
    im = v.render(); 
    if dim: im = Image.blend(im, Image.new('RGB', im.size, NIGHT), dim)
    return im.convert('RGBA')
def corner_tag(d, t='מפת תבליט · המיקומים להמחשה'):
    f = F(RUB, 24); tw = d.textlength(t, font=f, direction='rtl'); d.rounded_rectangle((36, H - 96, 36 + tw + 32, H - 54), 21, fill=(0, 0, 0, 140)); T(d, (36 + 16, H - 75), t, f, fill=PALE, anchor='lm', sh=False)

def card(src, box, w, rot=0, hl=()):
    c = Image.open(HERE + '/src/' + src).convert('RGB')
    if box: c = c.crop(box)
    if hl:
        lay = Image.new('RGB', c.size, WHITE); ld = ImageDraw.Draw(lay)
        for b in hl: ld.rectangle(b, fill=(255, 226, 90))
        from PIL import ImageChops
        c = ImageChops.multiply(c, lay)
    c = c.resize((w, int(c.height * w / c.width)), Image.LANCZOS)
    pad = 18; fr = Image.new('RGBA', (c.width + pad * 2, c.height + pad * 2), WHITE + (255,)); fr.paste(c, (pad, pad))
    sh = Image.new('RGBA', (fr.width + 80, fr.height + 80), (0, 0, 0, 0)); ImageDraw.Draw(sh).rectangle((40, 50, fr.width + 40, fr.height + 50), fill=(0, 0, 0, 150)); sh = sh.filter(ImageFilter.GaussianBlur(18))
    sh.alpha_composite(fr, (40, 40)); return sh.rotate(rot, Image.BICUBIC, expand=True)
def chip(d, x, y, t, col, fg=WHITE, size=40, anchor='r'):
    f = hf(t, size) if re.search(r'[0-9]', t) else F(RUB, size); tw = d.textlength(t, font=f, direction='rtl'); x0 = x - tw - 44 if anchor == 'r' else x
    d.rounded_rectangle((x0, y - size * .75, x0 + tw + 44, y + size * .75), size * .75, fill=col); T(d, (x0 + 22 + tw / 2, y), t, f, fill=fg, sh=False)
OUT = []
# 1 — opening: low map, big type
v = View(31.80, 35.27, 1.25); im = mapbase(v, .45); d = ImageDraw.Draw(im)
T(d, (W / 2, 620), 'E1', F(SEC, 380), fill=GOLD)
headline(d, [('מה זה בכלל?', WHITE), ('ולמה כולם', WHITE), ('נלחמים עליו', WHITE)], 950, 112, hl=2)
OUT.append(('01-open', finish(im)))
# 2 — wide map, orientation
v = View(31.80, 35.31, .78); im = mapbase(v, .05); d = ImageDraw.Draw(im)
path(im, v, ROUTE1, (240, 240, 240, 230), 6, glow=False); d = ImageDraw.Draw(im)
for n, s in [('רמאללה', 'r'), ('ירושלים', 'b'), ('בית לחם', 'r'), ('מעלה אדומים', 'b')]: label(d, v, *PL[n], n, s)
T(d, (W - 60, v.xy(31.70, 35.4)[1]), 'מדבר יהודה', F(KB, 46), fill=PALE, anchor='rm', stroke_width=4, stroke_fill=NIGHT)
x, y = v.xy(31.828, 35.39); T(d, (x, y - 30), 'כביש 1', F(SEC, 34), fill=WHITE, stroke_width=3, stroke_fill=NIGHT)
headline(d, [('ירושלים', WHITE), ('ומה שממזרח לה', LT)], 170, 92)
lower(d, 'מזרחית לירושלים, בדרך לים המלח,\nיושבת מעלה אדומים'); corner_tag(d); OUT.append(('02-wide', finish(im, .4)))
# 3 — zoom: E1 between Jerusalem and Ma'ale Adumim
v = View(31.787, 35.262, 1.75); im = mapbase(v); d = ImageDraw.Draw(im)
path(im, v, ROUTE1, (240, 240, 240, 230), 8, glow=False); poly(im, v, E1, GOLD + (150,), WHITE, 6); d = ImageDraw.Draw(im)
cx = sum(v.xy(*p)[0] for p in E1) / 5; cy = sum(v.xy(*p)[1] for p in E1) / 5; T(d, (cx, cy), 'E1', F(SEC, 110), fill=NIGHT, sh=False)
for n, s, sz in [('ירושלים', 'b', 50), ('הר הצופים', 'top', 40), ('עזריה', 'l', 36), ('אבו דיס', 'l', 36)]: label(d, v, *PL[n], n, s, sz)
label(d, v, *PL['מעלה אדומים'], 'מעלה אדומים', 'b', 50, dx=-90)
headline(d, [('השטח הריק בין ירושלים', WHITE), ('למעלה אדומים', GOLD)], 180, 84)
lower(d, 'בנייה כאן מחברת את מעלה אדומים\nלירושלים ברצף אחד'); corner_tag(d); OUT.append(('03-zoom-e1', finish(im, .35)))
# 4 — without E1: Palestinian corridor
v = View(31.80, 35.25, .78); im = mapbase(v, .15); d = ImageDraw.Draw(im)
P = path(im, v, CORR, RED + (255,), 16); d = ImageDraw.Draw(im)
(xa, ya), (xb, yb) = P[-2], P[-1]; a = math.atan2(yb - ya, xb - xa); L = 54
d.polygon([(xb + 12 * math.cos(a), yb + 12 * math.sin(a)), (xb - L * math.cos(a - .5), yb - L * math.sin(a - .5)), (xb - L * math.cos(a + .5), yb - L * math.sin(a + .5))], fill=RED)
for n, s in [('רמאללה', 'l'), ('ירושלים', 'l'), ('בית לחם', 'l'), ('מעלה אדומים', 'b')]: label(d, v, *PL[n], n, s)
headline(d, [('בלי E1', RED), ('רצף פלסטיני', WHITE)], 150, 84)
lower(d, 'רצף מרמאללה עד בית לחם:\nבדיוק מה שמדינה פלסטינית צריכה'); corner_tag(d); OUT.append(('04-corridor', finish(im, .35)))
# 5 — with E1: blocked
v = View(31.80, 35.25, .78); im = mapbase(v, .15); d = ImageDraw.Draw(im)
path(im, v, CORR[:3], RED + (255,), 16); path(im, v, CORR[4:], RED + (255,), 16); poly(im, v, E1, GOLD + (230,), WHITE, 6); d = ImageDraw.Draw(im)
cx = sum(v.xy(*p)[0] for p in E1) / 5; cy = sum(v.xy(*p)[1] for p in E1) / 5
d.rounded_rectangle((cx - 150, cy - 46, cx + 150, cy + 46), 46, fill=NIGHT, outline=GOLD, width=5); T(d, (cx, cy), 'נחסם', F(KB, 64), fill=GOLD, sh=False)
for n, s in [('רמאללה', 'l'), ('ירושלים', 'l'), ('בית לחם', 'l'), ('מעלה אדומים', 'b')]: label(d, v, *PL[n], n, s)
headline(d, [('עם E1', GOLD), ('הרצף נחתך', WHITE)], 150, 84, hl=1)
lower(d, 'לכן קוראים לזה "בולם":\nזה בולם מדינה פלסטינית'); corner_tag(d); OUT.append(('05-blocked', finish(im, .35)))
# 6 — Smotrich promoted the plan
v = View(31.80, 35.28, 1.6); im = mapbase(v, .55); d = ImageDraw.Draw(im)
s = Image.open(HERE + '/src/smotrich-cut.png').convert('RGBA'); s = s.resize((int(s.width * 1260 / s.height), 1260), Image.LANCZOS)
im.alpha_composite(s, (W - s.width + 120, H - s.height - 60)); d = ImageDraw.Draw(im)
fade = Image.new('RGBA', (W, H)); fd = ImageDraw.Draw(fade)
for y in range(H - 700, H): fd.line((0, y, W, y), fill=NIGHT + (int(235 * (y - (H - 700)) / 700),))
im.alpha_composite(fade); d = ImageDraw.Draw(im)
headline(d, [('שר האוצר', LT), ('קידם את התוכנית', WHITE)], 220, 104, hl=None)
T(d, (W - 80, 1450), '⁦3,401⁩', F(SEC, 150), fill=GOLD, anchor='rm'); T(d, (W - 80, 1580), 'יחידות דיור ב־E1', F(SEC, 56), anchor='rm')
T(d, (W - 80, 1680), 'אישור סופי · אוגוסט ⁦2025⁩', F(RUB, 44), fill=PALE, anchor='rm'); OUT.append(('06-smotrich', finish(im, .3)))
# 7 — news montage
v = View(31.80, 35.28, 1.6); im = mapbase(v, .55); d = ImageDraw.Draw(im)
c1 = card('jdn.jpg', None, 820, 4); im.alpha_composite(c1, (60, 360))
c2 = card('a7.jpg', (0, 120, 1320, 600), 900, -3); im.alpha_composite(c2, (40, 1020))
d = ImageDraw.Draw(im); headline(d, [('השבוע', GOLD), ('בכל הכותרות', WHITE)], 150, 96)
chip(d, W - 60, 1700, '\u206617.11.2026\u2069', RED); OUT.append(('07-news', finish(im, .3)))
# 8 — the AG (colour, Knesset photo)
v = View(31.80, 35.28, 1.6); im = mapbase(v, .5); d = ImageDraw.Draw(im)
ph = Image.open(HERE + '/src/a7.jpg').convert('RGB').crop((0, 1050, 1320, 1795)); ph = ImageOps.fit(ph, (W, 1000), Image.LANCZOS, centering=(.45, .3))
m = Image.new('L', (W, 1000), 255); md = ImageDraw.Draw(m)
for y in range(700, 1000): md.line((0, y, W, y), fill=int(255 * (1 - (y - 700) / 300)))
im.paste(ph, (0, 300), m); d = ImageDraw.Draw(im)
T(d, (W - 40, 1270), 'צילום: נעם מושקוביץ, דוברות הכנסת', F(RUB, 22), fill=PALE, anchor='rm', sh=False)
T(d, (W / 2, 170), 'ואז, היועמ״שית', F(KB, 110), fill=RED)
T(d, (W / 2, 1370), 'הורתה לעצור את המכרז', F(KB, 88)); T(d, (W / 2, 1480), 'עד להקמת ממשלה חדשה', F(KB, 70), fill=RED)
chip(d, W / 2 + 330, 1620, '\u20661,234\u2069 דירות', GOLD, NIGHT, 40); chip(d, W / 2 - 40, 1620, 'יומיים לפני פתיחת המעטפות', TEAL, WHITE, 36)
OUT.append(('08-ag', finish(im, .3)))
# 9 — she promised the court
v = View(31.80, 35.28, 1.6); im = mapbase(v, .6); d = ImageDraw.Draw(im)
c = card('clip-bagatz.jpg', None, 900, -2, hl=[(190, 625, 590, 690), (40, 700, 1290, 770), (740, 770, 1290, 840)]); im.alpha_composite(c, ((W - c.width) // 2, 560))
d = ImageDraw.Draw(im); headline(d, [('רק לפני חודש', GOLD), ('היא התחייבה בבג״ץ', WHITE)], 170, 96, hl=1)
lower(d, 'לאפשר לפתוח את המעטפות ב־\u206619\u2069 בנובמבר.\nיומיים לפני, היא עצרה.', 1640); OUT.append(('09-bagatz', finish(im, .3)))
# 10 — why it's wrong, plain
im = mapbase(View(31.80, 35.28, 1.6), .72); d = ImageDraw.Draw(im)
rows = [('הממשלה אישרה', '✓'), ('התוכנית אושרה סופית', '✓'), ('התחייבה בבג״ץ', '✓'), ('ואז עצרה', '✕')]
y = 480
for k, (t, m) in enumerate(rows):
    col = RED if k == 3 else LT
    T(d, (W - 110, y), t, F(KB, 72), fill=WHITE if k < 3 else RED, anchor='rm')
    d.ellipse((90, y - 50, 190, y + 50), outline=col, width=8)
    if k < 3: d.line((112, y, 135, y + 24, 170, y - 22), fill=col, width=10, joint='curve')
    else: d.line((115, y - 25, 165, y + 25), fill=col, width=10); d.line((115, y + 25, 165, y - 25), fill=col, width=10)
    y += 210
lower(d, 'החלטה של ממשלה נבחרת\nנעצרת בלי סמכות', 1500); OUT.append(('10-why', finish(im, .3)))
# 9 — end
v = View(31.79, 35.262, 1.25); im = mapbase(v, .35); poly(im, v, E1, GOLD + (200,), WHITE, 6); d = ImageDraw.Draw(im)
headline(d, [('אנחנו נחושים', WHITE), ('לבנות ב־E1', GOLD)], 260, 128, hl=None)
for n, s_ in [('ירושלים', 'l'), ('מעלה אדומים', 'b')]: label(d, v, *PL[n], n, s_, 50)
OUT.append(('11-end', finish(im, .45)))
os.makedirs(HERE + '/sketch3', exist_ok=True)
for n, im in OUT: im.save(HERE + f'/sketch3/{n}.jpg', quality=90)
fw, fh, g = 300, 533, 16; cols = 5; rr = math.ceil(len(OUT) / cols)
sheet = Image.new('RGB', (cols * (fw + g) + g, rr * (fh + 60) + g), (8, 10, 12)); sd = ImageDraw.Draw(sheet)
for i, (n, im) in enumerate(OUT):
    c, r = i % cols, i // cols; x = sheet.width - (c + 1) * (fw + g); y = g + r * (fh + 60)
    sheet.paste(im.resize((fw, fh)), (x, y)); sd.text((x + fw / 2, y + fh + 28), str(i + 1), font=F(SEC, 30), fill=WHITE, anchor='mm')
sheet.save(HERE + '/sketch3-sheet.jpg', quality=90); print('ok')
