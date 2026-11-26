"""'שָׁלֵו הַמְעַרְבֵּב' clip: half children's storybook, half pop. Synced to the user's song (lyric lines locked to the beat grid:
line k starts at 2.60 + (k-1)*2.778 s, found by Whisper on sliding windows). Footage muted, song only.
Only real footage of Shalev is used (as stickers); nobody is drawn or generated. The 'after' card is a paraphrase, no quote marks."""
import os, sys, math, glob, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
HERE = os.path.dirname(os.path.abspath(__file__))
SC = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/shalev/'; P = SC + 'prep/'; os.makedirs(P, exist_ok=True)
FD = SC + 'fonts/'; KB = glob.glob('/root/.claude/skills/synced/*/pro-video-editing/assets/fonts/Karantina-Bold.ttf')[0]
EMO = '/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'
V1 = HERE + '/footage/shalev-debate-v1.mp4'; V2 = HERE + '/footage/shalev-clip2.mov'; V3 = HERE + '/footage/shalev-clip3.mov'; SONG = HERE + '/song.wav'
W, H, FPS = 1080, 1920, 30
BEAT = 60 / 86.4; BAR = 4 * BEAT; L0 = 2.60
def LS(k): return L0 + (k - 1) * BAR          # start of lyric line k (1..14)
SONG_END = 41.6; C3 = LS(15) - .3; C3D = 8.95; END0 = C3 + C3D; TOTAL = END0 + 2.4
BR = [(LS(5), 'v1', 0.0, 3.55), (LS(9), 'v2', 1.70, 4.65)]   # song pauses, Shalev speaks (song time, src, in, out)
DSUM = sum(b - a for _, _, a, b in BR); TOTAL_V = TOTAL + DSUM
TAPE = HERE + '/../2026-11-reel-bennett-before-after/audio/tape_stop.wav'
C3SUB = [(0.0, 2.6, 'אני בטוח שכבר קנית ציצית,'), (2.6, 4.9, 'הנחת תפילין, שמת כיפה,'), (4.9, 6.2, 'תתחיל לשמור שבת.'), (6.2, 9.0, 'רק תבואו איתנו. אה?')]
LY = {1: 'שָׁלֵו שָׁלֵו, הַמְעַרְבֵּב', 2: 'עָשָׂה וָואחַד קַמְפֵּיין', 3: 'עִם מַדִּים וּמִלּוּאִים', 4: 'טִנֵּף עַל מִשְׁתַּמְּטִים',
      5: 'שָׁלֵו שָׁלֵו הַמְעַרְבֵּב', 6: 'עָשָׂה וָואחַד סִבּוּב', 7: 'עַל הַלּוֹחֲמִים, עַל הַחֲרֵדִים', 8: 'עַל בְּרִית הַמְּשָׁרְתִים',
      9: 'לָה לָה לָה כִּסֵּא', 10: 'לָה לָה לָה כִּסֵּא', 11: 'לָה לָה לָה כִּסֵּא', 12: 'לָה לָה לָה לָה', 13: 'שָׁלֵו שָׁלֵו הַמְעַרְבֵּב', 14: 'שָׁבַרְתָּ לִי תַּ\'לֵּב'}
# clip ranges (source, start, crop) per line
CLIPS = {6: ('v1', 8.9), 1: ('v1', 1.5), 2: ('v1', 3.8), 3: ('v1', 7.6), 4: ('v2', 1.6), 5: ('v1', 0.0), 9: ('v1', 27.4), 10: ('v1', 24.6), 11: ('v1', 29.8), 13: ('v1', 0.0), 7: ('v1', 4.0)}
INK = (45, 40, 90); RED = (230, 45, 60); YEL = (255, 210, 0); YEL2 = (255, 186, 0); WHITE = (255, 255, 255); BLACK = (0, 0, 0)
_f = {}
def F(name, s):
    k = (name, s)
    if k not in _f: _f[k] = ImageFont.truetype(KB if name == 'kar' else FD + name, s, layout_engine=ImageFont.Layout.RAQM)
    return _f[k]
def eo(x): x = max(0., min(1., x)); return 1 - (1 - x) ** 3
def bk(x, s=1.8): x = max(0., min(1., x)); x -= 1; return x * x * ((s + 1) * x + s) + 1
def beatpulse(t): ph = ((t - .51) / BEAT) % 1; return math.exp(-ph * 6)
rng = np.random.default_rng(7)

# ---------- footage ----------
def prep():
    for i, (_, src, a, b) in enumerate(BR):
        d = P + f'brk{i}/'
        if os.path.exists(d + '0001.png'): continue
        os.makedirs(d, exist_ok=True); crop = 'crop=720:620:0:0,scale=760:654' if src == 'v1' else 'crop=1080:1350:0:80,scale=640:800'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(a), '-t', str(b - a + .1), '-i', V1 if src == 'v1' else V2, '-vf', f'fps={FPS},{crop}', d + '%04d.png'], check=True)
    d = P + 'end3/'
    if not os.path.exists(d + '0001.png'):
        os.makedirs(d, exist_ok=True)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', V3, '-vf', f'fps={FPS},crop=1388:932:36:68,scale=900:604', d + '%04d.png'], check=True)
    for k, (src, s0) in CLIPS.items():
        d = P + f'c{k}/'
        if os.path.exists(d + '0001.png'): continue
        os.makedirs(d, exist_ok=True)
        crop = 'crop=720:620:0:0,scale=760:654' if src == 'v1' else 'crop=1080:1350:0:80,scale=640:800'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(s0), '-t', str(BAR * (2 if k == 7 else 1) + .3), '-i', V1 if src == 'v1' else V2, '-vf', f'fps={FPS},{crop}', d + '%04d.png'], check=True)
_cf = {}
def clipframe(k, u):
    d = P + f'c{k}/'
    if d not in _cf: _cf[d] = sorted(os.listdir(d))
    fs = _cf[d]; return Image.open(d + fs[max(0, min(len(fs) - 1, int(u * FPS)))]).convert('RGB')
STK_MASK = {}
def sticker(im, border=16, radius=30):
    w, h = im.size; key = (w, h, border)
    if key not in STK_MASK:
        m = Image.new('L', (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), radius, fill=255)
        bm = Image.new('L', (w + 2 * border, h + 2 * border), 0); ImageDraw.Draw(bm).rounded_rectangle((0, 0, w + 2 * border - 1, h + 2 * border - 1), radius + border, fill=255)
        sh = Image.new('L', (w + 2 * border + 80, h + 2 * border + 80), 0); sh.paste(bm.point(lambda v: v * .45), (40, 52)); sh = sh.filter(ImageFilter.GaussianBlur(16))
        STK_MASK[key] = (m, bm, sh)
    m, bm, sh = STK_MASK[key]
    out = Image.new('RGBA', sh.size, (0, 0, 0, 0)); out.paste((0, 0, 0, 255), (0, 0), sh)
    out.paste((255, 255, 255, 255), (40, 40), bm); tmp = im.convert('RGBA'); tmp.putalpha(m); out.alpha_composite(tmp, (40 + border, 40 + border))
    return out
def place(canvas, layer, cx, cy, scale=1., rot=0.):
    if scale <= .01: return
    l = layer if abs(scale - 1) < .001 else layer.resize((max(1, int(layer.width * scale)), max(1, int(layer.height * scale))), Image.BILINEAR)
    if abs(rot) > .05: l = l.rotate(rot, expand=True, resample=Image.BILINEAR)
    canvas.alpha_composite(l, (int(cx - l.width / 2), int(cy - l.height / 2)))

# ---------- emoji stickers ----------
_em = {}
def emoji(ch, size):
    k = (ch, size)
    if k not in _em:
        f = ImageFont.truetype(EMO, 109); im = Image.new('RGBA', (170, 170), (0, 0, 0, 0)); ImageDraw.Draw(im).text((12, 12), ch, font=f, embedded_color=True)
        im = im.crop(im.getbbox()); im = im.resize((size, int(size * im.height / im.width)), Image.LANCZOS)
        pad = 14; b = Image.new('RGBA', (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0)); b.alpha_composite(im, (pad, pad))
        m = b.getchannel('A').filter(ImageFilter.MaxFilter(13)); o = Image.new('RGBA', b.size, (255, 255, 255, 0)); o.putalpha(m); o.alpha_composite(b); _em[k] = o
    return _em[k]

# ---------- backgrounds ----------
def crayon(d, pts, col, w=10, passes=3, r=None):
    r = r or rng
    for _ in range(passes): d.line([(x + r.normal(0, 2.5), y + r.normal(0, 2.5)) for x, y in pts], fill=col, width=w, joint='curve')
def make_paper(seed):
    r = np.random.default_rng(seed); a = np.full((H, W, 3), (247, 238, 218), np.float32) + r.normal(0, 6, (H, W, 1))
    im = Image.fromarray(np.clip(a, 0, 255).astype('uint8')).convert('RGBA'); d = ImageDraw.Draw(im)
    for i in range(60): d.line((i, 0, i, H), fill=(200, 185, 150, int(90 * (1 - i / 60))))
    d.ellipse((860, 140, 1000, 280), fill=(255, 214, 90)); crayon(d, [(930 + 78 * math.cos(a), 210 + 78 * math.sin(a)) for a in np.linspace(0, 6.3, 30)], (240, 170, 40), 7, 2, r)
    for k in range(10): a = k * .628; crayon(d, [(930 + 95 * math.cos(a), 210 + 95 * math.sin(a)), (930 + 130 * math.cos(a), 210 + 130 * math.sin(a))], (240, 170, 40), 6, 2, r)
    for cx, cy in [(240, 230)]:
        for dx, dy, rr in [(-60, 10, 52), (0, -20, 66), (60, 10, 52)]: d.ellipse((cx + dx - rr, cy + dy - rr, cx + dx + rr, cy + dy + rr), fill=WHITE)
    pts = [(x, 1730 + 26 * math.sin(x / 140)) for x in range(0, W + 40, 40)]
    d.polygon(pts + [(W, H), (0, H)], fill=(150, 200, 110)); crayon(d, pts, (110, 170, 80), 12, 3, r)
    for x in range(80, W, 160): crayon(d, [(x, 1790), (x + 10, 1755)], (95, 150, 70), 6, 2, r)
    return im
PAPER = [make_paper(s) for s in (1, 2, 3)]       # 'boil': cycle 3 hand-drawn versions
def paper(t): return PAPER[int(t * 8) % 3].copy()
BURST = Image.new('RGB', (2400, 2400), YEL); bd = ImageDraw.Draw(BURST)
for k in range(24):
    a0 = k * 2 * math.pi / 24; a1 = a0 + math.pi / 24; bd.polygon([(1200, 1200), (1200 + 2000 * math.cos(a0), 1200 + 2000 * math.sin(a0)), (1200 + 2000 * math.cos(a1), 1200 + 2000 * math.sin(a1))], fill=YEL2)
BURST_R = Image.new('RGB', (2400, 2400), (255, 90, 90)); bd = ImageDraw.Draw(BURST_R)
for k in range(24):
    a0 = k * 2 * math.pi / 24; a1 = a0 + math.pi / 24; bd.polygon([(1200, 1200), (1200 + 2000 * math.cos(a0), 1200 + 2000 * math.sin(a0)), (1200 + 2000 * math.cos(a1), 1200 + 2000 * math.sin(a1))], fill=(235, 55, 70))
def pop(t, red=False, cy=900):
    b = (BURST_R if red else BURST).rotate(t * 18, resample=Image.BILINEAR); y0 = 1200 - cy
    return b.crop((660, y0, 660 + W, y0 + H)).convert('RGBA')

# ---------- text ----------
def lyric_story(im, k, t, y=1460, size=128):
    """handwritten-style storybook line, words appear one by one"""
    words = LY[k].split(' '); u = t - LS(k); n = len(words); d = ImageDraw.Draw(im); f = F('SecularOne.ttf', size)
    shown = [w for i, w in enumerate(words) if u > .15 + i * (1.6 / n)]
    if not shown: return
    full = ' '.join(words); tw = d.textlength(full, font=f, direction='rtl')
    if tw > W - 120: f = F('SecularOne.ttf', int(size * (W - 120) / tw)); tw = d.textlength(full, font=f, direction='rtl')
    x = W / 2 + tw / 2
    for i, w in enumerate(words):
        ww = d.textlength(w + (' ' if i < n - 1 else ''), font=f, direction='rtl')
        if w in shown:
            p = eo((u - .15 - i * (1.6 / n)) / .25); yy = y + 30 * (1 - p)
            d.text((x, yy), w, font=f, fill=INK + (int(255 * p),), anchor='ra', direction='rtl')
        x -= ww
def popword(im, s, cx, y, size, t0, t, fill=WHITE, blk=None, rot=0, stroke=10):
    p = (t - t0) / .18
    if p <= 0: return
    sc = 1.7 - .7 * eo(p); f = F('kar', int(size * sc))
    lay = Image.new('RGBA', (W + 400, int(size * sc * 1.5) + 60), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay); c = lay.width / 2
    tw = ld.textlength(s, font=f, direction='rtl')
    if blk: ld.rounded_rectangle((c - tw / 2 - 30, 26, c + tw / 2 + 30, 26 + int(size * sc * .98)), 20, fill=blk)
    ld.text((c + 8, 22), s, font=f, fill=BLACK, anchor='ma', direction='rtl', stroke_width=stroke, stroke_fill=BLACK)
    ld.text((c, 14), s, font=f, fill=fill, anchor='ma', direction='rtl', stroke_width=stroke, stroke_fill=BLACK)
    place(im, lay, cx, y + lay.height / 2, 1, rot)

# ---------- drawn props ----------
def blender_layer(t, spin, contents=()):
    """crayon blender (≈520x760) with spinning blades and swirling contents"""
    L = Image.new('RGBA', (620, 820), (0, 0, 0, 0)); d = ImageDraw.Draw(L); r = np.random.default_rng(int(t * 8) % 3 + 10)
    jar = [(90, 60), (150, 560), (470, 560), (530, 60)]
    d.polygon(jar, fill=(210, 235, 250, 150))
    for (nm, ang, rad, sc) in contents:
        a = ang + spin * 1.0; x = 310 + rad * math.cos(a); y = 330 + rad * .55 * math.sin(a)
        if isinstance(nm, Image.Image): place(L, nm, x, y, sc, math.degrees(a) * .3)
    crayon(d, jar + [jar[0]], (60, 110, 190), 12, 3, r); crayon(d, [(60, 60), (560, 60)], (60, 110, 190), 16, 2, r)
    d.rounded_rectangle((120, 570, 500, 720), 30, fill=(70, 120, 200)); crayon(d, [(120, 575), (500, 575)], (40, 80, 150), 8, 2, r)
    d.ellipse((280, 615, 340, 675), fill=(255, 210, 0)); d.ellipse((380, 625, 420, 665), fill=RED)
    for k in range(3):   # blades
        a = spin * 3 + k * 2.09; crayon(d, [(310, 520), (310 + 110 * math.cos(a), 520 + 26 * math.sin(a))], (120, 120, 130), 9, 1, r)
    for k in range(4):   # swirl lines
        a = spin * 2 + k * 1.57; pts = [(310 + (60 + 25 * i) * math.cos(a + i * .5), 360 + (60 + 25 * i) * .5 * math.sin(a + i * .5)) for i in range(6)]
        crayon(d, pts, (255, 255, 255), 5, 1, r)
    return L
def label(s, size=70, col=(255, 255, 255), bg=(45, 40, 90)):
    f = F('SecularOne.ttf', size); tmp = ImageDraw.Draw(Image.new('RGBA', (1, 1))); tw = int(tmp.textlength(s, font=f, direction='rtl'))
    L = Image.new('RGBA', (tw + 60, size + 50), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rounded_rectangle((0, 0, L.width - 1, L.height - 1), 22, fill=bg, outline=WHITE, width=6); d.text((L.width / 2, 14), s, font=f, fill=col, anchor='ma', direction='rtl')
    return L
LBL = {'l': label('הַלּוֹחֲמִים'), 'h': label('הַחֲרֵדִים'), 'b': label('בְּרִית הַמְּשָׁרְתִים', 62)}
def heart_layer(split):
    L = Image.new('RGBA', (700, 640), (0, 0, 0, 0))
    for side in (-1, 1):
        half = Image.new('RGBA', (700, 640), (0, 0, 0, 0)); d = ImageDraw.Draw(half)
        pts = [(350 + 300 * math.sin(a) ** 3 * 1.0, 300 - (240 * math.cos(a) - 95 * math.cos(2 * a) - 40 * math.cos(3 * a) - 16 * math.cos(4 * a))) for a in np.linspace(0, 2 * math.pi, 120)]
        d.polygon(pts, fill=(225, 40, 60)); crayon(d, pts + [pts[0]], (160, 20, 40), 10, 2)
        m = Image.new('L', (700, 640), 0); md = ImageDraw.Draw(m)
        zig = [(350 + (18 if i % 2 else -18), 40 + i * 55) for i in range(12)]
        md.polygon(([(0, 0)] + zig + [(0, 640)]) if side < 0 else ([(700, 0)] + zig + [(700, 640)]), fill=255)
        half.putalpha(ImageChops.multiply(half.getchannel('A'), m))
        L.alpha_composite(half.rotate(-side * 14 * split, center=(350, 600), resample=Image.BICUBIC), (int(side * 90 * split), int(40 * split)))
    return L

def flip(im_out, im_in, u):
    """storybook page turn: out page squeezes to the spine with shading, new page unfolds"""
    can = Image.new('RGBA', (W, H), (60, 50, 40, 255))
    if u < .5:
        k = 1 - u / .5; w = max(1, int(W * k)); pg = im_out.resize((w, H), Image.BILINEAR); can.alpha_composite(im_in.copy()); 
        sh = Image.new('RGBA', (w, H), (0, 0, 0, int(120 * (1 - k)))); pg.alpha_composite(sh); can.alpha_composite(pg, (W - w, 0))
    else:
        k = (u - .5) / .5; w = max(1, int(W * k)); can.alpha_composite(im_out.copy()); pg = im_in.resize((w, H), Image.BILINEAR)
        sh = Image.new('RGBA', (w, H), (0, 0, 0, int(120 * (1 - k)))); pg.alpha_composite(sh); can.alpha_composite(pg, (W - w, 0))
    return can

# ---------- scenes ----------
def stk_clip(im, k, t, cy=820, base=1.0, rot=-3, enter=.0):
    u = t - LS(k); p = bk((u - enter) / .45, 1.6)
    if p <= 0: return
    s = sticker(clipframe(k, u)); sc = base * (.25 + .75 * p) * (1 + .025 * beatpulse(t))
    place(im, s, W / 2, cy, sc, rot + 2 * math.sin(t * 3))
def scene(t):
    if t < LS(1): return cover(t)
    k = min(14, int((t - L0) / BAR) + 1); u = t - LS(k)
    f = SCENES[k](t, k, u)
    # transitions: storybook->storybook = page turn; anything with pop = punch-in + flash
    nxt = k + 1
    if k < 14 and LS(nxt) - t < .22 and STORY.get(k) and STORY.get(nxt):
        uu = 1 - (LS(nxt) - t) / .44
        return flip(f, SCENES[nxt](LS(nxt) + .01, nxt, .01), max(0, uu))
    if u < .22 and k > 1 and STORY.get(k) and STORY.get(k - 1):
        uu = .5 + u / .44
        return flip(SCENES[k - 1](LS(k) - .01, k - 1, BAR - .01), f, uu)
    if u < .12 and not (STORY.get(k) and STORY.get(k - 1)):
        z = 1.08 - .08 * eo(u / .12); f = f.resize((int(W * z), int(H * z)), Image.BILINEAR).crop((int((W * z - W) / 2), int((H * z - H) / 2), int((W * z - W) / 2) + W, int((H * z - H) / 2) + H))
        f = Image.blend(f.convert('RGB'), Image.new('RGB', (W, H), WHITE), .5 * (1 - u / .12)).convert('RGBA')
    return f
def cover(t):
    im = paper(t); d = ImageDraw.Draw(im)
    p = bk(t / .6)
    lay = Image.new('RGBA', (W, 520), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    ld.text((W / 2 + 8, 18), 'שָׁלֵו', font=F('RubikBubbles.ttf', 230), fill=(255, 196, 60), anchor='ma', direction='rtl')
    ld.text((W / 2, 10), 'שָׁלֵו', font=F('RubikBubbles.ttf', 230), fill=INK, anchor='ma', direction='rtl')
    ld.text((W / 2 + 6, 276), 'הַמְעַרְבֵּב', font=F('RubikBubbles.ttf', 190), fill=(255, 196, 60), anchor='ma', direction='rtl')
    ld.text((W / 2, 270), 'הַמְעַרְבֵּב', font=F('RubikBubbles.ttf', 190), fill=RED, anchor='ma', direction='rtl')
    place(im, lay, W / 2, 560, .4 + .6 * p, -4 * (1 - p))
    d.text((W / 2, 860), 'סִפּוּר מְצֻיָּר לְכָל הַמִּשְׁפָּחָה', font=F('SecularOne.ttf', 58), fill=(110, 100, 80), anchor='ma', direction='rtl')
    place(im, blender_layer(t, t * 2), W / 2, 1300, .9 * bk((t - .4) / .6), 4 * math.sin(t * 4))
    if t > LS(1) - .44:   # open the cover = page turn into L1
        return flip(im, SCENES[1](LS(1) + .01, 1, .01), (t - (LS(1) - .44)) / .44)
    return im
def s1(t, k, u):   # story: sticker + blender doodle pops on 'המערבב'
    im = paper(t); stk_clip(im, k, t, 780)
    if u > 1.3: place(im, blender_layer(t, t * 3), 900, 1270, .36 * bk((u - 1.3) / .4), 8)
    lyric_story(im, k, t); return im
def s2(t, k, u):   # pop: campaign
    im = pop(t); stk_clip(im, k, t, 820, 1.0, 3)
    for ch, x, y, s, r, at in [('📣', 140, 360, 170, -10, .2), ('🗳️', 930, 1290, 170, 10, .5), ('📸', 940, 380, 150, 8, .8)]:
        place(im, emoji(ch, s), x, y, bk((u - at) / .35) * (1 + .08 * beatpulse(t)), r)
    popword(im, 'עָשָׂה וָואחַד', W / 2, 1330, 200, LS(k) + .1, t); popword(im, 'קַמְפֵּיין', W / 2, 1560, 230, LS(k) + .8, t, blk=RED); return im
def s3(t, k, u):   # story: uniforms + reserves
    im = paper(t); stk_clip(im, k, t, 780, 1, 2)
    place(im, emoji('🪖', 190), 170, 1210, bk((u - .6) / .35), -12); place(im, emoji('🎖️', 160), 910, 1200, bk((u - 1.4) / .35), 10)
    lyric_story(im, k, t); return im
def s4(t, k, u):   # pop red: before the elections
    im = pop(t, True); stk_clip(im, k, t, 760, 1.0, -2)
    popword(im, 'טִנֵּף עַל', W / 2, 1290, 190, LS(k) + .1, t); popword(im, 'מִשְׁתַּמְּטִים', W / 2, 1500, 210, LS(k) + .7, t, blk=(30, 30, 30))
    if u > 1.5:
        p = (u - 1.5) / .16; sc = 2.4 - 1.4 * eo(p)
        st = Image.new('RGBA', (760, 210), (0, 0, 0, 0)); sd = ImageDraw.Draw(st); sd.rounded_rectangle((6, 6, 754, 204), 26, outline=WHITE, width=12, fill=(20, 20, 20, 200))
        sd.text((380, 30), 'לִפְנֵי הַבְּחִירוֹת', font=F('kar', 150), fill=WHITE, anchor='ma', direction='rtl'); place(im, st, W / 2, 330, sc, -8)
    return im
def s5(t, k, u):   # pop: the blender arrives, Shalev sticker gets sucked in
    im = pop(t); p = bk(u / .5)
    s = sticker(clipframe(k, u)); sc = max(.0, .62 * (1 - eo((u - 1.4) / .9)))
    bl = blender_layer(t, t * (3 + 6 * eo((u - 1.0) / 1.5)), [(s.resize((int(s.width * .5), int(s.height * .5))), 0, 0, max(0., .9 * eo((u - 1.6) / .8)))] if u > 1.6 else [])
    place(im, bl, W / 2, 1150, 1.25 * p, 3 * math.sin(t * 6))
    if sc > .01: place(im, s, W / 2, 620 + 400 * eo((u - 1.4) / .9), sc, 30 * eo((u - 1.4) / .9))
    popword(im, 'שָׁלֵו שָׁלֵו', W / 2, 140, 200, LS(k) + .05, t); popword(im, 'הַמְעַרְבֵּב', W / 2, 1640, 220, LS(k) + 1.3, t, blk=RED, rot=-3); return im
def s6(t, k, u):   # story: 'עשה ואחד סיבוב' - the sticker does a full spin
    im = paper(t); uu = u - .3; a = 360 * eo(uu / 1.2) if uu > 0 else 0
    p = bk(u / .45, 1.6); sk = sticker(clipframe(k, u)); place(im, sk, W / 2, 800, .95 * (.25 + .75 * p), -a + 2 * math.sin(t * 3))
    place(im, emoji('🌀', 170), 160, 1240, bk((u - .2) / .35) * (1 + .1 * beatpulse(t)), -t * 120)
    place(im, emoji('🔄', 150), 920, 1230, bk((u - .5) / .35), t * 90)
    lyric_story(im, k, t, 1440, 130); return im
def s7(t, k, u):   # pop: labels drop into the blender (lines 7-8)
    im = pop(t); uu = t - LS(7)
    cont = []
    for key, at in [('l', .55), ('h', 1.5), ('b', LS(8) - LS(7) + .5)]:
        if uu > at + .8: cont.append((LBL[key], {'l': 0, 'h': 2.1, 'b': 4.2}[key], 120, .7))
    bl = blender_layer(t, t * 5, cont); place(im, bl, W / 2, 1180, 1.3, 2 * math.sin(t * 7))
    for key, at in [('l', .55), ('h', 1.5), ('b', LS(8) - LS(7) + .5)]:
        v = (uu - at) / .8
        if 0 < v <= 1: place(im, LBL[key], W / 2 + 120 * math.sin(v * 3), 380 + 640 * v ** 2, 1.2 - .5 * v, 200 * v)
    if k == 7: popword(im, 'עַל הַלּוֹחֲמִים,', W / 2, 90, 150, LS(7) + .05, t); popword(im, 'עַל הַחֲרֵדִים', W / 2, 270, 150, LS(7) + 1.2, t, blk=RED)
    else: popword(im, 'עַל בְּרִית הַמְּשָׁרְתִים', W / 2, 120, 150, LS(8) + .05, t, blk=RED)
    return im
def s9(t, k, u):   # pop: la la la CHAIR — the chair grows each time
    im = pop(t, k == 10); n = k - 8
    stk_clip(im, k, t, 640, .8, (-1) ** k * 4)
    for i in range(3):   # musical notes
        place(im, emoji('🎵', 110), 140 + i * 400, 1180 + 40 * math.sin(t * 5 + i), (1 + .15 * beatpulse(t)) * (u > .2 + i * .45), 10 * math.sin(t * 3 + i))
    hit = 3 * BEAT - .05; p = bk((u - hit) / .3, 2.4) if u > hit else 0
    prev = .55 + .3 * (n - 1)
    if p > 0 or n > 1: place(im, emoji('🪑', 300), W / 2, 1420, (prev if p == 0 else prev + .3 * p) * (1 + .05 * beatpulse(t)), 6 * math.sin(t * 4))
    popword(im, 'לָה לָה לָה', W / 2, 130, 170, LS(k) + .05, t)
    popword(im, 'כִּסֵּא', W / 2, 1640, 230, LS(k) + hit, t, blk=RED, rot=-4); return im
def s12(t, k, u):   # pop: dancing chairs
    im = pop(t, True)
    for i in range(7):
        a = t * 2 + i * .9; place(im, emoji('🪑', 220), W / 2 + 380 * math.cos(a), 960 + 520 * math.sin(a), (.8 + .2 * beatpulse(t)) * bk((u - i * .08) / .3), 25 * math.sin(t * 6 + i))
    place(im, emoji('🎶', 200), W / 2, 960, 1 + .2 * beatpulse(t), 0)
    popword(im, 'לָה לָה לָה לָה', W / 2, 820, 230, LS(k) + .05, t, blk=(30, 30, 30)); return im
def s13(t, k, u):   # story: Shalev spinning inside the crayon blender
    im = paper(t); s = sticker(clipframe(k, u)); s = s.resize((int(s.width * .45), int(s.height * .45)))
    place(im, blender_layer(t, t * 4, [(s, 0, 30, 1.0)]), W / 2, 830, 1.15 * bk(u / .5), 3 * math.sin(t * 5))
    lyric_story(im, k, t, 1430); return im
def s14(t, k, u):   # story: heart breaks
    im = paper(t); split = eo((u - 1.0) / .5) if u > 1.0 else 0
    place(im, heart_layer(split), W / 2, 820, bk(u / .4) * (1 + .05 * beatpulse(t) * (split == 0)), 0)
    lyric_story(im, k, t, 1400, 130)
    return im
SCENES = {1: s1, 2: s2, 3: s3, 4: s4, 5: s5, 6: s6, 7: s7, 8: s7, 9: s9, 10: s9, 11: s9, 12: s12, 13: s13, 14: s14}
STORY = {1: True, 3: True, 6: True, 13: True, 14: True}
_c3 = None
def clip3(t):
    u = t - C3; im = paper(t); d = ImageDraw.Draw(im)
    global _c3
    if _c3 is None: _c3 = sorted(os.listdir(P + 'end3/'))
    fr = Image.open(P + 'end3/' + _c3[max(0, min(len(_c3) - 1, int(u * FPS)))]).convert('RGB')
    place(im, sticker(fr, 18, 34), W / 2, 760, bk(u / .5, 1.5), -2 + 1.5 * math.sin(t * 2))
    place(im, emoji('😏', 150), 900, 1130, bk((u - 6.2) / .3), 10)
    for a, b, txt in C3SUB:
        if a <= u < b:
            f = F('SecularOne.ttf', 84); tw = d.textlength(txt, font=f, direction='rtl'); p = eo((u - a) / .2)
            lay = Image.new('RGBA', (int(tw) + 80, 150), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
            ld.rounded_rectangle((0, 0, lay.width - 1, 149), 26, fill=WHITE, outline=INK, width=6); ld.text((lay.width / 2, 18), txt, font=f, fill=INK, anchor='ma', direction='rtl')
            place(im, lay, W / 2, 1330 + 20 * (1 - p), .9 + .1 * p, 0)
    if u < .44: return flip(scene(C3 - .01), im, .5 + u / .88)
    return im
def backcover(t):
    u = t - END0; im = paper(t); d = ImageDraw.Draw(im)
    lay = Image.new('RGBA', (W, 400), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    ld.text((W / 2 + 8, 18), 'הַסּוֹף.', font=F('RubikBubbles.ttf', 260), fill=(255, 196, 60), anchor='ma', direction='rtl')
    ld.text((W / 2, 10), 'הַסּוֹף.', font=F('RubikBubbles.ttf', 260), fill=INK, anchor='ma', direction='rtl')
    place(im, lay, W / 2, 760, bk(u / .5), -3)
    d.text((W / 2, 1080), 'סִפּוּרוֹ שֶׁל שָׁלֵו הַמְעַרְבֵּב', font=F('SecularOne.ttf', 70), fill=(110, 100, 80, int(255 * eo((u - .5) / .5))), anchor='ma', direction='rtl')
    place(im, emoji('💔', 150), W / 2, 1280, bk((u - .8) / .4), 0)
    if u < .44: return flip(clip3(END0 - .01), im, .5 + u / .88)
    return im
_bf = {}
def brk(i, u):
    d = P + f'brk{i}/'
    if d not in _bf: _bf[d] = sorted(os.listdir(d))
    fr = Image.open(d + _bf[d][max(0, min(len(_bf[d]) - 1, int(u * FPS)))]).convert('RGB')
    T = BR[i][0] + u; im = pop(T, True)
    place(im, sticker(fr, 20), W / 2, 900, 1.12 * bk(u / .35, 1.5) * (1 + .015 * math.sin(u * 9)), (-2, 2)[i] + 1.5 * math.sin(u * 4))
    popword(im, 'שָׁלֵו, לִפְנֵי הַבְּחִירוֹת:', W / 2, 150, 150, BR[i][0] + .05, T, blk=(30, 30, 30), rot=-2)
    place(im, emoji('🎤', 190), (880, 190)[i], 1560, bk((u - .3) / .3), (12, -12)[i])
    SUB = [[(0, 1.95, 'אתה מקדם השתמטות'), (1.95, 3.6, 'יש ביני לבינך פער')], [(0, 1.15, 'זה מתחיל בקידום'), (1.15, 3.0, 'של השתמטות המונית')]][i]
    for a0, b0, txt in SUB:
        if a0 <= u < b0: popword(im, txt, W / 2, 1330, 150, BR[i][0] + a0, T, fill=WHITE, blk=(30, 30, 30))
    if u < .1: im = Image.blend(im.convert('RGB'), Image.new('RGB', (W, H), WHITE), .6 * (1 - u / .1)).convert('RGBA')
    return im
def frame(T):
    off = 0.
    for i, (at, _, a, b) in enumerate(BR):
        if T < at + off: break
        if T < at + off + (b - a): return brk(i, T - at - off).convert('RGB')
        off += b - a
    t = T - off
    im = backcover(t) if t >= END0 else (clip3(t) if t >= C3 else scene(t))
    return im.convert('RGB')

if __name__ == '__main__':
    prep()
    if len(sys.argv) > 1 and sys.argv[1] == 'stills':
        ts = [LS(5) + 1.5, LS(9) + 3.55 + 1.5]; ts = ts + [1.2]
        ims = [frame(x).resize((216, 384)) for x in ts]; sh = Image.new('RGB', (9 * 220, 2 * 388), WHITE)
        for i, x in enumerate(ims): sh.paste(x, ((i % 9) * 220, (i // 9) * 388))
        sh.save(SC + 'stills.jpg'); print(TOTAL); sys.exit()
    if 'mux' not in sys.argv:
     ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', P + 'v.mp4'], stdin=subprocess.PIPE)
     for i in range(int(round(TOTAL_V * FPS))): ff.stdin.write(frame(i / FPS).tobytes())
     ff.stdin.close(); ff.wait()
    ins = ['-i', SONG, '-i', V1, '-i', V2, '-i', V3, '-i', TAPE]; fl = []; mix = []
    cuts = [0.] + [at for at, *_ in BR] + [SONG_END]; off = 0.; src = {'v1': 1, 'v2': 2}
    for n in range(len(cuts) - 1):
        a, b = cuts[n], cuts[n + 1]; last = n == len(cuts) - 2
        fade = f'afade=t=out:st={b - a - (0.6 if last else 0.12):.3f}:d={0.6 if last else 0.12}'
        fl.append(f'[0:a]aformat=sample_rates=48000:channel_layouts=stereo,atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,volume=1.3,afade=t=in:d=0.04,{fade},adelay={int((a + off) * 1000)}:all=1[s{n}]'); mix.append(f'[s{n}]')
        if not last:
            at, sv, c0, c1 = BR[n]
            fl.append(f'[{src[sv]}:a]aformat=sample_rates=48000:channel_layouts=stereo,atrim={c0}:{c1},asetpts=PTS-STARTPTS,highpass=f=90,loudnorm=I=-13:TP=-1.5,afade=t=in:d=0.03,afade=t=out:st={c1 - c0 - .08:.3f}:d=0.08,adelay={int((at + off + .12) * 1000)}:all=1[v{n}]')
            fl.append(f'[4:a]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:0.9,volume=0.5,adelay={int((at + off - .25) * 1000)}:all=1[t{n}]'); mix += [f'[v{n}]', f'[t{n}]']
            off += c1 - c0
    fl.append(f'[3:a]aformat=sample_rates=48000:channel_layouts=stereo,highpass=f=90,loudnorm=I=-14:TP=-1.5,afade=t=in:d=0.05,adelay={int((C3 + DSUM) * 1000)}:all=1[c]'); mix.append('[c]')
    fl.append(f"{''.join(mix)}amix=inputs={len(mix)}:normalize=0,apad=whole_dur={TOTAL_V:.2f},atrim=0:{TOTAL_V:.2f}[a]")
    subprocess.run(['ffmpeg', '-v', 'error', '-y'] + ins + ['-filter_complex', ';'.join(fl), '-map', '[a]', P + 'a.wav'], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', P + 'v.mp4', '-i', P + 'a.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'slow', '-crf', '21', '-maxrate', '10M', '-bufsize', '20M', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-t', f'{TOTAL_V:.2f}', '-movflags', '+faststart', P + 'mux.mp4'], check=True)
    LN = glob.glob('/root/.claude/skills/synced/*/pro-video-editing/scripts/loudnorm.py')[0]
    subprocess.run(['python3', LN, P + 'mux.mp4', HERE + '/shalev-hamearbev.mp4', '--target', '-14'], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', HERE + '/shalev-hamearbev.mp4', '-vf', 'scale=720:1280:flags=lanczos', '-c:v', 'libx264', '-preset', 'slow', '-b:v', '1500k', '-maxrate', '2000k', '-bufsize', '4000k', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-level', '4.0', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', HERE + '/shalev-hamearbev-small.mp4'], check=True)
    print('done', TOTAL_V)
