"""Moshe's 49 s CapCut cut of the Yesha reel, music removed (client adds 'רוח המחר' in Instagram).
His video is kept as-is; every piece of it was frame-matched to yesha-eshet-hayil-reel.mp4 and its sound is taken
from the music-free render (make.py --no-music) at the same reel time."""
import os, subprocess, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
CUT = HERE + '/src/user_cut/cut.mp4'; NOMUS = HERE + '/yesha-eshet-hayil-reel-no-music.mp4'
# (cut_start, cut_end, reel_time_at_cut_start)  from frame matching
SEGS = [(0.0, 4.53, 0.69), (4.53, 5.93, 5.89), (5.93, 8.13, 10.13), (8.13, 23.40, 14.48),   # (fine-tuned on speech envelopes)
        (23.40, 37.63, 33.23), (37.63, 43.17, 49.22), (43.17, 44.93, 54.76), (44.93, 49.10, 59.20)]
sr = 48000
def ld(p):
    return np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-ac', '2', '-ar', str(sr), '-f', 'f32le', '-'], capture_output=True).stdout, np.float32).reshape(-1, 2)
src = ld(NOMUS); cut = ld(CUT); N = len(cut); out = np.zeros((N, 2), np.float32); xf = int(.012 * sr)
for a, b, r in SEGS:
    i0, i1 = int(a * sr), min(N, int(b * sr)); j0 = int(r * sr)
    x = src[j0:j0 + (i1 - i0)].copy()
    if len(x) < i1 - i0: x = np.concatenate([x, np.zeros((i1 - i0 - len(x), 2), np.float32)])
    x[:xf] *= np.linspace(0, 1, xf)[:, None]; x[-xf:] *= np.linspace(1, 0, xf)[:, None]
    out[i0:i1] += x
out.tofile(HERE + '/_ucm.raw')
final = HERE + '/yesha-eshet-hayil-49s-no-music.mp4'
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', CUT, '-f', 'f32le', '-ar', str(sr), '-ac', '2', '-i', HERE + '/_ucm.raw',
                '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', '-shortest', final], check=True)
os.remove(HERE + '/_ucm.raw')
# sync check vs his audio (speech correlation per segment)
for a, b, r in SEGS:
    i0, i1 = int(a * sr), int(b * sr); u = cut[i0:i1, 0]; v = out[i0:i1, 0]
    print(a, b, 'corr', round(float(np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v) + 1e-9)), 2))
print(final)
