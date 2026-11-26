"""Hadassah rehab reel, round 4: only Smotrich-with-fighters talk is heard (staff / cameraman chatter muted), hopeful guitar bed.
Round 3 (client notes): Roni removed entirely (Ammunition Hill, not Oct-7), new gentle strings bed
(old track was too loud / distorted), more atmosphere: the Gandel Rehabilitation Center entrance + the rehab-room sign.
Fighters' shots come from Moshe's cut with faces blurred (src/user_cut/cut_v2.mp4, made by blur_trim.py);
their sound comes from the original clips (frame-matched in-points), untouched apart from a static gain."""
import os, subprocess, numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
_src = open(HERE + '/make.py').read().split('\n')
exec('\n'.join(_src[:_src.index(next(l for l in _src if l.startswith('enc = ')))]))   # headline / HL / overlay / ease
V2 = HERE + '/src/user_cut/cut_v2.mp4'
MUSIC2 = HERE + '/music/guitar_neptune_F.wav'   # hopeful acoustic (client: strings felt like Memorial Day)
def S_(n): return f'{HERE}/src/IMG_{n}.MOV'
# (video_src, v_t0, dur, audio_src, a_t0, kind)   kind: 'amb' (b-roll ambience) | 'talk' (people talking) | stripe names
SHOTS = [
    (S_('2129'), 0.0, 3.2, None, 0, 'open'),     # entrance: "The Gandel Rehabilitation Center" -> building
    (V2, 0.07, 2.43, None, 0, 'open'),           # Smotrich walks the corridor
    (S_('2080'), 0.4, 1.1, None, 0, 'amb'),       # sign: "חדר טיפול שיקום"
    (V2, 4.97, 3.44, S_('2066'), 0.167, 'talk'),          # red shirt (blurred) with Smotrich
    (V2, 8.41, 3.40, S_('2075'), 3.50, 'talk'),
    (V2, 11.81, 1.70, None, 0, 'amb'),           # fighter on the bed (blurred)
    (V2, 13.51, 1.86, S_('2103'), 0.233, 'talk'),
    (V2, 15.37, 1.27, None, 0, 'amb'),
    (V2, 23.21, 3.20, None, 0, 'amb'),            # walking by the pool
    (V2, 26.41, 3.60, S_('2064'), 0.50, 'talk'),          # red shirt goodbye (blurred)
    (S_('2062'), 1.0, 1.3, None, 0, 'close'),             # rehab b-roll + "החלמה מהירה"
    (S_('2077'), 0.0, 0.9, None, 0, 'close'),
    (S_('2076'), 0.5, 1.2, None, 0, 'close'),
    (S_('2113'), 0.5, 2.6, None, 0, 'close'),
]
VF_SRC = f'scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},eq=contrast=1.05:saturation=1.08'
VF_V2 = f'fps={FPS}'
def rd(src, t0, dur, vf):
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', f'{t0:.3f}', '-t', f'{dur:.3f}', '-i', src, '-vf', vf, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    n = 0; N = int(round(dur * FPS)); last = None
    while n < N:
        b = p.stdout.read(W * H * 3)
        if len(b) < W * H * 3: break
        last = Image.frombytes('RGB', (W, H), b); yield last; n += 1
    p.stdout.close(); p.kill(); p.wait()
    while n < N and last is not None: yield last; n += 1
# group consecutive stripe shots so the stripe runs across cuts
spans = {}; T = 0
for s in SHOTS:
    if s[5] in ('open', 'close'): spans.setdefault(s[5], [T, T]); spans[s[5]][1] = T + s[2]
    T += s[2]
TOTAL = T
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                        '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-pix_fmt', 'yuv420p', HERE + '/_v3.mp4'], stdin=subprocess.PIPE)
T = 0
for (vs, vt, d, as_, at, kind) in SHOTS:
    for k, fr in enumerate(rd(vs, vt, d, VF_V2 if vs == V2 else VF_SRC)):
        t = T + k / FPS
        if kind == 'open' and vs.endswith('2129.MOV'):          # slow push-in on the entrance
            z = 1.0 + .06 * (k / FPS) / d; cw, ch = int(W / z), int(H / z)
            fr = fr.crop(((W - cw) // 2, (H - ch) // 2, (W - cw) // 2 + cw, (H - ch) // 2 + ch)).resize((W, H), Image.LANCZOS)
        if t < .5: fr = Image.blend(Image.new('RGB', (W, H)), fr, t / .5)
        if kind in spans:
            a0, a1 = spans[kind]; s0 = a0 + (.45 if kind == 'open' else .2)
            if t >= s0: fr = overlay(kind, fr, t - s0, a1 - s0)
        if t > TOTAL - .6: fr = Image.blend(fr.convert('RGB'), Image.new('RGB', (W, H)), (t - (TOTAL - .6)) / .6)
        enc.stdin.write(fr.convert('RGB').tobytes())
    T += d
enc.stdin.close(); enc.wait()
# ---------------- audio ----------------
sr = 48000; N = int(TOTAL * sr); out = np.zeros((N, 2), np.float32)
def ld(p, ss=0, t=None):
    c = ['ffmpeg', '-v', 'error', '-ss', str(ss)] + (['-t', str(t)] if t else []) + ['-i', p, '-ac', '2', '-ar', str(sr), '-f', 'f32le', '-']
    return np.frombuffer(subprocess.run(c, capture_output=True).stdout, np.float32).reshape(-1, 2).copy()
def rms_db(x): return 20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-9)
T = 0; talk_mask = np.zeros(N, np.float32)
for (vs, vt, d, as_, at, kind) in SHOTS:
    if as_:
        x = ld(as_, at, d + .04)
        tgt = -21 if kind == 'talk' else -30                       # talk scenes up front, ambience way down
        x *= min(10 ** ((tgt - rms_db(x)) / 20), 4.0)               # static gain only, no processing
        r = int(.03 * sr); f = np.ones(len(x)); f[:r] = np.linspace(0, 1, r); f[-r:] = np.linspace(1, 0, r)
        i = int(T * sr); m = min(len(x), N - i); out[i:i + m] += (x * f[:, None])[:m]
    if kind == 'talk': talk_mask[int(T * sr):int((T + d) * sr)] = 1
    T += d
# strings bed: loop with 1.5 s crossfades, ducked under the talk scenes
mu = ld(MUSIC2); xf = int(.06 * sr); bed = mu.copy()   # seamless loop, tiny crossfade
while len(bed) < N + sr:
    rr = np.linspace(0, 1, xf)[:, None]
    bed = np.concatenate([bed[:-xf], bed[-xf:] * (1 - rr) + mu[:xf] * rr, mu[xf:]])
bed = bed[:N] / (np.abs(mu).max() + 1e-9)
k = int(.35 * sr); duck = np.convolve(talk_mask, np.ones(k) / k, 'same')
lvl = .30 - .19 * duck                                               # ~-10 dB under talk
tt = np.arange(N) / sr; lvl *= np.clip(tt / 1.0, 0, 1) * np.clip((TOTAL - tt) / 1.8, 0, 1)
out += bed * lvl[:, None]
out *= 10 ** ((-17 - rms_db(out)) / 20)                              # static gain to a social-media level
pk = np.abs(out); over = pk > .85                                    # rare transients only: gentle soft knee, no compression
out[over] = np.sign(out[over]) * (.85 + .14 * np.tanh((pk[over] - .85) / .14))
print('soft-knee samples %', round(100 * over.mean(), 3))
out.tofile(HERE + '/_a3.raw')
final = HERE + '/smotrich-hadassah-final.mp4'
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', HERE + '/_v3.mp4', '-f', 'f32le', '-ar', str(sr), '-ac', '2', '-i', HERE + '/_a3.raw',
                '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', '-shortest', final], check=True)
os.remove(HERE + '/_v3.mp4'); os.remove(HERE + '/_a3.raw')
print('done', round(TOTAL, 2), spans)
