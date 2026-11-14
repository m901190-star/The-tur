"""Yesha reel 9:16 - חוות בר דליה. User's narration (voice only). No music (added in Instagram). Yesha style."""
import os, sys, glob, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
HERE = os.path.dirname(os.path.abspath(__file__)); FT = HERE + '/footage/'; PH = HERE + '/photos/'
P = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/bardalia/prep/'; os.makedirs(P, exist_ok=True)
KB = glob.glob('/root/.claude/skills/synced/*/pro-video-editing/assets/fonts/Karantina-Bold.ttf')[0]
SEC = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/shalev/fonts/SecularOne.ttf'
LOGO = HERE + '/../../clients/yesha/logo_white.png'
W, H, FPS = 1080, 1920, 30; BLUE = (0x25, 0x66, 0xA2); WHITE = (255, 255, 255)
VO_END = 66.4; TOTAL = VO_END + 2.6
SHOTS = [(0.0, 4.3, 'img', 'p1.jpg', 0, (.5, .5)), (4.3, 8.8, 'vid', 'v9.mov', 0.5, 1), (8.8, 15.2, 'img', 'p5.jpg', 0, (.5, .32)),
         (15.2, 21.0, 'vid', 'v6.mov', 0.0, 1), (21.0, 26.9, 'vid', 'v11.mov', 4.5, .55), (26.9, 33.4, 'img', 'p7-sheepfold.jpg', 0, (.5, .5)),
         (33.4, 40.5, 'vid', 'v7.mov', 3.2, .6), (40.5, 45.1, 'img', 'p6.jpg', 0, (.5, .4)), (45.1, 48.8, 'vid', 'v3.mov', 0.0, 1),
         (48.8, 51.0, 'vid', 'v4.mov', 0.0, 1), (51.0, 54.4, 'vid', 'v15.mov', 0.5, 1), (54.4, 58.4, 'img', 'p3.jpg', 0, (.5, .45)),
         (58.4, 61.8, 'img', 'p2.jpg', 0, (.5, .5)), (61.8, 64.6, 'vid', 'v18.mov', 1.0, 1), (64.6, 99, 'vid', 'v12.mov', 1.0, 1)]
SUBS = [(0.47, 4.3, 'ממערב למחסום הבקעה, סמוך לכפר ברדלה,'), (4.3, 8.3, 'נמצאת חווה שמספרת סיפור של עבר, הווה ועתיד.'),
        (8.76, 13.2, 'על פי הידוע, במקום שכן בעבר כפר יהודי קטן'), (13.39, 15.1, 'בשם בר־דליה,'), (15.15, 18.2, 'שבו התגוררה משמרת הכהונה דליה,'),
        (18.35, 20.5, 'המוזכרת גם בגמרא.'), (21.06, 26.0, 'השם העתיק השתמר עד ימינו בשם הכפר ברדלה.'),
        (26.92, 29.5, 'בעקבות הפיגוע בצומת מחולה,'), (29.75, 33.2, 'שבו נהרג יונתן דויטש הי״ד,'), (33.36, 38.0, 'הוקמה החווה מתוך צורך אסטרטגי לחזק את האחיזה במרחב'),
        (38.11, 44.5, 'ולבלום רצף טריטוריאלי בין הכפרים בצפון השומרון לבין בקעת הירדן.'), (45.09, 48.7, 'אורי ואשחר רוזנפלד, יחד עם בנם אניעם,'),
        (48.81, 54.2, 'בונים כאן התיישבות חלוצית עם חזון להקים בית מדרש'), (54.44, 58.2, 'שמשלב תורה ועבודה, רוח ואדמה.'),
        (58.4, 61.6, 'היום, החווה שומרת על מאות דונמים,'), (61.77, 66.4, 'מעבדת את הקרקע ומפיחה חיים בשטח.')]
LABELS = [(0.3, 8.6, 'ברדלה · בקעת הירדן'), (13.3, 21.0, 'בר־דליה'), (29.6, 33.4, 'יונתן דויטש הי״ד'), (45.0, 51.0, 'משפחת רוזנפלד')]
def F(p, s): return ImageFont.truetype(p, s, layout_engine=ImageFont.Layout.RAQM)
def eo(x): x = max(0., min(1., x)); return 1 - (1 - x) ** 3
def prep():
    for i, (a, b, kind, src, t0, sp) in enumerate(SHOTS):
        if kind != 'vid': continue
        d = P + f's{i:02d}/'
        if os.path.exists(d + '0001.jpg'): continue
        os.makedirs(d, exist_ok=True); dur = ((b - a) if a >= 100 else (min(b, TOTAL) - a)) * sp + .6
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(t0), '-t', f'{dur:.2f}', '-i', FT + src, '-vf', f'setpts=PTS/{sp},fps={FPS},' + ('crop=iw*0.62:ih*0.62:iw*0.19:ih*0.04,' if src == 'v11.mov' else '') + 'scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,unsharp=5:5:0.7,eq=saturation=1.08:contrast=1.04', '-q:v', '2', d + '%04d.jpg'], check=True)
_ls, _img = {}, {}
def photo(n):
    if n not in _img:
        im = Image.open(PH + n).convert('RGB'); s = max(W * 1.15 / im.width, H * 1.15 / im.height)
        _img[n] = ImageEnhance.Color(im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)).enhance(1.06)
    return _img[n]
def shot(i, t):
    a, b, kind, src, t0, sp = SHOTS[i]; u = t - a; dur = max(.1, (b - a) if a >= 100 else min(b, TOTAL) - a)
    if kind == 'img':
        im = photo(src); z = 1 + .1 * u / dur; cx, cy = sp[0] * im.width, sp[1] * im.height
        cw, ch = min(im.width, int(W * 1.15 / z / 1.15 * im.width / (W * 1.15) * 1.15)), 0
        cw = min(im.width, int(im.width / 1.15 / z)); ch = min(im.height, int(im.height / 1.15 / z))
        x0 = int(max(0, min(im.width - cw, cx - cw / 2))); y0 = int(max(0, min(im.height - ch, cy - ch / 2)))
        return im.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.BILINEAR)
    d = P + f's{i:02d}/'
    if d not in _ls: _ls[d] = sorted(os.listdir(d))
    fs = _ls[d]; im = Image.open(d + fs[max(0, min(len(fs) - 1, int(u * FPS)))]).convert('RGB')
    z = 1 + .04 * min(1, u / dur); return im.resize((int(W * z), int(H * z)), Image.BILINEAR).crop((int((W * z - W) / 2), int((H * z - H) / 2), int((W * z - W) / 2) + W, int((H * z - H) / 2) + H))
def base(t):
    for i, (a, b, *_) in enumerate(SHOTS):
        if a <= t < b:
            f = shot(i, t)
            return f
GRAD = Image.new('RGBA', (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(GRAD)
for y in range(H): gd.line((0, y, W, y), fill=(5, 14, 28, int(170 * max(0, (y - H * .62) / (H * .38)) ** 1.4) + int(90 * max(0, (H * .14 - y) / (H * .14)))))
LG = Image.open(LOGO).convert('RGBA'); LG = LG.crop(LG.getchannel('A').getbbox()); LG = LG.resize((170, int(170 * LG.height / LG.width)), Image.LANCZOS)
def wrap(d, s, f, maxw):
    out, cur = [], ''
    for w in s.split():
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=f, direction='rtl') <= maxw: cur = t
        else: out.append(cur); cur = w
    return out + [cur]
def frame(t):
    im = base(t).convert('RGBA'); im.alpha_composite(GRAD); d = ImageDraw.Draw(im)
    for a, b, s in LABELS:
        if a <= t < b:
            p = eo((t - a) / .4); f = F(SEC, 54); tw = d.textlength(s, font=f, direction='rtl')
            lay = Image.new('RGBA', (int(tw) + 60, 90), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay); ld.rounded_rectangle((0, 0, lay.width - 1, 89), 14, fill=BLUE); ld.text((lay.width / 2, 12), s, font=f, fill=WHITE, anchor='ma', direction='rtl')
            lay.putalpha(lay.getchannel('A').point(lambda v: int(v * p))); im.alpha_composite(lay, (int(W / 2 - lay.width / 2), int(300 + 20 * (1 - p))))
    for a, b, s in SUBS:
        if a - .05 <= t < b + .2:
            p = eo((t - a + .05) / .2); f = F(KB, 92); lines = wrap(d, s, f, 940); y0 = 1560 - (len(lines) - 1) * 88 + 20 * (1 - p)
            for k, l in enumerate(lines):
                d.text((W / 2 + 6, y0 + k * 88 + 6), l, font=f, fill=BLUE, anchor='ma', direction='rtl'); d.text((W / 2, y0 + k * 88), l, font=f, fill=WHITE, anchor='ma', direction='rtl')
            break
    if t > VO_END:
        u = t - VO_END; lg = Image.open(LOGO).convert('RGBA'); lg = lg.crop(lg.getchannel('A').getbbox()); lg = lg.resize((420, int(420 * lg.height / lg.width)), Image.LANCZOS)
        lg.putalpha(lg.getchannel('A').point(lambda v: int(v * eo((u - .2) / .6)))); im.alpha_composite(lg, (int(W / 2 - 210), 1300))
    else: im.alpha_composite(LG, (W - 60 - LG.width, 70))
    if t < .4: im = Image.blend(Image.new('RGBA', (W, H), (0, 0, 0, 255)), im, t / .4)
    return im.convert('RGB')
# ---------- v3: new hook opening, all Bardala-village mentions removed, subtitles raised toward centre ----------
# hook audio (vo_hook_clean.wav): 0.35-3.6 -> new 0.0 ; 5.0-12.2 -> new 3.55
# old narration: 8.70-20.6 -> new 11.1 ; 26.9-66.4 -> new 23.0   (skips 'השם העתיק השתמר... ברדלה')
SHOTS.append((200.0, 207.5, 'vid', 'v9.mov', 0.5, 1))            # hook: view from the farmhouse window
H_END, J1, J2 = 11.1, 23.0, 2.4
def n2o(T): return T - J2 if T < J1 else T + 3.9
TOTAL3 = n2o(VO_END) * 0 + (VO_END - 3.9) + 2.6
SUB_Y = 1120
SUBS_H = [(0.05, 3.2, 'כפר יהודי מתקופת הגמרא חוזר לחיים.'), (3.66, 7.75, 'ממערב למחסום הבקעה נמצאת חווה'), (7.8, 10.75, 'שמספרת סיפור של עבר, הווה ועתיד.')]
GRAD3 = Image.new('RGBA', (W, H), (0, 0, 0, 0)); g3 = ImageDraw.Draw(GRAD3)
for y in range(H): g3.line((0, y, W, y), fill=(5, 14, 28, int(150 * max(0, 1 - abs(y - 1230) / 520) ** 1.2) + int(90 * max(0, (H * .14 - y) / (H * .14)))))
def hook_base(T):
    if T < 4.3: f = shot(0, T)
    else: f = shot(len(SHOTS) - 1, 200.0 + (T - 4.3))
    return f
def draw_subs(im, T, subs, size=92):
    d = ImageDraw.Draw(im)
    for a, b, s in subs:
        if a - .05 <= T < b + .2:
            p = eo((T - a + .05) / .2); f = F(KB, size); lines = wrap(d, s, f, 940); y0 = SUB_Y - (len(lines) - 1) * (size * .95) / 2 + 20 * (1 - p)
            for k, l in enumerate(lines):
                y = y0 + k * size * .95
                d.text((W / 2 + 6, y + 6), l, font=f, fill=BLUE, anchor='ma', direction='rtl'); d.text((W / 2, y), l, font=f, fill=WHITE, anchor='ma', direction='rtl')
            return
def label3(im, T, a, b, s):
    if not (a <= T < b): return
    d = ImageDraw.Draw(im); p = eo((T - a) / .4); f = F(SEC, 54); tw = d.textlength(s, font=f, direction='rtl')
    lay = Image.new('RGBA', (int(tw) + 60, 90), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay); ld.rounded_rectangle((0, 0, lay.width - 1, 89), 14, fill=BLUE); ld.text((lay.width / 2, 12), s, font=f, fill=WHITE, anchor='ma', direction='rtl')
    lay.putalpha(lay.getchannel('A').point(lambda v: int(v * p))); im.alpha_composite(lay, (int(W / 2 - lay.width / 2), int(300 + 20 * (1 - p))))
def frame3(T):
    if T < H_END:
        f = hook_base(T)
        if T > H_END - .25: f = Image.blend(f, base(n2o(H_END)), (T - (H_END - .25)) / .25)
        im = f.convert('RGBA'); im.alpha_composite(GRAD3); label3(im, T, .3, H_END, 'צפון בקעת הירדן'); draw_subs(im, T, SUBS_H, 104 if T < 3.3 else 92)
    else:
        t = n2o(T); f = base(t)
        if J1 <= T < J1 + .25: f = Image.blend(base(n2o(J1 - .001)), f, (T - J1) / .25)
        im = f.convert('RGBA'); im.alpha_composite(GRAD3)
        for a, b, s in LABELS:
            if s != 'ברדלה · בקעת הירדן': label3(im, t, a, b, s)
        if t <= VO_END: draw_subs(im, t, [x for x in SUBS if 'ברדלה' not in x[2]])
    if T > TOTAL3 - 2.6:
        u = T - (TOTAL3 - 2.6); lg = Image.open(LOGO).convert('RGBA'); lg = lg.crop(lg.getchannel('A').getbbox()); lg = lg.resize((420, int(420 * lg.height / lg.width)), Image.LANCZOS)
        lg.putalpha(lg.getchannel('A').point(lambda v: int(v * eo((u - .2) / .6)))); im.alpha_composite(lg, (int(W / 2 - 210), 1300))
    else: im.alpha_composite(LG, (W - 60 - LG.width, 70))
    if T < .4: im = Image.blend(Image.new('RGBA', (W, H), (0, 0, 0, 255)), im, T / .4)
    return im.convert('RGB')
def audio3():
    TT = TOTAL3; lo_a, lo_b = 26.5 - 3.9, 33.6 - 3.9
    return ['-i', HERE + '/vo_clean.wav', '-i', HERE + '/vo_hook_clean.wav', '-i', HERE + '/../2026-11-reel-bustan-david/music.wav', '-filter_complex',
        ';'.join([f'[2:a]atrim=0.35:3.6,asetpts=PTS-STARTPTS,afade=t=out:st=3.15:d=0.1[h1]',
                  f'[2:a]atrim=5.0:12.2,asetpts=PTS-STARTPTS,afade=t=in:d=0.05,afade=t=out:st=7.1:d=0.1,adelay=3550:all=1[h2]',
                  f'[1:a]atrim=8.70:20.6,asetpts=PTS-STARTPTS,afade=t=in:d=0.05,afade=t=out:st=11.8:d=0.1,adelay=11100:all=1[o1]',
                  f'[1:a]atrim=26.9:{VO_END},asetpts=PTS-STARTPTS,afade=t=in:d=0.05,adelay=23000:all=1[o2]',
                  f'[h1][h2][o1][o2]amix=inputs=4:normalize=0,aformat=sample_rates=48000:channel_layouts=stereo,apad=whole_dur={TT},asplit=2[v][k]',
                  f"[3:a]aformat=sample_rates=48000:channel_layouts=stereo,aloop=loop=3:size={int(25.6*44100)},atrim=0:{TT},volume='if(between(t,{lo_a},{lo_b}),0.12,if(gt(t,{TT-2.6}),0.55,0.30))':eval=frame,afade=t=in:d=1,afade=t=out:st={TT-2}:d=2[m]",
                  '[m][k]sidechaincompress=threshold=0.03:ratio=3:attack=20:release=350[md]', '[v][md]amix=inputs=2:normalize=0,alimiter=limit=0.95[a]'])]

# ---------- v4: map, Gemara, memorial and blocking beats ----------
import importlib.util as _iu
def _load(n):
    sp_ = _iu.spec_from_file_location(n, HERE + '/map/' + n + '.py'); m = _iu.module_from_spec(sp_); sp_.loader.exec_module(m); return m
MAPM, GEM = _load('make_map'), _load('make_gemara')
def _memorial():
    src = Image.open(PH + 'yehonatan-deutsch.jpg').convert('RGB')
    bg = src.resize((int(src.width * H / src.height), H), Image.LANCZOS); x0 = (bg.width - W) // 2
    from PIL import ImageFilter as _F
    bg = ImageEnhance.Brightness(bg.crop((x0, 0, x0 + W, H)).filter(_F.GaussianBlur(35))).enhance(.32).convert('RGBA')
    c = src.crop((180, 0, 1050, 698)); c = c.resize((960, int(960 * c.height / c.width)), Image.LANCZOS)
    m = Image.new('L', c.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, c.width - 1, c.height - 1), 26, fill=255)
    sh = Image.new('L', (c.width + 80, c.height + 80), 0); sh.paste(m, (40, 52)); sh = sh.filter(_F.GaussianBlur(20))
    y = 520; bg.paste((0, 0, 0, 140), ((W - c.width) // 2 - 40, y - 40), sh); bg.paste(c, ((W - c.width) // 2, y), m)
    d = ImageDraw.Draw(bg); yb = y + c.height + 60; f = F(KB, 120)
    d.text((W / 2 + 5, yb + 5), 'יונתן דויטש הי״ד', font=f, fill=BLUE, anchor='ma', direction='rtl'); d.text((W / 2, yb), 'יונתן דויטש הי״ד', font=f, fill=WHITE, anchor='ma', direction='rtl')
    d.line((W / 2 - 80, yb + 150, W / 2 + 80, yb + 150), fill=(0x27, 0xA4, 0xD1), width=4)
    d.text((W / 2, yb + 175), 'נרצח בפיגוע בצומת מחולה', font=F(SEC, 46), fill=(214, 228, 239), anchor='ma', direction='rtl')
    return bg.convert('RGB')
MEM = _memorial()
_P6 = None
def p6_land(u, dur):
    global _P6
    if _P6 is None:
        im = Image.open(PH + 'p6.jpg').convert('RGB'); top = im.crop((0, 300, im.width, 800))      # valley + fields above the dog
        s_ = H / top.height; _P6 = ImageEnhance.Color(top.resize((int(top.width * s_), H), Image.LANCZOS)).enhance(1.1)
    k = u / dur; x0 = int((_P6.width - W) * (.15 + .5 * k)); return _P6.crop((x0, 0, x0 + W, H))
BEATS = [(4.3, 11.1, 'map'), (17.6, 23.0, 'gem'), (23.0, 29.5, 'mem'), (29.5, 34.0, 'fold'), (34.0, 41.2, 'block'), (54.5, 57.9, 'land')]
def base4(T):
    for a, b, k in BEATS:
        if a <= T < b:
            u = T - a
            if k == 'map': return MAPM.frame(u * 4.5 / (b - a)), k
            if k == 'gem': return GEM.frame(u), k
            if k == 'mem':
                z = 1 + .04 * u / (b - a); im = MEM.resize((int(W * z), int(H * z)), Image.BILINEAR); x0 = (im.width - W) // 2; y0 = (im.height - H) // 2
                return im.crop((x0, y0, x0 + W, y0 + H)), k
            if k == 'fold': return MAPM.frame(2.9 + u * 1.7 / (b - a)), 'map'
            if k == 'block': return MAPM.frame(4.6 + u * 3.4 / (b - a)), k
            if k == 'land': return shot(5, 26.9 + u * 6.5 / (b - a)), 'normal_land'
    if T < H_END: return hook_base(T), 'hook'
    return base(n2o(T)), 'normal'
EDGES = sorted(set([x for a, b, _ in BEATS for x in (a, b)] + [H_END, J1]))
def frame4(T):
    f, kind = base4(T)
    im = f.convert('RGBA')
    if kind not in ('mem', 'map', 'gem', 'block'): im.alpha_composite(GRAD3)
    if kind in ('map', 'gem', 'block'):
        band = Image.new('RGBA', (W, H), (0, 0, 0, 0)); bd_ = ImageDraw.Draw(band)
        for y in range(1480, H): bd_.line((0, y, W, y), fill=(6, 16, 30, int(210 * min(1, (y - 1480) / 120))))
        im.alpha_composite(band)
    global SUB_Y
    SUB_Y = 1600 if kind in ('map', 'gem', 'block') else 1120
    if T < H_END:
        if T < 4.3: label3(im, T, .3, 4.3, 'צפון בקעת הירדן')
        draw_subs(im, T, SUBS_H, 104 if T < 3.3 else 92)
    elif kind != 'mem':
        t = n2o(T)
        if kind in ('normal', 'normal_land'):
            for a, b, s_ in LABELS:
                if s_ not in ('ברדלה · בקעת הירדן', 'יונתן דויטש הי״ד', 'בר־דליה'): label3(im, t, a, b, s_)
            if 11.1 <= T < 17.6: label3(im, T, 11.4, 17.6, 'בר־דליה')
        if t <= VO_END: draw_subs(im, t, [x for x in SUBS if 'ברדלה' not in x[2]])
    if T > TOTAL3 - 2.6:
        u = T - (TOTAL3 - 2.6); lg = Image.open(LOGO).convert('RGBA'); lg = lg.crop(lg.getchannel('A').getbbox()); lg = lg.resize((420, int(420 * lg.height / lg.width)), Image.LANCZOS)
        lg.putalpha(lg.getchannel('A').point(lambda v: int(v * eo((u - .2) / .6)))); im.alpha_composite(lg, (int(W / 2 - 210), 1300))
    else: im.alpha_composite(LG, (W - 60 - LG.width, 70))
    if T < .4: im = Image.blend(Image.new('RGBA', (W, H), (0, 0, 0, 255)), im, T / .4)
    return im.convert('RGB')
frame3 = frame4

if __name__ == '__main__':
    prep()
    if 'stills' in sys.argv:
        ts = [1.5, 6, 9.5, 13, 19, 22, 26, 31, 36, 40, 43, 48, 52, 56, 64]
        ims = [frame3(x).resize((180, 320)) for x in ts]; sh = Image.new('RGB', (8 * 184, 2 * 324), WHITE)
        for i, x in enumerate(ims): sh.paste(x, ((i % 8) * 184, (i // 8) * 324))
        sh.save(P + '../stills.jpg'); print(TOTAL3); sys.exit()
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-'] + audio3() +
        ['-map', '0:v', '-map', '[a]', '-c:v', 'libx264', '-preset', 'slow', '-crf', '19', '-maxrate', '7M', '-bufsize', '14M', '-profile:v', 'high', '-r', '30',
         '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-t', f'{TOTAL3}', '-movflags', '+faststart', HERE + '/yesha-bar-dalia.mp4'], stdin=subprocess.PIPE)
    for i in range(int(round(TOTAL3 * FPS))): ff.stdin.write(frame3(i / FPS).tobytes())
    ff.stdin.close(); ff.wait(); print('done', TOTAL3)
