"""haal.py <regel-id> <url1> [url2 ...]: downloadt de takes van een regel uit videos/no-rules/regels.tsv,
kiest de beste (lengte het dichtst bij ~2,75 woorden/s, lange stiltes tellen als straf) en zet hem in
assets/audio/<Nnn>/<id>_<spreker>.mp3. Logt de keuze in videos/no-rules/takes.log."""
import os, re, subprocess, sys, tempfile, urllib.request
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
rows = {l.split("\t")[0]: l.rstrip("\n").split("\t") for l in open(os.path.join(REPO, "videos/no-rules/regels.tsv"), encoding="utf-8")}

def expected(txt):
    w = len(re.sub(r"\[[^]]*\]", "", txt).split())
    return w / 2.75 + 0.3 * txt.count("…") + 0.4

def silences(path):
    log = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", "silencedetect=noise=-40dB:d=0.3", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    return [float(x) for x in re.findall(r"silence_duration: ([\d.]+)", log)]

rid, urls = sys.argv[1], sys.argv[2:]
_, who, txt = rows[rid]
exp = expected(txt)
best = None
for u in urls:
    tmp = tempfile.mktemp(suffix=".mp3")
    for k in range(3):
        try:
            urllib.request.urlretrieve(u, tmp); break
        except Exception:
            pass
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", tmp]))
    sil = max(silences(tmp) or [0])
    score = abs(dur - exp) / exp + 2.0 * max(0, sil - 0.9)
    if best is None or score < best[0]:
        best = (score, dur, sil, tmp)
d = os.path.join(REPO, "assets/audio", rid[:3]); os.makedirs(d, exist_ok=True)
out = os.path.join(d, f"{rid}_{who}.mp3")
os.replace(best[3], out)
print(f"{rid} {who:13s} {best[1]:5.2f}s (verwacht {exp:4.1f}, stilte {best[2]:.2f})")
with open(os.path.join(REPO, "videos/no-rules/takes.log"), "a") as fh:
    fh.write(f"{rid}\t{best[1]:.2f}\n")
