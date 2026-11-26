"""Yesha reel 'אשת חייל' — women's range training for farm women.
Hook (Avishag) -> data cards over range b-roll -> why it matters -> 'knowing how to use it' -> emotional close + Yesha logo.
Every section carries a big headline on top (client: so it can't be taken out of context). Lower third left free for the user's captions."""
import os, sys, glob, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); KIT = os.path.abspath(HERE + '/../..')
HAIM = KIT + '/fonts/HaimClassicv2FM-Bold.ttf'
LOGO = KIT + '/clients/yesha/logo_white.png'
SFX = glob.glob('/root/.claude/skills/synced/*/pro-video-editing/assets/sfx')[0]
MUSIC = HERE + '/music/uplifting_gm.wav'
W, H, FPS = 1080, 1920, 30
NAVY, BLUE, LB = (23, 64, 104), (37, 102, 162), (39, 164, 209)
IV = HERE + '/src/copy_80EA2197.mov'
def B(n): return f'{HERE}/src/IMG_{n}.MOV'
def F(s): return ImageFont.truetype(HAIM, s, layout_engine=ImageFont.Layout.RAQM)
def ease(t): t = max(0., min(1., t)); return 1 - (1 - t) ** 3

# ---------------- timeline ----------------
SPEECH = [[0.314, 3.782], [3.891, 7.44], [7.694, 8.905], [9.384, 10.138], [10.158, 12.18], [12.369, 13.394], [14.0, 14.34], [14.417, 15.798],
          [16.543, 20.189], [20.639, 23.045], [23.72, 27.357], [27.498, 29.842], [29.927, 32.717], [33.014, 36.299], [36.901, 40.83],
          [41.378, 42.398], [42.58, 44.837], [44.901, 52.798], [53.173, 62.045]]
PAD = .14
def iv_pieces(a, b):
    """continuous take — no jump cuts inside her speech (client note)"""
    return [[a, b]]
def _old_iv_pieces(a, b):
    out = []
    for s, e in SPEECH:
        if s >= a - .01 and e <= b + .01:
            s0, e0 = max(0, s - PAD), e + PAD
            if out and s0 <= out[-1][1] + .05: out[-1][1] = e0
            else: out.append([s0, e0])
    return out
SECTIONS = []  # each: dict(name, pieces=[(vsrc, vt0, dur, asrc|None, at0, again)])
def interview(name, a, b, cutaways=()):
    pcs = []
    for s, e in iv_pieces(a, b):
        t = s
        for (ca, cb, src, st) in cutaways:          # cutaway: replace picture between interview times ca..cb
            if s < cb and e > ca and t < cb:
                if ca > t: pcs.append((IV, t, ca - t, IV, t, 1.0)); t = ca
                ce = min(cb, e); pcs.append((src, st + (t - ca), ce - t, IV, t, 1.0)); t = ce
        if t < e: pcs.append((IV, t, e - t, IV, t, 1.0))
    SECTIONS.append(dict(name=name, pieces=pcs))
def broll(name, clips, bg_gain=.35):
    SECTIONS.append(dict(name=name, pieces=[(B(n), st, d, B(n), st, bg_gain) for (n, st, d) in clips]))
interview('hook', 0.15, 15.95)
broll('stat635', [('1866', .3, 3.6)])
broll('stat90', [('1862', .1, 2.0), ('1864', 1.0, 1.9)])
broll('front', [('1806', 2.0, 4.2)])
broll('project', [('1890', 0.0, 2.4), ('1790', 0.0, 2.6)])
interview('why', 16.4, 23.25)
interview('weapon', 44.8, 62.2, cutaways=[(47.5, 51.0, B('1816'), 0.5), (57.0, 60.5, B('1864'), 3.0)])
broll('close', [('1923', 0.5, 2.6), ('1866', 0.0, 4.0)], bg_gain=.2)

# ---------------- headlines: in a navy stripe ABOVE the footage, never over faces ----------------
BAND = 0; VH = H; BOTTOM = 1610  # lower-third stripe: text block bottom edge
def headline(lines, size=72, hl_size=None, gap=14):
    """returns a tight RGBA block: white lines as text, 'hl' lines in light-blue pills"""
    im = Image.new('RGBA', (W, 1400), (0, 0, 0, 0)); d = ImageDraw.Draw(im); y = 0
    for txt, kind in lines:
        f = F(hl_size if (kind == 'hl' and hl_size) else size)
        bb = d.textbbox((0, 0), txt, font=f, anchor='ls', direction='rtl'); tw = bb[2] - bb[0]; ih = bb[3] - bb[1]
        while tw > W - 120: f = F(f.size - 4); bb = d.textbbox((0, 0), txt, font=f, anchor='ls', direction='rtl'); tw = bb[2] - bb[0]; ih = bb[3] - bb[1]
        pad = 18
        if kind == 'hl':
            d.rounded_rectangle((W / 2 - tw / 2 - 30, y, W / 2 + tw / 2 + 30, y + ih + 2 * pad), 16, fill=LB + (255,))
        d.text((W / 2 + tw / 2, y + pad - bb[1]), txt, font=f, fill='white', anchor='rs', direction='rtl')
        y += ih + 2 * pad + gap
    return im.crop((0, 0, W, y - gap))
HL = {
    'hook': headline([('נשות החוות', 'w'), ('בקו החזית', 'hl')], size=110),
    'stat90': headline([('מתוכם 90 אירועי', 'w'), ('תקיפת רועים', 'hl')], size=104),
    'front': headline([('נשות החוות נמצאות', 'w'), ('בחזית ההתיישבות', 'w'), ('ונדרשות לשאת באחריות', 'hl'), ('לביטחונן ולביטחון משפחתן', 'hl')], size=96, gap=6),
    'project': headline([('פרויקט ״אשת חייל״', 'hl'), ('ימי אימון מקצועיים וייחודיים', 'w'), ('לנשות החוות שמחזיקות', 'w'), ('ברישיון בתוקף', 'w')], size=82, hl_size=118, gap=6),
    'why': headline([('למה זה', 'w'), ('כל כך חשוב?', 'hl')], size=110),
    'weapon': headline([('להחזיק נשק זה לא מספיק', 'w'), ('צריך לדעת', 'hl'), ('להשתמש בו', 'hl')], size=96),
    'close': headline([('זו האחריות שלנו כלפי המשפחות', 'w'), ('שנמצאות בחזית ועושות יום יום', 'w'), ('עבודה אדירה', 'hl'), ('למען ביטחון מדינת ישראל', 'hl')], size=82, gap=6),
}
SUB635 = headline([('פיגועי טרור', 'hl'), ('בחודשיים האחרונים', 'w')], size=84, gap=6)
def stat635(t):
    n = int(round(635 * ease(t / 1.1))); f = F(230); im = Image.new('RGBA', (W, 230 + 20 + SUB635.height), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.text((W / 2, 205), f'{n}', font=f, fill='white', anchor='ms'); im.alpha_composite(SUB635, (0, 250)); return im
logo = Image.open(LOGO).convert('RGBA'); logo = logo.resize((170, int(170 * logo.height / logo.width)), Image.LANCZOS)
def overlay(name, fr, t, sd):
    canvas = fr.convert('RGBA')
    blk = stat635(t) if name == 'stat635' else HL[name]
    fade = ease(t / .3)
    if name not in ('hook', 'why', 'weapon', 'close'): fade *= 1 - ease((t - (sd - .25)) / .25)
    y1 = BOTTOM; y0 = y1 - blk.height
    band = Image.new('RGBA', (W, blk.height + 70), NAVY + (215,)); bd = ImageDraw.Draw(band)
    bd.rectangle((0, 0, W, 7), fill=LB + (255,))
    band.alpha_composite(blk, (0, 38))
    band.putalpha(band.getchannel('A').point(lambda v: int(v * fade)))
    canvas.alpha_composite(band, (int((1 - ease(t / .35)) * 120), y0 - 38))
    if name == 'close':
        e = ease((t - 1.0) / .6)
        if e > 0:
            g = logo.copy(); g.putalpha(g.getchannel('A').point(lambda v: int(v * e))); canvas.alpha_composite(g, ((W - logo.width) // 2, 150))
    return canvas

# ---------------- render ----------------
def frames(src, t0, dur):
    yoff = '0' if src == IV else '(ih-oh)/2'
    vf = f'scale={W}:{VH}:force_original_aspect_ratio=increase,crop={W}:{VH}:(iw-ow)/2:{yoff},fps={FPS},eq=contrast=1.05:saturation=1.08'
    if src.endswith('1923.MOV'):
        vf = f'scale={W}:{VH}:force_original_aspect_ratio=increase,crop={W}:{VH},fps={FPS},eq=contrast=1.05:saturation=1.08'
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', f'{t0:.3f}', '-t', f'{dur:.3f}', '-i', src, '-filter_complex', vf,
                          '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    n = 0; last = None
    while n < int(round(dur * FPS)):
        b = p.stdout.read(W * VH * 3)
        if len(b) < W * VH * 3: break
        last = Image.frombytes('RGB', (W, VH), b); yield last; n += 1
    p.stdout.close(); p.kill(); p.wait()
    while n < int(round(dur * FPS)) and last is not None: yield last; n += 1
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                        '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-pix_fmt', 'yuv420p', HERE + '/_video.mp4'], stdin=subprocess.PIPE)
AUD = []; T = 0.0; MARKS = []
for sec in SECTIONS:
    sd = sum(p[2] for p in sec['pieces']); MARKS.append((sec['name'], T, sd)); lt = 0.0
    for (vs, vt, d, as_, at, g) in sec['pieces']:
        k = 0
        for fr in frames(vs, vt, d):
            im = overlay(sec['name'], fr.convert('RGBA'), lt + k / FPS, sd)
            enc.stdin.write(im.convert('RGB').tobytes()); k += 1
        AUD.append((as_, at, d, g, T + lt)); lt += k / FPS
    T += lt
enc.stdin.close(); enc.wait()

# ---------------- audio ----------------
sr = 48000; N = int(T * sr) + sr; out = np.zeros((N, 2), np.float32)
def load(p, ss=0, t=None, af=None):
    c = ['ffmpeg', '-v', 'error', '-ss', f'{ss:.3f}'] + (['-t', f'{t:.3f}'] if t else []) + ['-i', p] + (['-af', af] if af else []) + ['-ac', '2', '-ar', str(sr), '-f', 'f32le', '-']
    return np.frombuffer(subprocess.run(c, capture_output=True).stdout, np.float32).reshape(-1, 2).copy()
voice = load(IV, af='highpass=f=90,afftdn=nf=-25,acompressor=threshold=-20dB:ratio=3,loudnorm=I=-16:TP=-2')
def add(x, t, g):
    i = int(t * sr); m = min(len(x), N - i)
    if m <= 0: return
    x = x[:m].copy(); f = min(int(.02 * sr), m // 2)
    if f: x[:f] *= np.linspace(0, 1, f)[:, None]; x[-f:] *= np.linspace(1, 0, f)[:, None]
    out[i:i + m] += g * x
for (as_, at, d, g, tt) in AUD:
    if as_ == IV: add(voice[int(at * sr):int((at + d) * sr)], tt, 1.0)
    else:
        x = load(as_, at, d); x /= (np.abs(x).max() + 1e-9); add(x * .5, tt, g)
mus = load(MUSIC); mus /= np.abs(mus).max(); mus = np.tile(mus, (N // len(mus) + 2, 1))[:N]
pts = [(0, .0)]
for name, t0, d in MARKS:
    lvl = .10 if name in ('hook', 'why', 'weapon') else .42
    pts += [(t0 + .01, lvl), (t0 + d - .01, lvl)]
pts += [(T - 1.2, .42), (T, 0)]
env = np.interp(np.arange(N) / sr, [p[0] for p in pts], [p[1] for p in pts])
NOMUSIC = '--no-music' in sys.argv   # client adds 'רוח המחר' in Instagram
if not NOMUSIC: out += mus * env[:, None]
def sfx(n): x = load(f'{SFX}/{n}.wav'); return x / (np.abs(x).max() + 1e-9)
out[:int(T * sr)].tofile(HERE + '/_a.raw')
final = HERE + ('/yesha-eshet-hayil-reel-no-music.mp4' if NOMUSIC else '/yesha-eshet-hayil-reel.mp4')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', HERE + '/_video.mp4', '-f', 'f32le', '-ar', str(sr), '-ac', '2', '-i', HERE + '/_a.raw',
                '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000',
                '-movflags', '+faststart', '-shortest', final], check=True)
os.remove(HERE + '/_video.mp4'); os.remove(HERE + '/_a.raw')
print('done', round(T, 2)); [print(m) for m in MARKS]
