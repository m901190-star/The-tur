"""Original game-trailer title card 'SMOTRICH' (no Rockstar marks/fonts): tilted gradient badge + heavy outlined type."""
import os, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); W, H = 1080, 1920
FONT = '/usr/share/fonts/opentype/inter/InterDisplay-BlackItalic.otf'
def badge(text='SMOTRICH', bw=820, bh=300):
    g = np.zeros((bh, bw, 3), np.float32); xx = np.linspace(0, 1, bw)[None, :, None]; yy = np.linspace(0, 1, bh)[:, None, None]
    c1, c2, c3 = np.array([255, 120, 60.]), np.array([236, 60, 160.]), np.array([90, 70, 220.])
    t = (xx * .7 + yy * .3); g = np.where(t < .5, c1 + (c2 - c1) * (t / .5), c2 + (c3 - c2) * ((t - .5) / .5))
    grad = Image.fromarray(g.clip(0, 255).astype(np.uint8)).convert('RGBA')
    sh = Image.new('L', (bw, bh), 0); ImageDraw.Draw(sh).polygon([(40, 0), (bw, 0), (bw - 40, bh), (0, bh)], fill=255)
    b = Image.new('RGBA', (bw + 40, bh + 40), (0, 0, 0, 0)); b.paste(grad, (20, 20), sh)
    d = ImageDraw.Draw(b); d.polygon([(60, 20), (bw + 20, 20), (bw - 20, bh + 20), (20, bh + 20)], outline=(255, 255, 255), width=8)
    # light streak
    st = Image.new('RGBA', b.size, (0, 0, 0, 0)); ImageDraw.Draw(st).polygon([(bw * .55, 20), (bw * .7, 20), (bw * .45, bh + 20), (bw * .3, bh + 20)], fill=(255, 255, 255, 50)); st.putalpha(Image.composite(st.getchannel('A'), Image.new('L', b.size, 0), Image.new('L', b.size, 0).point(lambda v: 0)) if False else st.getchannel('A'))
    b.alpha_composite(st)
    f = ImageFont.truetype(FONT, 150); tw = d.textlength(text, font=f)
    if tw > bw - 100: f = ImageFont.truetype(FONT, int(150 * (bw - 100) / tw))
    d.text(((bw + 40) / 2, (bh + 40) / 2 + 6), text, font=f, fill='white', anchor='mm', stroke_width=10, stroke_fill=(15, 10, 30))
    return b
if __name__ == '__main__':
    bg = ImageOps.fit(Image.open(HERE + '/gen/aerial.png').convert('RGB'), (W, H), Image.LANCZOS).convert('RGBA')
    b = badge().rotate(8, resample=Image.BICUBIC, expand=True)
    shd = Image.new('RGBA', b.size, (0, 0, 0, 0)); shd.putalpha(b.getchannel('A').point(lambda v: int(v * .55))); shd = shd.filter(ImageFilter.GaussianBlur(18))
    x, y = (W - b.width) // 2, int(H * .42 - b.height / 2)
    bg.alpha_composite(shd, (x + 14, y + 22)); bg.alpha_composite(b, (x, y))
    bg.convert('RGB').save(HERE + '/sketch5-title.jpg', quality=92)
