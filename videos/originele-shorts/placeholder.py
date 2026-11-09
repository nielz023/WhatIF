"""Tijdelijke stille stemregels (geschatte duur) zodat de scènes al gebouwd kunnen worden.
Worden vervangen door de echte ElevenLabs-takes (zelfde bestandsnamen)."""
import csv, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
AUDIO = os.path.join(HERE, "..", "..", "assets", "audio")
rows = [l.rstrip("\n").split("\t") for l in open(os.path.join(HERE, "regels.tsv"), encoding="utf-8") if l.strip()]
by = {}
for rid, txt in rows:
    by.setdefault(rid[:3], []).append(txt)
    d = os.path.join(AUDIO, rid[:3]); os.makedirs(d, exist_ok=True)
    p = os.path.join(d, f"{rid}_Verteller.mp3")
    if os.path.exists(p) and "--force" not in sys.argv:
        continue
    words = len(txt.split()); dots = txt.count("...") + txt.count(".") * 0.5
    dur = words / 2.75 + dots * 0.18 + 0.15
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", f"{dur:.2f}",
                    "-b:a", "64k", p], check=True)
for code, lines in by.items():
    open(os.path.join(AUDIO, code, "zinnen.txt"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("ok", len(rows))
