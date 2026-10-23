"""Religious Zionism story video: field activity across the country (1080x1920, 30fps, no music)."""
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

OPEN_T, SLIDE_T, END_T = 3.6, 1.3, 4.2
# north to south
SLIDES = [
    ('קריית שמונה', P + 'kiryat-shmona.jpg'),
    ('קצרין', P + 'katzrin.jpg'),
    ('מעלות', P + 'maalot.jpg'),
    ('כרמיאל', M + 'karmiel-09.jpg'),
    ('עכו', M + 'akko-01.jpg'),
    ('קריית אתא', M + 'kiryat-ata-02.jpg'),
    ('מגדל העמק', M + 'migdal-haemek-01.jpg'),
    ('בית שאן', P + 'beit-shean.jpg'),
    ('חריש', M + 'harish-01.jpg'),
    ('ירושלים', M + 'jerusalem-cbs-01.jpg'),
    ('מעלה אדומים', M + '01-maale-adumim-a.jpg'),
    ('יד בנימין', M + 'yad-binyamin-01.jpg'),
    ('אשקלון', M + 'ashkelon-01.jpg'),
    ('נתיבות', M + 'netivot-02.jpg'),
    ('באר שבע', M + 'beer-sheva-01.jpg'),
    ('דימונה', M + 'dimona-02.jpg'),
]
SLIDES_START = OPEN_T
END_START = SLIDES_START + len(SLIDES) * SLIDE_T
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


# ---------- photo slides ----------
CARD_W, CARD_MAXH, CARD_CY = 940, 1030, 870
class Slide:
    def __init__(self, city, path):
        self.city = city
        im = Image.open(path).convert('RGB')
        # blurred, tinted fill of the same photo (no crop of the real photo)
        bg = im.copy(); s = max(W / bg.width, H / bg.height)
        bg = bg.resize((int(bg.width * s) + 2, int(bg.height * s) + 2), Image.BILINEAR)
        bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
        bg = bg.filter(ImageFilter.GaussianBlur(40))
        self.bg = Image.blend(bg, Image.new('RGB', (W, H), DEEP), 0.72)
        s = min(CARD_W / im.width, CARD_MAXH / im.height)
        self.cw, self.ch = int(im.width * s), int(im.height * s)
        self.src = im.resize((int(self.cw * 1.07), int(self.ch * 1.07)), Image.LANCZOS)
        self.mask = Image.new('L', (self.cw, self.ch), 0)
        ImageDraw.Draw(self.mask).rounded_rectangle((0, 0, self.cw - 1, self.ch - 1), radius=30, fill=255)

    def card(self, p):
        """Card at progress p of the slide: slow push-in (Ken Burns) inside a fixed frame."""
        z = 1.07 - 0.06 * p
        w, h = self.src.width / z * (1 / 1.07) * 1.0, None
        cw, ch = self.cw / (z / 1.0), self.ch / (z / 1.0)
        sx, sy = self.src.width / 1.07, self.src.height / 1.07
        vw, vh = sx * (1.0 / (z / 1.07)) / 1.07 * 1.07, None
        # visible window inside the over-sized source
        vw = self.src.width / (z / 1.0) * (1.0 / 1.07) * 1.07 / 1.07
        vw = self.cw * (1.07 / z); vh = self.ch * (1.07 / z)
        x0 = (self.src.width - vw) / 2; y0 = (self.src.height - vh) / 2
        c = self.src.resize((self.cw, self.ch), Image.BILINEAR, box=(x0, y0, x0 + vw, y0 + vh))
        return c


def draw_route(d, idx, n):
    """North-to-south route: dots from right (north) to left (south), current one highlighted."""
    y = 1612; x1, x0 = W - 150, 150
    d.line([(x0, y), (x1, y)], fill=(0x4E, 0x6E, 0x72), width=4)
    for i in range(n):
        x = x1 - (x1 - x0) * i / (n - 1)
        if i < idx:
            d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=TEAL_L)
        elif i == idx:
            d.ellipse((x - 14, y - 14, x + 14, y + 14), fill=WHITE)
            d.ellipse((x - 8, y - 8, x + 8, y + 8), fill=TEAL)
        else:
            d.ellipse((x - 6, y - 6, x + 6, y + 6), fill=(0x4E, 0x6E, 0x72))
    if idx > 0:
        d.line([(x1 - (x1 - x0) * idx / (n - 1), y), (x1, y)], fill=TEAL_L, width=4)
    text(d, (x1 + 70, y + 2), 'צפון', 34, PALE, anchor='rm', bold=False)
    text(d, (x0 - 20, y + 2), 'דרום', 34, PALE, anchor='rm', bold=False)


def slide_frame(sl, idx, t):
    img = sl.bg.copy(); d = ImageDraw.Draw(img)
    p = t / SLIDE_T
    # card entrance: scale 0.9 -> 1 with slight overshoot, fade in
    a = ease_out(t / 0.24); sc = 0.9 + 0.1 * ease_back(t / 0.3)
    card = sl.card(p)
    if sc != 1:
        card_s = card.resize((max(1, int(sl.cw * sc)), max(1, int(sl.ch * sc))), Image.BILINEAR)
        mask_s = sl.mask.resize(card_s.size, Image.BILINEAR)
    else:
        card_s, mask_s = card, sl.mask
    if a < 1:
        mask_s = mask_s.point(lambda v: int(v * a))
    cx, cy = W // 2, CARD_CY + int(40 * (1 - ease_out(t / 0.3)))
    # soft shadow + thin light frame
    ImageDraw.Draw(img).rounded_rectangle((cx - card_s.width // 2 - 5, cy - card_s.height // 2 - 5,
                                           cx + card_s.width // 2 + 5, cy + card_s.height // 2 + 5),
                                          radius=34, fill=tuple(int(v * (0.25 + 0.75 * (1 - a)) + PALE[i] * 0.75 * a) if False else PALE[i] for i, v in enumerate(DEEP))) if a > 0.6 else None
    img.paste(card_s, (cx - card_s.width // 2, cy - card_s.height // 2), mask_s)
    d = ImageDraw.Draw(img)
    img.paste(LOGO_TOP, ((W - LOGO_TOP.width) // 2, 196), LOGO_TOP)
    # city label slides in from the right
    la = ease_out((t - 0.12) / 0.28)
    if la > 0:
        lbl = Image.new('RGBA', (W, 200), (0, 0, 0, 0)); ld = ImageDraw.Draw(lbl)
        size = 104; tx = tw(ld, sl.city, size)
        bw = tx + 150; x_r = (W + bw) / 2
        ld.rectangle((x_r - bw, 30, x_r, 170), fill=TEAL_D + (235,))
        ld.rectangle((x_r - 12, 30, x_r, 170), fill=TEAL_L + (255,))
        chevron(ld, x_r - 34, 100, 58)
        text(ld, (x_r - 110, 98), sl.city, size, WHITE, anchor='rm')
        lbl.putalpha(lbl.getchannel('A').point(lambda v: int(v * la)))
        img.paste(lbl, (int(60 * (1 - la)), 1395), lbl)
    draw_route(ImageDraw.Draw(img), idx, len(SLIDES))
    return img


# ---------- opener: Jerusalem market march ----------
OPEN_FRAMES = HERE + '/prep/open/'
def prep_opener():
    os.makedirs(OPEN_FRAMES, exist_ok=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '3.3', '-t', str(OPEN_T), '-i', M + 'jerusalem-video-01.mov',
                    '-vf', f'fps={FPS},scale={W}:-2:flags=lanczos,crop={W}:{H},unsharp=5:5:0.6',
                    OPEN_FRAMES + '%04d.png'], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '3.3', '-t', str(OPEN_T), '-i', M + 'jerusalem-video-01.mov',
                    '-vn', '-ac', '2', '-ar', '48000', HERE + '/prep/open.wav'], check=True)


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


def open_frame(i, t):
    img = Image.open(OPEN_FRAMES + f'{min(i + 1, int(OPEN_T * FPS)):04d}.png').convert('RGB')
    img.paste(GRAD, (0, 0), GRAD)
    img.paste(LOGO_TOP, ((W - LOGO_TOP.width) // 2, 196), LOGO_TOP)
    pop_line(img, 'מקריית שמונה', 190, 1180, 0.35, t, WHITE)
    pop_line(img, 'ועד דימונה', 190, 1390, 0.95, t, WHITE, block=TEAL)
    d = ImageDraw.Draw(img)
    a = ease_out((t - 1.5) / 0.3)
    if a > 0:
        col = tuple(int(v * a + DEEP[k] * (1 - a)) for k, v in enumerate(PALE))
        text(d, (W / 2, 1560), 'ירושלים · שוק מחנה יהודה', 44, col, anchor='mm', bold=False)
    # quick flash-out into the first city
    if t > OPEN_T - 0.12:
        img = Image.blend(img, Image.new('RGB', (W, H), DEEP), (t - (OPEN_T - 0.12)) / 0.12 * 0.7)
    return img


# ---------- end card ----------
END_BG = Image.new('RGB', (W, H)); _e = ImageDraw.Draw(END_BG)
for y in range(H):
    t = y / H
    _e.line([(0, y), (W, y)], fill=tuple(int(DEEP[k] + (TEAL_D[k] - DEEP[k]) * t) for k in range(3)))


def end_frame(t):
    img = END_BG.copy(); d = ImageDraw.Draw(img)
    # big chevron sweeping in behind the text
    a = ease_out(t / 0.5)
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    chevron(ld, W + 260 - 200 * a, 1660, 760, col_a=TEAL + (70,), col_b=TEAL_L + (70,))
    img.paste(lay, (0, 0), lay)
    pop_line(img, 'בכל הארץ!', 200, 560, 0.25, t, WHITE)
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
    slides = [Slide(c, p) for c, p in SLIDES]
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                           '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
                           '-pix_fmt', 'yuv420p', out_video], stdin=subprocess.PIPE)
    n = int(round(TOTAL * FPS))
    for i in range(n):
        t = i / FPS
        if t < SLIDES_START:
            fr = open_frame(i, t)
        elif t < END_START:
            k = int((t - SLIDES_START) / SLIDE_T)
            fr = slide_frame(slides[k], k, t - SLIDES_START - k * SLIDE_T)
        else:
            fr = end_frame(t - END_START)
        ff.stdin.write(fr.convert('RGB').tobytes())
    ff.stdin.close(); ff.wait()


def mix_audio(out_wav):
    cues = [('open', 0.0, 0.45)]                         # market ambience, low
    cues += [('whoosh', 0.2, 0.45), ('pop_soft', 0.35, 0.9),     # headline lines pop in
             ('whoosh', 0.82, 0.45), ('pop_soft', 0.95, 0.9), ('blip', 1.5, 0.35)]
    for k in range(len(SLIDES)):
        t0 = SLIDES_START + k * SLIDE_T
        cues.append(('swoosh_soft' if k % 2 else 'whoosh', t0 - 0.1, 0.55))   # card transition
        cues.append(('pop_soft', t0 + 0.14, 0.55))                            # city label slides in
        cues.append(('tick', t0 + 0.05, 0.35))                                # route dot advances
    cues += [('riser', END_START - 1.5, 0.35), ('whoosh', END_START - 0.1, 0.6),
             ('swoosh_soft', END_START + 0.1, 0.4),                           # chevron sweep
             ('pop_soft', END_START + 0.25, 0.9), ('hit_soft', END_START + 0.8, 0.85),
             ('chime_up', END_START + 1.6, 0.4)]                              # logo reveal
    args = ['ffmpeg', '-v', 'error', '-y']
    for name, _, _ in cues:
        args += ['-i', HERE + '/prep/open.wav' if name == 'open' else SFX + name + '.wav']
    fl = []
    for j, (name, at, vol) in enumerate(cues):
        extra = ',afade=t=out:st=3.0:d=0.6' if name == 'open' else ''
        fl.append(f'[{j}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={vol}{extra},adelay={int(at * 1000)}|{int(at * 1000)}[a{j}]')
    fl.append(''.join(f'[a{j}]' for j in range(len(cues))) + f'amix=inputs={len(cues)}:normalize=0,atrim=0:{TOTAL:.3f},apad=whole_dur={TOTAL:.3f}[out]')
    args += ['-filter_complex', ';'.join(fl), '-map', '[out]', out_wav]
    subprocess.run(args, check=True)


if __name__ == '__main__':
    import sys
    vid, wav = HERE + '/prep/video.mp4', HERE + '/prep/audio.wav'
    if len(sys.argv) > 1 and sys.argv[1] == 'stills':        # quick look at key frames
        prep_opener(); slides = [Slide(c, p) for c, p in SLIDES]
        shots = [open_frame(int(2.5 * FPS), 2.5)] + [slide_frame(slides[k], k, 0.9) for k in (0, 3, 9, 15)] + [end_frame(3.5)]
        sheet = Image.new('RGB', (len(shots) * 370, 660), WHITE)
        for j, s in enumerate(shots):
            sheet.paste(s.resize((360, 640)), (j * 370, 0))
        sheet.save(HERE + '/stills.jpg'); print('stills')
    else:
        render(vid); mix_audio(wav)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', vid, '-i', wav, '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
                        '-shortest', '-movflags', '+faststart', HERE + '/prep/mux.mp4'], check=True)
        subprocess.run(['python3', SKILL + '/scripts/loudnorm.py', HERE + '/prep/mux.mp4', HERE + '/rz-story-field.mp4', '--target', '-14'], check=True)
        print('done', TOTAL)
