from PIL import Image, ImageDraw, ImageFilter
import glob
U='/root/.claude/uploads/1a5819ee-0cc0-5045-b086-4a8a80216453/'
def src(i): return Image.open(glob.glob(U+i+'*')[0]).convert('RGB')
crops={'stones':('842e4645',None),'car':('bf29146e',(29,515,1291,1465)),'shep1':('ea39b6e3',None),'shep2':('06142641',None),
 'manual':('ab8cbe3c',(20,224,977,1640)),'lynch':('bd21b636',None),'flag':('8eb5aa30',(100,480,1130,1840)),'nablus':('21639ac3',(0,330,962,1340)),
 'tg':('ab8cbe3c',None)}
def card(im,r):
    W,H=im.size; S=4
    m=Image.new('L',(W*S,H*S),0); ImageDraw.Draw(m).rounded_rectangle((0,0,W*S-1,H*S-1),r*S,fill=255)
    m=m.resize((W,H),Image.LANCZOS); im=im.convert('RGBA'); im.putalpha(m); return im
for k,(i,c) in crops.items():
    im=src(i)
    if c: im=im.crop(c)
    if im.width>1100: im=im.resize((1100,int(im.height*1100/im.width)),Image.LANCZOS)
    card(im,40 if k!='tg' else 0).save(f'web/{k}.png'); print(k,im.size)
