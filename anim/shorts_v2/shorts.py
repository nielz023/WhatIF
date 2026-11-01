"""Shorts uit video 2 ("10x FASTER every day"), staand 1080x1920, 30 fps, met een NIEUWE voice-over.

Werkwijze (niels 2026-11-01: zelfde momenten als in de video, maar een eigen, gerelateerde voice-over):
1. Beeld: de scènes van video 2 worden opnieuw gerenderd in 9:16 (WHATIF_VERTICAL=1, zie anim/lib/scene.py),
   alleen de stukken die de shorts gebruiken (WHATIF_RANGES). De camera houdt zijn hoogte-beeldhoek en schuift
   per frame mee met het hoofdpersonage. Uitvoer: out/<scène>_staand/frames.
2. Geluid: de geluidseffecten en sfeer van de scène lopen mee (geknipt per stuk), de oude verteller valt weg.
   Daarover de nieuwe verteller (assets/audio/V2S) en één muziekbed per short. Vertraagde stemmen van
   personages (vriend aan de telefoon, de natuurkundige) blijven met hun ondertitel.
3. Tekst: titel bovenin, HUD (DAY · SPEED, klok, tellers) onder de titel, ondertitels in woordgroepjes,
   eindkaart WATCH THE FULL VIDEO.

Gebruik:
    python3 anim/shorts_v2/shorts.py ranges            -> per scène de WHATIF_RANGES (voor het renderen)
    python3 anim/shorts_v2/shorts.py captions          -> anim/shorts_v2/captions.json (woordtijden uit de stem)
    blender -b -P anim/shorts_v2/shorts.py -- build v2s1 [--norender]
        -> out/v2s1/montage.json + frames (harde links), daarna anim/edit/montage.py -> out/v2s1/V2S1.mp4
"""
import json
import math
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
AUDIO = os.path.join(os.environ.get("WHATIF_ASSETS", os.path.join(REPO, "assets")), "audio")
OUT = os.path.join(REPO, "out")
FPS = 30
OFF = FPS / 24.0              # beeld n van een scène toont t = (n - OFF) / FPS
WHITE = (1, 1, 1, 1)
YELLOW = (1.0, 0.86, 0.15, 1)
SUBC = (1.0, 0.95, 0.75, 1)
TITLE = ("WHAT IF YOU GOT", "10x FASTER EVERY DAY?")

# stukken: (scène, van, tot) in scènetijd (s). keep = vertraagde personage-stemmen die blijven (bestand in assets/audio).
SHORTS = {
    "v2s1": dict(name="The garbage truck", music=("drone", 0.30), segs=[("f01", 0.0, 18.4), ("f09", 16.8, 37.6)]),
    "v2s2": dict(name="Sonic boom", music=("subbas", 0.30), segs=[("f08a", 7.7, 36.6), ("f08b", 4.0, 12.0)]),
    "v2s3": dict(name="Floating rain", music=("piano_zacht", 0.26), segs=[("f05b", 0.0, 30.0), ("f05b", 47.7, 53.4)],
                 keep=["F05/F05-06_Vriend_traag.mp3"]),
    "v2s4": dict(name="250 km/h on foot", music=("drums_build", 0.24),
                 segs=[("f04a", 8.1, 15.0), ("f04b", 10.5, 16.5), ("f04c", 0.3, 22.3)]),
    "v2s5": dict(name="Are you hurt?", music=("piano_hol", 0.26), segs=[("f06", 7.2, 44.0)]),
    "v2s6": dict(name="You will never see 9:00", music=("subbas", 0.30),
                 segs=[("f07", 13.0, 18.4), ("f07", 30.8, 62.0)], keep=["F07/F07-03_Wetenschapper_traag.mp3"]),
    "v2s7": dict(name="Light moving", music=("strijkers_emo", 0.26),
                 segs=[("f11", 39.8, 49.7), ("f12", 0.6, 22.0), ("f12", 71.2, 80.0)]),
}


def lines(code):
    """[(regel-id, gewenste start, tekst)] van de nieuwe verteller voor deze short."""
    n = code[-1]
    out = []
    for row in open(os.path.join(REPO, "videos/10x-faster/shorts/regels_shorts.tsv"), encoding="utf-8"):
        rid, t, txt = row.rstrip("\n").split("\t")
        if rid.startswith(f"S{n}-"):
            out.append((rid, float(t), txt))
    return out


def alen(path):
    try:
        import aud
        s = aud.Sound(path)
        return s.length / s.specs[0]
    except ImportError:
        return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                                              "csv=p=0", path]))


def seg_map(code):
    """[(scène, a, b, offset in de short)] en de lengte van het beeld."""
    o, out = 0.0, []
    for sc, a, b in SHORTS[code]["segs"]:
        out.append((sc, a, b, o))
        o += b - a
    return out, o


def to_short(code, scene, t):
    for sc, a, b, o in seg_map(code)[0]:
        if sc == scene and a - 1e-3 <= t <= b + 1e-3:
            return t - a + o
    return None


# ---------------------------------------------------------------------------------------------------------------
def ranges():
    """Per scène de stukken om te renderen (iets ruimer, samengevoegd)."""
    per = {}
    for code, s in SHORTS.items():
        for sc, a, b in s["segs"]:
            per.setdefault(sc, []).append((max(0.0, a - 0.1), b + 0.15))
    out = {}
    for sc, rs in sorted(per.items()):
        rs.sort()
        m = [list(rs[0])]
        for a, b in rs[1:]:
            if a <= m[-1][1] + 0.5:
                m[-1][1] = max(m[-1][1], b)
            else:
                m.append([a, b])
        out[sc] = ",".join(f"{a:.2f}-{b:.2f}" for a, b in m)
    return out


def captions():
    """Woordgroepjes per verteller-regel, getimed op de spraakstukken (stiltes uit ffmpeg silencedetect)."""
    res = {}
    for code in SHORTS:
        for rid, _, txt in lines(code):
            p = os.path.join(AUDIO, "V2S", f"{rid}_Verteller.mp3")
            if not os.path.exists(p):
                continue
            D = alen(p)
            log = subprocess.run(["ffmpeg", "-hide_banner", "-i", p, "-af", "silencedetect=noise=-38dB:d=0.18", "-f", "null",
                                  "-"], capture_output=True, text=True).stderr
            st = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", log)]
            en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
            if len(en) < len(st):
                en.append(D)
            speech, t = [], 0.0
            for a, b in zip(st, en):
                if a > t + 0.05:
                    speech.append((t, a))
                t = max(t, b)
            if t < D - 0.05:
                speech.append((t, D))
            clean = re.sub(r"\[[^]]*\]", "", txt).replace("…", "... ").strip()
            words = [w for w in re.sub(r"\s+", " ", clean).split(" ") if w]
            chunks, cur = [], ""
            for w in words:
                if cur and (len(cur) + 1 + len(w) > 16 or cur[-1] in ".?!:,"):
                    chunks.append(cur)
                    cur = w
                else:
                    cur = (cur + " " + w).strip()
            if cur:
                chunks.append(cur)
            # tijd over de spraakstukken verdelen naar het aantal tekens
            tot_sp = sum(b - a for a, b in speech) or D
            tot_ch = sum(len(c) + 2 for c in chunks)
            out, acc = [], 0.0
            for c in chunks:
                d = tot_sp * (len(c) + 2) / tot_ch

                def at(x):
                    for a, b in speech:
                        if x <= b - a:
                            return a + x
                        x -= b - a
                    return D
                out.append((c.upper().replace('"', ""), round(at(acc + 0.01), 3), round(at(acc + d - 0.01), 3)))
                acc += d
            # aaneengesloten maken (geen flitsen tussen groepjes)
            for i in range(len(out) - 1):
                if out[i + 1][1] - out[i][2] < 0.45:
                    out[i] = (out[i][0], out[i][1], out[i + 1][1])
            res[rid] = out
    with open(os.path.join(HERE, "captions.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    print("captions.json:", len(res), "regels")


# ---------------------------------------------------------------------------------------------------------------
HUD_Y = {0.94: 0.835, 0.855: 0.795, 0.785: 0.762, 0.715: 0.728, 0.645: 0.696}


def spec(code):
    S = SHORTS[code]
    segs, pic = seg_map(code)
    caps = json.load(open(os.path.join(HERE, "captions.json")))
    voice, sounds, texts, cards = [], [], [], []

    # vaste personage-stemmen (met ondertitel) uit de scènes
    fixed = []
    scene_specs = {}
    for sc, a, b, o in segs:
        p = os.path.join(OUT, f"{sc}_staand", "montage.json")
        if sc not in scene_specs:
            scene_specs[sc] = json.load(open(p))
    for sc, a, b, o in segs:
        sp = scene_specs[sc]
        for f, t in sp["voice"]:
            if f in S.get("keep", []) and a - 0.05 <= t < b:
                d = alen(os.path.join(AUDIO, f))
                voice.append((f, t - a + o))
                fixed.append((t - a + o, t - a + o + d))

    # nieuwe verteller: zo dicht mogelijk bij de gewenste tijd, nooit over een andere stem heen
    busy = sorted(fixed)
    last_end = 0.0
    for rid, want, txt in lines(code):
        p = os.path.join(AUDIO, "V2S", f"{rid}_Verteller.mp3")
        if not os.path.exists(p):
            raise SystemExit(f"Stem ontbreekt: {p}")
        d = alen(p)
        t = max(want, last_end + 0.15)
        for a, b in busy:
            if t < b + 0.15 and t + d > a - 0.15:
                t = b + 0.2
        voice.append((os.path.relpath(p, AUDIO).replace("\\", "/"), t))
        busy.append((t, t + d))
        busy.sort()
        last_end = t + d
        for body, c0, c1 in caps.get(rid, []):
            texts.append(dict(body=body, t0=t + c0, t1=t + c1, loc=(0.5, 0.30), size=118, color=WHITE,
                              anchor=("CENTER", "CENTER"), pop=False))
    vo_end = max(b for a, b in busy)
    length = max(pic, vo_end + 0.5) + 2.4          # + eindkaart
    card0 = max(pic - 0.2, vo_end + 0.35)

    # geluid uit de scènes (zonder muziek), per stuk geknipt
    for sc, a, b, o in segs:
        sp = scene_specs[sc]
        for s in sp["sounds"]:
            if s["file"].startswith("muziek/"):
                continue
            path = os.path.join(AUDIO, s["file"] + ("" if s["file"].endswith(".mp3") else ".mp3"))
            if not os.path.exists(path):
                continue
            flen = alen(path)
            cut = list(s.get("cut") or [0.0, None])
            c0 = cut[0] or 0.0
            c1 = cut[1] if cut[1] is not None else flen
            t0 = s["t"]
            t1 = s.get("loop_to") or (t0 + (c1 - c0))
            if t1 <= a or t0 >= b:
                continue
            n = dict(s)
            if t0 < a:                                   # begint vóór het stuk: later in het bestand instappen
                skip = a - t0
                if s.get("loop_to"):
                    skip = skip % max(0.1, c1 - c0)
                n["cut"] = [c0 + skip, cut[1]]
                n["t"] = o
                n["fade_in"] = 0.15
            else:
                n["t"] = t0 - a + o
            if s.get("loop_to"):
                n["loop_to"] = min(t1, b) - a + o
            elif t1 > b:                                 # loopt door na het stuk: afkappen
                cc = n.get("cut") or [c0, None]
                n["cut"] = [cc[0] or 0.0, (cc[0] or 0.0) + (b - max(t0, a))]
                n["fade_out"] = 0.12
            if n.get("keys"):
                n["keys"] = [[k - a + o, v] for k, v in n["keys"]]
            n["fade_out"] = max(n.get("fade_out", 0.0), 0.12) if n.get("loop_to") else n.get("fade_out", 0.0)
            sounds.append(n)

        # HUD en tellers: onder de titel, gecentreerd; ondertitels van bewaarde stemmen
        for x in sp["texts"]:
            if x["t1"] is None or x["t1"] <= a or x["t0"] >= b:
                continue
            n = dict(x)
            n["t0"] = max(x["t0"], a) - a + o
            n["t1"] = min(x["t1"], b) - a + o
            n["pop"] = x.get("pop", True) and x["t0"] >= a
            if x.get("hud"):
                y = min(HUD_Y, key=lambda k: abs(k - x["loc"][1]))
                n["loc"] = (0.5, HUD_Y[y])
                n["anchor"] = ("CENTER", "TOP")
                n["size"] = int(x["size"] * 0.9)
            elif '"' in x["body"] and any(k for k in S.get("keep", [])):
                n["loc"] = (0.5, 0.40)
                n["size"] = 60
                n["anchor"] = ("CENTER", "CENTER")
            else:
                continue                                 # 'THIS PART IS REAL', 'LATER IN THIS VIDEO' e.d.
            # de HUD verdwijnt onder de eindkaart
            n["t1"] = min(n["t1"], card0)
            if n["t1"] - n["t0"] > 0.02:
                texts.append(n)

    # HUD die tot het eind van het beeld loopt, doortrekken tot de eindkaart (beeld staat dan stil)
    # muziekbed + eindkaart
    m, vol = S["music"]
    sounds.append(dict(file=f"muziek/{m}", t=0.0, vol=vol, cut=[0.0, None], keys=None, loop_to=length - 0.1, duck=True,
                       fade_in=0.4, fade_out=1.2))
    sounds.append(dict(file="sfx/sfx_whoosh_titel", t=card0 - 0.1, vol=0.45, cut=None, keys=None, loop_to=None))
    texts.append(dict(body=TITLE[0], t0=0.0, t1=card0, loc=(0.5, 0.925), size=80, color=WHITE, anchor=("CENTER", "CENTER"),
                      pop=False))
    texts.append(dict(body=TITLE[1], t0=0.0, t1=card0, loc=(0.5, 0.887), size=80, color=YELLOW,
                      anchor=("CENTER", "CENTER"), pop=False))
    cards.append(dict(body="FULL VIDEO", t0=card0, t1=length, size=150, dim=0.66, color=YELLOW, fin=6, fout=1,
                      sub="ON THE CHANNEL", sub_scale=0.55))
    texts.append(dict(body="LIKE & SUBSCRIBE", t0=card0 + 0.4, t1=length, loc=(0.5, 0.30), size=72, color=WHITE,
                      anchor=("CENTER", "CENTER"), pop=True))
    return dict(code=code, length=length, picture_end=length, voice=voice, sounds=sounds, texts=texts, cards=cards,
                title=None, fps=FPS)


def frames(code):
    """Beelden van alle stukken achter elkaar in out/<code>/frames (harde links; anders kopie).
    Na het beeld blijft het laatste beeld staan tot het eind (eindkaart)."""
    import glob
    import shutil
    segs, pic = seg_map(code)
    d = os.path.join(OUT, code, "frames")
    if os.path.isdir(d):
        shutil.rmtree(d)
    os.makedirs(d)
    k, last = 1, None
    for sc, a, b, o in segs:
        src = os.path.join(OUT, f"{sc}_staand", "frames")
        n0 = int(math.ceil(a * FPS + OFF))
        cnt = int(round((b - a) * FPS))
        for n in range(n0, n0 + cnt):
            f = os.path.join(src, f"{n:04d}.png")
            if not os.path.exists(f):
                raise SystemExit(f"Beeld ontbreekt: {f} (render {sc} met WHATIF_RANGES uit 'shorts.py ranges')")
            dst = os.path.join(d, f"{k:05d}.png")
            try:
                os.link(f, dst)
            except OSError:
                shutil.copyfile(f, dst)
            last, k = f, k + 1
    return d, k - 1, last


def build(code, render=True):
    sp = spec(code)
    d, n, last = frames(code)
    import shutil
    total = int(round(sp["length"] * FPS))
    for k in range(n + 1, total + 2):                # stilstaand laatste beeld onder de eindkaart
        dst = os.path.join(d, f"{k:05d}.png")
        try:
            os.link(last, dst)
        except OSError:
            shutil.copyfile(last, dst)
    with open(os.path.join(OUT, code, "montage.json"), "w") as fh:
        json.dump(sp, fh, indent=1)
    print(f"{code}: {sp['length']:.2f} s, {n} beelden + stilstand, {len(sp['voice'])} stemmen")
    sys.argv = [sys.argv[0], "--", code] + ([] if render else ["--norender"])
    import runpy
    runpy.run_path(os.path.join(REPO, "anim", "edit", "montage.py"), run_name="__main__")


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    cmd = argv[0] if argv else "ranges"
    if cmd == "ranges":
        for sc, r in ranges().items():
            print(sc, r)
    elif cmd == "captions":
        captions()
    elif cmd == "spec":
        print(json.dumps(spec(argv[1]), indent=1)[:4000])
    elif cmd == "build":
        build(argv[1], render="--norender" not in argv)
