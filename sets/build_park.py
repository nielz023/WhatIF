"""Set (video 3, No Rules): het stadspark met klimrek, ijskraam en het bordje KEEP OFF THE GRASS.

Varianten (de plant-en-oogst-props blijven op dezelfde plek staan):
    ochtend   scène 3a-3b: normale ochtend, kinderen op het klimrek, bordje rechtop.
    dag2      scène 7k en 8g: ijskraam met rij, bordje plat in het gras, kampvuur, mensen op het gras.
    dag3      scène 9f-9g: de pestkop zet dranghekken om het park (OUR PARK), fietspad ervoor.
    jaar1     scène 18a-18e: het park vol moestuinbakken, bordje weer rechtop met krijt:
              ...EXCEPT TO GROW FOOD.

Gebruik:
    python3 sets/build_park.py <variant> [uitvoermap]
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402,F401
from lib import toon as T  # noqa: E402
from lib import props as P  # noqa: E402
from lib import stad as S  # noqa: E402
from lib import huis as HU  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
VAR = args[0] if args else "ochtend"
OUT = args[1] if len(args) > 1 else "/mnt/project-files/videos/geen-regels/sets/02_park"

mood = dict(T.MOODS["ochtend" if VAR == "ochtend" else "dag"])
if VAR == "dag2":
    mood.update(sun_rot=(48, 0, 60))
if VAR == "dag3":
    mood.update(sun_strength=0.85, sky_horizon=(0.75, 0.82, 0.95))
T.new_scene("Park_" + VAR, mood, samples=32)
rnd = random.Random(3)

# ---------------------------------------------------------------------------
# Ondergrond: gras, kronkelend grindpad, vijver, randbebouwing
# ---------------------------------------------------------------------------
T.use_collection(T.collection("Park"))
P.ground("Gras", (400, 400), (0.30, 0.56, 0.20), z=-0.02)
pad = T.toon("grindpad_aarde", (0.78, 0.68, 0.52))
pts = [(-60, -8), (-30, -6), (-12, -2), (0, -1), (12, -3), (30, -8), (60, -10)]
for i in range(len(pts) - 1):
    (x1, y1), (x2, y2) = pts[i], pts[i + 1]
    L = math.hypot(x2 - x1, y2 - y1)
    a = math.degrees(math.atan2(y2 - y1, x2 - x1))
    T.box(f"Pad_{i}", ((x1 + x2) / 2, (y1 + y2) / 2, -0.015 + 0.003 * (i % 2)), (L + 1.2, 3.0, 0.03), pad, rot=(0, 0, a), bevel=0, ol=0)
T.cyl("Vijver", (24, 14, 0.0), 7.0, 0.025, T.toon("water_vijver", (0.20, 0.45, 0.65)), seg=48, ol=0)
T.cyl("Vijverrand", (24, 14, -0.02), 7.4, 0.035, T.toon("vijverrand_steen", (0.62, 0.60, 0.56)), seg=48, ol=0)
for i in range(18):  # bomen rond het park
    a = i / 18 * math.tau
    r = rnd.uniform(34, 42)
    P.tree(f"Boom_{i}", (math.cos(a) * r, math.sin(a) * r * 0.8 + 6, 0), h=rnd.uniform(6.5, 9), r=rnd.uniform(2.4, 3.4),
           seed=i, kind="rond")
for i, (x, y) in enumerate([(-16, 10), (8, 18), (-26, -16), (14, -18)]):
    P.tree(f"Parkboom_{i}", (x, y, 0), h=7.5, r=3.0, seed=40 + i)
for i in range(10):
    P.hedge(f"Haag_{i}", (-45 + i * 10, 34, 0), (9.0, 1.2, 1.3))
for i in range(6):
    S.building(f"Randflat_{i}", (-50 + i * 20, 46, 0), w=16, d=10, floors=rnd.randint(4, 7),
               color=[(0.72, 0.60, 0.50), (0.55, 0.58, 0.64), (0.80, 0.72, 0.60)][i % 3], lit=0.0, seed=i)
for i, x in enumerate((-20, -6, 8, 22)):
    P.lamp_post(f"Parklamp_{i}", (x, -4.5 + (i % 2) * 5, 0))
for i, x in enumerate((-9, 5, 18)):
    P.bench(f"Parkbank_{i}", (x, 1.4 if i % 2 else -5.0, 0), rot=180 if i % 2 else 0)
P.bin_("Prullenbak_park", (-3, 1.5, 0))

# ---------------------------------------------------------------------------
# Speeltuin, ijskraam en het bordje
# ---------------------------------------------------------------------------
T.use_collection(T.collection("Speeltuin"))
T.box("Speeltuin_zand", (-6, 7, -0.01), (12, 8, 0.03), T.toon("speelzand", (0.90, 0.80, 0.58)), bevel=0, ol=0)
S.klimrek("Klimrek", (-7, 7, 0), rot_z=10)
S.sign("Bord_NO_DOGS", ["NO DOGS"], (-0.6, 3.2, 0), rot_z=10, w=0.7, h=0.32, bg=(0.95, 0.95, 0.95), fg=(0.85, 0.1, 0.1), post_h=1.1)

T.use_collection(T.collection("Plant en oogst"))
KOGT = (2.8, -4.2, 0)   # plek van het bordje KEEP OFF THE GRASS (vooraan in beeld in 3a)
kogt = S.sign("Bord_KEEP_OFF_THE_GRASS", ["KEEP OFF", "THE GRASS"], KOGT, rot_z=15, w=0.8, h=0.45, knocked=(VAR == "dag2"))
if VAR == "jaar1":
    # krijt onder het bordje, op een plankje aan dezelfde paal
    kb = T.box("Krijt_plankje", (0, 0, 0), (0.86, 0.03, 0.17), T.toon("bordplaat_krijt", (0.16, 0.18, 0.17)), bevel=0.01, ol=0)
    kt = HU.marker_text("Krijt_EXCEPT", "...EXCEPT TO GROW FOOD", (0, 0, 0), 0.06, "wit")
    for o, lz, ly in ((kb, 0.66, -0.005), (kt, 0.72, -0.024)):
        o.parent = kogt
        o.location = (0, ly, lz)

T.use_collection(T.collection("Ijskraam"))
S.ijskraam("Ijskraam", (12, 3.5, 0), rot_z=-30)

# ---------------------------------------------------------------------------
# Variantspullen
# ---------------------------------------------------------------------------
T.use_collection(T.collection("Variant " + VAR))
if VAR == "dag2":
    S.kampvuur("Kampvuur", (5.5, -9.5, 0), lit=True)
    for i, (x, y, c) in enumerate([(3.5, -11.0, (0.85, 0.3, 0.2)), (7.8, -11.4, (0.2, 0.5, 0.9)), (8.2, -8.0, (0.95, 0.8, 0.2))]):
        S.handdoek(f"Kleed_{i}", (x, y, 0.005), rot_z=rnd.uniform(-30, 30), color=c)
    for i in range(6):
        T.cyl(f"Blikje_{i}", (rnd.uniform(2, 9), rnd.uniform(-12, -7), 0), 0.033, 0.12,
              T.toon("blikje_rood", (0.85, 0.12, 0.1)), seg=12, ol=0)
    S.winkelkar("Winkelkar_park", (-2.5, -10.5, 0), rot=30)
elif VAR == "dag3":
    # dranghekken om het park met een groot karton OUR PARK
    for i in range(14):
        S.dranghek(f"Dranghek_{i}", (-18 + i * 2.5, -13.5, 0), rot_z=0, l=2.4)
    for i in range(6):
        S.dranghek(f"Dranghek_zij_{i}", (-19.3, -12.3 + i * 2.5, 0), rot_z=90, l=2.4)
    S.sign("Bord_OUR_PARK", ["OUR PARK", "KEEP OUT"], (-4, -13.7, 0), rot_z=0, w=1.6, h=0.9, bg=(0.78, 0.62, 0.40),
           fg=(0.12, 0.10, 0.10), post_h=0.25, marker=False)
    T.plane("Fietspad", (0, -17, 0.002), (120, 2.5), T.toon("fietspad", (0.62, 0.25, 0.20)))
    S.fiets2("Fiets_held", (2, -16.6, 0), rot=170, color=(0.15, 0.35, 0.75))
    S.fiets2("Fiets_vriend", (4.2, -17.3, 0), rot=175, color=(0.85, 0.12, 0.10), sticker=True)
elif VAR == "jaar1":
    crops = ["sla", "wortel", "tomaat", "kool", "sla", "tomaat", "wortel", "kool"]
    k = 0
    for gx in range(4):
        for gy in range(3):
            x, y = -18 + gx * 4.0, -15 + gy * 2.6
            if gx == 3 and gy == 2:
                continue
            S.moestuinbak(f"Moestuinbak_{k}", (x, y, 0), size=(3.0, 1.6), crop=crops[k % len(crops)], seed=k)
            k += 1
    for i in range(6):
        S.moestuinbak(f"Moestuinbak_vijver_{i}", (12 + (i % 3) * 3.6, -14 + (i // 3) * 2.4, 0), size=(3.0, 1.4),
                      crop=crops[(i + 3) % len(crops)], seed=20 + i)
    S.zonnepaneel("Zonnepaneel_ijskraam", (14.5, 3.0, 0), rot_z=10)
    T.cyl("Regenton", (10.0, -10.0, 0), 0.4, 1.0, T.toon("regenton_groen", (0.15, 0.40, 0.22)), seg=20, ol=0)
    S.sign("Bord_RUILPOST", ["SWAP POINT"], (9.0, -6.5, 0), rot_z=10, w=1.2, h=0.4, bg=(0.92, 0.85, 0.65), fg=(0.15, 0.12, 0.1))

T.use_collection(None)
T.character((0.5, -2.5, 0), rot_z=180)
if VAR == "ochtend":
    cams = [T.camera("CAM_01_crane_bordje", (4.5, -10.5, 3.6), (-3, 5, 1.2), lens=22),
            T.camera("CAM_02_track_pad", (-8, -11, 1.4), (-4, -3, 1.2), lens=30),
            T.camera("CAM_03_bordje_detail", (3.5, -6.0, 0.95), KOGT[:2] + (1.0,), lens=50)]
elif VAR == "dag2":
    cams = [T.camera("CAM_01_bordje_plat_kampvuur", (1.5, -16, 1.6), (4.5, -8, 0.4), lens=24),
            T.camera("CAM_02_ijskraam_rij", (6.0, -4.5, 1.6), (12, 3.5, 1.3), lens=28),
            T.camera("CAM_03_bordje_detail", (3.8, -5.8, 0.6), (KOGT[0], KOGT[1], 0.05), lens=40)]
elif VAR == "dag3":
    cams = [T.camera("CAM_01_dranghekken", (6, -22, 2.4), (-6, -12, 0.8), lens=24),
            T.camera("CAM_02_fietsers_hek", (-2, -20, 1.3), (3, -15, 1.0), lens=30)]
else:
    cams = [T.camera("CAM_01_crane_moestuinen", (2, -24, 7.5), (-6, -10, 0), lens=24),
            T.camera("CAM_02_klimrek", (-1, -2, 1.5), (-7, 7, 1.5), lens=26),
            T.camera("CAM_03_bordje_krijt", (3.6, -5.8, 0.85), (KOGT[0], KOGT[1], 0.7), lens=50)]
blend, renders = T.finish(OUT, "park_" + VAR, cams)
print("KLAAR", blend, renders)
