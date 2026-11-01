"""Nieuwe voice-overs van de shorts uit video 2: beste take kiezen en stiltes inkorten.

    python3 anim/shorts_v2/stemmen.py <map met takes S1-01_0.mp3, S1-01_1.mp3, ...>

Beste take: lengte het dichtst bij ~2,75 woorden/s, lange stiltes tellen als straf (zoals anim/v2/haal_takes.py).
Daarna: stilte begin/eind -> 0,05 s, pauzes binnen een regel max 0,4 s (0,6 s bij [short pause]).
Uitvoer: assets/audio/V2S/<regel>_Verteller.mp3
"""
import glob, os, re, subprocess, sys
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = sys.argv[1]
rows = {r: t for r, _, t in (l.rstrip("\n").split("\t") for l in open(os.path.join(REPO, "videos/10x-faster/shorts/regels_shorts.tsv"), encoding="utf-8"))}


def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]))


def silences(p, d=0.3):
    log = subprocess.run(["ffmpeg", "-hide_banner", "-i", p, "-af", f"silencedetect=noise=-42dB:d={d}", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", log)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
    D = dur(p)
    if len(en) < len(st):
        en.append(D)
    return [(max(0.0, a), b) for a, b in zip(st, en)], D


def expected(txt):
    w = len(re.sub(r"\[[^]]*\]", "", txt).split())
    return w / 2.75 + 0.35 * txt.count("[short pause]") + 0.3 * txt.count("…")


for rid, txt in rows.items():
    takes = sorted(glob.glob(os.path.join(SRC, f"{rid}_*.mp3")))
    if not takes:
        print("ONTBREEKT", rid)
        continue
    exp = expected(txt)
    scored = []
    for p in takes:
        sil, D = silences(p)
        inner = [b - a for a, b in sil if a > 0.01 and b < D - 0.01]
        scored.append((abs(D - exp) / exp + 2.0 * max(0, max(inner or [0]) - 0.9), p))
    p = sorted(scored)[0][1]
    mx = 0.6 if "[short pause]" in txt else 0.4
    sil, D = silences(p)
    keep, t = [], 0.0
    for a, b in sil:
        if a <= 0.01:
            t = max(0.0, b - 0.05)
            continue
        if b >= D - 0.01:
            keep.append((t, min(D, a + 0.08)))
            t = None
            break
        if b - a > mx:
            keep.append((t, a + mx / 2))
            t = b - mx / 2
    if t is not None:
        keep.append((t, D))
    flt = "".join(f"[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS[s{i}];" for i, (a, b) in enumerate(keep))
    flt += "".join(f"[s{i}]" for i in range(len(keep))) + f"concat=n={len(keep)}:v=0:a=1,afade=t=in:d=0.02[o]"
    out = os.path.join(REPO, "assets/audio/V2S", f"{rid}_Verteller.mp3")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", p, "-filter_complex", flt, "-map", "[o]", "-c:a", "libmp3lame",
                    "-q:a", "2", out], check=True)
    print(f"{rid} take {os.path.basename(p)} {D:5.2f} -> {dur(out):5.2f} s (verwacht {exp:.1f})")
