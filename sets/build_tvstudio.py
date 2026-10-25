"""Set: Tv-studio van een ochtendshow. Video 1, dag 11. Fel studiolicht, warm geel.

Gebruik:
    blender -b -P sets/build_tvstudio.py -- [studio] [uitvoermap]
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402,F401
from lib import toon as T  # noqa: E402
from lib import props as P  # noqa: E402
from lib import interior as I  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
OUT = args[1] if len(args) > 1 else "/mnt/project-files/sets/12_tvstudio"
rnd = random.Random(12)

mood = dict(T.MOODS["binnen"])
mood.update(ambient=(0.10, 0.09, 0.12), shadow_tint=(0.45, 0.38, 0.55), lit_tint=(1.0, 0.95, 0.85), sun_strength=0.0, fog_max=0.0, bloom=0.8)
T.new_scene("Tvstudio", mood, samples=48)

W, D, H = 22.0, 20.0, 7.0
T.use_collection(T.collection("Studio"))
room = I.room("Studio", W, D, H, wall_color=(0.08, 0.08, 0.10), floor_color=(0.10, 0.10, 0.12), skirting=False)
room["ceiling"].data.materials[0] = T.toon("studio_plafond", (0.05, 0.05, 0.06))

# podium + decor (halfronde set aan de achterkant)
YEL = T.toon("decor_geel", (0.98, 0.72, 0.15))
ORG = T.toon("decor_oranje", (0.95, 0.42, 0.12))
T.cyl("Podium", (0, 4.0, 0), 6.5, 0.35, T.pattern("podiumvloer", (0.78, 0.55, 0.32), (0.74, 0.51, 0.29), grout=(0.6, 0.4, 0.2), size=(1.5, 0.15), mortar=0.004, offset=0.5), seg=64, ol=0.015).scale.y = 0.6
panels = []
for k in range(9):
    a = math.radians(-70 + k * 17.5)
    x, y = 6.4 * math.sin(a), 4.0 + 6.4 * 0.6 * math.cos(a) + 0.6
    panels.append(T.box(f"Decorwand_{k}", (x, y, 0.35), (2.2, 0.2, 4.2), YEL if k % 2 else ORG, rot=(0, 0, -math.degrees(a) * 0.8), bevel=0.04, ol=0))
T.merge("Decorwand", panels, ol=0.02)
# grote schermen met showlogo
for k, x in enumerate((-3.6, 0, 3.6)):
    sc = [T.box(f"Scherm_{k}_rand", (0, 0, 0), (3.0, 0.12, 1.8), P.m("zwart"), bevel=0.03, ol=0),
          T.box(f"Scherm_{k}_beeld", (0, -0.065, 0.08), (2.8, 0.01, 1.64), T.glow("showscherm", (0.95, 0.55, 0.15), 1.6), bevel=0, ol=0)]
    o = T.merge(f"Showscherm_{k + 1}", sc, ol=0.01)
    o.location = (x, 7.2 - abs(x) * 0.25, 2.2 if k == 1 else 2.0)
    o.rotation_euler.z = math.radians(-x * 6)
    T.text(f"Showlogo_{k + 1}", "GOOD MORNING" if k == 1 else "LIVE", (x, 7.2 - abs(x) * 0.25 - 0.08, 2.75 if k == 1 else 2.6), 0.42 if k == 1 else 0.6,
           T.glow("logo_wit", (1.0, 1.0, 1.0), 3.0), rot=(90, 0, -x * 6), extrude=0.01)
    if k == 1:
        T.text("Showlogo_sub", "SHOW", (0, 7.2 - 0.08, 2.25), 0.5, T.glow("logo_wit", (1.0, 1.0, 1.0), 3.0), extrude=0.01)

# bank + salontafel met mokken
T.use_collection(T.collection("Meubels"))
SOFA = T.toon("bank_blauw", (0.15, 0.35, 0.75))
sofa = [T.box("Bank_zit", (0, 0, 0.0), (3.2, 0.95, 0.48), SOFA, bevel=0.12, ol=0),
        T.box("Bank_rug", (0, 0.4, 0.4), (3.2, 0.25, 0.65), SOFA, bevel=0.1, ol=0),
        T.box("Bank_arm_l", (-1.55, 0, 0.3), (0.25, 0.95, 0.4), SOFA, bevel=0.1, ol=0),
        T.box("Bank_arm_r", (1.55, 0, 0.3), (0.25, 0.95, 0.4), SOFA, bevel=0.1, ol=0)]
for k, x in enumerate((-0.8, 0.8)):
    sofa.append(T.box(f"Bank_kussen_{k}", (x, 0.1, 0.48), (1.4, 0.75, 0.15), SOFA, bevel=0.07, ol=0))
b = T.merge("Bank", sofa, ol=0.012)
b.location = (0.6, 4.6, 0.35)
I.chair("Presentatorstoel", (-2.6, 3.6, 0.35), rot=-60, color=(0.95, 0.95, 0.95))
T.cyl("Salontafel", (0.4, 3.2, 0.35), 0.6, 0.42, T.toon("salontafel", (0.95, 0.95, 0.95)), seg=32, ol=0.008)
for k, (dx, dy, c) in enumerate([(-0.2, 0.1, (0.95, 0.55, 0.15)), (0.15, -0.15, (0.95, 0.95, 0.95)), (0.3, 0.2, (0.95, 0.55, 0.15))]):
    T.cyl(f"Mok_{k + 1}", (0.4 + dx, 3.2 + dy, 0.77), 0.045, 0.1, T.toon(f"studiomok{k}", c), seg=14, ol=0.004)
T.cyl("Bloemenvaas", (0.75, 3.1, 0.77), 0.06, 0.2, T.glass("vaas", (0.8, 0.9, 1.0), alpha=0.5), seg=14, ol=0.004)
P.points_mesh("Bloemen", [(0.75 + rnd.uniform(-0.1, 0.1), 3.1 + rnd.uniform(-0.1, 0.1), 1.05 + rnd.uniform(0, 0.12)) for _ in range(9)], 0.04, T.toon("bloem_geel", (0.98, 0.85, 0.2)))

# camera's op statieven, studiolampen, publiek in het donker
T.use_collection(T.collection("Studio-apparatuur"))


def tv_camera(name, loc, target):
    p = [T.box(name + "_body", (0, 0, 1.4), (0.35, 0.7, 0.4), T.toon("tvcam", (0.2, 0.2, 0.22)), bevel=0.04, ol=0),
         T.cyl(name + "_lens", (0, -0.35, 1.6), 0.13, 0.3, P.m("zwart"), rot=(90, 0, 0), seg=16, ol=0),
         T.box(name + "_zoeker", (0.0, 0.4, 1.68), (0.3, 0.25, 0.2), P.m("zwart"), bevel=0.03, ol=0),
         T.box(name + "_tally", (0, -0.1, 1.82), (0.08, 0.08, 0.04), T.glow("tally_rood", (1.0, 0.1, 0.1), 6), bevel=0.01, ol=0),
         T.cyl(name + "_kolom", (0, 0, 0.25), 0.06, 1.0, P.m("metaal"), seg=10, ol=0)]
    for k in range(3):
        a = 2 * math.pi * k / 3
        p.append(T.to_mesh(T.tube(f"{name}_poot{k}", [(0, 0, 0.35), (0.6 * math.cos(a), 0.6 * math.sin(a), 0.03)], 0.03, P.m("metaal"))))
    o = T.merge(name, p, ol=0.01)
    o.location = loc
    d = (target[0] - loc[0], target[1] - loc[1])
    o.rotation_euler.z = math.atan2(d[1], d[0]) + math.pi / 2
    return o


for k, (x, y) in enumerate([(-4.5, -2.5), (0.3, -4.0), (4.8, -2.2)]):
    tv_camera(f"Tvcamera_{k + 1}", (x, y, 0), (0.5, 4.2))


def studio_lamp(name, loc, target, on=True):
    p = [T.cyl(name + "_huis", (0, 0, 0), 0.25, 0.45, P.m("zwart"), seg=16, ol=0),
         T.cyl(name + "_klep", (0, 0, 0.45), 0.25, 0.02, T.glow("studiolamp", (1.0, 0.92, 0.75), 5) if on else P.m("wit"), seg=16, ol=0)]
    o = T.merge(name, p, ol=0.008)
    o.location = loc
    d = (target[0] - loc[0], target[1] - loc[1], target[2] - loc[2])
    from mathutils import Vector
    o.rotation_euler = Vector(d).to_track_quat("Z", "Y").to_euler()
    return o


rig = [T.box("Lichtbrug_1", (0, 0.5, H - 0.6), (16, 0.15, 0.15), P.m("metaal"), bevel=0, ol=0),
       T.box("Lichtbrug_2", (0, -2.5, H - 0.6), (16, 0.15, 0.15), P.m("metaal"), bevel=0, ol=0)]
T.merge("Lichtbruggen", rig, ol=0.008)
for k, x in enumerate(range(-6, 7, 3)):
    for y in (0.5, -2.5):
        studio_lamp(f"Studiolamp_{x}_{y}", (x, y, H - 0.95), (x * 0.2, 4.0, 1.0))
T.spot_light("Key_light", (-4, -3, 5.5), (0.5, 4.2, 1.0), color=(1.0, 0.92, 0.75), energy=6000, angle=45, blend=0.5)
T.spot_light("Fill_light", (5, -2, 4.5), (0.5, 4.2, 1.0), color=(1.0, 0.85, 0.65), energy=3000, angle=50, blend=0.6)
T.spot_light("Decor_light", (0, 0, 6.5), (0, 7.0, 2.0), color=(1.0, 0.75, 0.40), energy=4000, angle=60, blend=0.6)
# publiek op tribune (simpele silhouetten in het donker)
T.use_collection(T.collection("Publiek (silhouetten)"))
SEAT = T.toon("tribune", (0.12, 0.12, 0.15))
heads = []
for r in range(4):
    y = -6.0 - r * 0.9
    T.box(f"Tribune_trede_{r}", (0, y, 0), (14, 0.9, 0.3 + r * 0.35), SEAT, bevel=0.02, ol=0.006)
    for k in range(18):
        x = -6.8 + k * 0.8 + (r % 2) * 0.4
        heads.append((x, y, 0.3 + r * 0.35 + 0.95))
P.points_mesh("Publiek_hoofden", heads, 0.13, T.toon("silhouet", (0.18, 0.16, 0.22)))
P.points_mesh("Publiek_lijven", [(h[0], h[1], h[2] - 0.45) for h in heads], 0.22, T.toon("silhouet", (0.18, 0.16, 0.22)))

T.use_collection(None)
T.character((0.0, 4.3, 0.35), rot_z=180)
cams = [
    T.camera("CAM_01_studio_wide", (0, -9.5, 3.5), (0, 4, 1.4), lens=22),
    T.camera("CAM_02_bank_medium", (0.4, -0.6, 1.4), (0.5, 4.4, 1.1), lens=35),
    T.camera("CAM_03_vanuit_decor", (2.5, 6.5, 2.6), (-1, -5, 1.0), lens=22),
]
blend, renders = T.finish(OUT, "tvstudio", cams)
print("KLAAR", blend, renders)
