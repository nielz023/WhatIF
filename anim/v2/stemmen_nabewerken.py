"""Stemmen van video 2 nabewerken (eenmalig, op de ruwe ElevenLabs-takes).

- stilte aan begin en eind -> 0,05 s;
- pauzes binnen een regel -> max 0,4 s; bij een [short pause]-tag max 0,6 s, bij [long pause] max 1,2 s
  (les uit video 1: Eleven v3 zet veel te lange stiltes in de clips);
- regels die we 'vanuit hem' horen (iedereen behalve de verteller vanaf dag 2) krijgen een
  extra versie *_traag.mp3: 3x zo traag en diep, als verre donder (de tekst staat als ondertitel in beeld).

    python3 anim/v2/stemmen_nabewerken.py <map met ruwe takes F01..F13>
"""
import os, re, subprocess, sys
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = sys.argv[1]
TRAAG = {"F05-06", "F06-07", "F07-03", "F09-06"}
rows = {r: t for r, w, t in (l.rstrip("\n").split("\t") for l in open(os.path.join(REPO, "videos/10x-faster/regels.tsv")))}


def silences(p, d=0.3):
    log = subprocess.run(["ffmpeg", "-hide_banner", "-i", p, "-af", f"silencedetect=noise=-42dB:d={d}", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", log)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]))
    if len(en) < len(st):
        en.append(dur)
    return [(max(0.0, a), b) for a, b in zip(st, en)], dur


for folder in sorted(os.listdir(SRC)):
    for fn in sorted(os.listdir(os.path.join(SRC, folder))):
        if not fn.endswith(".mp3") or "_traag" in fn:
            continue
        rid = fn[:6]
        txt = rows[rid]
        mx = 1.2 if "[long pause]" in txt else (0.6 if "[short pause]" in txt else 0.4)
        p = os.path.join(SRC, folder, fn)
        sil, dur = silences(p)
        keep, t = [], 0.0
        for a, b in sil:
            if a <= 0.01:                       # begin
                t = max(0.0, b - 0.05)
                continue
            if b >= dur - 0.01:                 # eind
                keep.append((t, min(dur, a + 0.08)))
                t = None
                break
            if b - a > mx:
                keep.append((t, a + mx / 2))
                t = b - mx / 2
        if t is not None:
            keep.append((t, dur))
        flt = "".join(f"[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS[s{i}];" for i, (a, b) in enumerate(keep))
        flt += "".join(f"[s{i}]" for i in range(len(keep))) + f"concat=n={len(keep)}:v=0:a=1,afade=t=in:d=0.02[o]"
        out = os.path.join(REPO, "assets/audio", folder, fn)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", p, "-filter_complex", flt, "-map", "[o]", "-c:a", "libmp3lame",
                        "-q:a", "2", out], check=True)
        nd = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out]))
        print(f"{rid} {dur:5.2f} -> {nd:5.2f} s")
        if rid in TRAAG:
            slow = out.replace(".mp3", "_traag.mp3")
            # 3x trager en ~1,5 octaaf lager (asetrate), dan dof en ver weg
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", out, "-af",
                            "asetrate=44100*0.36,aresample=44100,lowpass=f=700,aecho=0.8:0.7:120:0.35,volume=1.6",
                            "-c:a", "libmp3lame", "-q:a", "2", slow], check=True)
