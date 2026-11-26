"""Yesha reel 9:16 - Rosh Chodesh prayer at Oz VeGaon (photos only). Yesha style: white logo, Karantina w/ blue offset shadow, blue labels, no '!'.
Music: instrumental Splice loop already licensed for the Bustan David reel (no singing)."""
import os, glob, subprocess, math
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
HERE = os.path.dirname(os.path.abspath(__file__)); PH = HERE + '/photos/'
KB = glob.glob('/root/.claude/skills/synced/*/pro-video-editing/assets/fonts/Karantina-Bold.ttf')[0]
SEC = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/shalev/fonts/SecularOne.ttf'
LOGO = HERE + '/../../clients/yesha/logo_white.png'; MUSIC = HERE + '/../2026-11-reel-bustan-david/music.wav'
OUT = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/tefila/'; os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 1920, 30; BLUE = (0x25, 0x66, 0xA2); WHITE = (255, 255, 255)
# (photo, dur, pan from->to as fraction of horizontal travel, zoom from->to)
SHOTS = [('p1', 3.2, (.5, .5), (1.0, 1.10)), ('p2', 2.8, (.15, .55), (1.05, 1.05)), ('p6', 2.6, (.75, .35), (1.05, 1.08)),
         ('p3', 2.8, (.20, .60), (1.04, 1.04)), ('p4', 2.8, (.30, .70), (1.0, 1.04)), ('p5', 3.4, (.20, .45), (1.0, 1.08))]
TOTAL = sum(d for _, d, _, _ in SHOTS); XF = .35
def F(p, s): return ImageFont.truetype(p, s, layout_engine=ImageFont.Layout.RAQM)
def eo(x): x = max(0., min(1., x)); return 1 - (1 - x) ** 3
_img = {}
def img(n):
    if n not in _img:
        im = Image.open(PH + n + '.jpg').convert('RGB'); s = H * 1.12 / im.height; im = im.resize((int(im.width * s), int(H * 1.12)), Image.LANCZOS)
        _img[n] = ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(1.08)).enhance(1.04)
    return _img[n]
def shot(i, u):
    n, d, (p0, p1), (z0, z1) = SHOTS[i]; k = u / d; k = k * k * (3 - 2 * k); im = img(n); z = z0 + (z1 - z0) * k
    cw, ch = int(W / z * 1.0), int(H / z); cw = min(cw, im.width); ch = min(ch, im.height)
    px = p0 + (p1 - p0) * k; x0 = int((im.width - cw) * px); y0 = int((im.height - ch) * .5)
    return im.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.BILINEAR)
GRAD = Image.new('RGBA', (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(GRAD)
for y in range(H): gd.line((0, y, W, y), fill=(5, 14, 28, int(200 * max(0, (y - H * .5) / (H * .5)) ** 1.3) + int(80 * max(0, (H * .12 - y) / (H * .12)))))
LG = Image.open(LOGO).convert('RGBA'); LG = LG.crop(LG.getchannel('A').getbbox()); LG = LG.resize((170, int(170 * LG.height / LG.width)), Image.LANCZOS)
def headline(im, s, y, size, p):
    if p <= 0: return
    lay = Image.new('RGBA', (W, size + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); f = F(KB, size)
    d.text((W / 2 + 6, 6), s, font=f, fill=BLUE, anchor='ma', direction='rtl'); d.text((W / 2, 0), s, font=f, fill=WHITE, anchor='ma', direction='rtl')
    lay.putalpha(lay.getchannel('A').point(lambda v: int(v * min(1, p)))); im.alpha_composite(lay, (0, int(y + 30 * (1 - eo(p)))))
def label(im, s, y, size, p):
    if p <= 0: return
    d = ImageDraw.Draw(im); f = F(SEC, size); tw = d.textlength(s, font=f, direction='rtl')
    lay = Image.new('RGBA', (int(tw) + 60, size + 36), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay); ld.rounded_rectangle((0, 0, lay.width - 1, lay.height - 1), 14, fill=BLUE)
    ld.text((lay.width / 2, 12), s, font=f, fill=WHITE, anchor='ma', direction='rtl'); lay.putalpha(lay.getchannel('A').point(lambda v: int(v * min(1, p))))
    im.alpha_composite(lay, (int(W / 2 - lay.width / 2), int(y + 20 * (1 - eo(p)))))
def frame(t):
    acc = 0
    for i, (_, d, _, _) in enumerate(SHOTS):
        if t < acc + d or i == len(SHOTS) - 1:
            f = shot(i, min(d, t - acc))
            if i + 1 < len(SHOTS) and acc + d - t < XF: f = Image.blend(f, shot(i + 1, 0), 1 - (acc + d - t) / XF)
            break
        acc += d
    im = f.convert('RGBA'); im.alpha_composite(GRAD)
    e = TOTAL - 4.6   # ending block
    if t < e:
        label(im, 'ברגע זה · עוז וגאו״ן', 300, 54, (t - .3) / .4)
        headline(im, 'תפילת ראש חודש', 1270, 170, (t - .5) / .4); headline(im, 'מרגשת', 1440, 170, (t - .8) / .4)
        p = (t - 1.6) / .5; d = ImageDraw.Draw(im)
        if p > 0:
            for k, l in enumerate(['ע״י ישיבת מקור חיים', 'ובית מדרש להתחדשות']):
                ff = F(SEC, 56); d.text((W / 2, 1640 + k * 72), l, font=ff, fill=(255, 255, 255, int(255 * min(1, p))), anchor='ma', direction='rtl')
        if t > e - .4: im = Image.blend(im, f.convert('RGBA'), (t - (e - .4)) / .4)
    else:
        u = t - e; headline(im, 'יהי רצון שיתקבלו', 1250, 130, u / .4); headline(im, 'תפילותינו לטובה', 1385, 130, (u - .3) / .4)
        label(im, 'חודש טוב', 1580, 72, (u - 1.0) / .4)
    im.alpha_composite(LG, (W - 60 - LG.width, 70))
    if t < .4: im = Image.blend(Image.new('RGBA', (W, H), (0, 0, 0, 255)), im, t / .4)
    return im.convert('RGB')
if __name__ == '__main__':
    import sys
    if 'stills' in sys.argv:
        ims = [frame(x).resize((216, 384)) for x in [1.0, 3.5, 6.5, 9.0, 13.5, 16.5]]; sh = Image.new('RGB', (6 * 220, 384), WHITE)
        for i, x in enumerate(ims): sh.paste(x, (i * 220, 0))
        sh.save(OUT + 'stills.jpg'); print(TOTAL); sys.exit()
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', MUSIC,
        '-filter_complex', f'[1:a]atrim=0:{TOTAL},afade=t=in:d=0.8,afade=t=out:st={TOTAL - 1.8}:d=1.8,loudnorm=I=-15:TP=-1.5[a]', '-map', '0:v', '-map', '[a]',
        '-c:v', 'libx264', '-preset', 'slow', '-crf', '21', '-pix_fmt', 'yuv420p', '-vf', 'scale=720:1280:flags=lanczos', '-c:a', 'aac', '-b:a', '160k', '-t', f'{TOTAL}', '-movflags', '+faststart', HERE + '/yesha-rosh-chodesh.mp4'], stdin=subprocess.PIPE)
    for i in range(int(round(TOTAL * FPS))): ff.stdin.write(frame(i / FPS).tobytes())
    ff.stdin.close(); ff.wait(); print('done', TOTAL)
