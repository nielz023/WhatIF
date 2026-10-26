"""Plakt alle gemonteerde delen (S01 ... S28) achter elkaar tot de hele video, met Blenders eigen videobewerker
(geen losse ffmpeg nodig).

    blender -b -P anim/edit/assemble.py -- <map met de delen> [--out <video.mp4>] [--allow-missing]

De volgorde komt uit anim/scenes: elk scènescript sXX[_naam].py is één deel. In de map hoort per deel een mp4 die
begint met de code in hoofdletters, bijvoorbeeld S03A_keuken.mp4 of S03A.mp4. Ontbreekt er een, dan stopt het
script (of slaat het over met --allow-missing).
"""
import argparse
import glob
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
FPS = 24


def scene_codes():
    codes = []
    for p in sorted(glob.glob(os.path.join(REPO, "anim", "scenes", "s[0-9][0-9]*.py"))):
        codes.append(os.path.basename(p).split("_")[0].split(".")[0].upper())
    return codes


def find_part(folder, code):
    hits = [f for f in os.listdir(folder) if f.lower().endswith(".mp4")
            and (f.upper().startswith(code + "_") or os.path.splitext(f)[0].upper() == code)]
    return os.path.join(folder, sorted(hits)[0]) if hits else None


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--out", default=None)
    ap.add_argument("--allow-missing", action="store_true")
    a = ap.parse_args(argv)
    folder = os.path.abspath(a.folder)
    out = os.path.abspath(a.out or os.path.join(folder, "..", "WHAT_IF_2x_STRONGER.mp4"))

    parts, missing = [], []
    for code in scene_codes():
        p = find_part(folder, code)
        (parts if p else missing).append(p or code)
    if missing:
        print("ONTBREEKT:", ", ".join(missing))
        if not a.allow_missing:
            print("FOUT: niet alle delen zijn er (gebruik --allow-missing om toch te plakken)")
            return

    sc = bpy.context.scene
    sc.render.fps = FPS
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
    sc.render.resolution_percentage = 100
    sed = sc.sequence_editor_create()
    coll = sed.strips if hasattr(sed, "strips") else sed.sequences
    f = 1
    for p in parts:
        mv = coll.new_movie(name=os.path.basename(p)[:30], filepath=p, channel=1, frame_start=f)
        try:
            snd = coll.new_sound(name="geluid_" + os.path.basename(p)[:24], filepath=p, channel=2, frame_start=f)
            snd.frame_final_end = f + mv.frame_final_duration
        except Exception as e:  # deel zonder geluidsspoor
            print("geen geluid in", p, e)
        print(f"{os.path.basename(p)}: frame {f}, {mv.frame_final_duration / FPS:.1f} s")
        f += mv.frame_final_duration
    sc.frame_start, sc.frame_end = 1, f - 1

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
    total = (f - 1) / FPS
    print(f"{len(parts)} delen, {int(total // 60)}:{int(total % 60):02d} lang -> {out}")
    bpy.ops.render.render(animation=True)
    print("KLAAR", out)


main()
