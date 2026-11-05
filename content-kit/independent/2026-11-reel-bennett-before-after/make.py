"""Bennett: before the elections (archive VHS look) -> after the elections (news item inside a screen) -> closer.
Footage audio untouched; only SFX added. Text exactly as the user asked."""
import os, sys, math, glob, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageChops
HERE = os.path.dirname(os.path.abspath(__file__)); P = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/bennett/prep/'
os.makedirs(P, exist_ok=True)
SRC = '/root/.claude/uploads/1a5819ee-0cc0-5045-b086-4a8a80216453/79274151-copy_EE3DFFDC-F69B-47D7-913D-03036CD3A338.mov'
KB = glob.glob('/root/.claude/skills/synced/*/pro-video-editing/assets/fonts/Karantina-Bold.ttf')[0]
RUB = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/fonts/Rubik-700.ttf'
W, H, FPS = 1080, 1920, 30
T1 = 17.37; SRC_END = 37.6; CLOSE = 4.8; TOTAL = SRC_END + CLOSE
RED = (214, 32, 39); WHITE = (255, 255, 255); BLACK = (0, 0, 0)
_fc = {}
def F(p, s):
    k = (p, s)
    if k not in _fc: _fc[k] = ImageFont.truetype(p, s, layout_engine=ImageFont.Layout.RAQM)
    return _fc[k]
def eo(x): x = max(0, min(1, x)); return 1 - (1 - x) ** 3
def back(x, s=1.7): x = max(0, min(1, x)); x -= 1; return x * x * ((s + 1) * x + s) + 1
rng = np.random.default_rng(3)

def prep():
    if not os.path.exists(P + 'a/0001.png'):
        os.makedirs(P + 'a', exist_ok=True); os.makedirs(P + 'b', exist_ok=True)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-t', str(T1), '-i', SRC, '-vf', f'fps={FPS}', P + 'a/%04d.png'], check=True)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(T1), '-i', SRC, '-vf', f'fps={FPS},crop=1080:606:0:658', P + 'b/%04d.png'], check=True)
def fr(k, u):
    d = P + k + '/'; fs = sorted(os.listdir(d)); return Image.open(d + fs[max(0, min(len(fs) - 1, int(u * FPS)))]).convert('RGB')

SCAN = Image.new('L', (W, H), 0); sd = ImageDraw.Draw(SCAN)
for y in range(0, H, 4): sd.line((0, y, W, y), fill=70); sd.line((0, y + 1, W, y + 1), fill=35)
VIG = Image.new('L', (W, H), 0); vp = np.zeros((H, W), np.float32)
yy, xx = np.mgrid[0:H, 0:W]; r = np.sqrt(((xx - W / 2) / (W * .62)) ** 2 + ((yy - H / 2) / (H * .62)) ** 2)
VIG = Image.fromarray((np.clip((r - .55) / .6, 0, 1) * 200).astype('uint8'))

def vhs(im, t, amt=1.0):
    im = ImageEnhance.Color(im).enhance(.28); im = ImageEnhance.Contrast(im).enhance(.9)
    a = np.asarray(im).astype(np.int16)
    a = a * np.array([1.06, 1.0, .86]) + np.array([14, 8, 0])
    s = 7; out = a.copy(); out[:, s:, 0] = a[:, :-s, 0]; out[:, :-s, 2] = a[:, s:, 2]   # chroma bleed
    # tracking band rolling down + small line jitter
    band = int((t * 260) % (H + 300)) - 150
    for y in range(max(0, band), min(H, band + 60), 2):
        sh = int(rng.integers(-18, 18)); out[y] = np.roll(out[y], sh, axis=0); out[y] = out[y] * .8 + 50
    n = rng.normal(0, 14, (H // 2, W // 2, 1)).repeat(2, 0).repeat(2, 1)
    out = np.clip(out + n, 0, 255).astype('uint8')
    im = Image.fromarray(out).filter(ImageFilter.BoxBlur(.6))
    im = Image.composite(Image.new('RGB', (W, H), BLACK), im, SCAN)
    im = Image.composite(Image.new('RGB', (W, H), BLACK), im, VIG)
    return im

def outlined(d, xy, s, font, fill, stroke=10, anchor='ma', shadow=True):
    if shadow: d.text((xy[0] + 10, xy[1] + 12), s, font=font, fill=(0, 0, 0), anchor=anchor, direction='rtl', stroke_width=stroke, stroke_fill=(0, 0, 0))
    d.text(xy, s, font=font, fill=fill, anchor=anchor, direction='rtl', stroke_width=stroke, stroke_fill=(0, 0, 0))

def part_a(t):
    im = vhs(fr('a', t), t)
    d = ImageDraw.Draw(im)
    # OSD
    if int(t * 2) % 2 == 0 or t > 2:
        d.text((70, 90), 'PLAY', font=F(RUB, 52), fill=(235, 235, 235)); d.polygon([(232, 100), (232, 144), (268, 122)], fill=(235, 235, 235))
    d.text((70, 1780), 'ארכיון', font=F(RUB, 44), fill=(235, 235, 235), direction='rtl')
    # big title drops from the top at .25s, settles; shrinks into a lockup at 3.2s
    u = (t - .25) / .45
    if u > 0:
        y_off = -500 * (1 - back(u, 1.4)); k = eo((t - 3.2) / .6); sc = 1 - .38 * k; ytop = 170 - 40 * k
        lay = Image.new('RGBA', (W, 760), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        outlined(ld, (W / 2, 0), 'היחס לחרדים', F(KB, 230), WHITE, 11)
        f2 = F(KB, 170); tw = ld.textlength('לפני הבחירות', font=f2, direction='rtl')
        ld.rectangle((W / 2 - tw / 2 - 36, 250, W / 2 + tw / 2 + 36, 440), fill=(250, 250, 250)); ld.rectangle((W / 2 - tw / 2 - 36, 440, W / 2 + tw / 2 + 36, 452), fill=RED)
        ld.text((W / 2, 260), 'לפני הבחירות', font=f2, fill=BLACK, anchor='ma', direction='rtl')
        lay = lay.resize((int(W * sc), int(760 * sc)), Image.LANCZOS)
        im.paste(lay, (int((W - lay.width) / 2), int(ytop + y_off)), lay)
        if 0 <= t - .7 < .25: im = ImageChops.offset(im, int(rng.integers(-14, 14)), int(rng.integers(-14, 14)))
    return im

def static(alpha):
    n = (rng.random((H // 3, W // 3)) * 255).astype('uint8'); s = Image.fromarray(n).resize((W, H), Image.NEAREST).convert('RGB')
    return s, alpha

BLURBG = {}
def bg_b(u):
    k = int(u * FPS) // 3
    if k not in BLURBG:
        BLURBG.clear(); src = fr('b', u); bg = src.resize((int(1920 * 1080 / 606 * 606 / 1080 * 1080 / 606 * 1), 1920)) if False else src.resize((3422, 1920), Image.BILINEAR)
        x0 = (bg.width - W) // 2; bg = bg.crop((x0, 0, x0 + W, H)).filter(ImageFilter.GaussianBlur(40)); bg = ImageEnhance.Brightness(bg).enhance(.35)
        BLURBG[k] = bg
    return BLURBG[k].copy()

SW, SH_ = 1000, 561; SX, SY = (W - SW) // 2, 760
def part_b(t):
    u = t - T1; im = bg_b(u); d = ImageDraw.Draw(im)
    # screen enters: scale from .15 with slight rotation (back.out)
    k = back((u - .15) / .55, 1.6); kk = max(0, min(1, (u - .15) / .55))
    if kk > 0:
        scr = fr('b', u).resize((SW, SH_), Image.LANCZOS)
        fw, fh = SW + 36, SH_ + 36
        frame = Image.new('RGBA', (fw, fh), (0, 0, 0, 0)); fd = ImageDraw.Draw(frame)
        fd.rounded_rectangle((0, 0, fw - 1, fh - 1), 30, fill=(18, 18, 20, 255), outline=(70, 70, 76, 255), width=3)
        m = Image.new('L', (SW, SH_), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, SW - 1, SH_ - 1), 14, fill=255)
        frame.paste(scr, (18, 18), m)
        sc = .15 + .85 * k; rot = (1 - eo(kk)) * -8
        f2 = frame.resize((max(1, int(fw * sc)), max(1, int(fh * sc))), Image.LANCZOS).rotate(rot, expand=True, resample=Image.BICUBIC)
        sh = Image.new('RGBA', f2.size, (0, 0, 0, 0)); sh.putalpha(f2.getchannel('A').filter(ImageFilter.GaussianBlur(30)).point(lambda v: int(v * .7)))
        cx, cy = W // 2, SY + SH_ // 2
        im.paste((0, 0, 0), (cx - f2.width // 2 + 0, cy - f2.height // 2 + 30), sh)
        im.paste(f2, (cx - f2.width // 2, cy - f2.height // 2), f2)
    # header slams
    for i, (s, at, y, fill, blk) in enumerate([('היחס לחרדים', .45, 230, WHITE, None), ('אחרי הבחירות:', .75, 450, WHITE, RED)]):
        p = (u - at) / .18
        if p <= 0: continue
        sc = 1.6 - .6 * eo(p); f = F(KB, int(175 * sc)); al = min(1, p * 1.5)
        lay = Image.new('RGBA', (W, 400), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        if blk:
            tw = ld.textlength(s, font=f, direction='rtl'); ld.rectangle((W / 2 - tw / 2 - 30, 40, W / 2 + tw / 2 + 30, 40 + int(165 * sc)), fill=blk)
            ld.text((W / 2, 30), s, font=f, fill=fill, anchor='ma', direction='rtl')
        else: outlined(ld, (W / 2, 30), s, f, fill, 8)
        lay.putalpha(lay.getchannel('A').point(lambda v: int(v * al)))
        im.paste(lay, (0, int(y - 30 - (sc - 1) * 120)), lay)
    for at in (.45, .75):
        if 0 <= u - at < .2: im = ImageChops.offset(im, int(rng.integers(-12, 12)), int(rng.integers(-12, 12)))
    return im

def closer(t):
    u = t - SRC_END; im = Image.new('RGB', (W, H), (8, 8, 10)); d = ImageDraw.Draw(im)
    for s, at, y, hi, fs in [('בנט.', .25, 380, False, 330), ('פעם נוכל,', 1.25, 790, False, 230), ('תמיד נוכל.', 2.15, 1080, True, 230)]:
        p = (u - at) / .16
        if p <= 0: continue
        sc = 1.8 - .8 * eo(p); f = F(KB, int(fs * sc))
        lay = Image.new('RGBA', (W, 500), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        if hi:
            tw = ld.textlength(s, font=f, direction='rtl'); ld.rectangle((W / 2 - tw / 2 - 34, 50, W / 2 + tw / 2 + 34, 50 + int(218 * sc)), fill=RED)
            ld.text((W / 2, 40), s, font=f, fill=WHITE, anchor='ma', direction='rtl')
        else: ld.text((W / 2, 40), s, font=f, fill=WHITE, anchor='ma', direction='rtl')
        im.paste(lay, (0, int(y - 40 - (sc - 1) * 140)), lay)
    for at in (.25, 1.25, 2.15):
        if 0 <= u - at < .25: im = ImageChops.offset(im, int(rng.integers(-16, 16)), int(rng.integers(-16, 16)))
    if u < .12: im = Image.blend(im, Image.new('RGB', (W, H), WHITE), .6 * (1 - u / .12))
    return im

def frame(t):
    if t < T1 - .12: return part_a(t)
    if t < T1 + .18:   # VHS dropout: static burst
        base = part_a(min(t, T1 - .13)) if t < T1 else Image.new('RGB', (W, H), BLACK)
        s, _ = static(1); return Image.blend(base, s, .75)
    if t < SRC_END: return part_b(t)
    return closer(t)

AU = HERE + '/audio/'
def build_audio(out):
    T = f'{TOTAL:.2f}'
    hits = [('metal_impact', .7, .9), ('tape_stop', T1 - .3, 1.0), ('whoosh_hit', T1 + .05, .8), ('sub_impact', T1 + .75, 1.0),
            ('metal_impact', SRC_END + .25, 1.0), ('sub_impact', SRC_END + 1.25, .8), ('sub_impact', SRC_END + 2.15, 1.1)]
    ins = ['-i', SRC, '-stream_loop', '3', '-i', AU + 'music.wav']
    fl = [f'[0:a]aformat=sample_rates=48000:channel_layouts=stereo,loudnorm=I=-15:TP=-2,apad=whole_dur={T},asplit=2[v][key]',
          # music: dips while the footage speaks, rises on the hook and the closer
          f"[1:a]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:{T},volume='if(lt(t,3.2),0.9,if(gt(t,{SRC_END - .2:.2f}),1.0,0.42))':eval=frame,afade=t=out:st={TOTAL - 1.6:.2f}:d=1.6[m]",
          '[m][key]sidechaincompress=threshold=0.04:ratio=4:attack=20:release=300[md]']
    labs = []
    for k, (n, at, g) in enumerate(hits):
        ins += ['-i', AU + n + '.wav']; idx = 2 + k
        fl.append(f'[{idx}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={g},adelay={int(at * 1000)}:all=1[h{k}]'); labs.append(f'[h{k}]')
    fl.append(f"[v][md]{''.join(labs)}amix=inputs={2 + len(hits)}:normalize=0,alimiter=limit=0.95,atrim=0:{T}[o]")
    subprocess.run(['ffmpeg', '-v', 'error', '-y'] + ins + ['-filter_complex', ';'.join(fl), '-map', '[o]', out], check=True)

if __name__ == '__main__':
    prep()
    if len(sys.argv) > 1 and sys.argv[1] == 'stills':
        ts = [.5, 1.2, 5.0, 16.5, T1 + .05, T1 + .3, T1 + .9, 28, SRC_END + .5, SRC_END + 2.5]
        ims = [frame(x).resize((216, 384)) for x in ts]; sh = Image.new('RGB', (len(ims) * 220, 384))
        for k, x in enumerate(ims): sh.paste(x, (k * 220, 0))
        sh.save(P + '../stills.jpg'); print(TOTAL); sys.exit()
    if 'audio' in sys.argv: build_audio(P + 'a.wav'); sys.exit()
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', P + 'v.mp4'], stdin=subprocess.PIPE)
    for i in range(int(round(TOTAL * FPS))): ff.stdin.write(frame(i / FPS).tobytes())
    ff.stdin.close(); ff.wait()
    build_audio(P + 'a.wav')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', P + 'v.mp4', '-i', P + 'a.wav', '-c:v', 'libx264', '-preset', 'slow', '-crf', '21', '-maxrate', '10M', '-bufsize', '20M', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', P + 'mux.mp4'], check=True)
    LN = glob.glob('/root/.claude/skills/synced/*/pro-video-editing/scripts/loudnorm.py')[0]
    subprocess.run(['python3', LN, P + 'mux.mp4', HERE + '/bennett-before-after.mp4', '--target', '-14'], check=True)
    print('done', TOTAL)
