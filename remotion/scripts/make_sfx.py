"""
Synthesises the cartoon sound effects for the vacuum-balloon Short (48 kHz mono WAV,
peak -1 dBFS) into public/vacuum/sfx/. Run: python3 -I scripts/make_sfx.py
Every sound is built from sines, filtered noise and envelopes, so it is reproducible.
"""
import os
import wave

import numpy as np

SR = 48000
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'public', 'vacuum', 'sfx')
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(7)


def tt(dur):
    return np.arange(int(dur * SR)) / SR


def osc(freq):
    """Sine with a time-varying frequency array."""
    return np.sin(2 * np.pi * np.cumsum(freq) / SR)


def saw(freq, harmonics=8):
    ph = 2 * np.pi * np.cumsum(freq) / SR
    return sum(np.sin(k * ph) / k for k in range(1, harmonics + 1))


def noise(n):
    return rng.standard_normal(n)


def band(x, lo, hi):
    """Static band-pass by FFT with soft edges."""
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    w = 1 / (1 + (lo / np.maximum(f, 1)) ** 4) / (1 + (f / hi) ** 4)
    return np.fft.irfft(X * w, len(x))


def sweep_bp(x, fc, q=1.4):
    """Time-varying resonant band-pass (biquad, per-sample coefficients)."""
    y = np.zeros_like(x)
    x1 = x2 = y1 = y2 = 0.0
    for i in range(len(x)):
        w0 = 2 * np.pi * min(fc[i], SR * 0.45) / SR
        alpha = np.sin(w0) / (2 * q)
        cw = np.cos(w0)
        b0, b2 = alpha, -alpha
        a0, a1, a2 = 1 + alpha, -2 * cw, 1 - alpha
        yi = (b0 * x[i] + b2 * x2 - a1 * y1 - a2 * y2) / a0
        x2, x1 = x1, x[i]
        y2, y1 = y1, yi
        y[i] = yi
    return y


def env(n, attack, decay):
    t = np.arange(n) / SR
    return (1 - np.exp(-t / max(attack, 1e-4))) * np.exp(-t / decay)


def hump(n, peak=0.45, p=1.5):
    u = np.linspace(0, 1, n)
    a = np.where(u < peak, u / peak, (1 - u) / (1 - peak))
    return np.clip(a, 0, 1) ** p


def place(dst, src, at):
    i = int(at * SR)
    j = min(len(dst), i + len(src))
    dst[i:j] += src[: j - i]
    return dst


def save(name, x):
    x = np.asarray(x, dtype=np.float64)
    n = len(x)
    fade = min(int(0.003 * SR), n // 4)
    x[:fade] *= np.linspace(0, 1, fade)
    x[-fade:] *= np.linspace(1, 0, fade)
    peak = np.max(np.abs(x)) or 1
    x = x / peak * 10 ** (-1 / 20)
    with wave.open(os.path.join(OUT, name + '.wav'), 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())
    print(f'{name:14s} {n / SR:5.2f}s')


# ------------------------------------------------------------------ pops and clicks
def pop(f0, f1, dur=0.12, decay=0.035):
    t = tt(dur)
    f = f0 * (f1 / f0) ** (t / dur)
    x = osc(f) * env(len(t), 0.002, decay)
    click = band(noise(len(t)), 1500, 6000) * env(len(t), 0.0003, 0.003) * 0.4
    return x + click


save('pop', pop(320, 950))
save('pop_low', pop(190, 520, 0.14, 0.045))
t = tt(0.05)
save('tick', osc(np.full(len(t), 1900.0)) * env(len(t), 0.001, 0.012) + 0.3 * band(noise(len(t)), 3000, 9000) * env(len(t), 0.0002, 0.002))
t = tt(0.09)
c = np.zeros(len(t))
for at, f in ((0.0, 4200), (0.028, 3300)):
    s = osc(np.full(int(0.03 * SR), float(f))) * env(int(0.03 * SR), 0.0005, 0.006) + 0.5 * band(noise(int(0.03 * SR)), 2500, 9000) * env(int(0.03 * SR), 0.0002, 0.003)
    place(c, s, at)
save('click', c)

# ------------------------------------------------------------------ whooshes
def whoosh(dur, f0, f1, f2, q=1.2, peak=0.45):
    n = int(dur * SR)
    u = np.linspace(0, 1, n)
    fc = np.where(u < peak, f0 + (f1 - f0) * (u / peak), f1 + (f2 - f1) * ((u - peak) / (1 - peak)))
    x = sweep_bp(noise(n), fc, q)
    return x * hump(n, peak, 1.6)


save('whoosh', whoosh(0.75, 500, 1800, 700))
save('swish', whoosh(0.32, 900, 3200, 1200, 1.5, 0.4))
save('whoosh_down', whoosh(0.5, 2400, 1400, 380, 1.3, 0.3))
t = tt(0.4)
f = 450 * (1800 / 450) ** (t / 0.4) * (1 + 0.03 * np.sin(2 * np.pi * 18 * t))
save('whoosh_up', osc(f) * hump(len(t), 0.25, 1.2) * 0.8 + 0.5 * whoosh(0.4, 900, 3000, 2600, 1.6, 0.3))

# ------------------------------------------------------------------ rubber balloon
def squeak(dur, fa, fb, wob=6.0):
    t = tt(dur)
    f = fa + (fb - fa) * (t / dur) + 60 * np.sin(2 * np.pi * wob * t)
    x = band(saw(f, 10), 900, 4200)
    return x * hump(len(t), 0.3, 1.2)


save('squeak', squeak(0.24, 820, 1180))
save('squeak_sad', squeak(0.32, 1100, 640, 9))
nono = np.zeros(int(0.42 * SR))
place(nono, squeak(0.13, 900, 1050, 4), 0.0)
place(nono, squeak(0.13, 820, 980, 4), 0.2)
save('nono', nono)
gulp = np.zeros(int(0.2 * SR))
t = tt(0.09)
place(gulp, osc(260 * (120 / 260) ** (t / 0.09)) * env(len(t), 0.003, 0.03), 0)
place(gulp, pop(520, 300, 0.05, 0.012) * 0.7, 0.1)
save('gulp', gulp)

# ------------------------------------------------------------------ weights, thuds, boings
def thump(dur, f0, f1, decay):
    t = tt(dur)
    return osc(f0 * (f1 / f0) ** (t / dur)) * env(len(t), 0.002, decay)


th = thump(0.5, 95, 42, 0.12) + 0.6 * band(noise(int(0.5 * SR)), 40, 420) * env(int(0.5 * SR), 0.001, 0.03)
t = tt(0.5)
th += 0.35 * osc(160 + 25 * np.sin(2 * np.pi * 9 * t)) * env(len(t), 0.01, 0.16)
save('thud_heavy', th)

t = tt(0.55)
f = 230 + 190 * (1 - np.exp(-t / 0.06)) + 120 * np.sin(2 * np.pi * 13 * t) * np.exp(-t / 0.22)
save('boing', (osc(f) + 0.3 * osc(2 * f)) * env(len(t), 0.003, 0.2))

t = tt(0.35)
thud = thump(0.35, 120, 48, 0.09) + 0.7 * band(noise(len(t)), 40, 320) * env(len(t), 0.001, 0.025)
thud += 0.18 * (osc(np.full(len(t), 2230.0)) + osc(np.full(len(t), 3610.0))) * env(len(t), 0.001, 0.05)
save('thud', thud)

t = tt(0.28)
plop = thump(0.28, 190, 70, 0.06) + 0.4 * band(noise(len(t)), 80, 900) * env(len(t), 0.001, 0.02)
save('plop', plop)

t = tt(0.32)
stamp = thump(0.32, 105, 55, 0.07) + 0.8 * band(noise(len(t)), 300, 3200) * env(len(t), 0.0005, 0.018)
save('stamp', stamp)

# ------------------------------------------------------------------ pump, slurp, hose
def pump_stroke():
    n = int(0.34 * SR)
    air = band(noise(n), 1400, 5200) * env(n, 0.018, 0.12)
    thunk = thump(0.08, 140, 90, 0.025)
    x = air.copy()
    place(x, thunk * 0.8, 0)
    return x


save('pump', pump_stroke())
n = int(0.85 * SR)
u = np.linspace(0, 1, n)
sl = sweep_bp(noise(n), 2600 * (500 / 2600) ** u, 3.0)
sl *= (0.6 + 0.4 * np.sin(2 * np.pi * 14 * u * 0.85)) * hump(n, 0.2, 1.0)
save('slurp', sl)
t = tt(0.14)
save('pop_off', osc(520 * (160 / 520) ** (t / 0.14)) * env(len(t), 0.002, 0.04) + 0.3 * band(noise(len(t)), 800, 4000) * env(len(t), 0.001, 0.02))

# ------------------------------------------------------------------ crumple, crunch
def crackle(dur, rate, decay, lo=900, hi=7000, seed=1):
    n = int(dur * SR)
    x = np.zeros(n)
    r = np.random.default_rng(seed)
    tcur = 0.0
    while tcur < dur:
        tcur += r.exponential(1 / (rate * np.exp(-tcur / decay) + 1))
        i = int(tcur * SR)
        if i >= n - 200:
            break
        m = int(r.uniform(0.0006, 0.0025) * SR)
        x[i : i + m] += r.standard_normal(m) * np.exp(-np.arange(m) / (m / 3)) * r.uniform(0.3, 1.0)
    return band(x, lo, hi)


cr = crackle(0.6, 420, 0.18) * 1.0
place(cr, thump(0.22, 78, 42, 0.07) * 0.9, 0)
place(cr, squeak(0.26, 1150, 520, 10) * 0.25, 0.02)
save('crumple', cr)

t = tt(0.28)
crunch = crackle(0.28, 520, 0.06, 700, 6500, seed=4)
crunch += 0.35 * sum(osc(np.full(len(t), f)) * env(len(t), 0.001, d) for f, d in ((720, 0.12), (1180, 0.09), (1960, 0.06)))
save('crunch', crunch)

# ------------------------------------------------------------------ diamond
t = tt(0.9)
ting = sum(a * osc(np.full(len(t), 2093.0 * r)) * env(len(t), 0.003, d) for r, a, d in ((1, 1, 0.5), (1.5, 0.5, 0.35), (2, 0.35, 0.28), (3.01, 0.2, 0.2)))
ting *= 1 + 0.12 * np.sin(2 * np.pi * 7 * t)
save('ting', ting)

t = tt(0.5)
crack = 1.4 * band(noise(len(t)), 2000, 9000) * env(len(t), 0.0003, 0.008)
crack += sum(a * osc(np.full(len(t), f)) * env(len(t), 0.001, d) for f, a, d in ((1180, 0.5, 0.3), (2870, 0.45, 0.18), (4730, 0.35, 0.12), (6110, 0.25, 0.08)))
crack += 0.6 * thump(0.5, 95, 60, 0.06)
crack += 0.5 * crackle(0.5, 250, 0.08, 1500, 8000, seed=9)
save('crack', crack)

tk = np.zeros(int(0.5 * SR))
r = np.random.default_rng(3)
for k in range(7):
    f = r.uniform(3500, 7200)
    s = osc(np.full(int(0.08 * SR), f)) * env(int(0.08 * SR), 0.0005, 0.02)
    place(tk, s * r.uniform(0.4, 1.0), r.uniform(0, 0.38))
save('tinkle', tk)

t = tt(0.58)
f = 1500 * (470 / 1500) ** (t / 0.58) * (1 + 0.012 * np.sin(2 * np.pi * 9 * t))
save('whistle_fall', osc(f) * hump(len(t), 0.2, 0.8))

# ------------------------------------------------------------------ paper
n = int(0.5 * SR)
flut = np.abs(band(noise(n), 15, 70))
flut /= flut.max()
paper = band(noise(n), 900, 7000) * (0.25 + flut) * hump(n, 0.35, 1.0)
save('paper', paper)
