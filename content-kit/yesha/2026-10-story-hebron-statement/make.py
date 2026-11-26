"""Yesha Council story: statement on the Hebron operation (1080x1920)."""
import os
SRC = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/carousel2/make.py'
code = open(SRC).read(); exec(code[:code.index('# 1 — cover')])     # brand helpers
from PIL import Image, ImageDraw
OUT = os.path.dirname(os.path.abspath(__file__)); H = 1920
TOP = 230

P1 = 'אנחנו מברכים את ראש הממשלה ושר הביטחון על ההחלטה לצאת למבצע בחברון ומחזקים את ידי צה״ל וכוחות הביטחון שפועלים בשטח. מול תשתיות הטרור ואמצעי הלחימה הרבים ביהודה ושומרון נדרשת פעילות התקפית, נחושה ומתמשכת.'
P2 = 'אסור להסתפק בתגובה לפיגועים, צריך לגדוע את הטרור מהשורש ולפרק את תשתיותיו.'
P3 = 'מדינת ישראל חייבת לפרק את הרשות הפלסטינית, להשתלט על השטחים השולטים על מדינת ישראל המצויים בשטחי A ו-B ולהשיב לידיה את השליטה המלאה בשטח. זו הדרך היחידה להבטיח את ביטחון ישראל.'

img = Image.new('RGB', (W * S, H * S)); d = ImageDraw.Draw(img)
for y in range(H * S):
    t = y / (H * S); d.line([(0, y), (W * S, y)], fill=tuple(int(DEEP[i] + (NAVY[i] - DEEP[i]) * t) for i in range(3)))
arcs(img, 980, 1980, alpha=36, n=4, r0=420, step=80, width=40)
d = ImageDraw.Draw(img)
logo(img, 190, W - M, TOP - 20, plate=True)

def para(s, size, y, color, bold=False, lh=1.18, indent=0):
    for ln in wrap(d, s, size, W - 2 * M - indent, bold=bold):
        text(d, (W - M - indent, y), ln, size, color, bold=bold); y += size * lh
    return y

Y0 = 660
y = Y0
y = para(P1, 66, y, SOFT)
y += 34
y2 = para(P2, 72, y, WHITE, bold=True, indent=34)
d.rectangle(P(W - M - 10, y + 8, W - M, y2 - 12), fill=LB)            # accent bar beside the key line
y = para(P3, 66, y2 + 34, SOFT)
img.resize((W, H), Image.LANCZOS).save(OUT + '/yesha-story-hebron.png'); print('end y', y)
