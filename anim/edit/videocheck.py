"""Videocheck op een gerenderde scène of montage (mp4), zonder Blender. Lessen video 2 en 3.

Vindt in het BEELD wat de scènecheck (qc.txt) niet ziet:
  FLITS      1-3 frames die sterk afwijken van ervoor én erna (witte/grijze flits, paal voor de lens, 2:51 video 3)
  ZWART      frames die (bijna) zwart zijn buiten een bewuste fade
  WIT        frames die (bijna) helemaal wit zijn (overbelichte UE-shot 10:46 video 3)
  STIL       beeld dat langer dan --stil seconden niet verandert (bevroren render, ontbrekende frames)
  GELUID     integrated loudness niet -14 ±1 LUFS of true peak boven -1 dBTP
En per melding een contactvel (10 beelden/s rond het moment) in <uit>/check_<mm-ss>.png om zelf te bekijken.

    python3 anim/edit/videocheck.py WHAT_IF_NO_RULES_preview.mp4 --uit check/
    python3 anim/edit/videocheck.py out/n07b/n07b.mp4 --geen-geluid

Op niels' pc: dezelfde aanroep met python (ffmpeg moet in PATH staan). Eindcode 1 als er meldingen zijn.
"""
import argparse
import json
import os
import re
import subprocess
import sys


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def probe(path):
    r = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate,nb_frames",
             "-show_entries", "format=duration", "-of", "json", path])
    d = json.loads(r.stdout)
    num, den = d["streams"][0]["r_frame_rate"].split("/")
    return float(num) / float(den), float(d["format"]["duration"])


def frame_stats(path):
    """Gemiddelde helderheid (YAVG, 0-255) en verschil met het vorige frame (gemiddelde |dY|) per frame."""
    vf = "scale=240:-2,signalstats,metadata=print:file=-"
    r = run(["ffmpeg", "-v", "error", "-i", path, "-vf", vf, "-an", "-f", "null", "-"])
    yavg, ydif = [], []
    for line in r.stdout.splitlines():
        m = re.search(r"lavfi\.signalstats\.(YAVG|YDIF)=([\d.]+)", line)
        if m:
            (yavg if m.group(1) == "YAVG" else ydif).append(float(m.group(2)))
    return yavg, ydif


def tiny_frames(path, w=48, h=27):
    """Alle frames als lijst van bytes (grijs, w x h): genoeg om flitsen te zien, zonder numpy."""
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", f"scale={w}:{h},format=gray", "-an",
                        "-f", "rawvideo", "-"], capture_output=True)
    b, sz = r.stdout, w * h
    return [b[k:k + sz] for k in range(0, len(b) - sz + 1, sz)]


def mad(a, b):
    """Gemiddeld absoluut verschil (0-255) tussen twee mini-frames."""
    return sum(abs(x - y) for x, y in zip(a, b)) / len(a)


def loudness(path):
    r = run(["ffmpeg", "-v", "info", "-nostats", "-i", path, "-af", "ebur128=peak=true", "-vn", "-f", "null", "-"])
    txt = r.stderr
    i = re.findall(r"I:\s+(-?[\d.]+) LUFS", txt)
    p = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", txt)
    return (float(i[-1]) if i else None), (float(p[-1]) if p else None)


def tc(t):
    return f"{int(t // 60)}:{t % 60:05.2f}"


def sheet(path, t, out, fps):
    """10 beelden per seconde van t-1,0 tot t+1,0 s in een raster, met tijd op elk beeld."""
    t0 = max(0.0, t - 1.0)
    name = os.path.join(out, f"check_{int(t // 60):02d}-{t % 60:05.2f}.png".replace(".", "_", 1))
    vf = ("fps=10,scale=320:-2,drawtext=text='%{pts\\:hms}':x=6:y=6:fontsize=18:fontcolor=white:box=1:boxcolor=black@0.6,"
          "tile=5x4")
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t0:.3f}", "-t", "2.0", "-i", path, "-vf", vf, "-frames:v", "1",
         "-copyts", name])
    return name


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--uit", default=None, help="map voor contactvellen en rapport (standaard naast de video)")
    ap.add_argument("--stil", type=float, default=4.0, help="bevroren beeld langer dan dit (s) melden")
    ap.add_argument("--flits", type=float, default=25.0, help="afwijking (0-255 per pixel) voor een flits")
    ap.add_argument("--geen-geluid", action="store_true")
    ap.add_argument("--geen-vellen", action="store_true")
    a = ap.parse_args()
    out = a.uit or os.path.join(os.path.dirname(os.path.abspath(a.video)), "videocheck")
    os.makedirs(out, exist_ok=True)
    fps, dur = probe(a.video)
    yavg, ydif = frame_stats(a.video)
    n = len(yavg)
    rows = []

    def add(kind, i, msg):
        rows.append((kind, i / fps, msg))

    # FLITS: 1-3 frames die sterk afwijken van het frame ervoor én erna, terwijl ervoor en erna op elkaar lijken
    # (witte/grijze flits, een paal voor de lens, een los verkeerd frame). Op mini-frames van 48x27 grijs.
    tiny = tiny_frames(a.video)
    i = 1
    while i < len(tiny) - 1:
        hit = False
        for w in (1, 2, 3):
            if i + w >= len(tiny):
                break
            ref = mad(tiny[i - 1], tiny[i + w])
            dev = min(mad(tiny[i - 1], tiny[k]) for k in range(i, i + w))
            if dev > a.flits and ref < dev * 0.35:
                d = yavg[i] - yavg[i - 1] if i < n else 0
                kind = "lichter" if d > 8 else ("donkerder" if d < -8 else "ander beeld")
                add("FLITS", i, f"{w} frame(s) {kind} (afwijking {dev:.0f}, ervoor/erna {ref:.0f})")
                i += w
                hit = True
                break
        if not hit:
            i += 1
    # ZWART / WIT
    for kind, test in (("ZWART", lambda y: y < 10), ("WIT", lambda y: y > 235)):
        j = 0
        while j < n:
            if test(yavg[j]):
                k = j
                while k < n and test(yavg[k]):
                    k += 1
                fade = kind == "ZWART" and (j == 0 or k >= n - 2 or (j > 2 and yavg[j - 3] > yavg[j - 1] + 3))
                if not fade:
                    add(kind, j, f"{k - j} frame(s), helderheid {min(yavg[j:k]):.0f}-{max(yavg[j:k]):.0f}")
                j = k
            j += 1
    # STIL: beeld verandert niet (YDIF ~0) langer dan --stil
    j = 1
    while j < len(ydif):
        if ydif[j] < 0.05:
            k = j
            while k < len(ydif) and ydif[k] < 0.05:
                k += 1
            if (k - j) / fps > a.stil:
                add("STIL", j, f"{(k - j) / fps:.1f} s geen enkele beweging")
            j = k
        j += 1
    if not a.geen_geluid:
        lufs, peak = loudness(a.video)
        if lufs is None:
            rows.append(("GELUID", 0.0, "geen geluidsspoor gevonden"))
        else:
            if abs(lufs + 14) > 1.0:
                rows.append(("GELUID", 0.0, f"loudness {lufs:.1f} LUFS (moet -14)"))
            if peak is not None and peak > -1.0:
                rows.append(("GELUID", 0.0, f"true peak {peak:.1f} dBFS (max -1)"))
            print(f"GELUID {lufs} LUFS, peak {peak} dBFS")
    rows.sort(key=lambda r: r[1])
    rep = [f"VIDEOCHECK {a.video}  ({tc(dur)}, {fps:.0f} fps, {n} frames)"]
    for kind, t, msg in rows:
        line = f"{kind:7s} {tc(t)}  {msg}"
        if not a.geen_vellen and kind in ("FLITS", "ZWART", "WIT", "STIL"):
            line += "  -> " + os.path.basename(sheet(a.video, t, out, fps))
        rep.append(line)
    rep.append("OK" if not rows else f"{len(rows)} melding(en)")
    with open(os.path.join(out, "videocheck.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(rep) + "\n")
    print("\n".join(rep))
    sys.exit(1 if rows else 0)


if __name__ == "__main__":
    main()
