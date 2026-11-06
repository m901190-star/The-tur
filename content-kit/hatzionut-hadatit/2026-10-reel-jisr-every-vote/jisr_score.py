"""Original trailer-style score for the Jisr az-Zarqa reel (synthesised here, no samples, no copyright):
string ostinato in D minor, taikos, braams, risers, crashes, silence, and a big D-major finish."""
import numpy as np, wave, sys
sys.path.insert(0, '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/golan')
sys.path.insert(0, '/tmp/claude-0/-home-user-The-tur/1a5819ee-0cc0-5045-b086-4a8a80216453/scratchpad/golan2')
import make_jisr as g
SR = 48000; TOT = g.TOTAL; N = int(SR * (TOT + 4))
rng = np.random.default_rng(3)
L = np.zeros(N); R = np.zeros(N)
BEAT = 0.5; S16 = BEAT / 4
HOOK, S1, S2, FRZ, ASK, CLOSE, PUNCH = g.HOOK, g.S1[0], g.S2[0], g.FRZ[0], g.ASK[0], g.CLOSE[0], g.PUNCH
mhz = lambda m: 440 * 2 ** ((m - 69) / 12)

def put(x, at, gain=1.0, pan=0.0):
    i = int(at * SR)
    if i >= N: return
    x = x[:N - i]; L[i:i + len(x)] += x * gain * (1 - max(0, pan)); R[i:i + len(x)] += x * gain * (1 + min(0, pan))
def filt(x, lo=None, hi=None):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    if hi: X /= np.sqrt(1 + (f / hi) ** 4)
    if lo: X *= (f / lo) ** 2 / np.sqrt(1 + (f / lo) ** 4)
    return np.fft.irfft(X, len(x))
def reverb(x, sec=2.2, mix=.35):
    n = int(sec * SR); ir = rng.standard_normal(n) * np.exp(-np.arange(n) / SR / (sec / 5)); ir = filt(ir, hi=7000); ir /= np.sqrt((ir ** 2).sum())
    m = len(x) + n; y = np.fft.irfft(np.fft.rfft(x, m) * np.fft.rfft(ir, m), m); out = y * mix * 2.5; out[:len(x)] += x * (1 - mix); return out
def saw(f, n, det=0.0):
    t = np.arange(n) / SR; return 2 * ((f * (1 + det) * t + rng.random()) % 1) - 1
def adsr(n, a, d, s, r):
    e = np.full(n, s); A = int(a * SR); D = int(d * SR); Rl = int(r * SR)
    e[:A] = np.linspace(0, 1, max(A, 1))[:len(e[:A])]; e[A:A + D] = np.linspace(1, s, max(D, 1))[:len(e[A:A + D])]
    if Rl: e[-Rl:] *= np.linspace(1, 0, Rl)
    return e

# ---- instruments ----
def string_note(m, dur, bright=1.0):
    n = int(dur * SR); x = sum(saw(mhz(m), n, d) for d in (-.006, 0, .007)) / 3
    x = filt(x, lo=60, hi=900 + 1600 * bright); return x * adsr(n, .006, .05, .55, .03)
def taiko(big=1.0):
    n = int(1.6 * SR); t = np.arange(n) / SR; f = 95 * np.exp(-t * 9) + 46
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / .32)
    slap = filt(rng.standard_normal(n), lo=200, hi=2500) * np.exp(-t / .03)
    return reverb(np.tanh((body * 1.6 + slap * .5) * big), 2.4, .3)
def tom(p=1.0):
    n = int(.7 * SR); t = np.arange(n) / SR; f = 190 * p * np.exp(-t * 8) + 80 * p
    return reverb(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / .16) + .2 * filt(rng.standard_normal(n), lo=300, hi=3000) * np.exp(-t / .02), 1.6, .25)
def braam(d=2.8):
    n = int(d * SR); x = sum(saw(f, n, dt) for f in (36.7, 55.0, 73.4, 110.0) for dt in (-.004, 0, .005))
    x = np.tanh(filt(x, hi=520) * 2.6) * adsr(n, .02, .4, .6, 1.2); return reverb(x, 3.0, .4)
def crash(d=3.0):
    n = int(d * SR); t = np.arange(n) / SR; return reverb(filt(rng.standard_normal(n), lo=4500) * np.exp(-t / .9), 2.0, .3)
def riser(d):
    n = int(d * SR); t = np.arange(n) / SR; u = t / d
    x = filt(rng.standard_normal(n), lo=800) * u ** 2.5 + .5 * sum(np.sin(2 * np.pi * np.cumsum(mhz(50 + 30 * u) * (1 + k * .5)) / SR) for k in range(3)) * u ** 3
    return x
def chord(ms, d, bright=.6, att=.05):
    n = int(d * SR); x = sum(saw(mhz(m), n, dt) for m in ms for dt in (-.005, 0, .006)) / (3 * len(ms))
    return reverb(filt(x, lo=50, hi=700 + 2500 * bright) * adsr(n, att, .3, .85, 1.4), 3.0, .35)
def tick():
    n = int(.03 * SR); t = np.arange(n) / SR; return reverb((np.sin(2 * np.pi * 2600 * t) + .6 * rng.standard_normal(n)) * np.exp(-t / .004), 1.6, .5)

# ---- arrangement ----
OST = [50, 50, 53, 50, 57, 50, 53, 52, 50, 50, 53, 50, 58, 57, 53, 52]        # D minor 16ths
def ostinato(t0, t1, octave=0, gain=.3, bright=.5, ramp=False):
    k = 0; t = t0
    while t < t1 - 1e-6:
        u = (t - t0) / max(t1 - t0, .01)
        put(string_note(OST[k % 16] + 12 * octave, S16 * .95, bright + (.5 * u if ramp else 0)), t, gain * (0.8 + .4 * u if ramp else 1), pan=-.25)
        put(string_note(OST[k % 16] + 12 * octave + 12, S16 * .9, bright), t, gain * .45, pan=.3)
        k += 1; t += S16
# hook
for k in range(6): put(tick(), k * 0.45, .9)
ostinato(0.0, 2.0, -1, .22, .2); put(riser(1.0), 1.0, .3)
put(braam(), 2.0, .8); put(taiko(1.3), 2.0, 1.0); put(crash(), 2.0, .35)
# their clip, part 1: steady and low under the voice, a hit when Smotrich's name lands
ostinato(HOOK, S2, -1, .16, .3, ramp=True)
for t in np.arange(HOOK, S2, 2.0): put(taiko(.8), t, .55)
put(riser(.9), PUNCH - .9, .25); put(braam(2.2), PUNCH, .6); put(taiko(1.2), PUNCH, .8)
# part 2: "convinced me": the build
put(taiko(1.1), S2, .7); put(crash(), S2, .25)
ostinato(S2, FRZ, 0, .18, .4, ramp=True)
for t in np.arange(S2, FRZ, 1.0): put(taiko(.85), t, .6)
for t in np.arange(S2 + 4.0, FRZ, .5): put(tom(1.1), t + .25, .35)
put(riser(1.6), FRZ - 1.6, .45)
# freeze: "they recruit every vote"
put(braam(3.0), FRZ + .05, .95); put(taiko(1.5), FRZ + .05, 1.0); put(crash(), FRZ + .05, .45)
put(braam(2.0), FRZ + .45, .6); put(taiko(1.3), FRZ + .45, .9)
put(chord([38, 45, 50, 53, 57], ASK - FRZ, .4, .2), FRZ, .45)
# hard cut into silence, then "and you?"
cut = int(ASK * SR); fd = int(.015 * SR)
for ch in (L, R): ch[cut - fd:cut] *= np.linspace(1, 0, fd); ch[cut:] = 0
put(taiko(1.6), ASK + .35, 1.0); put(braam(2.0), ASK + .35, .7)
put(taiko(1.6), ASK + 1.2, 1.0); put(braam(2.4), ASK + 1.2, .9); put(crash(), ASK + 1.2, .4)
for k in range(8): put(tom(1 + k * .06), CLOSE - .8 + k * .1, .5)
put(riser(1.0), CLOSE - 1.0, .45)
# close: big D major
put(taiko(1.6), CLOSE, 1.0); put(crash(3.5), CLOSE, .5); put(braam(2.0), CLOSE, .5)
put(chord([38, 50, 54, 57, 62, 66], TOT - CLOSE + 1.5, .7, .03), CLOSE, .9)
ostinato(CLOSE + .55, TOT - .6, 0, .2, .8)
for dt in (.55, 1.15): put(taiko(1.3), CLOSE + dt, .9)
for t in np.arange(CLOSE + 1.6, TOT - .6, .5): put(taiko(.7), t, .45)
put(taiko(1.7), TOT - .55, 1.0); put(tick(), TOT - .55, .8)

x = np.stack([L, R], 1)[:int(TOT * SR)]
fade = int(.4 * SR); x[-fade:] *= np.linspace(1, 0, fade)[:, None]
x = np.tanh(x / max(1e-6, np.abs(x).max()) * 1.6) / np.tanh(1.6) * .95      # glue, loud like a trailer
w = wave.open(sys.argv[1], 'w'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32767).astype('<i2').tobytes()); w.close()
print('score', round(TOT, 2))
