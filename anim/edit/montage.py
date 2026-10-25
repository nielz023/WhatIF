"""Montage: gerenderde beelden + stem + geluid + muziek + HUD -> MP4 (in Blender zelf, geen ffmpeg nodig).

Gebruik (Blender 5.2):
    blender -b -P anim/edit/montage.py -- s01 [--frames out/s01/frames] [--out out/s01/S01_cold_open.mp4]

Elke scène heeft hieronder een lijst met geluiden (tijd in seconden), teksten en effecten.
"""
import argparse
import glob
import os
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
S01 = dict(
    length=55.0,
    picture_end=51.6,                      # smash cut naar zwart
    voice=[("S01/S01-01_Verteller", 1.2), ("S01/S01-02_Verteller", 4.3), ("S01/S01-03_Verteller", 11.8),
           ("S01/S01-04_Vriend", 15.6), ("S01/S01-05_Verteller", 18.6), ("S01/S01-06_Verteller", 24.4),
           ("S01/S01-07_Verteller", 38.2), ("S01/S01-08_Verteller", 43.4), ("S01/S01-09_Verteller", 46.6),
           ("S01/S01-10_Verteller", 49.6)],
    # (bestand, start, volume, [knip_in, knip_uit] in seconden binnen het bestand, volumesleutels (t, v))
    sounds=[
        ("sfx/sfx_pretpark_sfeer", 0.0, 0.55, None, [(7.8, 0.55), (9.6, 0.10)]),
        ("sfx/sfx_pretpark_sfeer", 29.9, 0.10, (0.0, 21.7), None),
        ("sfx/muziek_spanning", 1.0, 0.0, None, [(1.0, 0.0), (2.4, 0.32)]),
        ("sfx/muziek_spanning", 30.9, 0.32, (0.0, 20.7), None),
        ("sfx/sfx_remmen", 1.7, 1.0, None, None),
        ("sfx/sfx_trein_raast", 3.9, 0.85, None, [(7.6, 0.85), (8.9, 0.25)]),
        ("sfx/sfx_slowmo", 8.5, 0.9, None, None),
        ("sfx/sfx_knokkels", 19.0, 1.0, None, None),
        ("sfx/sfx_hologram", 24.0, 0.7, None, None),
        ("sfx/sfx_schuiven", 30.8, 0.9, None, None),
        ("sfx/sfx_hologram", 37.35, 0.55, None, None),
        ("sfx/sfx_staal", 40.95, 1.0, None, None),
        ("sfx/sfx_bouten", 45.92 - 0.55, 3.0, (0.5, 1.0), None),
        ("sfx/sfx_bouten", 46.95 - 0.55, 3.0, (0.5, 1.0), None),
        ("sfx/sfx_bouten", 47.86 - 0.55, 3.5, (0.5, 1.0), None),
        ("sfx/sfx_riser", 47.9, 0.8, None, None),
        ("sfx/sfx_trein_raast", 50.4, 0.9, (0.5, 1.7), None),
        ("sfx/sfx_titel", 50.75, 1.0, None, None),
    ],
    hud=[("DAY 16", 0.3, 51.6, (0.035, 0.94), 92, (1, 1, 1, 1)),
         ("65,536x STRONGER", 0.3, 51.6, (0.035, 0.845), 52, (1.0, 0.82, 0.18, 1))],
    sim=(24.2, 37.6),
    title=("16 DAYS EARLIER", 52.2, 55.0),
)
SCENES = {"s01": (S01, "S01_cold_open")}


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


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("scene", default="s01", nargs="?")
    ap.add_argument("--frames", default=None)
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    spec, base = SCENES[a.scene]
    frames_dir = os.path.abspath(a.frames or os.path.join(REPO, "out", a.scene, "frames"))
    out = os.path.abspath(a.out or os.path.join(REPO, "out", a.scene, base + ".mp4"))

    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.name = base + "_montage"
    sc.render.fps = FPS
    sc.frame_start, sc.frame_end = 1, int(round(spec["length"] * FPS))
    sed = sc.sequence_editor_create()

    files = sorted(glob.glob(os.path.join(frames_dir, "*.png")))
    if not files:
        raise SystemExit("Geen beelden gevonden in " + frames_dir)
    img = bpy.data.images.load(files[0])
    sc.render.resolution_x, sc.render.resolution_y = img.size
    sc.render.resolution_percentage = 100
    bpy.data.images.remove(img)

    # beeld
    pic = new_strip("image", sed, "beeld", 2, 1, filepath=files[0])
    for f in files[1:]:
        pic.elements.append(os.path.basename(f))
    pic.frame_final_end = min(pic.frame_final_end, F(spec["picture_end"]))
    black = new_strip("effect", sed, "zwart", 1, 1, type="COLOR", length=sc.frame_end)
    black.color = (0, 0, 0)

    # simulatie: blauw en ontkleurd, met een label
    t0, t1 = spec["sim"]
    adj = new_strip("effect", sed, "simulatie", 3, F(t0), type="ADJUSTMENT", length=F(t1) - F(t0))
    adj.color_saturation = 0.35
    adj.color_multiply = 1.05
    cb = adj.modifiers.new("blauw", "COLOR_BALANCE")
    cb.color_balance.gain = (0.78, 0.98, 1.30)
    cb.color_balance.lift = (0.95, 1.0, 1.08)
    text(sed, "SIMULATION", t0 + 0.15, t1, (0.965, 0.94), 56, (0.35, 0.95, 1.0, 1), 6, anchor=("RIGHT", "TOP"))

    # HUD
    for k, (body, h0, h1, loc, size, col) in enumerate(spec["hud"]):
        text(sed, body, h0, h1, loc, size, col, 4 + k)

    # titelkaart
    body, h0, h1 = spec["title"]
    title = text(sed, body, h0, h1, (0.5, 0.5), 140, (1, 1, 1, 1), 7, anchor=("CENTER", "CENTER"))
    title.blend_alpha = 0.0
    title.keyframe_insert("blend_alpha", frame=F(h0))
    title.blend_alpha = 1.0
    title.keyframe_insert("blend_alpha", frame=F(h0) + 4)

    # stem
    ch = 10
    for name, t in spec["voice"]:
        s = new_strip("sound", sed, name.split("/")[-1], ch, F(t), filepath=os.path.join(AUDIO, name + ".mp3"))
        s.volume = 1.0
        ch = 10 if ch == 11 else 11
    # geluid en muziek
    for k, (name, t, vol, cut, keys) in enumerate(spec["sounds"]):
        s = new_strip("sound", sed, name.split("/")[-1], 12 + k % 12, F(t), filepath=os.path.join(AUDIO, name + ".mp3"))
        if cut:
            start = s.frame_start
            s.frame_final_end = int(start + cut[1] * FPS)
            s.frame_final_start = int(start + cut[0] * FPS)
        s.volume = vol
        for tk, v in keys or []:
            s.volume = v
            s.keyframe_insert("volume", frame=F(tk))
        if s.frame_final_end > F(spec["picture_end"]) and "titel" not in name:
            s.frame_final_end = F(spec["picture_end"])

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
    bpy.ops.render.render(animation=True)
    print("KLAAR", out)


main()
