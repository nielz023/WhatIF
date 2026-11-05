"""Thumbnail video 3 (What IF There Were NO RULES?), bijlage E van het script.

Bouwt de cold open (anim/v3/scenes/n01_kruispunt.py: kruispunt 's nachts, rode alarmborden, de jongen in
pyjamabroek en hoodie), zet de jongen op één moment in een schrikpose en rendert een still vanuit een eigen
thumbnail-camera met extra rood licht op zijn gezicht. De tekst komt er daarna op met compose_thumb.py.

    python3 videos/geen-regels/thumbnail/thumb_no_rules.py -- <variant> [--pct 100] [--samples 128]
    (of: blender -b -P videos/geen-regels/thumbnail/thumb_no_rules.py -- <variant> ...)

Varianten:
    straat   groot gezicht rechts, recht in de lens; links achter hem een rood bord op de gevel
    groot    groot gezicht rechts; links boven het eind van de straat het enorme rode scherm
    omhoog   lage camera, hij kijkt geschrokken omhoog naar de rode schermen boven het kruispunt

Uitvoer: out/thumb/render_<variant>.png (1920x1080 bij --pct 100).
Env: WHATIF_ENGINE=CYCLES en WHATIF_CAST=cast_v3 worden standaard gezet.
"""
import math
import os
import runpy
import sys

os.environ.setdefault("WHATIF_ENGINE", "CYCLES")
os.environ.setdefault("WHATIF_CAST", "cast_v3")
os.environ.setdefault("WHATIF_NOQC", "1")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
VAR = argv[0] if argv and not argv[0].startswith("--") else "straat"


def opt(name, default):
    return type(default)(argv[argv.index(name) + 1]) if name in argv else default


PCT = opt("--pct", 100)
SAMPLES = opt("--samples", 128)
OUT = os.path.join(REPO, "out", "thumb")
os.makedirs(OUT, exist_ok=True)

# ------------------------------------------------------------------ cold open opbouwen (zonder renderen/opslaan)
os.chdir(REPO)
sys.argv = [sys.argv[0], "--", "--nosave", "--samples", str(SAMPLES), "--out", os.path.join(OUT, "n01")]
G = runpy.run_path(os.path.join(REPO, "anim", "v3", "scenes", "n01_kruispunt.py"))

import bpy  # noqa: E402
from mathutils import Vector as V  # noqa: E402

S, held, A, F = G["S"], G["held"], G["A"], G["F"]
T = G["T"]
sc = bpy.context.scene

# moment: na het afremmen, vóór de knipper van 1g; alle borden staan dan op rood
t = G["t_g"] + 0.8
f = F(t)
# n01 rekt 24 fps op naar 30 (frame_map); voor een still terug naar 1:1, anders valt de frame op een ander moment
sc.render.fps = 24
sc.render.frame_map_old = sc.render.frame_map_new = 100
sc.timeline_markers.clear()                      # geen shotcamera's meer die de thumbnail-camera overnemen
for o in [o for o in bpy.data.objects if o.name.startswith("N01_rood_flakker")]:
    bpy.data.objects.remove(o, do_unlink=True)

STOP = V((0.0, -1.6, 0.0))


def unit(v):
    v = V(v)
    return v / v.length


def bb_center(name):
    o = bpy.data.objects[name]
    pts = [o.matrix_world @ V(c) for c in o.bound_box]
    return sum(pts, V()) / len(pts)


# ------------------------------------------------------------------ pose per variant
if VAR == "straat":
    rot = 0.0                                     # gezicht naar -y, rug naar het grote scherm (y = +82)
    look = (0.0, 0.0)
    face = ("geschrokken", 1.0)
elif VAR == "groot":
    CAM_OFF = V((-0.78, -0.62, -0.28))             # camera links-voor hem; het grote scherm (y = +82) links in beeld
    d = unit(CAM_OFF.to_2d().to_3d())
    rot = math.degrees(math.atan2(d.x, -d.y))     # rot 0 kijkt naar -y; (sin r, -cos r) = d: hij kijkt de camera aan
    look = (0.0, 0.0)
    face = ("geschrokken", 1.0)
else:  # omhoog
    rot = 180.0                                   # gezicht naar +y, achter hem borden 3 en 4
    look = (0.0, 0.8)
    face = ("geschrokken", 1.0)

A.place(held, f - 1, tuple(STOP), rot)
A.place(held, f, tuple(STOP), rot)
A.place(held, f + 1, tuple(STOP), rot)
for ff in (f - 1, f, f + 1):
    A.expr(held, ff, face[0], amount=face[1], look=look)
    A.key_prop(held.rig, "mond_open", 0.42, ff)
    A.key_prop(held.rig, "knipper", 0.0, ff) if "knipper" in held.rig.keys() else None
    if VAR == "omhoog":
        pass
    else:
        A.bone_rot(held, ff, "head", (-4, -6 if VAR == "straat" else 0, 0))
        A.bone_rot(held, ff, "chest", (0, 0, 0))
if VAR == "omhoog":                              # kijkt omhoog naar het grote scherm boven/achter de camera
    for tt in (t - 1 / 24, t, t + 1 / 24):
        S.beat(held, tt, "staan", face="geschrokken", face_amt=1.0, at=V((0.0, 30.0, 9.0)))
    for ff in (f - 1, f, f + 1):
        A.key_prop(held.rig, "mond_open", 0.42, ff)
sc.frame_set(f)
bpy.context.view_layer.update()
H = S.headpos(held, t)
print("THUMB", VAR, "t", t, "frame", f, "hoofd", tuple(round(x, 2) for x in H), "rot", rot)

# ------------------------------------------------------------------ camera
cam_data = bpy.data.cameras.new("THUMB_cam")
cam = bpy.data.objects.new("THUMB_cam", cam_data)
sc.collection.objects.link(cam)
cam_data.sensor_width = 36
cam_data.clip_start = 0.05
cam_data.clip_end = 600


def aim(loc, target, lens):
    cam.location = loc
    cam.rotation_euler = (V(target) - V(loc)).to_track_quat("-Z", "Y").to_euler()
    cam_data.lens = lens


if VAR == "straat":
    # dichtbij en iets van onderen: hoofd rechts, links de straat in met het grote scherm boven het eind
    C = H + V((0.42, -0.95, -0.30))
    aim(C, H + V((-0.38, 0.0, 0.22)), 24)
    dof_target = H
elif VAR == "groot":
    C = H + CAM_OFF
    SCR = bb_center("Billboard_groot_frame")
    tgt = C + unit(H - C) * 0.75 + unit(SCR - C) * 1.25   # tussen hoofd (rechts) en scherm (links)
    aim(C, tgt, 20)
    dof_target = H
else:
    C = H + V((0.25, 0.85, -0.55))
    aim(C, H + V((-0.6, -3.0, 2.0)), 20)
    dof_target = H
cam_data.dof.use_dof = True
cam_data.dof.focus_distance = (V(dof_target) - cam.location).length
cam_data.dof.aperture_fstop = 2.8 if VAR != "omhoog" else 4.0
sc.camera = cam

# ------------------------------------------------------------------ licht: rood schermlicht op zijn gezicht
cam_dir = unit(cam.location - H)
right = unit(cam_dir.cross(V((0, 0, 1))))


FACE = float(os.environ.get("THUMB_FACE", 1.0))


def area(name, loc, target, color, energy, size):
    energy *= FACE
    ld = bpy.data.lights.new(name, "AREA")
    ld.color, ld.energy, ld.size = color, energy, size
    lo = bpy.data.objects.new(name, ld)
    sc.collection.objects.link(lo)
    lo.location = loc
    lo.rotation_euler = (V(target) - V(loc)).to_track_quat("-Z", "Y").to_euler()
    lo.visible_camera = False
    return lo


# de glans-randlichten van de figuur volgen hem in de video; hier achter hem zetten t.o.v. de thumbnail-camera
for o in [o for o in bpy.data.objects if o.name.startswith("Randlicht_") and o.type == "LIGHT"]:
    o.animation_data_clear()
    o.data.animation_data_clear()
    for c in list(o.constraints):
        o.constraints.remove(c)
    o.parent = None
    s_ = 1.0 if "oranje" in o.name else -1.0
    o.location = H - cam_dir * 1.5 + right * (1.3 * s_) + V((0, 0, 0.5))
    o.rotation_euler = (H - o.location).to_track_quat("-Z", "Y").to_euler()
    o.data.energy *= 0.6

RED = (1.0, 0.07, 0.04)
# hoofdlicht: rood van schuin boven, aan de kant van de borden
area("THUMB_rood_key", H + cam_dir * 1.1 + right * 1.3 + V((0, 0, 1.0)), H, RED, 240, 1.4)
# rood randlicht van achteren (het scherm achter hem)
area("THUMB_rood_rim", H - cam_dir * 1.4 - right * 0.9 + V((0, 0, 1.1)), H, RED, 300, 1.0)
# koel maanlicht aan de andere kant, zodat het gezicht vorm houdt (glans: oranje/blauw randlicht)
area("THUMB_blauw_vul", H + cam_dir * 1.0 - right * 1.4 + V((0, 0, 0.3)), H, (0.35, 0.5, 1.0), 45, 1.2)
# zacht warm oogwit-licht vanaf de camera (oogglans, huid niet helemaal rood)
area("THUMB_oog", cam.location + V((0, 0, 0.25)), H, (1.0, 0.85, 0.75), 4, 0.6)

# nacht donkerder dan in de video: maan en lucht omlaag, zodat het rode licht het beeld draagt
DARK = float(os.environ.get("THUMB_DARK", 0.35))
for o in bpy.data.objects:
    if o.type == "LIGHT" and (o.data.type == "SUN" or o.name in ("Maan_vul", "N01_vul_laag")):
        o.data.energy *= DARK
w = sc.world
if w and w.use_nodes:
    for n in w.node_tree.nodes:
        if n.type == "BACKGROUND":
            n.inputs["Strength"].default_value *= DARK

# ------------------------------------------------------------------ render
sc.render.engine = "CYCLES"
sc.cycles.samples = SAMPLES
sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
sc.render.resolution_percentage = PCT
VT = os.environ.get("THUMB_VIEW", "AgX")
sc.view_settings.view_transform = VT
sc.view_settings.look = "AgX - Punchy" if VT == "AgX" else "None"
sc.view_settings.exposure = float(os.environ.get("THUMB_EXPOSURE", 0.05))
sc.render.image_settings.file_format = "PNG"
sc.render.filepath = os.path.join(OUT, f"render_{VAR}{os.environ.get('THUMB_TAG', '')}.png")
sc.frame_set(f)
bpy.ops.render.render(write_still=True)
print("THUMB KLAAR", sc.render.filepath)
