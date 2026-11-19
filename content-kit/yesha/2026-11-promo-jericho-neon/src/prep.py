from PIL import Image, ImageDraw, ImageFilter
U='/root/.claude/uploads/1a5819ee-0cc0-5045-b086-4a8a80216453/'
def card(im,r=40,maxw=1100):
    if im.width>maxw: im=im.resize((maxw,int(im.height*maxw/im.width)),Image.LANCZOS)
    W,H=im.size; S=4; m=Image.new('L',(W*S,H*S),0); ImageDraw.Draw(m).rounded_rectangle((0,0,W*S-1,H*S-1),r*S,fill=255)
    im=im.convert('RGBA'); im.putalpha(m.resize((W,H),Image.LANCZOS)); return im
road=Image.open(U+'196d272b-image.jpg').convert('RGB')
d=ImageDraw.Draw(road); d.rectangle((1512,1048,1561,1066),fill=(176,168,140))
patch=road.crop((1505,1042,1568,1072)).filter(ImageFilter.GaussianBlur(2)); road.paste(patch,(1505,1042))
road.save('web/road_full.jpg',quality=92)
card(road.crop((0,250,2048,1536)),40,1100).save('web/road.png')
for k,f in [('living','b0fd2930'),('door','275e063b'),('hill','c36b3f79'),('porch','ec905d07'),('truck','8d87d661')]:
    card(Image.open(U+f+'-image.jpg').convert('RGB')).save(f'web/{k}.png')
