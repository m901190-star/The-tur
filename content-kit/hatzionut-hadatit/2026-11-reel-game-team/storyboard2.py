"""Detailed shot storyboard: 3 frames per shot (start/mid/end) simulating camera moves + HUD timing."""
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageOps
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from hud import hud
G = HERE + '/gen/'; T = HERE + '/sb/'
RUB = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/fonts/Rubik-700.ttf'
RUBR = RUB
def F(s): return ImageFont.truetype(RUB, s, layout_engine=ImageFont.Layout.RAQM)
def crop(src, z, cx=.5, cy=.5, dark=0):
    im = ImageOps.fit(Image.open(src).convert('RGB'), (1080, 1920), Image.LANCZOS)
    w, h = 1080 / z, 1920 / z; x0 = min(max(cx * 1080 - w / 2, 0), 1080 - w); y0 = min(max(cy * 1920 - h / 2, 0), 1920 - h)
    im = im.crop((x0, y0, x0 + w, y0 + h)).resize((1080, 1920), Image.LANCZOS)
    if dark: im = Image.blend(im, Image.new('RGB', im.size, 'black'), dark)
    return im
def sel(name, z, fill, show_name, dark=0):
    p = T + name + '_src.png'; crop(G + 'c-select.png', z, .5, .3, dark).save(p)
    src = open(HERE + '/select.py').read().replace("HERE + '/gen/c-select.png'", repr(p)).replace("HERE + '/sketch4-select.jpg'", repr(T + name + '.jpg'))
    src = src.replace("[('כלכלה', 1.0), ('התיישבות', 1.0), ('עמידות', .95)]", repr([('כלכלה', fill), ('התיישבות', fill), ('עמידות', fill * .95)]))
    if not show_name: src = src.replace("d.text((R, 1440), 'בצלאל", "0 and d.text((R, 1440), 'בצלאל")
    exec(compile(src, 'select', 'exec'), {'__file__': HERE + '/select.py'})
    return T + name + '.jpg'
def hf(name, src, z, cx, cy, mission, sub=None):
    p = T + name + '_src.png'; crop(G + src, z, cx, cy).save(p); hud(p, T + name + '.jpg', mission, sub); return T + name + '.jpg'
M1 = 'כלכלה חזקה במלחמה בשבע חזיתות'; M3 = 'למעלה מ־⁦100⁩ יישובים'; M4 = 'למעלה מ־⁦140⁩ חוות'
SHOTS = [
 ('0:00–0:03', 'בחר דמות', 'המוזיקה נכנסת. מצלמה מתקרבת לאט לפנים, השם קופץ, והמדדים מתמלאים בצהוב אחד-אחד על הביט.',
  [sel('1a', 1.0, 0, False, .35), sel('1b', 1.08, .5, True), sel('1c', 1.15, 1.0, True)]),
 ('0:03–0:08', 'משימה 1 · כלכלה', 'הולך במסדרון הבורסה, המצלמה עוקבת מאחור. הגרפים במסכים מטפסים. תיבת המשימה נכנסת מימין.',
  [hf('2a', 'c-scene1.png', 1.0, .5, .5, None), hf('2b', 'c-scene1.png', 1.12, .5, .45, M1), hf('2c', 'c-scene1.png', 1.25, .5, .4, M1)]),
 ('0:08–0:13', 'משימה 2 · מרכיבי ביטחון', 'נפתח בתקריב עליו נוהג (פנים גדולות). המצלמה נסוגה ורואים את הרייזר דוהר על דרך העפר לאורך גדר התיל והמצלמות.',
  [hf('3a', 'c-scene2-cu.png', 1.2, .45, .38, None), hf('3b', 'c-scene2-cu.png', 1.0, .5, .5, 'מרכיבי ביטחון'), hf('3c', 'c-scene2.png', 1.0, .5, .5, 'מרכיבי ביטחון')]),
 ('0:13–0:18', 'מנוף מניח קרוואן', 'הוא עומד על הגבעה. המנוף מוריד את הקרוואן לאט עד שנוחת על הקרקע, אבק קל. המצלמה מתקרבת לקרוואן.',
  [hf('4a', 'c-scene3.png', 1.0, .5, .5, M3, 'הניחו את הקרוואן'), hf('4b', 'c-scene3.png', 1.12, .6, .35, M3, 'הניחו את הקרוואן'), hf('4c', 'c-scene3.png', 1.25, .65, .3, M3, 'הניחו את הקרוואן')]),
 ('0:18–0:23', 'משימה 3 · חוות', 'נשען על הגדר מול הכבשים בשקיעה. המצלמה מתרחקת לאט ומראה את הנוף. בסוף כהה לשחור.',
  [hf('5a', 'c-scene4.png', 1.2, .5, .45, M4), hf('5b', 'c-scene4.png', 1.08, .5, .45, M4), hf('5c', 'c-scene4.png', 1.0, .5, .5, M4)]),
]
fw, fh, gap = 300, 533, 14; tw = 520; rh = fh + 60
W = tw + 3 * (fw + gap) + 60; H = 120 + len(SHOTS) * rh + 70
sheet = Image.new('RGB', (W, H), (18, 20, 24)); d = ImageDraw.Draw(sheet)
d.text((W - 30, 40), 'רילס משחק · בצלאל סמוטריץ׳ · סקיצה מפורטת (כ־23 שניות)', font=F(40), fill='white', anchor='ra', direction='rtl')
d.text((W - 30, 92), 'כל שורה = שוט. בכל שורה: התחלה, אמצע וסוף (מימין לשמאל). החיתוכים על מעברי המוזיקה (כל 5 שניות).', font=F(24), fill=(170, 170, 170), anchor='ra', direction='rtl')
import textwrap
for i, (t, title, desc, frames) in enumerate(SHOTS):
    y = 130 + i * rh
    tx = W - 30
    d.ellipse((tx - 54, y + 4, tx - 4, y + 54), fill=(214, 40, 40)); d.text((tx - 29, y + 29), str(i + 1), font=F(30), fill='white', anchor='mm')
    d.text((tx - 70, y + 10), title, font=F(34), fill='white', anchor='ra', direction='rtl')
    d.text((tx - 70, y + 58), '⁦' + t + '⁩', font=F(28), fill=(105, 180, 189), anchor='ra')
    words = desc.split(); lines = []; cur = ''
    for w_ in words:
        if d.textlength(cur + ' ' + w_, font=F(25), direction='rtl') > tw - 40: lines.append(cur); cur = w_
        else: cur = (cur + ' ' + w_).strip()
    lines.append(cur)
    for k, ln in enumerate(lines): d.text((tx, y + 120 + k * 38), ln, font=F(25), fill=(220, 220, 220), anchor='ra', direction='rtl')
    for j, f in enumerate(frames):
        x = W - tw - 30 - (j + 1) * (fw + gap)
        sheet.paste(Image.open(f).convert('RGB').resize((fw, fh)), (x, y))
        d.text((x + fw / 2, y + fh + 24), ['התחלה', 'אמצע', 'סוף'][j], font=F(22), fill=(150, 150, 150), anchor='mm', direction='rtl')
d.text((W / 2, H - 40), 'מוזיקה: הטראק ששלחת, מהשנייה ה־2.5 · בלי אפקטים קוליים · תג "נוצר ב-AI" לאורך כל הסרטון', font=F(24), fill=(170, 170, 170), anchor='mm', direction='rtl')
sheet.save(HERE + '/storyboard-detailed.jpg', quality=90); print(sheet.size)
