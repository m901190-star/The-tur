"""E1 explainer: animation storyboard (start/end state per shot) + VO line + timing. Local render only."""
import os, math
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(HERE + '/sketch3.py').read(); exec(src[:src.index('OUT = []')])
VO = [l.split('|')[3].strip() for l in open(HERE + '/script-v3.md').read().splitlines() if l.startswith('| ') and l.split('|')[1].strip().isdigit()]
def corr_arrow(im, v, pts):
    P = path(im, v, pts, RED + (255,), 16); d = ImageDraw.Draw(im)
    (xa, ya), (xb, yb) = P[-2], P[-1]; a = math.atan2(yb - ya, xb - xa); L = 54
    d.polygon([(xb + 12 * math.cos(a), yb + 12 * math.sin(a)), (xb - L * math.cos(a - .5), yb - L * math.sin(a - .5)), (xb - L * math.cos(a + .5), yb - L * math.sin(a + .5))], fill=RED)
def cities(d, v, items, size=46):
    for n, s in items: label(d, v, *PL[n], n, s, size)
S = []
# 1
v = View(31.80, 35.27, 1.25)
im = mapbase(v, .6); d = ImageDraw.Draw(im); T(d, (W / 2, 820), 'E1', F(SEC, 300), fill=GOLD); a = finish(im)
im = mapbase(v, .45); d = ImageDraw.Draw(im); T(d, (W / 2, 620), 'E1', F(SEC, 380), fill=GOLD)
headline(d, [('מה זה בכלל?', WHITE), ('ולמה כולם', WHITE), ('נלחמים עליו', WHITE)], 950, 112, hl=2); S.append((a, finish(im), 'E1 נכנס בזום, השאלה מופיעה מילה-מילה'))
# 2
v = View(31.80, 35.31, .78); a = finish(mapbase(v, .05), .4)
im = mapbase(v, .05); d = ImageDraw.Draw(im); path(im, v, ROUTE1, (240, 240, 240, 230), 6, glow=False); d = ImageDraw.Draw(im)
cities(d, v, [('רמאללה', 'r'), ('ירושלים', 'b'), ('בית לחם', 'r'), ('מעלה אדומים', 'b')])
headline(d, [('ירושלים', WHITE), ('ומה שממזרח לה', LT)], 170, 92); S.append((a, finish(im, .4), 'המפה נחשפת, השמות קופצים, כביש 1 מצטייר'))
# 3
v1 = View(31.79, 35.27, 1.1); im = mapbase(v1); d = ImageDraw.Draw(im); path(im, v1, ROUTE1, (240, 240, 240, 230), 6, glow=False); d = ImageDraw.Draw(im)
cities(d, v1, [('ירושלים', 'b'), ('מעלה אדומים', 'b')]); a = finish(im, .35)
v = View(31.787, 35.262, 1.75); im = mapbase(v); d = ImageDraw.Draw(im)
path(im, v, ROUTE1, (240, 240, 240, 230), 8, glow=False); poly(im, v, E1, GOLD + (150,), WHITE, 6); d = ImageDraw.Draw(im)
cx = sum(v.xy(*p)[0] for p in E1) / 5; cy = sum(v.xy(*p)[1] for p in E1) / 5; T(d, (cx, cy), 'E1', F(SEC, 110), fill=NIGHT, sh=False)
cities(d, v, [('ירושלים', 'b'), ('הר הצופים', 'top')], 46); label(d, v, *PL['מעלה אדומים'], 'מעלה אדומים', 'b', 50, dx=-90)
headline(d, [('השטח הריק בין ירושלים', WHITE), ('למעלה אדומים', GOLD)], 180, 84); S.append((a, finish(im, .35), 'זום פנימה, השטח של E1 נצבע בזהב'))
# 4
v = View(31.80, 35.25, .78)
im = mapbase(v, .15); corr_arrow(im, v, CORR[:3]); d = ImageDraw.Draw(im); cities(d, v, [('רמאללה', 'l'), ('ירושלים', 'l'), ('בית לחם', 'l'), ('מעלה אדומים', 'b')])
headline(d, [('בלי E1', RED)], 150, 84); a = finish(im, .35)
im = mapbase(v, .15); corr_arrow(im, v, CORR); d = ImageDraw.Draw(im); cities(d, v, [('רמאללה', 'l'), ('ירושלים', 'l'), ('בית לחם', 'l'), ('מעלה אדומים', 'b')])
headline(d, [('בלי E1', RED), ('רצף פלסטיני', WHITE)], 150, 84); S.append((a, finish(im, .35), 'חץ אדום נמתח מרמאללה עד בית לחם'))
# 5
im = mapbase(v, .15); path(im, v, CORR, RED + (255,), 16); poly(im, v, E1, GOLD + (230,), WHITE, 6); d = ImageDraw.Draw(im)
cities(d, v, [('רמאללה', 'l'), ('ירושלים', 'l'), ('בית לחם', 'l'), ('מעלה אדומים', 'b')]); headline(d, [('עם E1', GOLD)], 150, 84); a = finish(im, .35)
im = mapbase(v, .15); path(im, v, CORR[:3], RED + (255,), 16); path(im, v, CORR[4:], RED + (255,), 16); poly(im, v, E1, GOLD + (230,), WHITE, 6); d = ImageDraw.Draw(im)
cx = sum(v.xy(*p)[0] for p in E1) / 5; cy = sum(v.xy(*p)[1] for p in E1) / 5
d.rounded_rectangle((cx - 150, cy - 46, cx + 150, cy + 46), 46, fill=NIGHT, outline=GOLD, width=5); T(d, (cx, cy), 'נחסם', F(KB, 64), fill=GOLD, sh=False)
cities(d, v, [('רמאללה', 'l'), ('ירושלים', 'l'), ('בית לחם', 'l'), ('מעלה אדומים', 'b')]); headline(d, [('עם E1', GOLD), ('הרצף נחתך', WHITE)], 150, 84, hl=1)
S.append((a, finish(im, .35), 'E1 "נוחת" על החץ, החץ נקטע ברעידה'))
# 6, 7, 8, 9, 10, 11 from the sketch3 frames (end states) + simple start states
sk = lambda n: Image.open(HERE + f'/sketch3/{n}.jpg').convert('RGB')
def dim(img, k=.55): return Image.blend(img, Image.new('RGB', img.size, NIGHT), k)
im = mapbase(View(31.80, 35.28, 1.6), .55); s_ = Image.open(HERE + '/src/smotrich-cut.png').convert('RGBA'); s_ = s_.resize((int(s_.width * 1260 / s_.height), 1260)); im.alpha_composite(s_, (W - s_.width + 420, H - s_.height - 60))
S.append((finish(im, .3), sk('06-smotrich'), 'התמונה נכנסת מימין, המספר 3,401 רץ מ-0'))
im = mapbase(View(31.80, 35.28, 1.6), .55); im.alpha_composite(card('jdn.jpg', None, 820, 4), (60, 360)); S.append((finish(im, .3), sk('07-news'), 'הכתבות נופלות על המפה אחת אחרי השנייה'))
S.append((dim(sk('08-ag'), .35), sk('08-ag'), 'התמונה מתבהרת, הטקסט נכתב, התגים קופצים'))
im = mapbase(View(31.80, 35.28, 1.6), .6); c = card('clip-bagatz.jpg', None, 900, -2); im.alpha_composite(c, ((W - c.width) // 2, 560)); S.append((finish(im, .3), sk('09-bagatz'), 'הכתבה נכנסת, הסימון הצהוב נמרח על המשפט'))
S.append((dim(sk('10-why'), .0), sk('10-why'), 'וי אחרי וי על הביט, ואז ה-X האדום'))
S.append((dim(sk('11-end'), .5), sk('11-end'), 'E1 זוהר, הכותרת עולה, סיום'))
# timing from word count (Harrison ≈ 2.3 words/s) + small pads
t = 0.0; rows = []
for k, (a, b, act) in enumerate(S):
    dur = max(2.5, len(VO[k].split()) / 2.3 + .4); rows.append((t, t + dur, a, b, act, VO[k])); t += dur
fw, fh, g, tw = 270, 480, 14, 600; rh = fh + 50
for part, sl in [(1, rows[:6]), (2, rows[6:])]:
    Wd = tw + 2 * (fw + g) + 60; Hd = 110 + len(sl) * rh + 30
    sh = Image.new('RGB', (Wd, Hd), (10, 12, 14)); d = ImageDraw.Draw(sh)
    T(d, (Wd - 30, 50), f'E1 · סטוריבורד ({part}/2) · קריין: הריסון · ~{int(round(t))} שניות', F(RUB, 34), anchor='rm', sh=False)
    for i, (t0, t1, a, b, act, vo) in enumerate(sl):
        y = 100 + i * rh; k = rows.index((t0, t1, a, b, act, vo)) + 1; x = Wd - 30
        d.ellipse((x - 50, y, x, y + 50), fill=RED); T(d, (x - 25, y + 25), str(k), F(SEC, 28), sh=False)
        T(d, (x - 66, y + 25), f'⁦{int(t0)}–{int(round(t1))}s⁩', F(SEC, 30), fill=LT, anchor='rm', sh=False)
        words = vo.split(); lines = []; cur = ''
        for w_ in words:
            if d.textlength(cur + ' ' + w_, font=F(RUB, 27), direction='rtl') > tw - 50: lines.append(cur); cur = w_
            else: cur = (cur + ' ' + w_).strip()
        lines.append(cur)
        for j, ln in enumerate(lines): T(d, (x, y + 104 + j * 38), ln, F(RUB, 27), fill=WHITE, anchor='rm', sh=False)
        T(d, (x, y + 70), 'קריינות:', F(RUB, 22), fill=(150, 150, 150), anchor='rm', sh=False)
        T(d, (x, y + 120 + len(lines) * 38), 'תנועה: ' + act, F(RUB, 23), fill=GOLD, anchor='rm', sh=False)
        for j, img in enumerate((a, b)):
            xx = Wd - tw - 30 - (j + 1) * (fw + g); sh.paste(img.resize((fw, fh)), (xx, y))
            T(d, (xx + fw / 2, y + fh + 20), ['התחלה', 'סוף'][j], F(RUB, 20), fill=(150, 150, 150), sh=False)
    sh.save(HERE + f'/storyboard-{part}.jpg', quality=88)
print(round(t, 1))
