"""Add the Farms Union logo to Moshe's cover as a second peel-sticker, matching the Yesha sticker already on it."""
import os, numpy as np
from PIL import Image, ImageDraw, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
im = Image.open(HERE + '/cover_src.png').convert('RGBA')
S = 2  # supersample
R = 122 * S; D = 2 * R + 40 * S
def sticker(logo_path, mirror=False):
    c = Image.new('RGBA', (D, D), (0, 0, 0, 0))
    cx = cy = D // 2
    yy, xx = np.mgrid[0:D, 0:D]
    inside = (xx - cx) ** 2 + (yy - cy) ** 2 <= R ** 2
    # fold line near the lower-left edge
    n = np.array([.62 if mirror else -.62, .78]); n /= np.linalg.norm(n); off = R * .74
    dist = (xx - cx) * n[0] + (yy - cy) * n[1] - off
    body = inside & (dist <= 0)
    paper = np.zeros((D, D, 4), np.float32)
    shade = np.clip(248 - 8 * ((yy - cy) / R), 0, 255)   # very soft vertical gradient
    paper[body, :3] = shade[body, None]; paper[body, 3] = 255
    # flap: reflected over the fold, curled
    ys, xs = np.nonzero(inside & (dist > 0)); dd = dist[ys, xs]
    fx = (xs - n[0] * dd * 1.6).astype(int); fy = (ys - n[1] * dd * 1.6).astype(int)
    ok = (fx >= 0) & (fx < D) & (fy >= 0) & (fy < D)
    flap = np.zeros((D, D, 4), np.float32)
    g = 200 + 50 * (1 - dd[ok] / (dd.max() + 1e-6))
    flap[fy[ok], fx[ok], :3] = g[:, None]; flap[fy[ok], fx[ok], 3] = 255
    body_im = Image.fromarray(paper.astype(np.uint8), 'RGBA')
    flap_im = Image.fromarray(flap.astype(np.uint8), 'RGBA').filter(ImageFilter.MaxFilter(3))
    # logo
    lg = Image.open(logo_path).convert('RGBA'); lg = lg.crop(lg.getbbox())
    lg.thumbnail((int(R * 1.3), int(R * .95)), Image.LANCZOS)
    body_im.alpha_composite(lg, (cx - lg.width // 2 + int(R * (-.06 if mirror else .06)), cy - lg.height // 2 - int(R * .12)))
    body_im.putalpha(Image.fromarray(np.minimum(np.asarray(body_im.getchannel('A')), (body * 255).astype(np.uint8))))
    # shadows
    out = Image.new('RGBA', (D, D), (0, 0, 0, 0))
    sh = body_im.getchannel('A').filter(ImageFilter.GaussianBlur(10 * S)).point(lambda v: int(v * .45))
    out.paste((0, 0, 0, 255), (0, 12 * S), sh)
    out.alpha_composite(body_im)
    fsh = flap_im.getchannel('A').filter(ImageFilter.GaussianBlur(6 * S)).point(lambda v: int(v * .5))
    t = Image.new('RGBA', (D, D), (0, 0, 0, 0)); t.putalpha(fsh); out.alpha_composite(t, (3 * S, 6 * S))
    out.alpha_composite(flap_im)
    return out.resize((D // S, D // S), Image.LANCZOS)
import cv2
# 1) remove the original Yesha sticker (centre ~(552,120)) so the pair can be placed symmetrically
a = np.asarray(im.convert('RGB')).copy()
m = np.zeros(a.shape[:2], np.uint8); cv2.circle(m, (556, 124), 152, 255, -1)
a[:38][m[:38] > 0] = (255, 254, 254)                      # white frame strip
mp = m.copy(); mp[:38] = 0
src = np.roll(a, -300, axis=1)                              # same horizontal band of bokeh, 300px to the right
soft = cv2.GaussianBlur(mp, (0, 0), 10).astype(np.float32)[..., None] / 255
a = (a * (1 - soft) + src * soft).astype(np.uint8); a[:38][m[:38] > 0] = (255, 254, 254)
im = Image.fromarray(a).convert('RGBA')
# 2) two matching stickers, mirrored around the centre: Yesha right, Farms Union left
ye = sticker(HERE + '/../../../clients/yesha/logo.png', mirror=True)
un = sticker(HERE + '/../src/igud_hachavot.png', mirror=False)
CY, DX = 128, 150
for st, cx in [(un, 540 - DX), (ye, 540 + DX)]:
    im.alpha_composite(st, (cx - st.width // 2, CY - st.height // 2))
im.convert('RGB').save(HERE + '/cover.png'); print('ok')
