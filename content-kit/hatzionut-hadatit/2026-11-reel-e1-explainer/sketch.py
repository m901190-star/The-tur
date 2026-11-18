"""E1 explainer reel: graphic-direction sketch frames (1080x1920), RZ palette, Haim headlines."""
import os, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
HERE = os.path.dirname(os.path.abspath(__file__))
KB = HERE + '/../../fonts/HaimClassicv2FM-Bold.ttf'
SEC = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/shalev/fonts/SecularOne.ttf'
RUB = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/fonts/Rubik-700.ttf'
W, H = 1080, 1920
DEEP, TEAL, LT, PALE, NIGHT = (43, 81, 85), (80, 146, 153), (105, 180, 189), (173, 213, 217), (16, 36, 40)
RED, GOLD, WHITE = (214, 58, 58), (240, 196, 80), (255, 255, 255)
def F(p, s): return ImageFont.truetype(p, s, layout_engine=ImageFont.Layout.RAQM)
def rtl(d, xy, t, f, fill=WHITE, anchor='mm', **k): d.text(xy, t, font=f, fill=fill, anchor=anchor, direction='rtl', **k)
def bg():
    im = Image.new('RGB', (W, H), NIGHT); d = ImageDraw.Draw(im)
    for y in range(H): d.line((0, y, W, y), fill=tuple(int(NIGHT[i] + (DEEP[i] - NIGHT[i]) * (1 - abs(y / H - .45) * 1.6)) for i in range(3)))
    for x in range(0, W, 60): d.line((x, 0, x, H), fill=(255, 255, 255, 0) if False else tuple(min(255, c + 6) for c in NIGHT), width=1)
    for y in range(0, H, 60): d.line((0, y, W, y), fill=tuple(min(255, c + 6) for c in NIGHT), width=1)
    return im
def tag(d):
    f = F(SEC, 26); t = 'איור סכמטי'; d.rounded_rectangle((40, H - 110, 220, H - 66), 22, fill=(0, 0, 0)); rtl(d, (130, H - 88), t, f, fill=PALE)
def sub(d, t, y=1640):
    f = F(RUB, 46); lines = t.split('\n')
    for k, l in enumerate(lines):
        tw = d.textlength(l, font=f, direction='rtl'); yy = y + k * 66
        d.rounded_rectangle((W / 2 - tw / 2 - 24, yy - 34, W / 2 + tw / 2 + 24, yy + 34), 14, fill=(0, 0, 0))
        rtl(d, (W / 2, yy), l, f)
# --- schematic geography (not to scale) ---
P = {'ירושלים': (420, 900), 'מעלה אדומים': (720, 880), 'רמאללה': (440, 430), 'בית לחם': (430, 1310)}
def city(d, name, r=26, col=WHITE, lab=True, side='r'):
    x, y = P[name]; d.ellipse((x - r, y - r, x + r, y + r), fill=col, outline=NIGHT, width=5)
    if lab:
        f = F(KB, 54); 
        if side == 'r': rtl(d, (x + r + 16, y), name, f, anchor='lm')
        elif side == 'l': rtl(d, (x - r - 16, y), name, f, anchor='rm')
        else: rtl(d, (x, y - r - 40), name, f)
def e1_zone(im, alpha=200, col=GOLD):
    lay = Image.new('RGBA', (W, H)); ld = ImageDraw.Draw(lay)
    ld.polygon([(500, 820), (700, 790), (735, 870), (690, 960), (520, 975), (470, 900)], fill=col + (alpha,), outline=WHITE + (255,))
    im.paste(Image.alpha_composite(im.convert('RGBA'), lay).convert('RGB'))
def arrow(d, pts, col, w=18, head=True):
    d.line(pts, fill=col, width=w, joint='curve')
    if head:
        (x0, y0), (x1, y1) = pts[-2], pts[-1]; a = math.atan2(y1 - y0, x1 - x0); L = 46
        d.polygon([(x1 + 10 * math.cos(a), y1 + 10 * math.sin(a)), (x1 - L * math.cos(a - .5), y1 - L * math.sin(a - .5)), (x1 - L * math.cos(a + .5), y1 - L * math.sin(a + .5))], fill=col)
import re
def hf(t, s): return F(SEC, int(s * .9)) if re.search(r'[A-Za-z0-9]', t) else F(KB, s)   # Haim: no Latin, 0 reads like ם
def title(d, t, y=210, s=110, col=WHITE):
    for k, l in enumerate(t.split('\n')): rtl(d, (W / 2, y + k * (s + 10)), l, hf(l, s), fill=col)
def logo_area(d): pass  # client logo optional; RZ posts have no party logo unless asked
frames = []
# 1 hook
im = bg(); d = ImageDraw.Draw(im)
rtl(d, (W / 2, 700), 'E1', F(SEC, 420), fill=GOLD)
title(d, 'מה זה בכלל,\nולמה כולם נלחמים עליו?', 1080, 92)
sub(d, 'הסבר ב־⁦60⁩ שניות'); frames.append(('01-hook', im))
# 2 map: where
im = bg(); d = ImageDraw.Draw(im)
d.line((P['ירושלים'], P['מעלה אדומים']), fill=(120, 140, 140), width=6)
e1_zone(im); d = ImageDraw.Draw(im)
for n, s in [('ירושלים', 'l'), ('מעלה אדומים', 'r')]: city(d, n, side=s)
rtl(d, (600, 890), 'E1', F(SEC, 70), fill=NIGHT, anchor='mm')
title(d, 'שטח פתוח בין\nירושלים למעלה אדומים', 230, 90)
sub(d, 'בנייה ב־E1 מחברת את מעלה אדומים\nלירושלים ברצף אחד'); tag(d); frames.append(('02-map-where', im))
# 3 map: the palestinian contiguity
im = bg(); d = ImageDraw.Draw(im)
arrow(d, [(470, 470), (650, 620), (640, 900), (560, 1150), (460, 1280)], RED + (), 22)
for n, s in [('ירושלים', 'l'), ('מעלה אדומים', 'r'), ('רמאללה', 'l'), ('בית לחם', 'l')]: city(d, n, r=22, side=s)
title(d, 'בלי E1:', 200, 110, RED)
rtl(d, (W / 2, 330), 'רצף פלסטיני מרמאללה עד בית לחם', F(KB, 58))
sub(d, 'בדיוק הרצף שמדינה פלסטינית\nצריכה כדי לקום'); tag(d); frames.append(('03-map-without', im))
# 4 map: blocked
im = bg(); d = ImageDraw.Draw(im)
arrow(d, [(470, 470), (650, 620), (640, 790)], RED, 22, head=False)
arrow(d, [(640, 990), (560, 1150), (460, 1280)], RED, 22, head=False)
e1_zone(im, 235); d = ImageDraw.Draw(im)
for n, s in [('ירושלים', 'l'), ('מעלה אדומים', 'r'), ('רמאללה', 'l'), ('בית לחם', 'l')]: city(d, n, r=22, side=s)
cx, cy = 600, 890; d.ellipse((cx - 120, cy - 120, cx + 120, cy + 120), outline=RED, width=16); d.line((cx - 85, cy - 85, cx + 85, cy + 85), fill=RED, width=16)
title(d, 'עם E1:', 200, 110, GOLD)
rtl(d, (W / 2, 330), 'הרצף נחסם', F(KB, 74))
sub(d, 'לכן קוראים לזה "בולם":\nזה בולם את המדינה הפלסטינית'); tag(d); frames.append(('04-map-blocked', im))
# 5 numbers / timeline
im = bg(); d = ImageDraw.Draw(im)
title(d, 'איפה זה עומד?', 220, 110)
rows = [('אישור סופי לתוכנית', 'אוגוסט \u20662025\u2069', '\u20663,401\u2069 יח״ד', LT), ('מכרז ראשון', 'פתיחת המעטפות נקבעה ל־\u206619.11\u2069', '\u20661,234\u2069 דירות', LT), ('היועמ״שית: לעצור', '\u206617.11.2026\u2069 · עד ממשלה חדשה', 'נעצר', RED)]
y = 520
for k, (what, dt, num, col) in enumerate(rows):
    d.rounded_rectangle((90, y, W - 90, y + 250), 30, fill=(0, 0, 0), outline=col, width=5)
    rtl(d, (W - 140, y + 75), what, F(KB, 62), anchor='rm')
    rtl(d, (W - 140, y + 175), dt, F(RUB, 38), fill=PALE, anchor='rm')
    rtl(d, (140, y + 75), num, F(SEC, 50), fill=GOLD if col == LT else RED, anchor='lm')
    y += 310
sub(d, 'המכרז נעצר יומיים לפני פתיחת המעטפות', 1600); frames.append(('05-timeline', im))
# 6 the AG decision + sanctions
im = bg(); d = ImageDraw.Draw(im)
title(d, 'באותו שבוע', 230, 100)
for k, (nm, col) in enumerate([('בריטניה', (200, 30, 50)), ('אוסטרליה', (20, 50, 120))]):
    x = 300 + k * 480; d.rounded_rectangle((x - 200, 420, x + 200, 640), 24, fill=col); rtl(d, (x, 530), nm, F(KB, 68))
rtl(d, (W / 2, 720), 'סנקציות על מתיישבים וחברות בנייה', F(RUB, 44), fill=PALE)
d.rounded_rectangle((120, 860, W - 120, 1260), 30, fill=(0, 0, 0), outline=RED, width=6)
rtl(d, (W / 2, 960), 'היועמ״שית', F(KB, 90))
rtl(d, (W / 2, 1080), 'עוצרת את הבנייה ב־E1', F(SEC, 66), fill=RED)
rtl(d, (W / 2, 1180), 'עד להקמת ממשלה חדשה', F(RUB, 40), fill=PALE)
sub(d, '"היא משדרת להן מסר ברור:\nזו הדרך לעצור את הבנייה"', 1560); frames.append(('06-ag-sanctions', im))
# 7 quote card with photo
im = bg(); ph = Image.open(HERE + '/../2026-11-reel-game-team/refs/face2.jpg').convert('RGB'); ph = ImageOps.fit(ph, (W, 1150), Image.LANCZOS, centering=(.5, .3))
im.paste(ph, (0, 0)); fade = Image.new('L', (W, 1150), 0); fd = ImageDraw.Draw(fade)
for y in range(1150): fd.line((0, y, W, y), fill=int(255 * max(0, (y - 650) / 500)))
im.paste(Image.new('RGB', (W, 1150), NIGHT), (0, 0), fade); d = ImageDraw.Draw(im)
rtl(d, (W / 2, 1220), '"היא לא מייצגת', F(KB, 110)); rtl(d, (W / 2, 1350), 'את מדינת ישראל"', F(KB, 110))
rtl(d, (W / 2, 1500), 'בצלאל סמוטריץ׳, שר האוצר', F(RUB, 42), fill=LT); frames.append(('07-quote', im))
# 8 end
im = bg(); d = ImageDraw.Draw(im)
title(d, 'אנחנו נחושים', 760, 130); title(d, 'לבנות ב־E1', 910, 150, GOLD)
rtl(d, (W / 2, 1120), 'ולחסל את רעיון המדינה הפלסטינית', F(RUB, 48), fill=PALE); frames.append(('08-end', im))
os.makedirs(HERE + '/sketch', exist_ok=True)
for n, im in frames: im.save(HERE + f'/sketch/{n}.jpg', quality=90)
fw, fh, g = 300, 533, 16; cols = 4; rows_ = 2
sheet = Image.new('RGB', (cols * (fw + g) + g, rows_ * (fh + 60) + g), (10, 12, 14)); sd = ImageDraw.Draw(sheet)
for i, (n, im) in enumerate(frames):
    c, r = i % cols, i // cols; x = sheet.width - g - (c + 1) * (fw + g) + g; y = g + r * (fh + 60)
    sheet.paste(im.resize((fw, fh)), (x, y)); sd.text((x + fw / 2, y + fh + 28), str(i + 1), font=F(SEC, 30), fill=WHITE, anchor='mm')
sheet.save(HERE + '/sketch-sheet.jpg', quality=90); print('ok')
