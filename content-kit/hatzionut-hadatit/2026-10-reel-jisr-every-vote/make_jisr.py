"""Religious Zionism reel: the other side's get-out-the-vote clip in Jisr az-Zarqa -> 'they recruit every vote. And you?'
1080x1920, original trailer score. Their words stay as said (their own burned-in subtitles); the target is their campaign, not the voters."""
import os, sys, math, subprocess
G = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/golan'
sys.path.insert(0, G)
import make_golan as mg
from make_golan import (W, H, FPS, WHITE, TEAL, RED, BLACK, INK, PALE, slam, glitch, shake, vignette, LOGO_S, BALLOT_BIG, CLOSE_BG, LOGO_E,
                        ease_out, SKILL, SFX, text)
from PIL import Image, ImageDraw, ImageEnhance, ImageChops, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__)); P = HERE + '/prep/'; os.makedirs(P, exist_ok=True)
SRC = '/root/.claude/uploads/1a5819ee-0cc0-5045-b086-4a8a80216453/e4b13de0-2877696218248454943.mp4'
HOOK = 3.2
S1 = (HOOK, 8.0, 9.0)                 # (reel start, src start, dur): "למה? ... וסמוטריץ' ונתניהו קודם כל הביתה"
S2 = (S1[0] + S1[2], 96.0, 8.8)       # "לא, גם אני יוצא, בטח! ... שכנעת אותי ... עוד קול בג'יסר"
FRZ = (S2[0] + S2[2], 1.6)
ASK = (FRZ[0] + FRZ[1], 2.4)
CLOSE = (ASK[0] + ASK[1], 4.6)
TOTAL = CLOSE[0] + CLOSE[1]
PUNCH = S1[0] + (14.6 - S1[1])        # "וסמוטריץ'" lands

def prep():
    for k, (t0, s0, d) in enumerate((S1, S2)):
        dd = P + f's{k}/'; os.makedirs(dd, exist_ok=True)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(s0), '-t', str(d + .1), '-i', SRC, '-vf', f'fps={FPS},scale={W}:{H}:flags=lanczos,unsharp=5:5:0.5', dd + '%04d.png'], check=True)
def sframe(k, u):
    dd = P + f's{k}/'; fs = sorted(os.listdir(dd)); return Image.open(dd + fs[min(len(fs) - 1, int(u * FPS))]).convert('RGB')
def grade(im): return ImageEnhance.Color(ImageEnhance.Contrast(im).enhance(1.12)).enhance(.85)

def clip_scene(t):
    k = 0 if t < S2[0] else 1; t0, s0, d = (S1, S2)[k]; u = t - t0
    im = grade(sframe(k, u))
    z = 1.0 + 0.04 * u / d
    if k == 0 and t >= PUNCH: z += 0.10 * math.exp(-(t - PUNCH) * 2.5) + 0.06
    im = im.resize((int(W * z), int(H * z)), Image.BILINEAR); x0 = (im.width - W) // 2; y0 = int((im.height - H) * .35)
    im = vignette(im.crop((x0, y0, x0 + W, y0 + H)))
    d_ = ImageDraw.Draw(im); text(d_, (W - 70, 230), 'ג׳סר א־זרקא', 52, PALE, anchor='rm', bold=False); d_.rectangle((W - 54, 206, W - 44, 254), fill=RED)
    if k == 0 and 0 <= t - PUNCH < .3: im = glitch(im, 16 * math.exp(-(t - PUNCH) * 9))
    dx, dy = shake(t, [PUNCH]); im = ImageChops.offset(im, dx, dy)
    if u < .07: im = Image.blend(im, Image.new('RGB', (W, H), WHITE), .45 * (1 - u / .07))
    im.paste(LOGO_S, ((W - LOGO_S.width) // 2, 70), LOGO_S)
    return im

def freeze_scene(t):
    u = t - FRZ[0]; im = grade(sframe(1, S2[2] - .05))
    im = ImageEnhance.Brightness(ImageEnhance.Contrast(Image.blend(ImageOps.grayscale(im).convert('RGB'), Image.new('RGB', (W, H), RED), .2)).enhance(1.3)).enhance(.55)
    z = 1 + .12 * ease_out(u / .4); im = im.resize((int(W * z), int(H * z)), Image.BILINEAR); x0 = (im.width - W) // 2; y0 = (im.height - H) // 2
    im = vignette(im.crop((x0, y0, x0 + W, y0 + H)))
    slam(im, 'הם מגייסים', 200, 760, FRZ[0] + .05, t)
    slam(im, 'כל קול.', 230, 990, FRZ[0] + .45, t, WHITE, block=RED)
    dx, dy = shake(t, [FRZ[0] + .05, FRZ[0] + .45]); im = ImageChops.offset(im, dx, dy)
    if u < .3: im = glitch(im, 14 * math.exp(-u * 9))
    im.paste(LOGO_S, ((W - LOGO_S.width) // 2, 70), LOGO_S)
    return im

def ask_scene(t):
    im = Image.new('RGB', (W, H), INK)
    slam(im, 'ואתה?', 330, 820, ASK[0] + .35, t)
    slam(im, 'נשאר בבית?', 170, 1120, ASK[0] + 1.2, t, WHITE, block=RED)
    im = vignette(im); dx, dy = shake(t, [ASK[0] + .35, ASK[0] + 1.2]); return ImageChops.offset(im, dx, dy)

def close_scene(t):
    u = t - CLOSE[0]; im = CLOSE_BG.copy()
    slam(im, 'ישראל חייבת', 190, 420, CLOSE[0] + .1, t)
    slam(im, 'ציונות דתית חזקה!', 170, 640, CLOSE[0] + .55, t, WHITE, block=TEAL)
    bu = ease_out((u - 1.15) / .25)
    if bu > 0:
        sc = 1.7 - .7 * bu; b = BALLOT_BIG.resize((int(BALLOT_BIG.width * sc), int(BALLOT_BIG.height * sc)), Image.BILINEAR)
        im.paste(b, (int(W / 2 - b.width / 2), int(1110 - b.height / 2)), b)
    la = ease_out((u - 1.8) / .35)
    if la > 0:
        lg = LOGO_E.copy(); lg.putalpha(lg.getchannel('A').point(lambda v: int(v * la))); im.paste(lg, ((W - lg.width) // 2, 1650 - lg.height // 2), lg)
    dx, dy = shake(t, [CLOSE[0] + .55, CLOSE[0] + 1.15], 12); return ImageChops.offset(im, dx, dy)

def hook_scene(t):
    im = Image.new('RGB', (W, H), INK)
    slam(im, 'הם כבר יצאו', 220, 700, .4, t)
    slam(im, 'לשטח.', 260, 940, .95, t)
    slam(im, 'המטרה: להעיף את סמוטריץ׳.', 96, 1260, 2.0, t, WHITE, block=RED)
    im = vignette(im); dx, dy = shake(t, [2.0]); im = ImageChops.offset(im, dx, dy)
    if 2.0 <= t < 2.35: im = glitch(im, 18 * math.exp(-(t - 2.0) * 9))
    if t > HOOK - .08: im = Image.blend(im, Image.new('RGB', (W, H), WHITE), (t - (HOOK - .08)) / .08 * .6)
    return im

def frame(t):
    if t < HOOK: return hook_scene(t)
    if t < FRZ[0]: return clip_scene(t)
    if t < ASK[0]: return freeze_scene(t)
    if t < CLOSE[0]: return ask_scene(t)
    return close_scene(t)

def render(out):
    prep()
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-vf', 'noise=alls=8:allf=t', '-c:v', 'libx264', '-preset', 'medium', '-crf', '21', '-maxrate', '12M', '-bufsize', '24M', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for i in range(int(round(TOTAL * FPS))): ff.stdin.write(frame(i / FPS).convert('RGB').tobytes())
    ff.stdin.close(); ff.wait()

def mix(out_wav):
    subprocess.run(['python3', HERE + '/jisr_score.py', P + 'score.wav'], check=True)
    v = lambda k, at, s0, d: f"[0:a]aformat=sample_rates=48000:channel_layouts=stereo,atrim={s0}:{s0 + d},asetpts=PTS-STARTPTS,highpass=f=90,loudnorm=I=-14:TP=-1.5,afade=t=in:d=0.03,afade=t=out:st={d - 0.1:.2f}:d=0.1,adelay={int(at * 1000)}|{int(at * 1000)}[v{k}]"
    fl = [v(1, S1[0], S1[1], S1[2]), v(2, S2[0], S2[1], S2[2]),
          f'[v1][v2]amix=inputs=2:normalize=0,apad=whole_dur={TOTAL:.3f},asplit=2[voice][key]',
          '[1:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=0.9[score]',
          '[score][key]sidechaincompress=threshold=0.03:ratio=5:attack=15:release=350[duck]',
          f'[duck][voice]amix=inputs=2:normalize=0,atrim=0:{TOTAL:.3f},apad=whole_dur={TOTAL:.3f}[out]']
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', SRC, '-i', P + 'score.wav', '-filter_complex', ';'.join(fl), '-map', '[out]', out_wav], check=True)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'stills':
        prep(); ts = [2.6, S1[0] + 2, PUNCH + .1, S2[0] + 4, FRZ[0] + 1, ASK[0] + 1.8, CLOSE[0] + 3.5]
        im = [frame(x) for x in ts]; sh = Image.new('RGB', (len(im) * 250, 440), WHITE)
        for k, x in enumerate(im): sh.paste(x.resize((240, 427)), (k * 250, 0))
        sh.save(HERE + '/stills.jpg'); print('stills', TOTAL)
    else:
        if 'audio' not in sys.argv: render(P + 'v.mp4')
        mix(P + 'a.wav')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', P + 'v.mp4', '-i', P + 'a.wav', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', P + 'mux.mp4'], check=True)
        subprocess.run(['python3', SKILL + '/scripts/loudnorm.py', P + 'mux.mp4', HERE + '/rz-jisr-every-vote.mp4', '--target', '-14'], check=True)
        print('done', TOTAL)
