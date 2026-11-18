"""E1 explainer reel: animated render of the approved storyboard + Harrison VO + Splice bed. 720x1280 @30."""
import os, sys, subprocess, math, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
_s = open(HERE + '/sample4.py').read(); exec(_s[:_s.index('\nOUT = []')])
FPS, OW, OH = 30, 720, 1280
def eo(x): x = max(0., min(1., x)); return 1 - (1 - x) ** 3
def eio(x): x = max(0., min(1., x)); return x * x * (3 - 2 * x)
def dur(f): return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f], capture_output=True, text=True).stdout)
VOF = [HERE + f'/vo2/{k:02d}.mp3' for k in range(1, 12)]; VOF[6] = HERE + '/vo2/07c.mp3'   # Barrett, vocalized, 'E-echad'
VD = [dur(f) for f in VOF]; LEAD = .25; PAD = [.35, .45, .5, .6, .6, .5, .45, .45, .5, .55, 1.2]
D = [VD[k] + LEAD + PAD[k] for k in range(11)]
# fast finish: cached vignette + grain
_m = Image.new('L', (W, H), 0); _md = ImageDraw.Draw(_m)
for i in range(60): _md.ellipse((-W * .25 + i * 6, -H * .12 + i * 6, W * 1.25 - i * 6, H * 1.12 - i * 6), fill=int(255 * i / 60))
VIG = _m.filter(ImageFilter.GaussianBlur(80)); DARK = Image.new('RGB', (W, H), (4, 12, 14)); G3 = Image.merge('RGB', [GRAIN] * 3)
def fin(im, vign=.18):
    im = im.convert('RGB'); im = Image.blend(im, Image.blend(im, G3, .5), .1)
    return Image.composite(im, Image.blend(im, DARK, vign), VIG)
def ai_tag(d):
    f = F(RUB, 24); t = 'קריינות AI'; tw = d.textlength(t, font=f, direction='rtl'); d.rounded_rectangle((36, 40, 36 + tw + 30, 80), 20, fill=(0, 0, 0, 120)); T(d, (36 + 15 + tw / 2, 60), t, f, fill=PALE, sh=False)
def alpha_layer(fn, a):
    """draw into transparent layer then composite with alpha a"""
    lay = Image.new('RGBA', (W, H)); fn(lay, ImageDraw.Draw(lay)); 
    if a < 1: lay.putalpha(lay.split()[-1].point(lambda p: int(p * a)))
    return lay
def partial(pts, p):
    if p >= 1: return pts
    seg = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]; L = sum(seg) * p; out = [pts[0]]
    for i, s_ in enumerate(seg):
        if L >= s_: out.append(pts[i + 1]); L -= s_
        else: f = L / s_; out.append((pts[i][0] + (pts[i + 1][0] - pts[i][0]) * f, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * f)); break
    return out
def headline_a(im, lines, y, size, a, hl=None, rise=40):
    if a <= 0: return
    im.alpha_composite(alpha_layer(lambda l, d: headline(d, lines, y + rise * (1 - a), size, hl), a))
def lower_a(im, t_, a, y=1660):
    if a > 0: im.alpha_composite(alpha_layer(lambda l, d: lower(d, t_, y), a))
def latlon_band(im, v, pts, col, w, a, p=1.0):
    P = partial([v.xy(*q) for q in pts], p)
    if len(P) < 2 or a <= 0: return
    lay = Image.new('RGBA', (W, H)); ld = ImageDraw.Draw(lay); ld.line(P, fill=col + (int(a),), width=w, joint='curve')
    for x, y in (P[0], P[-1]): ld.ellipse((x - w / 2, y - w / 2, x + w / 2, y + w / 2), fill=col + (int(a),))
    im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(3)))
def area_a(im, v, pts, col, a, fa=95):
    if a <= 0: return
    lay = Image.new('RGBA', (W, H)); area(lay, v, pts, col, fa); lay.putalpha(lay.split()[-1].point(lambda q: int(q * a))); im.alpha_composite(lay)
def places_a(im, v, t, t0=.2, step=.3, which=('ירושלים', 'מעלה אדומים', 'רמאללה', 'בית לחם')):
    cfg = {'רמאללה': (RED, 'l'), 'בית לחם': (RED, 'l'), 'ירושלים': (GOLD, 'l'), 'מעלה אדומים': (LT, 'b')}
    for k, n in enumerate(which):
        a = eo((t - t0 - k * step) / .35)
        if a <= 0: continue
        def fn(l, d, n=n):
            c, s_ = cfg[n]; x, y = pin(d, v, *PL[n], c, 13); label(d, v, *PL[n], n, s_, 46, dot=False)
            if c == RED: abbas_badge(d, x, y)
            else: flag(d, x + 4, y - 12, .8)
        im.alpha_composite(alpha_layer(fn, a))
def e1_glow(im, v, a, glow=1.0):
    if a <= 0: return
    lay = Image.new('RGBA', (W, H)); ld = ImageDraw.Draw(lay); ld.polygon([v.xy(*p) for p in E1], fill=GOLD + (int(200 * a * glow),)); im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(36)))
    lay = Image.new('RGBA', (W, H)); poly(lay, v, E1, GOLD + (int(220 * a),), WHITE + (int(255 * a),), 6); im.alpha_composite(lay)
CARD = {}
def cardc(key, *a, **k):
    if key not in CARD: CARD[key] = card(*a, **k)
    return CARD[key]
def paste_scaled(im, c, cx, cy, s, a):
    if a <= 0: return
    c2 = c.resize((max(1, int(c.width * s)), max(1, int(c.height * s))), Image.BILINEAR)
    if a < 1: c2.putalpha(c2.split()[-1].point(lambda q: int(q * a)))
    im.alpha_composite(c2, (int(cx - c2.width / 2), int(cy - c2.height / 2)))
# ---------- shots ----------
V2 = (31.80, 35.31, .78); V3 = (31.787, 35.262, 1.75); V4 = (31.80, 35.25, .78)
def lerpv(a, b, u): return View(*(a[i] + (b[i] - a[i]) * u for i in range(3)))
def s1(t, D):
    v = View(31.80, 35.27, 1.15 + .12 * t / D); im = mapbase(v, .45); d = ImageDraw.Draw(im)
    p = eo(t / .5); 
    if p > 0: im.alpha_composite(alpha_layer(lambda l, dd: T(dd, (W / 2, 620), 'E1', F(SEC, max(10, int(380 * (.6 + .4 * p)))), fill=GOLD), p))
    for k, (txt, c) in enumerate([('מה זה בכלל?', WHITE), ('ולמה כולם', WHITE), ('נלחמים עליו', WHITE)]):
        a = eo((t - .5 - k * .35) / .3); headline_a(im, [(txt, c)], 950 + k * 126, 112, a, hl=0 if (k == 2 and t > 1.7) else None)
    return im, None
def s2(t, D):
    v = View(V2[0], V2[1], V2[2] * (1 + .04 * t / D)); im = mapbase(v, .05)
    P = partial([v.xy(*p) for p in ROUTE1], eo((t - .3) / 1.6))
    if len(P) > 1: ImageDraw.Draw(im).line(P, fill=(240, 240, 240, 230), width=6, joint='curve')
    places_a(im, v, t, .4, .35, ('ירושלים', 'מעלה אדומים', 'רמאללה', 'בית לחם'))
    if t > 1.8:
        a = eo((t - 1.8) / .4); x, y = v.xy(31.828, 35.39)
        im.alpha_composite(alpha_layer(lambda l, d: T(d, (x, y - 30), 'כביש 1', F(SEC, 34), fill=WHITE, stroke_width=3, stroke_fill=NIGHT), a))
    headline_a(im, [('ירושלים', WHITE), ('ומה שממזרח לה', LT)], 170, 92, eo(t / .4))
    lower_a(im, 'מזרחית לירושלים, בדרך לים המלח,\nיושבת מעלה אדומים', eo((t - .6) / .4))
    corner_tag(ImageDraw.Draw(im), 'מפת תבליט · המיקומים להמחשה'); return im, None
def s3(t, D):
    u = eio(t / 1.6); v = lerpv(V2, V3, u); im = mapbase(v)
    ImageDraw.Draw(im).line([v.xy(*p) for p in ROUTE1], fill=(255, 255, 255, 240), width=int(6 + 2 * u), joint='curve')
    a = eo((t - 1.5) / .7); e1_glow(im, v, a, .8 + .2 * math.sin(t * 3))
    if a > 0:
        cx = sum(v.xy(*p)[0] for p in E1) / 5; cy = sum(v.xy(*p)[1] for p in E1) / 5
        im.alpha_composite(alpha_layer(lambda l, d: T(d, (cx, cy), 'E1', F(SEC, 110), fill=NIGHT, sh=False), a))
    def labs(l, d):
        x, y = pin(d, v, *PL['ירושלים'], GOLD); flag(d, x + 6, y - 14, .9); label(d, v, *PL['ירושלים'], 'ירושלים', 'b', 54, dot=False)
        x, y = pin(d, v, *PL['מעלה אדומים'], LT); flag(d, x + 6, y - 14, .9); label(d, v, *PL['מעלה אדומים'], 'מעלה אדומים', 'b', 54, dot=False, dx=-90)
    im.alpha_composite(alpha_layer(labs, 1.0))
    headline_a(im, [('השטח הריק בין ירושלים', WHITE), ('למעלה אדומים', GOLD)], 180, 84, eo((t - 1.4) / .4), hl=1 if t > 2.2 else None)
    if t > 3.5: im.alpha_composite(alpha_layer(lambda l, d: chipbar(d, 1650, [('מחבר את מעלה אדומים לירושלים', TEAL, WHITE)]), eo((t - 3.5) / .3)))
    return im, None
def s4(t, D):
    v = View(*V4); im = mapbase(v, .05)
    for k, n in enumerate(('ירושלים', 'מעלה אדומים', 'רמאללה', 'בית לחם')):
        area_a(im, v, AREAS[n], BLUE if k < 2 else RED, eo((t - .2 - k * .3) / .5), 80 if k < 2 else 95)
    t_opt = 1.6; t_red = .5 * D
    if t_opt < t < t_red + .6:
        fa = eo((t - t_opt) / .5) * (1 - eo((t - t_red) / .6))
        latlon_band(im, v, [(31.788, 35.235), (31.798, 35.27), (31.782, 35.295)], BLUE, 90, 160 * fa)
        latlon_band(im, v, CORR, RED, 70, 110 * fa)
    if t >= t_red: latlon_band(im, v, CORR, RED, 70, 160, eio((t - t_red) / 1.8))
    places_a(im, v, t, .3, .3)
    if t < t_red: headline_a(im, [('שתי אפשרויות', WHITE)], 170, 96, eo((t - t_opt) / .4) * (1 - eo((t - t_red + .3) / .3)), hl=0)
    headline_a(im, [('בלי E1', RED), ('רצף פלסטיני', WHITE)], 150, 84, eo((t - t_red) / .4))
    if t_opt < t < t_red:
        a = eo((t - t_opt - .6) / .3); im.alpha_composite(alpha_layer(lambda l, d: (chipbar(d, 1560, [('ירושלים – מעלה אדומים', BLUE, WHITE)]), chipbar(d, 1660, [('רמאללה – בית לחם', RED, WHITE)])), a * (1 - eo((t - t_red + .3) / .3))))
    lower_a(im, 'רצף מרמאללה עד בית לחם:\nבדיוק מה שמדינה פלסטינית צריכה', eo((t - t_red - 1.6) / .4))
    corner_tag(ImageDraw.Draw(im), 'הגבולות להמחשה'); return im, None
def s5(t, D):
    v = View(*V4); im = mapbase(v, .05)
    for k, n in enumerate(('ירושלים', 'מעלה אדומים', 'רמאללה', 'בית לחם')): area_a(im, v, AREAS[n], BLUE if k < 2 else RED, 1, 80 if k < 2 else 95)
    cut = eo((t - 1.6) / .4)
    latlon_band(im, v, CORR[:3], RED, 70, 160); latlon_band(im, v, CORR[4:], RED, 70, 160)
    if cut < 1: latlon_band(im, v, CORR[2:5], RED, 70, 160 * (1 - cut))
    latlon_band(im, v, [(31.788, 35.235), (31.798, 35.27), (31.782, 35.295)], BLUE, 120, 215, eio(t / 1.6))
    e1_glow(im, v, eo((t - 1.0) / .5))
    places_a(im, v, 9)
    if t > 2.0:
        cx = sum(v.xy(*p)[0] for p in E1) / 5 + 250; cy = sum(v.xy(*p)[1] for p in E1) / 5 - 110; s_ = .6 + .4 * eo((t - 2.0) / .25) + .08 * math.sin(min(1, (t - 2) / .5) * math.pi)
        def chipn(l, d): d.rounded_rectangle((cx - 140 * s_, cy - 48 * s_, cx + 140 * s_, cy + 48 * s_), 48 * s_, fill=GOLD, outline=WHITE, width=5); T(d, (cx, cy), 'נחסם', F(KB, int(64 * s_)), fill=NIGHT, sh=False)
        im.alpha_composite(alpha_layer(chipn, 1))
    headline_a(im, [('עם E1', GOLD), ('הרצף נחתך', WHITE)], 150, 84, eo(t / .4), hl=1 if t > 2.2 else None)
    lower_a(im, 'זה בולם את הרעיון\nשל הקמת מדינה פלסטינית', eo((t - .55 * D) / .4))
    corner_tag(ImageDraw.Draw(im), 'הגבולות להמחשה')
    shake = 10 * math.sin(t * 60) * max(0, 1 - abs(t - 1.8) / .25) if 1.55 < t < 2.05 else 0
    return im, shake
def house(d, x, y, s, col):
    d.polygon([(x, y - s * .55), (x - s * .55, y - s * .05), (x + s * .55, y - s * .05)], fill=col); d.rectangle((x - s * .4, y - s * .05, x + s * .4, y + s * .45), fill=col); d.rectangle((x - s * .1, y + s * .15, x + s * .1, y + s * .45), fill=NIGHT)
SM = Image.open(HERE + '/src/smotrich-cut.png').convert('RGBA'); SM = SM.resize((int(SM.width * 1150 / SM.height), 1150), Image.LANCZOS)
def s6(t, D):
    v = View(31.80, 35.28, 1.6 * (1 + .03 * t / D)); im = mapbase(v, .35)
    glow = Image.new('RGBA', (W, H)); gd = ImageDraw.Draw(glow); gd.ellipse((W - 760, 520, W + 100, 1420), fill=LT + (int(160 * eo(t / .6)),)); im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(90)))
    x = W - SM.width + 160 + int(500 * (1 - eo(t / .6))); im.alpha_composite(SM, (x, 420))
    fade = Image.new('RGBA', (W, H)); fd = ImageDraw.Draw(fade)
    for y in range(1250, H, 2): fd.rectangle((0, y, W, y + 2), fill=NIGHT + (int(240 * min(1, (y - 1250) / 300)),))
    im.alpha_composite(fade)
    headline_a(im, [('שר האוצר', LT), ('קידם את התוכנית', WHITE)], 170, 100, eo((t - .2) / .4), hl=1 if t > 1 else None)
    t0 = .5 * D; d = ImageDraw.Draw(im); n = int(28 * eo((t - t0) / 1.4))
    for k in range(n):
        r, c = divmod(k, 7); house(d, 90 + c * 62, 1400 + r * 70, 46, GOLD if (r + c) % 3 else (255, 230, 150))
    if t > t0:
        val = int(3401 * eo((t - t0) / 1.6)); im.alpha_composite(alpha_layer(lambda l, dd: (T(dd, (W - 80, 1440), f'⁦{val:,}⁩', F(SEC, 160), fill=GOLD, anchor='rm'), T(dd, (W - 80, 1570), 'יחידות דיור ב־E1', F(SEC, 56), anchor='rm')), eo((t - t0) / .3)))
    if t > .35 * D: im.alpha_composite(alpha_layer(lambda l, dd: chipbar(dd, 1690, [('אישור סופי · אוגוסט ⁦2025⁩', TEAL, WHITE)]), eo((t - .35 * D) / .3)))
    return im, None
def s7(t, D):
    im = mapbase(View(31.80, 35.28, 1.6), .5)
    c1 = cardc('jdn', 'jdn.jpg', None, 820, 4); c2 = cardc('a7', 'a7.jpg', (0, 120, 1320, 600), 900, -3)
    paste_scaled(im, c1, 60 + c1.width / 2, 360 + c1.height / 2, 1.25 - .25 * eo((t - .2) / .35), eo((t - .2) / .25))
    paste_scaled(im, c2, 40 + c2.width / 2, 1020 + c2.height / 2, 1.25 - .25 * eo((t - .9) / .35), eo((t - .9) / .25))
    headline_a(im, [('השבוע', GOLD), ('בכל הכותרות', WHITE)], 150, 96, eo(t / .4))
    if t > 1.6: im.alpha_composite(alpha_layer(lambda l, d: chip(d, W - 60, 1700, '⁦17.11.2026⁩', RED), eo((t - 1.6) / .3)))
    if t > .55 * D: im.alpha_composite(alpha_layer(lambda l, d: chipbar(d, 1800, [('⁦1,234⁩ דירות במכרז הראשון', GOLD, NIGHT)]), eo((t - .55 * D) / .3)))
    return im, None
AG = Image.open(HERE + '/src/a7.jpg').convert('RGB').crop((0, 1050, 1320, 1795)); AG = ImageOps.fit(AG, (W, 1000), Image.LANCZOS, centering=(.45, .3))
AGM = Image.new('L', (W, 1000), 255); _d = ImageDraw.Draw(AGM)
for y in range(700, 1000): _d.line((0, y, W, y), fill=int(255 * (1 - (y - 700) / 300)))
def s8(t, D):
    im = mapbase(View(31.80, 35.28, 1.6), .5); z = 1.0 + .05 * t / D
    ph = AG.resize((int(W * z), int(1000 * z))).crop((int(W * (z - 1) / 2), 0, int(W * (z - 1) / 2) + W, 1000))
    ph = Image.blend(Image.new('RGB', ph.size, NIGHT), ph, eo(t / .7)); im.paste(ph, (0, 300), AGM); d = ImageDraw.Draw(im)
    T(d, (W - 40, 1270), 'צילום: נעם מושקוביץ, דוברות הכנסת', F(RUB, 22), fill=PALE, anchor='rm', sh=False)
    im.alpha_composite(alpha_layer(lambda l, dd: T(dd, (W / 2, 170), 'ואז, היועמ״שית', F(KB, 110), fill=RED), eo((t - .1) / .4)))
    t1 = .35 * D; im.alpha_composite(alpha_layer(lambda l, dd: T(dd, (W / 2, 1370), 'הורתה לעצור את המכרז', F(KB, 88)), eo((t - t1) / .4)))
    t2 = .7 * D; im.alpha_composite(alpha_layer(lambda l, dd: T(dd, (W / 2, 1480), 'עד להקמת ממשלה חדשה', F(KB, 70), fill=RED), eo((t - t2) / .4)))
    if t > .15 * D: im.alpha_composite(alpha_layer(lambda l, dd: chip(dd, W / 2 + 280, 1620, 'יומיים לפני פתיחת המעטפות', TEAL, WHITE, 36), eo((t - .15 * D) / .3)))
    return im, None
HL = [(190, 625, 590, 690), (40, 700, 1290, 770), (740, 770, 1290, 840)]
def s9(t, D):
    im = mapbase(View(31.80, 35.28, 1.6), .55)
    ws = [eo((t - (.25 + k * .17) * D) / (.15 * D)) for k in range(3)]
    boxes = tuple((int(x1 - (x1 - x0) * w), y0, x1, y1) for (x0, y0, x1, y1), w in zip(HL, ws) if w > 0.01)
    c = cardc(('bg', boxes), 'clip-bagatz.jpg', None, 900, -2, hl=boxes)
    if len(CARD) > 40: CARD.clear()
    y = 560 + int(600 * (1 - eo(t / .5))); im.alpha_composite(c, ((W - c.width) // 2, y))
    headline_a(im, [('רק לפני חודש', GOLD), ('היא התחייבה בבג״ץ', WHITE)], 170, 96, eo((t - .2) / .4), hl=1 if t > .5 * D else None)
    lower_a(im, 'לאפשר לפתוח את המעטפות ב־⁦19⁩ בנובמבר.\nיומיים לפני, היא עצרה.', eo((t - .8 * D) / .4), 1640)
    return im, None
def s10(t, D):
    im = mapbase(View(31.80, 35.28, 1.6), .72); d = ImageDraw.Draw(im)
    rows = [('הממשלה אישרה', 0), ('התוכנית אושרה סופית', .18), ('התחייבה בבג״ץ', .36), ('ואז עצרה', .56)]
    y = 480
    for k, (txt, at) in enumerate(rows):
        a = eo((t - LEAD - at * VD[9]) / .3); col = RED if k == 3 else LT
        if a > 0:
            def row(l, dd, y=y, k=k, txt=txt, col=col):
                T(dd, (W - 110, y), txt, F(KB, 72), fill=WHITE if k < 3 else RED, anchor='rm'); dd.ellipse((90, y - 50, 190, y + 50), outline=col, width=8)
                if k < 3: dd.line((112, y, 135, y + 24, 170, y - 22), fill=col, width=10, joint='curve')
                else: dd.line((115, y - 25, 165, y + 25), fill=col, width=10); dd.line((115, y + 25, 165, y - 25), fill=col, width=10)
            s_ = 1 + .25 * (1 - a) if k == 3 else 1
            im.alpha_composite(alpha_layer(row, a))
        y += 210
    lower_a(im, 'החלטה של ממשלה נבחרת\nנעצרת בלי סמכות', eo((t - .8 * VD[9]) / .4), 1500)
    shake = 8 * math.sin(t * 60) * max(0, 1 - abs(t - LEAD - .56 * VD[9] - .1) / .2)
    return im, shake
def s11(t, D):
    v = View(31.79, 35.262, 1.25 * (1 + .06 * t / D)); im = mapbase(v, .35)
    for n in ('ירושלים', 'מעלה אדומים'): area_a(im, v, AREAS[n], BLUE, 1, 70)
    e1_glow(im, v, 1, .75 + .25 * math.sin(t * 4))
    headline_a(im, [('אנחנו נחושים', WHITE), ('לבנות ב־E1', GOLD)], 260, 128, eo((t - .2) / .5), rise=80)
    sub_a = eo((t - .5 * VD[10]) / .4)
    if sub_a > 0: im.alpha_composite(alpha_layer(lambda l, d: (T(d, (W / 2, 1560), 'כדי לחסל את רעיון', F(KB, 84)), T(d, (W / 2, 1670), 'המדינה הפלסטינית', F(KB, 84), fill=RED)), sub_a))
    return im, None
SHOTS = [s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11]
# ---------- render ----------
only = [int(a) for a in sys.argv[1:]] if len(sys.argv) > 1 else None
if only:   # preview stills
    for k in only:
        for frac in (.1, .5, .95):
            im, _ = SHOTS[k - 1](frac * D[k - 1], D[k - 1]); d = ImageDraw.Draw(im); ai_tag(d)
            fin(im).resize((OW, OH)).save(f'/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/p{k}_{frac}.jpg', quality=85)
    sys.exit()
TOT = sum(D); NF = int(TOT * FPS)
p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{OW}x{OH}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', HERE + '/v-silent.mp4'], stdin=subprocess.PIPE)
starts = np.cumsum([0] + D[:-1]); n = 0
for k, fn in enumerate(SHOTS):
    nf = int(round((starts[k] + D[k]) * FPS)) - n
    for i in range(nf):
        t = i / FPS; im, sh = fn(t, D[k]); d = ImageDraw.Draw(im); ai_tag(d); out = fin(im)
        if sh: out = out.transform(out.size, Image.AFFINE, (1, 0, -sh, 0, 1, 0), fillcolor=(4, 12, 14))
        tg = n / FPS
        if tg < .3: out = Image.blend(Image.new('RGB', out.size), out, tg / .3)
        if tg > TOT - .8: out = Image.blend(out, Image.new('RGB', out.size), min(1, (tg - (TOT - .8)) / .8))
        if k > 0 and i < 5: out = Image.blend(Image.new('RGB', out.size, (255, 255, 255)), out, .55 + .09 * i)   # flash cut
        p.stdin.write(out.resize((OW, OH), Image.BILINEAR).tobytes()); n += 1
    print('shot', k + 1, 'done', flush=True)
p.stdin.close(); p.wait()
# audio: VO at shot starts + bed (pad + pulse), ducked
ins, fl = [], []
for k, f in enumerate(VOF):
    ins += ['-i', f]; fl.append(f'[{k + 1}:a]aresample=48000,aformat=channel_layouts=stereo,adelay={int((starts[k] + LEAD) * 1000)}:all=1[v{k}]')
ins += ['-stream_loop', '-1', '-i', HERE + '/sfx/pad.wav', '-stream_loop', '-1', '-i', HERE + '/sfx/pulse.wav']
fl.append(''.join(f'[v{k}]' for k in range(11)) + 'amix=inputs=11:normalize=0,volume=1.0,asplit[vo][sc]')
fl.append(f'[12:a]atrim=0:{TOT:.2f},volume=0.22[pd]; [13:a]atrim=0:{TOT:.2f},highpass=f=60,volume=0.16[pl]; [pd][pl]amix=inputs=2:normalize=0,afade=t=in:d=1.5,afade=t=out:st={TOT - 1.8:.2f}:d=1.8[bed0]')
fl.append('[bed0][sc]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=350[bed]')
fl.append('[vo][bed]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', HERE + '/v-silent.mp4'] + ins + ['-filter_complex', ';'.join(fl), '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-t', f'{TOT:.2f}', HERE + '/rz-e1-explainer.mp4'], check=True)
os.remove(HERE + '/v-silent.mp4'); print('done', round(TOT, 1))
