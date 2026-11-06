"""Yesha Council story: warning about deliberate provocations in Judea and Samaria on election day (1080x1920)."""
import os
SRC = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/carousel2/make.py'
code = open(SRC).read(); exec(code[:code.index('# 1 — cover')])     # brand helpers
from PIL import Image, ImageDraw
OUT = os.path.dirname(os.path.abspath(__file__)); H = 1920
TOP = 230
KICK = 'מועצת יש״ע מתריעה'
HEAD = 'חשש לפרובוקציות מכוונות ביהודה ושומרון בניסיון להשפיע על הבחירות'
P1 = 'כבר משעות הבוקר המוקדמות הגיעו לאזור גוש שילה בבנימין עשרות פעילים זרים, מצוידים במצלמות, וקיים חשש כי ינסו לעורר עימותים מכוונים בשטח זה ובאזורים נוספים.'
P2 = 'במועצת יש״ע חוששים כי מטרת הפרובוקציות היא לייצר סערה תקשורתית, לגרור את ראש הממשלה להתייחסות פומבית ולהשפיע באמצעותה על השיח הציבורי ביום הבחירות.'
P3 = 'מועצת יש״ע קוראת למשטרה ולכוחות הביטחון למנוע פרובוקציות ולא לאפשר את הבערת השטח לצרכים פוליטיים.'

img = Image.new('RGB', (W * S, H * S)); d = ImageDraw.Draw(img)
for y in range(H * S):
    t = y / (H * S); d.line([(0, y), (W * S, y)], fill=tuple(int(DEEP[i] + (NAVY[i] - DEEP[i]) * t) for i in range(3)))
arcs(img, 980, 1980, alpha=36, n=4, r0=420, step=80, width=40)
d = ImageDraw.Draw(img)
lg = Image.open(OUT + '/../../clients/yesha/logo_white.png').convert('RGBA'); lg = lg.crop(lg.getchannel('A').getbbox())   # white logo on dark, no plate
lw = 210 * S; lg = lg.resize((lw, int(lw * lg.height / lg.width)), Image.LANCZOS); img.paste(lg, ((W - M) * S - lw, (TOP - 60) * S), lg)

def para(s, size, y, color, bold=False, lh=1.2, indent=0):
    for ln in wrap(d, s, size, W - 2 * M - indent, bold=bold):
        text(d, (W - M - indent, y), ln, size, color, bold=bold); y += size * lh
    return y

y = 470
tag(d, y, KICK, size=50, bg=LB)                                   # "warning" label
y += 118
y = para(HEAD, 104, y, WHITE, bold=True, lh=1.08)
y += 46
d.rectangle(P(W - M - 260, y, W - M, y + 6), fill=LB); y += 52
y = para(P1, 56, y, SOFT)
y += 28
y = para(P2, 56, y, SOFT)
y += 34
y2 = para(P3, 60, y, WHITE, bold=True, indent=34)
d.rectangle(P(W - M - 10, y + 8, W - M, y2 - 12), fill=LB)            # accent bar beside the call to action
img.resize((W, H), Image.LANCZOS).save(OUT + '/yesha-story-provocations.png'); print('end y', y2)
