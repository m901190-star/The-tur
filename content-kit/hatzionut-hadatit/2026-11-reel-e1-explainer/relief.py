"""Teal hillshaded relief map from Terrarium DEM + lat/lon projection helpers."""
import math, os, numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
D = np.load(HERE + '/data/dem.npz'); DEM = D['dem']; Z = int(D['z']); X0 = int(D['x0']); Y0 = int(D['y0'])
def gx(lon): return ((lon + 180) / 360 * 2 ** Z - X0) * 256
def gy(lat): r = math.radians(lat); return ((1 - math.log(math.tan(r) + 1 / math.cos(r)) / math.pi) / 2 * 2 ** Z - Y0) * 256
_shade = None
def shaded():
    global _shade
    if _shade is not None: return _shade
    z = DEM; dy, dx = np.gradient(z, 15.0)   # ~15 m/px at z13 (lat 31.8)
    slope = np.pi / 2 - np.arctan(np.hypot(dx, dy) * 1.6); asp = np.arctan2(-dx, dy)
    az, alt = math.radians(315), math.radians(40)
    hs = np.sin(alt) * np.sin(slope) + np.cos(alt) * np.cos(slope) * np.cos(az - asp); hs = np.clip(hs, 0, 1)
    stops = [(-420, (10, 26, 30)), (-200, (16, 40, 44)), (0, (24, 58, 62)), (300, (38, 84, 88)), (600, (62, 120, 126)), (850, (104, 168, 174)), (1000, (150, 200, 204))]
    e = np.clip(z, -420, 1000); col = np.zeros(z.shape + (3,), np.float32)
    for (a, ca), (b, cb) in zip(stops, stops[1:]):
        m = (e >= a) & (e <= b); t = ((e - a) / (b - a))[m][:, None]; col[m] = np.array(ca) * (1 - t) + np.array(cb) * t
    out = col * (0.45 + 0.75 * hs[..., None]); _shade = np.clip(out, 0, 255).astype(np.uint8); return _shade
class View:
    def __init__(self, lat, lon, ppx, W=1080, H=1920):   # ppx = screen px per DEM px
        self.cx, self.cy, self.s, self.W, self.H = gx(lon), gy(lat), ppx, W, H
    def xy(self, lat, lon): return ((gx(lon) - self.cx) * self.s + self.W / 2, (gy(lat) - self.cy) * self.s + self.H / 2)
    def render(self):
        S = shaded(); w, h = self.W / self.s, self.H / self.s; x0, y0 = self.cx - w / 2, self.cy - h / 2
        im = Image.fromarray(S).crop((int(x0), int(y0), int(x0 + w), int(y0 + h)))
        return im.resize((self.W, self.H), Image.LANCZOS)
