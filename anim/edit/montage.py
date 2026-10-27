"""Montage: gerenderde beelden + stem + geluid + muziek + HUD -> MP4 (in Blender zelf, geen ffmpeg nodig).

Gebruik (Blender 5.2):
    blender -b -P anim/edit/montage.py -- s01 [--frames out/s01/frames] [--out out/s01/S01_cold_open.mp4]
    blender -b -P anim/edit/montage.py -- s02        (leest out/s02/montage.json van het scènescript)

S01 staat hieronder uitgeschreven; vanaf S02 schrijft elk scènescript zijn eigen montage.json
(stemmen, muziek met ducking onder de stem, geluid, HUD, titelkaarten).
"""
import argparse
import glob
import json
import os
import re
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
AUDIO = os.path.join(os.environ.get("WHATIF_ASSETS", os.path.join(REPO, "assets")), "audio")
FPS = 24


def F(t):
    return int(round(t * FPS)) + 1


# ---------------------------------------------------------------------------
# S01 · cold open
# ---------------------------------------------------------------------------
# niels (2026-10-27): de cold open was een minuut en moest korter en spannender. Nu ~23 s, geknipt uit de al
# gerenderde S01-beelden: de remmen falen, hij staat op de rails, dan meteen de greep in het staal en de bouten.
# De uitleg (cruiseschip, simulatie) valt weg; die komt op dag 16 (S17B) toch terug.
# edit: stukken (van, tot) in seconden van de S01-render, achter elkaar geplakt. Alle andere tijden zijn nieuwe tijd.
S01_END = 22.75
S01 = dict(
    length=26.2,
    picture_end=S01_END,
    edit=[(1.0, 5.95), (11.4, 18.4), (40.8, 51.6)],
    voice=[("S01/S01-01_Verteller.mp3", 0.2), ("S01/S01-03_Verteller.mp3", 5.4), ("S01/S01-04_Vriend.mp3", 9.2),
           ("S01/S01-08_Verteller.mp3", 14.6), ("S01/S01-09_Verteller.mp3", 17.8), ("S01/S01-10_Verteller.mp3", 20.8)],
    sounds=[
        dict(file="sfx/sfx_pretpark_sfeer", t=0.0, vol=0.5, keys=[(3.5, 0.5), (5.5, 0.10)], loop_to=S01_END, fade_in=0.4),
        dict(file="sfx/muziek_spanning", t=0.0, vol=0.32, loop_to=S01_END, fade_in=1.5),
        dict(file="sfx/sfx_remmen", t=0.7, vol=1.0),
        dict(file="sfx/sfx_trein_raast", t=2.9, vol=0.85, keys=[(5.0, 0.85), (6.3, 0.25)], fade_out=1.0),
        dict(file="sfx/sfx_hartslag", t=5.0, vol=0.6, cut=(0.0, 6.95), fade_in=1.0, fade_out=0.4),
        dict(file="sfx/sfx_whoosh", t=11.7, vol=0.6),
        dict(file="muziek/drums_build", t=11.95, vol=0.24, loop_to=S01_END, fade_in=2.0),
        dict(file="sfx/sfx_staal", t=12.12, vol=1.0),
        dict(file="sfx/sfx_metaal_buigt", t=12.6, vol=0.6),
        dict(file="sfx/sfx_bouten", t=16.54, vol=1.0, cut=(0.5, 1.0)),
        dict(file="sfx/sfx_bouten", t=17.57, vol=1.0, cut=(0.5, 1.0)),
        dict(file="sfx/sfx_bouten", t=18.48, vol=1.0, cut=(0.5, 1.0)),
        dict(file="sfx/sfx_riser", t=19.07, vol=0.8),
        dict(file="sfx/sfx_trein_raast", t=21.57, vol=0.9, cut=(0.5, 1.7)),
        dict(file="sfx/sfx_titel", t=21.92, vol=1.0),
    ],
    texts=[dict(body="DAY 16", t0=0.3, t1=S01_END, loc=(0.035, 0.94), size=92, color=(1, 1, 1, 1),
                anchor=("LEFT", "TOP"), pop=False),
           dict(body="65,536x STRONGER", t0=0.3, t1=S01_END, loc=(0.035, 0.845), size=52, color=(1.0, 0.82, 0.18, 1),
                anchor=("LEFT", "TOP"), pop=False)],
    cards=[],
    sim=None,
    title=("16 DAYS EARLIER", S01_END + 0.6, 26.2),
)
SCENES = {"s01": (S01, "S01_cold_open")}


# ---------------------------------------------------------------------------
# Mixen: de stem staat centraal
# ---------------------------------------------------------------------------
# Elk bestand wordt eerst gemeten en op een vast niveau gezet, zodat een hard opgenomen effect
# (achtbaan, remmen) nooit boven de stem uitkomt. Daarna duikt alles weg zodra er gesproken wordt.
VOICE_DB = -18.0        # gemiddeld niveau van de stem (dBFS, actieve delen)
SFX_DB = -26.0          # luidste 0,4 s van een effect bij vol 1.0
MUSIC_DB = -31.0        # gemiddeld niveau van muziek bij vol 0.3
AMB_DB = -38.0          # gemiddeld niveau van sfeergeluid bij vol 0.2
DUCK = dict(voice=1.0, sfx=0.45, music=0.32, amb=0.45)   # factor zolang er iemand praat

# niels (2026-10-26): de speelse muziek klonk te kinderlijk. Deze tracks worden bij de montage vervangen door
# serieuzere, filmische muziek; de scènescripts en beelden blijven zoals ze zijn.
MUSIC_SWAP = {
    "speels": "strijkers_warm", "funky": "drums_build", "retrofunk": "drums_build", "pizz_spanning": "cello",
    "ochtend": "piano_warm", "fiets": "opbouw_vliegen", "mall": "piano_hol", "mok_thema": "strijkers_emo",
    "lofi": "subbas", "kermis_wals": "drone", "jingle": "strijk_noot", "lente": "piano_zacht", "werkplaats": "drone",
}
_LEVELS = {}


def _level(path):
    """(luidste 0,4 s, gemiddeld actief niveau) in dBFS."""
    if path not in _LEVELS:
        import aud
        import numpy as np
        snd = aud.Sound(path)
        d = snd.data()
        sr = int(snd.specs[0])
        m = d.mean(axis=1) if d.ndim > 1 else d
        w = max(1, int(sr * 0.4))
        n = len(m) // w
        if n == 0:
            r = np.array([np.sqrt((m ** 2).mean() + 1e-12)])
        else:
            r = np.sqrt((m[:n * w].reshape(n, w) ** 2).mean(axis=1) + 1e-12)
        db = 20 * np.log10(r)
        act = db[db > db.max() - 30]
        _LEVELS[path] = (float(db.max()), float(10 * np.log10((10 ** (act / 10)).mean())))
    return _LEVELS[path]


def _kind(snd):
    f = snd["file"]
    if f.startswith("muziek/") or "/muziek_" in f:
        return "music"
    if "_sfeer" in f or "geroezemoes" in f or snd.get("loop_to"):
        return "amb"
    return "sfx"


def _gain(path, kind, v):
    import math
    peak, act = _level(path)
    v = max(0.0, v)
    if v <= 0:
        return 0.0
    if kind == "voice":
        db = VOICE_DB - act
    elif kind == "music":
        db = MUSIC_DB + 20 * math.log10(v / 0.3) - act
    elif kind == "amb":
        db = min(AMB_DB + 20 * math.log10(v / 0.2), -32.0) - act
    else:
        db = SFX_DB + 20 * math.log10(min(v, 1.0)) - peak
    return 10 ** (max(-40.0, min(18.0, db)) / 20)


def new_strip(kind, sed, name, channel, start, **kw):
    """Werkt met zowel de oude (sequences) als de nieuwe (strips) VSE-API."""
    coll = sed.strips if hasattr(sed, "strips") else sed.sequences
    if kind == "effect":
        length = kw.pop("length")
        try:
            return coll.new_effect(name=name, type=kw["type"], channel=channel, frame_start=start, length=length)
        except TypeError:
            return coll.new_effect(name=name, type=kw["type"], channel=channel, frame_start=start, frame_end=start + length)
    if kind == "sound":
        return coll.new_sound(name=name, filepath=kw["filepath"], channel=channel, frame_start=start)
    if kind == "image":
        return coll.new_image(name=name, filepath=kw["filepath"], channel=channel, frame_start=start)


_FONT = []


def _font():
    """Inter (zit bij Blender) in plaats van het standaard monospace-lettertype."""
    if not _FONT:
        d = bpy.utils.system_resource("DATAFILES", path="fonts") or ""
        p = os.path.join(d, "Inter.woff2")
        _FONT.append(bpy.data.fonts.load(p, check_existing=True) if os.path.exists(p) else None)
    return _FONT[0]


def text(sed, body, t0, t1, loc, size, color, channel, anchor=("LEFT", "TOP")):
    s = new_strip("effect", sed, body[:20], channel, F(t0), type="TEXT", length=F(t1) - F(t0))
    s.text = body
    s.font_size = size * bpy.context.scene.render.resolution_x / 1920
    font = _font()
    if font:
        s.font = font
    s.color = color
    s.location = loc
    if hasattr(s, "use_bold"):
        s.use_bold = True
    s.use_shadow = True
    if hasattr(s, "shadow_color"):
        s.shadow_color = (0, 0, 0, 0.85)
    if hasattr(s, "anchor_x"):
        s.anchor_x, s.anchor_y = anchor
    else:
        s.align_x, s.align_y = anchor
    return s


def _pack(used, base, f0, f1):
    """Eerste vrije kanaal vanaf base waar [f0, f1) niet overlapt."""
    ch = base
    while True:
        if all(f1 <= a or f0 >= b for a, b in used.get(ch, [])):
            used.setdefault(ch, []).append((f0, f1))
            return ch
        ch += 1


def _alen(path):
    import aud
    s = aud.Sound(path)
    return s.length / s.specs[0]


def _legacy(spec):
    """Oude S01-notatie -> nieuwe notatie."""
    out = dict(length=spec["length"], picture_end=spec["picture_end"], voice=[(v + ".mp3", t) for v, t in spec["voice"]],
               sounds=[], texts=[], cards=[], sim=spec.get("sim"), title=spec.get("title"))
    for name, t, vol, cut, keys in spec["sounds"]:
        out["sounds"].append(dict(file=name, t=t, vol=vol, cut=cut, keys=keys, loop_to=None, duck=False))
    for body, h0, h1, loc, size, col in spec["hud"]:
        out["texts"].append(dict(body=body, t0=h0, t1=h1, loc=loc, size=size, color=col, anchor=("LEFT", "TOP"), pop=False))
    return out


def _fade(s, f0, f1, pop=True, out=True):
    if not pop:
        return
    s.blend_alpha = 0.0
    s.keyframe_insert("blend_alpha", frame=f0)
    s.blend_alpha = 1.0
    s.keyframe_insert("blend_alpha", frame=f0 + 4)
    if out and f1 - f0 > 10:
        s.keyframe_insert("blend_alpha", frame=f1 - 4)
        s.blend_alpha = 0.0
        s.keyframe_insert("blend_alpha", frame=f1)


def build(spec, frames_dir, out, render=True):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.name = os.path.basename(os.path.splitext(out)[0]) + "_montage"
    sc.render.fps = FPS
    length = spec["length"]
    pic_end = spec.get("picture_end") or length
    sc.frame_start, sc.frame_end = 1, int(round(length * FPS))
    sed = sc.sequence_editor_create()
    used = {}

    files = sorted(glob.glob(os.path.join(frames_dir, "*.png")))
    if not files:
        raise SystemExit("Geen beelden gevonden in " + frames_dir)
    img = bpy.data.images.load(files[0])
    sc.render.resolution_x, sc.render.resolution_y = img.size
    sc.render.resolution_percentage = 100
    bpy.data.images.remove(img)

    # beeld
    if spec.get("edit"):
        # montage uit stukken van één render: frame n van de render is bestand nr. n
        byno = {int(re.findall(r"(\d+)\.png$", f)[0]): f for f in files}
        pos = 1
        for i, (a, b) in enumerate(spec["edit"]):
            part = [byno[n] for n in range(F(a), F(b)) if n in byno]
            if len(part) != F(b) - F(a):
                raise SystemExit("Beelden ontbreken voor stuk %d (%.2f-%.2f s)" % (i, a, b))
            pic = new_strip("image", sed, "beeld%d" % i, 2, pos, filepath=part[0])
            for f in part[1:]:
                pic.elements.append(os.path.basename(f))
            print("stuk %d: %.2f-%.2f s -> %.3f s" % (i, a, b, (pos - 1) / FPS))
            pos += len(part)
        print("beeld tot %.3f s (picture_end %.3f)" % ((pos - 1) / FPS, pic_end))
    else:
        pic = new_strip("image", sed, "beeld", 2, 1, filepath=files[0])
        for f in files[1:]:
            pic.elements.append(os.path.basename(f))
        pic.frame_final_end = min(pic.frame_final_end, F(pic_end))
    black = new_strip("effect", sed, "zwart", 1, 1, type="COLOR", length=sc.frame_end)
    black.color = (0, 0, 0)

    # simulatie (alleen S01): blauw en ontkleurd, met een label
    if spec.get("sim"):
        t0, t1 = spec["sim"]
        adj = new_strip("effect", sed, "simulatie", 3, F(t0), type="ADJUSTMENT", length=F(t1) - F(t0))
        adj.color_saturation = 0.35
        adj.color_multiply = 1.05
        cb = adj.modifiers.new("blauw", "COLOR_BALANCE")
        cb.color_balance.gain = (0.78, 0.98, 1.30)
        cb.color_balance.lift = (0.95, 1.0, 1.08)
        text(sed, "SIMULATION", t0 + 0.15, t1, (0.965, 0.94), 56, (0.35, 0.95, 1.0, 1), 6, anchor=("RIGHT", "TOP"))

    # titelkaarten: verdonkerde achtergrond + grote tekst
    for c in spec.get("cards", []):
        f0, f1 = F(c["t0"]), F(c["t1"])
        dim = new_strip("effect", sed, "dim", _pack(used, 20, f0, f1), f0, type="COLOR", length=f1 - f0)
        dim.color = tuple(c.get("bg") or (0.02, 0.02, 0.05))
        dim.blend_type = "ALPHA_OVER"
        fin, fout = c.get("fin", 5), c.get("fout", 5)
        dim.blend_alpha = 0.0
        dim.keyframe_insert("blend_alpha", frame=f0)
        dim.blend_alpha = c["dim"]
        dim.keyframe_insert("blend_alpha", frame=f0 + fin)
        dim.keyframe_insert("blend_alpha", frame=f1 - fout)
        dim.blend_alpha = 0.0
        dim.keyframe_insert("blend_alpha", frame=f1)
        if not c["body"].strip():
            continue
        s = text(sed, c["body"], c["t0"], c["t1"], (0.5, 0.54), c["size"], tuple(c["color"]), _pack(used, 20, f0, f1),
                 anchor=("CENTER", "CENTER"))
        _fade(s, f0, f1)
        if c.get("sub"):
            s2 = text(sed, c["sub"], c["t0"] + 0.3, c["t1"], (0.5, 0.40), int(c["size"] * c.get("sub_scale", 0.45)), (1.0, 0.82, 0.18, 1),
                      _pack(used, 20, F(c["t0"] + 0.3), f1), anchor=("CENTER", "CENTER"))
            _fade(s2, F(c["t0"] + 0.3), f1)

    # HUD en andere teksten
    for x in spec.get("texts", []):
        t1 = x["t1"] if x["t1"] is not None else pic_end
        f0, f1 = F(x["t0"]), F(t1)
        s = text(sed, x["body"], x["t0"], t1, tuple(x["loc"]), x["size"], tuple(x["color"]), _pack(used, 40, f0, f1),
                 anchor=tuple(x["anchor"]))
        _fade(s, f0, f1, x.get("pop", True), out=x["t1"] is not None)

    # titel (S01: "16 DAYS EARLIER")
    if spec.get("title"):
        body, h0, h1 = spec["title"]
        title = text(sed, body, h0, h1, (0.5, 0.5), 140, (1, 1, 1, 1), _pack(used, 20, F(h0), F(h1)), anchor=("CENTER", "CENTER"))
        title.blend_alpha = 0.0
        title.keyframe_insert("blend_alpha", frame=F(h0))
        title.blend_alpha = 1.0
        title.keyframe_insert("blend_alpha", frame=F(h0) + 4)

    # stem: genormaliseerd, altijd het luidst
    vint = []
    for name, t in spec["voice"]:
        path = os.path.join(AUDIO, name)
        d = _alen(path)
        f0 = F(t)
        s = new_strip("sound", sed, os.path.basename(name)[:30], _pack(used, 60, f0, f0 + int(d * FPS) + 2), f0, filepath=path)
        s.volume = _gain(path, "voice", 1.0) * float(os.environ.get("MIX_VOICE", "1"))
        vint.append((t, t + d))

    def duck_at(t):
        d = 0.0
        for a, b in vint:
            if a - 0.3 <= t <= b + 0.5:
                w = min(1.0, (t - (a - 0.3)) / 0.25, ((b + 0.5) - t) / 0.35)
                d = max(d, max(0.0, w))
        return d

    # geluid en muziek: elk bestand op een vast niveau onder de stem, en alles duikt weg zodra er gesproken wordt
    for snd in spec["sounds"]:
        if snd["file"].startswith("muziek/"):
            snd["file"] = "muziek/" + MUSIC_SWAP.get(snd["file"][7:], snd["file"][7:])
        path = os.path.join(AUDIO, snd["file"] + ("" if snd["file"].endswith(".mp3") else ".mp3"))
        if not os.path.exists(path):
            print("LET OP: geluid ontbreekt", path)
            continue
        kind = _kind(snd)
        flen = _alen(path)
        cut = snd.get("cut") or (0.0, None)
        c0 = cut[0] or 0.0
        c1 = cut[1] if cut[1] is not None else flen
        piece = max(0.05, c1 - c0)
        t_start = snd["t"]
        t_end = snd.get("loop_to") or (t_start + piece)
        t_end = min(t_end, length if "titel" in snd["file"] else pic_end)
        fi, fo = snd.get("fade_in", 0.0), snd.get("fade_out", 0.0)
        keys = snd.get("keys")

        def vol_at(p, snd=snd, keys=keys, kind=kind, path=path, fi=fi, fo=fo, t_start=t_start, t_end=t_end):
            v = snd["vol"]
            if keys:
                ks = sorted(keys)
                v = ks[0][1] if p <= ks[0][0] else ks[-1][1]
                for (ka, va), (kb, vb) in zip(ks, ks[1:]):
                    if ka <= p <= kb:
                        v = va + (vb - va) * (p - ka) / max(1e-6, kb - ka)
            g = _gain(path, kind, v)
            if fi:
                g *= min(1.0, max(0.0, (p - t_start) / fi))
            if fo:
                g *= min(1.0, max(0.0, (t_end - p) / fo))
            return g * (1.0 - (1.0 - DUCK[kind]) * duck_at(p))

        tt = t_start
        first = True
        while tt < t_end - 0.05:
            seg = min(piece if first else (flen if cut[1] is None else piece), t_end - tt)
            src0 = c0 if first else (0.0 if cut[1] is None and c0 > 0 else c0)
            f0 = F(tt)
            nframes = max(1, int(round(seg * FPS)))
            ch = _pack(used, 80, f0, f0 + nframes)
            s = new_strip("sound", sed, os.path.basename(snd["file"])[:30], ch, f0 - int(round(src0 * FPS)), filepath=path)
            s.frame_final_start = f0
            s.frame_final_end = f0 + nframes
            pts = {tt, tt + seg}
            if fi:
                pts |= {t_start, t_start + fi}
            if fo:
                pts |= {t_end - fo, t_end}
            for k in keys or []:
                pts.add(k[0])
            for a, b in vint:
                pts |= {a - 0.3, a - 0.05, b + 0.15, b + 0.5}
            for p in sorted(pts):
                if tt - 0.01 <= p <= tt + seg + 0.01:
                    s.volume = vol_at(p)
                    s.keyframe_insert("volume", frame=F(p))
            tt += seg
            first = False

    # uitvoer: H.264 + AAC
    r = sc.render
    if hasattr(r.image_settings, "media_type"):
        r.image_settings.media_type = "VIDEO"
    r.image_settings.file_format = "FFMPEG"
    r.ffmpeg.format = "MPEG4"
    r.ffmpeg.codec = "H264"
    r.ffmpeg.constant_rate_factor = "HIGH"
    r.ffmpeg.ffmpeg_preset = "GOOD"
    r.ffmpeg.audio_codec = "AAC"
    r.ffmpeg.audio_bitrate = 192
    r.ffmpeg.audio_channels = "STEREO"
    r.ffmpeg.audio_mixrate = 48000
    r.use_sequencer = True
    r.filepath = out
    os.makedirs(os.path.dirname(out), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.splitext(out)[0] + "_montage.blend", relative_remap=False)
    if render:
        bpy.ops.render.render(animation=True)
        print("KLAAR", out)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("scene", default="s01", nargs="?")
    ap.add_argument("--frames", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--norender", action="store_true")
    a = ap.parse_args(argv)
    sdir = os.path.join(REPO, "out", a.scene)
    if a.scene in SCENES:
        spec, base = SCENES[a.scene]
        if "hud" in spec:
            spec = _legacy(spec)
    else:
        with open(os.path.join(sdir, "montage.json")) as fh:
            spec = json.load(fh)
        base = a.scene.upper()
    frames_dir = os.path.abspath(a.frames or os.path.join(sdir, "frames"))
    out = os.path.abspath(a.out or os.path.join(sdir, base + ".mp4"))
    build(spec, frames_dir, out, render=not a.norender)


main()
