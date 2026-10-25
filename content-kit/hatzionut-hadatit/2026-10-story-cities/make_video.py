"""Religious Zionism story video #2: activists across the country, city by city (1080x1920, 30fps, no music)."""
import os, subprocess, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/pro-video-editing'
FONT_B = SKILL + '/assets/fonts/Karantina-Bold.ttf'
FONT_R = SKILL + '/assets/fonts/Karantina-Regular.ttf'
SFX = SKILL + '/assets/sfx/'
LOGO = '/root/.claude/uploads/1a5819ee-0cc0-5045-b086-4a8a80216453/5fd07075-image.png'   # original, untouched
M, P = HERE + '/media/', HERE + '/prep/'

W, H, FPS = 1080, 1920, 30
DEEP = (0x1B, 0x33, 0x36); TEAL_D = (0x2B, 0x51, 0x55); TEAL = (0x50, 0x92, 0x99)
TEAL_L = (0x69, 0xB4, 0xBD); PALE = (0xAD, 0xD5, 0xD9); MIST = (0xEA, 0xF2, 0xF3); WHITE = (255, 255, 255)

U = '/root/.claude/uploads/1a5819ee-0cc0-5045-b086-4a8a80216453/'
OPEN_T, PHOTO_T, END_T = 3.5, 1.0, 4.2
# north to south. ('v', file, start, dur, audio_from) — audio_from overrides the clip's own sound
CITIES = [
    ('קצרין', [('p', U + '4108a468-image.jpg'), ('v', M + 'v06-katzrin.mov', 0.6, 2.6)]),
    ('נתניה', [('p', U + 'caadec50-image.jpg'), ('p', U + 'caf39821-image.jpg')]),
    # clip 4's own sound is not used (it may name the yeshiva); the Petah Tikva bus chant from clip 8 plays under it
    ('פתח תקווה', [('v', M + 'v04-petahtikva.mov', 1.0, 3.0, (M + 'v08-petahtikva.mov', 3.5))]),
    ('תל אביב', [('v', M + 'v01-telaviv.mov', 0.2, 3.6), ('p', U + '9050e4fb-image.jpg')]),
    ('בת ים', [('v', M + 'v03-batyam.mov', 0.6, 3.6)]),
    ('ירושלים', [('p', U + '61660d37-image.jpg'), ('p', U + '7e0b1fe1-image.jpg')]),
    ('מעלה אדומים', [('p', U + 'd08a8e70-image.jpg')]),
    ('אשקלון', [('v', M + 'v13-ashkelon.mov', 0.0, 3.6), ('p', U + 'ea9a61af-image.jpg'), ('p', U + '78e5bd5b-image.jpg'),
                ('p', U + '6ea7f215-image.jpg'), ('p', U + 'c98b45b3-image.jpg')]),
]
OPEN_CLIP = (M + 'v08-petahtikva.mov', 0.0)
ITEMS = []          # (city_index, item, start, dur, first_in_city)
_t = OPEN_T
for ci, (city, items) in enumerate(CITIES):
    for k, it in enumerate(items):
        d = PHOTO_T if it[0] == 'p' else it[3]
        ITEMS.append((ci, it, _t, d, k == 0)); _t += d
END_START = _t
TOTAL = END_START + END_T
_fonts = {}
def F(size, bold=True):
    k = (int(size), bold)
    if k not in _fonts:
        _fonts[k] = ImageFont.truetype(FONT_B if bold else FONT_R, int(size))
    return _fonts[k]


def text(d, xy, s, size, fill, anchor='ra', bold=True, rtl=True):
    d.text(xy, s, font=F(size, bold), fill=fill, anchor=anchor, direction='rtl' if rtl else 'ltr')


def tw(d, s, size, bold=True):
    return d.textlength(s, font=F(size, bold), direction='rtl')


def ease_out(t):           # cubic
    t = min(max(t, 0), 1); return 1 - (1 - t) ** 3


def ease_back(t, s=1.4):
    t = min(max(t, 0), 1) - 1; return t * t * ((s + 1) * t + s) + 1


def logo_img(w):
    lg = Image.open(LOGO).convert('RGBA'); lg = lg.crop(lg.getchannel('A').getbbox())
    return lg.resize((int(w), int(w * lg.height / lg.width)), Image.LANCZOS)


LOGO_TOP = logo_img(250)
LOGO_END = logo_img(760)


def chevron(d, x_right, cy, h, col_a=TEAL, col_b=TEAL_L):
    """The logo's chevron motif, pointing left (reading direction)."""
    u = h / 2
    d.polygon([(x_right, cy - u), (x_right - u * 0.75, cy - u), (x_right - u * 1.75, cy), (x_right - u, cy)], fill=col_a)
    d.polygon([(x_right - u * 1.75, cy), (x_right - u, cy), (x_right - u * 0.25, cy + u), (x_right - u * 1.0, cy + u)], fill=col_b)


# ---------- cards: photos (slow push-in) and video clips ----------
CARD_W, CARD_MAXH, CARD_CY = 940, 1030, 870
# the ballot (פתק ט) as a faint watermark behind everything: letter + text only, tinted with the brand teal
def ballot_layer(h, alpha, rot, letter_only=False):
    b = Image.open(U + '6157759a-image.jpg').convert('L')
    if letter_only: b = b.crop((0, 0, b.width, int(b.height * 0.69)))
    a = b.point(lambda v: max(0, min(255, int((235 - v) * 1.4))))
    lay = Image.new('RGBA', b.size, TEAL_L + (0,)); lay.putalpha(a.point(lambda v: int(v * alpha)))
    lay = lay.resize((int(b.width * h / b.height), h), Image.LANCZOS)
    return lay.rotate(rot, resample=Image.BICUBIC, expand=True)
BALLOT_BG = ballot_layer(1500, 0.28, -8, letter_only=True)
BALLOT_END = ballot_layer(1650, 0.13, 6)
def _bg(im):
    bg = im.copy(); s = max(W / bg.width, H / bg.height)
    bg = bg.resize((int(bg.width * s) + 2, int(bg.height * s) + 2), Image.BILINEAR)
    bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
    bg = Image.blend(bg.filter(ImageFilter.GaussianBlur(40)), Image.new('RGB', (W, H), DEEP), 0.72)
    bg.paste(BALLOT_BG, ((W - BALLOT_BG.width) // 2 + 40, (H - BALLOT_BG.height) // 2 - 130), BALLOT_BG)
    return bg

class Card:
    def __init__(self, it, idx):
        self.video = it[0] == 'v'
        if self.video:
            self.dir = P + f'v{idx:02d}/'; os.makedirs(self.dir, exist_ok=True)
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(it[2]), '-t', str(it[3] + 0.2), '-i', it[1],
                            '-vf', f'fps={FPS},unsharp=5:5:0.5', self.dir + '%04d.png'], check=True)
            self.frames = sorted(os.listdir(self.dir))
            im = Image.open(self.dir + self.frames[len(self.frames) // 2]).convert('RGB')
        else:
            im = Image.open(it[1]).convert('RGB')
        self.bg = _bg(im)
        s = min(CARD_W / im.width, CARD_MAXH / im.height)
        self.cw, self.ch = int(im.width * s), int(im.height * s)
        if not self.video:
            self.src = im.resize((int(self.cw * 1.07), int(self.ch * 1.07)), Image.LANCZOS)
        self.mask = Image.new('L', (self.cw, self.ch), 0)
        ImageDraw.Draw(self.mask).rounded_rectangle((0, 0, self.cw - 1, self.ch - 1), radius=30, fill=255)

    def card(self, t, dur):
        if self.video:
            f = self.frames[min(len(self.frames) - 1, int(t * FPS))]
            return Image.open(self.dir + f).convert('RGB').resize((self.cw, self.ch), Image.LANCZOS)
        z = 1.07 - 0.06 * (t / dur)
        vw, vh = self.cw * (1.07 / z), self.ch * (1.07 / z)
        x0, y0 = (self.src.width - vw) / 2, (self.src.height - vh) / 2
        return self.src.resize((self.cw, self.ch), Image.BILINEAR, box=(x0, y0, x0 + vw, y0 + vh))


def draw_route(d, idx, n):
    y = 1640; x1, x0 = W - 150, 150
    d.line([(x0, y), (x1, y)], fill=(0x4E, 0x6E, 0x72), width=4)
    if idx > 0:
        d.line([(x1 - (x1 - x0) * idx / (n - 1), y), (x1, y)], fill=TEAL_L, width=4)
    for i in range(n):
        x = x1 - (x1 - x0) * i / (n - 1)
        if i < idx: d.ellipse((x - 8, y - 8, x + 8, y + 8), fill=TEAL_L)
        elif i == idx:
            d.ellipse((x - 15, y - 15, x + 15, y + 15), fill=WHITE); d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=TEAL)
        else: d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=(0x4E, 0x6E, 0x72))
    text(d, (x1 + 70, y + 2), 'צפון', 34, PALE, anchor='rm', bold=False)
    text(d, (x0 - 20, y + 2), 'דרום', 34, PALE, anchor='rm', bold=False)


def item_frame(card, ci, t, dur, city_t, first):
    img = card.bg.copy()
    a = ease_out(t / 0.22); sc = 0.9 + 0.1 * ease_back(t / 0.3)
    c = card.card(t, dur)
    if sc != 1:
        c = c.resize((max(1, int(card.cw * sc)), max(1, int(card.ch * sc))), Image.BILINEAR)
    m = card.mask.resize(c.size, Image.BILINEAR)
    if a < 1: m = m.point(lambda v: int(v * a))
    cx, cy = W // 2, CARD_CY + int(40 * (1 - ease_out(t / 0.3)))
    if a > 0.6:
        ImageDraw.Draw(img).rounded_rectangle((cx - c.width // 2 - 5, cy - c.height // 2 - 5, cx + c.width // 2 + 5, cy + c.height // 2 + 5), radius=34, fill=PALE)
    img.paste(c, (cx - c.width // 2, cy - c.height // 2), m)
    img.paste(LOGO_TOP, ((W - LOGO_TOP.width) // 2, 150), LOGO_TOP)
    # city label: slides in once per city, then stays while that city's items play
    la = ease_out((city_t - 0.12) / 0.28)
    if la > 0:
        city = CITIES[ci][0]
        lbl = Image.new('RGBA', (W, 200), (0, 0, 0, 0)); ld = ImageDraw.Draw(lbl)
        size = 104; bw = tw(ld, city, size) + 150; x_r = (W + bw) / 2
        ld.rectangle((x_r - bw, 30, x_r, 170), fill=TEAL_D + (235,)); ld.rectangle((x_r - 12, 30, x_r, 170), fill=TEAL_L + (255,))
        chevron(ld, x_r - 34, 100, 58); text(ld, (x_r - 110, 98), city, size, WHITE, anchor='rm')
        lbl.putalpha(lbl.getchannel('A').point(lambda v: int(v * la)))
        img.paste(lbl, (int(60 * (1 - la)), 1420), lbl)
    draw_route(ImageDraw.Draw(img), ci, len(CITIES))
    return img

GRAD = Image.new('RGBA', (W, H), (0, 0, 0, 0))
_g = ImageDraw.Draw(GRAD)
for y in range(H):
    t = y / H
    a = int(170 * max(0, 1 - t / 0.16)) + int(235 * max(0, (t - 0.45) / 0.55) ** 1.3)
    _g.line([(0, y), (W, y)], fill=DEEP + (min(a, 235),))


def pop_line(img, s, size, y, t0, t, color, block=None):
    a = ease_out((t - t0) / 0.22)
    if a <= 0:
        return
    sc = 0.85 + 0.15 * ease_back((t - t0) / 0.3)
    lay = Image.new('RGBA', (W, int(size * 1.6)), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    if block:
        tx = tw(ld, s, size); ld.rectangle(((W - tx) / 2 - 30, size * 0.12, (W + tx) / 2 + 30, size * 1.25), fill=block + (255,))
    text(ld, (W / 2, size * 0.68), s, size, color, anchor='mm')
    if sc != 1:
        lay = lay.resize((int(W * sc), int(lay.height * sc)), Image.BILINEAR)
    lay.putalpha(lay.getchannel('A').point(lambda v: int(v * a)))
    img.paste(lay, ((W - lay.width) // 2, int(y - lay.height / 2)), lay)


# ---------- opener: the Petah Tikva bus chanting, full bleed ----------
OPEN_FRAMES = P + 'open/'
def prep_opener():
    os.makedirs(OPEN_FRAMES, exist_ok=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(OPEN_CLIP[1]), '-t', str(OPEN_T + 0.1), '-i', OPEN_CLIP[0],
                    '-vf', f'fps={FPS},scale={W}:-2:flags=lanczos,crop={W}:{H},unsharp=5:5:0.6', OPEN_FRAMES + '%04d.png'], check=True)


def open_frame(i, t):
    fs = sorted(os.listdir(OPEN_FRAMES))
    img = Image.open(OPEN_FRAMES + fs[min(i, len(fs) - 1)]).convert('RGB')
    img.paste(GRAD, (0, 0), GRAD)
    img.paste(LOGO_TOP, ((W - LOGO_TOP.width) // 2, 150), LOGO_TOP)
    pop_line(img, 'יוצאים לחרוש', 180, 1170, 0.3, t, WHITE)
    pop_line(img, 'את הארץ', 180, 1370, 0.75, t, WHITE, block=TEAL)
    a = ease_out((t - 1.4) / 0.3)
    if a > 0:
        col = tuple(int(v * a + DEEP[k] * (1 - a)) for k, v in enumerate(PALE))
        text(ImageDraw.Draw(img), (W / 2, 1545), 'מקצרין ועד אשקלון', 52, col, anchor='mm', bold=False)
    if t > OPEN_T - 0.12:
        img = Image.blend(img, Image.new('RGB', (W, H), DEEP), (t - (OPEN_T - 0.12)) / 0.12 * 0.7)
    return img


# ---------- end card ----------
END_BG = Image.new('RGB', (W, H)); _e = ImageDraw.Draw(END_BG)
for y in range(H):
    t = y / H
    _e.line([(0, y), (W, y)], fill=tuple(int(DEEP[k] + (TEAL_D[k] - DEEP[k]) * t) for k in range(3)))


def end_frame(t):
    img = END_BG.copy()
    ba = ease_out(t / 0.8); bl = BALLOT_END.copy(); bl.putalpha(bl.getchannel('A').point(lambda v: int(v * ba)))
    img.paste(bl, ((W - bl.width) // 2 - 30, (H - bl.height) // 2 + 170 + int(40 * (1 - ba))), bl)
    d = ImageDraw.Draw(img)
    # big chevron sweeping in behind the text
    a = ease_out(t / 0.5)
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    chevron(ld, W + 260 - 200 * a, 1660, 760, col_a=TEAL + (70,), col_b=TEAL_L + (70,))
    img.paste(lay, (0, 0), lay)
    pop_line(img, 'חורשים את הארץ', 200, 560, 0.25, t, WHITE)
    pop_line(img, 'כן. סמוטריץ׳.', 190, 800, 0.8, t, WHITE, block=TEAL)
    la = ease_out((t - 1.6) / 0.4)
    if la > 0:
        sc = 0.9 + 0.1 * ease_back((t - 1.6) / 0.45)
        lg = LOGO_END.resize((int(LOGO_END.width * sc), int(LOGO_END.height * sc)), Image.BILINEAR)
        lg.putalpha(lg.getchannel('A').point(lambda v: int(v * la)))
        img.paste(lg, ((W - lg.width) // 2, 1080 - lg.height // 2 + 120), lg)
    return img


def render(out_video):
    prep_opener()
    cards = [Card(it, j) for j, (_, it, _, _, _) in enumerate(ITEMS)]
    city_start = {}
    for ci, it, st, d, first in ITEMS:
        city_start.setdefault(ci, st)
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', out_video], stdin=subprocess.PIPE)
    for i in range(int(round(TOTAL * FPS))):
        t = i / FPS
        if t < OPEN_T: fr = open_frame(i, t)
        elif t < END_START:
            j = max(k for k, x in enumerate(ITEMS) if x[2] <= t + 1e-6)
            ci, it, st, d, first = ITEMS[j]
            fr = item_frame(cards[j], ci, t - st, d, t - city_start[ci], first)
        else: fr = end_frame(t - END_START)
        ff.stdin.write(fr.convert('RGB').tobytes())
    ff.stdin.close(); ff.wait()


def mix_audio(out_wav):
    cues = []    # (file, at, vol, trim_start, trim_dur)
    cues.append((OPEN_CLIP[0], 0.0, 1.0, OPEN_CLIP[1], OPEN_T))
    cues += [(SFX + 'whoosh.wav', 0.18, 0.35, 0, 0), (SFX + 'pop_soft.wav', 0.3, 0.7, 0, 0), (SFX + 'pop_soft.wav', 0.75, 0.7, 0, 0), (SFX + 'blip.wav', 1.4, 0.3, 0, 0)]
    for ci, it, st, d, first in ITEMS:
        cues.append((SFX + ('whoosh.wav' if first else 'swoosh_soft.wav'), st - 0.1, 0.5 if first else 0.35, 0, 0))
        if first: cues += [(SFX + 'pop_soft.wav', st + 0.14, 0.55, 0, 0), (SFX + 'tick.wav', st + 0.05, 0.35, 0, 0)]
        if it[0] == 'v':
            f, s0 = (it[4] if len(it) > 4 else (it[1], it[2]))
            cues.append((f, st, 1.0, s0, d))
    cues += [(SFX + 'riser.wav', END_START - 1.5, 0.3, 0, 0), (SFX + 'whoosh.wav', END_START - 0.1, 0.6, 0, 0), (SFX + 'swoosh_soft.wav', END_START + 0.1, 0.4, 0, 0),
             (SFX + 'pop_soft.wav', END_START + 0.25, 0.9, 0, 0), (SFX + 'hit_soft.wav', END_START + 0.8, 0.85, 0, 0), (SFX + 'chime_up.wav', END_START + 1.6, 0.4, 0, 0)]
    args = ['ffmpeg', '-v', 'error', '-y']; fl = []
    for j, (f, at, vol, s0, dur) in enumerate(cues):
        args += ['-i', f]
        ex = f',atrim={s0}:{s0 + dur},asetpts=PTS-STARTPTS,loudnorm=I=-18:TP=-3,afade=t=in:d=0.08,afade=t=out:st={dur - 0.15}:d=0.15' if dur else ''
        fl.append(f'[{j}:a]aformat=sample_rates=48000:channel_layouts=stereo{ex},volume={vol},adelay={int(max(0, at) * 1000)}|{int(max(0, at) * 1000)}[a{j}]')
    fl.append(''.join(f'[a{j}]' for j in range(len(cues))) + f'amix=inputs={len(cues)}:normalize=0,atrim=0:{TOTAL:.3f},apad=whole_dur={TOTAL:.3f}[out]')
    subprocess.run(args + ['-filter_complex', ';'.join(fl), '-map', '[out]', out_wav], check=True)


if __name__ == '__main__':
    import sys
    os.makedirs(P, exist_ok=True)
    vid, wav = P + 'video.mp4', P + 'audio.wav'
    if len(sys.argv) > 1 and sys.argv[1] == 'stills':
        prep_opener(); pick = [0, 3, 5, 9, 14]; cards = {j: Card(ITEMS[j][1], j) for j in pick}
        shots = [open_frame(60, 2.0)] + [item_frame(cards[j], ITEMS[j][0], 0.8, ITEMS[j][3], 0.8, True) for j in pick] + [end_frame(3.5)]
        sheet = Image.new('RGB', (len(shots) * 370, 660), WHITE)
        for j, s in enumerate(shots): sheet.paste(s.resize((360, 640)), (j * 370, 0))
        sheet.save(HERE + '/stills.jpg'); print('stills', TOTAL)
    else:
        render(vid); mix_audio(wav)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', vid, '-i', wav, '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', P + 'mux.mp4'], check=True)
        subprocess.run(['python3', SKILL + '/scripts/loudnorm.py', P + 'mux.mp4', HERE + '/rz-story-cities.mp4', '--target', '-14'], check=True)
        print('done', TOTAL)
