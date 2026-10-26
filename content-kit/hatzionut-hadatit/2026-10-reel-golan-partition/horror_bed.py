"""Horror sound bed for the Golan reel, synthesised (no music): drone, braams, reverse swells, tinnitus, screech, rising tension, silence."""
import numpy as np, wave, sys
sys.path.insert(0, '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/golan')
import make_golan as g
SR = 48000; T = g.TOTAL + 3.0; N = int(SR * T)
rng = np.random.default_rng(7)
L = np.zeros(N); R = np.zeros(N)
t_all = np.arange(N) / SR

def put(x, at, gain=1.0, pan=0.0):
    i = int(at * SR); x = x[:max(0, N - i)]
    L[i:i + len(x)] += x * gain * (1 - max(0, pan)); R[i:i + len(x)] += x * gain * (1 + min(0, pan))
def env(n, a, d):
    t = np.arange(n) / SR; return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)
def lp(x, fc):                     # one-pole low-pass
    a = np.exp(-2 * np.pi * fc / SR); y = np.empty_like(x); s = 0.0
    for i in range(len(x)): s = (1 - a) * x[i] + a * s; y[i] = s
    return y
def lp_fast(x, fc):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X /= np.sqrt(1 + (f / fc) ** 4); return np.fft.irfft(X, len(x))
def hp_fast(x, fc):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X *= (f / fc) ** 2 / np.sqrt(1 + (f / fc) ** 4); return np.fft.irfft(X, len(x))
def reverb(x, sec=2.5, mix=.5):
    n = int(sec * SR); ir = rng.standard_normal(n) * np.exp(-np.arange(n) / SR / (sec / 5)); ir = lp_fast(ir, 6000); ir /= np.sqrt((ir ** 2).sum())
    m = len(x) + n; y = np.fft.irfft(np.fft.rfft(x, m) * np.fft.rfft(ir, m), m)
    out = np.zeros(m); out[:len(x)] += x * (1 - mix); out += y * mix * 3; return out
def saw(f, n, det=0.0):
    t = np.arange(n) / SR; ph = (f * (1 + det)) * t; return 2 * (ph % 1) - 1

def braam(d=2.6):
    n = int(d * SR); x = sum(saw(f, n, dt) for f in (41.2, 61.7, 82.4, 55.0) for dt in (-.004, .0, .005))
    x = np.tanh(lp_fast(x, 380) * 2.2)
    return reverb(x * env(n, .03, .9), 3.0, .45)
def boom(d=3.0):
    n = int(d * SR); t = np.arange(n) / SR; f = 70 * np.exp(-t * 3) + 28
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, .005, .7)
    return reverb(np.tanh(x * 2) + .3 * lp_fast(rng.standard_normal(n), 200) * env(n, .002, .25), 3.5, .35)
def reverse_swell(d=1.1):
    n = int(d * SR); x = hp_fast(rng.standard_normal(n), 900) * np.linspace(0, 1, n) ** 3
    x += .4 * np.sin(2 * np.pi * np.cumsum(np.linspace(120, 900, n)) / SR) * np.linspace(0, 1, n) ** 4
    return reverb(x, 1.5, .5)[::-1][-n:] if False else x
def tick(at, gain):
    n = int(.03 * SR); t = np.arange(n) / SR; x = (np.sin(2 * np.pi * 2600 * t) + .6 * rng.standard_normal(n)) * np.exp(-t / .004)
    put(reverb(x, 1.8, .55), at, gain)
def tinnitus(d):
    n = int(d * SR); t = np.arange(n) / SR
    x = np.sin(2 * np.pi * 3150 * t) * (.6 + .4 * np.sin(2 * np.pi * 7 * t)) + .5 * np.sin(2 * np.pi * 3170 * t)
    return x * np.minimum(1, t / .05) * np.minimum(1, (d - t) / .4)
def screech(d=1.4):
    n = int(d * SR); t = np.arange(n) / SR; x = 0
    for f0, dt in ((3200, 0), (3330, .1), (2900, .2), (4100, .05)):
        f = f0 * np.exp(-t * 0.9) ; x = x + np.sin(2 * np.pi * np.cumsum(f) / SR + dt)
    x = x / 4 + .3 * hp_fast(rng.standard_normal(n), 3000)
    return reverb(x * env(n, .01, .45), 2.0, .5)
def tension(d):
    """Detuned cluster gliding upward: the dread that builds over the map."""
    n = int(d * SR); t = np.arange(n) / SR; x = 0
    for f0 in (180, 190.5, 254, 269):
        f = f0 * 2 ** (1.6 * t / d); x = x + np.sin(2 * np.pi * np.cumsum(f) / SR)
    return x / 4 * (t / d) ** 1.5
def drone(d):
    n = int(d * SR); x = sum(saw(f, n, dt) for f in (32.7, 49.0, 46.2) for dt in (-.003, .003))
    x = lp_fast(x, 140) + .35 * lp_fast(rng.standard_normal(n), 90)
    return x / 3

# --- timeline ---
HOOK, FRZ, G1, G2, MAP, HUSH, TURN, CLOSE = g.HOOK, g.FRZ[0], g.G1[0], g.G2[0], g.MAP[0], g.HUSH[0], g.TURN[0], g.CLOSE[0]
dr = drone(HUSH); de = np.ones(len(dr))
tt = np.arange(len(dr)) / SR
de *= np.minimum(1, tt / 0.3)                                    # fade in
de *= np.where((tt > G1) & (tt < HUSH), 1.0, 1.0)
de *= 0.55 + 0.45 * np.clip((tt - MAP) / 5.5, 0, 1) * (tt > MAP)  # swells over the map
de[-int(.01 * SR):] = np.linspace(1, 0, int(.01 * SR))           # hard cut into silence
put(dr * de, 0, .55)
tick(0.0, 1.0)
for k in range(5): tick(0.45 + k * 0.5, 1.0 if k < 2 else .6)    # the clock
put(reverse_swell(1.1), 2.0 - 1.1, .35)
put(braam(), 2.0, .55); put(boom(), 2.0, .7)
put(reverse_swell(1.0), FRZ - 1.0, .3)
put(braam(3.0), FRZ, .5); put(tinnitus(1.5), FRZ, .045)
put(tension(HUSH - MAP), MAP, .12, .2); put(tension(HUSH - MAP)[::1] * 1.0, MAP, .1, -.2)
put(boom(2.5), MAP, .45)
put(reverse_swell(.8), MAP + 1.7 - .8, .3); put(screech(), MAP + 1.7, .16); put(braam(2.2), MAP + 1.7, .4)
put(boom(2.5), MAP + 2.2, .45)
put(reverse_swell(.8), MAP + 4.8 - .8, .35); put(braam(2.5), MAP + 4.8, .6); put(boom(), MAP + 4.8, .7)
# silence: everything is cut hard at HUSH
cut = int(HUSH * SR); fade = int(.012 * SR)
for ch in (L, R):
    ch[cut - fade:cut] *= np.linspace(1, 0, fade); ch[cut:int(TURN * SR)] = 0
# relief and close: a soft swell up, one last tick with a long tail
up = hp_fast(rng.standard_normal(int(1.2 * SR)), 2000) * np.linspace(0, 1, int(1.2 * SR)) ** 2
put(up, TURN - 0.1, .12)
put(boom(3.0), CLOSE + 0.55, .35)
tick(g.TOTAL - 0.55, .9)
x = np.stack([L, R], 1)[:int(g.TOTAL * SR)]; x /= max(1e-6, np.abs(x).max()) / 0.9
w = wave.open(sys.argv[1], 'w'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32767).astype('<i2').tobytes()); w.close()
print('bed', round(g.TOTAL, 2))
