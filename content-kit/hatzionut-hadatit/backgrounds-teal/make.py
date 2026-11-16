"""RZ teal background (grid + glow + floating dots), from the economy motion reel. Stills in 3 sizes + a seamless 10s 9:16 loop."""
import os, math, random, subprocess, numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
TEAL, PALE, NIGHT = (80, 146, 153), (173, 213, 217), (18, 40, 43)
def base(W, H):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); px = np.zeros((H, W, 3), np.float32)
    g = np.clip(1 - np.hypot((xx - W / 2) / (W * .75), (yy - H * .38) / (H * .5)), 0, 1) ** 1.5
    px += g[..., None] * (np.array(TEAL, np.float32) - np.array(NIGHT, np.float32)) * .75 + np.array(NIGHT, np.float32)
    px += ((xx % 60 < 1.5) | (yy % 60 < 1.5)).astype(np.float32)[..., None] * 9
    return Image.fromarray(np.clip(px, 0, 255).astype(np.uint8))
def dots(W, H, n, t, L=10.0, seed=3):
    random.seed(seed); lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); TILE = H / 4
    for _ in range(n):
        x, y, r, a, ph = random.uniform(0, W), random.uniform(0, H), random.uniform(2, 6), random.uniform(.15, .5), random.uniform(0, 1)
        q = (t / L + ph) % 1; y2 = y - 140 * q; x2 = x + 10 * math.sin(2 * math.pi * q); aa = a * math.sin(math.pi * q) * 1.3
        d.ellipse((x2 - r, y2 - r, x2 + r, y2 + r), fill=PALE + (int(255 * aa * .6),))
    return lay
for name, (W, H) in {'9x16': (1080, 1920), '1x1': (1080, 1080), '4x5': (1080, 1350), '16x9': (1920, 1080)}.items():
    im = base(W, H).convert('RGBA'); im.alpha_composite(dots(W, H, int(70 * W * H / (1080 * 1920)), 0)); im.convert('RGB').save(HERE + f'/rz-bg-teal-{name}.png')
W, H, FPS, L = 1080, 1920, 30, 10.0; B = base(W, H).convert('RGBA')
ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-crf', '20', '-pix_fmt', 'yuv420p',
                       '-movflags', '+faststart', HERE + '/rz-bg-teal-9x16-loop.mp4'], stdin=subprocess.PIPE)
for i in range(int(L * FPS)):
    im = B.copy(); im.alpha_composite(dots(W, H, 70, i / FPS, L)); ff.stdin.write(im.convert('RGB').tobytes())
ff.stdin.close(); ff.wait(); print('ok')
