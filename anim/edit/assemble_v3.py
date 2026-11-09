"""Eindmontage video 3 ("What If There Were No Rules"), in Blenders eigen videobewerker (geen ffmpeg nodig).

    blender -b -P anim/edit/assemble_v3.py -- --scenes "<map met nXX_*.mp4>" --json "<map met out/<code>/montage.json>"
        [--ue videos/no-rules/ue_overlays.json] [--out <video.mp4>] [--allow-missing] [--audio-only] [--norender]

Wat het doet:
  * zet alle scènes (anim/v3/scenes/nXX_*.py) op volgorde; bestanden met _old of _UE in de naam tellen niet mee;
  * knipt de teaser (scène 0), de flash-forwards (scène 2), de kaart 1 DAY EARLIER, 21a (= n05c) en 22b (= n06a 6b)
    uit bestaande renders, met hun eigen stem (N00, N02, N22-02) en effecten (zie videos/no-rules/montage_hergebruik.md);
  * legt de Unreal-shots als beeld (zonder geluid) over de Blender-scène: de stem loopt gewoon door;
  * een doorlopend muziekbed per bedrijf, weggedoken onder elke stemregel en weggedraaid waar een scène eigen muziek heeft;
  * 22d: zwart met het Driftmark-logo;
  * meet de hele mix (EBU R128, eigen numpy-meting) en zet hem op -14 LUFS met een piek van hooguit -1 dBFS.
"""
import argparse
import glob
import json
import math
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
AUDIO = os.path.join(os.environ.get("WHATIF_ASSETS", os.path.join(REPO, "assets")), "audio")
LOGO = os.path.join(REPO, "assets", "branding", "driftmark_logo.png")
FPS = 30
TARGET_LUFS = -14.0
PEAK_MAX = -1.0

VOICE_DB, SFX_DB, MUSIC_DB = -18.0, -26.0, -31.0
BED_VOL = 0.22          # muziekbed iets onder het niveau van scènemuziek (0.3)
BED_DUCK = 0.32         # factor onder de stem

# muziekbed per stuk van de video: (eerste scènecode, track)
BEDS = [("n01", "drone"), ("n03a", "m_vredig_klok"), ("n05a", "m_nacht_angst"), ("n07a", "m_spanning_puls"),
        ("n10a", "m_nacht_angst"), ("n14a", "m_hoop"), ("n17a", "m_winter"), ("n18a", "m_tijdsprong_hoop"),
        ("n21b", "m_twist"), ("n22a", "m_hoop")]


def F(t):
    return int(round(t * FPS)) + 1


# ------------------------------------------------------------------ geluid: niveaus (zelfde regels als montage.py)
_LV = {}


def _level(path):
    if path not in _LV:
        import aud
        import numpy as np
        snd = aud.Sound(path)
        d = snd.data()
        sr = int(snd.specs[0])
        m = d.mean(axis=1) if d.ndim > 1 else d
        w = max(1, int(sr * 0.4))
        n = len(m) // w
        r = (np.sqrt((m[:n * w].reshape(n, w) ** 2).mean(axis=1) + 1e-12) if n
             else np.array([np.sqrt((m ** 2).mean() + 1e-12)]))
        db = 20 * np.log10(r)
        act = db[db > db.max() - 30]
        _LV[path] = (float(db.max()), float(10 * np.log10((10 ** (act / 10)).mean())), len(m) / sr)
    return _LV[path]


def gain(path, kind, v=1.0):
    peak, act, _ = _level(path)
    if v <= 0:
        return 0.0
    if kind == "voice":
        db = VOICE_DB - act
    elif kind == "music":
        db = MUSIC_DB + 20 * math.log10(v / 0.3) - act
    else:
        db = SFX_DB + 20 * math.log10(min(v, 1.0)) - peak
    return 10 ** (max(-40.0, min(18.0, db)) / 20)


def alen(path):
    return _level(path)[2]


def voice_path(line_id):
    hits = sorted(glob.glob(os.path.join(AUDIO, line_id[:3], line_id + "_*.mp3")))
    hits = [h for h in hits if not h.endswith("_traag.mp3")] or hits
    if not hits:
        raise SystemExit("Geen stem voor " + line_id)
    return hits[0]


def sfx_path(name):
    return os.path.join(AUDIO, "sfx", name + ".mp3")


def music_path(name):
    return os.path.join(AUDIO, "muziek", name + ".mp3")


# ------------------------------------------------------------------ VSE-hulp (oude en nieuwe API)
def coll(sed):
    return sed.strips if hasattr(sed, "strips") else sed.sequences


def effect(sed, name, typ, ch, f0, n):
    c = coll(sed)
    try:
        return c.new_effect(name=name, type=typ, channel=ch, frame_start=f0, length=n)
    except TypeError:
        return c.new_effect(name=name, type=typ, channel=ch, frame_start=f0, frame_end=f0 + n)


def trim(s, f0, n):
    s.frame_final_start = f0
    s.frame_final_end = f0 + n


def movie(sed, path, ch, f0, src0, n):
    kw = dict(name=os.path.basename(path)[:30], filepath=path, channel=ch, frame_start=f0 - int(round(src0 * FPS)))
    try:
        s = coll(sed).new_movie(fit_method="FIT", **kw)   # Unreal-clips kunnen een andere resolutie hebben
    except TypeError:
        s = coll(sed).new_movie(**kw)
    trim(s, f0, n)
    return s


def sound(sed, path, ch, f0, src0, n, vol=1.0):
    s = coll(sed).new_sound(name=os.path.basename(path)[:30], filepath=path, channel=ch,
                            frame_start=f0 - int(round(src0 * FPS)))
    trim(s, f0, n)
    s.volume = vol
    return s


USED = {}


def free_ch(base, f0, f1):
    ch = base
    while True:
        if all(f1 <= a or f0 >= b for a, b in USED.get(ch, [])):
            USED.setdefault(ch, []).append((f0, f1))
            return ch
        ch += 1


# ------------------------------------------------------------------ bronnen
def scene_codes():
    out = []
    for p in sorted(glob.glob(os.path.join(REPO, "anim", "v3", "scenes", "n[0-9][0-9]*.py"))):
        out.append(os.path.basename(p)[:-3].split("_")[0])
    return out


def find_mp4(folder, code):
    hits = [f for f in os.listdir(folder) if f.lower().endswith(".mp4")
            and (f.lower().startswith(code + "_") or os.path.splitext(f)[0].lower() == code)
            and "_old" not in f.lower() and "_ue" not in f.lower()]
    hits.sort(key=lambda f: os.path.getmtime(os.path.join(folder, f)), reverse=True)
    return os.path.join(folder, hits[0]) if hits else None


def find_json(root, code):
    hits = glob.glob(os.path.join(root, "**", code, "montage.json"), recursive=True)
    hits.sort(key=os.path.getmtime, reverse=True)
    if not hits:
        return None
    with open(hits[0]) as fh:
        return json.load(fh)


def movie_len(path):
    clip = bpy.data.movieclips.load(path)
    n = clip.frame_duration
    fps = clip.fps or FPS
    bpy.data.movieclips.remove(clip)
    return n / fps


# ------------------------------------------------------------------ de tijdlijn
class Timeline:
    def __init__(self, sed):
        self.sed = sed
        self.t = 0.0
        self.voice = []       # (t0, t1) globaal
        self.own_music = []   # (t0, t1) waar een scène eigen muziek heeft
        self.marks = {}       # scènecode -> starttijd
        self.flashes = []

    def clip(self, path, src0, dur, audio=False, vol=1.0):
        f0, n = F(self.t), int(round(dur * FPS))
        movie(self.sed, path, free_ch(1, f0, f0 + n), f0, src0, n)
        if audio:
            sound(self.sed, path, free_ch(20, f0, f0 + n), f0, src0, n, vol)
        self.t += dur

    def black(self, dur):
        f0, n = F(self.t), int(round(dur * FPS))
        s = effect(self.sed, "zwart", "COLOR", free_ch(1, f0, f0 + n), f0, n)
        s.color = (0, 0, 0)
        self.t += dur
        return f0, n

    def text(self, body, t0, dur, size=110, loc=(0.5, 0.5)):
        f0, n = F(t0), int(round(dur * FPS))
        s = effect(self.sed, body[:20], "TEXT", free_ch(40, f0, f0 + n), f0, n)
        s.text = body
        s.font_size = size
        s.color = (1, 1, 1, 1)
        s.location = loc
        if hasattr(s, "anchor_x"):
            s.anchor_x, s.anchor_y = "CENTER", "CENTER"
        else:
            s.align_x, s.align_y = "CENTER", "CENTER"
        if hasattr(s, "use_bold"):
            s.use_bold = True
        d = bpy.utils.system_resource("DATAFILES", path="fonts") or ""
        fp = os.path.join(d, "Inter.woff2")
        if os.path.exists(fp):
            s.font = bpy.data.fonts.load(fp, check_existing=True)
        return s

    def flash(self, t, frames=2):
        f0 = F(t) - 1
        s = effect(self.sed, "flits", "COLOR", free_ch(45, f0, f0 + frames), f0, frames)
        s.color = (1, 1, 1)

    def say(self, line_id, t):
        p = voice_path(line_id)
        d = alen(p)
        f0, n = F(t), int(round(d * FPS)) + 2
        sound(self.sed, p, free_ch(50, f0, f0 + n), f0, 0.0, n, gain(p, "voice"))
        self.voice.append((t, t + d))

    def sfx(self, name, t, v=0.6, dur=None):
        p = sfx_path(name)
        if not os.path.exists(p):
            print("LET OP: sfx ontbreekt", name)
            return
        d = min(alen(p), dur or 1e9)
        f0, n = F(t), int(round(d * FPS))
        return sound(self.sed, p, free_ch(60, f0, f0 + n), f0, 0.0, n, gain(p, "sfx", v))


def build(a):
    sc = bpy.context.scene
    sc.render.fps = FPS
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
    sc.render.resolution_percentage = 100
    sed = sc.sequence_editor_create()
    T = Timeline(sed)
    S = os.path.abspath(a.scenes)
    jroot = os.path.abspath(a.json) if a.json else None

    codes = scene_codes()
    mp4 = {c: find_mp4(S, c) for c in codes}
    missing = [c for c in codes if not mp4[c]]
    if missing:
        print("ONTBREEKT:", ", ".join(missing))
        if not a.allow_missing:
            raise SystemExit("FOUT: niet alle scènes zijn er (gebruik --allow-missing voor een proefversie)")

    def src(code):
        return mp4.get(code)

    def place(code, src0, dur, audio=False, vol=1.0):
        if src(code):
            T.clip(src(code), src0, dur, audio, vol)
        else:
            T.black(dur)

    # ---------------- scène 0: teaser (dag 4, de stroomuitval), geen muziek, alleen gezoem en een thunk per blok
    t0 = T.t
    place("n10a", 11.2, 2.5)   # 0a LOW WIDE: hij fietst voor de zwarte golf uit
    place("n10a", 13.7, 1.5)   # 0b CLOSE: kijkt over zijn schouder
    place("n10a", 9.2, 2.0)    # 0c drone: de golf haalt zijn fietslamp in
    place("n10c", 0.6, 2.0)    # 0d MEDIUM: op slot, een hand op zijn schouder
    T.black(1.0)               # 0e zwart
    T.say("N00-01", t0 + 0.05)
    zoem = T.sfx("sfx_stroom_zoem", t0, 0.25, dur=8.0)
    if zoem:
        for k, v in ((0.0, 0.15), (5.8, 0.9), (6.1, 0.0)):
            zoem.volume = gain(sfx_path("sfx_stroom_zoem"), "sfx", 0.25) * v
            zoem.keyframe_insert("volume", frame=F(t0 + k))
    for k, tk in enumerate((0.2, 1.1, 2.0, 3.0, 4.3, 5.4)):
        T.sfx("sfx_stroom_thunk", t0 + tk, 0.35 + 0.08 * k)
    T.sfx("sfx_adem_hijgen", t0 + 6.0, 0.5, dur=2.0)
    T.marks["teaser"] = (t0, T.t)

    # ---------------- de scènes, met scène 2 na n01 en 21a / 22b op hun plek
    def scene(code):
        p = src(code)
        if not p:
            print("zwart in plaats van", code)
            T.marks[code] = (T.t, T.t + 3.0)
            T.black(3.0)
            return
        dur = movie_len(p)
        start = T.t
        T.clip(p, 0.0, dur, audio=True)
        T.marks[code] = (start, T.t)
        spec = find_json(jroot, code) if jroot else None
        if spec is None:
            print("LET OP: geen montage.json voor", code, "(muziekbed duikt hier niet onder de stem)")
            return
        for rel, tv in spec.get("voice", []):
            p_v = os.path.join(AUDIO, rel)
            d = alen(p_v) if os.path.exists(p_v) else 2.0
            T.voice.append((start + tv, start + tv + d))
        for snd in spec.get("sounds", []):
            if snd["file"].startswith("muziek/"):
                pm = music_path(snd["file"][7:])
                end = snd.get("loop_to") or (snd["t"] + (alen(pm) if os.path.exists(pm) else 10.0))
                T.own_music.append((start + snd["t"], start + min(end, dur)))

    for code in codes:
        if code == "n21b":   # 21a: exact hetzelfde shot als 5c, met zijn alarm
            place("n05c", 0.0, 3.0, audio=True)
        if code == "n22c":   # 22b: de jongen als kind bij zijn raam (6b), nieuwe stem
            tb = T.t
            place("n06a", 4.0, 4.0)
            T.say("N22-02", tb + 0.3)
        scene(code)
        if code == "n01":    # scène 2: flash-forwards op de beat, witte flits tussen de shots
            tf = T.t
            for c, s0, d in (("n07b", 11.5, 2.0), ("n08c", 1.0, 1.5), ("n12a", 7.2, 2.0),
                             ("n13a", 1.0, 2.0), ("n17a", 0.5, 2.0), ("n21b", 10.5, 3.8)):
                if T.t > tf:
                    T.flash(T.t)
                    T.sfx("sfx_whoosh", T.t - 0.1, 0.25)
                place(c, s0, d)
            T.say("N02-01", tf + 0.1)
            T.say("N02-02", tf + 7.6)
            T.say("N02-03", tf + 9.6)
            T.marks["flash"] = (tf, T.t)
            tk = T.t   # 2b: kaart
            T.black(1.0)
            T.text("1 DAY EARLIER", tk, 1.0)
            T.sfx("sfx_klok_tik", tk + 0.1, 0.5)

    # ---------------- 22d: zwart met het Driftmark-logo
    tl = T.t
    f0, n = T.black(2.0)
    if os.path.exists(LOGO):
        s = coll(sed).new_image(name="driftmark_logo", filepath=LOGO, channel=free_ch(40, f0, f0 + n), frame_start=f0)
        trim(s, f0, n)
        if hasattr(s, "blend_type"):
            s.blend_type = "ALPHA_OVER"
        for fr, v in ((f0, 0.0), (f0 + 8, 1.0), (f0 + n - 6, 1.0), (f0 + n, 0.0)):
            s.blend_alpha = v
            s.keyframe_insert("blend_alpha", frame=fr)
    T.marks["logo"] = (tl, T.t)
    total = T.t

    # ---------------- Unreal-shots als beeld over de Blender-scène (geen geluid: de stem loopt door)
    if a.ue and os.path.exists(a.ue):
        with open(a.ue) as fh:
            for u in json.load(fh):
                p = u["file"] if os.path.isabs(u["file"]) else os.path.join(S, u["file"])
                if u["scene"] not in T.marks or not os.path.exists(p):
                    print("UE overgeslagen:", u)
                    continue
                d = u.get("dur") or movie_len(p)
                tg = T.marks[u["scene"]][0] + u["t0"]
                movie(sed, p, free_ch(10, F(tg), F(tg) + int(round(d * FPS))), F(tg), u.get("src0", 0.0), int(round(d * FPS)))
                print(f"UE {os.path.basename(p)} op {tg:.2f} s ({d:.1f} s)")

    # ---------------- muziekbed: doorlopend, onder de stem weggedoken, weg waar een scène eigen muziek heeft
    beds = []
    for i, (code, track) in enumerate(BEDS):
        if code not in T.marks:
            continue
        b0 = T.marks[code][0]
        nxt = [T.marks[c][0] for c, _ in BEDS[i + 1:] if c in T.marks]
        b1 = nxt[0] if nxt else T.marks["logo"][1]
        beds.append((b0, b1, track))
    fl = T.marks.get("flash")
    if fl:   # de flash-forwards krijgen hun eigen beat (niet weggedraaid)
        beds.append((fl[0], fl[1] + 1.0, "m_flashforward_beat"))

    def duck(t):
        d = 0.0
        for v0, v1 in T.voice:
            if v0 - 0.3 <= t <= v1 + 0.5:
                d = max(d, max(0.0, min(1.0, (t - (v0 - 0.3)) / 0.25, ((v1 + 0.5) - t) / 0.35)))
        return d

    def own(t):
        o = 0.0
        for m0, m1 in T.own_music:
            o = max(o, max(0.0, min(1.0, (t - (m0 - 1.0)) / 1.0, ((m1 + 1.0) - t) / 1.0)))
        return o

    for b0, b1, track in beds:
        p = music_path(track)
        if not os.path.exists(p):
            print("LET OP: muziek ontbreekt", track)
            continue
        is_ff = track == "m_flashforward_beat"
        g = gain(p, "music", 0.35 if is_ff else BED_VOL)
        L = alen(p)
        tt = b0 - (0.0 if is_ff else 1.0)   # 1 s overlap: zachte overgang tussen beds
        tt = max(0.0, tt)
        while tt < b1 - 0.05:
            seg = min(L, b1 + (0.0 if is_ff else 1.0) - tt)
            f0, n = F(tt), max(1, int(round(seg * FPS)))
            s = sound(sed, p, free_ch(80, f0, f0 + n), f0, 0.0, n, g)
            pts = sorted({tt + k * 0.25 for k in range(int(seg / 0.25) + 1)} | {tt + seg})
            for q in pts:
                fade = min(1.0, max(0.0, (q - (b0 - 1.0)) / 1.0), max(0.0, (b1 + 1.0 - q) / 1.0))
                if is_ff:
                    v = g * fade * (1.0 - 0.45 * duck(q))
                elif (fl and fl[0] - 0.5 <= q <= fl[1] + 0.5) or (T.marks["teaser"][0] <= q < T.marks["teaser"][1]):
                    v = 0.0
                else:
                    v = g * fade * (1.0 - own(q)) * (1.0 - (1.0 - BED_DUCK) * duck(q))
                s.volume = v
                s.keyframe_insert("volume", frame=F(q))
            tt += seg

    sc.frame_start, sc.frame_end = 1, F(total)
    print(f"LENGTE {int(total // 60)}:{int(total % 60):02d} ({total:.1f} s), {len(T.voice)} stemregels, "
          f"{len(T.own_music)} stukken scènemuziek")
    return total


def read_wav(path):
    """WAV lezen (16-bit PCM of 32-bit float), zonder externe modules."""
    import struct
    import numpy as np
    with open(path, "rb") as fh:
        data = fh.read()
    pos, fmt, ch, sr, bits, raw = 12, 1, 2, 48000, 16, None
    while pos + 8 <= len(data):
        cid, size = data[pos:pos + 4], struct.unpack("<I", data[pos + 4:pos + 8])[0]
        body = data[pos + 8:pos + 8 + size]
        if cid == b"fmt ":
            fmt, ch, sr = struct.unpack("<HHI", body[:8])
            bits = struct.unpack("<H", body[14:16])[0]
            if fmt == 0xFFFE:
                fmt = struct.unpack("<H", body[24:26])[0]
        elif cid == b"data":
            raw = body
        pos += 8 + size + (size & 1)
    if fmt == 3:
        x = np.frombuffer(raw, dtype=np.float32 if bits == 32 else np.float64).astype(np.float64)
    else:
        x = np.frombuffer(raw[:len(raw) // 2 * 2], dtype=np.int16).astype(np.float64) / 32768.0
    return x[:len(x) // ch * ch], sr, ch


# ------------------------------------------------------------------ luidheid (EBU R128 / BS.1770, met gating)
def lufs_arr(x, sr):
    import numpy as np

    # K-weging (ITU-R BS.1770-4) als amplituderespons in het frequentiedomein, in blokken (geen scipy nodig)
    if sr != 48000:
        print("LET OP: mixrate", sr, "- K-weging is voor 48 kHz berekend")

    def resp(b, a_, w):
        z = np.exp(-1j * w)
        return (b[0] + b[1] * z + b[2] * z * z) / (a_[0] + a_[1] * z + a_[2] * z * z)

    N = 1 << 19
    w = 2 * np.pi * np.fft.rfftfreq(N) 
    H = np.abs(resp([1.53512485958697, -2.69169618940638, 1.19839281085285], [1.0, -1.69065929318241, 0.73248077421585], w)
               * resp([1.0, -2.0, 1.0], [1.0, -1.99004745483398, 0.99007225036621], w))
    y = np.empty_like(x)
    for i in range(0, len(x), N):
        seg = x[i:i + N]
        n = len(seg)
        spec = np.fft.rfft(seg, n=N, axis=0) * H[:, None]
        y[i:i + n] = np.fft.irfft(spec, n=N, axis=0)[:n]
    blk, hop = int(0.4 * sr), int(0.1 * sr)
    p2 = (y ** 2).sum(axis=1)
    cs = np.concatenate([[0.0], np.cumsum(p2)])
    starts = np.arange(0, len(p2) - blk, hop)
    z = (cs[starts + blk] - cs[starts]) / blk
    lk = -0.691 + 10 * np.log10(z + 1e-15)
    z = z[lk > -70]
    rel = -0.691 + 10 * np.log10(z.mean()) - 10
    z2 = z[(-0.691 + 10 * np.log10(z + 1e-15)) > rel]
    integ = -0.691 + 10 * np.log10(z2.mean())
    peak = 20 * np.log10(np.abs(x).max() + 1e-12)
    return float(integ), float(peak)


def limiter(x, thr):
    """Look-ahead piekbegrenzer per blok van 1 ms (aanzet 3 ms vooruit, loslaten ~80 ms)."""
    import numpy as np
    sr = 48000
    B = sr // 1000
    nb = len(x) // B + 1
    pad = np.zeros((nb * B, x.shape[1]))
    pad[:len(x)] = x
    pk = np.abs(pad).reshape(nb, B, -1).max(axis=(1, 2))
    g = np.minimum(1.0, thr / np.maximum(pk, 1e-9))
    gl = g.copy()
    for k in range(1, 4):            # vooruitkijken: al zakken vóór de piek
        gl[:-k] = np.minimum(gl[:-k], g[k:])
    gl[1:] = np.minimum(gl[1:], g[:-1])
    rel = 1.0 - math.exp(-1.0 / 80.0)
    env = np.empty_like(gl)
    e = 1.0
    for i in range(nb):
        e = min(gl[i], e + (1.0 - e) * rel)
        env[i] = e
    t_b = (np.arange(nb) + 0.5) * B
    gs = np.interp(np.arange(len(x)), t_b, env)
    y = x * gs[:, None]
    return np.clip(y, -thr, thr), float((env < 0.999).mean())


def write_wav16(path, y, sr=48000):
    import struct
    import numpy as np
    d = (np.clip(y, -1, 1) * 32767).astype("<i2").tobytes()
    ch = y.shape[1]
    with open(path, "wb") as fh:
        fh.write(b"RIFF" + struct.pack("<I", 36 + len(d)) + b"WAVEfmt " +
                 struct.pack("<IHHIIHH", 16, 1, ch, sr, sr * ch * 2, ch * 2, 16) + b"data" + struct.pack("<I", len(d)) + d)


def master_wav(raw, out):
    import numpy as np
    x, sr, ch = read_wav(raw)
    x = x.reshape(-1, ch)
    L0, pk0 = lufs_arr(x, sr)
    thr = 10 ** (PEAK_MAX / 20)
    g_db = TARGET_LUFS - L0
    for _ in range(3):               # limiter haalt wat luidheid weg: bijsturen
        y, frac = limiter(x * 10 ** (g_db / 20), thr)
        L, pk = lufs_arr(y, sr)
        if abs(L - TARGET_LUFS) < 0.2:
            break
        g_db += TARGET_LUFS - L
    write_wav16(out, y, sr)
    print(f"LUIDHEID mix {L0:.1f} LUFS (piek {pk0:.1f} dBFS) -> master {L:.1f} LUFS, piek {pk:.1f} dBFS, "
          f"gain {g_db:+.1f} dB, limiter actief {frac * 100:.1f}% van de tijd")
    if frac > 0.05:
        print("LET OP: de limiter werkt vaak; de mix heeft veel pieken (effecten te hard?)")


def setup_output(out, audio_only=False):
    sc = bpy.context.scene
    r = sc.render
    try:
        sc.view_settings.view_transform = "Standard"
        sc.view_settings.look = "None"
    except Exception:
        pass
    if hasattr(r.image_settings, "media_type"):
        r.image_settings.media_type = "VIDEO"
    r.image_settings.file_format = "FFMPEG"
    r.ffmpeg.format = "MPEG4"
    r.ffmpeg.codec = "H264"
    r.ffmpeg.constant_rate_factor = "HIGH"
    r.ffmpeg.ffmpeg_preset = "GOOD"
    r.ffmpeg.audio_codec = "AAC"
    r.ffmpeg.audio_bitrate = 256
    r.ffmpeg.audio_channels = "STEREO"
    r.ffmpeg.audio_mixrate = 48000
    r.use_sequencer = True
    r.filepath = out


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenes", required=True)
    ap.add_argument("--json", default=None)
    ap.add_argument("--ue", default=os.path.join(REPO, "videos", "no-rules", "ue_overlays.json"))
    ap.add_argument("--out", default=None)
    ap.add_argument("--allow-missing", action="store_true")
    ap.add_argument("--audio-only", action="store_true", help="alleen mix + luidheidsmeting, geen video")
    ap.add_argument("--norender", action="store_true")
    ap.add_argument("--preview", default=None, help="proef: alleen seconden a-b, op halve resolutie, bv. 0-45")
    a = ap.parse_args(argv)
    out = os.path.abspath(a.out or os.path.join(a.scenes, "..", "WHAT_IF_NO_RULES.mp4"))
    build(a)
    sc = bpy.context.scene

    # luidheid: de mix wegschrijven, meten, op -14 LUFS zetten met een limiter op -1 dBFS, en die ene master-WAV
    # als enige geluidsspoor gebruiken (alle losse geluidsstrips gaan op mute)
    raw = os.path.splitext(out)[0] + "_mix_raw.wav"
    master = os.path.splitext(out)[0] + "_mix_master.wav"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    bpy.ops.sound.mixdown(filepath=raw, check_existing=False, container="WAV", codec="PCM", format="F32",
                          mixrate=48000, channels="STEREO")
    master_wav(raw, master)
    for s in coll(sc.sequence_editor):
        if s.type == "SOUND":
            s.mute = True
    n = sc.frame_end
    sound(sc.sequence_editor, master, free_ch(120, 1, n + 1), 1, 0.0, n, 1.0)

    setup_output(out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.splitext(out)[0] + "_montage.blend", relative_remap=False)
    if a.audio_only or a.norender:
        return
    if a.preview:
        p0, p1 = (float(v) for v in a.preview.split("-"))
        sc.frame_start, sc.frame_end = max(sc.frame_start, F(p0)), min(sc.frame_end, F(p1))   # nooit voorbij het einde
        sc.render.resolution_percentage = 50
    bpy.ops.render.render(animation=True)
    print("KLAAR", out)


main()
