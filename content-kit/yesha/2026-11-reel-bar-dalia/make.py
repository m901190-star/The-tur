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
        os.makedirs(d, exist_ok=True); dur = (min(b, TOTAL) - a + .6) * sp
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(t0), '-t', f'{dur:.2f}', '-i', FT + src, '-vf', f'setpts=PTS/{sp},fps={FPS},' + ('crop=iw*0.62:ih*0.62:iw*0.19:ih*0.04,' if src == 'v11.mov' else '') + 'scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,eq=saturation=1.08:contrast=1.04', '-q:v', '3', d + '%04d.jpg'], check=True)
_ls, _img = {}, {}
def photo(n):
    if n not in _img:
        im = Image.open(PH + n).convert('RGB'); s = max(W * 1.15 / im.width, H * 1.15 / im.height)
        _img[n] = ImageEnhance.Color(im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)).enhance(1.06)
    return _img[n]
def shot(i, t):
    a, b, kind, src, t0, sp = SHOTS[i]; u = t - a; dur = max(.1, min(b, TOTAL) - a)
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
            if i + 1 < len(SHOTS) and b - t < .25: f = Image.blend(f, shot(i + 1, b + .001), (1 - (b - t) / .25) * .5)
            if i > 0 and t - a < .25: f = Image.blend(shot(i - 1, a - .001), f, .5 + (t - a) / .5)
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
if __name__ == '__main__':
    prep()
    if 'stills' in sys.argv:
        ts = [2, 6, 11, 17, 24, 30, 37, 42, 46.5, 50, 53, 56, 60, 63, 67.5]
        ims = [frame(x).resize((180, 320)) for x in ts]; sh = Image.new('RGB', (8 * 184, 2 * 324), WHITE)
        for i, x in enumerate(ims): sh.paste(x, ((i % 8) * 184, (i // 8) * 324))
        sh.save(P + '../stills.jpg'); print(TOTAL); sys.exit()
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', HERE + '/vo_clean.wav', '-i', HERE + '/../2026-11-reel-bustan-david/music.wav',
        '-filter_complex', f"[1:a]atrim=0:{VO_END},aformat=sample_rates=48000:channel_layouts=stereo,apad=whole_dur={TOTAL},asplit=2[v][k];[2:a]aformat=sample_rates=48000:channel_layouts=stereo,aloop=loop=3:size={int(25.6*44100)},atrim=0:{TOTAL},volume='if(between(t,26.5,33.6),0.12,if(gt(t,{VO_END}),0.55,0.30))':eval=frame,afade=t=in:d=1,afade=t=out:st={TOTAL-2}:d=2[m];[m][k]sidechaincompress=threshold=0.03:ratio=3:attack=20:release=350[md];[v][md]amix=inputs=2:normalize=0,alimiter=limit=0.95[a]", '-map', '0:v', '-map', '[a]', '-vf', 'scale=720:1280:flags=lanczos',
        '-c:v', 'libx264', '-preset', 'slow', '-b:v', '2200k', '-maxrate', '3000k', '-bufsize', '6000k', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-t', f'{TOTAL}', '-movflags', '+faststart', HERE + '/yesha-bar-dalia.mp4'], stdin=subprocess.PIPE)
    for i in range(int(round(TOTAL * FPS))): ff.stdin.write(frame(i / FPS).tobytes())
    ff.stdin.close(); ff.wait(); print('done', TOTAL)
