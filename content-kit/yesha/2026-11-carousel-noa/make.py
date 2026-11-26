"""Yesha carousel 'נעה' (dating-profile concept), story-text style: full-bleed photo, centered white text with black outline + colour emoji. 1080x1350."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
HERE = os.path.dirname(os.path.abspath(__file__)); P = HERE + '/photos/'
RUB = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/fonts/Rubik-700.ttf'
EMO = '/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'
W, H = 1080, 1350
SLIDES = [  # photo, crop box (None=centre), lines [(text, emoji)], y-centre
    ('01.jpg', (320, 0, 1280, 1200), [('היי, אני נעה.', ''), ('נעים להכיר', '🤩')], .42),
    ('02.jpg', None, [('גיל: צעירה מאוד.', ''), ('מבט: ממש רחוק', '☁️')], .38),
    ('04.jpg', None, [('מחפשת:', ''), ('משפחות רציניות בלבד', '🇮🇱')], .40),
    ('07.jpg', None, [('אל תדאגו,', ''), ('אני לא קשה להשגה', '💁')], .36),
    ('08.jpg', 'aerial', [('מהזווית הזאת', ''), ('אני הכי פוטוגנית', '📸')], .20),
    ('05.jpg', None, [('יש לי כלב.', ''), ('בעצם… כמה', '🐶')], .30),
    ('09.jpg', None, [('הם מקבלים פה', ''), ('יחס של מלכים', '👑')], .58),
    ('06.jpg', None, [('תחביבים: שקיעות.', ''), ('הרבה שקיעות', '🌅')], .55),
    ('11.jpg', None, [('אז… יוצאים?', '😉🏡')], .50)]
def cover(im, box=None):
    if box: im = im.crop(box)
    return ImageOps.fit(im, (W, H), Image.LANCZOS, centering=(.5, .5))
def aerial(im):
    im = im.crop((0, 525, im.width, 1075)); bg = ImageOps.fit(im, (W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(30))
    fg = im.resize((W, int(W * im.height / im.width)), Image.LANCZOS); bg.paste(fg, (0, (H - fg.height) // 2)); return bg
_ec = {}
def emoji(e, size):
    k = (e, size)
    if k not in _ec:
        f = ImageFont.truetype(EMO, 109, layout_engine=ImageFont.Layout.RAQM); parts = []
        for ch in [e] if e in ('🇮🇱',) else list(e.replace('️', '')):
            t = Image.new('RGBA', (300, 160), (0, 0, 0, 0)); ImageDraw.Draw(t).text((10, 10), ch if ch != '☁' else '☁️', font=f, embedded_color=True)
            t = t.crop(t.getchannel('A').getbbox()); s = size / t.height; parts.append(t.resize((int(t.width * s), size), Image.LANCZOS))
        wsum = sum(p.width for p in parts) + 8 * (len(parts) - 1); out = Image.new('RGBA', (wsum, size), (0, 0, 0, 0)); x = 0
        for p in parts: out.alpha_composite(p, (x, 0)); x += p.width + 8
        _ec[k] = out
    return _ec[k]
def draw(im, lines, yc):
    d = ImageDraw.Draw(im); f = ImageFont.truetype(RUB, 70, layout_engine=ImageFont.Layout.RAQM); lh = 92
    y0 = int(H * yc - len(lines) * lh / 2)
    for i, (t, e) in enumerate(lines):
        tw = d.textlength(t, font=f, direction='rtl'); em = emoji(e, 74) if e else None
        total = tw + (em.width + 16 if em else 0); xr = W / 2 + total / 2; y = y0 + i * lh
        while total > W - 80 and f.size > 48:
            f = ImageFont.truetype(RUB, f.size - 4, layout_engine=ImageFont.Layout.RAQM); tw = d.textlength(t, font=f, direction='rtl'); total = tw + (em.width + 16 if em else 0); xr = W / 2 + total / 2
        d.text((xr, y), t, font=f, fill='white', anchor='ra', direction='rtl', stroke_width=4, stroke_fill='black')
        if em: im.alpha_composite(em, (int(xr - tw - 16 - em.width), int(y + 4)))
os.makedirs(HERE + '/slides', exist_ok=True)
for n, (ph, box, lines, yc) in enumerate(SLIDES, 1):
    src = Image.open(P + ph).convert('RGB')
    im = (aerial(src) if box == 'aerial' else cover(src, box)).convert('RGBA'); draw(im, lines, yc)
    im.convert('RGB').save(HERE + f'/slides/{n:02d}.jpg', quality=93)
sheet = Image.new('RGB', (5 * 216, 2 * 270), 'white')
for n in range(len(SLIDES)): sheet.paste(Image.open(HERE + f'/slides/{n + 1:02d}.jpg').resize((216, 270)), ((n % 5) * 216, (n // 5) * 270))
sheet.save('/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/noa_sheet.jpg'); print('ok')
