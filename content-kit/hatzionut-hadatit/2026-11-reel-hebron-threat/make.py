"""Smotrich reel: the Hebron suspect who threatened to murder him (+ Strock) — arrest bodycam + KAN Reshet Bet audio as the hook,
then Smotrich to camera. Over his PA lines: the real headlines as paper clippings with an animated yellow marker on the Fatah/PA link.
No captions (Moshe captions in CapCut). 1080x1920."""
import os, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); KIT = os.path.abspath(HERE + '/../..')
HAIM = KIT + '/fonts/HaimClassicv2FM-Bold.ttf'
W, H, FPS = 1080, 1920, 30
YEL = (255, 222, 0)
SM, AR, NEWS = HERE + '/src/smotrich.mov', HERE + '/src/arrest.mov', HERE + '/src/news.mov'
MUSIC = HERE + '/music/verbbass_cm_100.wav'
def F(s): return ImageFont.truetype(HAIM, s, layout_engine=ImageFont.Layout.RAQM)
def ease(t): t = max(0., min(1., t)); return 1 - (1 - t) ** 3
def eio(t): t = max(0., min(1., t)); return t * t * (3 - 2 * t)

# ---------------- timeline ----------------
HOOK = [(7.7, 1.3), (10.0, 2.3), (13.0, 2.6)]          # arrest: flashlight entry -> cuffed on the floor -> taken down the stairs
HOOK_D = sum(d for _, d in HOOK)
NEWS_IN, NEWS_A, NEWS_B = 0.15, 6.30, 11.74            # "תושב חברון בן 20, חשוד שאיים לרצוח את השרים סטרוק, סמוטריץ' ונבחרים נוספים"
SM_A, SM_B = 4.0, 40.98                                  # from "ראיתי שעצרו מחבל…" (the off-camera question is dropped)
C1 = (7.2, 11.3)    # Haredim10 clipping: "וקיבל כסף מהפת״ח"       (src time in smotrich.mov)
C2 = (11.3, 14.0)   # i24 clipping: "יצר קשר עם גורמים ברש״פ לצורך קבלת הכשרה צבאית"
PUNCH = [(14.0, 1.10), (26.6, 1.14)]                    # punch-ins on "לא ירתיעו…" and "מדינת טרור בלב ליבה…"
TOTAL = HOOK_D + (SM_B - SM_A)

# ---------------- clippings ----------------
def torn(card, seed):
    """paper clipping: ragged top/bottom edges + soft shadow, returns RGBA with margin"""
    rng = np.random.default_rng(seed); w, h = card.size
    m = Image.new('L', (w, h), 255); d = ImageDraw.Draw(m)
    for edge in ('top', 'bot'):
        xs = np.arange(0, w + 12, 12); ys = np.cumsum(rng.normal(0, 2.2, len(xs))); ys = np.clip(ys - ys.mean(), -7, 7) + 9
        pts = [(x, y if edge == 'top' else h - y) for x, y in zip(xs, ys)]
        d.polygon(pts + ([(w, 0), (0, 0)] if edge == 'top' else [(w, h), (0, h)]), fill=0)
    out = Image.new('RGBA', (w + 120, h + 120), (0, 0, 0, 0))
    sh = Image.new('L', out.size, 0); sh.paste(m, (60 + 14, 60 + 22)); sh = sh.filter(ImageFilter.GaussianBlur(18))
    out.paste(Image.new('RGBA', out.size, (0, 0, 0, 255)), (0, 0), sh.point(lambda v: int(v * .65)))
    c = card.convert('RGBA'); c.putalpha(m); out.alpha_composite(c, (60, 60)); return out

def stack(path, parts):
    im = Image.open(path).convert('RGB'); ws = im.width
    hs = sum(b - a for a, b in parts); out = Image.new('RGB', (ws, hs)); y = 0; offs = []
    for a, b in parts: out.paste(im.crop((0, a, ws, b)), (0, y)); offs.append((a, y)); y += b - a
    return out, offs

def remap(offs, y):  # source y -> stacked y
    for a, yy in reversed(offs):
        if y >= a: return yy + (y - a)

CARD_W = 960
def build(path, parts, marks, dark, seed):
    base, offs = stack(path, parts); s = CARD_W / base.width
    base = base.resize((CARD_W, int(base.height * s)), Image.LANCZOS)
    boxes = [(x0 * s, remap(offs, y0) * s, x1 * s, remap(offs, y1) * s) for (x0, y0, x1, y1) in marks]
    return base, boxes, dark, seed

C_H10 = build(HERE + '/src/h_haredim10.jpg', [(20, 210), (770, 1320)],
              [(138, 1118, 566, 1222), (902, 1214, 1268, 1300)], True, 3)
C_I24 = build(HERE + '/src/h_i24.jpg', [(0, 300), (330, 1260)],
              [(156, 1090, 456, 1160), (300, 1174, 1282, 1244)], False, 7)
C_YNET = build(HERE + '/src/h_ynet.jpg', [(20, 200), (215, 545)], [], False, 11)

def marked(card, t, t0=.55, per=.42):
    """yellow marker swept right->left over each box, one after another"""
    base, boxes, dark, seed = card; im = base.copy()
    a = np.asarray(im).astype(np.float32) / 255
    for i, (x0, y0, x1, y1) in enumerate(boxes):
        p = eio((t - t0 - i * per) / per)
        if p <= 0: continue
        xl = x1 - (x1 - x0) * p
        X0, X1, Y0, Y1 = int(xl), int(x1), int(y0), int(y1)
        reg = a[Y0:Y1, X0:X1]; yel = np.array(YEL, np.float32) / 255
        L = reg.mean(2, keepdims=True)
        reg[:] = yel * (1 - L) if dark else reg * yel          # dark page: white text turns black on yellow
        a[Y0:Y1, X0:X1] = reg
    return torn(Image.fromarray((a * 255).astype(np.uint8)), seed)

# ---------------- small labels ----------------
def label(txt, size=40, fg=(255, 255, 255), bg=(0, 0, 0, 150), padx=22, pady=12):
    f = F(size); d = ImageDraw.Draw(Image.new('RGB', (1, 1)))
    bb = d.textbbox((0, 0), txt, font=f, anchor='ls', direction='rtl'); tw, th = bb[2] - bb[0], bb[3] - bb[1]
    im = Image.new('RGBA', (tw + 2 * padx, th + 2 * pady), bg); ImageDraw.Draw(im).text((padx + tw, pady - bb[1]), txt, font=f, fill=fg, anchor='rs', direction='rtl')
    return im
CREDIT = label('צילום: דוברות המשטרה', 30, bg=(0, 0, 0, 110), padx=16, pady=9)
KAN = label('כאן חדשות | רשת ב׳', 48)

# news waveform bars (real amplitude of the KAN clip)
sr = 48000
def load(p, ss=0, t=None, af=None):
    c = ['ffmpeg', '-v', 'error', '-ss', str(ss)] + (['-t', str(t)] if t else []) + ['-i', p] + (['-af', af] if af else []) + ['-ac', '2', '-ar', str(sr), '-f', 'f32le', '-']
    return np.frombuffer(subprocess.run(c, capture_output=True).stdout, np.float32).reshape(-1, 2).copy()
news = load(NEWS, NEWS_A, NEWS_B - NEWS_A, 'highpass=f=90,loudnorm=I=-16:TP=-2')
nm = news[:, 0]; hop = sr // FPS
env = np.array([np.sqrt((nm[i * hop:(i + 1) * hop] ** 2).mean() + 1e-9) for i in range(len(nm) // hop)]); env = env / (env.max() + 1e-9)

def bars(t):
    k = int((t - NEWS_IN) * FPS); n = 23; im = Image.new('RGBA', (n * 18, 90), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i in range(n):
        j = k - abs(i - n // 2) * 2; v = env[j] if 0 <= j < len(env) else 0
        h = 8 + v * 78 * (0.65 + 0.35 * np.sin(i * 1.7 + k * .3) ** 2)
        d.rounded_rectangle((i * 18, 45 - h / 2, i * 18 + 9, 45 + h / 2), 4, fill=(255, 255, 255, 235))
    return im

# ---------------- video ----------------
def frames(src, t0, dur, vf):
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', f'{t0:.3f}', '-t', f'{dur:.3f}', '-i', src, '-vf', vf,
                          '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    n = 0; last = None; N = int(round(dur * FPS))
    while n < N:
        b = p.stdout.read(W * H * 3)
        if len(b) < W * H * 3: break
        last = Image.frombytes('RGB', (W, H), b); yield last; n += 1
    p.stdout.close(); p.kill(); p.wait()
    while n < N and last is not None: yield last; n += 1

AR_VF = f'crop=405:720:437:0,scale={W}:{H}:flags=bicubic,fps={FPS},eq=contrast=1.12:saturation=0.75:brightness=0.03,noise=alls=10:allf=t'
SM_VF = f'scale={W}:{H}:flags=lanczos,fps={FPS},eq=contrast=1.04:saturation=1.04'
vign = Image.radial_gradient('L').resize((W, H)).point(lambda v: int(min(255, max(0, v - 90) * 1.0)))
dark = Image.new('RGB', (W, H), (0, 0, 0))

enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                        '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-pix_fmt', 'yuv420p', HERE + '/_video.mp4'], stdin=subprocess.PIPE)
T = 0.0
for (a, d) in HOOK:
    for k, fr in enumerate(frames(AR, a, d, AR_VF)):
        t = T + k / FPS
        im = Image.composite(dark, fr, vign).convert('RGBA')
        # ynet clipping drops over the last shot
        if t > 3.75:
            e = ease((t - 3.75) / .35)
            im = Image.blend(im.convert('RGB'), Image.new('RGB', (W, H)), .45 * e).convert('RGBA')
            c = torn(C_YNET[0], C_YNET[3]).rotate(-1.6, resample=Image.BICUBIC, expand=True)
            c = c.resize((int(c.width * (1.08 - .08 * e)), int(c.height * (1.08 - .08 * e))), Image.LANCZOS)
            c.putalpha(c.getchannel('A').point(lambda v: int(v * e)))
            im.alpha_composite(c, ((W - c.width) // 2, 520 - c.height // 2 + int((1 - e) * -40)))
        if NEWS_IN <= t < NEWS_IN + len(env) / FPS + .3:
            ke = ease((t - NEWS_IN) / .3)
            b = bars(t); tag = KAN.copy()
            blk = Image.new('RGBA', (max(b.width, tag.width), b.height + tag.height + 14), (0, 0, 0, 0))
            blk.alpha_composite(tag, ((blk.width - tag.width) // 2, 0)); blk.alpha_composite(b, ((blk.width - b.width) // 2, tag.height + 14))
            blk.putalpha(blk.getchannel('A').point(lambda v: int(v * ke)))
            im.alpha_composite(blk, ((W - blk.width) // 2, 1330))
        if 1.3 <= t < HOOK_D: im.alpha_composite(CREDIT, (W - CREDIT.width - 40, 1700))
        enc.stdin.write(im.convert('RGB').tobytes())
    T += d

def zoom_at(st):
    if 14.0 <= st < 20.0: return 1.10                       # hard punch-in on "לא ירתיעו…", back to wide at 20.0
    if st >= 26.6: return 1.0 + .14 * eio((st - 26.6) / 3.9)  # slow push on "מדינת טרור בלב ליבה…"
    return 1.0

for k, fr in enumerate(frames(SM, SM_A, SM_B - SM_A, SM_VF)):
    st = SM_A + k / FPS
    z = zoom_at(st)
    if z > 1.001:
        cw, ch = int(W / z), int(H / z); x0 = (W - cw) // 2; y0 = int((H - ch) * .28)
        fr = fr.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.LANCZOS)
    im = fr.convert('RGBA')
    for (c0, c1), card, rot in [(C1, C_H10, 1.2), (C2, C_I24, -1.4)]:
        if c0 <= st < c1:
            tt = st - c0; e = ease(tt / .32)
            first = (c0, c1) == C1
            out = 1.0 if first else 1 - ease((st - (c1 - .25)) / .25)
            bg = fr.filter(ImageFilter.GaussianBlur(22)); bg = Image.blend(bg, Image.new('RGB', (W, H), (12, 12, 14)), .55)
            im = Image.blend(fr, bg, (e if first else 1.0) * out).convert('RGBA')
            e = e if first else max(e, 0.0)
            c = marked(card, tt).rotate(rot, resample=Image.BICUBIC, expand=True)
            sc = (1.0 + .035 * (tt / (c1 - c0))) * (0.92 + .08 * e)
            c = c.resize((int(c.width * sc), int(c.height * sc)), Image.LANCZOS)
            c.putalpha(c.getchannel('A').point(lambda v: int(v * (1.0 if not first else e) * out)))
            dx = int((1 - e) * (140 if (c0, c1) == C2 else 0)); dy = int((1 - e) * 60 if (c0, c1) == C1 else 0)
            im.alpha_composite(c, ((W - c.width) // 2 + dx, (H - c.height) // 2 - 60 + dy))
    if st > SM_B - .45: im = Image.blend(im.convert('RGB'), Image.new('RGB', (W, H)), (st - (SM_B - .45)) / .45).convert('RGBA')
    enc.stdin.write(im.convert('RGB').tobytes())
enc.stdin.close(); enc.wait()

# ---------------- audio ----------------
N = int(TOTAL * sr); out = np.zeros((N, 2), np.float32)
def add(x, t, g):
    i = int(t * sr); m = min(len(x), N - i); out[i:i + m] += g * x[:m]
T = 0
for (a, d) in HOOK:                                       # bodycam room tone, low
    x = load(AR, a, d); x /= np.abs(x).max() + 1e-9
    f = np.ones(len(x)); r = int(.04 * sr); f[:r] = np.linspace(0, 1, r); f[-r:] = np.linspace(1, 0, r); add(x * f[:, None], T, .10); T += d
f = np.ones(len(news)); r = int(.06 * sr); f[:r] = np.linspace(0, 1, r); f[-int(.12 * sr):] = np.linspace(1, 0, int(.12 * sr))
add(news * f[:, None], NEWS_IN, 1.0)
v = load(SM, SM_A, SM_B - SM_A, 'highpass=f=80,afftdn=nf=-25,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,loudnorm=I=-16:TP=-1.5')
f = np.ones(len(v)); f[-int(.4 * sr):] = np.linspace(1, 0, int(.4 * sr)); add(v * f[:, None], HOOK_D, 1.0)
m = load(MUSIC); m /= np.abs(m).max() + 1e-9; m = np.tile(m, (int(np.ceil(N / len(m))) + 1, 1))[:N]
tt = np.arange(N) / sr
lvl = np.interp(tt, [0, .4, HOOK_D - .3, HOOK_D + .4, TOTAL - 1.5, TOTAL], [0, .30, .30, .085, .085, 0])
out += m * lvl[:, None]
out.tofile(HERE + '/_a.raw')
final = HERE + '/smotrich-hebron-threat-reel.mp4'
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', HERE + '/_video.mp4', '-f', 'f32le', '-ar', str(sr), '-ac', '2', '-i', HERE + '/_a.raw',
                '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000',
                '-movflags', '+faststart', '-shortest', final], check=True)
os.remove(HERE + '/_a.raw'); os.remove(HERE + '/_video.mp4')
print('done', round(TOTAL, 2), 'hook', HOOK_D, 'news ends', round(NEWS_IN + len(news) / sr, 2))
