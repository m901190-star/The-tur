"""English version of the Bar Dalia reel: user's cloned voice (en/vo_en_raw.wav), English on-screen text, NO logos.
Reuses make.py visuals; English time E is mapped piecewise-linearly onto the Hebrew final timeline T."""
import os, sys, subprocess, numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); EN = HERE + '/en/'
HE2EN = {'צפון בקעת הירדן': 'Northern Jordan Valley', 'בר־דליה': 'Bar Dalia', 'משפחת רוזנפלד': 'The Rosenfeld Family',
         'יונתן דויטש הי״ד': 'Yonatan Deutsch', 'נרצח בפיגוע בצומת מחולה': 'Killed in the Mehola Junction terror attack',
         'מעבר הבקעה': 'Valley Checkpoint', 'ממערב למחסום': 'West of the checkpoint', 'צפון השומרון': 'Northern Samaria',
         'בקעת הירדן': 'Jordan Valley', 'בולמת רצף טריטוריאלי': 'Creating a barrier', 'חוות בר דליה': 'Bar Dalia Farm',
         'תלמוד ירושלמי': 'Jerusalem Talmud'}
def tr(src):
    for k in sorted(HE2EN, key=len, reverse=True): src = src.replace("'" + k + "'", "'" + HE2EN[k] + "'")
    return src.replace("direction='rtl'", "direction='ltr'")
G = {'__file__': HERE + '/make.py', '__name__': 'make_en_base'}
exec(compile(tr(open(HERE + '/make.py').read().split("if __name__ == '__main__':")[0]), 'make.py', 'exec'), G)
import importlib.util as iu, types
for n, key in (('make_map', 'MAPM'), ('make_gemara', 'GEM')):
    m = types.ModuleType(n); m.__file__ = HERE + '/map/' + n + '.py'
    exec(compile(tr(open(m.__file__).read()).split("if __name__ == '__main__':")[0], m.__file__, 'exec'), m.__dict__); G[key] = m
_ML = G['MAPM'].label
def _lab(im, s, x, y, size, fill=(255, 255, 255), bg=(0x25, 0x66, 0xA2), anchor_x='c', alpha=1.):
    size = int(size * .85)
    if s == 'Valley Checkpoint': y -= 80
    tw = ImageDraw.Draw(im).textlength(s, font=G['F'](G['SEC'], size)) + 50
    if anchor_x == 'c': x = max(tw / 2 + 24, min(im.width - tw / 2 - 24, x))
    _ML(im, s, x, y, size, fill=fill, bg=bg, anchor_x=anchor_x, alpha=alpha)
G['MAPM'].label = _lab
W, H, FPS, BLUE, WHITE, F, KB, eo = G['W'], G['H'], G['FPS'], G['BLUE'], G['WHITE'], G['F'], G['KB'], G['eo']

# ---- tightened voice: phrase pieces (raw times) + pause after each ----
SEG = [(0.46,4.12,.45),(4.61,6.76,.08),(7.06,8.09,.08),(8.40,10.28,.10),(10.63,11.13,.08),(11.39,12.05,.50),(12.71,13.87,.12),(14.24,15.61,.06),
       (15.96,17.01,.06),(17.34,18.30,.15),(18.85,20.84,.12),(21.32,23.30,.55),(24.24,28.30,.12),(28.66,30.53,.10),(30.98,32.34,.45),(33.07,39.46,.06),
       (39.82,41.11,.10),(41.44,42.45,.50),(43.24,43.66,.10),(44.11,45.84,.08),(46.19,47.85,.10),(48.21,50.13,.10),(50.47,52.43,.08),(52.85,54.26,.08),
       (54.56,55.65,.05),(55.90,56.49,.10),(56.78,58.11,.50),(58.85,61.52,.12),(61.93,64.80,0)]
PAD, LEAD = .04, .25
ST = []; e = LEAD
for a, b, g in SEG: ST.append(e); e += (b - a) + 2 * PAD + g
VO_END_E = e; TOTAL_E = VO_END_E + 2.6
# anchors: Hebrew final T  <->  English segment start
ANC = [(0.0, 0.0), (0.05, ST[0]), (3.66, ST[1]), (7.8, ST[2]), (11.16, ST[6]), (17.55, ST[10]), (23.02, ST[12]), (29.46, ST[14]), (34.21, ST[15] + 3.2),
       (41.19, ST[18]), (44.91, ST[21]), (50.54, ST[24]), (54.5, ST[27]), (57.87, ST[28]), (62.5, VO_END_E), (65.1, TOTAL_E)]
def e2t(E): return float(np.interp(E, [b for a, b in ANC], [a for a, b in ANC]))
SUBG = [([0], 'A Jewish village from the Talmudic era is coming back to life.'), ([1], 'West of the Jordan Valley checkpoint'),
        ([2,3,4,5], 'stands a farm that tells a story of past, present and future.'), ([6,7,8], 'According to tradition, a small Jewish village called Bar Dalia'),
        ([9,10], 'once stood here, home to the Delaiah priestly course,'), ([11], 'which is also mentioned in the Talmud.'),
        ([12], 'After the terror attack at Mehola Junction in August 2024,'), ([13,14], 'in which Yonatan Deutsch was killed, the farm was established.'),
        ([15], 'The goal was to strengthen our presence in the area'), ([15], 'and create a barrier between villages in northern Samaria'),
        ([16,17], 'where terrorists operate and the Jordan Valley.'), ([18,19,20], 'Today, Uri and Ashchar Rosenfeld, together with their son Aniam,'),
        ([21], 'are building a pioneering farm here,'), ([22,23], 'with a vision of founding a beit midrash, a house of Torah study,'),
        ([24,25,26], 'that joins Torah and labor, spirit and soil.'), ([27], 'Today, the farm safeguards hundreds of dunams,'),
        ([28], 'working the land and breathing life into the area.')]
SUBS_E = [(ST[ix[0]], ST[ix[-1]] + SEG[ix[-1]][1] - SEG[ix[-1]][0] + 2 * PAD, s) for ix, s in SUBG]
SUBS_E[8] = (SUBS_E[8][0], SUBS_E[8][0] + 3.2, SUBS_E[8][2]); SUBS_E[9] = (SUBS_E[9][0] + 3.2, SUBS_E[9][1], SUBS_E[9][2])
def wrap(d, s, f, maxw):
    out, cur = [], ''
    for w in s.split():
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: out.append(cur); cur = w
    return out + [cur]
def subs(im, E, size=84):
    d = ImageDraw.Draw(im)
    for a, b, s in SUBS_E:
        if a - .05 <= E < b + .2:
            p = eo((E - a + .05) / .2); f = F(KB, size); lines = wrap(d, s, f, 940); lh = size * 1.0
            y0 = G['SUB_Y'] - (len(lines) - 1) * lh / 2 + 20 * (1 - p)
            for k, l in enumerate(lines):
                y = y0 + k * lh; d.text((W / 2 + 5, y + 5), l, font=f, fill=BLUE, anchor='ma'); d.text((W / 2, y), l, font=f, fill=WHITE, anchor='ma')
            return
def frame(E):
    T = e2t(E); f, kind = G['base4'](T); im = f.convert('RGBA')
    if kind != 'mem': im.alpha_composite(G['GRAD3'])
    if T < G['H_END']:
        if T < 4.3: G['label3'](im, T, .3, 4.3, 'Northern Jordan Valley')
    elif kind in ('normal', 'normal_land'):
        t = G['n2o'](T)
        for a, b, s_ in G['LABELS']:
            if s_ in ('The Rosenfeld Family',): G['label3'](im, t, a, b, s_)
        if 11.1 <= T < 17.6: G['label3'](im, T, 11.4, 17.6, 'Bar Dalia')
    if kind != 'mem': subs(im, E)
    if T < .4: im = Image.blend(Image.new('RGBA', (W, H), (0, 0, 0, 255)), im, T / .4)
    return im.convert('RGB')
def audio():
    parts = []; labs = []
    for i, ((a, b, g), s) in enumerate(zip(SEG, ST)):
        parts.append(f'[1:a]atrim={a - PAD:.3f}:{b + PAD:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={b - a + PAD:.3f}:d=0.03,adelay={int(s * 1000)}:all=1[p{i}]'); labs.append(f'[p{i}]')
    lo_a, lo_b = [float(np.interp(x, [a for a, b in ANC], [b for a, b in ANC])) for x in (22.6, 29.7)]; TT = TOTAL_E
    parts += [''.join(labs) + f'amix=inputs={len(SEG)}:normalize=0,highpass=f=70,acompressor=threshold=-20dB:ratio=2.5:attack=10:release=150,loudnorm=I=-16:TP=-1.5,aformat=sample_rates=48000:channel_layouts=stereo,apad=whole_dur={TT},asplit=2[v][k]',
              f"[2:a]aformat=sample_rates=48000:channel_layouts=stereo,aloop=loop=4:size={int(25.6*44100)},atrim=0:{TT},volume='if(between(t,{lo_a},{lo_b}),0.12,if(gt(t,{TT-2.6}),0.55,0.30))':eval=frame,afade=t=in:d=1,afade=t=out:st={TT-2}:d=2[m]",
              '[m][k]sidechaincompress=threshold=0.03:ratio=3:attack=20:release=350[md]', '[v][md]amix=inputs=2:normalize=0,alimiter=limit=0.95[a]']
    return ['-i', EN + 'vo_en2_raw.wav', '-i', HERE + '/../2026-11-reel-bustan-david/music.wav', '-filter_complex', ';'.join(parts)]
if __name__ == '__main__':
    G['prep']()
    if 'stills' in sys.argv:
        ts = [1.5, 5, 9, 14, 18, 21, 24, 27, 29.5, 32, 35, 38, 43, 48, 53, 59]
        ims = [frame(x).resize((180, 320)) for x in ts]; sh = Image.new('RGB', (8 * 184, 2 * 324), WHITE)
        for i, x in enumerate(ims): sh.paste(x, ((i % 8) * 184, (i // 8) * 324))
        sh.save(sys.argv[2]); print(TOTAL_E, ST); sys.exit()
    out = EN + 'main_en.mp4'
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-'] + audio() +
        ['-map', '0:v', '-map', '[a]', '-vf', 'scale=720:1280:flags=lanczos', '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-maxrate', '4M', '-bufsize', '8M',
         '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-ar', '48000', '-t', f'{TOTAL_E}', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    for i in range(int(round(TOTAL_E * FPS))): ff.stdin.write(frame(i / FPS).tobytes())
    ff.stdin.close(); ff.wait(); print('done', TOTAL_E)
