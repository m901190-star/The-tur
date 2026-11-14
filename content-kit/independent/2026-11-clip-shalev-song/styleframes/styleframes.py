import numpy as np, math, glob
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
S='/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/shalev/'
W,H=1080,1920; rng=np.random.default_rng(4)
AM=S+'fonts/Amatic-Bold.ttf'; VR=S+'fonts/VarelaRound.ttf'
KB=glob.glob('/root/.claude/skills/synced/*/pro-video-editing/assets/fonts/Karantina-Bold.ttf')[0]
EMO='/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'
def F(p,s): return ImageFont.truetype(p,s,layout_engine=ImageFont.Layout.RAQM)
def emoji(ch,size):
    f=ImageFont.truetype(EMO,109); im=Image.new('RGBA',(160,160),(0,0,0,0)); ImageDraw.Draw(im).text((10,10),ch,font=f,embedded_color=True)
    im=im.crop(im.getbbox()); return im.resize((size,int(size*im.height/im.width)),Image.LANCZOS)
def crayon(d,pts,col,w=10,passes=3):
    for _ in range(passes):
        q=[(x+rng.normal(0,2.5),y+rng.normal(0,2.5)) for x,y in pts]; d.line(q,fill=col,width=w,joint='curve')
def sticker(im,border=18,rot=0):
    im=im.convert('RGBA'); w,h=im.size; m=Image.new('L',(w,h),0); ImageDraw.Draw(m).rounded_rectangle((0,0,w-1,h-1),28,fill=255); im.putalpha(m)
    b=Image.new('RGBA',(w+2*border,h+2*border),(0,0,0,0)); bm=Image.new('L',b.size,0); ImageDraw.Draw(bm).rounded_rectangle((0,0,b.width-1,b.height-1),40,fill=255)
    b.paste((255,255,255,255),(0,0),bm); b.alpha_composite(im,(border,border))
    sh=Image.new('RGBA',(b.width+60,b.height+60),(0,0,0,0)); sh.paste((0,0,0,90),(30,40),bm.filter(ImageFilter.GaussianBlur(0)))
    sh=sh.filter(ImageFilter.GaussianBlur(14)); sh.alpha_composite(b,(30,30)); return sh.rotate(rot,expand=True,resample=Image.BICUBIC)
shalev=Image.open(S+'shalev_top.png')

# ---- A: storybook ----
paper=np.full((H,W,3),(247,238,218),np.float32)+rng.normal(0,6,(H,W,1)); A=Image.fromarray(np.clip(paper,0,255).astype('uint8')).convert('RGBA')
d=ImageDraw.Draw(A)
# page edge / book gutter shading
for i in range(60): d.line((i,0,i,H),fill=(200,185,150,int(90*(1-i/60))))
# sky blob + sun + clouds + hills
d.ellipse((760,150,960,350),fill=(255,214,90)); crayon(d,[(860+130*math.cos(a),250+130*math.sin(a)) for a in np.linspace(0,6.3,40)],(240,170,40),8)
for k in range(10): a=k*.628; crayon(d,[(860+150*math.cos(a),250+150*math.sin(a)),(860+200*math.cos(a),250+200*math.sin(a))],(240,170,40),7,2)
for cx,cy in [(260,260),(520,180)]:
    for dx,dy,r in [(-60,10,55),(0,-20,70),(60,10,55)]: d.ellipse((cx+dx-r,cy+dy-r,cx+dx+r,cy+dy+r),fill=(255,255,255))
crayon(d,[(x,1640+40*math.sin(x/140)) for x in range(0,W+40,40)],(110,170,80),14,3)
d.polygon([(x,1640+40*math.sin(x/140)) for x in range(0,W+40,40)]+[(W,H),(0,H)],fill=(150,200,110))
# title
d.text((W/2,420),'שָׁלֵו הַמְעַרְבֵּב',font=F(AM,190),fill=(60,50,120),anchor='ma',direction='rtl')
crayon(d,[(250,640),(540,660),(830,640)],(230,90,80),10)
st=sticker(shalev.resize((640,551)),18,-4); A.alpha_composite(st,((W-st.width)//2,700))
# crayon blender doodle
bx,by=780,1330; crayon(d,[(bx,by),(bx+40,by+230),(bx+180,by+230),(bx+220,by)],(70,120,200),10); crayon(d,[(bx-10,by),(bx+230,by)],(70,120,200),12)
d.rectangle((bx+30,by+235,bx+190,by+300),fill=(70,120,200))
for k in range(3): crayon(d,[(bx+60+k*40,by+60),(bx+80+k*40,by+140)],(230,90,80),6,2)
d.text((W/2,1460),'עָשָׂה וָואחַד קַמְפֵּיין',font=F(AM,120),fill=(40,40,40),anchor='ma',direction='rtl')
A.convert('RGB').save(S+'styleA_storybook.jpg',quality=92)

# ---- B: fast pop blender ----
B=Image.new('RGBA',(W,H),(255,212,0,255)); d=ImageDraw.Draw(B)
for k in range(24):   # sunburst
    a0=k*2*math.pi/24; a1=a0+math.pi/24; d.polygon([(W/2,900),(W/2+2000*math.cos(a0),900+2000*math.sin(a0)),(W/2+2000*math.cos(a1),900+2000*math.sin(a1))],fill=(255,190,0))
st=sticker(shalev.resize((700,603)),20,3); B.alpha_composite(st,((W-st.width)//2,480))
for ch,x,y,s,r in [('🌀',80,300,170,0),('🪑',830,1200,180,-12),('🪖',90,1180,170,10),('💔',840,330,150,8),('🎖️',470,1330,140,0)]:
    e=emoji(ch,s).rotate(r,expand=True,resample=Image.BICUBIC); B.alpha_composite(e,(x,y))
def pop(d,xy,s,size,fill,stroke,blk=None):
    f=F(KB,size)
    if blk:
        tw=d.textlength(s,font=f,direction='rtl'); d.rounded_rectangle((xy[0]-tw/2-30,xy[1]+10,xy[0]+tw/2+30,xy[1]+size*.95),18,fill=blk)
    d.text((xy[0]+8,xy[1]+10),s,font=f,fill=(0,0,0),anchor='ma',direction='rtl',stroke_width=10,stroke_fill=(0,0,0))
    d.text(xy,s,font=f,fill=fill,anchor='ma',direction='rtl',stroke_width=10,stroke_fill=stroke)
pop(d,(W/2,120),'שָׁלֵו שָׁלֵו',230,(255,255,255),(0,0,0))
pop(d,(W/2,1520),'הַמְעַרְבֵּב',260,(255,255,255),(0,0,0),blk=(230,40,60))
B.convert('RGB').save(S+'styleB_pop.jpg',quality=92)
sh=Image.new('RGB',(1100,980),'white'); sh.paste(Image.open(S+'styleA_storybook.jpg').resize((540,960)),(0,10)); sh.paste(Image.open(S+'styleB_pop.jpg').resize((540,960)),(560,10)); sh.save(S+'styles.jpg',quality=90)
