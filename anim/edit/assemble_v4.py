"""Eindmontage video 4 ("What IF You Could Never Die?"), in Blenders eigen videobewerker (geen ffmpeg nodig).

    blender -b -P anim/edit/assemble_v4.py -- --scenes "<map met dXX_*.mp4>" --json "<map met out/<code>/montage.json>"
        [--frames <map met out/<code>/frames>] [--out <video.mp4>] [--allow-missing] [--audio-only] [--norender]
        [--preview a-b]

Wat het doet:
  * cold open (script scène 0-2) geknipt uit bestaande renders: 0a-0c en 2b uit d19b (de rode zon), de flash-forwards
    (1a-1f) uit d06e, d11, d15, d19g en d20a op de beat met witte flitsen, 2a zwart + "So how long is forever?",
    2c de titelkaart. Deze stukken komen bij voorkeur uit de losse PNG-frames (--frames), want die hebben nog GEEN HUD
    (de teller hoort niet in de cold open); zonder frames wordt de mp4 gebruikt en staat de teller erin (melding);
  * daarna alle scènes (anim/v4/scenes/dXX_*.py) op volgorde; bestanden met _old in de naam tellen niet mee;
  * een doorlopend muziekbed per deel, weggedoken onder elke stemregel en weggedraaid waar een scène eigen muziek
    heeft; geen bed vanaf de rode reus (19a) tot het slot (stilte en de tik zijn daar het geluid);
  * zwart met het Driftmark-logo aan het eind;
  * meet de hele mix (EBU R128) en zet hem op -14 LUFS met een piek van hooguit -1 dBFS;
  * levert ook de VOICE-OVER APART (wens niels 9 nov): <naam>_voiceover.wav (alleen alle stemmen, op hun plek in de
    video, -16 LUFS) en de map <naam>_voiceover_los/ met elke stemregel los en genummerd op volgorde + lijst.tsv
    (nummer, starttijd in de video, regel-id, wie, tekst).
"""
import argparse
import glob
import json
import math
import os
import re
import shutil
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
AUDIO = os.path.join(os.environ.get("WHATIF_ASSETS", os.path.join(REPO, "assets")), "audio")
LOGO = os.path.join(REPO, "assets", "branding", "driftmark_logo.png")
FPS = 30
TARGET_LUFS = -14.0
PEAK_MAX = -2.0   # sample-peak; AAC-encoding voegt ~0,7 dB toe (true peak moet <= -1 dBTP)

VOICE_DB, SFX_DB, MUSIC_DB = -18.0, -26.0, -31.0
BED_VOL = 0.22          # muziekbed iets onder het niveau van scènemuziek (0.3)
BED_DUCK = 0.32         # factor onder de stem

# muziekbed per stuk van de video: (eerste scènecode, track)
# None = geen bed (stilte, alleen de tik)
BEDS = [("d02", "m_vredig_klok"), ("d08a", "m_hoop"), ("d10a", "m_spanning_puls"), ("d11", "m_hoop"),
        ("d13a", "m_nacht_angst"), ("d15", "m_winter"), ("d16", "drone"), ("d17", "m_tijdsprong_hoop"),
        ("d19a", None), ("d22a", "m_hoop"), ("d22b", None)]
REGELS = os.path.join(REPO, "videos", "never-die", "regels.tsv")
VO_LUFS = -16.0


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
    for p in sorted(glob.glob(os.path.join(REPO, "anim", "v4", "scenes", "d[0-9][0-9]*.py"))):
        out.append(os.path.basename(p)[:-3].split("_")[0])
    return out


def find_mp4(folder, code):
    hits = [f for f in os.listdir(folder) if f.lower().endswith(".mp4")
            and (f.lower().startswith(code + "_") or os.path.splitext(f)[0].lower() == code)
            and "_old" not in f.lower()]
    hits.sort(key=lambda f: os.path.getmtime(os.path.join(folder, f)), reverse=True)
    return os.path.join(folder, hits[0]) if hits else None


def find_json(root, code):
    hits = glob.glob(os.path.join(root, "**", code, "montage.json"), recursive=True)
    hits.sort(key=os.path.getmtime, reverse=True)
    if not hits:
        return None
    with open(hits[0]) as fh:
        return json.load(fh)


def find_frames(root, code):
    """Losse PNG-frames van een scène (frame n = bestand n = tijd (n-1)/30), zonder HUD."""
    if not root:
        return None
    for d in glob.glob(os.path.join(root, "**", code, "frames"), recursive=True):
        files = glob.glob(os.path.join(d, "*.png"))
        if files:
            byno = {}
            for f in files:
                m = re.findall(r"(\d+)\.png$", f)
                if m:
                    byno[int(m[0])] = f
            return byno
    return None


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
        self.vo_lines = []    # (t, pad) elke stemregel, voor de losse voice-over

    def clip(self, path, src0, dur, audio=False, vol=1.0):
        f0, n = F(self.t), int(round(dur * FPS))
        movie(self.sed, path, free_ch(1, f0, f0 + n), f0, src0, n)
        if audio:
            sound(self.sed, path, free_ch(20, f0, f0 + n), f0, src0, n, vol)
        self.t += dur

    def frames(self, byno, src0, dur):
        """Stuk uit losse frames (zonder HUD). Geeft False als er frames ontbreken."""
        n = int(round(dur * FPS))
        # de renders beginnen bij frame 2 (OUT_OFF), niet bij 1: tel vanaf het eerste bestaande frame
        a = int(round(src0 * FPS)) + min(byno)
        part = [byno.get(k) for k in range(a, a + n)]
        if not all(part):
            return False
        f0 = F(self.t)
        ch = free_ch(1, f0, f0 + n)
        s = coll(self.sed).new_image(name=os.path.basename(part[0])[:30], filepath=part[0], channel=ch, frame_start=f0)
        for f in part[1:]:
            s.elements.append(os.path.basename(f))
        trim(s, f0, n)
        self.t += dur
        return True

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
        s.color = (1, 1, 1, 1) if len(s.color) == 4 else (1, 1, 1)
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
        self.vo_lines.append((t, p))

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

    froot = os.path.abspath(a.frames) if a.frames else jroot
    fr_cache = {}
    hud_warn = []

    def place(code, src0, dur, audio=False, vol=1.0):
        """Stuk uit een scène: liefst uit de frames (geen HUD), anders uit de mp4 (met HUD), anders zwart."""
        if code not in fr_cache:
            fr_cache[code] = find_frames(froot, code)
        if fr_cache[code] and not audio and T.frames(fr_cache[code], src0, dur):
            return
        if src(code):
            if not audio:
                hud_warn.append(code)
            T.clip(src(code), src0, dur, audio, vol)
        else:
            T.black(dur)

    # ---------------- scène 0: de rode zon (5 miljard jaar). Geen muziek: alleen het gebrul van de zon en de tik.
    t0 = T.t
    place("d19b", 0.0, 3.0)    # 0a CLOSE push-in: zijn gezicht, rood verlicht
    place("d19b", 3.0, 2.2)    # 0b DETAIL: het horloge in zijn hand, de wijzers tikken
    place("d19b", 5.2, 3.2)    # 0c LOW WIDE: de vuurmuur komt over de horizon op hem af
    T.say("D00-01", t0 + 0.1)
    T.say("D00-02", t0 + 5.55)
    brul = T.sfx("sfx_zon_gebrul", t0, 0.5, dur=T.t - t0)
    if brul:
        g0 = gain(sfx_path("sfx_zon_gebrul"), "sfx", 0.5)
        for k, v in ((0.0, 0.35), (5.0, 0.6), (T.t - t0 - 0.3, 1.0), (T.t - t0, 0.0)):
            brul.volume = g0 * v
            brul.keyframe_insert("volume", frame=F(t0 + k))
    for tk in (3.3, 4.3):
        T.sfx("sfx_horloge_tik", t0 + tk, 0.7)
    T.marks["koud"] = (t0, T.t)

    # ---------------- scène 1: flash-forwards op de beat, elke cut op een tik, witte flits tussen de shots
    tf = T.t
    for c, s0, d in (("d06e", 0.9, 2.1),     # 1a de vuilniswagen raakt hem, hij landt op zijn voeten
                     ("d11", 4.0, 2.1),      # 1b de oude man (zijn broertje) woelt door zijn haar
                     ("d15", 0.3, 2.1),      # 1c de stad onder het ijs, één figuurtje op de witte vlakte
                     ("d19g", 0.4, 2.1),     # 1d hij zweeft door de ruimte
                     ("d20a", 9.6, 2.0),     # 1e de sterren gaan één voor één uit
                     ("d20a", 15.8, 2.2)):   # 1f zijn gezicht bij het laatste sterretje; het gaat uit
        if T.t > tf:
            T.flash(T.t)
            T.sfx("sfx_whoosh", T.t - 0.1, 0.2)
        T.sfx("sfx_horloge_tik", T.t, 0.6)
        place(c, s0, d)
    T.marks["flash"] = (tf, T.t)

    # ---------------- scène 2: zwart + de vraag, de vuurmuur raakt hem (wit), de titel
    t2 = T.t
    T.black(1.2)               # 2a zwart, tik
    T.sfx("sfx_horloge_tik", t2 + 0.05, 0.8)
    T.say("D02-01", t2 + 0.25)
    place("d19b", 10.4, 2.2)   # 2b CLOSE: ogen dicht, de vuurmuur, wit
    tb = T.t - 2.2
    brul2 = T.sfx("sfx_zon_gebrul", tb, 0.6, dur=1.4)
    if brul2:
        g0 = gain(sfx_path("sfx_zon_gebrul"), "sfx", 0.6)
        for k, v in ((0.0, 0.0), (0.3, 1.0), (1.2, 1.0), (1.4, 0.0)):   # bij het wit valt alles weg
            brul2.volume = g0 * v
            brul2.keyframe_insert("volume", frame=F(tb + k))
    T.black(0.5)               # 0,5 s stilte
    tt = T.t
    T.black(3.0)               # 2c titelkaart
    glow = T.text("WHAT IF YOU COULD NEVER DIE?", tt, 3.0, size=128)
    try:
        glow.color = (1.0, 0.18, 0.06, 1.0) if len(glow.color) == 4 else (1.0, 0.18, 0.06)
        glow.font_size = 131
        if hasattr(glow, "blend_type"):
            glow.blend_type = "ALPHA_OVER"
        for k, v in ((0.0, 0.0), (0.12, 1.0), (1.6, 0.0)):   # rode gloed die wegtrekt
            glow.blend_alpha = v
            glow.keyframe_insert("blend_alpha", frame=F(tt + k))
    except Exception as e:
        print("titelgloed:", e)
    title = T.text("WHAT IF YOU COULD NEVER DIE?", tt, 3.0, size=128)
    if hasattr(title, "blend_type"):
        title.blend_type = "ALPHA_OVER"
    for k, v in ((0.0, 0.0), (0.4, 1.0), (2.6, 1.0), (3.0, 0.0)):
        title.blend_alpha = v
        title.keyframe_insert("blend_alpha", frame=F(tt + k))
    T.sfx("sfx_horloge_tik", tt + 0.02, 1.0)   # één zware tik die nagalmt
    T.sfx("sfx_dreun", tt + 0.02, 0.5)
    T.marks["titel"] = (t2, T.t)

    # ---------------- de scènes
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
            print("LET OP: geen montage.json voor", code, "(muziekbed duikt hier niet onder de stem; stem niet in de losse voice-over)")
            return
        for rel, tv in spec.get("voice", []):
            p_v = os.path.join(AUDIO, rel)
            d = alen(p_v) if os.path.exists(p_v) else 2.0
            T.voice.append((start + tv, start + tv + d))
            if os.path.exists(p_v):
                T.vo_lines.append((start + tv, p_v))
            else:
                print("LET OP: stembestand ontbreekt", rel)
        for snd in spec.get("sounds", []):
            if snd["file"].startswith("muziek/"):
                pm = music_path(snd["file"][7:])
                end = snd.get("loop_to") or (snd["t"] + (alen(pm) if os.path.exists(pm) else 10.0))
                T.own_music.append((start + snd["t"], start + min(end, dur)))

    for code in codes:
        scene(code)

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

    # ---------------- muziekbed: doorlopend, onder de stem weggedoken, weg waar een scène eigen muziek heeft
    beds = []
    for i, (code, track) in enumerate(BEDS):
        if code not in T.marks or track is None:
            continue
        b0 = T.marks[code][0]
        nxt = [T.marks[c][0] for c, _ in BEDS[i + 1:] if c in T.marks]
        b1 = nxt[0] if nxt else T.marks["logo"][1]
        beds.append((b0, b1, track))
    fl = T.marks.get("flash")
    if fl:   # de flash-forwards krijgen hun eigen beat (niet weggedraaid)
        beds.append((fl[0], fl[1] + 0.3, "m_flashforward_beat"))

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
                elif (fl and fl[0] - 0.5 <= q <= fl[1] + 0.5) or (T.marks["koud"][0] <= q < T.marks["titel"][1]):
                    v = 0.0
                else:
                    v = g * fade * (1.0 - own(q)) * (1.0 - (1.0 - BED_DUCK) * duck(q))
                s.volume = v
                s.keyframe_insert("volume", frame=F(q))
            tt += seg

    sc.frame_start, sc.frame_end = 1, F(total)
    if hud_warn:
        print("LET OP: geen frames voor", ", ".join(sorted(set(hud_warn))), "-> stukken uit de mp4, de HUD staat in beeld in de cold open")
    print(f"LENGTE {int(total // 60)}:{int(total % 60):02d} ({total:.1f} s), {len(T.voice)} stemregels, "
          f"{len(T.own_music)} stukken scènemuziek")
    return T


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


def master_wav(raw, out, target=TARGET_LUFS):
    import numpy as np
    x, sr, ch = read_wav(raw)
    x = x.reshape(-1, ch)
    L0, pk0 = lufs_arr(x, sr)
    thr = 10 ** (PEAK_MAX / 20)
    g_db = target - L0
    for _ in range(3):               # limiter haalt wat luidheid weg: bijsturen
        y, frac = limiter(x * 10 ** (g_db / 20), thr)
        L, pk = lufs_arr(y, sr)
        if abs(L - target) < 0.2:
            break
        g_db += target - L
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


def export_voiceover(T, out):
    """Wens niels (9 nov): de complete voice-over apart (alleen stemmen, op hun plek in de video) en elke regel los,
    genummerd op volgorde, met een lijst."""
    sc = bpy.context.scene
    sed = sc.sequence_editor
    base = os.path.splitext(out)[0]
    lines = sorted(T.vo_lines)
    tekst = {}
    if os.path.exists(REGELS):
        with open(REGELS, encoding="utf-8") as fh:
            for row in fh:
                c = row.rstrip("\n").split("\t")
                if len(c) >= 3:
                    tekst[c[0]] = (c[1], c[2])
    los = base + "_voiceover_los"
    if os.path.isdir(los):
        shutil.rmtree(los)
    os.makedirs(los)
    with open(os.path.join(los, "lijst.tsv"), "w", encoding="utf-8") as fh:
        fh.write("nr\tstart\tregel\twie\ttekst\tbestand\n")
        for i, (t, p) in enumerate(lines, 1):
            lid = os.path.basename(p).split("_")[0]
            wie, txt = tekst.get(lid, (os.path.splitext(os.path.basename(p))[0].split("_")[-1], ""))
            naam = f"{i:03d}_{lid}_{wie}.mp3"
            shutil.copyfile(p, os.path.join(los, naam))
            fh.write(f"{i}\t{int(t // 60)}:{t % 60:05.2f}\t{lid}\t{wie}\t{txt}\t{naam}\n")
    # alle geluid uit, alleen de stemmen erin, mixdown, op -16 LUFS (piek -1 dBFS)
    was = {s.name: s.mute for s in coll(sed) if s.type == "SOUND"}
    for s in coll(sed):
        if s.type == "SOUND":
            s.mute = True
    extra = []
    for t, p in lines:
        d = alen(p)
        f0, n = F(t), int(round(d * FPS)) + 2
        extra.append(sound(sed, p, free_ch(200, f0, f0 + n), f0, 0.0, n, gain(p, "voice")))
    raw = base + "_voiceover_raw.wav"
    bpy.ops.sound.mixdown(filepath=raw, check_existing=False, container="WAV", codec="PCM", format="F32",
                          mixrate=48000, channels="STEREO")
    master_wav(raw, base + "_voiceover.wav", target=VO_LUFS)
    os.remove(raw)
    for s in extra:
        coll(sed).remove(s)
    for s in coll(sed):
        if s.type == "SOUND" and s.name in was:
            s.mute = was[s.name]
    print(f"VOICE-OVER {len(lines)} regels -> {base}_voiceover.wav en {los}")


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenes", required=True)
    ap.add_argument("--json", default=None)
    ap.add_argument("--frames", default=None, help="map waarin out/<code>/frames staan (standaard: --json)")
    ap.add_argument("--out", default=None)
    ap.add_argument("--allow-missing", action="store_true")
    ap.add_argument("--audio-only", action="store_true", help="alleen mix + luidheidsmeting, geen video")
    ap.add_argument("--norender", action="store_true")
    ap.add_argument("--preview", default=None, help="proef: alleen seconden a-b, op halve resolutie, bv. 0-45")
    a = ap.parse_args(argv)
    out = os.path.abspath(a.out or os.path.join(a.scenes, "..", "WHAT_IF_NEVER_DIE.mp4"))
    T = build(a)
    sc = bpy.context.scene

    # luidheid: de mix wegschrijven, meten, op -14 LUFS zetten met een limiter op -1 dBFS, en die ene master-WAV
    # als enige geluidsspoor gebruiken (alle losse geluidsstrips gaan op mute)
    raw = os.path.splitext(out)[0] + "_mix_raw.wav"
    master = os.path.splitext(out)[0] + "_mix_master.wav"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    bpy.ops.sound.mixdown(filepath=raw, check_existing=False, container="WAV", codec="PCM", format="F32",
                          mixrate=48000, channels="STEREO")
    master_wav(raw, master)
    export_voiceover(T, out)
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
