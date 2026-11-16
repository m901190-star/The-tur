"""RZ reel 9:16: Channel 14 clip stays in the middle; top/bottom black bars filled with RZ-teal motion graphics + Haim subtitles. No party logo."""
import os, sys, math, subprocess, random, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
HAIM = HERE + '/../../fonts/HaimClassicv2FM-Bold.ttf'; SEC = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/shalev/fonts/SecularOne.ttf'
W, H, FPS = 1080, 1920, 30; DUR = 30.13; Y0, Y1 = 656, 1263
DEEP, TEAL, LT, PALE, WHITE = (43, 81, 85), (80, 146, 153), (105, 180, 189), (173, 213, 217), (255, 255, 255)
NIGHT = (18, 40, 43)
_fc = {}
def F(p, s):
    k = (p, s)
    if k not in _fc: _fc[k] = ImageFont.truetype(p, s, layout_engine=ImageFont.Layout.RAQM)
    return _fc[k]
def eo(x): x = max(0., min(1., x)); return 1 - (1 - x) ** 3
def eob(x): x = max(0., min(1., x)); c = 1.7; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
# ---------- static background for the bars ----------
BG = Image.new('RGB', (W, H), NIGHT); px = np.zeros((H, W, 3), np.float32)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
for cy in (330, 1590):
    g = np.clip(1 - np.hypot((xx - 540) / 800, (yy - cy) / 420), 0, 1) ** 1.5
    px += g[..., None] * (np.array(TEAL, np.float32) - np.array(NIGHT, np.float32)) * .75
px += np.array(NIGHT, np.float32); grid = ((xx % 60 < 1.5) | (yy % 60 < 1.5)).astype(np.float32)[..., None] * 9
BG = Image.fromarray(np.clip(px + grid, 0, 255).astype(np.uint8))
random.seed(3); PART = [(random.uniform(0, W), random.uniform(0, H), random.uniform(2, 6), random.uniform(10, 35), random.uniform(.15, .5)) for _ in range(70)]
def background(t):
    im = BG.copy().convert('RGBA'); lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for x, y, r, sp, a in PART:
        y2 = (y - sp * t) % H; d.ellipse((x - r, y2 - r, x + r, y2 + r), fill=PALE + (int(255 * a * .6),))
    im.alpha_composite(lay); return im
# ---------- helpers ----------
def txt(d, xy, s, f, fill=WHITE, anchor='ma', shadow=True, rtl=True):
    kw = {'direction': 'rtl'} if rtl else {}
    if shadow: d.text((xy[0] + 5, xy[1] + 5), s, font=f, fill=DEEP + (255,) if len(fill) == 4 else DEEP, anchor=anchor, **kw)
    d.text(xy, s, font=f, fill=fill, anchor=anchor, **kw)
def pill(d, cx, y, s, f, bg=LT, fg=NIGHT, rtl=True):
    kw = {'direction': 'rtl'} if rtl else {}
    tw = d.textlength(s, font=f, **kw); hgt = f.size + 26
    d.rounded_rectangle((cx - tw / 2 - 30, y, cx + tw / 2 + 30, y + hgt), hgt // 2, fill=bg); d.text((cx, y + 11), s, font=f, fill=fg, anchor='ma', **kw)
def arrow(d, cx, cy, size, down=True, fill=LT):
    s = size; sg = 1 if down else -1
    d.rectangle((cx - s * .16, cy - sg * s * .5, cx + s * .16, cy + sg * s * .1) if down else (cx - s * .16, cy + s * .1 * -1 + 0, cx + s * .16, cy + s * .5), fill=fill)
    d.polygon([(cx - s * .42, cy + sg * s * .05), (cx + s * .42, cy + sg * s * .05), (cx, cy + sg * s * .55)], fill=fill)
def check(d, cx, cy, r, p):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=LT)
    pts = [(cx - r * .45, cy), (cx - r * .1, cy + r * .38), (cx + r * .5, cy - r * .35)]
    if p > 0: q = min(1, p * 2); d.line([pts[0], (pts[0][0] + (pts[1][0] - pts[0][0]) * q, pts[0][1] + (pts[1][1] - pts[0][1]) * q)], fill=NIGHT, width=int(r * .22))
    if p > .5: q = min(1, (p - .5) * 2); d.line([pts[1], (pts[1][0] + (pts[2][0] - pts[1][0]) * q, pts[1][1] + (pts[2][1] - pts[1][1]) * q)], fill=NIGHT, width=int(r * .22))
def house(d, cx, cy, s, fill=PALE):
    d.polygon([(cx - s * .55, cy - s * .05), (cx, cy - s * .5), (cx + s * .55, cy - s * .05)], fill=fill)
    d.rectangle((cx - s * .4, cy - s * .08, cx + s * .4, cy + s * .45), fill=fill)
    d.rectangle((cx - s * .1, cy + s * .12, cx + s * .1, cy + s * .45), fill=NIGHT); d.rectangle((cx + s * .18, cy + s * .02, cx + s * .32, cy + s * .16), fill=NIGHT)
def globe(d, cx, cy, r, t):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=TEAL, outline=PALE, width=6)
    for k in range(6):
        ph = (t * .6 + k / 6) % 1; w = r * math.cos(ph * math.pi)
        if abs(w) > 4: d.ellipse((cx - abs(w), cy - r, cx + abs(w), cy + r), outline=PALE + (150,), width=3)
    for la in (-.55, 0, .55):
        yy_ = cy + la * r; ww = r * math.sqrt(1 - la * la); d.line((cx - ww, yy_, cx + ww, yy_), fill=PALE + (150,), width=3)
def flag(im, cx, cy, w, a):
    h = w * .72; L = Image.new('RGBA', (int(w), int(h)), WHITE + (255,)); d = ImageDraw.Draw(L); B = (0, 56, 184)
    d.rectangle((0, h * .1, w, h * .24), fill=B); d.rectangle((0, h * .76, w, h * .9), fill=B)
    r = h * .2; c = (w / 2, h / 2)
    for sg in (1, -1): d.polygon([(c[0], c[1] - sg * r), (c[0] - r * .87, c[1] + sg * r / 2), (c[0] + r * .87, c[1] + sg * r / 2)], outline=B, width=max(3, int(w * .03)))
    L.putalpha(int(255 * a)); im.alpha_composite(L, (int(cx - w / 2), int(cy - h / 2)))
# ---------- top-panel scenes ----------
SC = [(0.0, 3.8, 'A'), (3.8, 6.25, 'B'), (6.25, 10.6, 'C'), (10.6, 23.1, 'D'), (23.1, DUR, 'E')]
def scene(k, u, T):
    L = Image.new('RGBA', (W, Y0), (0, 0, 0, 0)); d = ImageDraw.Draw(L); CX = W / 2
    if k == 'A':
        if u > .1: pill(d, CX, 150, 'האינפלציה באוקטובר', F(HAIM, 50))
        if u > .5: txt(d, (CX, 250), 'הנמוכה ביותר מזה', F(HAIM, 66))
        if u > .9:
            v = 5.5 * eo((u - .9) / 1.0); s = f'{v:.1f}'; f = F(HAIM, 230); fs = F(HAIM, 96)
            nw = d.textlength('5.5', font=f); sw = d.textlength('שנים', font=fs, direction='rtl'); x0 = CX - (nw + 30 + sw) / 2
            txt(d, (x0 + nw, 590), s, f, anchor='rs', rtl=False); txt(d, (x0 + nw + 30, 590), 'שנים', fs, anchor='ls')
            arrow(d, x0 - 90, 470 + 18 * math.sin(T * 6), 110)
    if k == 'B':
        if u > .05: pill(d, CX, 150, 'מחירי הדירות', F(HAIM, 50))
        s = max(2, 230 * eob(u / .4)); house(d, CX + 120, 400, s)
        if u > .3: arrow(d, CX - 190, 360 + 40 * ((u * 1.6) % 1), 150)
        if u > .5: txt(d, (CX, 560), 'ממשיכים לרדת', F(HAIM, 66))
    if k == 'C':
        if u > .05: pill(d, CX, 150, 'נתונים מאוד מאוד טובים', F(HAIM, 50))
        for i, s in enumerate(['האינפלציה', 'מחירי הדירות', 'המדד']):
            st = .25 + i * .45
            if u > st:
                p = eo((u - st) / .35); y = 290 + i * 110; dx = 60 * (1 - p)
                check(d, 820 + dx, y + 36, 38, (u - st) / .5); txt(d, (760 + dx, y), s, F(HAIM, 70), anchor='ra')
                arrow(d, 230 + dx, y + 30, 70)
    if k == 'D':
        if u > 2.6: pill(d, CX, 150, 'לראשונה', F(HAIM, 54))
        gr = max(2, 150 * eob(u / .5)); globe(d, 300, 420, gr, T)
        if u > 3.0:
            txt(d, (760, 250), 'מקום', F(HAIM, 72))
            n = int(round(1 + 24 * eo((u - 3.0) / 1.3))); sc = 1 + .15 * max(0, 1 - (u - 4.3) / .35) if u > 4.3 else 1
            txt(d, (760, 560), f'{n}', F(HAIM, int(240 * sc)), anchor='ms', rtl=False)
        if u > 6.1: txt(d, (CX, 585), 'בכלכלות הגדולות בעולם', F(HAIM, 52), fill=PALE + (255,))
        if u > 8.9: flag(L, 300, 420 + 10 * math.sin(T * 3), max(4, 150 * eob((u - 8.9) / .45)), 1)
    if k == 'E':
        if u > .05: pill(d, 860, 170, 'S&P', F(SEC, 50), rtl=False)
        base = 590; hs = [120, 170, 240, 340]
        for i, h_ in enumerate(hs):
            p = eo((u - .2 - i * .15) / .6); x = 130 + i * 105
            if p > 0: d.rounded_rectangle((x, base - h_ * p, x + 75, base), 10, fill=LT if i == 3 else TEAL)
        if u > 1.0:
            p = eo((u - 1.0) / .5); d.line((120, base - 100, 120 + 390 * p, base - 100 - 300 * p), fill=PALE, width=12)
            if p > .95: arrow(d, 515, base - 410, 90, down=False, fill=PALE)
        if u > .6: txt(d, (1010, 290), 'העלתה את', F(HAIM, 64), anchor='ra')
        if u > .9: txt(d, (1010, 390), 'תחזית הצמיחה', F(HAIM, 78), anchor='ra')
        if u > 1.2: txt(d, (1010, 490), 'של ישראל', F(HAIM, 78), anchor='ra', fill=PALE + (255,))
    return L
SUBS = [(0.4, 2.2, 'האינפלציה באוקטובר'), (2.2, 3.8, 'הנמוכה ביותר מזה חמש שנים וחצי'), (3.8, 5.4, 'מחירי הדירות ממשיכים לרדת'), (5.4, 6.1, 'המדד ירד'),
        (6.4, 8.0, 'נתונים מאוד מאוד טובים'), (8.0, 10.3, 'זה מצטרף לנתונים בימים האחרונים'), (10.8, 13.0, 'למרות המלחמה, ישראל לראשונה'),
        (13.5, 16.2, 'כן, בפעם הראשונה עלתה למקום ה־25'), (16.7, 19.6, 'בכלכלות הגדולות בעולם'), (19.6, 22.9, 'ישראל נכנסה לראשונה'),
        (23.3, 26.3, 'ו־S&P העלתה את תחזית הצמיחה של ישראל'), (26.3, 29.3, 'תחזית פסיכית של איזה 7% שנה הבאה')]
def wrap(d, s, f, maxw):
    out, cur = [], ''
    for w in s.split():
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=f, direction='rtl') <= maxw: cur = t
        else: out.append(cur); cur = w
    return out + [cur]
import re
def runs(word):
    return [(r, bool(re.match(r'[A-Za-z&]', r))) for r in re.findall(r'[A-Za-z&]+|[^A-Za-z&]+', word)]
def mixed_line(d, cx, base, line, size, fill=WHITE):
    fh, fl = F(HAIM, size), F(SEC, int(size * .95)); sp = d.textlength(' ', font=fh, direction='rtl')
    items = []
    for w in line.split():
        rs = [(r, fl if lat else fh, lat) for r, lat in runs(w)]
        items.append([(r, f, lat, d.textlength(r, font=f, **({} if lat else {'direction': 'rtl'}))) for r, f, lat in rs])
    tot = sum(sum(x[3] for x in it) for it in items) + sp * (len(items) - 1); x = cx + tot / 2
    for it in items:
        for r, f, lat, w in it:
            kw = {} if lat else {'direction': 'rtl'}
            d.text((x + 5, base + 5), r, font=f, fill=NIGHT, anchor='rs', **kw); d.text((x, base), r, font=f, fill=fill, anchor='rs', **kw); x -= w
        x -= sp
def subs(im, t):
    d = ImageDraw.Draw(im)
    for a, b, s in SUBS:
        if a <= t < b + .15:
            p = eob((t - a) / .25); size = int(84 * (.85 + .15 * p)); lines = wrap(d, s, F(HAIM, size), 900)
            for k, l in enumerate(lines): mixed_line(d, W / 2, 1360 + size * .82 + k * 92, l, size)
            return
def frame(t, src):
    im = background(t)
    clip = Image.fromarray(src[Y0:Y1]); im.paste(clip, (0, Y0))
    d = ImageDraw.Draw(im); d.rectangle((0, Y0 - 6, W, Y0 - 1), fill=LT); d.rectangle((0, Y1, W, Y1 + 5), fill=LT)
    for a, b, k in SC:
        if a <= t < b:
            L = scene(k, t - a, t); fade = min(eo((t - a) / .3), 1 if b >= DUR else eo((b - t) / .2))
            if fade < 1: L.putalpha(L.getchannel('A').point(lambda v: int(v * fade)))
            im.alpha_composite(L, (0, int(20 * (1 - eo((t - a) / .3)))))
    subs(im, t)
    return im.convert('RGB')
if __name__ == '__main__':
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', HERE + '/source.mov', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
    V = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3); N = int(round(DUR * FPS))
    if 'stills' in sys.argv:
        ts = [1.5, 3.3, 5.5, 9, 12, 16, 21, 27]; ims = [frame(x, V[min(int(x * FPS), len(V) - 1)]).resize((270, 480)) for x in ts]
        sh = Image.new('RGB', (4 * 274, 2 * 484)); [sh.paste(x, ((i % 4) * 274, (i // 4) * 484)) for i, x in enumerate(ims)]; sh.save(sys.argv[2]); sys.exit()
    SFX = []  # Moshe: SFX overpowered the speaker - removed
    _OLD_SFX = [('woosh2', .05, .30), ('pop', .12, .28), ('ding', 1.9, .30), ('whoosh', 3.65, .32), ('pop', 3.85, .25), ('whoosh', 6.1, .32), ('pop', 6.5, .25), ('pop', 6.95, .25),
           ('pop', 7.4, .25), ('whoosh', 10.45, .32), ('pop', 13.2, .25), ('ding', 14.9, .32), ('pop', 16.7, .2), ('ding', 19.5, .28), ('whoosh', 22.95, .32), ('pop', 23.15, .25), ('swell', 23.35, .35)]
    ins, fl = [], []
    for i, (n, at, v) in enumerate(SFX):
        ins += ['-i', HERE + f'/sfx/{n}.wav']; fl.append(f'[{i + 2}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={v},adelay={int(at * 1000)}:all=1[s{i}]')
    fc = ';'.join(['[1:a]aformat=sample_rates=48000:channel_layouts=stereo[v]'] + fl + ['[v]' + ''.join(f'[s{i}]' for i in range(len(SFX))) + f'amix=inputs={len(SFX) + 1}:normalize=0,alimiter=limit=0.95[a]'])
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', HERE + '/source.mov'] + ins + ['-filter_complex', fc,
        '-map', '0:v', '-map', '[a]', '-vf', 'scale=720:1280:flags=lanczos', '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-maxrate', '4M', '-bufsize', '8M',
        '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-t', str(DUR), '-movflags', '+faststart', HERE + '/rz-economy-motion.mp4'], stdin=subprocess.PIPE)
    for i in range(N): ff.stdin.write(frame(i / FPS, V[min(i, len(V) - 1)]).tobytes())
    ff.stdin.close(); ff.wait(); print('done')
