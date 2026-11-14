"""Subtitle style options for RZ videos: keep the party teal, but make text readable over the teal backdrop."""
import os, glob
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
KB = glob.glob('/root/.claude/skills/synced/*/pro-video-editing/assets/fonts/Karantina-Bold.ttf')[0]
RUB = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/fonts/Rubik-900.ttf'
DEEP, TEAL, LT, PALE, WHITE = (43, 81, 85), (80, 146, 153), (105, 180, 189), (173, 213, 217), (255, 255, 255)
W, H = 1080, 1920
src = Image.open(HERE + '/../2026-11-yt-thumb-knesset26-faction/source.jpg').convert('RGB')
s = H / src.height; fr = src.resize((int(src.width * s), H), Image.LANCZOS); x0 = int(fr.width * .49 - W / 2); fr = fr.crop((x0, 0, x0 + W, H))
L1, L2, KEY = 'וריבונות לתפארת,', 'שצומחת ומתפתחת בצורה מדהימה', 'לתפארת,'
def F(p, s): return ImageFont.truetype(p, s, layout_engine=ImageFont.Layout.RAQM)
def words_line(d, cx, y, line, f, color, keycolor=None, stroke=0, sfill=None, keybox=None):
    ws = line.split(' '); sp = d.textlength(' ', font=f); widths = [d.textlength(w, font=f, direction='rtl') for w in ws]
    tot = sum(widths) + sp * (len(ws) - 1); x = cx + tot / 2
    for w, wd in zip(ws, widths):
        key = w == KEY
        if key and keybox: d.rounded_rectangle((x - wd - 18, y + 8, x + 18, y + f.size * .98), 14, fill=keybox)
        d.text((x, y), w, font=f, fill=(keycolor if key and keycolor else color), anchor='ra', direction='rtl', stroke_width=stroke, stroke_fill=sfill)
        x -= wd + sp
def opt_a():   # white, thick deep-teal outline + drop shadow; key word light teal
    im = fr.copy().convert('RGBA'); sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(sh); f = F(KB, 108)
    for i, l in enumerate([L1, L2]): words_line(sd, W / 2 + 6, 1330 + i * 120 + 8, l, f, (0, 0, 0, 170), stroke=12, sfill=(0, 0, 0, 170))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6))); d = ImageDraw.Draw(im)
    for i, l in enumerate([L1, L2]): words_line(d, W / 2, 1330 + i * 120, l, f, WHITE, keycolor=PALE, stroke=10, sfill=DEEP)
    return im
def opt_b():   # solid deep-teal boxes behind each line (like news lower thirds); key word in light-teal highlight
    im = fr.copy().convert('RGBA'); d = ImageDraw.Draw(im); f = F(KB, 100)
    for i, l in enumerate([L1, L2]):
        tw = d.textlength(l, font=f, direction='rtl'); y = 1330 + i * 116
        d.rounded_rectangle((W / 2 - tw / 2 - 26, y + 4, W / 2 + tw / 2 + 26, y + 106), 16, fill=DEEP + (240,))
        words_line(d, W / 2, y, l, f, WHITE, keycolor=DEEP, keybox=PALE)
    return im
def opt_c():   # dark gradient at the bottom + Rubik black, key word in a pale-teal block (clean, modern)
    im = fr.copy().convert('RGBA'); g = Image.new('RGBA', im.size, (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    for y in range(H): gd.line((0, y, W, y), fill=(8, 22, 24, int(220 * max(0, (y - H * .58) / (H * .42)) ** 1.2)))
    im.alpha_composite(g); d = ImageDraw.Draw(im); f = F(RUB, 58)
    for i, l in enumerate([L1, L2]): words_line(d, W / 2, 1420 + i * 84, l, f, WHITE, keycolor=DEEP, keybox=LT)
    return im
names = ['א · לבן עם מסגרת כהה', 'ב · פס כהה מאחורי הטקסט', 'ג · הצללה תחתונה + רוביק']
opts = [opt_a(), opt_b(), opt_c()]
for i, o in enumerate(opts): o.convert('RGB').save(HERE + f'/option-{"abc"[i]}.jpg', quality=92)
sh = Image.new('RGB', (3 * 370, 690), WHITE); d = ImageDraw.Draw(sh); fl = F('/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/fonts/Rubik-700.ttf', 28)
for i, o in enumerate(opts):
    sh.paste(o.convert('RGB').resize((360, 640)), (i * 370 + 5, 0)); d.text((i * 370 + 365, 650), names[i], font=fl, fill=(30, 30, 30), anchor='ra', direction='rtl')
sh.save(HERE + '/compare.jpg', quality=90); print('ok')
