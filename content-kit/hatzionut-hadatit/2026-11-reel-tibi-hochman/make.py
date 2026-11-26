"""Smotrich reel: Tibi assaults Guy Hochman. Source clip + slow-mo replay with a teal title bar, then his statement as animated text cards. 1080x1920."""
import os, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.abspath(os.path.join(HERE, '..', '..'))
HAIM = KIT + '/fonts/HaimClassicv2FM-Bold.ttf'
LOGO = KIT + '/clients/hatzionut-hadatit/logo.png'
SFX = [p for p in [os.path.join(r, 'assets/sfx') for r in __import__('glob').glob('/root/.claude/skills/synced/*/pro-video-editing')]][0]
W, H, FPS = 1080, 1920, 30
DEEP, TEAL, LT, PALE, NIGHT = (43, 81, 85), (80, 146, 153), (105, 180, 189), (173, 213, 217), (16, 36, 39)
TMP = HERE + '/_tmp'; os.makedirs(TMP, exist_ok=True)
SRC = HERE + '/source.mp4'
S1 = (0.0, 4.9)          # real time
S2 = (2.7, 4.5, 0.5)     # replay range, speed
CARD = 3.3
CARDS = [  # (line1 white, line2 highlighted) — his exact words
    ('ככה זה שהם מרגישים בעלי הבית,', 'האלימות הפרלמנטרית הופכת לאלימות פיזית.'),
    ('על המשטרה לפתוח באופן מיידי', 'בחקירה פלילית נגד אחמד טיבי.'),
    ('אני שב וקורא לגדי, נפתלי, ואיווט:', 'אין מקום לשיתוף פעולה עם תומכי טרור.'),
    ('אחים. יהודים.', 'זמן אחדות!'),
]
def F(s): return ImageFont.truetype(HAIM, s, layout_engine=ImageFont.Layout.RAQM)
def run(c): subprocess.run(c, check=True)

def wrap(d, text, font, maxw):
    words, lines, cur = text.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=font, direction='rtl') <= maxw: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur); return lines

def pill_text(d, R, y, text, font, fill, fg, pad=20):
    bb = d.textbbox((0, 0), text, font=font, anchor='ls', direction='rtl'); tw = d.textlength(text, font=font, direction='rtl')
    ih = bb[3] - bb[1]; d.rounded_rectangle((R - tw - 2 * pad - 8, y, R, y + ih + 2 * pad), 14, fill=fill)
    d.text((R - pad - 4, y + pad - bb[1]), text, font=font, fill=fg, anchor='rs', direction='rtl'); return y + ih + 2 * pad

# ---------- title bar overlay for the footage ----------
bar = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(bar)
for yy in range(560): d.line((0, yy, W, yy), fill=NIGHT + (int(200 * (1 - yy / 560) ** 1.2),))
R = W - 60; y = 190
f1 = F(76)
d.rectangle((R - 6, y + 12, R, y + 98), fill=LT)
for dx, dy, c in [(4, 4, (0, 0, 0, 170)), (0, 0, (255, 255, 255, 255))]:
    d.text((R - 26 + dx, y + dy), 'התקיפה האלימה של טיבי', font=f1, fill=c, anchor='ra', direction='rtl')
pill_text(d, R, y + 118, 'נגד גיא הוכמן', F(76), LT + (255,), DEEP)
bar.save(TMP + '/bar.png')
replay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(replay)
pill_text(d, W - 60, 1380, 'צפו שוב', F(52), (220, 40, 40, 255), (255, 255, 255))
replay.save(TMP + '/replay.png')

base = "scale=1080:1920:flags=lanczos,setsar=1,fps=30"
run(['ffmpeg', '-v', 'error', '-y', '-ss', str(S1[0]), '-t', str(S1[1] - S1[0]), '-i', SRC, '-i', TMP + '/bar.png',
     '-filter_complex', f"[0:v]{base},eq=contrast=1.05:saturation=1.05[v];[v][1]overlay=0:0,format=yuv420p[o]",
     '-map', '[o]', '-an', '-c:v', 'libx264', '-crf', '17', TMP + '/s1.mp4'])
s2d = (S2[1] - S2[0]) / S2[2]
run(['ffmpeg', '-v', 'error', '-y', '-ss', str(S2[0]), '-t', str(S2[1] - S2[0]), '-i', SRC, '-i', TMP + '/bar.png', '-i', TMP + '/replay.png',
     '-filter_complex', f"[0:v]setpts=PTS/{S2[2]},minterpolate=fps=30:mi_mode=blend,{base},"
                        f"scale=iw*(1.10+0.06*t/{s2d}):-2:eval=frame,crop=1080:1920,eq=contrast=1.08:saturation=0.9[v];"
                        f"[v][1]overlay=0:0[a];[a][2]overlay=0:0,format=yuv420p[o]",
     '-map', '[o]', '-an', '-c:v', 'libx264', '-crf', '17', TMP + '/s2.mp4'])

# ---------- statement cards ----------
fr = subprocess.run(['ffmpeg', '-v', 'error', '-ss', '3.3', '-i', SRC, '-frames:v', '1', '-vf', 'scale=1080:1920', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
bg = Image.frombytes('RGB', (W, H), fr).filter(ImageFilter.GaussianBlur(28))
bg = Image.blend(bg, Image.new('RGB', (W, H), NIGHT), .70)
logo = Image.open(LOGO).convert('RGBA'); logo = logo.resize((420, int(420 * logo.height / logo.width)), Image.LANCZOS)
def ease(t): t = max(0., min(1., t)); return 1 - (1 - t) ** 3
def card_layer(l1, l2, last):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    fa, fb = (F(150), F(170)) if last else (F(88), F(84))
    L1 = wrap(d, l1, fa, W - 160); L2 = wrap(d, l2, fb, W - 190)
    lh1 = int(fa.size * 1.05); h1 = lh1 * len(L1)
    hb = [d.textbbox((0, 0), t, font=fb, anchor='ls', direction='rtl') for t in L2]
    h2 = sum(b[3] - b[1] + 40 + 14 for b in hb)
    top = (H - (h1 + 40 + h2)) // 2 - (120 if last else 60)
    R = W - 70
    d.rectangle((R - 6, top + 10, R, top + h1 - 6), fill=LT)
    for i, t in enumerate(L1):
        d.text((R - 26, top + i * lh1), t, font=fa, fill='white', anchor='ra', direction='rtl')
    y = top + h1 + 40
    l2_top = y
    for t in L2:
        y = pill_text(d, R, y, t, fb, LT + (255,), NIGHT) + 14
    return lay, top, l2_top
frames_dir = TMP + '/cards'; os.makedirs(frames_dir, exist_ok=True)
n = 0
for ci, (a, b) in enumerate(CARDS):
    last = ci == len(CARDS) - 1
    lay, top, l2_top = card_layer(a, b, last)
    up = lay.crop((0, 0, W, l2_top)); lo = lay.crop((0, l2_top, W, H))
    dur = CARD + (0.8 if last else 0)
    for k in range(int(dur * FPS)):
        t = k / FPS; im = bg.copy().convert('RGBA')
        e1 = ease(t / .35); e2 = ease((t - .35) / .35)
        if e1 > 0:
            u = up.copy(); u.putalpha(u.getchannel('A').point(lambda v: int(v * e1)))
            im.alpha_composite(u, (int((1 - e1) * 60), 0))
        if e2 > 0:
            l = lo.copy(); l.putalpha(l.getchannel('A').point(lambda v: int(v * e2)))
            im.alpha_composite(l, (0, l2_top + int((1 - e2) * 40)))
        if last:
            e3 = ease((t - .9) / .5)
            if e3 > 0:
                g = logo.copy(); g.putalpha(g.getchannel('A').point(lambda v: int(v * e3)))
                im.alpha_composite(g, ((W - logo.width) // 2, 1340 + int((1 - e3) * 30)))
        if t > dur - .2 and not last:
            im = Image.blend(im, bg.convert('RGBA'), (t - (dur - .2)) / .2)
        im.convert('RGB').save(f'{frames_dir}/{n:05d}.jpg', quality=92); n += 1
run(['ffmpeg', '-v', 'error', '-y', '-framerate', str(FPS), '-i', frames_dir + '/%05d.jpg', '-vf', 'format=yuv420p',
     '-c:v', 'libx264', '-crf', '17', TMP + '/s3.mp4'])
with open(TMP + '/list.txt', 'w') as f:
    for s in ['s1', 's2', 's3']: f.write(f"file '{TMP}/{s}.mp4'\n")
run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', TMP + '/list.txt', '-c', 'copy', TMP + '/video.mp4'])

# ---------- audio ----------
sr = 48000
def load(p, ss=0, t=None):
    c = ['ffmpeg', '-v', 'error', '-ss', str(ss)] + (['-t', str(t)] if t else []) + ['-i', p, '-ac', '2', '-ar', str(sr), '-f', 'f32le', '-']
    return np.frombuffer(subprocess.run(c, capture_output=True).stdout, np.float32).reshape(-1, 2).copy()
s1d = S1[1] - S1[0]; s3d = len(CARDS) * CARD + 0.8; total = s1d + s2d + s3d; N = int(total * sr)
out = np.zeros((N, 2), np.float32)
def add(x, t, g):
    i = int(t * sr); m = min(len(x), N - i); out[i:i + m] += g * x[:m]
src = load(SRC, S1[0], s1d); src /= np.abs(src).max() + 1e-9
fade = np.ones(len(src)); fade[-int(.25 * sr):] = np.linspace(1, 0, int(.25 * sr)); add(src * fade[:, None], 0, .9)
mus = load(HERE + '/music/toms_122_D.wav'); mus /= np.abs(mus).max()
mus = np.tile(mus, (int(np.ceil(N / len(mus))) + 1, 1))[:N]
env = np.interp(np.arange(N) / sr, [0, s1d - .3, s1d, total - 1.2, total], [.12, .12, .55, .55, 0])
out += mus * env[:, None]
def sfx(name): x = load(f'{SFX}/{name}.wav'); return x / (np.abs(x).max() + 1e-9)
add(sfx('impact'), s1d, .5)
for i in range(len(CARDS)): add(sfx('swoosh_soft'), s1d + s2d + i * CARD, .35)
add(sfx('hit_soft'), s1d + s2d + (len(CARDS) - 1) * CARD + .35, .5)
out.tofile(TMP + '/a.raw')
final = HERE + '/smotrich-tibi-hochman-reel.mp4'
run(['ffmpeg', '-v', 'error', '-y', '-i', TMP + '/video.mp4', '-f', 'f32le', '-ar', str(sr), '-ac', '2', '-i', TMP + '/a.raw',
     '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000',
     '-movflags', '+faststart', '-shortest', final])
print('done', round(total, 2))
