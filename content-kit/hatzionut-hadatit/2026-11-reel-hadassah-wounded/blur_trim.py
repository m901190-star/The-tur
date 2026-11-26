"""Client notes on Moshe's cut: (1) drop "לפני 26 שנה בגבעת התחמושת" (cut 4.97 -> 7.73, end of the Roni shot);
(2) blur the faces of the fighters: red shirt (all his shots) and the fighter on the bed. Faces from YuNet (src/user_cut/cut_faces.json)."""
import os, json, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); W, H, FPS = 1080, 1920, 30
CUT = HERE + '/src/user_cut/cut.mp4'; OUT = HERE + '/src/user_cut/cut_v2.mp4'
DET = json.load(open(HERE + '/src/user_cut/cut_faces.json'))
DROP = (4.97, 7.73)
# segments: (t0, t1, rule)  rule = ('static', box) | ('pick', xmax)  -> leftmost detection with x < xmax
SEGS = [(7.73, 11.17, ('static', (0, 330, 390, 790))),       # red shirt, profile from behind
        (11.17, 14.57, ('pick', 500)),                         # red shirt facing camera
        (14.57, 16.27, ('pick', 300)),                         # fighter sitting on the bed (wide)
        (16.27, 18.13, ('pick', 500)),                         # fighter on the bed (close)
        (29.17, 32.80, ('pick', 520))]                         # red shirt standing with Smotrich
def pick(i, xmax):
    c = [d for d in DET[i] if d[0] < xmax and d[4] > .6] if i < len(DET) else []
    return min(c, key=lambda d: d[0])[:4] if c else None
# per-frame boxes with gap filling (nearest detection inside the segment) + smoothing
boxes = {}
for (t0, t1, rule) in SEGS:
    fr = list(range(int(round(t0 * FPS)), min(len(DET), int(round(t1 * FPS)))))
    if rule[0] == 'static':
        for i in fr: boxes[i] = rule[1]
        continue
    raw = {i: pick(i, rule[1]) for i in fr}; have = [i for i in fr if raw[i]]
    sm = None
    for i in fr:
        b = raw[i] or raw[min(have, key=lambda j: abs(j - i))]
        x, y, w, h = b; b = np.array([x, y, x + w, y + h], float)
        sm = b if sm is None else sm * .6 + b * .4
        boxes[i] = tuple(sm)
    if t0 == 14.57:   # before the first detection his face is half out of frame on the left
        for i in fr:
            if i < 15.0 * FPS: x0, y0, x1, y1 = boxes[i]; boxes[i] = (0, min(y0, 560), max(x1, 220), max(y1, 800))
def blur(im, b, pad=.45):
    x0, y0, x1, y1 = b; w, h = x1 - x0, y1 - y0
    x0, y0, x1, y1 = max(0, x0 - w * pad), max(0, y0 - h * pad), min(W, x1 + w * pad), min(H, y1 + h * pad * .8)
    bl = im.filter(ImageFilter.GaussianBlur(28)).filter(ImageFilter.BoxBlur(18))
    m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).ellipse((x0, y0, x1, y1), fill=255); m = m.filter(ImageFilter.GaussianBlur(10))
    return Image.composite(bl, im, m)
p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', CUT, '-vf', f'scale={W}:{H},fps={FPS}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                        '-c:v', 'libx264', '-crf', '16', '-preset', 'medium', '-pix_fmt', 'yuv420p', HERE + '/_v2v.mp4'], stdin=subprocess.PIPE)
i = 0; kept = 0
while True:
    b = p.stdout.read(W * H * 3)
    if len(b) < W * H * 3: break
    t = i / FPS
    if not (DROP[0] <= t < DROP[1]):
        im = Image.frombytes('RGB', (W, H), b)
        if i in boxes: im = blur(im, boxes[i])
        enc.stdin.write(im.tobytes()); kept += 1
    i += 1
enc.stdin.close(); enc.wait()
sr = 48000
a = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', CUT, '-ac', '2', '-ar', str(sr), '-f', 'f32le', '-'], capture_output=True).stdout, np.float32).reshape(-1, 2)
i0, i1, xf = int(round(DROP[0] * FPS)) * sr // FPS, int(round(DROP[1] * FPS)) * sr // FPS, int(.12 * sr)
ramp = np.linspace(0, 1, xf)[:, None]
mid = a[i0 - xf // 2:i0 + xf // 2] * (1 - ramp) + a[i1 - xf // 2:i1 + xf // 2] * ramp
out = np.concatenate([a[:i0 - xf // 2], mid, a[i1 + xf // 2:]]).astype(np.float32)[:int(kept / FPS * sr)]
out.tofile(HERE + '/_v2a.raw')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', HERE + '/_v2v.mp4', '-f', 'f32le', '-ar', str(sr), '-ac', '2', '-i', HERE + '/_v2a.raw',
                '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k', '-shortest', OUT], check=True)
os.remove(HERE + '/_v2v.mp4'); os.remove(HERE + '/_v2a.raw'); print('cut_v2', round(kept / FPS, 2))
