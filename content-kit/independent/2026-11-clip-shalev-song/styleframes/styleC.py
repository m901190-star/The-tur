exec(open('/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/shalev/styleframes.py').read().split('# ---- A: storybook ----')[0])
# combo: storybook page + pop elements
paper=np.full((H,W,3),(247,238,218),np.float32)+rng.normal(0,6,(H,W,1)); C=Image.fromarray(np.clip(paper,0,255).astype('uint8')).convert('RGBA'); d=ImageDraw.Draw(C)
for i in range(60): d.line((i,0,i,H),fill=(200,185,150,int(90*(1-i/60))))
# crayon sunburst behind the sticker (pop energy, hand-drawn)
cx,cy=540,900
for k in range(18):
    a=k*2*math.pi/18; crayon(d,[(cx+330*math.cos(a),cy+330*math.sin(a)),(cx+520*math.cos(a),cy+520*math.sin(a))],(255,196,60),16,2)
d.ellipse((860,140,1000,280),fill=(255,214,90))
for ccx,ccy in [(230,250)]:
    for dx,dy,r in [(-60,10,55),(0,-20,70),(60,10,55)]: d.ellipse((ccx+dx-r,ccy+dy-r,ccx+dx+r,ccy+dy+r),fill=(255,255,255))
crayon(d,[(x,1700+30*math.sin(x/140)) for x in range(0,W+40,40)],(110,170,80),14,3)
d.polygon([(x,1700+30*math.sin(x/140)) for x in range(0,W+40,40)]+[(W,H),(0,H)],fill=(150,200,110))
# storybook title (handwritten, niqqud)
d.text((W/2,340),'שָׁלֵו שָׁלֵו',font=F(AM,200),fill=(60,50,120),anchor='ma',direction='rtl')
st=sticker(shalev.resize((640,551)),18,-3); C.alpha_composite(st,((W-st.width)//2,cy-st.height//2))
# pop elements as stickers with white outline
def emo_sticker(ch,size,rot):
    e=emoji(ch,size); m=e.getchannel('A').filter(ImageFilter.MaxFilter(15)); b=Image.new('RGBA',(e.width,e.height),(255,255,255,0)); b.putalpha(m)
    b.alpha_composite(e); return b.rotate(rot,expand=True,resample=Image.BICUBIC)
for ch,x,y,s,r in [('🪖',60,1150,170,12),('🪑',840,1160,170,-10),('💔',850,520,140,10),('🌀',70,520,150,0)]:
    C.alpha_composite(emo_sticker(ch,s,r),(x,y))
# bold pop word in a red block, slightly tilted, crayon underline
lay=Image.new('RGBA',(W,330),(0,0,0,0)); ld=ImageDraw.Draw(lay); f=F(KB,250); tw=ld.textlength('הַמְעַרְבֵּב',font=f,direction='rtl')
ld.rounded_rectangle((W/2-tw/2-34,30,W/2+tw/2+34,290),22,fill=(230,40,60))
ld.text((W/2+8,22),'הַמְעַרְבֵּב',font=f,fill=(0,0,0),anchor='ma',direction='rtl')
ld.text((W/2,14),'הַמְעַרְבֵּב',font=f,fill=(255,255,255),anchor='ma',direction='rtl')
lay=lay.rotate(-3,resample=Image.BICUBIC); C.alpha_composite(lay,(0,1330))
C.convert('RGB').save(S+'styleC_combo.jpg',quality=92)
