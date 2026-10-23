"""Smotrich demolition video: vertical 1080x1920, speech + tractor b-roll, captions, no logo, no music."""
import os, subprocess
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = HERE + '/../pro-video-editing'
FONTS = SKILL + '/assets/fonts'
SFX = SKILL + '/assets/sfx/'
SRC = HERE + '/src/'
SEG = HERE + '/seg/'
os.makedirs(SEG, exist_ok=True)
W, H, FPS = 1080, 1920, 30
OFF = 3.7                      # output time = speech source time + OFF
OPEN = (SRC + '04.mp4', 1.8, 4.0)   # trampoline smash: start, duration

# (kind, out_start, out_end, broll clip, broll start)
# 's' = speaker card over blurred b-roll, 'b' = full-screen b-roll
TL = [
    ('s', 4.0, 9.2, '03', 0.0),
    ('b', 9.2, 12.9, '03', 4.0),
    ('s', 12.9, 17.7, '06', 0.0),
    ('b', 17.7, 21.0, '06', 2.0),
    ('s', 21.0, 25.5, '07', 0.0),
    ('b', 25.5, 28.6, '08', 3.0),
    ('b', 28.6, 31.6, '05', 1.0),
    ('s', 31.6, 36.8, '09', 0.0),
    ('b', 36.8, 39.6, '09', 6.0),
    ('b', 39.6, 42.5, '11', 0.0),
    ('s', 42.5, 46.7, '08', 10.0),
    ('b', 46.7, 49.6, '10', 0.5),
    ('b', 49.6, 52.7, '07', 1.0),
    ('s', 52.7, 56.0, '05', 9.0),
    ('b', 56.0, 59.0, '09', 14.0),
    ('b', 59.0, 62.1, '12', 0.0),
    ('s', 62.1, 64.4, '08', 15.0),
    ('b', 64.4, 66.4, '04', 8.0),      # end hold: last line stays on screen
]
TOTAL = TL[-1][2]

FILL = f'scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps={FPS}'


def run(args):
    subprocess.run(['ffmpeg', '-v', 'error', '-y'] + args, check=True)


def card_mask():
    m = Image.new('L', (1000, 750), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, 999, 749), radius=36, fill=255)
    m.save(SEG + 'mask.png')
    fr = Image.new('RGBA', (1012, 762), (0, 0, 0, 0))
    ImageDraw.Draw(fr).rounded_rectangle((0, 0, 1011, 761), radius=40, fill=(255, 199, 44, 255))
    fr.save(SEG + 'frame.png')


def bottom_shade():
    g = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(g)
    for y in range(H):
        t = y / H
        a = int(120 * max(0, 1 - t / 0.12)) + int(200 * max(0, (t - 0.6) / 0.4) ** 1.2)
        d.line([(0, y), (W, y)], fill=(0, 0, 0, min(a, 200)))
    g.save(SEG + 'shade.png')


def seg_speaker(i, a, b, clip, bs):
    d = b - a
    src_t = a - OFF
    run(['-ss', f'{bs}', '-t', f'{d}', '-i', SRC + clip + '.mp4',
         '-ss', f'{src_t:.3f}', '-t', f'{d}', '-i', SRC + '01.mp4',
         '-i', SEG + 'mask.png', '-i', SEG + 'frame.png',
         '-filter_complex',
         f'[0:v]{FILL},boxblur=18:2,eq=brightness=-0.12:saturation=0.85[bg];'
         f'[1:v]fps={FPS},crop=960:720:160:0,scale=1000:750,format=rgba[sp];'
         f'[2:v]format=gray[m];[sp][m]alphamerge[spm];'
         f'[bg][3:v]overlay=34:479[bf];[bf][spm]overlay=40:485,format=yuv420p[v]',
         '-map', '[v]', '-an', '-c:v', 'libx264', '-crf', '17', '-preset', 'fast', SEG + f'{i:02d}.mp4'])


def seg_broll(i, a, b, clip, bs):
    d = b - a
    # slow push-in keeps static shots alive
    run(['-ss', f'{bs}', '-t', f'{d}', '-i', SRC + clip + '.mp4',
         '-filter_complex',
         f"[0:v]{FILL},scale=w='iw*(1+0.05*t/{d})':h='ih*(1+0.05*t/{d})':eval=frame,crop={W}:{H},format=yuv420p[v]",
         '-map', '[v]', '-an', '-c:v', 'libx264', '-crf', '17', '-preset', 'fast', SEG + f'{i:02d}.mp4'])


def seg_open():
    f, s, d = OPEN
    run(['-ss', f'{s}', '-t', f'{d}', '-i', f, '-vf', f'{FILL},format=yuv420p', '-an',
         '-c:v', 'libx264', '-crf', '17', '-preset', 'fast', SEG + 'open.mp4'])


def overlays():
    """Hook line on the opener and the name lower-third on the first speaker shot."""
    fb = ImageFont.truetype(FONTS + '/Karantina-Bold.ttf', 150)
    fr = ImageFont.truetype(FONTS + '/Karantina-Regular.ttf', 56)
    hook = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(hook)
    for k, (line, col) in enumerate([('״מחירים כואבים', (255, 255, 255)), ('מאוד, מאוד״', (255, 199, 44))]):
        y = 1260 + k * 165
        d.text((W / 2 + 6, y + 6), line, font=fb, fill=(0, 0, 0, 170), anchor='mm', direction='rtl')
        d.text((W / 2, y), line, font=fb, fill=col, anchor='mm', direction='rtl')
    hook.save(SEG + 'hook.png')
    lt = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lt)
    name = 'השר בצלאל סמוטריץ׳'
    w = d.textlength(name, font=fr, direction='rtl')
    x1, y = W - 40, 1250
    d.rectangle((x1 - w - 60, y, x1, y + 84), fill=(0, 0, 0, 200))
    d.rectangle((x1 - 10, y, x1, y + 84), fill=(255, 199, 44, 255))
    d.text((x1 - 34, y + 42), name, font=fr, fill=(255, 255, 255), anchor='rm', direction='rtl')
    lt.save(SEG + 'lowerthird.png')


def assemble():
    with open(SEG + 'list.txt', 'w') as fh:
        fh.write(f"file 'open.mp4'\n")
        for i in range(len(TL)):
            fh.write(f"file '{i:02d}.mp4'\n")
    run(['-f', 'concat', '-safe', '0', '-i', SEG + 'list.txt', '-c', 'copy', SEG + 'concat.mp4'])
    run(['-i', SEG + 'concat.mp4', '-i', SEG + 'shade.png', '-loop', '1', '-t', '10', '-i', SEG + 'hook.png', '-loop', '1', '-t', '10', '-i', SEG + 'lowerthird.png',
         '-filter_complex',
         f"[0:v][1:v]overlay=0:0[a];"
         f"[2:v]format=rgba,fade=t=in:st=0.5:d=0.25:alpha=1,fade=t=out:st=3.6:d=0.3:alpha=1[hk];"
         f"[a][hk]overlay=0:0:enable='between(t,0.5,3.95)'[b];"
         f"[3:v]format=rgba,fade=t=in:st=4.2:d=0.3:alpha=1,fade=t=out:st=8.4:d=0.3:alpha=1[lt];"
         f"[b][lt]overlay=0:0:enable='between(t,4.2,8.75)',ass={HERE}/caps.ass:fontsdir={FONTS},format=yuv420p[v]",
         '-map', '[v]', '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', SEG + 'video.mp4'])


def audio():
    cues = []   # (file, at, gain, extra)
    cues.append((OPEN[0], 0.0, 1.0, f'atrim={OPEN[1]}:{OPEN[1] + OPEN[2] + 0.2},asetpts=PTS-STARTPTS,afade=t=out:st={OPEN[2] - 0.5}:d=0.7'))
    cues.append((SRC + '01.mp4', OFF, 1.0, 'highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=10:release=200'))
    # b-roll ambience low under the voice
    for kind, a, b, clip, bs in TL:
        if kind == 'b' and clip != '01':
            cues.append((SRC + clip + '.mp4', a, 0.18, f'atrim={bs}:{bs + b - a},asetpts=PTS-STARTPTS,afade=t=in:d=0.15,afade=t=out:st={b - a - 0.2}:d=0.2'))
    # transition sounds on every cut, a hit when the hook lands
    cues.append((SFX + 'hit_soft.wav', 0.5, 0.9, ''))
    cues.append((SFX + 'whoosh.wav', 3.75, 0.6, ''))
    cues.append((SFX + 'pop_soft.wav', 4.25, 0.5, ''))
    for k, (kind, a, b, clip, bs) in enumerate(TL[1:], 1):
        cues.append((SFX + ('swoosh_soft.wav' if k % 2 else 'whoosh.wav'), a - 0.12, 0.35, ''))
    cues.append((SFX + 'impact.wav', TL[-1][1], 0.5, ''))
    args = []
    for f, _, _, _ in cues:
        args += ['-i', f]
    fl = []
    for j, (f, at, g, ex) in enumerate(cues):
        chain = f'[{j}:a]aformat=sample_rates=48000:channel_layouts=stereo'
        if ex:
            chain += ',' + ex
        chain += f',volume={g},adelay={int(at * 1000)}|{int(at * 1000)}[a{j}]'
        fl.append(chain)
    fl.append(''.join(f'[a{j}]' for j in range(len(cues))) + f'amix=inputs={len(cues)}:normalize=0,afade=t=out:st={TOTAL - 0.8}:d=0.8,atrim=0:{TOTAL}[out]')
    run(args + ['-filter_complex', ';'.join(fl), '-map', '[out]', SEG + 'audio.wav'])


if __name__ == '__main__':
    import sys
    card_mask(); bottom_shade(); overlays()
    if 'final' not in sys.argv:
        seg_open()
        for i, (kind, a, b, clip, bs) in enumerate(TL):
            (seg_speaker if kind == 's' else seg_broll)(i, a, b, clip, bs)
    assemble(); audio()
    run(['-i', SEG + 'video.mp4', '-i', SEG + 'audio.wav', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
         '-shortest', '-movflags', '+faststart', SEG + 'mux.mp4'])
    subprocess.run(['python3', SKILL + '/scripts/loudnorm.py', SEG + 'mux.mp4', HERE + '/smotrich-demolition.mp4', '--target', '-14'], check=True)
    print('done', TOTAL)
