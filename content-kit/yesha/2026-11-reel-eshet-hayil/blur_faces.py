"""Client: blur the interviewee's face and every woman holding a weapon (and the instructor).
Input: Moshe's updated cut (src/user_cut/cut2.mp4). Faces: YuNet detections (src/user_cut/cut2_faces.json), held over
missed frames, plus hand-placed ellipses where the detector can't see the face (profiles / headscarves / motion)."""
import os, json, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); W, H, FPS = 1080, 1920, 30
SRC = HERE + '/src/user_cut/cut2.mp4'; OUT = HERE + '/yesha-eshet-hayil-blurred.mp4'
DET = json.load(open(HERE + '/src/user_cut/cut2_faces.json'))
SHOTS = [0.0, 9.56, 13.16, 15.16, 17.06, 21.26, 23.46, 32.32, 35.82, 40.06, 43.56, 44.99, 49.2]
# per-shot y-window where real faces can be (kills detections on the captions / sky)
YWIN = {0: (150, 700), 9.56: (450, 1000), 13.16: (400, 900), 15.16: (350, 1000), 17.06: (150, 1000), 21.26: (600, 1050),
        23.46: (150, 700), 32.32: (200, 700), 35.82: (150, 700), 40.06: (150, 900), 43.56: (150, 700), 44.99: (550, 1050)}
INTERVIEW = (0, 23.46, 35.82, 43.56)
# manual ellipses: (t0, t1, [(t, x0, y0, x1, y1), ...]) — linearly interpolated keyframes
MANUAL = [
    (15.17, 17.07, [(15.17, 220, 540, 520, 920), (16.2, 200, 540, 500, 920), (17.07, 190, 540, 470, 920)]),   # headscarf woman, profile
    (17.07, 18.3, [(17.07, 640, 260, 980, 640), (18.3, 600, 280, 960, 660)]),                                 # pink-scarf woman, side
    (17.07, 18.3, [(17.07, 30, 360, 230, 580), (18.3, 60, 380, 260, 600)]),                                   # woman left
    (32.33, 35.83, [(32.33, 520, 320, 780, 560), (34.0, 520, 280, 790, 520), (35.83, 530, 250, 790, 480)]),   # instructor
    (40.07, 43.57, [(40.07, 0, 480, 320, 760), (41.2, 0, 220, 320, 540), (42.4, 20, 260, 330, 560), (43.57, 40, 300, 330, 560)]),  # woman 1
    (41.0, 43.57, [(41.0, 720, 470, 1080, 810), (43.57, 760, 480, 1080, 800)]),                                # woman 2 (back of head)
]
HOLD = 14
def shot_of(t):
    for a, b in zip(SHOTS[:-1], SHOTS[1:]):
        if a <= t < b: return a, b
    return SHOTS[-2], SHOTS[-1]
def boxes_at(i):
    t = i / FPS; a, b = shot_of(t); y0w, y1w = YWIN[a]; out = []
    for j in range(max(int(round(a * FPS)), i - HOLD), min(int(round(b * FPS)), i + HOLD + 1, len(DET))):
        for (x, y, w, h, c) in DET[j]:
            if c < .45 or h > (480 if a in INTERVIEW else 330) or h < 18 or not (y0w <= y + h / 2 <= y1w): continue
            out.append((x, y, x + w, y + h, 1.0))
    for (m0, m1, keys) in MANUAL:
        if m0 <= t < m1:
            ks = sorted(keys)
            for k in range(len(ks) - 1):
                if ks[k][0] <= t <= ks[k + 1][0]:
                    f = (t - ks[k][0]) / max(1e-6, ks[k + 1][0] - ks[k][0])
                    bx = [ks[k][n] + (ks[k + 1][n] - ks[k][n]) * f for n in range(1, 5)]; out.append((*bx, 0.0)); break
            else: out.append((*ks[-1][1:], 0.0))
    return out
def blur(im, boxes):
    if not boxes: return im
    m = Image.new('L', (W, H), 0); d = ImageDraw.Draw(m)
    for (x0, y0, x1, y1, det) in boxes:
        w, h = x1 - x0, y1 - y0; px, py = (w * .45, h * .35) if det else (0, 0)
        d.ellipse((x0 - px, y0 - py * 1.2, x1 + px, y1 + py), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(9))
    bl = im.filter(ImageFilter.GaussianBlur(26)).filter(ImageFilter.BoxBlur(16))
    return Image.composite(bl, im, m)
p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', SRC, '-vf', f'scale={W}:{H},fps={FPS}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', SRC,
                        '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-pix_fmt', 'yuv420p',
                        '-c:a', 'copy', '-movflags', '+faststart', '-shortest', OUT], stdin=subprocess.PIPE)
i = 0
while True:
    b = p.stdout.read(W * H * 3)
    if len(b) < W * H * 3: break
    enc.stdin.write(blur(Image.frombytes('RGB', (W, H), b), boxes_at(i)).tobytes()); i += 1
enc.stdin.close(); enc.wait(); print('frames', i, OUT)
