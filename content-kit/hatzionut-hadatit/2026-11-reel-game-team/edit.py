"""Assemble RZ game reel: 5 AI shots + game HUD overlays + client music. 720x1280, 30fps."""
import os, sys, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); G = HERE + '/gen/'
from hud import overlay
KB = HERE + '/../../fonts/HaimClassicv2FM-Bold.ttf'; RUB = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/fonts/Rubik-700.ttf'
SEC = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/shalev/fonts/SecularOne.ttf'
W, H, FPS = 720, 1280, 30; BW, BH = 1080, 1920; GOLD = (255, 205, 70)
def F(p, s): return ImageFont.truetype(p, s, layout_engine=ImageFont.Layout.RAQM)
def eo(x): x = max(0., min(1., x)); return 1 - (1 - x) ** 3
def frames(path, t0, dur):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(t0), '-t', str(dur), '-i', path, '-vf', f'scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
def select_layer(u):
    lay = Image.new('RGBA', (BW, BH)); od = ImageDraw.Draw(lay)
    for y in range(1150, BH): od.line((0, y, BW, y), fill=(8, 10, 16, int(230 * ((y - 1150) / 770) ** 1.1)))
    d = od; R = BW - 60
    d.text((R, 70), 'בחר דמות', font=F(RUB, 40), fill='white', anchor='ra', direction='rtl', stroke_width=3, stroke_fill='black')
    d.polygon([(60, 70), (110, 95), (60, 120)], fill='white'); d.polygon([(130, 70), (180, 95), (130, 120)], fill=(255, 255, 255, 120))
    pn = eo((u - .35) / .35)
    if pn > 0:
        d.text((R + int((1 - pn) * 200), 1440), 'בצלאל סמוטריץ׳', font=F(KB, 112), fill=(255, 255, 255, int(255 * pn)), anchor='rs', direction='rtl', stroke_width=6, stroke_fill=(0, 0, 0, int(255 * pn)))
        fc = F(RUB, 42); cw = d.textlength('FIGHTER', font=fc)
        d.rectangle((R - cw - 36, 1460, R, 1520), fill=(214, 40, 40, int(255 * pn))); d.text((R - 18, 1490), 'FIGHTER', font=fc, fill=(255, 255, 255, int(255 * pn)), anchor='rm')
    y = 1570
    for k, (name, v) in enumerate([('כלכלה', 1.0), ('התיישבות', 1.0), ('עמידות', .95)]):
        d.text((R, y), name, font=F(SEC, 40), fill='white', anchor='ra', direction='rtl')
        fill = v * eo((u - .9 - k * .45) / .6); bx0, bx1 = 120, R - 220
        for j in range(10):
            x0 = bx1 - (j + 1) * (bx1 - bx0) / 10 + 6; x1 = bx1 - j * (bx1 - bx0) / 10
            d.rectangle((x0, y + 10, x1, y + 44), fill=(GOLD if j < round(fill * 10) else (70, 70, 70)))
        y += 90
    return lay
def ai_tag(lay, top=True):
    d = ImageDraw.Draw(lay); f = F(SEC, 28); t = 'נוצר ב-AI'; tw = d.textlength(t, font=f, direction='rtl')
    x, y = 40, (150 if top else BH - 80)
    d.rounded_rectangle((x, y, x + tw + 30, y + 46), 23, fill=(0, 0, 0, 110)); d.text((x + 15, y + 23), t, font=f, fill=(255, 255, 255, 220), anchor='lm', direction='rtl')
M3 = 'למעלה מ־⁦100⁩ יישובים'
# (clip, trim start, length, mission, sub, mission-in time)
SHOTS = [('v-select.mp4', 0.0, 3.3, 'SELECT', None, 0),
         ('v-economy.mp4', 0.0, 5.0, 'כלכלה חזקה במלחמה בשבע חזיתות', None, .6),
         ('v-razor.mp4', 0.0, 5.0, 'מרכיבי ביטחון', None, .6),
         ('v-crane.mp4', 0.0, 5.0, M3, 'הניחו את הקרוואן', .4),
         ('v-farm.mp4', 0.0, 5.0, 'למעלה מ־⁦140⁩ חוות', None, .5)]
cache = {}
p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', HERE + '/v-silent.mp4'], stdin=subprocess.PIPE)
n_total = 0; TOT = sum(s[2] for s in SHOTS)
for si, (clip, t0, dur, mis, sub, tin) in enumerate(SHOTS):
    V = frames(G + clip, t0, dur)
    for i, fr in enumerate(V):
        u = i / FPS; im = Image.fromarray(fr).convert('RGBA')
        if mis == 'SELECT': lay = select_layer(u); ai_tag(lay, top=False)
        else:
            sl = round(eo((u - tin) / .45), 2) if u >= tin else 0
            key = (si, sl)
            if key not in cache:
                lay = overlay(mis if sl > 0 else None, sub if sl >= 1 else None, slide=max(sl, .001)); ai_tag(lay); cache[key] = lay
            lay = cache[key]
        im.alpha_composite(lay.resize((W, H), Image.BILINEAR))
        tg = n_total / FPS
        if tg > TOT - .7: im = Image.blend(im, Image.new('RGBA', (W, H), (0, 0, 0, 255)), min(1, (tg - (TOT - .7)) / .7))
        p.stdin.write(im.convert('RGB').tobytes()); n_total += 1
p.stdin.close(); p.wait()
T = n_total / FPS
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', HERE + '/v-silent.mp4', '-ss', '2.45', '-t', f'{T:.2f}', '-i', HERE + '/music/track.wav',
    '-filter_complex', f'[1:a]afade=t=out:st={T - 1.2:.2f}:d=1.2,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]', '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', HERE + '/rz-game-reel.mp4'], check=True)
os.remove(HERE + '/v-silent.mp4'); print('done', T)
