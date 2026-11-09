"""Yesha reel - בוסתן דוד (9:16). User's narration (face not shown) + the mother's own voice + site footage. Splice music, no singing.
Yesha rules: white logo top-right, Karantina headlines with blue offset shadow, blue label boxes, no exclamation marks, calm motion."""
import os, sys, math, glob, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
HERE = os.path.dirname(os.path.abspath(__file__)); FT = HERE + '/footage/'; PH = HERE + '/photos/'
P = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/bustan/prep/'; os.makedirs(P, exist_ok=True)
KB = glob.glob('/root/.claude/skills/synced/*/pro-video-editing/assets/fonts/Karantina-Bold.ttf')[0]
SEC = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/shalev/fonts/SecularOne.ttf'
LOGO = HERE + '/../../clients/yesha/logo_white.png'
EMO = '/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'
W, H, FPS = 1080, 1920, 30
BLUE = (0x25, 0x66, 0xA2); NAVY = (0x17, 0x40, 0x68); LB = (0x27, 0xA4, 0xD1); WHITE = (255, 255, 255)
MOM_D = 6.35; P1_END = 16.6; P2_START = 16.75
MOM_AT = P1_END - .45 + .15; OFF2 = MOM_AT + MOM_D + .15 - P2_START
CUT = (26.0, 29.25)   # removed: 'נשתלו עצים שהגיעו מבארי' (unverified) -> 'והיום, בבוסתן שנבנה לזכרו, שתי בריכות מים...'
CD = CUT[1] - CUT[0]
def V(nt): return nt - 0.45 if nt < P1_END else (nt + OFF2 if nt < CUT[0] else nt + OFF2 - CD)
VO_END = 62.6
TOTAL = V(VO_END) + 2.6
_f = {}
def F(p, s):
    k = (p, s)
    if k not in _f: _f[k] = ImageFont.truetype(p, s, layout_engine=ImageFont.Layout.RAQM)
    return _f[k]
def eo(x): x = max(0., min(1., x)); return 1 - (1 - x) ** 3
def ss(x): x = max(0., min(1., x)); return x * x * (3 - 2 * x)

# ---------- shots: (narration start, narration end, kind, source, in-point, speed) ----------
SHOTS = [(0.45, 2.2, 'img', 'p4-97140d1b.jpg', 0, 1), (2.2, 4.9, 'vid', 'IMG_8174.mov', 1.0, 1), (4.9, 7.0, 'vid', 'IMG_8184.mov', 0.0, 1),
         (7.0, 9.4, 'vid', 'IMG_8184.mov', 2.1, 1), (9.4, 11.1, 'vid', 'IMG_8163.mov', 0.0, .9), (11.1, 13.8, 'img', 'p5-901abf95.jpg', 0, 1),
         (13.8, P1_END, 'vid', 'IMG_8175.mov', 0.5, 1),
         (P2_START, 23.4, 'img', 'p3-0ea0cbf0.jpg', 0, 1),            # the plaque: 'שמסר את חייו למעננו בשמחת תורה תשפ"ד'
         (23.4, 29.3, 'vid', 'IMG_8157.mov', 0.0, .85),               # 'והיום, בבוסתן שנבנה לזכרו' - the site being built, flag
         (29.3, 31.4, 'vid', 'IMG_8182.mov', 4.0, 1), (31.4, 33.3, 'vid', 'IMG_8179.mov', 0.5, 1), (33.3, 35.6, 'vid', 'IMG_8166.mov', 0.2, 1),
         (35.6, 40.4, 'vid', 'IMG_8162.mov', 0.0, 1), (40.4, 43.3, 'vid', 'IMG_8160.mov', 0.0, .8), (43.3, 46.2, 'vid', 'IMG_8161.mov', 0.0, 1),
         (46.2, 48.4, 'vid', 'IMG_8168.mov', 0.8, 1), (48.4, 50.0, 'vid', 'IMG_8187.mov', 1.0, 1), (50.0, 51.6, 'vid', 'IMG_8170.mov', 3.0, 1),
         (51.6, 54.0, 'vid', 'IMG_8180.mov', 0.3, 1), (54.0, 56.3, 'vid', 'IMG_8161.mov', 9.0, 1), (56.3, 59.4, 'vid', 'IMG_8181.mov', 0.5, 1),
         (59.4, 99, 'vid', 'IMG_8174.mov', 3.5, .7)]
SUBS = [(0.75, 2.0, 'נוסעים בכביש 90?'), (2.41, 4.47, 'יש עצירה שאתם חייבים לעשות.'), (5.04, 5.92, 'בוסתן דוד,'), (6.30, 9.11, 'על שם רס״ן דוד מאיר הי״ד,'),
        (9.57, 10.64, 'מכוכב השחר.'), (11.26, 13.7, 'קצין בסיירת מטכ״ל, איש של שטח,'), (13.7, 16.43, 'שהכיר את הארץ כמו את כף ידו.'),
        (16.88, 17.85, 'בשמחת תורה,'), (18.46, 21.66, 'דוד נלחם בגבורה בקרבות בבארי,'), (22.23, 23.02, 'ושם נפל.'),
        (23.75, 25.87, 'והיום, בבוסתן שנבנה לזכרו,'),
        (29.35, 31.26, 'שתי בריכות מים אקולוגיות,'), (31.62, 33.06, 'נוף שעוצר את הנשימה,'), (33.56, 35.42, 'ועגלת קפה עם מאפים טריים,'),
        (35.83, 37.08, 'סנדוויצ\'ים מושקעים,'), (37.59, 39.68, 'וקפה שמחמם את הלב.'), (40.64, 43.3, 'את המצפה מימן עם ישראל, בגיוס המונים,'),
        (43.3, 45.96, 'ובנו אותו חבריו ליחידה,'), (46.40, 48.16, 'מכינות קדם־צבאיות,'), (48.64, 51.27, 'ונוער מכל הארץ ומכל העולם.'),
        (51.78, 53.68, 'מקום פתוח לכל עם ישראל,'), (54.06, 56.08, 'לצעוד בשבילים שדוד אהב.'), (56.47, 59.08, 'אז בפעם הבאה בכביש 90,'), (59.54, 61.68, 'רושמים בוויז: בוסתן דוד.')]

def prep():
    for i, (a, b, kind, src, t0, sp) in enumerate(SHOTS):
        if kind != 'vid': continue
        d = P + f's{i:02d}/'
        if os.path.exists(d + '0001.jpg'): continue
        os.makedirs(d, exist_ok=True); dur = (min(b, VO_END) - a + .6) * sp
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(t0), '-t', f'{dur:.2f}', '-i', FT + src, '-vf', f'setpts=PTS/{sp},fps={FPS},scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,eq=saturation=1.08:contrast=1.04', '-q:v', '3', d + '%04d.jpg'], check=True)
    d = P + 'mom/'
    if not os.path.exists(d + '0001.jpg'):
        os.makedirs(d, exist_ok=True); subprocess.run(['ffmpeg', '-v', 'error', '-y', '-t', str(MOM_D + .1), '-i', FT + 'mother.mov', '-vf', f'fps={FPS}', '-q:v', '3', d + '%04d.jpg'], check=True)
_ls = {}
def frames(d):
    if d not in _ls: _ls[d] = sorted(os.listdir(d))
    return _ls[d]
_img = {}
def photo(name):
    if name not in _img:
        im = Image.open(PH + name).convert('RGB'); s = max(W * 1.15 / im.width, H * 1.15 / im.height)
        _img[name] = ImageEnhance.Color(im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)).enhance(1.06)
    return _img[name]
def shot_frame(i, nt):
    a, b, kind, src, t0, sp = SHOTS[i]; u = nt - a; dur = max(.1, min(b, VO_END + 2) - a)
    if kind == 'img':
        im = photo(src); k = u / dur; z = 1 + .08 * k
        if 'p7' in src: cx, cy = .80 * im.width, .55 * im.height; z = 1 + .25 * ss(k)        # push in on the young trees
        elif 'p5' in src: cx, cy = .5 * im.width, .45 * im.height
        else: cx, cy = im.width / 2, im.height / 2
        w, h = W / z * (im.width / (W * 1.15)) * 1.15 / (im.width / (W * 1.15)) / 1.0, H / z
        w = W / z * (im.width / (im.width)); cw, ch = int(W * 1.0 / z * (im.width / (W * 1.15)) / (im.width / (W * 1.15))), int(H / z)
        cw = min(im.width, int(W / z * 1.0)); ch = min(im.height, int(H / z))
        x0 = int(max(0, min(im.width - cw, cx - cw / 2))); y0 = int(max(0, min(im.height - ch, cy - ch / 2)))
        return im.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.BILINEAR)
    fs = frames(P + f's{i:02d}/'); im = Image.open(P + f's{i:02d}/' + fs[max(0, min(len(fs) - 1, int(u * FPS)))]).convert('RGB')
    z = 1 + .04 * min(1, u / dur); return im.resize((int(W * z), int(H * z)), Image.BILINEAR).crop((int((W * z - W) / 2), int((H * z - H) / 2), int((W * z - W) / 2) + W, int((H * z - H) / 2) + H))
def base(nt):
    for i, (a, b, *_ ) in enumerate(SHOTS):
        if a <= nt < b:
            f = shot_frame(i, nt)
            if i + 1 < len(SHOTS) and b - nt < .25: f = Image.blend(f, shot_frame(i + 1, b + .001), (1 - (b - nt) / .25) * .5)
            if i > 0 and nt - a < .25 and SHOTS[i - 1][1] == a: f = Image.blend(shot_frame(i - 1, a - .001), f, .5 + (nt - a) / .5)
            return f
    return shot_frame(0, .45)

# ---------- graphics ----------
LG = Image.open(LOGO).convert('RGBA'); LG = LG.crop(LG.getchannel('A').getbbox()); LG = LG.resize((170, int(170 * LG.height / LG.width)), Image.LANCZOS)
GRAD = Image.new('RGBA', (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(GRAD)
for y in range(H):
    a = int(170 * max(0, (y - H * .62) / (H * .38)) ** 1.4) + int(90 * max(0, (H * .14 - y) / (H * .14)))
    gd.line((0, y, W, y), fill=(5, 14, 28, a))
def headline(d, xy, s, size, anchor='ma'):
    f = F(KB, size); d.text((xy[0] + 6, xy[1] + 6), s, font=f, fill=BLUE, anchor=anchor, direction='rtl'); d.text(xy, s, font=f, fill=WHITE, anchor=anchor, direction='rtl')
def label(im, s, cx, y, size=52, alpha=1.):
    d = ImageDraw.Draw(im); f = F(SEC, size); tw = d.textlength(s, font=f, direction='rtl')
    lay = Image.new('RGBA', (int(tw) + 60, size + 36), BLUE + (int(255 * alpha),)); ImageDraw.Draw(lay).text((lay.width / 2, 12), s, font=f, fill=(255, 255, 255, int(255 * alpha)), anchor='ma', direction='rtl')
    im.alpha_composite(lay, (int(cx - lay.width / 2), int(y)))
def wrap(d, s, f, maxw):
    out, cur = [], ''
    for w in s.split():
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=f, direction='rtl') <= maxw: cur = t
        else: out.append(cur); cur = w
    return out + [cur]
def subtitle(im, nt):
    for a, b, s in SUBS:
        if a - .05 <= nt < b + .25:
            p = eo((nt - a + .05) / .2); d = ImageDraw.Draw(im); f = F(KB, 96); lines = wrap(d, s, f, 940)
            y0 = 1560 - (len(lines) - 1) * 92 + 20 * (1 - p)
            for k, l in enumerate(lines): headline(d, (W / 2, y0 + k * 92), l, 96)
            return
_em = {}
def emoji(ch, size):
    if (ch, size) not in _em:
        im = Image.new('RGBA', (170, 170), (0, 0, 0, 0)); ImageDraw.Draw(im).text((12, 12), ch, font=ImageFont.truetype(EMO, 109), embedded_color=True)
        im = im.crop(im.getbbox()); _em[(ch, size)] = im.resize((size, int(size * im.height / im.width)), Image.LANCZOS)
    return _em[(ch, size)]
def overlays(im, nt, vt):
    d = ImageDraw.Draw(im)
    if 0.45 <= nt < 4.9: label(im, 'כביש 90 · בקעת הירדן', W / 2, 300, 50, eo((nt - .6) / .4))
    if 4.9 <= nt < 7.0:
        p = eo((nt - 5.0) / .5); lay = Image.new('RGBA', (W, 330), (0, 0, 0, 0)); headline(ImageDraw.Draw(lay), (W / 2, 10), 'בוסתן דוד', 250)
        lay.putalpha(lay.getchannel('A').point(lambda v: int(v * p))); im.alpha_composite(lay, (0, int(560 + 40 * (1 - p))))
    if 6.3 <= nt < 11.1:
        p = eo((nt - 6.3) / .4); label(im, 'רס״ן דוד מאיר הי״ד', W / 2, 300, 60, p)
        if nt > 9.4: label(im, 'כוכב השחר', W / 2, 400, 46, eo((nt - 9.5) / .4))
    if 29.1 <= nt < 40.4 and nt < 29.1 + 99: pass
    if 40.4 <= nt < 43.3: label(im, 'בגיוס המונים מכל הארץ', W / 2, 300, 50, eo((nt - 40.5) / .4))
    if nt >= 59.3:   # navigation search: 'בוסתן דוד'
        u = nt - 59.3; p = eo(u / .4); bar = Image.new('RGBA', (900, 150), (0, 0, 0, 0)); bd = ImageDraw.Draw(bar)
        bd.rounded_rectangle((0, 0, 899, 149), 75, fill=(255, 255, 255, 245)); bd.ellipse((790, 45, 850, 105), outline=(120, 120, 120), width=8); bd.line((840, 95, 870, 125), fill=(120, 120, 120), width=9)
        txt = 'בוסתן דוד'; n = int(max(0, min(len(txt), (u - .4) / .1))); bd.text((750, 34), txt[:n], font=F(SEC, 70), fill=(30, 30, 30), anchor='ra', direction='rtl')
        if int(u * 2.5) % 2 == 0 and n < len(txt): bd.line((750 - bd.textlength(txt[:n], font=F(SEC, 70), direction='rtl') - 6, 40, 750 - bd.textlength(txt[:n], font=F(SEC, 70), direction='rtl') - 6, 110), fill=LB, width=5)
        bar.putalpha(bar.getchannel('A').point(lambda v: int(v * p))); im.alpha_composite(bar, (90, int(760 + 40 * (1 - p))))
        if u > 1.6:
            q = eo((u - 1.6) / .35); pin = emoji('📍', 150); im.alpha_composite(pin, (int(W / 2 - pin.width / 2), int(470 + 150 * (1 - q) - 0)))
        if u > 2.2: label(im, 'כביש 90 · בקעת הירדן', W / 2, 960, 46, eo((u - 2.2) / .4))
    if vt > TOTAL - 2.6:   # end: logo in the centre
        u = vt - (TOTAL - 2.6); lg = Image.open(LOGO).convert('RGBA'); lg = lg.crop(lg.getchannel('A').getbbox()); lg = lg.resize((420, int(420 * lg.height / lg.width)), Image.LANCZOS)
        lg.putalpha(lg.getchannel('A').point(lambda v: int(v * eo((u - .3) / .6)))); im.alpha_composite(lg, (int(W / 2 - 210), 1180))
def mom_frame(u):
    fs = frames(P + 'mom/'); fr = Image.open(P + 'mom/' + fs[max(0, min(len(fs) - 1, int(u * FPS)))]).convert('RGB')
    bg = fr.resize((int(H * fr.width / fr.height), H), Image.BILINEAR); x0 = (bg.width - W) // 2; bg = ImageEnhance.Brightness(bg.crop((x0, 0, x0 + W, H)).filter(ImageFilter.GaussianBlur(30))).enhance(.55)
    im = bg.convert('RGBA'); fg = fr.resize((W, int(W * fr.height / fr.width)), Image.LANCZOS); im.paste(fg, (0, (H - fg.height) // 2))
    label(im, 'חיה מאיר, אמא של דוד', W / 2, (H - fg.height) // 2 - 130, 56, eo(u / .5))
    return im
def frame(vt):
    if MOM_AT <= vt < MOM_AT + MOM_D:
        im = mom_frame(vt - MOM_AT); u = vt - MOM_AT
        if u < .3: im = Image.blend(base(P1_END - .001).convert('RGBA'), im, u / .3)
        if MOM_AT + MOM_D - vt < .3: im = Image.blend(im, base(P2_START).convert('RGBA'), 1 - (MOM_AT + MOM_D - vt) / .3)
    else:
        if vt < MOM_AT: nt = min(vt + .45, P1_END - .001)
        else:
            nt = max(vt - OFF2, P2_START)
            if nt >= CUT[0]: nt += CD
        nt = max(nt, .45)
        im = base(nt).convert('RGBA'); im.alpha_composite(GRAD); overlays(im, nt, vt); subtitle(im, nt)
        if vt < .5: im = Image.blend(Image.new('RGBA', (W, H), (0, 0, 0, 255)), im, vt / .5)
    im.alpha_composite(LG, (W - 60 - LG.width, 70))
    return im.convert('RGB')

def audio(out):
    T = f'{TOTAL:.2f}'
    fl = [f'[0:a]atrim=0.6:{P1_END},asetpts=PTS-STARTPTS,afade=t=out:st={P1_END - .6 - .08:.2f}:d=0.08,adelay={int(V(.6) * 1000)}:all=1[a1]',
          f'[0:a]atrim={P2_START}:{CUT[0]},asetpts=PTS-STARTPTS,afade=t=in:d=0.05,afade=t=out:st={CUT[0] - P2_START - .06:.2f}:d=0.06,adelay={int(V(P2_START) * 1000)}:all=1[a2]',
          f'[0:a]atrim={CUT[1]}:{VO_END},asetpts=PTS-STARTPTS,afade=t=in:d=0.05,adelay={int(V(CUT[1]) * 1000)}:all=1[a3]',
          f'[1:a]aformat=sample_rates=48000:channel_layouts=mono,atrim=0:{MOM_D},asetpts=PTS-STARTPTS,highpass=f=80,loudnorm=I=-16:TP=-1.5,afade=t=in:d=0.15,afade=t=out:st={MOM_D - .3:.2f}:d=0.3,adelay={int(MOM_AT * 1000)}:all=1[mo]',
          '[a1][a2][a3][mo]amix=inputs=4:normalize=0,aformat=sample_rates=48000:channel_layouts=stereo,asplit=2[voice][key]',
          f"[2:a]aformat=sample_rates=48000:channel_layouts=stereo,aloop=loop=3:size={int(25.6 * 48000)},atrim=0:{T},volume='if(between(t,{MOM_AT - .5:.2f},{V(CUT[1]):.2f}),0.16,if(gt(t,{V(59.3):.2f}),0.42,0.30))':eval=frame,afade=t=in:d=1.0,afade=t=out:st={TOTAL - 2.0:.2f}:d=2.0[m]",
          '[m][key]sidechaincompress=threshold=0.03:ratio=3:attack=25:release=400[md]',
          f'[voice][md]amix=inputs=2:normalize=0,alimiter=limit=0.95,apad=whole_dur={T},atrim=0:{T}[o]']
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', HERE + '/vo_clean.wav', '-i', FT + 'mother.mov', '-i', HERE + '/music.wav', '-filter_complex', ';'.join(fl), '-map', '[o]', out], check=True)

if __name__ == '__main__':
    prep()
    if 'stills' in sys.argv:
        ts = [1.0, 3.5, 6.0, 8.5, 10.5, 12.5, 15.0, MOM_AT + 3, V(20), V(25), V(30), V(32.5), V(34.5), V(38), V(41.5), V(45), V(49.5), V(52.5), V(55), V(58), V(60.5), TOTAL - 1]
        ims = [frame(x).resize((180, 320)) for x in ts]; sh = Image.new('RGB', (11 * 184, 2 * 324), WHITE)
        for i, x in enumerate(ims): sh.paste(x, ((i % 11) * 184, (i // 11) * 324))
        sh.save(P + '../stills.jpg'); print(TOTAL); sys.exit()
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', P + 'v.mp4'], stdin=subprocess.PIPE)
    for i in range(int(round(TOTAL * FPS))): ff.stdin.write(frame(i / FPS).tobytes())
    ff.stdin.close(); ff.wait()
    audio(P + 'a.wav')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', P + 'v.mp4', '-i', P + 'a.wav', '-map', '0:v', '-map', '1:a', '-vf', 'scale=720:1280:flags=lanczos', '-c:v', 'libx264', '-preset', 'slow', '-b:v', '2200k', '-maxrate', '3000k', '-bufsize', '6000k', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-t', f'{TOTAL:.2f}', '-movflags', '+faststart', P + 'mux.mp4'], check=True)
    LN = glob.glob('/root/.claude/skills/synced/*/pro-video-editing/scripts/loudnorm.py')[0]
    subprocess.run(['python3', LN, P + 'mux.mp4', HERE + '/yesha-bustan-david.mp4', '--target', '-14'], check=True)
    print('done', TOTAL)
