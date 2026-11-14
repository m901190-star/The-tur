"""Animated map beat for Bar Dalia (9:16): tinted map, camera push to 'מעבר הבקעה', pin drop + pulses, westward arrow to the farm,
then a 'blocking' beat (farm sits between north-Samaria villages and the valley). Schematic, not a precise survey map."""
import os, sys, math, glob, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance
HERE = os.path.dirname(os.path.abspath(__file__))
KB = glob.glob('/root/.claude/skills/synced/*/pro-video-editing/assets/fonts/Karantina-Bold.ttf')[0]
SEC = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/shalev/fonts/SecularOne.ttf'
W, H, FPS = 1080, 1920, 30; NAVY = (0x17, 0x40, 0x68); BLUE = (0x25, 0x66, 0xA2); LB = (0x27, 0xA4, 0xD1); ICE = (0xE8, 0xF2, 0xF8); WHITE = (255, 255, 255); GOLD = (240, 200, 90)
def F(p, s): return ImageFont.truetype(p, s, layout_engine=ImageFont.Layout.RAQM)
def eo(x): x = max(0., min(1., x)); return 1 - (1 - x) ** 3
def bk(x, s=2.0): x = max(0., min(1., x)); x -= 1; return x * x * ((s + 1) * x + s) + 1
def ss(x): x = max(0., min(1., x)); return x * x * (3 - 2 * x)
# --- stylised base map (navy blueprint) ---
src = Image.open(HERE + '/source-map.jpg').convert('RGB')
_sd = ImageDraw.Draw(src); _bg = (244, 240, 233)
_sd.ellipse((637 - 46, 968 - 112, 637 + 46, 968 + 4), fill=_bg); _sd.rectangle((688, 895, 915, 945), fill=_bg)
_sd.line((600, 860, 645, 975), fill=(160, 175, 205), width=7)
g = ImageOps.autocontrast(ImageOps.grayscale(src), cutoff=1)
base = ImageOps.colorize(g, black=(8, 22, 40), mid=(23, 64, 104), white=(46, 102, 150))
a = np.asarray(src).astype(np.int16)                      # keep roads (blue-grey) as light lines, water/green as soft tint
road = ((a[..., 2] - a[..., 0] > 18) & (a[..., 2] > 150)).astype(np.uint8) * 255
green = ((a[..., 1] - a[..., 0] > 14) & (a[..., 1] > 200)).astype(np.uint8) * 255
bm = base.convert('RGBA')
bm.alpha_composite(Image.new('RGBA', bm.size, (39, 164, 209, 70)), (0, 0)) if False else None
gl = Image.new('RGBA', bm.size, (40, 120, 110, 0)); gl.putalpha(Image.fromarray(green).filter(ImageFilter.GaussianBlur(2)).point(lambda v: int(v * .45))); bm.alpha_composite(gl)
rl = Image.new('RGBA', bm.size, ICE + (0,)); rl.putalpha(Image.fromarray(road).filter(ImageFilter.GaussianBlur(.8)).point(lambda v: int(v * .85))); bm.alpha_composite(rl)
# grid
gd = ImageDraw.Draw(bm)
for x in range(0, bm.width, 60): gd.line((x, 0, x, bm.height), fill=(232, 242, 248, 14))
for y in range(0, bm.height, 60): gd.line((0, y, bm.width, y), fill=(232, 242, 248, 14))
# hide the original red pin (we draw our own)
PX, PY = 637, 968            # checkpoint pin tip in source coords
S = 1.5; MAP = bm.resize((int(bm.width * S), int(bm.height * S)), Image.LANCZOS)
P = (PX * S, PY * S); FARM = ((PX - 200) * S, (PY - 20) * S)   # schematic: west of the checkpoint
def cam(t):
    k = ss(t / 2.2) if t < 4.6 else 1.0
    z = 1.0 + .45 * k if t < 4.6 else 1.45 - .35 * ss((t - 4.6) / 1.2)
    cx = (MAP.width / 2) * (1 - k) + (P[0] - 120 * k) * k if t < 4.6 else P[0] - 120 - 60 * ss((t - 4.6) / 1.2)
    cy = (MAP.height / 2) * (1 - k) + P[1] * k if t < 4.6 else P[1]
    return cx, cy, z
def to_screen(pt, c):
    cx, cy, z = c; return W / 2 + (pt[0] - cx) * z / 1.0 * (W / (MAP.width * .0 + W)) * 1, H / 2 + (pt[1] - cy) * z
def view(c):
    cx, cy, z = c; w, h = W / z, H / z
    x0, y0 = cx - w / 2, cy - h / 2
    fr = MAP.crop((int(x0), int(y0), int(x0 + w), int(y0 + h))).resize((W, H), Image.BILINEAR)
    return fr
def pin(sz):
    L = Image.new('RGBA', (sz, int(sz * 1.4)), (0, 0, 0, 0)); d = ImageDraw.Draw(L); r = sz / 2
    d.ellipse((0, 0, sz - 1, sz - 1), fill=WHITE); d.polygon([(sz * .12, r * 1.25), (sz * .88, r * 1.25), (r, L.height - 1)], fill=WHITE)
    d.ellipse((r - sz * .22, r - sz * .22, r + sz * .22, r + sz * .22), fill=BLUE); return L
PIN = pin(92)
def label(im, s, x, y, size, fill=WHITE, bg=BLUE, anchor_x='c', alpha=1.):
    d = ImageDraw.Draw(im); f = F(SEC, size); tw = d.textlength(s, font=f, direction='rtl')
    L = Image.new('RGBA', (int(tw) + 50, size + 34), (0, 0, 0, 0)); ld = ImageDraw.Draw(L); ld.rounded_rectangle((0, 0, L.width - 1, L.height - 1), 14, fill=bg); ld.text((L.width / 2, 10), s, font=f, fill=fill, anchor='ma', direction='rtl')
    L.putalpha(L.getchannel('A').point(lambda v: int(v * alpha)))
    xx = x - L.width / 2 if anchor_x == 'c' else (x - L.width if anchor_x == 'r' else x); im.alpha_composite(L, (int(xx), int(y)))
def frame(t):
    c = cam(t); im = view(c).convert('RGBA'); d = ImageDraw.Draw(im)
    def sp(pt): return (W / 2 + (pt[0] - c[0]) * c[2], H / 2 + (pt[1] - c[1]) * c[2])
    p = sp(P); f = sp(FARM)
    # pulses
    if t > 1.1:
        for k in range(3):
            u = ((t - 1.1) - k * .5) % 1.5
            if u < 1.2: r = 20 + 160 * eo(u / 1.2); d.ellipse((p[0] - r, p[1] - r * .5, p[0] + r, p[1] + r * .5), outline=(232, 242, 248, int(200 * (1 - u / 1.2))), width=4)
    # pin drop
    if t > .7:
        k = bk((t - .7) / .5, 2.4); im.alpha_composite(PIN, (int(p[0] - PIN.width / 2), int(p[1] - PIN.height - 260 * (1 - k))))
        label(im, 'מעבר הבקעה', min(p[0], W - 170), p[1] - 210, 54, alpha=eo((t - 1.0) / .4))
    # westward arrow to the farm
    if t > 2.0:
        k = eo((t - 2.0) / .9); x1 = p[0] - 30; x2 = x1 + (f[0] - x1) * k; y1 = p[1] - 40; y2 = y1 + (f[1] - 40 - y1) * k
        glow = Image.new('RGBA', (W, H), (0, 0, 0, 0)); gg = ImageDraw.Draw(glow); gg.line((x1, y1, x2, y2), fill=GOLD + (200,), width=18); im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(10)))
        d.line((x1, y1, x2, y2), fill=GOLD, width=9)
        if k > .95:
            ang = math.atan2(y2 - y1, x2 - x1); L = 34
            d.polygon([(x2 + 10 * math.cos(ang), y2 + 10 * math.sin(ang)), (x2 - L * math.cos(ang - .5), y2 - L * math.sin(ang - .5)), (x2 - L * math.cos(ang + .5), y2 - L * math.sin(ang + .5))], fill=GOLD)
        label(im, 'ממערב למחסום', (x1 + x2) / 2, y1 + 40, 44, fill=NAVY, bg=GOLD, alpha=eo((t - 2.4) / .4))
    # farm marker
    if t > 2.9:
        k = bk((t - 2.9) / .45, 2.6); r = 26 * k
        d.ellipse((f[0] - r - 10, f[1] - 40 - r - 10, f[0] + r + 10, f[1] - 40 + r + 10), fill=(240, 200, 90, 90)); d.ellipse((f[0] - r, f[1] - 40 - r, f[0] + r, f[1] - 40 + r), fill=GOLD)
    # blocking beat: villages (west) | farm | valley (east)
    if t > 4.6:
        u = t - 4.6; k = eo(u / .6)
        wl = Image.new('RGBA', (W, H), (0, 0, 0, 0)); wd = ImageDraw.Draw(wl)
        wd.rectangle((0, 0, f[0] - 120, H), fill=(20, 20, 30, int(70 * k))); wl = wl; im.alpha_composite(wl)
        label(im, 'צפון השומרון', max(150, (f[0] - 120) / 2), 520, 52, bg=(30, 40, 60), alpha=k)
        label(im, 'בקעת הירדן', min(W - 150, (p[0] + W) / 2 + 40), 520, 52, bg=(30, 40, 60), alpha=k)
        # barrier: thick vertical bar through the farm
        h = 520 * eo((u - .4) / .6); bx = f[0]
        glow = Image.new('RGBA', (W, H), (0, 0, 0, 0)); gg = ImageDraw.Draw(glow); gg.rounded_rectangle((bx - 14, f[1] - 40 - h / 2, bx + 14, f[1] - 40 + h / 2), 14, fill=(240, 200, 90, 200)); im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(14)))
        d.rounded_rectangle((bx - 8, f[1] - 40 - h / 2, bx + 8, f[1] - 40 + h / 2), 8, fill=GOLD)
        if u > 1.1:
            for s_, yy in [(-1, f[1] - 260), (1, f[1] + 180)]:
                a2 = eo((u - 1.1) / .4); xL = bx - 220 + 120 * a2; d.line((bx - 260, yy, xL, yy), fill=(232, 242, 248), width=6); d.polygon([(xL + 14, yy), (xL - 10, yy - 14), (xL - 10, yy + 14)], fill=(232, 242, 248))
                d.line((bx - 40, yy - 22, bx - 6, yy + 22), fill=(220, 60, 60), width=8); d.line((bx - 40, yy + 22, bx - 6, yy - 22), fill=(220, 60, 60), width=8)
            label(im, 'בולמת רצף טריטוריאלי', W / 2, f[1] + 320, 60, fill=NAVY, bg=GOLD, alpha=eo((u - 1.5) / .4))
    if t > 3.1: label(im, 'חוות בר דליה', f[0], f[1] - 160, 62, fill=NAVY, bg=WHITE, alpha=eo((t - 3.1) / .4))
    return im.convert('RGB')
if __name__ == '__main__':
    T = 8.0
    if 'stills' in sys.argv:
        ims = [frame(x).resize((216, 384)) for x in [.3, 1.5, 3.6, 5.5, 7.5]]; sh = Image.new('RGB', (5 * 220, 384), WHITE)
        for i, x in enumerate(ims): sh.paste(x, (i * 220, 0))
        sh.save(HERE + '/map-stills.jpg'); sys.exit()
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-vf', 'scale=720:1280', '-c:v', 'libx264', '-crf', '21', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', HERE + '/map-preview.mp4'], stdin=subprocess.PIPE)
    for i in range(int(T * FPS)): ff.stdin.write(frame(i / FPS).tobytes())
    ff.stdin.close(); ff.wait(); print('done')
