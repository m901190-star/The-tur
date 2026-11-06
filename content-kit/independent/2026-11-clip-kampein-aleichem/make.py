"""'הֵבָאנוּ קַמְפֵּין עֲלֵיכֶם' - satirical storybook+pop clip (same engine/style as 'שָׁלֵו הַמְעַרְבֵּב'). No logo of ours.
Real footage/photos only (cut-out stickers); parody slogans are shown being scribbled over the real one, never as a genuine ad.
Song lines found with Whisper on the beat grid (71.8 bpm)."""
import os, sys, math, glob, subprocess, importlib.util
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
HERE = os.path.dirname(os.path.abspath(__file__)); MAT = HERE + '/materials/'; STK = HERE + '/stickers/'
spec = importlib.util.spec_from_file_location('sm', HERE + '/../2026-11-clip-shalev-song/make.py'); sm = importlib.util.module_from_spec(spec); spec.loader.exec_module(sm)
F, eo, bk, place, emoji, crayon, paper, pop, popword, flip, sticker = sm.F, sm.eo, sm.bk, sm.place, sm.emoji, sm.crayon, sm.paper, sm.pop, sm.popword, sm.flip, sm.sticker
W, H, FPS = 1080, 1920, 30; INK, RED, WHITE, BLACK = sm.INK, sm.RED, sm.WHITE, sm.BLACK
SC = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/kamp/'; P = SC + 'prep/'; os.makedirs(P, exist_ok=True)
SONG = HERE + '/song.wav'; BEAT = 60 / 71.8; BAR = 4 * BEAT
L = {1: 13.03, 2: 16.37, 3: 19.72, 4: 23.06, 5: 29.75, 6: 33.09, 7: 36.44}   # 7 = תאכלו
KAMP = [25.59, 26.43, 27.26]; EAT = [36.50, 37.30, 38.10]; HAT = 38.96; SONG_END = 42.0
BALLOT = (1.7, 8.6); SMOT = (L[5], 6.1); HOPE_D = 3.45; BACK_D = 3.8
TOTAL_V = SONG_END + SMOT[1] + HOPE_D + BACK_D
def beatpulse(t): return math.exp(-(((t - .522) / BEAT) % 1) * 6)
rng = np.random.default_rng(11)

# ---------- footage frames ----------
VIDS = {'ballot': (MAT + '12-video.mov', 0, BALLOT[1], 'crop=1080:1200:0:250,scale=680:756'),
        'smot': (MAT + '06-video.mov', 0, SMOT[1], 'crop=1500:1080:200:0,scale=860:619'),
        'hope': (MAT + '16-video.mov', 0, HOPE_D, 'crop=1600:1080:160:0,scale=900:608')}
def prep():
    for k, (src, s0, d, vf) in VIDS.items():
        o = P + k + '/'
        if os.path.exists(o + '0001.png'): continue
        os.makedirs(o, exist_ok=True); subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(s0), '-t', str(d + .1), '-i', src, '-vf', f'fps={FPS},{vf}', o + '%04d.png'], check=True)
_vf = {}
def vframe(k, u):
    d = P + k + '/'
    if d not in _vf: _vf[d] = sorted(os.listdir(d))
    fs = _vf[d]; return Image.open(d + fs[max(0, min(len(fs) - 1, int(u * FPS)))]).convert('RGB')

# ---------- stickers ----------
def diecut(im, out=16):
    """cut-out sticker: thick white outline + soft shadow"""
    im = im.convert('RGBA'); pad = out + 30; b = Image.new('RGBA', (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0)); b.alpha_composite(im, (pad, pad))
    a = b.getchannel('A').point(lambda v: 255 if v > 60 else 0).filter(ImageFilter.MaxFilter(2 * (out // 2) + 1)).filter(ImageFilter.MaxFilter(2 * (out // 2) + 1)).filter(ImageFilter.GaussianBlur(1.2))
    wl = Image.new('RGBA', b.size, (255, 255, 255, 0)); wl.putalpha(a)
    sh = Image.new('RGBA', b.size, (0, 0, 0, 0)); sh.putalpha(a.point(lambda v: v * .35).filter(ImageFilter.GaussianBlur(10)))
    o = Image.new('RGBA', b.size, (0, 0, 0, 0)); o.alpha_composite(sh, (6, 12)); o.alpha_composite(wl); o.alpha_composite(b); return o
def fitw(im, w): return im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)
def fith(im, h): return im.resize((int(im.width * h / im.height), h), Image.LANCZOS)
HEADS = {k: diecut(fith(Image.open(STK + k + '.png'), 330)) for k in ['bennett', 'lapid', 'eisenkot', 'shalev', 'liberman', 'golan']}
NAMES = {'bennett': 'נַפְתָּלִי בֶּנֶט', 'lapid': 'יָאִיר לַפִּיד', 'eisenkot': 'גָּדִי אַיְזֶנְקוֹט', 'shalev': 'יוֹנָתָן שָׁלֵו', 'liberman': 'אֲבִיגְדוֹר לִיבֶּרְמַן', 'golan': 'יָאִיר גּוֹלָן'}
ORDER = ['bennett', 'lapid', 'eisenkot', 'shalev', 'liberman', 'golan']
def poster(path, crop=None, w=820, border=14):
    im = Image.open(MAT + path).convert('RGB')
    if crop: im = im.crop(crop)
    return sticker(fitw(im, w), border, 18)
POST = {'mahapecha': poster('02-bennett-mahapchat-hamesharetim.jpg', None, 900), 'navtiach': poster('13-bennett-navtiach-letaken.png', (300, 150, 1800, 520), 900),
        'neshaker': poster('14-parody-beyachad-neshaker.png', (300, 150, 1800, 520), 900), 'nochel': poster('15-parody-nochel-nishar-nochel.png', (150, 150, 1850, 520), 900),
        'liberman': poster('01-liberman-100-0-banner.jpg', (335, 205, 805, 1010), 470), 'golan': poster('03-golan-5-banim-mesharetim.jpg', (205, 0, 452, 471), 420),
        'protest': poster('07-protest-banner-bismuth.jpg', (225, 20, 1320, 545), 760), 'down': poster('08-liberman-banner-coming-down.jpg', (255, 220, 865, 1010), 520),
        'tv09': poster('09-tv-hamahapach-shel-liberman.jpg', (0, 0, 1320, 900), 860)}
def card(k):
    C = Image.new('RGBA', (460, 640), (0, 0, 0, 0)); d = ImageDraw.Draw(C)
    d.rounded_rectangle((8, 8, 452, 632), 34, fill=(255, 252, 240), outline=INK, width=7)
    d.rounded_rectangle((26, 26, 434, 380), 24, fill=(120, 190, 235))
    for i in range(0, 460, 46): d.line((i, 26, i + 140, 380), fill=(140, 205, 245), width=14)
    h = HEADS[k]; h2 = fith(h, 370) if h.width * 370 / h.height <= 430 else fitw(h, 430); C.alpha_composite(h2, (int(230 - h2.width / 2), int(392 - h2.height)))
    d = ImageDraw.Draw(C); nm = NAMES[k]; f = F('SecularOne.ttf', 50)
    while d.textlength(nm, font=f, direction='rtl') > 400: f = F('SecularOne.ttf', f.size - 2)
    d.text((230, 398), nm, font=f, fill=INK, anchor='ma', direction='rtl')
    d.text((230, 470), 'כּוֹחַ־עַל:', font=F('SecularOne.ttf', 30), fill=(120, 110, 90), anchor='ma', direction='rtl')
    d.text((230, 508), 'מַבְטִיחַ לְהִלָּחֵם בַּמִּשְׁתַּמְּטִים', font=F('SecularOne.ttf', 34), fill=RED, anchor='ma', direction='rtl')
    return C
CARDS = {k: card(k) for k in ORDER}
def stars(im, cx, cy, n, sc=1.):
    for i in range(5):
        if i < n: place(im, emoji('⭐', 52), cx + (i - 2) * 64 * sc, cy, sc, 0)
def stamp(txt, col, w=None, size=96):
    f = F('kar', size); tmp = ImageDraw.Draw(Image.new('RGBA', (1, 1))); tw = int(tmp.textlength(txt, font=f, direction='rtl')); w = w or tw + 70
    S = Image.new('RGBA', (w, size + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(S)
    d.rounded_rectangle((4, 4, w - 4, size + 36), 18, outline=col, width=9); d.text((w / 2, 6), txt, font=f, fill=col, anchor='ma', direction='rtl')
    m = Image.fromarray((np.random.default_rng(len(txt)).random((S.height, S.width)) > .12).astype('uint8') * 255)   # worn ink
    S.putalpha(ImageChops.multiply(S.getchannel('A'), m)); return S
ST = {'ok': stamp('✔ הִבְטִיחַ', (30, 150, 70)), 'no': stamp('✘ הֵפֵר', RED), 'sat': stamp('סָאטִירָה 😂'.replace(' 😂', ''), (120, 60, 200), size=70), 'expired': stamp('פָּג תּוֹקֶף', RED, size=110)}
def tape(im, x, y, rot):
    t = Image.new('RGBA', (150, 46), (255, 240, 170, 200)); place(im, t, x, y, 1, rot)
def subtitle(im, txt, y=1560, size=78):
    d = ImageDraw.Draw(im); f = F('SecularOne.ttf', size); tw = d.textlength(txt, font=f, direction='rtl')
    while tw > W - 120: f = F('SecularOne.ttf', f.size - 4); tw = d.textlength(txt, font=f, direction='rtl')
    lay = Image.new('RGBA', (int(tw) + 70, f.size + 54), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    ld.rounded_rectangle((0, 0, lay.width - 1, lay.height - 1), 24, fill=WHITE, outline=INK, width=6); ld.text((lay.width / 2, 16), txt, font=f, fill=INK, anchor='ma', direction='rtl')
    place(im, lay, W / 2, y, 1, 0)
def tv(fr):
    """drawn retro TV around a frame"""
    w, h = fr.size; T = Image.new('RGBA', (w + 110, h + 170), (0, 0, 0, 0)); d = ImageDraw.Draw(T)
    d.rounded_rectangle((0, 0, w + 109, h + 109), 46, fill=(200, 120, 70), outline=(110, 60, 30), width=9)
    m = Image.new('L', (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), 30, fill=255); T.paste(fr, (55, 55), m)
    d.line((w * .3, h + 105, w * .22, h + 165), fill=(110, 60, 30), width=14); d.line((w * .7 + 110, h + 105, w * .78 + 110, h + 165), fill=(110, 60, 30), width=14)
    d.line((w / 2 + 55, 0, w / 2 - 60, -1), fill=(0, 0, 0)); return T
def flipped_paper(t):
    im = paper(t); place(im, emoji('😎', 150), 930, 210, 1, 0); place(im, emoji('🌧️', 190), 240, 240, 1, 0); return im

# ---------- scenes (song time t) ----------
def s_cover(t):
    im = paper(t); p = bk(t / .6)
    lay = Image.new('RGBA', (W, 560), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    for txt, y, col, sz in [('הֵבָאנוּ', 0, INK, 190), ('קַמְפֵּין', 190, RED, 230), ('עֲלֵיכֶם', 410, INK, 150)]:
        ld.text((W / 2 + 7, y + 8), txt, font=F('RubikBubbles.ttf', sz), fill=(255, 196, 60), anchor='ma', direction='rtl'); ld.text((W / 2, y), txt, font=F('RubikBubbles.ttf', sz), fill=col, anchor='ma', direction='rtl')
    place(im, lay, W / 2, 640, .4 + .6 * p, -4 * (1 - p))
    ImageDraw.Draw(im).text((W / 2, 1000), 'סִפּוּר עַל שִׁשָּׁה חֲבֵרִים שֶׁהִבְטִיחוּ', font=F('SecularOne.ttf', 58), fill=(110, 100, 80), anchor='ma', direction='rtl')
    for ch, x, y, s, r, at in [('📣', 220, 1290, 230, -12, .3), ('🗳️', 860, 1300, 200, 10, .5), ('✨', 540, 1420, 120, 0, .7)]: place(im, emoji(ch, s), x, y, bk((t - at) / .35), r)
    return im
def s_ballot(t):
    u = t - BALLOT[0]; im = paper(t)
    popword(im, 'פֶּרֶק א׳: הַהַבְטָחָה', W / 2, 110, 120, BALLOT[0] + .1, t, blk=(30, 30, 30), rot=-2)
    place(im, tv(vframe('ballot', u).convert('RGBA')), W / 2, 820, bk(u / .5, 1.4), -1.5 + math.sin(t * 2))
    if u > 7.2: place(im, POST['mahapecha'], W / 2, 420, .78 * bk((u - 7.2) / .3, 2), -4)
    if u > 7.6: place(im, ST['ok'], 860, 560, bk((u - 7.6) / .25, 2.4), 12)
    for a, b, s in [(0, 3.0, 'זה יום גורלי לעתיד המדינה שלנו.'), (3.0, 6.0, 'אני קורא לכולם לצאת ולהצביע'), (6.0, 8.7, 'כדי להביא את מהפכת המשרתים.')]:
        if a <= u < b: subtitle(im, s, 1590)
    return im
def s_pre(t):   # glue & brush: the campaign wall gets ready
    u = t - (BALLOT[0] + BALLOT[1]); im = paper(t)
    popword(im, 'הַקַּמְפֵּיין מַתְחִיל', W / 2, 260, 170, BALLOT[0] + BALLOT[1] + .15, t, blk=RED, rot=-3)
    for ch, x, y, s, r, at in [('🪣', 330, 1050, 260, -8, .2), ('🖌️', 760, 980, 230, 25, .5), ('📣', 540, 1380, 220, 0, .8)]:
        place(im, emoji(ch, s), x, y + 10 * math.sin(t * 6 + x), bk((u - at) / .35) * (1 + .06 * beatpulse(t)), r + 6 * math.sin(t * 4))
    return im
def lyric_top(im, t, k, text=None, blk=None):
    popword(im, text or 'הֵבָאנוּ קַמְפֵּין עֲלֵיכֶם', W / 2, 80, 140, L[k] + .02, t, blk=blk)
def s_cards(t, k):
    u = t - L[k]; im = pop(t, k == 2); pair = ORDER[(k - 1) * 2:(k - 1) * 2 + 2]
    for i, key in enumerate(pair):
        at = .1 + i * .55; p = bk((u - at) / .45, 1.5); x = (720, 360)[i]; rot = (5, -5)[i] + 2 * math.sin(t * 3 + i)
        if p > 0:
            place(im, CARDS[key], x, 930, 1.08 * p, rot)
            ns = int(max(0, min(5, (u - at - .4) / .14)))
            if ns: stars(im, x, 1310, ns, .9)
            if u > at + 1.3: place(im, ST['ok'], x, 640, .7 * bk((u - at - 1.3) / .22, 2.4), rot * 2)
    for ch, x, y, s in [('📣', 120, 1560, 170), ('🔥', 950, 1580, 150)]: place(im, emoji(ch, s), x, y, (1 + .12 * beatpulse(t)) * bk((u - .3) / .3), 8 * math.sin(t * 4))
    lyric_top(im, t, k); popword(im, ['', 'פֶּרֶק א׳', 'פֶּרֶק א׳', 'פֶּרֶק א׳'][k] and '', W / 2, 0, 1, 1e9, t)
    return im
def s_wall(t):
    u = t - L[4]; im = paper(t)
    layout = [('mahapecha', 540, 470, .82, -3, .05), ('golan', 250, 980, .9, 5, .7), ('protest', 690, 1000, .78, -4, 1.4),
              ('liberman', 830, 820, .6, 7, KAMP[0] - L[4]), ('mahapecha', 300, 820, .5, -9, KAMP[1] - L[4]), ('golan', 560, 1250, .7, 3, KAMP[2] - L[4])]
    for key, x, y, sc, r, at in layout:
        if u > at:
            p = (u - at) / .18; s2 = sc * (1.8 - .8 * eo(p)); place(im, POST[key], x, y, s2, r); tape(im, x - 120 * sc, y - POST[key].height * sc / 2 + 10, r - 30); tape(im, x + 120 * sc, y - POST[key].height * sc / 2 + 10, r + 30)
            if p < 1.2: place(im, emoji('💥', 260), x, y, 1.3 * (1 - min(1, p)), 0)
    for i, at in enumerate(KAMP):
        popword(im, 'קַמְפֵּין!', (750, 330, 540)[i], (1500, 1560, 1680)[i], 170, at, t, blk=(RED, (30, 30, 30), (40, 110, 200))[i], rot=(-8, 6, -3)[i])
    if u > 5.0:   # everyone lined up on the soldiers' side
        v = u - 5.0; bar = Image.new('RGBA', (W, 520), (0, 0, 0, 0)); bd = ImageDraw.Draw(bar); bd.rounded_rectangle((20, 40, W - 20, 500), 40, fill=(70, 120, 60, 235), outline=WHITE, width=8)
        bd.text((W / 2, 50), 'צַד הַמְּשָׁרְתִים 🪖'.replace(' 🪖', ''), font=F('RubikBubbles.ttf', 90), fill=WHITE, anchor='ma', direction='rtl')
        place(im, bar, W / 2, 1640 + 300 * (1 - eo(v / .4)), 1, 0)
        for i, key in enumerate(ORDER):
            pv = bk((v - .2 - i * .1) / .3, 2); place(im, HEADS[key], 110 + i * 172, 1745 + 300 * (1 - eo(v / .4)), .5 * pv, (-1) ** i * 5)
        place(im, emoji('🪖', 120), 120, 1500 + 300 * (1 - eo(v / .4)), 1, -10)
    lyric_top(im, t, 4, 'הֵבָאנוּ קַמְפֵּין עֲלֵיכֶם' if u < 2.5 else 'קַמְפֵּין, קַמְפֵּין, קַמְפֵּין עֲלֵיכֶם', None if u < 2.5 else RED)
    return im
def s_morph(t):   # verse 2: the real slogan gets scribbled into the parodies
    u = t - L[5]; im = flipped_paper(t)
    popword(im, 'פֶּרֶק ב׳: אַחֲרֵי הַבְּחִירוֹת', W / 2, 250, 110, L[5] + .05, t, blk=(30, 30, 30), rot=2)
    seq = [('navtiach', 0), ('neshaker', 1.25), ('nochel', 2.35)]
    cur = [k for k, a in seq if u >= a][-1]; a0 = dict(seq)[cur]; p = eo((u - a0) / .25)
    place(im, POST[cur], W / 2, 860, .98 + .06 * (1 - p), -2 + 2 * (1 - p))
    for k, a in seq[1:]:   # marker scribble in the half second before each change
        if a - .45 < u < a + .05:
            q = (u - (a - .45)) / .5; d = ImageDraw.Draw(im); pts = [(150 + 780 * (i / 20), 860 + 50 * math.sin(i * 1.7)) for i in range(int(21 * q))]
            if len(pts) > 1: crayon(d, pts, RED, 18, 2); place(im, emoji('🖊️', 160), pts[-1][0], pts[-1][1] - 60, 1, -30)
    if u > 1.3: place(im, ST['sat'], 800, 1130, .9 * bk((u - 1.3) / .25), -10)
    place(im, HEADS['bennett'], 260, 1330, .75 * bk((u - .3) / .35), -6)
    if u > 2.4: place(im, ST['no'], 300, 1180, .8 * bk((u - 2.4) / .2, 2.4), -14)
    lyric_top(im, t, 5); return im
def s_liberman(t):
    u = t - L[6]; im = flipped_paper(t)
    if u < 1.0: place(im, POST['liberman'], W / 2, 900, 1.15, -2)
    elif u < 2.0:
        q = eo((u - 1.0) / .3); place(im, POST['liberman'], W / 2, 900 + 900 * q, 1.15 * (1 - .3 * q), -2 + 40 * q); place(im, POST['down'], W / 2, 860, .95 * q, 2)
        if u > 1.3: place(im, emoji('⬇️', 150), 820, 620, bk((u - 1.3) / .2), 0)
    else:
        place(im, POST['down'], 300, 700, .5, 6); place(im, tv(Image.open(MAT + '09-tv-hamahapach-shel-liberman.jpg').convert('RGB').resize((760, 742)).convert('RGBA')), W / 2 + 60, 1000, .9 * bk((u - 2.0) / .4, 1.6), -2)
        place(im, stamp('🔄 מַהְפָּךְ'.replace('🔄 ', ''), RED, size=100), 800, 1520, bk((u - 2.5) / .2, 2.4), -10); place(im, emoji('🔄', 150), 260, 1560, bk((u - 2.6) / .25), t * 120)
    lyric_top(im, t, 6); return im
def s_eat(t):   # the coalition table with the Haredim; hats get eaten
    u = t - L[7]; im = flipped_paper(t); d = ImageDraw.Draw(im)
    d.rounded_rectangle((40, 1240, W - 40, 1420), 30, fill=(190, 120, 70), outline=(110, 60, 30), width=8); d.rectangle((90, 1420, 130, 1700), fill=(150, 90, 50)); d.rectangle((W - 130, 1420, W - 90, 1700), fill=(150, 90, 50))
    d.text((W / 2, 1290), 'שֻׁלְחַן הַקּוֹאָלִיצְיָה עִם הַחֲרֵדִים', font=F('SecularOne.ttf', 52), fill=WHITE, anchor='ma', direction='rtl')
    place(im, emoji('🤝', 150), W / 2, 1110, 1 + .1 * beatpulse(t), 0); place(im, stamp('חֹק גִּיּוּס 🤫'.replace(' 🤫', ''), (30, 30, 30), size=60), 870, 1130, 1, 8); place(im, emoji('🤫', 110), 1000, 1050, 1, 0)
    bites = sum(1 for a in EAT if t >= a); gone = t >= HAT
    for i, key in enumerate(ORDER):
        x = 110 + i * 172; y = 1000 + (i % 2) * 40; place(im, HEADS[key], x, y, .52, (-1) ** i * 4)
        pl = Image.new('RGBA', (170, 60), (0, 0, 0, 0)); ImageDraw.Draw(pl).ellipse((0, 0, 169, 59), fill=WHITE, outline=(150, 150, 150), width=4); place(im, pl, x, 1225, 1, 0)
        if not gone:
            hat = emoji('🎩', 110).copy()
            if bites:   # bite marks: punch circles out of the hat
                m = hat.getchannel('A').copy(); md = ImageDraw.Draw(m)
                for b in range(bites): cx = hat.width - 10 - b * 26; md.ellipse((cx - 26, -20 + b * 18, cx + 26, 30 + b * 18), fill=0)
                hat.putalpha(m)
            place(im, hat, x, 1190, 1, 0)
        else: place(im, emoji('🍽️', 80), x, 1200, 1, 0)
    for a in EAT:
        if 0 <= t - a < .35:
            place(im, emoji('😋', 170), W / 2 + rng.normal(0, 200), 760, bk((t - a) / .15, 2.4), 0)
            for j in range(10): place(im, emoji('✨', 40), W / 2 + rng.normal(0, 380), 1180 + rng.normal(0, 60), 1, 0)
    for i, a in enumerate(EAT): popword(im, 'תֹּאכְלוּ', (780, 540, 300)[i], 200 + i * 150, 150, a, t, blk=(RED, (30, 30, 30), RED)[i], rot=(-6, 4, -3)[i])
    popword(im, 'תַּ\'כּוֹבַע 🎩'.replace(' 🎩', ''), W / 2, 640, 210, HAT, t, blk=(40, 110, 200), rot=-4)
    if t > HAT + .9:   # the tail: 'all a bluff'
        v = t - HAT - .9; popword(im, 'הַכֹּל חַרְטָה', W / 2, 1480, 200, HAT + .9, t, blk=RED, rot=-5)
        for i, key in enumerate(ORDER): place(im, emoji('❌', 70), 110 + i * 172, 900 + (i % 2) * 40, bk((v - i * .08) / .2, 2.4), 0)
    return im

def scene(t):
    if t < BALLOT[0]: s = s_cover(t)
    elif t < BALLOT[0] + BALLOT[1]: s = s_ballot(t)
    elif t < L[1]: s = s_pre(t)
    elif t < L[4]: s = s_cards(t, 1 if t < L[2] else 2 if t < L[3] else 3)
    elif t < L[5]: s = s_wall(t)
    elif t < L[6]: s = s_morph(t)
    elif t < L[7]: s = s_liberman(t)
    else: s = s_eat(t)
    # cuts: page turn between story pages; punch + flash into pop
    for b in [BALLOT[0], BALLOT[0] + BALLOT[1], L[1], L[2], L[3], L[4], L[6], L[7]]:
        if 0 <= t - b < .12:
            z = 1.07 - .07 * eo((t - b) / .12); s = s.resize((int(W * z), int(H * z)), Image.BILINEAR); x0 = (s.width - W) // 2; y0 = (s.height - H) // 2; s = s.crop((x0, y0, x0 + W, y0 + H))
            s = Image.blend(s.convert('RGB'), Image.new('RGB', (W, H), WHITE), .45 * (1 - (t - b) / .12)).convert('RGBA')
    return s
def s_smot(u):
    T = L[5]; im = pop(T + u, True)
    popword(im, 'מִישֶׁהוּ אָמַר אֶת זֶה מֵרֹאשׁ...', W / 2, 200, 120, 0.05, u, blk=(30, 30, 30), rot=-2)
    place(im, tv(vframe('smot', u).convert('RGBA')), W / 2, 860, bk(u / .45, 1.4), 1.5 * math.sin(u * 2))
    place(im, emoji('🔮', 190), 930, 1250, bk((u - .4) / .3) * (1 + .08 * math.sin(u * 8)), 0)
    for a, b, s in [(0, 2.75, 'השמאל ברגע נותן להם דף חלק,'), (2.75, 4.3, 'פוטר אותם מגיוס,'), (4.3, 6.2, 'ואני מקבל ממשלת שמאל')]:
        if a <= u < b: subtitle(im, s, 1560)
    if u < .1: im = Image.blend(im.convert('RGB'), Image.new('RGB', (W, H), WHITE), .6 * (1 - u / .1)).convert('RGBA')
    return im
def s_hope(u):
    im = flipped_paper(SONG_END + u)
    place(im, sticker(vframe('hope', u), 18, 30), W / 2, 820, bk(u / .45, 1.4), -2)
    for ch, x, y, s, r, at in [('📦', 170, 1240, 190, -10, .4), ('⭐', 760, 1250, 70, 0, .9), ('🛒', 920, 470, 150, 10, .6)]: place(im, emoji(ch, s), x, y, bk((u - at) / .3), r)
    place(im, stamp('-99%', RED, size=110), 800, 1360, bk((u - 1.2) / .2, 2.4), -12)
    for a, b, s in [(0, 1.9, 'הפכו אותי לתקוות שווא.'), (1.9, 3.5, 'תקווה מעלי אקספרס.')]:
        if a <= u < b: subtitle(im, s, 1600)
    if u < .1: im = Image.blend(im.convert('RGB'), Image.new('RGB', (W, H), WHITE), .5 * (1 - u / .1)).convert('RGBA')
    return im
def s_back(u):
    im = paper(SONG_END + 20 + u); d = ImageDraw.Draw(im)
    lay = Image.new('RGBA', (W, 460), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    for txt, y in [('הֵפֵרוּ אֶת כָּל', 0), ('הַהַבְטָחוֹת.', 200)]:
        ld.text((W / 2 + 7, y + 8), txt, font=F('RubikBubbles.ttf', 170), fill=(255, 196, 60), anchor='ma', direction='rtl'); ld.text((W / 2, y), txt, font=F('RubikBubbles.ttf', 170), fill=INK, anchor='ma', direction='rtl')
    place(im, lay, W / 2, 560, bk(u / .5), -2)
    cp = Image.new('RGBA', (900, 430), (0, 0, 0, 0)); cd = ImageDraw.Draw(cp); cd.rounded_rectangle((6, 6, 894, 424), 30, fill=(255, 250, 225))
    for x in range(20, 890, 34): cd.line((x, 6, x + 16, 6), fill=INK, width=6); cd.line((x, 424, x + 16, 424), fill=INK, width=6)
    for y in range(20, 420, 34): cd.line((6, y, 6, y + 16), fill=INK, width=6); cd.line((894, y, 894, y + 16), fill=INK, width=6)
    cd.text((450, 40), 'קוּפּוֹן הַבְטָחוֹת', font=F('SecularOne.ttf', 64), fill=INK, anchor='ma', direction='rtl')
    cd.text((450, 140), 'לְהִלָּחֵם בַּמִּשְׁתַּמְּטִים', font=F('SecularOne.ttf', 84), fill=RED, anchor='ma', direction='rtl')
    cd.text((450, 320), '* הַבְטָחוֹת תְּקֵפוֹת עַד לְמוֹצָאֵי הַבְּחִירוֹת', font=F('SecularOne.ttf', 40), fill=(90, 80, 70), anchor='ma', direction='rtl')
    place(im, cp, W / 2, 1150, bk((u - .5) / .45), 2); place(im, emoji('✂️', 110), 130, 950, bk((u - .8) / .3), -20)
    if u > 1.4: place(im, ST['expired'], 770, 1040, 1.6 - .6 * eo((u - 1.4) / .15), -14)
    if u > 2.2: d.text((W / 2, 1560), 'הַסּוֹף... עַד הַבְּחִירוֹת הַבָּאוֹת', font=F('SecularOne.ttf', 60), fill=(110, 100, 80, int(255 * eo((u - 2.2) / .4))), anchor='ma', direction='rtl'); place(im, emoji('😏', 90), W / 2, 1680, bk((u - 2.4) / .3), 0)
    return im
def frame(T):
    if T < L[5]: return scene(T).convert('RGB')
    if T < L[5] + SMOT[1]: return s_smot(T - L[5]).convert('RGB')
    t = T - SMOT[1]
    if t < SONG_END: return scene(t).convert('RGB')
    u = t - SONG_END
    if u < HOPE_D: return s_hope(u).convert('RGB')
    return s_back(u - HOPE_D).convert('RGB')

def build_audio(out):
    TT = f'{TOTAL_V:.2f}'; BN = HERE + '/../2026-11-reel-bennett-before-after/audio/'
    duck = f"volume='if(between(t,{BALLOT[0] - .1:.2f},{BALLOT[0] + BALLOT[1]:.2f}),0.3,1)':eval=frame"
    fl = [f'[0:a]aformat=sample_rates=48000:channel_layouts=stereo,loudnorm=I=-14:TP=-1.5,asplit=2[sa][sb]',
          f'[sa]atrim=0:{L[5]:.3f},asetpts=PTS-STARTPTS,{duck},afade=t=out:st={L[5] - .12:.3f}:d=0.12[s1]',
          f'[sb]atrim={L[5]:.3f}:{SONG_END},asetpts=PTS-STARTPTS,afade=t=in:d=0.04,afade=t=out:st={SONG_END - L[5] - .5:.3f}:d=0.5,adelay={int((L[5] + SMOT[1]) * 1000)}:all=1[s2]',
          f'[1:a]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:{BALLOT[1]},asetpts=PTS-STARTPTS,highpass=f=90,loudnorm=I=-13:TP=-1.5,adelay={int(BALLOT[0] * 1000)}:all=1[v1]',
          f'[2:a]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:{SMOT[1]},asetpts=PTS-STARTPTS,highpass=f=90,loudnorm=I=-13:TP=-1.5,afade=t=out:st={SMOT[1] - .1:.2f}:d=0.1,adelay={int((L[5] + .1) * 1000)}:all=1[v2]',
          f'[3:a]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:{HOPE_D},asetpts=PTS-STARTPTS,highpass=f=90,loudnorm=I=-13:TP=-1.5,adelay={int((SONG_END + SMOT[1]) * 1000)}:all=1[v3]',
          f'[4:a]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:0.9,volume=0.5,adelay={int((L[5] - .3) * 1000)}:all=1[x1]',
          f'[5:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=0.55,adelay={int((KAMP[0] - .05) * 1000)}:all=1[x2]',
          f'[6:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=0.7,adelay={int((SONG_END + SMOT[1] + HOPE_D + 1.4) * 1000)}:all=1[x3]',
          f"[s1][s2][v1][v2][v3][x1][x2][x3]amix=inputs=8:normalize=0,alimiter=limit=0.95,apad=whole_dur={TT},atrim=0:{TT}[a]"]
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', SONG, '-i', MAT + '12-video.mov', '-i', MAT + '06-video.mov', '-i', MAT + '16-video.mov', '-i', BN + 'tape_stop.wav', '-i', BN + 'whoosh_hit.wav', '-i', BN + 'sub_impact.wav',
                    '-filter_complex', ';'.join(fl), '-map', '[a]', out], check=True)

if __name__ == '__main__':
    prep()
    if 'stills' in sys.argv:
        ts = [1.0, 4.0, 9.6, 11.6, 15.5, 18.8, 22.3, 24.6, 27.0, 29.0, L[5] + 3.0, L[5] + 6.1 + 1.0, L[5] + 6.1 + 2.0, L[5] + 6.1 + 3.0, L[6] + 6.1 + .6, L[6] + 6.1 + 1.5, L[6] + 6.1 + 2.8, 37.6 + 6.1, 40.5 + 6.1, SONG_END + 6.1 + 2.5, SONG_END + 6.1 + HOPE_D + 3.0]
        ims = [frame(x).resize((216, 384)) for x in ts]; sh = Image.new('RGB', (11 * 220, 2 * 388), WHITE)
        for i, x in enumerate(ims): sh.paste(x, ((i % 11) * 220, (i // 11) * 388))
        sh.save(SC + 'stills.jpg'); print(TOTAL_V); sys.exit()
    if 'mux' not in sys.argv:
        ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', P + 'v.mp4'], stdin=subprocess.PIPE)
        for i in range(int(round(TOTAL_V * FPS))): ff.stdin.write(frame(i / FPS).tobytes())
        ff.stdin.close(); ff.wait()
    build_audio(P + 'a.wav')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', P + 'v.mp4', '-i', P + 'a.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'slow', '-b:v', '1800k', '-maxrate', '2400k', '-bufsize', '4800k', '-vf', 'scale=720:1280:flags=lanczos', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-c:a', 'aac', '-b:a', '160k', '-t', f'{TOTAL_V:.2f}', '-movflags', '+faststart', P + 'mux.mp4'], check=True)
    LN = glob.glob('/root/.claude/skills/synced/*/pro-video-editing/scripts/loudnorm.py')[0]
    subprocess.run(['python3', LN, P + 'mux.mp4', HERE + '/kampein-aleichem.mp4', '--target', '-14'], check=True)
    print('done', TOTAL_V)
