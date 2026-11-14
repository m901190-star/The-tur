"""Religious Zionism story #2, map version: a plough line runs across a map of Israel, city by city (1080x1920, 30fps, no music)."""
import os, sys, math, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_video import *          # brand colours, fonts, easing, logo, ballot, pop_line, GRAD
from PIL import Image, ImageDraw, ImageFilter

# ---------- map ----------
LON0, LAT0, K, CL = 34.10, 33.45, 1400, math.cos(math.radians(31.5))
def geo(lon, lat): return ((lon - LON0) * K * CL, (LAT0 - lat) * K)
OUTLINE = [(35.105, 33.093), (35.20, 33.08), (35.33, 33.07), (35.50, 33.12), (35.57, 33.27), (35.63, 33.26), (35.80, 33.33), (35.87, 33.29),
           (35.93, 33.15), (35.89, 32.95), (35.84, 32.82), (35.78, 32.72), (35.60, 32.70), (35.57, 32.60), (35.55, 32.40), (35.53, 32.20),
           (35.52, 32.00), (35.55, 31.85), (35.52, 31.75), (35.52, 31.50), (35.45, 31.15), (35.40, 30.95), (35.30, 30.70), (35.15, 30.40),
           (35.05, 30.10), (34.97, 29.55), (34.90, 29.49), (34.88, 29.55), (34.75, 30.00), (34.55, 30.40), (34.40, 30.80), (34.27, 31.22),
           (34.38, 31.33), (34.50, 31.48), (34.57, 31.56), (34.52, 31.60), (34.54, 31.67), (34.64, 31.80), (34.75, 32.08), (34.84, 32.33),
           (34.88, 32.47), (34.95, 32.82), (34.99, 32.83), (35.07, 32.92), (35.09, 33.01)]
KINNERET = [(35.52, 32.88), (35.58, 32.90), (35.64, 32.84), (35.63, 32.73), (35.57, 32.71), (35.52, 32.78)]
GEO = {'קצרין': (35.69, 32.99), 'נתניה': (34.86, 32.33), 'פתח תקווה': (34.89, 32.09), 'תל אביב': (34.78, 32.08), 'בת ים': (34.75, 32.02),
       'ירושלים': (35.21, 31.78), 'מעלה אדומים': (35.30, 31.78), 'אשקלון': (34.57, 31.67)}
PTS = [geo(*GEO[c]) for c, _ in CITIES]
MW, MH = int(1.95 * K * CL), int(4.05 * K)

def build_map():
    m = Image.new('RGB', (MW, MH), DEEP); d = ImageDraw.Draw(m)
    for y in range(0, MH, 46):                       # faint dot grid, like a field
        for x in range(0, MW, 46): d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(0x22, 0x40, 0x44))
    poly = [geo(*p) for p in OUTLINE]
    glow = Image.new('L', (MW, MH), 0); ImageDraw.Draw(glow).polygon(poly, fill=255)
    glow = glow.filter(ImageFilter.GaussianBlur(40))
    m.paste(Image.new('RGB', (MW, MH), TEAL), (0, 0), glow.point(lambda v: int(v * .35)))
    d = ImageDraw.Draw(m); d.polygon(poly, fill=(0x3A, 0x70, 0x75), outline=TEAL_L); d.line(poly + [poly[0]], fill=TEAL_L, width=6, joint='curve')
    for y in range(0, MH, 30):                        # furrows: the land is ploughed
        d.line([(0, y), (MW, y)], fill=(0x46, 0x80, 0x85), width=3)
    mask = Image.new('L', (MW, MH), 0); ImageDraw.Draw(mask).polygon(poly, fill=255)
    base = Image.new('RGB', (MW, MH), DEEP); bd = ImageDraw.Draw(base)
    for y in range(0, MH, 46):
        for x in range(0, MW, 46): bd.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(0x22, 0x40, 0x44))
    base.paste(Image.new('RGB', (MW, MH), TEAL), (0, 0), glow.point(lambda v: int(v * .35)))
    base.paste(m, (0, 0), mask)
    bd = ImageDraw.Draw(base); bd.line(poly + [poly[0]], fill=TEAL_L, width=6, joint='curve')
    bd.polygon([geo(*p) for p in KINNERET], fill=DEEP)
    return base
MAP = build_map()
BGTILE = Image.new('RGB', (W, H), DEEP)

# camera: (cx, cy) map point shown at screen (SX, SY), s = screen px per map px
SX, SY = W / 2, 1290
OVER = (MW / 2 + 40, MH / 2 - 420, 0.34)
def cam_city(i):
    s = 1.0 if CITIES[i][0] in ('פתח תקווה', 'תל אביב', 'בת ים') else 0.62
    return (PTS[i][0], PTS[i][1], s)
def lerp_cam(a, b, u):
    u = ease_out(u) if u < 1 else 1
    ls = math.log(a[2]) + (math.log(b[2]) - math.log(a[2])) * u          # zoom in log space
    return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u, math.exp(ls))
def to_screen(cam, p): return (SX + (p[0] - cam[0]) * cam[2], SY + (p[1] - cam[1]) * cam[2])

def map_view(cam, sy=SY):
    cx, cy, s = cam
    x0, y0 = cx - SX / s, cy - sy / s; x1, y1 = x0 + W / s, y0 + H / s
    bx0, by0, bx1, by1 = max(0, x0), max(0, y0), min(MW, x1), min(MH, y1)       # clip to the map, rest is plain background
    out = BGTILE.copy()
    if bx1 > bx0 and by1 > by0:
        ow, oh = max(1, round((bx1 - bx0) * s)), max(1, round((by1 - by0) * s))
        out.paste(MAP.resize((ow, oh), Image.BILINEAR, box=(bx0, by0, bx1, by1)), (round((bx0 - x0) * s), round((by0 - y0) * s)))
    return out

def draw_path(d, cam, upto, frac):
    """Plough line through the cities visited so far; the last leg grows with frac."""
    pts = [to_screen(cam, PTS[i]) for i in range(upto + 1)]
    if upto + 1 < len(PTS) and frac > 0:
        a, b = to_screen(cam, PTS[upto]), to_screen(cam, PTS[upto + 1])
        pts.append((a[0] + (b[0] - a[0]) * frac, a[1] + (b[1] - a[1]) * frac))
    if len(pts) > 1:
        d.line(pts, fill=TEAL, width=22, joint='curve'); d.line(pts, fill=WHITE, width=8, joint='curve')
    return pts[-1]

def draw_pins(d, cam, lit, t, active=-1, pop=1.0):
    for i, p in enumerate(PTS):
        x, y = to_screen(cam, p)
        if -60 < x < W + 60 and -60 < y < H + 60:
            if i == active:
                r = 26 * ease_back(pop); pr = 26 + 30 * ((t * 1.4) % 1)
                d.ellipse((x - pr, y - pr, x + pr, y + pr), outline=TEAL_L, width=4)
                d.ellipse((x - r, y - r, x + r, y + r), fill=WHITE); d.ellipse((x - r * .55, y - r * .55, x + r * .55, y + r * .55), fill=TEAL)
            elif i <= lit: d.ellipse((x - 15, y - 15, x + 15, y + 15), fill=WHITE); d.ellipse((x - 8, y - 8, x + 8, y + 8), fill=TEAL)
            else: d.ellipse((x - 10, y - 10, x + 10, y + 10), fill=PALE)

def big_name(img, name, u, y=1560):
    """City name slams in huge, from the right."""
    a = ease_out(u / 0.25)
    if a <= 0: return
    lay = Image.new('RGBA', (W, 300), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    size = 190 if len(name) < 8 else 160
    tx = tw(ld, name, size); x_r = (W + tx) / 2 + 40
    ld.rectangle((x_r - tx - 90, 40, x_r + 20, 260), fill=TEAL_D + (230,)); ld.rectangle((x_r + 8, 40, x_r + 20, 260), fill=TEAL_L + (255,))
    chevron(ld, x_r - 10, 150, 70)
    text(ld, (x_r - 80, 148), name, size, WHITE, anchor='rm')
    lay.putalpha(lay.getchannel('A').point(lambda v: int(v * a)))
    img.paste(lay, (int(90 * (1 - a)), int(y - 150)), lay)

def small_name(img, name, y=1700):
    lay = Image.new('RGBA', (W, 140), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    size = 88; tx = tw(ld, name, size); x_r = (W + tx + 110) / 2
    ld.rectangle((x_r - tx - 110, 20, x_r, 120), fill=TEAL_D + (235,)); ld.rectangle((x_r - 10, 20, x_r, 120), fill=TEAL_L + (255,))
    chevron(ld, x_r - 26, 70, 44); text(ld, (x_r - 86, 68), name, size, WHITE, anchor='rm')
    img.paste(lay, (0, int(y - 70)), lay)

# ---------- timeline ----------
FLY, ARRIVE, PHOTO = 0.65, 0.55, 0.95
OPEN, INTRO, END = 3.3, 1.2, 4.6
# chant moments picked from the loudness of each clip; ('v', file, start, dur[, (audio_file, audio_start)])
MEDIA = {
    'קצרין': [('p', U + '4108a468-image.jpg'), ('v', M + 'v06-katzrin.mov', 1.0, 2.0)],
    'נתניה': [('p', U + 'caadec50-image.jpg'), ('p', U + 'caf39821-image.jpg')],
    'פתח תקווה': [('v', M + 'v04-petahtikva.mov', 3.5, 2.8, (M + 'v08-petahtikva.mov', 3.9))],
    'תל אביב': [('v', M + 'v01-telaviv.mov', 4.7, 3.4), ('p', U + '9050e4fb-image.jpg')],
    'בת ים': [('v', M + 'v03-batyam.mov', 0.3, 3.4)],
    'ירושלים': [('p', U + '61660d37-image.jpg'), ('p', U + '7e0b1fe1-image.jpg')],
    'מעלה אדומים': [('p', U + 'd08a8e70-image.jpg')],
    'אשקלון': [('v', M + 'v13-ashkelon.mov', 1.6, 2.3), ('p', U + 'ea9a61af-image.jpg'), ('p', U + '78e5bd5b-image.jpg'),
               ('p', U + '6ea7f215-image.jpg'), ('p', U + 'c98b45b3-image.jpg')]}
OPENING = (M + 'v08-petahtikva.mov', 1.0)
SEG = []      # (kind, t0, dur, data)
t = 0
SEG.append(('open', t, OPEN, None)); t += OPEN
SEG.append(('intro', t, INTRO, None)); t += INTRO
for ci, (city, _) in enumerate(CITIES):
    SEG.append(('fly', t, FLY, ci)); t += FLY
    SEG.append(('arrive', t, ARRIVE, ci)); t += ARRIVE
    pk = 0
    for it in MEDIA[city]:
        d = PHOTO if it[0] == 'p' else it[3]
        SEG.append(('media', t, d, (ci, it, pk))); t += d
        if it[0] == 'p': pk += 1
SEG.append(('end', t, END, None)); t += END
TOTAL2 = t

# ---------- media ----------
class Media:
    def __init__(self, it, key):
        self.it = it; self.video = it[0] == 'v'
        if self.video:
            self.dir = P + f'm_{key}/'; os.makedirs(self.dir, exist_ok=True)
            probe = subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', it[1]]).decode().split(',')
            self.vertical = int(probe[1]) > int(probe[0])
            vf = f'fps={FPS},scale={W}:-2:flags=lanczos,crop={W}:{H},unsharp=5:5:0.6' if self.vertical else f'fps={FPS},unsharp=5:5:0.5'
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(it[2]), '-t', str(it[3] + 0.2), '-i', it[1], '-vf', vf, self.dir + '%04d.png'], check=True)
            self.frames = sorted(os.listdir(self.dir))
        else:
            self.vertical = False; self.photo = Image.open(it[1]).convert('RGB')
    def frame(self, t):
        return Image.open(self.dir + self.frames[min(len(self.frames) - 1, int(t * FPS))]).convert('RGB')

def polaroid(im, maxw=800, maxh=900, rot=0):
    s = min(maxw / im.width, maxh / im.height); im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    b, bb = 20, 20
    card = Image.new('RGBA', (im.width + 2 * b + 60, im.height + b + bb + 60), (0, 0, 0, 0))
    sh = Image.new('RGBA', card.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rectangle((38, 44, 30 + im.width + 2 * b, 34 + im.height + b + bb), fill=(0, 0, 0, 150))
    card.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    ImageDraw.Draw(card).rectangle((30, 30, 30 + im.width + 2 * b, 30 + im.height + b + bb), fill=MIST)
    card.paste(im, (30 + b, 30 + b))
    return card.rotate(rot, resample=Image.BICUBIC, expand=True)
TILT = [-5, 4, -3, 6, -6]

def iris(full, under, center, r):
    m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).ellipse((center[0] - r, center[1] - r, center[0] + r, center[1] + r), fill=255)
    under.paste(full, (0, 0), m); return under

# ---------- frames ----------
OPEN_FR = P + 'open2/'
def prep_open():
    os.makedirs(OPEN_FR, exist_ok=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(OPENING[1]), '-t', str(OPEN + .1), '-i', OPENING[0],
                    '-vf', f'fps={FPS},scale={W}:-2:flags=lanczos,crop={W}:{H},unsharp=5:5:0.6', OPEN_FR + '%04d.png'], check=True)

def slam(img, s, size, y, t0, t, color, block=None):
    """Bigger, harder entrance than Friday's pop: drops from 1.6x scale."""
    u = (t - t0) / 0.18
    if u <= 0: return
    a = ease_out(u); sc = 1.6 - 0.6 * ease_out(u)
    lay = Image.new('RGBA', (W, int(size * 1.6)), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    if block:
        tx = tw(ld, s, size); ld.rectangle(((W - tx) / 2 - 34, size * 0.12, (W + tx) / 2 + 34, size * 1.28), fill=block + (255,))
    text(ld, (W / 2, size * 0.7), s, size, color, anchor='mm')
    lay = lay.resize((int(W * sc), int(lay.height * sc)), Image.BILINEAR)
    lay.putalpha(lay.getchannel('A').point(lambda v: int(v * a)))
    img.paste(lay, ((W - lay.width) // 2, int(y - lay.height / 2)), lay)

def frame_at(t, media):
    k = max(j for j, s in enumerate(SEG) if s[1] <= t + 1e-6); kind, t0, dur, data = SEG[k]; u = t - t0
    if kind == 'open':
        fs = sorted(os.listdir(OPEN_FR)); img = Image.open(OPEN_FR + fs[min(int(u * FPS), len(fs) - 1)]).convert('RGB')
        img.paste(GRAD, (0, 0), GRAD)
        slam(img, 'יוצאים', 230, 1110, 0.25, u, WHITE)
        slam(img, 'לחרוש את הארץ', 170, 1330, 0.7, u, WHITE, block=TEAL)
        if u > OPEN - 0.25:                 # iris closes into a point: the first pin
            r = max(1, int(1400 * (1 - ease_out((u - (OPEN - 0.25)) / 0.25))))
            img = iris(img, map_view(OVER), (SX, SY), r)
        return img
    if kind == 'intro':
        cam = lerp_cam(OVER, (OVER[0], OVER[1], OVER[2] * 1.05), u / dur); img = map_view(cam); d = ImageDraw.Draw(img)
        draw_pins(d, cam, -1, t)
        a = ease_out(u / 0.3); col = tuple(int(v * a + DEEP[i] * (1 - a)) for i, v in enumerate(WHITE))
        text(d, (W / 2, 1700), 'מקצרין ועד אשקלון', 96, col, anchor='mm')
        return img
    if kind == 'end':
        cam = lerp_cam(cam_city(len(CITIES) - 1), OVER, u / 1.0); img = map_view(cam); d = ImageDraw.Draw(img)
        draw_path(d, cam, len(CITIES) - 1, 0); draw_pins(d, cam, len(CITIES) - 1, t)
        if u > 0.9:
            ov = Image.new('RGBA', (W, H), DEEP + (int(170 * ease_out((u - 0.9) / 0.4)),)); img.paste(ov, (0, 0), ov)
            slam(img, 'בכל הארץ', 210, 560, 1.0, u, WHITE)
            slam(img, 'כן. סמוטריץ׳.', 180, 800, 1.45, u, WHITE, block=TEAL)
            la = ease_out((u - 2.0) / 0.4)
            if la > 0:
                lg = LOGO_END.copy(); lg.putalpha(lg.getchannel('A').point(lambda v: int(v * la)))
                img.paste(lg, ((W - lg.width) // 2, 1180 - lg.height // 2 + int(30 * (1 - la))), lg)
        return img
    ci = data if kind != 'media' else data[0]
    city = CITIES[ci][0]
    if kind == 'fly':
        a = cam_city(ci - 1) if ci > 0 else OVER
        cam = lerp_cam(a, cam_city(ci), u / dur); img = map_view(cam); d = ImageDraw.Draw(img)
        if ci > 0: draw_path(d, cam, ci - 1, ease_out(u / dur))
        draw_pins(d, cam, ci - 1, t)
        return img
    cam = cam_city(ci); img = map_view(cam); d = ImageDraw.Draw(img)
    draw_path(d, cam, ci, 0)
    if kind == 'arrive':
        draw_pins(d, cam, ci - 1, t, active=ci, pop=u / 0.3)
        big_name(img, city, u)
        return img
    _, it, pk = data; mm = media[(t0, city)]
    draw_pins(d, cam, ci - 1, t, active=ci)
    pin = to_screen(cam, PTS[ci])
    if mm.video and mm.vertical:              # full bleed, opened from the pin like an iris
        full = mm.frame(u); r = int(2300 * ease_out(u / 0.28))
        img = iris(full, img, pin, max(1, r)) if r < 2250 else full
        if u > dur - 0.18: img = iris(full, map_view(cam), pin, int(2300 * (1 - ease_out((u - (dur - 0.18)) / 0.18))) + 1)
        small_name(img, city)
        return img
    # photos (and landscape clips) drop onto the map as polaroids, stacking per city
    prev = [s for s in SEG if s[0] == 'media' and s[3][0] == ci and s[1] < t0 and s[3][1][0] == 'p']
    for s in prev[-2:]:
        pm = media[(s[1], city)]; pc = pm.pol
        img.paste(pc, (int(W / 2 - pc.width / 2 + 20 * TILT[s[3][2] % 5]), int(760 - pc.height / 2)), pc)
    if mm.video:
        pc = polaroid(mm.frame(u), 980, 700, TILT[pk % 5] * .5)
    else:
        pc = mm.pol
    a = ease_out(u / 0.22); sc = 1.25 - 0.25 * ease_back(u / 0.3)
    pc2 = pc.resize((int(pc.width * sc), int(pc.height * sc)), Image.BILINEAR) if sc != 1 else pc
    if a < 1: pc2 = pc2.copy(); pc2.putalpha(pc2.getchannel('A').point(lambda v: int(v * a)))
    cx, cy = W / 2, 760
    ImageDraw.Draw(img).line([pin, (cx, cy + pc.height / 2 - 60)], fill=PALE, width=3)
    img.paste(pc2, (int(cx - pc2.width / 2), int(cy - pc2.height / 2)), pc2)
    small_name(img, city)
    return img

def render2(out):
    prep_open(); media = {}
    for kind, t0, dur, data in SEG:
        if kind == 'media':
            ci, it, pk = data; m = Media(it, f'{int(t0 * 100)}'); media[(t0, CITIES[ci][0])] = m
            if not m.video: m.pol = polaroid(m.photo, 800, 880, TILT[pk % 5])
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for i in range(int(round(TOTAL2 * FPS))):
        img = frame_at(i / FPS, media)
        img.paste(LOGO_TOP, ((W - LOGO_TOP.width) // 2, 150), LOGO_TOP)
        ff.stdin.write(add_ballot(img.convert('RGB')).tobytes())
    ff.stdin.close(); ff.wait()
    return media

def mix2(out_wav):
    S_ = lambda n: SFX + n + '.wav'
    cues = [(OPENING[0], 0.0, 1.0, OPENING[1], OPEN), (S_('hit_soft'), 0.25, 0.7, 0, 0), (S_('whoosh'), 0.62, 0.4, 0, 0), (S_('hit_soft'), 0.7, 0.6, 0, 0),
            (S_('swoosh_soft'), OPEN - 0.3, 0.5, 0, 0), (S_('blip'), OPEN + 0.2, 0.3, 0, 0)]
    for kind, t0, dur, data in SEG:
        if kind == 'fly': cues += [(S_('whoosh'), t0, 0.45, 0, 0)]
        if kind == 'arrive': cues += [(S_('pop'), t0, 0.5, 0, 0), (S_('impact'), t0 + 0.02, 0.3, 0, 0)]
        if kind == 'media':
            ci, it, pk = data
            if it[0] == 'p': cues += [(S_('click'), t0 + 0.12, 0.5, 0, 0), (S_('swoosh_soft'), t0, 0.3, 0, 0)]
            else:
                f, s0 = it[4] if len(it) > 4 else (it[1], it[2])
                cues += [(S_('swoosh_soft'), t0, 0.35, 0, 0), (f, t0, 1.0, s0, dur)]
        if kind == 'end': cues += [(S_('whoosh'), t0, 0.4, 0, 0), (S_('riser'), t0 - 0.2, 0.3, 0, 0), (S_('hit_soft'), t0 + 1.0, 0.85, 0, 0),
                                   (S_('hit_soft'), t0 + 1.45, 0.85, 0, 0), (S_('chime_up'), t0 + 2.0, 0.4, 0, 0)]
    args = ['ffmpeg', '-v', 'error', '-y']; fl = []
    for j, (f, at, vol, s0, dur) in enumerate(cues):
        args += ['-i', f]
        ex = f',atrim={s0}:{s0 + dur},asetpts=PTS-STARTPTS,loudnorm=I=-17:TP=-3,afade=t=in:d=0.06,afade=t=out:st={dur - 0.15}:d=0.15' if dur else ''
        fl.append(f'[{j}:a]aformat=sample_rates=48000:channel_layouts=stereo{ex},volume={vol},adelay={int(max(0, at) * 1000)}|{int(max(0, at) * 1000)}[a{j}]')
    fl.append(''.join(f'[a{j}]' for j in range(len(cues))) + f'amix=inputs={len(cues)}:normalize=0,atrim=0:{TOTAL2:.3f},apad=whole_dur={TOTAL2:.3f}[out]')
    subprocess.run(args + ['-filter_complex', ';'.join(fl), '-map', '[out]', out_wav], check=True)

if __name__ == '__main__':
    os.makedirs(P, exist_ok=True)
    if len(sys.argv) > 1 and sys.argv[1] == 'stills':
        prep_open(); media = {}
        for kind, t0, dur, data in SEG:
            if kind == 'media':
                ci, it, pk = data; m = Media(it, f'{int(t0 * 100)}'); media[(t0, CITIES[ci][0])] = m
                if not m.video: m.pol = polaroid(m.photo, 800, 880, TILT[pk % 5])
        ts = [1.5, OPEN + 0.6] + [s[1] + s[2] * .7 for s in SEG if s[0] in ('fly', 'arrive')][2:6] + [s[1] + 0.6 for s in SEG if s[0] == 'media'][:9] + [TOTAL2 - 0.5]
        shots = []
        for tt in ts:
            im = frame_at(tt, media); im.paste(LOGO_TOP, ((W - LOGO_TOP.width) // 2, 150), LOGO_TOP); shots.append(add_ballot(im.convert('RGB')))
        sheet = Image.new('RGB', (8 * 250, 2 * 450), WHITE)
        for j, s in enumerate(shots[:16]): sheet.paste(s.resize((240, 427)), ((j % 8) * 250, (j // 8) * 450))
        sheet.save(HERE + '/stills2.jpg'); print('stills', round(TOTAL2, 2))
    else:
        render2(P + 'video2.mp4'); mix2(P + 'audio2.wav')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', P + 'video2.mp4', '-i', P + 'audio2.wav', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', P + 'mux2.mp4'], check=True)
        subprocess.run(['python3', SKILL + '/scripts/loudnorm.py', P + 'mux2.mp4', HERE + '/rz-story-map.mp4', '--target', '-14'], check=True)
        print('done', round(TOTAL2, 2))
