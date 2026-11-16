import glob, subprocess, numpy as np, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
KB = glob.glob('/root/.claude/skills/synced/*/pro-video-editing/assets/fonts/Karantina-Bold.ttf')[0]
LOGO = HERE + '/../../clients/yesha/logo_white.png'
W, H, FPS, DUR = 720, 1280, 30, 6.0
NAVY, BLUE, LBLUE = (23,64,104), (37,102,162), (39,164,209)
def F(s): return ImageFont.truetype(KB, s, layout_engine=ImageFont.Layout.RAQM)
def eo(x): x=max(0.,min(1.,x)); return 1-(1-x)**3
# frames of slowed footage
src = subprocess.run(['ffmpeg','-v','error','-i',HERE+'/footage/opening.mov','-vf',
  f'setpts={DUR/4.04}*PTS,fps={FPS},scale={W}:{H}','-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True).stdout
fr = np.frombuffer(src,np.uint8).reshape(-1,H,W,3); N = int(DUR*FPS)
lg = Image.open(LOGO).convert('RGBA'); lg = lg.crop(lg.getchannel('A').getbbox()); lg = lg.resize((120,int(120*lg.height/lg.width)),Image.LANCZOS)
# vignette/gradient for legibility
g = np.zeros((H,W),np.float32); y = np.arange(H)[:,None]
g[:] = 0.55*np.exp(-((y-620)/330.)**2)
GR = Image.fromarray((g*255).astype(np.uint8))
def text_shadow(im, xy, s, f, a, anchor):
    lay = Image.new('RGBA', im.size, (0,0,0,0)); d = ImageDraw.Draw(lay)
    x,y = xy
    d.text((x+6,y+6), s, font=f, fill=BLUE+(int(255*a),), anchor=anchor)
    d.text((x,y), s, font=f, fill=(255,255,255,int(255*a)), anchor=anchor)
    im.alpha_composite(lay)
T_CNT0, T_CNT1, T_L2 = 0.5, 2.1, 2.7
def frame(i):
    t = i/FPS
    im = Image.fromarray(fr[min(i,len(fr)-1)]).convert('RGBA')
    dark = Image.new('RGBA',(W,H),NAVY+(0,)); dark.putalpha(GR.point(lambda v:int(v*min(1,t/0.6))))
    im.alpha_composite(dark)
    # line 1: כ־ 1500 שנה  (RTL: right->left)
    if t >= T_CNT0:
        a = eo((t-T_CNT0)/0.3)
        p = eo((t-T_CNT0)/(T_CNT1-T_CNT0)); n = int(round(1500*p)) if t<T_CNT1 else 1500
        # punch scale on landing
        k = 1.0 + 0.12*max(0,1-(t-T_CNT1)/0.35) if t>=T_CNT1 else 1.0
        fn = F(int(200*k)); fw = F(int(100*k))
        num = f'{n:,}'; d0 = ImageDraw.Draw(im); nw = d0.textlength('1,500', font=fn); yw = d0.textlength('years', font=fw)
        y = 590; x0 = W/2 - (nw + 16 + yw)/2
        text_shadow(im,(W/2,y-200),'For about',F(78),a,'ms')
        text_shadow(im,(x0+nw,y),num,fn,a,'rs')
        text_shadow(im,(x0+nw+16,y),'years',fw,a,'ls')
    if t >= T_L2:
        u = (t-T_L2)/0.45; a = eo(u); dy = int(40*(1-eo(u)))
        text_shadow(im,(W/2,690+dy),'there was no',F(84),a,'ms')
        # bar behind last line
        lay = Image.new('RGBA',(W,H),(0,0,0,0)); d = ImageDraw.Draw(lay)
        u2 = eo((t-T_L2-0.25)/0.45); bw = int((d.textlength('Jewish village here', font=F(78))+50)*u2)
        if bw>0: d.rectangle([W/2-bw/2,715,W/2+bw/2,815],fill=LBLUE+(int(235*a),))
        im.alpha_composite(lay)
        if t >= T_L2+0.4:
            text_shadow(im,(W/2,795),'Jewish village here',F(78),eo((t-T_L2-0.4)/0.35),'ms')
    return im.convert('RGB')
P = subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
  '-i',HERE+'/opening-music/guitar.wav','-i',HERE+'/opening-music/drone.wav','-i',HERE+'/opening-music/hit.wav',
  '-filter_complex',
  '[1:a]atrim=0:6,afade=t=in:d=0.3,volume=0.9[g];'
  '[2:a]atrim=0:6,afade=t=in:d=1.0,volume=0.6[dr];'
  '[3:a]adelay=2050|2050,volume=0.9[h];'
  '[g][dr][h]amix=inputs=3:normalize=0,afade=t=out:st=5.4:d=0.6,loudnorm=I=-14:TP=-1.5[a]',
  '-map','0:v','-map','[a]','-t',str(DUR),'-c:v','libx264','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k',
  '-movflags','+faststart',HERE+'/en/opening-en.mp4'],stdin=subprocess.PIPE)
for i in range(N): P.stdin.write(frame(i).tobytes())
P.stdin.close(); P.wait()
for t in (1.2,2.2,4.5): frame(int(t*FPS)).save(f'/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/open_en_{t}.png')
