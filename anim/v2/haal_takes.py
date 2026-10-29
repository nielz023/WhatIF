"""Leest een opgeslagen ElevenLabs run-status (JSON), koppelt elke take aan een regel uit
videos/10x-faster/regels.tsv (op de prompttekst + stem) en zet de beste take in assets/audio/Fnn/.
Beste take: lengte het dichtst bij ~2,75 woorden/s (plus pauzetags), lange stiltes tellen als straf.
    python3 haal_takes.py status.json [...]
"""
import json, os, re, subprocess, sys, tempfile, urllib.request
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
VOICES = {"zfc8CJQpe8Kqyl0vvCzo": "Verteller", "MeDfWn0QGAwSljXBLc2G": "Broertje", "ogwqBH5bbF03DSbNiRNN": "Mama",
          "cCYjmrGZaI86GUJ7F2Nn": "Papa", "3XOBzXhnDY98yeWQ3GdM": "Vriend", "rHWSYoq8UlV0YIBKMryp": "Pestkop",
          "B52raBK48m23qWYbwchQ": "Wetenschapper"}
rows = [l.rstrip("\n").split("\t") for l in open(os.path.join(REPO, "videos/10x-faster/regels.tsv"), encoding="utf-8")]
by_text = {}
for rid, who, txt in rows:
    by_text.setdefault((txt.strip(), who), []).append(rid)

def expected(txt):
    w = len(re.sub(r"\[[^]]*\]", "", txt).split())
    return w / 2.75 + 0.35 * txt.count("[short pause]") + 1.0 * txt.count("[long pause]") + 0.3 * txt.count("…")

def longest_silence(path):
    log = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", "silencedetect=noise=-40dB:d=0.3", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    d = [float(x) for x in re.findall(r"silence_duration: ([\d.]+)", log)]
    return max(d or [0])

cands = {}
for p in sys.argv[1:]:
    data = json.load(open(p))
    for m in data.get("media", []):
        voice = (m.get("voice") or {}).get("voice_id")
        key = (m["prompt"].strip(), VOICES.get(voice, "?"))
        if key not in by_text:
            print("ONBEKEND", key); continue
        cands.setdefault(key, []).append(m)
for key, ms in cands.items():
    rid = by_text[key][0]
    exp = expected(key[0])
    scored = []
    for m in ms:
        tmp = tempfile.mktemp(suffix=".mp3")
        urllib.request.urlretrieve(m["url"], tmp)
        dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", tmp]))
        sil = longest_silence(tmp)
        allowed = 1.6 if "[long pause]" in key[0] else 0.9
        score = abs(dur - exp) / exp + 2.0 * max(0, sil - allowed)
        scored.append((score, dur, sil, tmp, m["generation_id"]))
    scored.sort()
    s, dur, sil, tmp, gid = scored[0]
    d = os.path.join(REPO, "assets/audio", rid[:3]); os.makedirs(d, exist_ok=True)
    out = os.path.join(d, f"{rid}_{key[1]}.mp3")
    os.replace(tmp, out)
    alt = " | ".join(f"{x[1]:.2f}s stil {x[2]:.2f}" for x in scored[1:])
    print(f"{rid} {key[1]:13s} gekozen {dur:5.2f}s (verwacht {exp:4.1f}, stilte {sil:.2f}) gen {gid}  anders: {alt}")
    with open(os.path.join(REPO, "videos/10x-faster/takes.log"), "a") as fh:
        fh.write(f"{rid}\t{gid}\t{dur:.2f}\n")
