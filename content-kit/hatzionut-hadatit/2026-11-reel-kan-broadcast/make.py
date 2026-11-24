"""Smotrich reel: KAN broadcaster / IDF soldiers. Voice up front, quiet tense music, Haim captions with teal keyword pills,
emoji pop-ins, punch-in zooms, sarcastic OUT/IN board, RZ logo end card. 1080x1920."""
import os, glob, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); KIT = os.path.abspath(HERE + '/../..')
HAIM = KIT + '/fonts/HaimClassicv2FM-Bold.ttf'
SKILL = glob.glob('/root/.claude/skills/synced/*/pro-video-editing')[0]
LAT = SKILL + '/assets/fonts/Karantina-Bold.ttf'; SFX = SKILL + '/assets/sfx'
EMO = '/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'
LOGO = KIT + '/clients/hatzionut-hadatit/logo.png'
MUSIC = HERE + '/../2026-11-reel-tibi-hochman/music/pulse_90.wav'
W, H, FPS = 1080, 1920, 30
DEEP, LT, PALE, NIGHT = (43, 81, 85), (105, 180, 189), (173, 213, 217), (16, 36, 39)
RED, GREEN = (214, 40, 40), (40, 170, 90)
# (start, end, text, highlight, emoji)  — text follows his published statement; line at 4.0–7.5 is from the audio, to be confirmed
CAPS = [
    (0.40, 3.40, 'האמת עוד לא יצאה לאור בפרשה המטויחת של', False, None),
    (4.02, 6.25, 'הפצ״רית שהוציאה את דיבתם רעה', False, None),
    (6.62, 7.95, 'בעלילת דם על לוחמינו', False, None),
    (8.14, 10.40, 'וכעת תורו של תאגיד השידור הציבורי', False, '📺'),
    (10.60, 12.40, 'להטיל רפש בחיילי צה״ל', True, None),
    (12.55, 13.95, 'בתחקיר מהונדס', True, '🎬'),
    (14.10, 15.80, 'בסגנון שוברים שתיקה.', False, None),
    (16.12, 17.50, 'זה הוא שפל נוסף', False, '📉'),
    (17.74, 19.00, 'של גוף תקשורת', False, None),
    (19.14, 22.60, 'שממומן מכספי המיסים של כולנו.', True, '💸'),
    (22.85, 24.30, 'כולנו משלמים,', False, '🧾'),
    (24.45, 27.40, 'אבל רק לחלקנו יש מקום בתאגיד השידור הציבורי', False, None),
]
OUT_T, IN_T, END_V = 27.87, 29.97, 32.44
LOGO_D = 0.0
def F(s): return ImageFont.truetype(HAIM, s, layout_engine=ImageFont.Layout.RAQM)
def FL(s): return ImageFont.truetype(LAT, s)
def ease(t): t = max(0., min(1., t)); return 1 - (1 - t) ** 3
def back(t):  # overshoot pop
    t = max(0., min(1., t)); c = 1.70158; return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2
_em = {}
def emoji(e, size):
    if (e, size) not in _em:
        f = ImageFont.truetype(EMO, 109, layout_engine=ImageFont.Layout.RAQM)
        t = Image.new('RGBA', (220, 160), (0, 0, 0, 0)); ImageDraw.Draw(t).text((10, 10), e, font=f, embedded_color=True)
        t = t.crop(t.getchannel('A').getbbox()); _em[(e, size)] = t.resize((size, int(size * t.height / t.width)), Image.LANCZOS)
    return _em[(e, size)]
def wrap(d, text, font, maxw):
    out, cur = [], ''
    for w in text.split():
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=font, direction='rtl') <= maxw: cur = t
        else: out.append(cur); cur = w
    return out + [cur]
_cap = {}
def caption_img(text, hl):
    if (text, hl) in _cap: return _cap[(text, hl)]
    im = Image.new('RGBA', (W, 400), (0, 0, 0, 0)); d = ImageDraw.Draw(im); f = F(84)
    lines = wrap(d, text, f, W - 160); y = 10
    for l in lines:
        tw = d.textlength(l, font=f, direction='rtl'); bb = d.textbbox((0, 0), l, font=f, anchor='ls', direction='rtl'); ih = bb[3] - bb[1]
        x = (W + tw) / 2
        if hl:
            d.rounded_rectangle((x - tw - 26, y, x + 26, y + ih + 40), 14, fill=LT + (255,))
            d.text((x, y + 20 - bb[1]), l, font=f, fill=NIGHT, anchor='rs', direction='rtl')
        else:
            d.text((x, y + 20 - bb[1]), l, font=f, fill='white', anchor='rs', direction='rtl', stroke_width=6, stroke_fill=(0, 0, 0))
        y += ih + 52
    im = im.crop((0, 0, W, y)); _cap[(text, hl)] = im; return im
def hook_img():
    im = Image.new('RGBA', (W, 560), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for yy in range(560): d.line((0, yy, W, yy), fill=NIGHT + (int(215 * (1 - yy / 560) ** 1.3),))
    R = W - 70; f1 = F(80); y = 150
    d.rectangle((R - 6, y + 12, R, y + 92), fill=LT)
    d.text((R - 26, y), 'תאגיד השידור הציבורי', font=f1, fill='white', anchor='ra', direction='rtl')
    t = 'להטיל רפש בחיילי צה״ל'; f2 = F(72); bb = d.textbbox((0, 0), t, font=f2, anchor='ls', direction='rtl'); tw = bb[2] - bb[0]; ih = bb[3] - bb[1]
    d.rounded_rectangle((R - tw - 52, y + 112, R + 6, y + 112 + ih + 40), 14, fill=RED)
    d.text((R - 24, y + 132 - bb[1]), t, font=f2, fill='white', anchor='rs', direction='rtl')
    return im
HOOK = hook_img()
def board_row(name, word, col, mark):
    im = Image.new('RGBA', (W - 120, 150), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, im.width - 1, 149), 24, fill=(255, 255, 255, 240))
    fw = FL(96); d.rounded_rectangle((18, 18, 250, 132), 18, fill=col); d.text((134, 75), word, font=fw, fill='white', anchor='mm')
    f = F(64); d.text((im.width - 30, 75), name, font=f, fill=NIGHT, anchor='rm', direction='rtl')
    e = emoji(mark, 64); im.alpha_composite(e, (270, 75 - e.height // 2)); return im
ROW_OUT = board_row('איילה חסון', 'OUT', RED, '❌')
ROW_IN = board_row('השחרת חיילי צה״ל', 'IN', GREEN, '✅')
logo = Image.open(LOGO).convert('RGBA'); logo = logo.resize((520, int(520 * logo.height / logo.width)), Image.LANCZOS)

def zoom_for(t):
    for i, c in enumerate(CAPS):
        if c[0] - .05 <= t < (CAPS[i + 1][0] - .05 if i + 1 < len(CAPS) else OUT_T):
            return 1.0 if i % 2 == 0 else 1.10
    return 1.14 if t >= OUT_T else 1.0
def overlay(im, t):
    if t < 3.6:
        a = 1 - ease((t - 3.2) / .4) if t > 3.2 else 1.0
        h = HOOK.copy(); h.putalpha(h.getchannel('A').point(lambda v: int(v * a))); im.alpha_composite(h, (0, 0))
    for (s, e, txt, hl, em) in CAPS:
        if s <= t < e + .12:
            pass  # captions removed: user adds his own transcription
            if em:
                k = back((t - s) / .35); sz = max(1, int(170 * k)); g = emoji(em, 170).resize((sz, sz), Image.LANCZOS)
                im.alpha_composite(g, (W // 2 - sz // 2, 1120 - sz // 2))
    if OUT_T <= t:
        k = back((t - OUT_T) / .35); r = ROW_OUT.resize((max(1, int(ROW_OUT.width * k)), max(1, int(ROW_OUT.height * k))))
        im.alpha_composite(r, ((W - r.width) // 2, 1180 + (150 - r.height) // 2))
    if IN_T <= t:
        k = back((t - IN_T) / .35); r = ROW_IN.resize((max(1, int(ROW_IN.width * k)), max(1, int(ROW_IN.height * k))))
        im.alpha_composite(r, ((W - r.width) // 2, 1360 + (150 - r.height) // 2))
    return im

dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', HERE + '/source.mov', '-vf', f'scale={W}:{H},fps={FPS},eq=contrast=1.05:saturation=1.08',
                        '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                        '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-pix_fmt', 'yuv420p', HERE + '/_video.mp4'], stdin=subprocess.PIPE)
n = 0; last = None; CX, CY = 540, 620
while True:
    buf = dec.stdout.read(W * H * 3)
    if len(buf) < W * H * 3: break
    t = n / FPS; fr = Image.frombytes('RGB', (W, H), buf); z = zoom_for(t)
    if z != 1.0:
        w2, h2 = int(W / z), int(H / z); x0 = int(CX - w2 / 2); y0 = int(CY - h2 * CY / H)
        fr = fr.crop((x0, y0, x0 + w2, y0 + h2)).resize((W, H), Image.LANCZOS)
    im = overlay(fr.convert('RGBA'), t); last = im
    enc.stdin.write(im.convert('RGB').tobytes()); n += 1
bg = Image.new('RGBA', (W, H), NIGHT + (255,))
for k in range(0):
    t = k / FPS; a = ease(t / .4); im = Image.blend(last, bg, a)
    g = logo.copy(); g.putalpha(g.getchannel('A').point(lambda v: int(v * ease((t - .25) / .4))))
    im.alpha_composite(g, ((W - logo.width) // 2, (H - logo.height) // 2)); enc.stdin.write(im.convert('RGB').tobytes())
enc.stdin.close(); enc.wait()
total = n / FPS + LOGO_D

# audio: voice up front (normalized), quiet music bed, a few meaningful SFX
sr = 48000
def load(p, af=None):
    c = ['ffmpeg', '-v', 'error', '-i', p] + (['-af', af] if af else []) + ['-ac', '2', '-ar', str(sr), '-f', 'f32le', '-']
    return np.frombuffer(subprocess.run(c, capture_output=True).stdout, np.float32).reshape(-1, 2).copy()
N = int(total * sr); out = np.zeros((N, 2), np.float32)
def add(x, t, g): i = int(t * sr); m = min(len(x), N - i); out[i:i + m] += g * x[:m]
voice = load(HERE + '/source.mov', 'highpass=f=80,afftdn=nf=-25,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,loudnorm=I=-16:TP=-2')
add(voice, 0, 1.0)
mus = load(MUSIC); mus /= np.abs(mus).max(); mus = np.tile(mus, (N // len(mus) + 2, 1))[:N]
env = np.interp(np.arange(N) / sr, [0, .3, END_V - .5, END_V, total - .3, total], [0, .085, .085, .085, .085, 0])
out += mus * env[:, None]
def sfx(n_): x = load(f'{SFX}/{n_}.wav'); return x / (np.abs(x).max() + 1e-9)
add(sfx('whoosh'), 0, .25)
for (s, e, txt, hl, em) in CAPS:
    if em: add(sfx('pop_soft'), s, .22)
add(sfx('impact'), OUT_T, .3); add(sfx('ding'), IN_T, .28)
out.tofile(HERE + '/_a.raw')
final = HERE + '/smotrich-kan-reel.mp4'
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', HERE + '/_video.mp4', '-f', 'f32le', '-ar', str(sr), '-ac', '2', '-i', HERE + '/_a.raw',
                '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000',
                '-movflags', '+faststart', '-shortest', final], check=True)
os.remove(HERE + '/_video.mp4'); os.remove(HERE + '/_a.raw'); print('done', round(total, 2))
