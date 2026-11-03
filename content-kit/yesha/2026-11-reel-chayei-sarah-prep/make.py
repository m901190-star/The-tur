"""Yesha Council reel: preparations for Shabbat Chayei Sarah in Hebron & Kiryat Arba (1080x1920, ~27s).
Field clip + photos with push-ins, crowd photo, closer: Shabbat table before the Machpela at night. Original light score."""
import os, sys, math, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); P = HERE + '/prep/'; os.makedirs(P, exist_ok=True)
U = '/root/.claude/uploads/1a5819ee-0cc0-5045-b086-4a8a80216453/'
CAR = HERE + '/../2026-11-hebron-chat-carousel/'
SCR = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/'
KB = SCR + 'pro-video-editing/assets/fonts/Karantina-Bold.ttf'; RB = SCR + 'fonts/Rubik-700.ttf'
SFX = SCR + 'pro-video-editing/assets/sfx/'; LOUD = SCR + 'pro-video-editing/scripts/loudnorm.py'
VID = U + '359c5c60-d97c4d72-2614-402c-b9a0-3b54630b0f15.mov'
W, H, FPS = 1080, 1920, 30
NAVY = (0x17, 0x40, 0x68); BLUE = (0x25, 0x66, 0xA2); LB = (0x27, 0xA4, 0xD1); DEEP = (0x0E, 0x2A, 0x47); WHITE = (255, 255, 255); GOLD = (0xFF, 0xD9, 0x9A)
WL = Image.open(HERE + '/../../clients/yesha/logo_white.png').convert('RGBA'); WL = WL.crop(WL.getchannel('A').getbbox())
LOGO = WL.resize((190, int(190 * WL.height / WL.width)), Image.LANCZOS)
_f = {}
def F(p, s):
    if (p, s) not in _f: _f[(p, s)] = ImageFont.truetype(p, s)
    return _f[(p, s)]
def eo(t): t = min(max(t, 0), 1); return 1 - (1 - t) ** 3
def eb(t, s=1.6): t = min(max(t, 0), 1) - 1; return t * t * ((s + 1) * t + s) + 1
def cover(im, w, h, fy=.5, fx=.5):
    s = max(w / im.width, h / im.height); im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
    x0 = int((im.width - w) * fx); y0 = int((im.height - h) * fy); return im.crop((x0, y0, x0 + w, y0 + h))

# ---- shots: (kind, src, dur, label, opts) ----
SHOTS = [('v', 3.5, 0.0, 'open'), ('p', U + '9dc40d68-image.jpg', 1.6, .5), ('v', 2.6, 9.5, None), ('p', U + 'b0418f93-image.jpg', 1.6, .55),
         ('p', U + 'aa1a10b1-image.jpg', 1.5, .45), ('p', U + '223f3d2f-image.jpg', 1.5, .5), ('p', U + '64f93c84-image.jpg', 1.5, .75),
         ('v', 2.6, 15.5, None), ('p', U + '0d1a32ec-image.jpg', 1.6, .5), ('crowd', U + '472f4304-image.webp', 3.4, .5), ('close', None, 5.0, None)]
LABELS = [(3.5, 9.1, 'מקימים את האוהל הגדול'), (9.1, 15.7, 'מכינים מקום לכל האורחים'), (15.7, 18.0, 'הכל מוכן בשבילכם')]
T0 = []; _t = 0
for s in SHOTS: T0.append(_t); _t += s[2] if s[0] != 'v' else s[1]
TOT = _t
def dur(s): return s[1] if s[0] == 'v' else s[2]

def prep_video():
    d = P + 'vid/'; os.makedirs(d, exist_ok=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', VID, '-vf', f'fps={FPS},scale={W}:{H}:flags=lanczos,unsharp=5:5:0.5,eq=saturation=1.12:contrast=1.05', d + '%04d.png'], check=True)
    return d, sorted(os.listdir(d))

def text_block(img, lines, y, t, t0, size=150, color=WHITE, block=None, shadow=True):
    d = ImageDraw.Draw(img)
    for k, (ln, col, blk) in enumerate(lines):
        u = eo((t - t0 - k * .18) / .35)
        if u <= 0: continue
        lay = Image.new('RGBA', (W, int(size * 1.5)), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        f = F(KB, size); tw = ld.textlength(ln, font=f, direction='rtl')
        if blk: ld.rectangle(((W - tw) / 2 - 30, size * .14, (W + tw) / 2 + 30, size * 1.3), fill=blk + (255,))
        if shadow and not blk: ld.text((W / 2 + 5, size * .78 + 6), ln, font=f, fill=DEEP + (200,), anchor='mm', direction='rtl')
        ld.text((W / 2, size * .78), ln, font=f, fill=col, anchor='mm', direction='rtl')
        lay.putalpha(lay.getchannel('A').point(lambda v: int(v * u)))
        img.alpha_composite(lay, (0, int(y + k * size * 1.12 + (1 - u) * 40)))

def label(img, t):
    for a, b, s in LABELS:
        if a <= t < b:
            u = eo((t - a) / .3) * (1 - eo((t - (b - .25)) / .25))
            lay = Image.new('RGBA', (W, 140), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay); f = F(RB, 54); tw = ld.textlength(s, font=f, direction='rtl')
            x1 = W - 60; ld.rounded_rectangle((x1 - tw - 70, 20, x1, 120), 18, fill=NAVY + (235,)); ld.rectangle((x1 - 12, 20, x1, 120), fill=LB + (255,))
            ld.text((x1 - 36, 70), s, font=f, fill=WHITE, anchor='rm', direction='rtl')
            lay.putalpha(lay.getchannel('A').point(lambda v: int(v * u))); img.alpha_composite(lay, (int(80 * (1 - u)), 1520))

GRAD = Image.new('RGBA', (W, H)); _g = ImageDraw.Draw(GRAD)
for y in range(H): _g.line([(0, y), (W, y)], fill=DEEP + (int(170 * max(0, 1 - y / H / .14) + 200 * max(0, (y / H - .62) / .38) ** 1.3),))

def closer_bg():
    """Machpela at night with the Shabbat table cut-out, candle-lit (same treatment as the carousel closer, vertical)."""
    bg = cover(Image.open(CAR + 'machpela-night.jpg').convert('RGB'), W, H, fy=0, fx=.42)
    bg = Image.blend(bg, Image.new('RGB', bg.size, (0x0A, 0x18, 0x2E)), .42).convert('RGBA')
    sh = Image.new('RGBA', bg.size); sd = ImageDraw.Draw(sh)
    for y in range(H): t = y / H; sd.line([(0, y), (W, y)], fill=(8, 20, 38, min(240, int(225 * max(0, 1 - t / .36) ** 1.3 + 255 * max(0, (t - .62) / .3) ** 1.2))))
    bg.alpha_composite(sh)
    it = Image.open(CAR + 'shabbat_cut.png').convert('RGBA'); it = it.crop(it.getchannel('A').getbbox())
    iw = 1020; it = it.resize((iw, int(iw * it.height / it.width)), Image.LANCZOS); ix, iy = 30, H - it.height - 300
    glow = Image.new('L', bg.size, 0); gd = ImageDraw.Draw(glow)
    for fx, fy in ((.448, .07), (.562, .055)):
        cx, cy = ix + iw * fx, iy + it.height * fy
        for r, v in ((480, 40), (260, 80), (120, 150), (40, 230)): gd.ellipse((cx - r, cy - r, cx + r, cy + r), fill=v)
    warm = Image.new('RGBA', bg.size, (0xFF, 0xC9, 0x7A, 0)); warm.putalpha(glow.filter(ImageFilter.GaussianBlur(50)).point(lambda v: int(v * .85))); bg.alpha_composite(warm)
    a = np.asarray(it).astype(np.float32); a[..., 1] *= .93; a[..., 2] *= .8; it2 = Image.fromarray(a.clip(0, 255).astype(np.uint8), 'RGBA')
    fl = Image.new('L', it.size, 255); fd = ImageDraw.Draw(fl)
    for x in range(160): fd.line([(x, 0), (x, it.height)], fill=int(255 * x / 160))
    it2.putalpha(Image.fromarray(np.minimum(np.asarray(it2.getchannel('A')), np.asarray(fl)))); bg.alpha_composite(it2, (ix, iy))
    bot = Image.new('RGBA', bg.size); bd = ImageDraw.Draw(bot)
    for y in range(iy + it.height - 120, H): t = (y - (iy + it.height - 120)) / (H - (iy + it.height - 120)); bd.line([(0, y), (W, y)], fill=(8, 20, 38, int(250 * min(1, t * 1.5) ** 1.2)))
    bg.alpha_composite(bot)
    return bg, [(ix + iw * fx, iy + it.height * fy) for fx, fy in ((.448, .07), (.562, .055))]

def render(out):
    vd, vf = prep_video()
    photos = {}
    for s in SHOTS:
        if s[0] in ('p', 'crowd'):
            photos[s[1]] = cover(Image.open(s[1]).convert('RGB'), int(W * 1.12), int(H * 1.12), fy=.5, fx=s[3]).convert('RGBA')
    cbg, flames = closer_bg()
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-maxrate', '12M', '-bufsize', '24M', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for i in range(int(round(TOT * FPS))):
        t = i / FPS; j = max(k for k in range(len(SHOTS)) if T0[k] <= t + 1e-6); s = SHOTS[j]; u = t - T0[j]; D = dur(s)
        if s[0] == 'v':
            fr = Image.open(vd + vf[min(len(vf) - 1, int((s[2] + u) * FPS))]).convert('RGBA')
            z = 1 + .04 * u / D; fr = fr.resize((int(W * z), int(H * z)), Image.BILINEAR).crop((int(W * (z - 1) / 2), int(H * (z - 1) / 2), int(W * (z - 1) / 2) + W, int(H * (z - 1) / 2) + H))
        elif s[0] in ('p', 'crowd'):
            src = photos[s[1]]; z = 1.0 + .09 * u / D; vw, vh = W * 1.12 / (1.12 / 1.0) / z * 1.0, H / z
            vw = W / z; cx = src.width / 2 + (18 if j % 2 else -18) * u / D
            fr = src.resize((W, H), Image.BILINEAR, box=(cx - vw / 2, src.height / 2 - vh / 2, cx + vw / 2, src.height / 2 + vh / 2))
        else:
            fr = cbg.copy()
            for cx, cy in flames:                                              # flicker
                fl = Image.new('L', (W, H), 0); ImageDraw.Draw(fl).ellipse((cx - 28, cy - 44, cx + 28, cy + 32), fill=255)
                k = .55 + .2 * math.sin(t * 17 + cx) + .1 * math.sin(t * 29); g = Image.new('RGBA', (W, H), (0xFF, 0xE6, 0xB0, 0)); g.putalpha(fl.filter(ImageFilter.GaussianBlur(22)).point(lambda v: int(v * k)))
                fr.alpha_composite(g)
        fr.alpha_composite(GRAD)
        if s[0] == 'v' and s[3] == 'open':
            text_block(fr, [('ההכנות', WHITE, None), ('בעיצומן', DEEP, LB)], 620, t, .35, 200)
            u2 = eo((t - 1.2) / .4)
            if u2 > 0:
                d = ImageDraw.Draw(fr); d.text((W / 2, 1120 + (1 - u2) * 20), 'שבת חיי שרה · חברון וקריית ארבע', font=F(RB, 52), fill=(255, 255, 255, int(255 * u2)), anchor='ma', direction='rtl')
        elif s[0] == 'crowd':
            text_block(fr, [('ובשבת הזאת', WHITE, None), ('חברון מתמלאת', DEEP, LB)], 1150, t, T0[j] + .2, 160)
        elif s[0] == 'close':
            text_block(fr, [('השבת, חיי שרה', WHITE, None), ('כולנו בעיר האבות', GOLD, None)], 300, t, T0[j] + .3, 150)
            u2 = eo((t - T0[j] - 1.5) / .5)
            if u2 > 0:
                d = ImageDraw.Draw(fr); d.text((W / 2, 1720), 'מחכים לכם', font=F(RB, 62), fill=(255, 255, 255, int(255 * u2)), anchor='ma', direction='rtl')
        label(fr, t)
        if s[0] != 'close' or u < 4.3: fr.alpha_composite(LOGO, ((W - LOGO.width) // 2, 80))
        else: fr.alpha_composite(LOGO, ((W - LOGO.width) // 2, 80))
        if u < .1 and j > 0: fr = Image.blend(fr, Image.new('RGBA', (W, H), (255, 255, 255, 255)), .35 * (1 - u / .1))
        if t > TOT - .6: fr = Image.blend(fr, Image.new('RGBA', (W, H), (0, 0, 0, 255)), (t - (TOT - .6)) / .6)
        if t < .25: fr = Image.blend(Image.new('RGBA', (W, H), (0, 0, 0, 255)), fr, t / .25)
        ff.stdin.write(fr.convert('RGB').tobytes())
    ff.stdin.close(); ff.wait()

def score(out):
    """Original warm score: D-major plucks over soft pads and a light kick, building into the closer."""
    SR = 48000; n = int(TOT * SR); x = np.zeros((n, 2)); rng = np.random.default_rng(2); BPM = 104; B = 60 / BPM
    hz = lambda m: 440 * 2 ** ((m - 69) / 12)
    def put(s, at, g=1, pan=0):
        i = int(at * SR); s = s[:max(0, n - i)]; x[i:i + len(s), 0] += s * g * (1 - max(0, pan)); x[i:i + len(s), 1] += s * g * (1 + min(0, pan))
    def pluck(m, d=.6):
        t = np.arange(int(d * SR)) / SR; return (np.sin(2 * np.pi * hz(m) * t) + .3 * np.sin(4 * np.pi * hz(m) * t)) * np.exp(-t / .22)
    def pad(ms, d):
        t = np.arange(int(d * SR)) / SR; s = sum(np.sin(2 * np.pi * hz(m) * t * (1 + dt)) for m in ms for dt in (-.002, .002)) / (2 * len(ms))
        return s * np.minimum(1, t / .6) * np.minimum(1, (d - t) / .6)
    def kick():
        t = np.arange(int(.35 * SR)) / SR; return np.sin(2 * np.pi * np.cumsum(50 + 90 * np.exp(-t * 30)) / SR) * np.exp(-t / .12)
    prog = [[62, 66, 69], [59, 62, 66], [55, 59, 62], [57, 61, 64]]          # D Bm G A
    arp = [0, 1, 2, 1, 2, 1, 0, 2]
    bar = 4 * B; k = 0; t = 0
    while t < TOT - .5:
        ch = prog[k % 4]; put(pad([c - 12 for c in ch], bar + .4), t, .22)
        for q in range(8): put(pluck(ch[arp[q]] + 12, .5), t + q * B / 2, .16, (-.3 if q % 2 else .3))
        if t > 3.4: [put(kick(), t + q * B, .5) for q in range(4)]
        t += bar; k += 1
    for at in [T0[j] for j in range(1, len(SHOTS))]:                         # soft hits on cuts are added as SFX in the mix
        pass
    ir_n = int(2 * SR); ir = rng.standard_normal((ir_n, 2)) * np.exp(-np.arange(ir_n) / SR / .4)[:, None]; ir /= np.sqrt((ir ** 2).sum(0))
    m = n + ir_n; wet = np.stack([np.fft.irfft(np.fft.rfft(x[:, c], m) * np.fft.rfft(ir[:, c], m), m)[:n] for c in range(2)], 1)
    y = x * .8 + wet * .9; f = int(1.2 * SR); y[-f:] *= np.linspace(1, 0, f)[:, None]; y = np.tanh(y / np.abs(y).max() * 1.2) / np.tanh(1.2) * .85
    w = wave.open(out, 'w'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((y * 32767).astype('<i2').tobytes()); w.close()

MUSIC = HERE + '/music.wav'      # Splice: NH_IFR_115_music_western_red_Gmaj (licensed via the user's Splice account)
def mix(out):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', MUSIC, '-af', f'aresample=48000,afade=t=in:d=0.4,afade=t=out:st={TOT - 1.4}:d=1.4,atrim=0:{TOT}', P + 'score.wav'], check=True)
    cues = [(P + 'score.wav', 0, .75), (SFX + 'whoosh.wav', .3, .4), (SFX + 'pop_soft.wav', .4, .6), (SFX + 'pop_soft.wav', .6, .5)]
    for j in range(1, len(SHOTS)): cues.append((SFX + ('swoosh_soft.wav' if j % 2 else 'whoosh.wav'), T0[j] - .1, .3))
    cues += [(SFX + 'chime_up.wav', T0[-1] + .3, .4)]
    args = ['ffmpeg', '-v', 'error', '-y']; fl = []
    for k, (f, at, v) in enumerate(cues):
        args += ['-i', f]; fl.append(f'[{k}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={v},adelay={int(max(0, at) * 1000)}|{int(max(0, at) * 1000)}[a{k}]')
    # the clip's own site sound, low, under the video shots
    args += ['-i', VID]; vi = len(cues)
    for q, j in enumerate([j for j, s in enumerate(SHOTS) if s[0] == 'v']):
        s = SHOTS[j]; fl.append(f'[{vi}:a]aformat=sample_rates=48000:channel_layouts=stereo,atrim={s[2]}:{s[2] + s[1]},asetpts=PTS-STARTPTS,volume=0.35,afade=t=in:d=0.1,afade=t=out:st={s[1] - .2}:d=0.2,adelay={int(T0[j] * 1000)}|{int(T0[j] * 1000)}[v{q}]')
    nv = sum(1 for s in SHOTS if s[0] == 'v')
    fl.append(''.join(f'[a{k}]' for k in range(len(cues))) + ''.join(f'[v{q}]' for q in range(nv)) + f'amix=inputs={len(cues) + nv}:normalize=0,atrim=0:{TOT:.3f},apad=whole_dur={TOT:.3f}[o]')
    subprocess.run(args + ['-filter_complex', ';'.join(fl), '-map', '[o]', out], check=True)

if __name__ == '__main__':
    if 'audio' not in sys.argv or not os.path.exists(P + 'v.mp4'): render(P + 'v.mp4')
    mix(P + 'a.wav')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', P + 'v.mp4', '-i', P + 'a.wav', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', P + 'm.mp4'], check=True)
    subprocess.run(['python3', LOUD, P + 'm.mp4', HERE + '/yesha-reel-chayei-sarah-prep.mp4', '--target', '-14'], check=True)
    print('done', TOT)
