"""Assemble 'מועכים ערכים' squishy reel: 5 AI shots + end still, Haim captions, permanent AI/satire label. 720x1280, silent."""
import os, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); G = HERE + '/gen/'
KB = HERE + '/../../fonts/HaimClassicv2FM-Bold.ttf'; SEC = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/shalev/fonts/SecularOne.ttf'
W, H, FPS = 720, 1280, 30; NAVY, RED = (24, 44, 104), (220, 40, 50)
def F(p, s): return ImageFont.truetype(p, s, layout_engine=ImageFont.Layout.RAQM)
def eo(x): x = max(0., min(1., x)); return 1 - (1 - x) ** 3
SHOTS = [('shot-open.mp4', 0.0, 4.2, None), ('shot-bennett.mp4', 0.0, 5.0, ['לא אשב עם', 'המפלגות הערביות']),
         ('shot-liberman.mp4', 0.0, 5.0, ['100% לחיילים!', '0% למשתמטים!']), ('shot-soldier.mp4', 0.0, 5.0, ['ברית המשרתים']),
         ('shot-envelope.mp4', 0.0, 5.0, ['צו גיוס'])]
def frames(path, t0, dur):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(t0), '-t', str(dur), '-i', path, '-vf', f'scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
def caption(im, lines, u):
    d = ImageDraw.Draw(im); p = eo(u / .3); f = F(KB, 74)
    for k, l in enumerate(lines):
        y = 860 + k * 84 + 20 * (1 - p); tw = d.textlength(l, font=f, direction='rtl')
        d.rounded_rectangle((W / 2 - tw / 2 - 22, y - 6, W / 2 + tw / 2 + 22, y + 80), 14, fill=(255, 255, 255, int(235 * p)))
        d.text((W / 2, y), l, font=f, fill=NAVY + (int(255 * p),), anchor='ma', direction='rtl')
def label(im):
    d = ImageDraw.Draw(im); f = F(SEC, 24); t = 'נוצר ב-AI · סאטירה'; tw = d.textlength(t, font=f, direction='rtl')
    d.rounded_rectangle((W - 24 - tw - 28, 120, W - 24, 162), 21, fill=(0, 0, 0, 150)); d.text((W - 24 - 14, 141), t, font=f, fill=(255, 255, 255, 235), anchor='rm', direction='rtl')
out = []
for name, t0, dur, cap in SHOTS:
    V = frames(G + name, t0, dur)
    HOLD = 1.0 if cap else 0.0                       # client: the text must be readable before the squeeze
    if HOLD: V = np.concatenate([np.repeat(V[:1], int(HOLD * FPS), 0), V])
    for i, fr in enumerate(V):
        im = Image.fromarray(fr).convert('RGBA'); lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        if cap: caption(lay, cap, i / FPS)
        label(lay); im.alpha_composite(lay); out.append(im.convert('RGB'))
end = Image.open(G + 'still-end.png').convert('RGB'); s = max(W / end.width, H / end.height); end = end.resize((int(end.width * s), int(end.height * s)), Image.LANCZOS)
ED = 3.5
for i in range(int(ED * FPS)):
    u = i / FPS; z = 1 + .06 * u / ED; e2 = end.resize((int(end.width * z), int(end.height * z)), Image.BILINEAR)
    x0 = (e2.width - W) // 2; y0 = (e2.height - H) // 2; im = e2.crop((x0, y0, x0 + W, y0 + H)).convert('RGBA')
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); p = eo((u - .3) / .4)
    if p > 0:
        d.rectangle((0, 470, W, 760), fill=NAVY + (int(225 * p),))
        d.text((W / 2, 500), 'הבטחות תקפות', font=F(KB, 96), fill=(255, 255, 255, int(255 * p)), anchor='ma', direction='rtl')
        d.text((W / 2, 615), 'עד למוצאי הבחירות', font=F(KB, 96), fill=(255, 255, 255, int(255 * p)), anchor='ma', direction='rtl')
    label(lay); im.alpha_composite(lay); out.append(im.convert('RGB'))
if out:
    out[0] = out[0]
# ---- SFX: plastic crinkle on the opening, squeeze + squish on every squishy, paper crumple on the signs ----
starts, t = [], 0.0
for name, t0, dur, cap in SHOTS: starts.append(t); t += dur + (1.0 if cap else 0.0)
EV = [('crinkle', starts[0] + .2, .55)]
for k in range(1, 5):
    EV += [('squeeze', starts[k] + 2.0, .9), ('squish', starts[k] + 2.5, .85), ('squish', starts[k] + 3.2, .6)]
    if k in (1, 2): EV.append(('paper', starts[k] + 2.2, .4))
TT = len(out) / FPS; ins, fl = [], []
for i, (n, at, v) in enumerate(EV):
    ins += ['-i', HERE + f'/sfx/{n}.wav']; dur = 1.6 if n in ('paper', 'crinkle') else 1.2
    fl.append(f'[{i + 1}:a]atrim=0:{dur},afade=t=out:st={dur - .3}:d=.3,aformat=sample_rates=48000:channel_layouts=stereo,volume={v},adelay={int(at * 1000)}:all=1[s{i}]')
fc = ';'.join(fl + [''.join(f'[s{i}]' for i in range(len(EV))) + f'amix=inputs={len(EV)}:normalize=0,apad=whole_dur={TT},atrim=0:{TT},loudnorm=I=-16:TP=-1.5[a]'])
ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-'] + ins + ['-filter_complex', fc, '-map', '0:v', '-map', '[a]',
    '-t', f'{TT}', '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-movflags', '+faststart', HERE + '/meuchim-arachim.mp4'], stdin=subprocess.PIPE)
for im in out: ff.stdin.write(im.tobytes())
ff.stdin.close(); ff.wait(); print('done', len(out) / FPS)
