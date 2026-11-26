"""Download Terrarium DEM tiles (AWS open data, Mapzen/Tilezen) for the Jerusalem–E1 area and save a float array."""
import math, io, os, urllib.request, numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); Z = 13
LAT0, LAT1, LON0, LON1 = 31.64, 31.96, 35.08, 35.52
def tx(lon): return (lon + 180) / 360 * 2 ** Z
def ty(lat): r = math.radians(lat); return (1 - math.log(math.tan(r) + 1 / math.cos(r)) / math.pi) / 2 * 2 ** Z
x0, x1 = int(tx(LON0)), int(tx(LON1)); y0, y1 = int(ty(LAT1)), int(ty(LAT0))
A = np.zeros(((y1 - y0 + 1) * 256, (x1 - x0 + 1) * 256), np.float32)
for x in range(x0, x1 + 1):
    for y in range(y0, y1 + 1):
        b = urllib.request.urlopen(f'https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{Z}/{x}/{y}.png').read()
        t = np.asarray(Image.open(io.BytesIO(b)).convert('RGB')).astype(np.float32)
        A[(y - y0) * 256:(y - y0 + 1) * 256, (x - x0) * 256:(x - x0 + 1) * 256] = t[..., 0] * 256 + t[..., 1] + t[..., 2] / 256 - 32768
np.savez_compressed(HERE + '/data/dem.npz', dem=A, z=Z, x0=x0, y0=y0); print(A.shape, A.min(), A.max())
