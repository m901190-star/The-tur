"""Yesha Council story: chair's statement after the attack (3 frames, 1080x1920)."""
import os
SRC = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/carousel2/make.py'
code = open(SRC).read()
exec(code[:code.index('# 1 — cover')])           # reuse the carousel's brand helpers
from PIL import Image, ImageDraw
OUT = os.path.dirname(os.path.abspath(__file__))
H = 1920                                          # story format
PHOTO = '/root/.claude/uploads/1a5819ee-0cc0-5045-b086-4a8a80216453/14cbb170-image.jpg'
NAME = 'ישראל גנץ'
ROLE = 'ראש המועצה האזורית בנימין ויו״ר מועצת יש״ע'
TOP, BOTTOM = 230, 1640                           # Instagram story safe area


def dark_canvas():
    img = Image.new('RGB', (W * S, H * S)); d = ImageDraw.Draw(img)
    for y in range(H * S):
        t = y / (H * S)
        d.line([(0, y), (W * S, y)], fill=tuple(int(DEEP[i] + (NAVY[i] - DEEP[i]) * t) for i in range(3)))
    return img


def quote_lines(d, s, size, y, color=WHITE, lh=1.12, width=W - 2 * M):
    for ln in wrap(d, s, size, width, bold=True):
        text(d, (W - M, y), ln, size, color, shadow=(5, 5, DEEP)); y += size * lh
    return y


def signature(d, y):
    d.rectangle(P(W - M - 90, y, W - M, y + 8), fill=LB)
    text(d, (W - M, y + 30), NAME, 64, WHITE)
    text(d, (W - M, y + 108), ROLE, 38, SOFT, bold=False)


def frame_dots(d, n):
    for i in range(3):
        x = W / 2 + (1 - i) * 34
        d.ellipse(P(x - 8, BOTTOM + 40, x + 8, BOTTOM + 56), fill=WHITE if i == n - 1 else (0x4A, 0x6E, 0x94))


def save(img, n):
    img.resize((W, H), Image.LANCZOS).save(os.path.join(OUT, f'story-0{n}.png'))


# 1 — photo + key line
def f1():
    img = Image.open(PHOTO).convert('RGB').resize((W * S, H * S), Image.LANCZOS)   # photo is exactly 9:16
    ov = Image.new('RGBA', img.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    for y in range(H * S):
        t = y / (H * S)
        a = int(150 * max(0, 1 - t / 0.2)) + int(250 * min(1, max(0, (t - 0.40) / 0.22)) ** 1.2)
        od.line([(0, y), (W * S, y)], fill=DEEP + (min(a, 238),))
    img.paste(ov, (0, 0), ov)
    d = ImageDraw.Draw(img)
    logo(img, 200, W - M, TOP, plate=True)
    y = quote_lines(d, '״זה לא מחבל בודד ולא פיגוע נקודתי, אלא איום רחב שהולך ומתעצם ועלול להסתיים באסון כבד.״', 92, 1080)
    signature(d, y + 30)
    frame_dots(d, 1)
    save(img, 1)


# 2 — the number he cited
def f2():
    img = dark_canvas(); arcs(img, 980, 1900, alpha=40, n=4, r0=420, step=80, width=40)
    d = ImageDraw.Draw(img)
    logo(img, 200, W - M, TOP, plate=True)
    tag(d, 560, 'רק בשלושים הימים האחרונים', 50, bg=BLUE)
    text(d, (W - M, 650), '197', 480, WHITE, rtl=False, shadow=(14, 14, BLUE))
    text(d, (W - M, 1150), 'אירועי טרור ותקיפות', 112, LB, shadow=(5, 5, DEEP))
    text(d, (W - M, 1275), 'ביהודה ושומרון', 112, LB, shadow=(5, 5, DEEP))
    y = 1410
    for ln in wrap(d, 'בהם פיגועי אבנים, דריסה, תקיפות רועים יהודים וחסימות צירים.', 46, W - 2 * M):
        text(d, (W - M, y), ln, 50, SOFT, bold=False); y += 64
    frame_dots(d, 2)
    save(img, 2)


# 3 — the demand
def f3():
    img = dark_canvas(); arcs(img, 120, 1900, alpha=40, n=4, r0=420, step=80, width=40)
    d = ImageDraw.Draw(img)
    logo(img, 200, W - M, TOP, plate=True)
    text(d, (W - M, 400), '״', 280, LB, shadow=(6, 6, DEEP))
    y = quote_lines(d, 'אסור לנו לחזור על הטעות שקדמה לשבעה באוקטובר.', 104, 630, color=LB)
    y = quote_lines(d, 'כדי למנוע שבעה באוקטובר נוסף, מדינת ישראל חייבת לפרק את הרשות הפלסטינית ולהשיב לידיה את השליטה בשטח באופן מלא עד לחיסול הטרור.״', 80, y + 40)
    signature(d, y + 50)
    frame_dots(d, 3)
    save(img, 3)


for f in (f1, f2, f3):
    f()
sheet = Image.new('RGB', (372 * 3, 660), WHITE)
for k in range(3):
    sheet.paste(Image.open(os.path.join(OUT, f'story-0{k + 1}.png')).resize((360, 640)), (k * 372, 0))
sheet.save(os.path.join(OUT, 'sheet.png'))
print('done')
