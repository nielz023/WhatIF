"""Knipt de gekozen ElevenLabs-take per short in losse zinnen op woordtijden (Scribe-transcriptie).

    python3 videos/originele-shorts/knip.py            (alle OR-shorts)

Leest regels.tsv, woorden/ORn.json en /mnt/project-files/shorts/originelen/vo_takes/ORn_GEKOZEN.mp3.
Schrijft assets/audio/ORn/ORn-NN_Verteller.mp3 en woorden/ORn_regels.json (woordtijden per regel, t.o.v. regelstart)
voor de ondertiteling.
"""
import json, os, re, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
TAKES = "/mnt/project-files/shorts/originelen/vo_takes"
rows = [l.rstrip("\n").split("\t") for l in open(os.path.join(HERE, "regels.tsv"), encoding="utf-8") if l.strip()]
codes = sorted({r[0][:3] for r in rows})
norm = lambda s: re.sub(r"[^a-z0-9']", "", s.lower())
for code in codes:
    lines = [(rid, t) for rid, t in rows if rid.startswith(code)]
    words = [w for w in json.load(open(os.path.join(HERE, "woorden", code + ".json")))["words"] if w["type"] == "word"]
    take = os.path.join(TAKES, f"{code}_GEKOZEN.mp3")
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", take]))
    i, spans = 0, []
    for rid, txt in lines:
        n = len(txt.split())
        ws = words[i:i + n]
        assert [norm(w["text"]) for w in ws] == [norm(x) for x in txt.split()], (rid, [w["text"] for w in ws])
        spans.append(ws)
        i += n
    assert i == len(words), code
    out = os.path.join(REPO, "assets", "audio", code)
    os.makedirs(out, exist_ok=True)
    meta = {}
    for k, ((rid, txt), ws) in enumerate(zip(lines, spans)):
        a = 0.0 if k == 0 else (spans[k - 1][-1]["end"] + ws[0]["start"]) / 2
        a = max(a, ws[0]["start"] - 0.12)
        b = dur if k == len(lines) - 1 else (ws[-1]["end"] + spans[k + 1][0]["start"]) / 2
        b = min(b, ws[-1]["end"] + 0.18) if k < len(lines) - 1 else min(dur, ws[-1]["end"] + 0.3)
        f = os.path.join(out, f"{rid}_Verteller.mp3")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-to", f"{b:.3f}", "-i", take, "-af",
                        "afade=t=in:d=0.015,areverse,afade=t=in:d=0.04,areverse", "-c:a", "libmp3lame", "-q:a", "2", f], check=True)
        meta[rid] = [dict(w=w["text"], s=round(w["start"] - a, 3), e=round(w["end"] - a, 3)) for w in ws]
        print(f"{rid} {a:6.2f}-{b:6.2f} ({b - a:4.2f} s) {txt}")
    json.dump(meta, open(os.path.join(HERE, "woorden", code + "_regels.json"), "w"), indent=0)
