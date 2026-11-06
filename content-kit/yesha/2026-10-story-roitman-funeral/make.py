"""Yesha Council story: the funeral procession of Ron Yonatan Roitman (1080x1920 video).
Portrait intro in the memorial style, then the procession footage with name and caption. No music, original sound."""
import os, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter
OUT = os.path.dirname(os.path.abspath(__file__))
SCR = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/roitman/'
FONTS = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/pro-video-editing/assets/fonts/'
LOGNORM = '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/pro-video-editing/scripts/loudnorm.py'
VID = '/root/.claude/uploads/1a5819ee-0cc0-5045-b086-4a8a80216453/3d3409ff-841781843919180038.mp4'
PHOTO = '/root/.claude/uploads/1a5819ee-0cc0-5045-b086-4a8a80216453/d7526711-image.jpg'
LOGO = OUT + '/../../clients/yesha/logo.png'
W, H = 1080, 1920
INTRO = 3.5                    # portrait seconds before the footage
XF = 0.8                       # crossfade
BLUE = (0x25, 0x66, 0xA2); WHITE = (255, 255, 255); SOFT = (0xD6, 0xE4, 0xEF)
os.makedirs(SCR, exist_ok=True)
F = lambda s, b=True: ImageFont.truetype(FONTS + ('Karantina-Bold.ttf' if b else 'Karantina-Regular.ttf'), s)

def run(a): subprocess.run(['ffmpeg', '-v', 'error', '-y'] + a, check=True)

def name(d, y, s, size):
    d.text((W / 2 + 7, y + 7), s, font=F(size), fill=BLUE, anchor='ma', direction='rtl')
    d.text((W / 2, y), s, font=F(size), fill=WHITE, anchor='ma', direction='rtl')

def logo(img, w=150, y=40):
    lg = Image.open(LOGO).convert('RGBA'); lg = lg.crop(lg.getchannel('A').getbbox())
    lg = lg.resize((w, int(w * lg.height / lg.width)), Image.LANCZOS)
    img.alpha_composite(lg, (W - 36 - w, y))

def fade(img, start, end, maxa=235):
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = (y / H - start) / (end - start)
        if t > 0: d.line([(0, y), (W, y)], fill=(0, 0, 0, int(maxa * min(1, t) ** 1.1)))

# portrait for the intro (the photo's left half is Ron)
p = Image.open(PHOTO).convert('RGB').crop((0, 0, 655, 1130))
s = max(W / p.width, H / p.height) * 1.06
p = p.resize((int(p.width * s), int(p.height * s)), Image.LANCZOS)
p.crop(((p.width - W * 1.06) // 2 if False else (p.width - int(W * 1.06)) // 2, 0, (p.width - int(W * 1.06)) // 2 + int(W * 1.06), int(H * 1.06))).save(SCR + 'portrait.png')

# intro text layer
ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); fade(ov, .50, .78, 245); logo(ov)
d = ImageDraw.Draw(ov)
name(d, 1370, 'סמ״ר רון יונתן רויטמן הי״ד', 110)
d.text((W / 2, 1500), 'בן 23 מאשקלון', font=F(54, False), fill=SOFT, anchor='ma', direction='rtl')
d.text((W / 2, 1640), 'יהי זכרו ברוך', font=F(72), fill=WHITE, anchor='ma', direction='rtl')
ov.save(SCR + 'intro_ov.png')

# footage text layer: circular portrait, headline, name
ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); fade(ov, .52, .80, 235); logo(ov, 130, 205)   # below the photo credit burned into the footage
pc = Image.open(PHOTO).convert('RGB').crop((40, 60, 600, 620)).resize((230, 230), Image.LANCZOS)
m = Image.new('L', (230, 230), 0); ImageDraw.Draw(m).ellipse((0, 0, 229, 229), fill=255)
ring = Image.new('RGBA', (246, 246), (0, 0, 0, 0)); ImageDraw.Draw(ring).ellipse((0, 0, 245, 245), fill=WHITE)
ov.alpha_composite(ring, ((W - 246) // 2, 1000)); ov.paste(pc, ((W - 230) // 2, 1008), m)
d = ImageDraw.Draw(ov)
d.text((W / 2, 1290), 'מאות מלווים בדרכו האחרונה את', font=F(64, False), fill=SOFT, anchor='ma', direction='rtl')
name(d, 1380, 'סמ״ר רון יונתן רויטמן הי״ד', 104)
d.text((W / 2, 1510), 'שנפל בפיגוע ליד חברון ביום שישי', font=F(54, False), fill=SOFT, anchor='ma', direction='rtl')
d.text((W / 2, 1650), 'יהי זכרו ברוך', font=F(72), fill=WHITE, anchor='ma', direction='rtl')
ov.save(SCR + 'video_ov.png')

dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', VID]))
total = INTRO + dur - XF
fr = int(INTRO * 30) + 30
run(['-loop', '1', '-t', f'{INTRO + 1}', '-i', SCR + 'portrait.png', '-loop', '1', '-t', f'{INTRO + 1}', '-i', SCR + 'intro_ov.png',
     '-i', VID, '-loop', '1', '-t', f'{dur}', '-i', SCR + 'video_ov.png',
     '-filter_complex',
     f"[0:v]scale=w='{int(W*1.06)}*(1+0.05*t/{INTRO+1})':h=-2:eval=frame,crop={W}:{H},setsar=1,fps=30,format=rgba[ph];"
     f"[1:v]format=rgba,fade=t=in:st=0.3:d=0.6:alpha=1[io];[ph][io]overlay=0:0,fade=t=in:st=0:d=0.5,format=yuv420p[intro];"
     f"[2:v]scale={W}:-2,crop={W}:{H}:0:(ih-{H})/2,setsar=1,fps=30[v];"
     f"[3:v]format=rgba,fade=t=in:st=0.4:d=0.7:alpha=1[vo];[v][vo]overlay=0:0,format=yuv420p[foot];"
     f"[intro][foot]xfade=transition=fade:duration={XF}:offset={INTRO - XF + 0.0},fade=t=out:st={total - 0.8}:d=0.8[out];"
     f"[2:a]afade=t=in:d=1.2,adelay={int((INTRO - XF) * 1000)}|{int((INTRO - XF) * 1000)},afade=t=out:st={total - 1.2}:d=1.2,atrim=0:{total}[a]",
     '-map', '[out]', '-map', '[a]', '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', SCR + 'mux.mp4'])
subprocess.run(['python3', LOGNORM, SCR + 'mux.mp4', OUT + '/yesha-story-roitman.mp4', '--target', '-16'], check=True)
print('done', round(total, 2))
