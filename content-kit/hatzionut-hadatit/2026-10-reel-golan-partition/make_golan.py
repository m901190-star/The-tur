"""Religious Zionism attack reel: Yair Golan on partition (1080x1920, 30fps). Dark, no music: clock, heartbeat, drone, hits.
The quote is shown in full and unaltered; the Abu Mazen line is the party's message, not a quote."""
import os, sys, math, subprocess
RZ = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/rz2'
sys.path.insert(0, RZ)
from make_video import (W, H, FPS, F, text, tw, ease_out, ease_back, chevron, logo_img, SKILL, SFX,
                        DEEP, TEAL_D, TEAL, TEAL_L, PALE, MIST, WHITE)
from make_video import ballot_card
from make_map import OUTLINE, KINNERET, geo
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageChops, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__)); P = HERE + '/prep/'; os.makedirs(P, exist_ok=True)
SRC = '/root/.claude/uploads/1a5819ee-0cc0-5045-b086-4a8a80216453/e80ff434-313375444314171030.mp4'
RED = (0xE5, 0x24, 0x2B); BLACK = (0, 0, 0); INK = (0x0B, 0x0F, 0x10)

# ---------- timeline ----------
HOOK = 3.2
G1 = (HOOK, 3.0)              # clip 0.0-3.0: "מבחינתי, חלוקת הארץ היא הדרך היחידה"
FRZ = (HOOK + 3.0, 1.3)       # freeze on the last frame of that line
G2 = (FRZ[0] + FRZ[1], 4.8)   # clip 3.0-7.8: the rest of the sentence
MAP = (G2[0] + G2[1], 6.0)
HUSH = (MAP[0] + MAP[1], 0.5)
TURN = (HUSH[0] + HUSH[1], 1.8)
CLOSE = (TURN[0] + TURN[1], 4.6)
TOTAL = CLOSE[0] + CLOSE[1]
LINES = [(0.0, 3.0, 'מבחינתי, חלוקת הארץ היא', 'הדרך היחידה'), (3.0, 5.5, 'לשמור על בית לאומי לעם היהודי', 'בארץ ישראל'), (5.5, 7.8, 'מדינה יהודית,', 'ציונית ודמוקרטית')]

def glitch(img, amt):
    if amt < 1: return img
    r, g, b = img.split(); r = ImageChops.offset(r, int(amt), 0); b = ImageChops.offset(b, -int(amt), 0)
    return Image.merge('RGB', (r, g, b))

def slam(img, s, size, y, t0, t, color=WHITE, block=None, dur=0.16, x=None):
    u = (t - t0) / dur
    if u <= 0: return
    a = ease_out(u); sc = 1.8 - 0.8 * ease_out(u)
    lay = Image.new('RGBA', (W, int(size * 1.6)), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    if block:
        tx_ = tw(ld, s, size); ld.rectangle(((W - tx_) / 2 - 34, size * 0.12, (W + tx_) / 2 + 34, size * 1.3), fill=block + (255,))
    text(ld, (W / 2, size * 0.72), s, size, color, anchor='mm')
    lay = lay.resize((int(W * sc), int(lay.height * sc)), Image.BILINEAR); lay.putalpha(lay.getchannel('A').point(lambda v: int(v * a)))
    img.paste(lay, ((W - lay.width) // 2, int(y - lay.height / 2)), lay)

def shake(t, hits, k=22):
    for h in hits:
        d = t - h
        if 0 <= d < 0.25: return int(k * math.exp(-d * 18) * math.sin(d * 110)), int(k * .6 * math.exp(-d * 18) * math.cos(d * 95))
    return 0, 0

LOGO_S = logo_img(170)
BALLOT_BIG = ballot_card(300, -7)
VIG = Image.new('L', (W, H), 0); _v = ImageDraw.Draw(VIG)
for k in range(60):
    r = k / 60; _v.ellipse((-W * .4 * (1 - r) - 40, -H * .3 * (1 - r) - 40, W + W * .4 * (1 - r) + 40, H + H * .3 * (1 - r) + 40), fill=int(190 * (1 - r) ** 2))
VIG = VIG.filter(ImageFilter.GaussianBlur(60))
def vignette(img): return Image.composite(Image.new('RGB', (W, H), BLACK), img, VIG)

# ---------- clip ----------
CLIPF = P + 'clip/'
def prep_clip():
    os.makedirs(CLIPF, exist_ok=True)
    # crop the burned-in subtitles away; we set our own (same words)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', SRC, '-t', '7.9', '-vf', f'fps={FPS},crop=720:395:0:0,scale={W}:-2:flags=lanczos,unsharp=5:5:0.6', CLIPF + '%04d.png'], check=True)
def clip_frame(ct):
    fs = sorted(os.listdir(CLIPF)); return Image.open(CLIPF + fs[min(len(fs) - 1, int(ct * FPS))]).convert('RGB')
CY = 560      # clip top

def caption(img, l1, l2, u, hot=None):
    a = ease_out(u / 0.15)
    lay = Image.new('RGBA', (W, 330), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    for k, ln in enumerate((l1, l2)):
        size = 92; y = 80 + k * 120
        if hot and hot in ln:                       # draw the key words in red, rest white (RTL: compose right to left)
            pre, post = ln.split(hot, 1); x = (W + tw(ld, ln, size)) / 2
            for seg, col in ((pre, WHITE), (hot, RED), (post, WHITE)):
                if seg: text(ld, (x, y), seg, size, col, anchor='rm'); x -= tw(ld, seg, size)
        else:
            text(ld, (W / 2, y), ln, size, WHITE, anchor='mm')
    lay.putalpha(lay.getchannel('A').point(lambda v: int(v * a)))
    img.paste(lay, (0, CY + 600), lay)

def golan_frame(t):
    img = Image.new('RGB', (W, H), INK)
    if t < FRZ[0]: ct = t - G1[0]
    elif t < G2[0]: ct = 2.97
    else: ct = 3.0 + (t - G2[0])
    fr = clip_frame(ct)
    frz = FRZ[0] <= t < G2[0]
    z = 1.0 + 0.02 * (t - G1[0]) / 9
    if frz:
        u = t - FRZ[0]; z = 1.0 + 0.16 * ease_out(u / 0.35)
        fr = ImageOps.grayscale(fr).convert('RGB'); fr = Image.blend(fr, Image.new('RGB', fr.size, RED), 0.22 * min(1, u / 0.1))
        fr = ImageEnhance.Contrast(fr).enhance(1.35)
    fr = fr.resize((int(W * z), int(fr.height * z)), Image.BILINEAR).crop(((int(W * z) - W) // 2, 0, (int(W * z) - W) // 2 + W, int(593 * z)))
    img.paste(fr.crop((0, 0, W, min(fr.height, 640))), (0, CY - (fr.height - 593) // 2))
    d = ImageDraw.Draw(img)
    text(d, (W - 60, CY - 50), 'יאיר גולן · חוג בית', 52, PALE, anchor='rm', bold=False)
    d.rectangle((W - 46, CY - 74, W - 38, CY - 26), fill=RED)
    if frz:
        u = t - FRZ[0]
        slam(img, 'חלוקת הארץ', 210, CY + 300, 0.0 + FRZ[0], t, WHITE, block=RED)
        slam(img, '״הדרך היחידה״', 120, CY + 700, 0.35 + FRZ[0], t, WHITE)
    else:
        ct2 = ct
        for a0, a1, l1, l2 in LINES:
            if a0 <= ct2 < a1: caption(img, l1, l2, ct2 - a0, hot='חלוקת הארץ')
    img = vignette(img)
    if frz:
        dx, dy = shake(t, [FRZ[0]]); img = ImageChops.offset(img, dx, dy); img = glitch(img, 14 * math.exp(-(t - FRZ[0]) * 10))
    img.paste(LOGO_S, ((W - LOGO_S.width) // 2, 70), LOGO_S)
    return img

# ---------- map ----------
LON0, LAT0, S = 34.20, 33.35, 0.56 * 1400 / 1400      # screen projection (px per map px folded in below)
def scr(lon, lat):
    x, y = geo(lon, lat); return (x * 0.36 + 150, y * 0.36 + 10)
WB = [(35.15, 32.52), (35.30, 32.56), (35.55, 32.39), (35.53, 32.20), (35.52, 32.00), (35.55, 31.85), (35.52, 31.75), (35.47, 31.50),
      (35.40, 31.35), (35.10, 31.36), (34.88, 31.40), (34.95, 31.60), (35.05, 31.72), (35.12, 31.80), (34.98, 31.85),
      (34.97, 32.10), (35.00, 32.30), (35.05, 32.45)]
def poly_img(pts, fill, outline=None, w=0):
    m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).polygon([scr(*p) for p in pts], fill=255); return m
LAND = poly_img(OUTLINE, 1); WBM = poly_img(WB, 1)
REST = ImageChops.subtract(LAND, WBM)
def build_layers():
    base = Image.new('RGB', (W, H), INK); d = ImageDraw.Draw(base)
    for y in range(0, H, 40):
        for x in range(0, W, 40): d.ellipse((x - 1.5, y - 1.5, x + 1.5, y + 1.5), fill=(0x1A, 0x22, 0x24))
    land = Image.new('RGB', (W, H), (0x26, 0x33, 0x36)); ld = ImageDraw.Draw(land)
    for y in range(0, H, 14): ld.line([(0, y), (W, y)], fill=(0x2E, 0x3D, 0x40), width=2)
    piece = Image.new('RGB', (W, H), (0x3A, 0x2A, 0x2C)); pd = ImageDraw.Draw(piece)
    for y in range(0, H, 14): pd.line([(0, y), (W, y)], fill=(0x48, 0x30, 0x32), width=2)
    teal = Image.new('RGB', (W, H), (0x3A, 0x70, 0x75)); td = ImageDraw.Draw(teal)
    for y in range(0, H, 14): td.line([(0, y), (W, y)], fill=(0x46, 0x80, 0x85), width=2)
    return base, land, piece, teal
BASE, LANDTX, PIECETX, TEALTX = build_layers()
PIECE_RGBA = PIECETX.copy(); PIECE_RGBA.putalpha(WBM)
TEAL_PIECE = TEALTX.copy(); TEAL_PIECE.putalpha(WBM)
JLM = scr(35.21, 31.78); KS = scr(34.91, 32.18)
STK = Image.open(HERE + '/abbas_sticker.png').convert('RGBA'); STK = STK.resize((300, int(300 * STK.height / STK.width)), Image.LANCZOS)
PC = scr(35.27, 32.17)     # sticker spot on the torn piece

def crack_line(u):
    """Jagged red crack along the western edge of the torn piece, drawn progressively."""
    west = [scr(*p) for p in [WB[0]] + WB[:9:-1] + [WB[9]]]      # the western (green line) edge, north to south
    pts = []
    for i in range(len(west) - 1):
        a, b = west[i], west[i + 1]
        for k in range(6):
            f = k / 6; j = 7 * math.sin(i * 7.1 + k * 3.3)
            pts.append((a[0] + (b[0] - a[0]) * f + j, a[1] + (b[1] - a[1]) * f))
    pts.append(west[-1]); n = max(2, int(len(pts) * min(1, u)))
    return pts[:n]

def map_frame(t, teal=False, heal=0.0):
    u = t - MAP[0]
    img = BASE.copy()
    sep = 0 if teal else ease_out((u - 0.9) / 0.6) * 46        # the piece drifts east, the land splits
    sep *= (1 - heal)
    img.paste(TEALTX if teal else LANDTX, (0, 0), REST)
    lay = TEAL_PIECE if teal else PIECE_RGBA
    rot = lay.rotate(-3 * sep / 46, center=PC, resample=Image.BICUBIC) if sep else lay
    img.paste(rot, (int(sep), int(sep * .15)), rot)
    d = ImageDraw.Draw(img)
    d.line([scr(*p) for p in OUTLINE] + [scr(*OUTLINE[0])], fill=TEAL_L if teal else (0x55, 0x66, 0x6A), width=3)
    if not teal:
        cl = crack_line(u / 0.8)
        if len(cl) > 1:
            gl = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(gl).line(cl, fill=RED + (200,), width=18)
            img.paste(gl.filter(ImageFilter.GaussianBlur(10)), (0, 0), gl.filter(ImageFilter.GaussianBlur(10)))
            d = ImageDraw.Draw(img); d.line(cl, fill=RED, width=6)
    # pins
    for (lbl, p, t0) in (('ירושלים', JLM, 3.2), ('כפר סבא', KS, 4.0)):
        on = not teal and u >= t0
        r = 12 + (10 * abs(math.sin((u - t0) * 6)) if on else 0)
        d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=RED if on else (0x80, 0x88, 0x8A))
    return img

def map_scene(t):
    u = t - MAP[0]; img = map_frame(t)
    # sticker slaps onto the torn piece
    su = (u - 1.7) / 0.18
    if su > 0:
        sc = 1.9 - 0.9 * ease_out(su); s2 = STK.resize((int(STK.width * sc), int(STK.height * sc)), Image.BILINEAR)
        img.paste(s2, (int(PC[0] + 46 - s2.width / 2), int(PC[1] - s2.height / 2)), s2)
    img = vignette(img)
    slam(img, 'חלוקת הארץ', 120, 300, MAP[0] + 1.9, t, PALE)
    slam(img, '= מדינה לאבו מאזן.', 150, 450, MAP[0] + 2.2, t, WHITE, block=RED)
    for k, (q, t0) in enumerate((('ירושלים?', 3.2), ('כפר סבא?', 4.0), ('הבית שלך?', 4.8))):
        if u >= t0: slam(img, q, 170, 1560 + 0, MAP[0] + t0, t, WHITE if k < 2 else RED, block=None if k < 2 else None) if (u < t0 + 0.8 or k == 2) else None
    dx, dy = shake(t, [MAP[0] + 0.0, MAP[0] + 1.7, MAP[0] + 2.2, MAP[0] + 3.2, MAP[0] + 4.0, MAP[0] + 4.8], 16)
    img = ImageChops.offset(img, dx, dy)
    for h in (MAP[0] + 1.7, MAP[0] + 4.8):
        if 0 <= t - h < .3: img = glitch(img, 16 * math.exp(-(t - h) * 9))
    img.paste(LOGO_S, ((W - LOGO_S.width) // 2, 70), LOGO_S)
    return img

def turn_scene(t):
    u = t - TURN[0]; heal = ease_out(u / 0.9)
    img = map_frame(MAP[0] + 6.0, teal=heal > 0.5, heal=heal)
    if heal <= 0.5: img = Image.blend(img, map_frame(MAP[0] + 6.0, teal=True), heal * 2)
    # sticker rips off and flies away
    fu = u / 0.5
    if fu < 1:
        s2 = STK.rotate(-50 * fu, expand=True, resample=Image.BICUBIC)
        img.paste(s2, (int(PC[0] + 46 - s2.width / 2 + 900 * fu ** 2), int(PC[1] - s2.height / 2 - 700 * fu ** 2)), s2)
    img.paste(LOGO_S, ((W - LOGO_S.width) // 2, 70), LOGO_S)
    return img

CLOSE_BG = Image.new('RGB', (W, H)); _c = ImageDraw.Draw(CLOSE_BG)
for y in range(H): _c.line([(0, y), (W, y)], fill=tuple(int(DEEP[k] + (TEAL_D[k] - DEEP[k]) * y / H) for k in range(3)))
LOGO_E = logo_img(560)
def close_scene(t):
    u = t - CLOSE[0]; img = CLOSE_BG.copy()
    slam(img, 'רק ציונות דתית חזקה', 140, 430, CLOSE[0] + 0.1, t)
    slam(img, 'תעצור את זה.', 160, 610, CLOSE[0] + 0.5, t)
    slam(img, 'כן. סמוטריץ׳.', 190, 860, CLOSE[0] + 1.0, t, WHITE, block=TEAL)
    bu = ease_out((u - 1.5) / 0.25)
    if bu > 0:
        sc = 1.6 - 0.6 * bu; b = BALLOT_BIG.resize((int(BALLOT_BIG.width * sc), int(BALLOT_BIG.height * sc)), Image.BILINEAR)
        img.paste(b, (int(W / 2 - b.width / 2), int(1250 - b.height / 2)), b)
    la = ease_out((u - 2.0) / 0.35)
    if la > 0:
        lg = LOGO_E.copy(); lg.putalpha(lg.getchannel('A').point(lambda v: int(v * la))); img.paste(lg, ((W - lg.width) // 2, 1640 - lg.height // 2), lg)
    dx, dy = shake(t, [CLOSE[0] + 1.0, CLOSE[0] + 1.5], 12)
    return ImageChops.offset(img, dx, dy)

def hook_scene(t):
    img = Image.new('RGB', (W, H), INK)
    slam(img, 'חלוקת', 300, 760, 0.45, t)
    slam(img, 'הארץ.', 300, 1040, 0.95, t)
    slam(img, 'הם כבר לא מסתירים את זה.', 110, 1380, 2.0, t, WHITE, block=RED)
    img = vignette(img); dx, dy = shake(t, [2.0]); img = ImageChops.offset(img, dx, dy)
    if 2.0 <= t < 2.35: img = glitch(img, 18 * math.exp(-(t - 2.0) * 9))
    if t > HOOK - 0.08: img = Image.blend(img, Image.new('RGB', (W, H), WHITE), (t - (HOOK - 0.08)) / 0.08 * .6)
    return img

def frame(t):
    if t < HOOK: return hook_scene(t)
    if t < MAP[0]: return golan_frame(t)
    if t < HUSH[0]: return map_scene(t)
    if t < TURN[0]: return Image.new('RGB', (W, H), BLACK)
    if t < CLOSE[0]: return turn_scene(t)
    return close_scene(t)

def render(out):
    prep_clip()
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-vf', 'noise=alls=8:allf=t', '-c:v', 'libx264', '-preset', 'medium', '-crf', '21', '-maxrate', '12M', '-bufsize', '24M', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for i in range(int(round(TOTAL * FPS))):
        ff.stdin.write(frame(i / FPS).convert('RGB').tobytes())
    ff.stdin.close(); ff.wait()

def mix(out_wav):
    X = lambda n: SFX + n + '.wav'
    c = []   # (file, at, vol, trim0, dur, extra)
    c.append((HERE + '/drone.wav', 0, .55, 0, HUSH[0], ''))
    for k in range(6): c.append((X('tick'), 0.45 + k * 0.5 - (0 if k < 2 else 0), .8 if k < 2 else .5, 0, 0, ''))
    c += [(X('impact'), 2.0, .8, 0, 0, ''), (X('bass_drop'), 2.0, .6, 0, 0, '')]
    c.append((SRC, G1[0], 1.0, 0.0, 3.0, ''))
    c += [(X('impact'), FRZ[0], .9, 0, 0, ''), (SRC, FRZ[0], .45, 2.2, 0.8, ',aecho=0.8:0.7:220|440:0.5|0.3')]
    c.append((SRC, G2[0], 1.0, 3.0, 4.8, ''))
    for k in range(6): c.append((HERE + '/heart.wav', MAP[0] + k * (0.95 - k * .06), .9, 0, 0, ''))
    c += [(X('impact'), MAP[0], .6, 0, 0, ''), (X('whoosh'), MAP[0] + 0.85, .5, 0, 0, ''), (X('hit_soft'), MAP[0] + 1.7, .9, 0, 0, ''),
          (X('pop'), MAP[0] + 1.72, .5, 0, 0, ''), (X('impact'), MAP[0] + 2.2, .7, 0, 0, ''),
          (X('hit_soft'), MAP[0] + 3.2, .8, 0, 0, ''), (X('hit_soft'), MAP[0] + 4.0, .8, 0, 0, ''), (X('impact'), MAP[0] + 4.8, .9, 0, 0, ''),
          (X('riser'), MAP[0] + 4.9, .4, 0, 0, '')]
    c += [(X('whoosh'), TURN[0], .6, 0, 0, ''), (X('swoosh_soft'), TURN[0] + .1, .5, 0, 0, ''), (X('chime_up'), TURN[0] + 0.6, .45, 0, 0, '')]
    c += [(X('hit_soft'), CLOSE[0] + .1, .8, 0, 0, ''), (X('hit_soft'), CLOSE[0] + .5, .8, 0, 0, ''), (X('impact'), CLOSE[0] + 1.0, .7, 0, 0, ''),
          (X('pop'), CLOSE[0] + 1.5, .6, 0, 0, ''), (X('chime_up'), CLOSE[0] + 2.0, .4, 0, 0, ''), (X('tick'), TOTAL - 0.55, .9, 0, 0, '')]
    args = ['ffmpeg', '-v', 'error', '-y']; fl = []
    for j, (f, at, vol, s0, dur, ex) in enumerate(c):
        args += ['-i', f]
        tr = f',atrim={s0}:{s0 + dur},asetpts=PTS-STARTPTS' if dur else ''
        if f == SRC: tr += ',highpass=f=90,loudnorm=I=-16:TP=-2,afade=t=in:d=0.03,afade=t=out:st=%.2f:d=0.08' % (dur - 0.08)
        if f.endswith('drone.wav'): tr += f',afade=t=in:d=0.6,afade=t=out:st={dur - 0.05}:d=0.05'
        fl.append(f'[{j}:a]aformat=sample_rates=48000:channel_layouts=stereo{tr}{ex},volume={vol},adelay={int(at * 1000)}|{int(at * 1000)}[a{j}]')
    fl.append(''.join(f'[a{j}]' for j in range(len(c))) + f'amix=inputs={len(c)}:normalize=0,atrim=0:{TOTAL:.3f},apad=whole_dur={TOTAL:.3f}[out]')
    subprocess.run(args + ['-filter_complex', ';'.join(fl), '-map', '[out]', out_wav], check=True)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'stills':
        prep_clip(); ts = [2.6, G1[0] + 1.2, FRZ[0] + .9, G2[0] + 3.5, MAP[0] + 2.8, MAP[0] + 5.2, TURN[0] + 1.2, CLOSE[0] + 3.5]
        im = [frame(x).convert('RGB') for x in ts]; sh = Image.new('RGB', (len(im) * 250, 440), WHITE)
        for k, x in enumerate(im): sh.paste(x.resize((240, 427)), (k * 250, 0))
        sh.save(HERE + '/stills.jpg'); print('stills', TOTAL)
    else:
        render(P + 'v.mp4'); mix(P + 'a.wav')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', P + 'v.mp4', '-i', P + 'a.wav', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', P + 'mux.mp4'], check=True)
        subprocess.run(['python3', SKILL + '/scripts/loudnorm.py', P + 'mux.mp4', HERE + '/rz-golan-partition.mp4', '--target', '-14'], check=True)
        print('done', TOTAL)
