"""Take Moshe's CapCut cut (src/user_cut/cut.mp4) as-is and add: opening stripe, a rehab b-roll tail
(machines, treadmill, stairs, pool) with the closing stripe, and continue his music bed (ensemble_am loop) under the tail."""
import os, sys, subprocess, numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(HERE + '/make.py').read().split('\n')
exec('\n'.join(src[:src.index(next(l for l in src if l.startswith('enc = ')))]))          # helpers: headline/HL/overlay/frames (stops before the make.py render)
CUT = HERE + '/src/user_cut/cut_v2.mp4'  # blurred and trimmed by blur_trim.py
CUT_D = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', CUT], capture_output=True, text=True).stdout)
OPEN_D = 4.6
TAIL = [('2062', 1.0, 1.3), ('2077', 0.0, 0.9), ('2076', 0.5, 1.2), ('2113', 0.5, 2.4)]
TAIL_D = sum(d for _, _, d in TAIL)
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                        '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-pix_fmt', 'yuv420p', HERE + '/_video_uc.mp4'], stdin=subprocess.PIPE)
def cut_frames():
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', CUT, '-vf', f'scale={W}:{H},fps={FPS}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    while True:
        b = p.stdout.read(W * H * 3)
        if len(b) < W * H * 3: break
        yield Image.frombytes('RGB', (W, H), b)
    p.wait()
n = 0
for fr in cut_frames():
    t = n / FPS
    im = overlay('open', fr, t, OPEN_D) if t < OPEN_D else fr
    enc.stdin.write(im.convert('RGB').tobytes()); n += 1
NCUT = n
k = 0; TOT = TAIL_D
for (c, st, d) in TAIL:
    for fr in frames(B(c), st, d):
        t = k / FPS
        im = overlay('close', fr, t, TOT) if not CLEAN else fr
        if t > TOT - .5: im = Image.blend(im.convert('RGB'), Image.new('RGB', (W, H)), (t - (TOT - .5)) / .5)
        enc.stdin.write(im.convert('RGB').tobytes()); k += 1
enc.stdin.close(); enc.wait()
# ---- audio: his mix untouched, music continues from where it is at the cut's end ----
sr = 48000
def ld(p): return np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-ac', '2', '-ar', str(sr), '-f', 'f32le', '-'], capture_output=True).stdout, np.float32).reshape(-1, 2).copy()
a = ld(CUT)[:int(NCUT / FPS * sr)]; m = ld(MUSIC)
seg = a[-int(2.5 * sr):, 0]; mm = m[:, 0]
from numpy.fft import rfft, irfft
N2 = 1 << int(np.ceil(np.log2(len(mm) + len(seg)))); c = irfft(rfft(mm, N2) * np.conj(rfft(seg, N2)), N2)
e = np.sqrt(np.convolve(mm ** 2, np.ones(len(seg)), 'valid')) + 1e-6; r = c[:len(e)] / e; i = int(r.argmax())
g = float(np.dot(mm[i:i + len(seg)], seg) / np.dot(mm[i:i + len(seg)], mm[i:i + len(seg)]))
pos = i + len(seg)                                   # music sample at the cut's end
ml = np.tile(m, (4, 1)); tail = g * ml[pos:pos + int(TAIL_D * sr)]
fo = np.ones(len(tail)); fo[-int(1.2 * sr):] = np.linspace(1, 0, int(1.2 * sr)); tail *= fo[:, None]
print('music pos', round(pos / sr, 2), 'gain', round(g, 3), 'corr', round(float(r.max() / np.sqrt(len(seg))), 2))
out = np.concatenate([a, tail.astype(np.float32)]); out.tofile(HERE + '/_a_uc.raw')
final = HERE + ('/smotrich-hadassah-final-clean.mp4' if CLEAN else '/smotrich-hadassah-final.mp4')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', HERE + '/_video_uc.mp4', '-f', 'f32le', '-ar', str(sr), '-ac', '2', '-i', HERE + '/_a_uc.raw',
                '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', '-shortest', final], check=True)
os.remove(HERE + '/_a_uc.raw'); os.remove(HERE + '/_video_uc.mp4')
print('done', round(NCUT / FPS + TAIL_D, 2), final)
