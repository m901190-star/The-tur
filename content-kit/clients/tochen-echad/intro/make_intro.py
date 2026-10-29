"""Tochen Echad podcast intro: logo sting (~5.5s). Renders 16:9 (1920x1080) and 9:16 (1080x1920).
Mark halves fly in and lock, wordmark wipes out from behind the mark, tagline follows, a glint sweeps the logo, push-in, out."""
import os, sys, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__)); P = HERE + '/prep/'; os.makedirs(P, exist_ok=True)
LOGO = HERE + '/../logo.png'
SFX = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/pro-video-editing/assets/sfx/'
LOUD = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/pro-video-editing/scripts/loudnorm.py'
FPS, DUR = 30, 5.6
INK = (0x14, 0x18, 0x1D); CHAR = (0x26, 0x2C, 0x33); YEL = (0xFF, 0xE4, 0x19)
SPLIT = 2089                                  # logo x where the mark starts
T_Y, T_W, T_WORD, T_TAG, T_GLINT, T_OUT = 0.35, 0.62, 1.05, 1.75, 2.35, 4.85

def eo(t): t = min(max(t, 0), 1); return 1 - (1 - t) ** 3
def eb(t, s=1.7): t = min(max(t, 0), 1) - 1; return t * t * ((s + 1) * t + s) + 1
def eio(t): t = min(max(t, 0), 1); return 3 * t * t - 2 * t * t * t

def layers():
    im = Image.open(LOGO).convert('RGBA'); a = np.array(im)
    yel = a[:, :, 2] < 120; mark = np.zeros(a.shape[:2], bool); mark[:, SPLIT:] = True
    def part(m):
        b = a.copy(); b[~m, 3] = 0; return Image.fromarray(b, 'RGBA')
    return im.size, part(yel & mark), part(~yel & mark), part(yel & ~mark), part(~yel & ~mark)

class Comp:
    def __init__(self, W, H, logo_w):
        self.W, self.H = W, H
        (lw, lh), my, mw, word, tag = layers()
        s = logo_w / lw; self.s = s
        rs = lambda im: im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
        self.my, self.mw, self.word, self.tag = rs(my), rs(mw), rs(word), rs(tag)
        self.ox, self.oy = (W - self.my.width) // 2, (H - self.my.height) // 2      # logo top-left
        self.split = int(SPLIT * s)
        self.glow = Image.new('RGBA', self.my.size, (0, 0, 0, 0))
        full = Image.alpha_composite(Image.alpha_composite(self.my, self.mw), Image.alpha_composite(self.word, self.tag))
        g = full.getchannel('A').filter(ImageFilter.GaussianBlur(28 * s * 2.2))
        self.glow = Image.new('RGBA', full.size, YEL + (0,)); self.glow.putalpha(g.point(lambda v: int(v * .55)))
        self.full = full
        # background: ink with a soft charcoal spotlight + film grain
        yy, xx = np.mgrid[0:H, 0:W]; r = np.sqrt(((xx - W / 2) / (W * .55)) ** 2 + ((yy - H / 2) / (H * .55)) ** 2)
        k = np.clip(1 - r, 0, 1)[..., None] ** 1.6
        self.bg = (np.array(INK)[None, None] * (1 - k) + np.array(CHAR)[None, None] * k * 1.25).clip(0, 255).astype(np.uint8)
        rng = np.random.default_rng(5)
        self.dust = [(rng.random() * W, rng.random() * H, .4 + rng.random() * 1.6, rng.random() * 6.28, 1 + rng.random() * 3) for _ in range(70)]
        self.grain = [(rng.standard_normal((H // 2, W // 2)) * 7).astype(np.int16) for _ in range(6)]

    def background(self, t):
        g = self.grain[int(t * FPS) % 6]; g = np.kron(g, np.ones((2, 2), np.int16))[:self.H, :self.W]
        img = Image.fromarray((self.bg.astype(np.int16) + g[..., None]).clip(0, 255).astype(np.uint8))
        d = ImageDraw.Draw(img, 'RGBA'); a_all = eo((t - 0.9) / 1.2) * (1 - eo((t - T_OUT) / .5))
        for x, y, sz, ph, sp in self.dust:                                  # slow rising yellow dust
            yy = (y - t * sp * 14) % self.H; xx = x + math.sin(t * .7 + ph) * 12
            al = int(90 * a_all * (.5 + .5 * math.sin(t * 2 + ph)))
            if al > 2: d.ellipse((xx - sz, yy - sz, xx + sz, yy + sz), fill=YEL + (al,))
        return img

    def streak(self, img, t):
        """A thin light streak across the frame before anything appears."""
        u = (t - 0.0) / 0.55
        if not 0 < u < 1.3: return
        lay = Image.new('RGBA', (self.W, self.H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        x = self.W * (1.15 - 1.3 * eio(u)); cy = self.H / 2
        for k, (w, al) in enumerate(((self.W * .5, 40), (self.W * .25, 90), (self.W * .08, 220))):
            d.rectangle((x - w / 2, cy - 1.5 - k, x + w / 2, cy + 1.5 + k), fill=YEL + (al,))
        lay = lay.filter(ImageFilter.GaussianBlur(3)); img.alpha_composite(lay) if img.mode == 'RGBA' else img.paste(lay, (0, 0), lay)

    def place(self, canvas, layer, dx, dy, sc=1.0, rot=0.0, alpha=1.0, crop=None):
        if alpha <= 0: return
        L = layer
        if crop: L = L.crop(crop); off = (crop[0], crop[1])
        else: off = (0, 0)
        if sc != 1 or rot:
            cx, cy = L.width / 2, L.height / 2
            L2 = L.resize((max(1, int(L.width * sc)), max(1, int(L.height * sc))), Image.BICUBIC)
            if rot: L2 = L2.rotate(rot, resample=Image.BICUBIC, expand=True)
            off = (off[0] + cx - L2.width / 2, off[1] + cy - L2.height / 2); L = L2
        if alpha < 1: L = L.copy(); L.putalpha(L.getchannel('A').point(lambda v: int(v * alpha)))
        canvas.alpha_composite(L, (int(self.ox + off[0] + dx), int(self.oy + off[1] + dy)))

    def logo_frame(self, t):
        c = Image.new('RGBA', (self.W, self.H), (0, 0, 0, 0)); s = self.s
        mx0, mx1 = self.split, self.my.width
        # yellow half: in from the right, spinning, overshoot
        u = (t - T_Y) / 0.5
        if u > 0:
            p = eb(u); self.place(c, self.my, (1 - p) * 900 * s * 2, -(1 - p) * 120 * s * 2, 1 + (1 - p) * .6, (1 - p) * -40, min(1, u * 4), crop=(mx0, 0, mx1, self.my.height))
        u = (t - T_W) / 0.45
        if u > 0:
            p = eb(u); self.place(c, self.mw, (1 - p) * 220 * s * 2, (1 - p) * 700 * s * 2, 1 + (1 - p) * .5, (1 - p) * 35, min(1, u * 4), crop=(mx0, 0, mx1, self.mw.height))
        # wordmark: wipes out from behind the mark, right to left
        u = eo((t - T_WORD) / .55)
        if u > 0:
            x0 = int(mx0 * (1 - u)); dx = (1 - u) * 60 * s * 2
            if mx0 - x0 > 2: self.place(c, self.word, dx, 0, 1.0, 0, 1.0, crop=(x0, 0, mx0, self.word.height))
        u = eo((t - T_TAG) / .5)
        if u > 0:
            x0 = int(mx0 * (1 - u)); self.place(c, self.tag, 0, (1 - u) * 18 * s * 2, 1, 0, u, crop=(x0, 0, mx0, self.tag.height))
        return c

    def glint(self, logo, t):
        u = (t - T_GLINT) / .7
        if not 0 < u < 1: return logo
        w, h = logo.size; band = Image.new('L', (w, h), 0); d = ImageDraw.Draw(band)
        x = -w * .3 + (w * 1.6) * eio(u); bw = w * .07
        d.polygon([(x, 0), (x + bw, 0), (x + bw - h * .5, h), (x - h * .5, h)], fill=255)
        band = band.filter(ImageFilter.GaussianBlur(bw * .35))
        hi = Image.new('RGBA', (w, h), (255, 255, 255, 0)); hi.putalpha(ImageChops.multiply(band, logo.getchannel('A')).point(lambda v: int(v * .85)))
        out = logo.copy(); out.alpha_composite(hi); return out

    def frame(self, t):
        img = self.background(t).convert('RGBA'); self.streak(img, t)
        # motion blur on the fast part: average sub-frames
        subs = [t + k / FPS / 4 for k in range(4)] if T_Y < t < T_W + .45 else [t]
        acc = None
        for st in subs:
            L = np.asarray(self.logo_frame(st), np.float32); acc = L if acc is None else acc + L
        logo = Image.fromarray((acc / len(subs)).astype(np.uint8), 'RGBA')
        logo = self.glint(logo, t)
        # slow push-in over the whole sting, a punch on the lock, and the out move
        z = 1 + .035 * t / DUR + .045 * math.exp(-max(0, t - (T_W + .45)) * 7) * (t > T_W + .45)
        ou = eio((t - T_OUT) / .6); z += ou * .25
        if z != 1:
            logo = logo.resize((int(self.W * z), int(self.H * z)), Image.BICUBIC); x0 = (logo.width - self.W) // 2; y0 = (logo.height - self.H) // 2
            logo = logo.crop((x0, y0, x0 + self.W, y0 + self.H))
        # glow behind the locked logo
        ga = eo((t - (T_W + .4)) / .6) * (.7 + .3 * math.sin(t * 2.2)) * (1 - ou)
        if ga > 0:
            g = self.glow.copy(); g.putalpha(g.getchannel('A').point(lambda v: int(v * ga))); img.alpha_composite(g, (self.ox, self.oy))
        # shockwave ring when the halves lock
        u = (t - (T_W + .45)) / .55
        if 0 < u < 1:
            ring = Image.new('RGBA', (self.W, self.H), (0, 0, 0, 0)); d = ImageDraw.Draw(ring)
            cx = self.ox + (self.split + self.my.width) / 2; cy = self.oy + self.my.height * .45; r = 40 + eo(u) * self.H * .7
            d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=YEL + (int(170 * (1 - u)),), width=max(1, int(10 * (1 - u))))
            img.alpha_composite(ring.filter(ImageFilter.GaussianBlur(2)))
        if ou < 1:
            if ou > 0: logo.putalpha(logo.getchannel('A').point(lambda v: int(v * (1 - ou))))
            img.alpha_composite(logo)
        # flash on lock
        fl = math.exp(-max(0, t - (T_W + .45)) * 12) if t > T_W + .45 else 0
        out = img.convert('RGB')
        if fl > .02: out = Image.blend(out, Image.new('RGB', out.size, (255, 250, 220)), .16 * fl)
        if t < .15: out = Image.blend(Image.new('RGB', out.size, (0, 0, 0)), out, t / .15)
        if t > DUR - .35: out = Image.blend(out, Image.new('RGB', out.size, (0, 0, 0)), (t - (DUR - .35)) / .35)
        return out

def render(W, H, logo_w, out):
    c = Comp(W, H, logo_w)
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for i in range(int(DUR * FPS)): ff.stdin.write(c.frame(i / FPS).tobytes())
    ff.stdin.close(); ff.wait()

def sound(out):
    """Synth sub-boom + kit SFX, timed to the animation."""
    SR = 48000; n = int(DUR * SR); x = np.zeros((n, 2))
    def put(sig, at, g=1.0):
        i = int(at * SR); sig = sig[:n - i]; x[i:i + len(sig)] += sig[:, None] * g if sig.ndim == 1 else sig * g
    t = np.arange(int(2.5 * SR)) / SR; f = 58 * np.exp(-t * 2.5) + 30
    put(np.tanh(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / .6) * 2.2), T_W + .45, .9)       # the lock
    rng = np.random.default_rng(1); r = np.arange(int(1.05 * SR)) / SR
    noise = rng.standard_normal(len(r)); noise = np.convolve(noise, np.ones(6) / 6, 'same')
    put(noise * (r / r[-1]) ** 3 * .35, T_W + .45 - 1.05, 1)                                         # rising air into the lock
    wave_path = P + 'synth.wav'
    import wave
    y = (x / max(1, np.abs(x).max() / .9) * 32767).astype('<i2'); w = wave.open(wave_path, 'w'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(y.tobytes()); w.close()
    cues = [(wave_path, 0, 1.0), (SFX + 'swoosh_soft.wav', 0.0, .35), (SFX + 'whoosh.wav', T_Y - .05, .7), (SFX + 'whoosh.wav', T_W - .05, .6),
            (SFX + 'impact.wav', T_W + .43, .8), (SFX + 'swoosh_soft.wav', T_WORD, .45), (SFX + 'blip.wav', T_TAG + .1, .25),
            (SFX + 'chime_up.wav', T_GLINT, .45), (SFX + 'whoosh.wav', T_OUT, .5)]
    args = ['ffmpeg', '-v', 'error', '-y']; fl = []
    for j, (f, at, v) in enumerate(cues):
        args += ['-i', f]; fl.append(f'[{j}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={v},adelay={int(at * 1000)}|{int(at * 1000)}[a{j}]')
    fl.append(''.join(f'[a{j}]' for j in range(len(cues))) + f'amix=inputs={len(cues)}:normalize=0,afade=t=out:st={DUR - .5}:d=0.5,atrim=0:{DUR},apad=whole_dur={DUR}[o]')
    subprocess.run(args + ['-filter_complex', ';'.join(fl), '-map', '[o]', out], check=True)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'stills':
        c = Comp(1920, 1080, 1250); ts = [.3, .55, .85, 1.2, 1.6, 2.1, 2.7, 3.8, 5.0]
        ims = [c.frame(x).resize((480, 270)) for x in ts]; sh = Image.new('RGB', (480 * 3, 270 * 3))
        for k, im in enumerate(ims): sh.paste(im, ((k % 3) * 480, (k // 3) * 270))
        sh.save(HERE + '/stills.jpg'); print('ok'); sys.exit()
    sound(P + 'sfx.wav')
    for name, (W, H, lw) in {'16x9': (1920, 1080, 1250), '9x16': (1080, 1920, 900)}.items():
        render(W, H, lw, P + f'v_{name}.mp4')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', P + f'v_{name}.mp4', '-i', P + 'sfx.wav', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', P + f'm_{name}.mp4'], check=True)
        subprocess.run(['python3', LOUD, P + f'm_{name}.mp4', HERE + f'/tochen-echad-intro-{name}.mp4', '--target', '-14'], check=True)
    print('done')
