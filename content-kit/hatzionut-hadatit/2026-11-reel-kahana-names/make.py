"""RZ reel: Smotrich 'who would you prefer' - MK photo cards fly in from both sides and collide.
Arab-list MKs (left) in B&W, Jewish MKs (right) in colour, per client concept. Splice music + impact. 720p out."""
import os, math, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); P = HERE + '/photos/'
KB = HERE + '/../../fonts/HaimClassicv2FM-Bold.ttf'
W, H, FPS = 1080, 1920, 30; DEEP, TEAL, LT = (43, 81, 85), (80, 146, 153), (105, 180, 189)
def F(s): return ImageFont.truetype(KB, s, layout_engine=ImageFont.Layout.RAQM)
def eo(x): x = max(0., min(1., x)); return 1 - (1 - x) ** 3
CW, CH = 420, 520
def card(photo, name, color):
    c = Image.new('RGBA', (CW, CH), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    top, bot = ((80, 146, 153), (30, 62, 66)) if color else ((95, 95, 95), (35, 35, 35))
    g = Image.new('RGBA', (CW, CH)); gd = ImageDraw.Draw(g)
    for y in range(CH): t = y / CH; gd.line((0, y, CW, y), fill=tuple(int(top[i] * (1 - t) + bot[i] * t) for i in range(3)) + (255,))
    m = Image.new('L', (CW, CH), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, CW - 1, CH - 1), 28, fill=255); c.paste(g, (0, 0), m)
    cut = Image.open(P + photo).convert('RGBA'); a = cut.getchannel('A').point(lambda v: 255 if v > 170 else 0).filter(ImageFilter.GaussianBlur(1)); cut.putalpha(a)
    cut = cut.crop(a.getbbox()); s = max((CW - 30) / cut.width, (CH - 70) / cut.height); cut = cut.resize((int(cut.width * s), int(cut.height * s)), Image.LANCZOS)
    if cut.width > CW: x0 = (cut.width - CW) // 2; cut = cut.crop((x0, 0, x0 + CW, cut.height))
    if cut.height > CH - 40: cut = cut.crop((0, 0, cut.width, CH - 40))
    if not color: cut = Image.merge('RGBA', (*[ImageOps.grayscale(cut.convert('RGB'))] * 3, cut.getchannel('A')))
    lay = Image.new('RGBA', (CW, CH), (0, 0, 0, 0)); lay.paste(cut, ((CW - cut.width) // 2, CH - cut.height), cut)
    c.alpha_composite(Image.composite(lay, Image.new('RGBA', (CW, CH), (0, 0, 0, 0)), m))
    d = ImageDraw.Draw(c); d.rounded_rectangle((0, CH - 96, CW, CH), 28, fill=(DEEP if color else (20, 20, 20)) + (240,)); d.rectangle((0, CH - 96, CW, CH - 70), fill=(DEEP if color else (20, 20, 20)) + (240,))
    d.text((CW / 2, CH - 50), name, font=F(54), fill=(255, 255, 255), anchor='mm', direction='rtl')
    d.rounded_rectangle((0, 0, CW - 1, CH - 1), 28, outline=(255, 255, 255), width=6)
    return c
PAIRS = [  # (bw card, colour card, t_left_in, t_contact, t_out)
    (card('jabareen-cut.png', "יוסף ג'בארין", False), card('mor-cut.png', 'צביקה מור', True), 3.95, 5.62, 7.0),
    (card('taha-cut.png', 'וואליד טאהא', False), card('madan-cut.png', 'אלישע מדן', True), 8.95, 11.15, 12.65)]
LX, RX, CY = 300, 780, 1470
def overlay(t):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); shake = (0, 0)
    for bw, col, ti, tc, to in PAIRS:
        if not (ti <= t < to + .4): continue
        out = eo((t - to) / .35) if t >= to else 0
        lx = -CW + (LX + CW) * eo((t - ti) / .35)
        if t >= tc: lx = LX - 34 * math.sin(min(1, (t - tc) / .25) * math.pi) * (1 - min(1, (t - tc) / .25))
        rin = tc - .28
        if t < rin: rx = W + CW
        elif t < tc: rx = W + CW / 2 + (RX - (W + CW / 2)) * ((t - rin) / .28) ** 1.6
        else: rx = RX + 34 * math.sin(min(1, (t - tc) / .25) * math.pi) * (1 - min(1, (t - tc) / .25))
        dy = int(900 * out ** 2)
        if t >= tc and t < tc + .35: k = 1 - (t - tc) / .35; shake = (int(16 * k * math.sin(t * 90)), int(10 * k * math.cos(t * 70)))
        for c, x, rot in ((bw, lx, 4), (col, rx, -4)):
            cc = c.rotate(rot, resample=Image.BICUBIC, expand=True); lay.alpha_composite(cc, (int(x - cc.width / 2), int(CY - cc.height / 2 + dy)))
        if tc <= t < tc + .18:   # impact flash
            k = 1 - (t - tc) / .18; fl = Image.new('RGBA', (W, H), (0, 0, 0, 0)); fd = ImageDraw.Draw(fl); r = 120 + 400 * (1 - k)
            fd.ellipse((540 - r, CY - r, 540 + r, CY + r), fill=(255, 255, 255, int(200 * k))); lay.alpha_composite(fl.filter(ImageFilter.GaussianBlur(30)))
    return lay, shake
if __name__ == '__main__':
    TT = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', HERE + '/source.mp4'], capture_output=True, text=True).stdout); N = int(TT * FPS)
    RD = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', HERE + '/source.mp4', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    EV = []
    for bw, col, ti, tc, to in PAIRS: EV += [('whoosh', ti - .05, .35), ('whoosh', tc - .3, .4), ('smash', tc - .02, .6)]
    ins, fl = [], []
    for i, (n, at, v) in enumerate(EV):
        ins += ['-i', HERE + f'/sfx/{n}.wav']; fl.append(f'[{i + 2}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={v},adelay={int(at * 1000)}:all=1[e{i}]')
    MI = len(EV) + 2
    fc = ';'.join(['[1:a]loudnorm=I=-16:TP=-1.5,aformat=sample_rates=48000:channel_layouts=stereo,asplit=2[v][k]'] + fl +
        [f"[{MI}:a]aformat=sample_rates=48000:channel_layouts=stereo,aloop=loop=3:size={int(19.2*44100)},atrim=0:{TT},volume='if(lt(t,13.2),0.22,0.08)':eval=frame,afade=t=in:d=0.8,afade=t=out:st={TT-1.5}:d=1.5[m]",
         '[m][k]sidechaincompress=threshold=0.04:ratio=4:attack=15:release=300[md]',
         '[v][md]' + ''.join(f'[e{i}]' for i in range(len(EV))) + f'amix=inputs={len(EV) + 2}:normalize=0,alimiter=limit=0.95[a]'])
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', HERE + '/source.mp4'] + ins + ['-i', HERE + '/sfx/music.wav',
        '-filter_complex', fc, '-map', '0:v', '-map', '[a]', '-vf', 'scale=720:1280:flags=lanczos', '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-maxrate', '4M', '-bufsize', '8M',
        '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-t', str(TT), '-movflags', '+faststart', HERE + '/rz-kahana-names.mp4'], stdin=subprocess.PIPE)
    for i in range(N):
        buf = RD.stdout.read(W * H * 3)
        if len(buf) < W * H * 3: break
        t = i / FPS; fr = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
        if any(ti <= t < to + .4 for _, _, ti, _, to in PAIRS):
            lay, (sx, sy) = overlay(t); im = Image.fromarray(fr).convert('RGBA')
            if sx or sy: im = Image.fromarray(np.roll(np.roll(np.array(im), sy, 0), sx, 1))
            im.alpha_composite(lay); fr = np.array(im.convert('RGB'))
        ff.stdin.write(fr.tobytes())
    ff.stdin.close(); ff.wait(); print('done', TT)
