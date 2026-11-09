"""Timing van het script: per shot de gesproken woorden tegen de shotlengte.
Gebruik: python3 timing.py script.md [--fix] [--headers]
  --fix      verleng shots die te kort zijn (afgerond op 0,5 s) in het bestand
  --headers  herbereken de tijden in de scène- en deelkoppen
Norm: 2,6 woorden per seconde, + 0,35 s per '...' of ' -- ' pauze, + 0,6 s uitloop (G.9)."""
import math
import re
import sys

P = sys.argv[1]
FIX = "--fix" in sys.argv
HDR = "--headers" in sys.argv
lines = open(P).read().split("\n")

shot_re = re.compile(r"^(?:- )?\*\*(\d+[a-z0-9-]*[a-z0-9]?) · ([^*]*?)(\d+(?:,\d+)?) s\b")
scene_re = re.compile(r"^## Scène (\d+) · ")
end_re = re.compile(r"^(# |## [A-I]\. |---$)")
WPS = 2.6


def secs(x):
    return float(x.replace(",", "."))


def fmt(t):
    t = int(round(t))
    return f"{t // 60}:{t % 60:02d}"


shots = []  # (lineidx, id, dur, words, need, scene)
cur = None
scene = None
for i, L in enumerate(lines):
    m = scene_re.match(L)
    if m:
        scene = int(m.group(1))
        cur = None
        continue
    if end_re.match(L) and not L.startswith("# DEEL") and not L.startswith("# OUTRO"):
        if L.startswith("## ") or L.startswith("# B"):
            pass
    m = shot_re.match(L)
    if m and scene is not None:
        cur = dict(i=i, id=m.group(1), dur=secs(m.group(3)), text=[L], scene=scene)
        shots.append(cur)
        continue
    if L.startswith("#"):
        cur = None
        if L.startswith("# Bijlagen"):
            scene = None
        continue
    if cur is not None and not L.startswith("- **") or (cur is not None and L.startswith("- **") and not shot_re.match(L)):
        if cur is not None:
            cur["text"].append(L)

bad = []
for s in shots:
    txt = "\n".join(s["text"])
    quotes = re.findall(r"\"([^\"]+)\"", txt)
    spoken = " ".join(quotes)
    words = len(re.findall(r"[A-Za-z0-9',]+", spoken))
    pauses = spoken.count("...")
    need = (words / WPS + pauses * 0.35 + 0.6) if words else 0
    s["words"], s["need"] = words, need
    if need > s["dur"] + 0.05:
        bad.append(s)

for s in bad:
    new = math.ceil(s["need"] * 2) / 2
    print(f"TE KORT  {s['id']:6s} {s['dur']:4.1f} s, nodig {s['need']:4.1f} s ({s['words']} woorden) -> {new}")
    if FIX:
        L = lines[s["i"]]
        m = shot_re.match(L)
        st, en = m.span(3)
        lines[s["i"]] = L[:st] + ("%g" % new).replace(".", ",") + L[en:]
        s["dur"] = new

# scènetotalen
tot = {}
for s in shots:
    tot[s["scene"]] = tot.get(s["scene"], 0) + s["dur"]
t = 0
starts = {}
for sc in sorted(tot):
    starts[sc] = (t, t + tot[sc])
    t += tot[sc]
print("\nScène  start  eind   duur")
for sc, (a, b) in starts.items():
    print(f"{sc:5d}  {fmt(a):>5s}  {fmt(b):>5s}  {b - a:5.1f}")
print("TOTAAL", fmt(t), f"woorden {sum(s['words'] for s in shots)}")

if HDR:
    for i, L in enumerate(lines):
        m = scene_re.match(L)
        if m:
            sc = int(m.group(1))
            if sc in starts:
                a, b = starts[sc]
                lines[i] = re.sub(r"\(\d+:\d\d-\d+:\d\d\)", f"({fmt(a)}-{fmt(b)})", L, count=1)
    parts = {"DEEL 0": (0, 2), "DEEL 1": (3, 7), "DEEL 2": (8, 10), "DEEL 3": (11, 13), "DEEL 4": (14, 17), "DEEL 5": (18, 19), "OUTRO": (20, 20)}
    for i, L in enumerate(lines):
        for k, (a, b) in parts.items():
            if L.startswith("# " + k):
                lines[i] = re.sub(r"\(\d+:\d\d-\d+:\d\d\)", f"({fmt(starts[a][0])}-{fmt(starts[b][1])})", L, count=1)
if FIX or HDR:
    open(P, "w").write("\n".join(lines))
    print("bestand bijgewerkt")
