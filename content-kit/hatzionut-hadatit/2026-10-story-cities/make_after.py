"""Religious Zionism aftermovie: fast, full-bleed mix of the field clips and photos, cut to the chants. No locations, minimal graphics, no music."""
import os, sys, math, random, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_video import *          # colours, fonts, easing, logo, ballot, U/M/P paths
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

B = 0.5                            # one beat (120 bpm): photo cuts land on the grid
v = lambda n: M + n + '.mov'
ph = lambda n: U + n + '-image.jpg'
# (kind, src, start, dur[, opts]) — opts: audio=(file, start) replaces the clip's own sound, mute=True uses the chant bed,
# cut=fraction of the frame bottom to crop away, box=(x0, y0, x1, y1) photo crop
SHOTS = [
    ('v', v('v22'), 7.4, 3.6),                                   # market march, the chant leader
    ('p', ph('730c5ab5'), 0, B), ('p', ph('caadec50'), 0, B), ('p', ph('72b62016'), 0, B), ('p', ph('61660d37'), 0, B),
    ('v', v('v08-petahtikva'), 1.0, 2.5),
    ('p', ph('2e3afae4'), 0, B), ('p', ph('9050e4fb'), 0, B), ('p', ph('acd39014'), 0, B),
    ('v', v('v20'), 0.4, 2.8),                                   # night, flags, dancing
    ('p', ph('59cbbb2b'), 0, B), ('p', ph('4f010c1d'), 0, B, {'box': (0, 450, 620, 1550)}), ('p', ph('78e5bd5b'), 0, B),
    ('v', v('v01-telaviv'), 4.7, 3.4),
    ('p', ph('ea9a61af'), 0, B), ('p', ph('7e0b1fe1'), 0, B),
    ('v', v('v24'), 12.0, 2.2, {'cut': .2, 'mute': True}),
    ('v', v('v03-batyam'), 0.3, 2.8),
    ('p', ph('488d6f05'), 0, B), ('p', ph('537b1a3c'), 0, B), ('p', ph('d08a8e70'), 0, B),
    ('v', v('v21'), 1.0, 2.4),
    ('p', ph('4108a468'), 0, B), ('p', ph('caf39821'), 0, B),
    ('v', v('v06-katzrin'), 1.0, 1.5, {'mute': True}),
    # clip 4's own sound is not used (it may name the yeshiva); the Petah Tikva bus chant from clip 8 plays there
    ('v', v('v04-petahtikva'), 3.5, 2.3, {'audio': (v('v08-petahtikva'), 3.9)}),
    ('p', ph('6ea7f215'), 0, B), ('p', ph('5ef87594'), 0, B),
    ('v', v('v13-ashkelon'), 1.0, 2.3),
    ('v', v('v23'), 45.5, 1.8, {'mute': True}),
] + [('p', ph(n), 0, B / 2) for n in ('f3cca4bb', 'c98b45b3', '61660d37', '730c5ab5', '72b62016', 'caadec50', '4a4ef56a', '9050e4fb')]
END_D = 4.4
T0 = []; _t = 0
for s_ in SHOTS: T0.append(_t); _t += s_[3]
END_AT = _t; TOT = END_AT + END_D
opt = lambda s_: s_[4] if len(s_) > 4 else {}
_dur = {}
def fdur(f):
    if f not in _dur: _dur[f] = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]))
    return _dur[f]
# sound: clips play their chant; photos and muted clips ride on with the previous chant (L-cut), falling back to the market chant
BED = [(v('v22'), 7.0, 11.2), (v('v03-batyam'), 0.3, 4.8), (v('v20'), 3.4, 11.5), (v('v21'), 3.4, 7.0)]
AUD = []
cur = None; bed_i = 0
for j, s_ in enumerate(SHOTS):
    o = opt(s_); d = s_[3]
    if s_[0] == 'v' and not o.get('mute'):
        f, p0 = o.get('audio', (s_[1], s_[2])); cur = [f, p0, fdur(f)]
    elif cur is None or cur[1] + d > cur[2] - .05 or (cur[0] == v('v22') and cur[1] + d > 11.2):
        f, a0, a1 = BED[bed_i % len(BED)]; bed_i += 1; cur = [f, a0, a1 if a1 < fdur(f) else fdur(f)]
    AUD.append((cur[0], cur[1], T0[j], d)); cur[1] += d
AUD.append((v('v22'), 7.0, END_AT, 2.6))

def cover(im, w=W, h=H, fx=.5):
    s = max(w / im.width, h / im.height); im = im.resize((int(im.width * s + .5), int(im.height * s + .5)), Image.LANCZOS)
    x0 = int(max(0, min(im.width - w, im.width * fx - w / 2)))
    return im.crop((x0, (im.height - h) // 2, x0 + w, (im.height - h) // 2 + h))
# wide group shots stay whole (full width over a blurred copy); others fill the frame around their subject
FIT = {'61660d37', 'caadec50', 'ea9a61af', '7e0b1fe1', 'd08a8e70'}
FOCUS = {'4108a468': .64, '9050e4fb': .42, 'caf39821': .45}

def grade(im):
    im = ImageEnhance.Contrast(im).enhance(1.12); im = ImageEnhance.Color(im).enhance(1.15)
    return im
VIG = Image.new('L', (W, H), 0); _vd = ImageDraw.Draw(VIG)
for k in range(60):
    r = k / 60; _vd.ellipse((-W * .35 * (1 - r) - 40, -H * .25 * (1 - r) - 40, W + W * .35 * (1 - r) + 40, H + H * .25 * (1 - r) + 40), fill=int(150 * (1 - r) ** 2))
VIG = VIG.filter(ImageFilter.GaussianBlur(60)); BLACK = Image.new('RGB', (W, H), (0, 0, 0))

class Shot:
    def __init__(self, s, j):
        self.kind, self.src, self.ss, self.d = s[:4]; self.o = opt(s)
        big = (int(W * 1.18), int(H * 1.18))
        if self.kind == 'p':
            im = Image.open(self.src).convert('RGB'); key = os.path.basename(self.src)[:8]
            if 'box' in self.o: im = im.crop(self.o['box'])
            if key in FIT:
                bg = ImageEnhance.Brightness(cover(im, *big).filter(ImageFilter.GaussianBlur(30))).enhance(.55)
                fg = im.resize((big[0] - 60, int((big[0] - 60) * im.height / im.width)), Image.LANCZOS)
                bg.paste(fg, (30, (big[1] - fg.height) // 2)); self.img = grade(bg)
            else:
                self.img = grade(cover(im, *big, fx=FOCUS.get(key, .5)))
        else:
            self.dir = P + f'a{j:02d}/'; os.makedirs(self.dir, exist_ok=True)
            w, h = map(int, subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', self.src]).decode().split(','))
            self.vert = h > w
            cut = self.o.get('cut', 0)      # crop away a burned-in caption bar at the bottom
            pre = f'crop=iw*{1 - cut:.3f}:ih*{1 - cut:.3f}:iw*{cut / 2:.3f}:0,' if cut else ''
            vf = (f'fps={FPS},{pre}scale={big[0]}:-2:flags=lanczos,crop={big[0]}:{big[1]},unsharp=5:5:0.6' if self.vert
                  else f'fps={FPS},scale={W}:-2:flags=lanczos,unsharp=5:5:0.6')
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(self.ss), '-t', str(self.d + .2), '-i', self.src, '-vf', vf, self.dir + '%04d.png'], check=True)
            self.fr = sorted(os.listdir(self.dir))
            if not self.vert:
                mid = Image.open(self.dir + self.fr[len(self.fr) // 2]).convert('RGB')
                self.bg = ImageEnhance.Brightness(cover(mid, *big).filter(ImageFilter.GaussianBlur(30))).enhance(.55)

    def raw(self, u):
        if self.kind == 'p': return self.img
        f = grade(Image.open(self.dir + self.fr[min(len(self.fr) - 1, int(u * FPS))]).convert('RGB'))
        if self.vert: return f
        c = self.bg.copy(); c.paste(f, ((c.width - f.width) // 2, (c.height - f.height) // 2)); return c

    def frame(self, u, j):
        src = self.raw(u)
        # punch-in on the cut, then a slow drift; photos alternate drift direction
        z = 1.0 + 0.10 * math.exp(-u * 9) + (0.05 * u / max(self.d, .5) if self.kind == 'p' else 0.02 * u / self.d)
        vw, vh = W * 1.18 / z / 1.18 * 1.0, H / z
        vw = W / z; dx = (25 if j % 2 else -25) * (u / max(self.d, .5)) if self.kind == 'p' else 0
        shake = 14 * math.exp(-u * 14) * math.sin(u * 90)
        cx, cy = src.width / 2 + dx + shake, src.height / 2 + shake * .6
        return src.resize((W, H), Image.BILINEAR, box=(cx - vw / 2, cy - vh / 2, cx + vw / 2, cy + vh / 2))

def slam(img, s, size, y, t0, t, color, block=None):
    u = (t - t0) / 0.16
    if u <= 0: return
    a = ease_out(u); sc = 1.7 - 0.7 * ease_out(u)
    lay = Image.new('RGBA', (W, int(size * 1.6)), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    if block:
        tx = tw(ld, s, size); ld.rectangle(((W - tx) / 2 - 34, size * 0.12, (W + tx) / 2 + 34, size * 1.28), fill=block + (255,))
    text(ld, (W / 2, size * 0.7), s, size, color, anchor='mm')
    lay = lay.resize((int(W * sc), int(lay.height * sc)), Image.BILINEAR); lay.putalpha(lay.getchannel('A').point(lambda v: int(v * a)))
    img.paste(lay, ((W - lay.width) // 2, int(y - lay.height / 2)), lay)

END_BG = Image.new('RGB', (W, H)); _e = ImageDraw.Draw(END_BG)
for y in range(H): _e.line([(0, y), (W, y)], fill=tuple(int(DEEP[k] + (TEAL_D[k] - DEEP[k]) * y / H) for k in range(3)))
LOGO_SMALL = logo_img(190)

def frame(t, shots, last):
    if t >= END_AT:
        u = t - END_AT
        img = last.copy() if u < 0.12 else END_BG.copy()
        if u < 0.12: img = Image.blend(img, Image.new('RGB', (W, H), WHITE), 1 - u / 0.12)
        slam(img, 'בכל הארץ', 220, 620, 0.15, u, WHITE)
        slam(img, 'כן. סמוטריץ׳.', 190, 870, 0.65, u, WHITE, block=TEAL)
        la = ease_out((u - 1.25) / 0.35)
        if la > 0:
            lg = LOGO_END.copy(); lg.putalpha(lg.getchannel('A').point(lambda v: int(v * la))); img.paste(lg, ((W - lg.width) // 2, 1240 - lg.height // 2), lg)
        return img
    j = max(k for k in range(len(SHOTS)) if T0[k] <= t + 1e-6); u = t - T0[j]
    img = shots[j].frame(u, j)
    img = Image.composite(BLACK, img, VIG)
    if u < 0.07: img = Image.blend(img, Image.new('RGB', (W, H), WHITE), 0.45 * (1 - u / 0.07))    # flash on every cut
    img.paste(LOGO_SMALL, ((W - LOGO_SMALL.width) // 2, 70), LOGO_SMALL)
    return img

def render(out):
    shots = [Shot(s, j) for j, s in enumerate(SHOTS)]
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-vf', 'noise=alls=7:allf=t', '-c:v', 'libx264', '-preset', 'medium', '-crf', '21', '-maxrate', '12M', '-bufsize', '24M', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    last = None
    for i in range(int(round(TOT * FPS))):
        img = frame(i / FPS, shots, last)
        if i / FPS < END_AT: last = img
        ff.stdin.write(add_ballot(img.convert('RGB')).tobytes())
    ff.stdin.close(); ff.wait()

def mix(out_wav):
    S_ = lambda n: SFX + n + '.wav'
    cues = [(f, s0, at, d, 1.0) for f, s0, at, d in AUD]
    for j, s in enumerate(SHOTS):                       # a hit on every cut keeps the beat
        if s[0] == 'p': cues.append((S_('hit_soft' if s[3] >= B else 'click'), 0, T0[j], 0, .55 if s[3] >= B else .5))
        else: cues.append((S_('whoosh'), 0, max(0, T0[j] - .12), 0, .35))
    cues += [(S_('impact'), 0, END_AT, 0, .6), (S_('hit_soft'), 0, END_AT + .65, 0, .9), (S_('chime_up'), 0, END_AT + 1.25, 0, .4)]
    args = ['ffmpeg', '-v', 'error', '-y']; fl = []
    for j, (f, s0, at, d, vol) in enumerate(cues):
        args += ['-i', f]
        ex = f',atrim={s0}:{s0 + d},asetpts=PTS-STARTPTS,loudnorm=I=-16:TP=-2,afade=t=in:d=0.05,afade=t=out:st={d - 0.12}:d=0.12' if d else ''
        fl.append(f'[{j}:a]aformat=sample_rates=48000:channel_layouts=stereo{ex},volume={vol},adelay={int(at * 1000)}|{int(at * 1000)}[a{j}]')
    fl.append(''.join(f'[a{j}]' for j in range(len(cues))) + f'amix=inputs={len(cues)}:normalize=0,afade=t=out:st={TOT - 0.6}:d=0.6,atrim=0:{TOT:.3f},apad=whole_dur={TOT:.3f}[out]')
    subprocess.run(args + ['-filter_complex', ';'.join(fl), '-map', '[out]', out_wav], check=True)

if __name__ == '__main__':
    os.makedirs(P, exist_ok=True)
    if len(sys.argv) > 1 and sys.argv[1] == 'stills':
        shots = [Shot(s, j) for j, s in enumerate(SHOTS)]
        ts = [T0[j] + min(.3, SHOTS[j][3] / 2) for j in range(0, len(SHOTS), 2)][:7] + [TOT - 1]
        im = [add_ballot(frame(tt, shots, None).convert('RGB')) for tt in ts]
        sh = Image.new('RGB', (len(im) * 250, 440), WHITE)
        for k, x in enumerate(im): sh.paste(x.resize((240, 427)), (k * 250, 0))
        sh.save(HERE + '/stills3.jpg'); print('stills', TOT)
    else:
        render(P + 'v3.mp4'); mix(P + 'a3.wav')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', P + 'v3.mp4', '-i', P + 'a3.wav', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', P + 'mux3.mp4'], check=True)
        subprocess.run(['python3', SKILL + '/scripts/loudnorm.py', P + 'mux3.mp4', HERE + '/rz-aftermovie.mp4', '--target', '-14'], check=True)
        print('done', TOT)
