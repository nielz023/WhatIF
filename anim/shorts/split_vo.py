"""Knipt een voice-over (één take per short) in losse zinnen voor de scènescripts.

    python3 anim/shorts/split_vo.py <take.mp3> <code> <scripts.md-sectie als tekstbestand>

Zoekt alle stiltes, kiest daaruit de grenzen die het best passen bij de lengte van elke zin (in tekens)
en schrijft assets/audio/<CODE>/<CODE>-NN_Verteller.mp3. Pauzes binnen een zin worden niet aangeraakt.
"""
import os
import re
import subprocess
import sys

take, code, txt = sys.argv[1], sys.argv[2].upper(), sys.argv[3]
lines = [l.strip() for l in open(txt) if l.strip()]
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
out = os.path.join(REPO, "assets", "audio", code)
os.makedirs(out, exist_ok=True)

dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", take]))
log = subprocess.run(["ffmpeg", "-hide_banner", "-i", take, "-af", "silencedetect=noise=-40dB:d=0.18", "-f", "null", "-"],
                     capture_output=True, text=True).stderr
starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]
ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
sil = [(a, b) for a, b in zip(starts, ends) if a > 0.2 and b < dur - 0.2]
speech0 = ends[0] if starts and starts[0] < 0.05 else 0.0
speech1 = starts[-1] if len(starts) > len(ends) or (starts and starts[-1] > ends[-1]) else dur

# doel: grens k ligt op het aandeel tekens van zin 0..k
w = [len(re.sub(r"\[[^]]*\]", "", l)) for l in lines]
tot = sum(w)
cum = [sum(w[:k + 1]) / tot for k in range(len(w) - 1)]
span = speech1 - speech0
target = [speech0 + c * span for c in cum]

# dynamisch programmeren: kies len(lines)-1 stiltes (oplopend) die het dichtst bij de doelen liggen; lange stiltes tellen mee
n, m = len(target), len(sil)
INF = 1e9
cost = [[INF] * (m + 1) for _ in range(n + 1)]
back = [[None] * (m + 1) for _ in range(n + 1)]
for j in range(m + 1):
    cost[0][j] = 0.0
for i in range(1, n + 1):
    for j in range(i, m + 1):
        a, b = sil[j - 1]
        mid = (a + b) / 2
        c = (mid - target[i - 1]) ** 2 - 0.6 * (b - a)
        best = min(range(i - 1, j), key=lambda k: cost[i - 1][k])
        cost[i][j] = cost[i - 1][best] + c
        back[i][j] = best
j = min(range(n, m + 1), key=lambda k: cost[n][k])
pick = []
for i in range(n, 0, -1):
    pick.append(sil[j - 1])
    j = back[i][j]
pick.reverse()

bounds = [max(0.0, speech0 - 0.05)] + [p for s in pick for p in (s[0] + 0.06, s[1] - 0.06)] + [min(dur, speech1 + 0.15)]
for k, l in enumerate(lines):
    a, b = bounds[2 * k], bounds[2 * k + 1]
    f = os.path.join(out, f"{code}-{k + 1:02d}_Verteller.mp3")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-to", f"{b:.3f}", "-i", take, "-af",
                    "afade=t=in:d=0.02,areverse,afade=t=in:d=0.04,areverse", "-c:a", "libmp3lame", "-q:a", "2", f], check=True)
    print(f"{code}-{k + 1:02d} {a:6.2f}-{b:6.2f} ({b - a:4.2f} s) {l[:60]}")
