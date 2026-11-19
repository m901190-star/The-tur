"""Tochen Echad Premium intro, in the spirit of the Apple TV+ sting: an extreme close-up of the logo, layered translucent
gold copies at different depths rush back and collapse into the logo, it settles and shimmers, then the subscriber line.
Original synth score (swelling chord). Renders 16:9 and 9:16."""
import os, sys, math, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__)); P = HERE + '/prep/'; os.makedirs(P, exist_ok=True)
LOGO = HERE + '/../tochen-echad-premium-C-black-gold.png'
FB = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/pro-video-editing/assets/fonts/Karantina-Bold.ttf'
LOUD = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/pro-video-editing/scripts/loudnorm.py'
FPS, DUR = 30, 7.0
T_LAND, T_L1, T_L2, T_GLINT = 1.55, 2.5, 3.3, 2.0
CHAMP = (0xF7, 0xE3, 0x9C); GOLD = (0xD9, 0xAE, 0x4F)
# depth layers: tint, depth offset, x spread, y spread  (they collapse onto each other as the camera pulls back)
LAYERS = [((255, 214, 120), 0.00, 0.0, 0.0), ((255, 150, 40), 0.10, -1.0, .25), ((255, 240, 190), 0.22, 1.1, -.2),
          ((200, 120, 30), 0.36, -1.8, .4), ((255, 255, 255), 0.52, 1.9, -.35), ((230, 170, 60), 0.70, -2.6, .5)]

def eo(t): t = min(max(t, 0), 1); return 1 - (1 - t) ** 3
def eio(t): t = min(max(t, 0), 1); return t * t * (3 - 2 * t)

def load_logo():
    im = Image.open(LOGO).convert('RGBA'); return im

class Comp:
    def __init__(self, W, H, logo_w):
        self.W, self.H = W, H
        L = load_logo(); self.base = L; self.lw = logo_w; self.k0 = logo_w / L.width          # final screen scale
        A = np.asarray(L.getchannel('A'), np.float32) / 255
        self.tints = [Image.fromarray((np.dstack([np.full(A.shape, c[i]) for i in range(3)] + [A * 255])).astype(np.uint8), 'RGBA').filter(ImageFilter.GaussianBlur(dz * 22)) for c, dz, *_ in LAYERS]   # deeper copies are softer: glass, not cardboard
        g = L.getchannel('A').resize((L.width // 4, L.height // 4)).filter(ImageFilter.GaussianBlur(18)).resize(L.size)
        self.glow = Image.new('RGBA', L.size, GOLD + (0,)); self.glow.putalpha(g.point(lambda v: int(v * .6)))
        self.cx, self.cy = W / 2, H * (.42 if H > W else .40)
        self.macro = (L.width * .80, L.height * .30)                      # the point we start zoomed into (the gold mark)
        f1 = ImageFont.truetype(FB, int(logo_w * .11)); f2 = ImageFont.truetype(FB, int(logo_w * .075))
        self.l1 = self.line('למנויים מגיע תוכן בלעדי!', f1, highlight='בלעדי!')
        self.l2 = self.line('בקרוב! הירשמו עכשיו', f2)
        yy, xx = np.mgrid[0:H, 0:W]; r = np.sqrt(((xx - self.cx) / (W * .6)) ** 2 + ((yy - self.cy) / (H * .6)) ** 2)
        self.bg = (np.clip(1 - r, 0, 1) ** 2 * 16)[..., None] * np.array([1.0, .8, .45])[None, None]   # faint warm vignette

    def line(self, s, f, highlight=None):
        d = ImageDraw.Draw(Image.new('RGBA', (1, 1))); w = int(d.textlength(s, font=f, direction='rtl')) + 40
        im = Image.new('RGBA', (w, int(f.size * 1.5)), (0, 0, 0, 0)); dd = ImageDraw.Draw(im); y = f.size * .75
        if highlight and highlight in s:
            pre, post = s.split(highlight, 1); x = w - 20
            for seg, col in ((pre, (255, 255, 255)), (highlight, CHAMP), (post, (255, 255, 255))):
                if seg: dd.text((x, y), seg, font=f, fill=col, anchor='rm', direction='rtl'); x -= d.textlength(seg, font=f, direction='rtl')
        else: dd.text((w - 20, y), s, font=f, fill=(255, 255, 255, 230), anchor='rm', direction='rtl')
        return im.crop(im.getchannel('A').getbbox())

    def place(self, layer, scale, anchor, screen):
        """Affine-place `layer` so that point `anchor` (layer px) lands at `screen` with `scale`. Out-of-bounds is transparent."""
        a = 1 / scale
        data = (a, 0, anchor[0] - screen[0] * a, 0, a, anchor[1] - screen[1] * a)
        return np.asarray(layer.transform((self.W, self.H), Image.AFFINE, data, resample=Image.BILINEAR), np.float32)

    def frame(self, t):
        acc = np.zeros((self.H, self.W, 3), np.float32) + self.bg
        p = min(1, t / T_LAND); u = 1 - (1 - eio(p)) ** 1.6    # camera pull-back 0..1: lingers in the macro, then rushes back
        zoom = math.exp(math.log(9.0) * (1 - u))           # 9x macro -> 1x
        # the anchor glides from the macro point to the logo centre while pulling back
        ax = self.macro[0] + (self.base.width / 2 - self.macro[0]) * eio(u); ay = self.macro[1] + (self.base.height / 2 - self.macro[1]) * eio(u)
        spread = (1 - u) ** 1.4; settle = t > T_LAND
        for k, (tint, dz, sx, sy) in enumerate(LAYERS):
            if settle and k > 0: continue
            sc = self.k0 * zoom * (1 + dz * spread * 2.2)
            scr = (self.cx + sx * spread * self.W * .08, self.cy + sy * spread * self.H * .12)
            lay = self.place(self.tints[k], sc, (ax, ay), scr)
            alpha = lay[..., 3:4] / 255 * (.8 if k == 0 else .38 * spread + .02)
            acc = acc * (1 - alpha * .35) + lay[..., :3] * alpha * (.6 if k else 1)                          # additive: light, glassy overlaps
        # once settled: the real logo (gold mark, white wordmark) replaces the tinted stack, with a soft glow
        if t > T_LAND - .25:
            m = eo((t - (T_LAND - .25)) / .5); sc = self.k0 * zoom
            g = self.place(self.glow, sc, (ax, ay), (self.cx, self.cy)); acc += g[..., :3] * (g[..., 3:4] / 255) * .5 * m
            real = self.place(self.base, sc, (ax, ay), (self.cx, self.cy)); ra = real[..., 3:4] / 255 * m
            acc = acc * (1 - ra) + real[..., :3] * ra
            # glint across the settled logo
            gu = (t - T_GLINT) / .8
            if 0 < gu < 1:
                xs = np.arange(self.W)[None, :]; ys = np.arange(self.H)[:, None]
                pos = self.cx - self.lw * .7 + self.lw * 1.4 * eio(gu)
                band = np.exp(-(((xs - pos) + (ys - self.cy) * .45) / (self.lw * .05)) ** 2)[..., None]
                acc += band * ra * 140
        # breathing scale after landing (tiny push-in) is baked into the text positions below
        img = Image.fromarray(acc.clip(0, 255).astype(np.uint8)).convert('RGBA')
        ly = self.cy + self.base.height * self.k0 / 2 + self.lw * .10
        for line, t0, y in ((self.l1, T_L1, ly), (self.l2, T_L2, ly + self.l1.height + self.lw * .045)):
            a = eo((t - t0) / .55)
            if a > 0:
                L = line.copy(); w = int(L.width * a)                                       # right-to-left wipe + rise
                if w < 2: continue
                L = L.crop((L.width - w, 0, L.width, L.height)); L.putalpha(L.getchannel('A').point(lambda v: int(v * a)))
                img.alpha_composite(L, (int(self.cx + line.width / 2 - w), int(y + (1 - a) * 20)))
        out = img.convert('RGB')
        if t > DUR - .5: out = Image.blend(out, Image.new('RGB', out.size, (0, 0, 0)), (t - (DUR - .5)) / .5)
        return out

def render(W, H, lw, out):
    c = Comp(W, H, lw)
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-vf', 'noise=alls=4:allf=t', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for i in range(int(DUR * FPS)): ff.stdin.write(c.frame(i / FPS).tobytes())
    ff.stdin.close(); ff.wait()

def score(out):
    """Original: a deep swell that blooms into a warm major chord exactly as the logo lands, a shimmer on the glint, a soft tail."""
    SR = 48000; n = int(DUR * SR); t = np.arange(n) / SR; x = np.zeros((n, 2))
    rng = np.random.default_rng(4)
    def hz(m): return 440 * 2 ** ((m - 69) / 12)
    env_sw = np.clip(t / T_LAND, 0, 1) ** 2.2 * np.exp(-np.clip(t - T_LAND, 0, None) / 2.4)
    for m, g, pan in ((37, .9, 0), (49, .55, -.3), (56, .45, .3), (61, .4, -.2), (65, .35, .25), (68, .28, -.35), (73, .2, .35)):   # Db major, wide voicing
        f = hz(m) * (1 + .003 * np.sin(2 * np.pi * .3 * t + m))
        s = sum(np.sin(2 * np.pi * np.cumsum(f * (1 + d)) / SR + rng.random() * 6) for d in (-.002, 0, .002)) / 3
        bright = np.clip((t - .6) / T_LAND, 0, 1)
        s = s * (1 - .5 * (1 - bright)) + .25 * np.sign(s) * bright * .2
        x[:, 0] += s * env_sw * g * (1 - pan); x[:, 1] += s * env_sw * g * (1 + pan)
    # sub drop on the landing
    tt = np.clip(t - T_LAND, 0, None); sub = np.sin(2 * np.pi * np.cumsum(42 * np.exp(-tt * 1.8) + 28) / SR) * np.exp(-tt / .9) * (t > T_LAND)
    x += sub[:, None] * 1.1
    # reverse air into the landing
    air = rng.standard_normal(n); air = np.convolve(air, np.ones(8) / 8, 'same') * np.clip((t - .2) / (T_LAND - .2), 0, 1) ** 4 * (t < T_LAND)
    x += air[:, None] * .25
    # shimmer: bell partials on the glint
    for k, m in enumerate((85, 89, 92, 97)):
        t0 = T_GLINT + .12 * k; tt = np.clip(t - t0, 0, None)
        b = np.sin(2 * np.pi * hz(m) * tt) * np.exp(-tt / 1.1) * (t > t0) * .12
        x[:, 0] += b * (1 - (k % 2) * .6); x[:, 1] += b * (1 - ((k + 1) % 2) * .6)
    # simple stereo reverb
    ir_n = int(2.6 * SR); ir = rng.standard_normal((ir_n, 2)) * np.exp(-np.arange(ir_n) / SR / .55)[:, None]; ir /= np.sqrt((ir ** 2).sum(0))
    m = n + ir_n; wet = np.stack([np.fft.irfft(np.fft.rfft(x[:, c], m) * np.fft.rfft(ir[:, c], m), m)[:n] for c in range(2)], 1)
    y = x * .65 + wet * 1.6
    fade = int(.6 * SR); y[-fade:] *= np.linspace(1, 0, fade)[:, None]
    y = np.tanh(y / np.abs(y).max() * 1.3) / np.tanh(1.3) * .9
    w = wave.open(out, 'w'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((y * 32767).astype('<i2').tobytes()); w.close()

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'stills':
        c = Comp(1920, 1080, 1100); ts = [0.05, .4, .8, 1.1, 1.35, 1.7, 2.4, 3.2, 4.5]
        ims = [c.frame(x).resize((480, 270)) for x in ts]; sh = Image.new('RGB', (480 * 3, 270 * 3))
        for k, im in enumerate(ims): sh.paste(im, ((k % 3) * 480, (k // 3) * 270))
        sh.save(HERE + '/stills.jpg'); print('ok'); sys.exit()
    score(P + 'score.wav')
    for name, (W, H, lw) in {'16x9': (1920, 1080, 1100), '9x16': (1080, 1920, 880)}.items():
        render(W, H, lw, P + f'v_{name}.mp4')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', P + f'v_{name}.mp4', '-i', P + 'score.wav', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', P + f'm_{name}.mp4'], check=True)
        subprocess.run(['python3', LOUD, P + f'm_{name}.mp4', HERE + f'/tochen-echad-premium-intro-{name}.mp4', '--target', '-14'], check=True)
    print('done')
