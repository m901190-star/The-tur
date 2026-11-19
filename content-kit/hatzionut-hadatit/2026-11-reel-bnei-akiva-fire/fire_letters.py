"""Composite exact Hebrew word as burning burlap letters onto a clean plate, using real flame texture patches from an AI fire image (screen blend)."""
import sys, numpy as np, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
plate_p, src_p, out_p = sys.argv[1:4]
RUB='/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/fonts/Rubik-700.ttf'
plate=np.asarray(Image.open(plate_p).convert('RGB')).astype(np.float32)/255; H,W,_=plate.shape
src=np.asarray(Image.open(src_p).convert('RGB')).astype(np.float32)/255
# letter stroke centerline mask: thin font strokes on mesh
f=ImageFont.truetype(RUB,300,layout_engine=ImageFont.Layout.RAQM)
m=Image.new('L',(W,H),0); d=ImageDraw.Draw(m)
d.text((W//2+20,1305),'אחדות',font=f,fill=255,anchor='ms',direction='rtl')
m=m.filter(ImageFilter.MinFilter(15))  # thinner tubes
mask=np.asarray(m)>128
ys,xs=np.nonzero(mask)
# flame patches from source letters region (bright fire)
sy0,sy1,sx0,sx1=650,1220,240,1300
lum=src[...,0]*.3+src[...,1]*.6+src[...,2]*.1
cand=[(y,x) for y in range(sy0+140,sy1-40,12) for x in range(sx0+40,sx1-40,12) if lum[y,x]>.85]
random.seed(2); acc=np.zeros_like(plate)
PH,PW=200,90
for i in range(0,len(ys),9):
    y,x=ys[i],xs[i]
    cy,cx=random.choice(cand)
    patch=src[cy-PH+40:cy+40,cx-PW//2:cx+PW//2]
    # remove dark background: keep flame light
    pl_=patch[...,0]*.3+patch[...,1]*.6+patch[...,2]*.1
    a=np.clip((pl_-0.62)/0.33,0,1)[...,None]**1.6
    p=patch*a
    y0=y-PH+40; x0=x-PW//2
    if y0<0 or x0<0 or x0+PW>W or y0+PH>H: continue
    acc[y0:y0+PH,x0:x0+PW]=np.maximum(acc[y0:y0+PH,x0:x0+PW],p)
# core: bright burning burlap along strokes
core=np.asarray(m.filter(ImageFilter.GaussianBlur(3))).astype(np.float32)[...,None]/255
coreC=core*np.array([1.0,.85,.55])
light=np.maximum(acc,coreC)
glow=np.asarray(Image.fromarray((np.clip(light.mean(-1),0,1)*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(60))).astype(np.float32)[...,None]/255
glowC=glow*np.array([1.0,.45,.12])*0.9
out=1-(1-plate)*(1-light)*(1-glowC)  # screen
# keep foreground people in front: dark pixels below mesh top
pl=plate.mean(-1); yy=np.arange(H)[:,None]
people=((pl<0.12)&(yy>1330)).astype(np.float32)
people=np.asarray(Image.fromarray((people*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2))).astype(np.float32)[...,None]/255
out=out*(1-people)+plate*people
Image.fromarray((np.clip(out,0,1)*255).astype(np.uint8)).save(out_p)
