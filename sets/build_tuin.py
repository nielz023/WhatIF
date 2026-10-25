"""Set: Achtertuin en dak van het huis. Video 1, dag 4 (zonsondergang, oranje en paars).

Gebruik:
    blender -b -P sets/build_tuin.py -- [zonsondergang] [uitvoermap]
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402,F401
from lib import toon as T  # noqa: E402
from lib import props as P  # noqa: E402
from lib import street as S  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
MOOD = args[0] if args else "zonsondergang"
OUT = args[1] if len(args) > 1 else "/mnt/project-files/sets/07_achtertuin_dak"

mood = dict(T.MOODS[MOOD])
mood.update(sun_rot=(66, 0, 150), fog_start=40, fog_end=350, fog_max=0.5)
if mood.get("sun_disc"):
    mood["sun_disc"] = dict(mood["sun_disc"], dir=(150, 7))
T.new_scene("Achtertuin_" + MOOD, mood, samples=32)
rnd = random.Random(5)

# Huizen: achtergevels kijken naar de tuin (+y). Tuin van het huis: x -3..3, y 0..14
T.use_collection(T.collection("Huizen"))
BRICKS = [(0.72, 0.38, 0.26), (0.80, 0.55, 0.38), (0.62, 0.30, 0.22), (0.85, 0.75, 0.60)]
for k, x in enumerate(range(-24, 25, 6)):
    hero = x == 0
    S.terraced_house("Huis_hoofdpersonage_achter" if hero else f"Huis_achter_{x}", x, 0.0,
                     color=(0.95, 0.88, 0.72) if hero else BRICKS[k % 4], door_color=(0.95, 0.95, 0.93),
                     facing=1, lit=rnd.random() < 0.5)
# huizen aan de overkant van de tuinen (achterkanten)
for k, x in enumerate(range(-27, 28, 6)):
    S.terraced_house(f"Huis_overkant_{x}", x, 30.0, color=BRICKS[(k + 2) % 4], facing=-1, lit=rnd.random() < 0.4)

T.use_collection(T.collection("Tuin"))
P.ground("Gras_grond", (400, 400), (0.24, 0.50, 0.18), z=-0.02)
T.plane("Gazon", (0, 8, 0.0), (6, 14), T.toon("gazon", (0.30, 0.60, 0.22)))
T.plane("Terras", (0, 1.6, 0.01), (6, 3.2), T.pattern("terrastegels", (0.70, 0.66, 0.60), (0.66, 0.62, 0.56), grout=(0.5, 0.48, 0.45), size=(0.6, 0.6), mortar=0.015))
FENCE = T.toon("schutting_hout", (0.58, 0.36, 0.20))
for xs in (-3.0, 3.0):
    planks = [T.box(f"Schutting_{xs}_{k}", (xs, 0.3 + k * 0.19, 0), (0.05, 0.17, 1.9), FENCE, bevel=0.01, ol=0) for k in range(73)]
    T.merge(f"Schutting_{'links' if xs < 0 else 'rechts'}", planks, ol=0.008)
T.merge("Schutting_achter", [T.box(f"Schutting_a_{k}", (-3 + 0.095 + k * 0.19, 14.0, 0), (0.17, 0.05, 1.9), FENCE, bevel=0.01, ol=0) for k in range(32)], ol=0.008)
# buurtuinen als achtergrondvulling
for k, x in enumerate((-12, -6, 6, 12)):
    T.plane(f"Buurgazon_{x}", (x, 8, 0.0), (5.9, 14), T.toon("gazon_buren", (0.27, 0.54, 0.20)))
    P.tree(f"Buurboom_{x}", (x + rnd.uniform(-1.5, 1.5), 11 + rnd.uniform(-1, 2), 0), h=6.5, r=2.2, seed=k + 3)

# Trampoline
tp = [T.cyl("Trampoline_doek", (0, 0, 0.75), 1.7, 0.04, T.toon("trampoline_doek", (0.12, 0.12, 0.16)), seg=40, ol=0),
      T.torus("Trampoline_rand", (0, 0, 0.8), 1.8, 0.1, T.toon("trampoline_blauw", (0.15, 0.45, 0.95)), seg=48, seg2=8, ol=0)]
for k in range(6):
    a = 2 * math.pi * k / 6
    tp.append(T.to_mesh(T.tube(f"Trampoline_poot{k}", [(1.8 * math.cos(a), 1.8 * math.sin(a), 0.8), (1.9 * math.cos(a), 1.9 * math.sin(a), 0.0)], 0.03, P.m("metaal"))))
    tp.append(T.to_mesh(T.tube(f"Trampoline_netpaal{k}", [(1.8 * math.cos(a), 1.8 * math.sin(a), 0.8), (1.8 * math.cos(a), 1.8 * math.sin(a), 2.6)], 0.025, P.m("metaal"))))
tp.append(T.cyl("Trampoline_net", (0, 0, 0.85), 1.79, 1.7, T.glass("net", (0.15, 0.15, 0.18), alpha=0.25), seg=40, ol=0, cap=False))
T.merge("Trampoline", tp, ol=0.012).location = (1.2, 10.2, 0)
# Barbecue (kogelbarbecue)
bbq = [T.sphere("BBQ_ketel", (0, 0, 0.8), 0.32, P.m("zwart"), scale=(1, 1, 0.75), seg=20, ol=0),
       T.cyl("BBQ_rooster", (0, 0, 0.8), 0.31, 0.02, P.m("metaal"), seg=20, ol=0),
       T.sphere("BBQ_deksel", (0.0, 0.32, 0.95), 0.32, P.m("zwart"), scale=(1, 1, 0.6), rot=(-70, 0, 0), seg=20, ol=0)]
for k in range(3):
    a = 2 * math.pi * k / 3
    bbq.append(T.to_mesh(T.tube(f"BBQ_poot{k}", [(0.15 * math.cos(a), 0.15 * math.sin(a), 0.6), (0.35 * math.cos(a), 0.35 * math.sin(a), 0)], 0.018, P.m("metaal"))))
T.merge("Barbecue", bbq, ol=0.01).location = (-2.2, 3.6, 0)
# Tuinset met parasol
TS = T.toon("tuinset_hout", (0.75, 0.55, 0.32))
ts = [T.cyl("Tuintafel_blad", (0, 0, 0.72), 0.55, 0.04, TS, seg=24, ol=0), T.cyl("Tuintafel_poot", (0, 0, 0), 0.05, 0.72, TS, seg=10, ol=0),
      T.cyl("Parasol_stok", (0, 0, 0.7), 0.025, 1.7, P.m("wit"), seg=8, ol=0),
      T.cyl("Parasol_doek", (0, 0, 2.05), 1.4, 0.4, T.toon("parasol", (0.95, 0.35, 0.20)), r2=0.05, seg=8, ol=0)]
T.merge("Tuinset_tafel_parasol", ts, ol=0.01).location = (-1.4, 1.6, 0)
from lib import interior as I  # noqa: E402
for k, (dx, dy, r) in enumerate([(-0.8, 0, -90), (0.8, 0, 90), (0, 0.8, 180)]):
    I.chair(f"Tuinstoel_{k + 1}", (-1.4 + dx, 1.6 + dy, 0), rot=r, color=(0.75, 0.55, 0.32))
# Struiken
for k in range(7):
    T.sphere(f"Struik_{k}", (rnd.choice((-2.5, 2.5)) + rnd.uniform(-0.2, 0.2), rnd.uniform(4, 13), 0.4), rnd.uniform(0.5, 0.8), P.m("boomblad" if k % 2 else "boomblad2"), scale=(1, 1, 0.8), seg=14, ol=0.012)
# Schuurtje achterin
shed = [T.box("Schuur_romp", (0, 0, 0), (2.4, 2.0, 2.1), T.toon("schuur", (0.35, 0.50, 0.38)), bevel=0.03, ol=0),
        T.box("Schuur_deur", (0, -1.01, 0.05), (0.9, 0.04, 1.85), T.toon("schuurdeur", (0.85, 0.82, 0.70)), bevel=0.01, ol=0)]
roof = T.mesh_from("Schuur_dak", [(-1.4, -1.2, 2.1), (1.4, -1.2, 2.1), (1.4, 1.2, 2.1), (-1.4, 1.2, 2.1), (-1.4, 0, 2.8), (1.4, 0, 2.8)],
                   [(0, 1, 5, 4), (4, 5, 2, 3), (0, 4, 3), (1, 2, 5)], T.toon("schuur_dak", (0.20, 0.20, 0.22)))
shed.append(roof)
T.merge("Schuurtje", shed, ol=0.015).location = (-1.5, 12.4, 0)

# Dak: satellietschotel op het dak van het huis (schoorsteen zit al aan het huis)
T.use_collection(T.collection("Dak"))
dish = [T.sphere("Schotel", (0, 0, 0), 0.45, T.toon("schotel", (0.92, 0.92, 0.94)), scale=(1, 0.35, 1), seg=20, ol=0),
        T.cyl("Schotel_arm", (0, -0.2, 0), 0.02, 0.6, P.m("metaal"), rot=(-90, 0, 0), seg=8, ol=0),
        T.sphere("Schotel_lnb", (0, -0.8, 0), 0.06, P.m("zwart"), seg=8, ol=0),
        T.cyl("Schotel_paal", (0, 0.1, -0.9), 0.04, 0.9, P.m("metaal"), seg=8, ol=0)]
d = T.merge("Satellietschotel", dish, ol=0.01)
d.location = (1.6, -2.6, 8.9)
d.rotation_euler = (math.radians(-25), 0, math.radians(200))

T.use_collection(None)
T.character((0.4, -4.5, 9.15), rot_z=180)  # staat op de nok van het dak
T.character((0.6, 6.0, 0.0), rot_z=200, coll_name="Hoofdpersonage (tuin)")
cams = [
    T.camera("CAM_01_tuin_wide", (-2.2, 13.2, 2.0), (0.5, 1.0, 2.6), lens=20),
    T.camera("CAM_02_dak", (-3.5, 3.5, 9.6), (0.4, -4.5, 9.9), lens=26),
    T.camera("CAM_03_vanaf_dak", (0.4, -3.6, 10.8), (0.5, 14, 1.0), lens=24),
]
blend, renders = T.finish(OUT, "achtertuin_dak_" + MOOD, cams)
print("KLAAR", blend, renders)
