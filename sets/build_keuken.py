"""Set: Keuken / eettafel. Video 1, dag 1 en 2 (ochtend) en dag 10 (zondagsdiner met opa en oma, avond).

Gebruik:
    blender -b -P sets/build_keuken.py -- [ochtend|zondagsdiner] [uitvoermap]
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
MOOD = args[0] if args else "ochtend"
OUT = args[1] if len(args) > 1 else "/mnt/project-files/sets/04_keuken"
DINNER = MOOD == "zondagsdiner"

if DINNER:
    mood = dict(T.MOODS["zonsondergang"])
    mood.update(sun_rot=(78, 0, 200), sun_strength=0.7, ambient=(0.22, 0.18, 0.22), fog_max=0.0, bloom=0.5)
else:
    mood = dict(T.MOODS["ochtend"])
    mood.update(sun_rot=(48, 0, 150), sun_strength=1.4, ambient=(0.34, 0.30, 0.30), fog_max=0.0)
T.new_scene("Keuken_" + MOOD, mood, samples=48)

W, D, H = 4.8, 4.2, 2.6
WIN = (1.5, 2.9, 1.05, 2.05)  # achterwand, boven het aanrecht
T.use_collection(T.collection("Kamer"))
room = I.room("Keuken", W, D, H, wall_color=(0.98, 0.88, 0.58), floor_color=(0.6, 0.4, 0.22),
              holes={"back": [WIN], "left": [(2.6, 3.5, 0, 2.1)]})
room["floor"].data.materials[0] = T.pattern("keukenvloer", (0.66, 0.44, 0.24), (0.60, 0.39, 0.20), grout=(0.45, 0.28, 0.14), size=(1.2, 0.18), mortar=0.006, offset=0.5)
I.window("Keukenraam", W, D, "back", *WIN, curtains=None)
I.door("Keukendeur", W, D, "left", 3.05, color=(0.85, 0.85, 0.82))
lamp = I.ceiling_lamp("Hanglamp_tafel", (0.2, -0.6, H), on=DINNER)
if DINNER:
    T.point_light("Hanglamp_licht", (0.2, -0.6, H - 0.8), color=(1.0, 0.78, 0.5), energy=120, radius=0.15)

# ---------------------------------------------------------------------------
# Aanrecht langs de achterwand, bovenkastjes, koelkast
# ---------------------------------------------------------------------------
T.use_collection(T.collection("Aanrecht en koelkast"))
CAB = T.toon("keukenkast", (0.32, 0.58, 0.55))
CAB_D = T.toon("keukenkast_deur", (0.38, 0.66, 0.62))
TOP = T.toon("werkblad", (0.92, 0.90, 0.85))
X0, X1 = -W / 2, W / 2 - 0.85  # ruimte voor de koelkast rechts
YB = D / 2 - 0.31
parts = [T.box("Aanrecht_kast", ((X0 + X1) / 2, YB, 0.1), (X1 - X0, 0.6, 0.78), CAB, bevel=0.01, ol=0),
         T.box("Aanrecht_plint", ((X0 + X1) / 2, YB + 0.03, 0), (X1 - X0, 0.54, 0.1), T.toon("plint_donker", (0.2, 0.22, 0.25)), bevel=0, ol=0),
         T.box("Werkblad", ((X0 + X1) / 2, YB - 0.02, 0.88), (X1 - X0 + 0.02, 0.66, 0.04), TOP, bevel=0.008, ol=0)]
n = int((X1 - X0) / 0.6)
for k in range(n):
    x = X0 + 0.3 + k * ((X1 - X0) / n)
    parts.append(T.box(f"Kastdeur_{k}", (x, YB - 0.305, 0.14), ((X1 - X0) / n - 0.03, 0.01, 0.7), CAB_D, bevel=0.005, ol=0))
    parts.append(T.box(f"Kastgreep_{k}", (x, YB - 0.32, 0.72), (0.14, 0.02, 0.02), P.m("metaal"), bevel=0, ol=0))
T.merge("Aanrecht", parts, ol=0.008)
# spoelbak onder het raam
T.box("Spoelbak", (2.2 - W / 2, YB - 0.02, 0.86), (0.6, 0.42, 0.05), T.toon("rvs", (0.70, 0.72, 0.75)), bevel=0.01, ol=0.004)
T.cyl("Keukenkraan", (2.2 - W / 2, YB + 0.22, 0.9), 0.02, 0.32, P.m("metaal"), seg=10, ol=0.004)
T.cyl("Keukenkraan_boog", (2.2 - W / 2, YB + 0.22, 1.2), 0.018, 0.18, P.m("metaal"), rot=(90, 0, 0), seg=10, ol=0.004)
# broodrooster en waterkoker
toaster = [T.box("Broodrooster_body", (0, 0, 0), (0.28, 0.17, 0.19), T.toon("broodrooster", (0.85, 0.15, 0.12)), bevel=0.04, ol=0),
           T.box("Broodrooster_sleuf1", (0, -0.035, 0.18), (0.2, 0.025, 0.02), P.m("zwart"), bevel=0, ol=0),
           T.box("Broodrooster_sleuf2", (0, 0.035, 0.18), (0.2, 0.025, 0.02), P.m("zwart"), bevel=0, ol=0),
           T.box("Broodrooster_hendel", (0.15, 0, 0.12), (0.03, 0.04, 0.025), P.m("zwart"), bevel=0, ol=0)]
tst = T.merge("Broodrooster", toaster, ol=0.006)
tst.location = (-1.55, YB, 0.9)
kettle = [T.cyl("Waterkoker_body", (0, 0, 0.02), 0.09, 0.22, T.toon("waterkoker", (0.92, 0.92, 0.94)), r2=0.07, seg=20, ol=0),
          T.cyl("Waterkoker_voet", (0, 0, 0), 0.1, 0.025, P.m("zwart"), seg=20, ol=0),
          T.box("Waterkoker_handvat", (0.1, 0, 0.06), (0.03, 0.04, 0.18), P.m("zwart"), bevel=0.01, ol=0),
          T.cyl("Waterkoker_tuit", (-0.08, 0, 0.17), 0.025, 0.08, T.toon("waterkoker", (0.92, 0.92, 0.94)), rot=(0, -60, 0), seg=10, ol=0)]
kt = T.merge("Waterkoker", kettle, ol=0.006)
kt.location = (-1.0, YB + 0.05, 0.9)
# mokkenrek met de WORLD'S OKAYEST MOM-mok
T.box("Mokkenrek_plank", (0.95, D / 2 - 0.08, 1.45), (0.7, 0.1, 0.03), T.toon("plank_hout", (0.72, 0.48, 0.26)), bevel=0.005, ol=0.004)
mug_cols = [(0.95, 0.45, 0.15), (0.2, 0.5, 0.9), (0.98, 0.98, 0.98), (0.3, 0.7, 0.35)]
for k in range(4):
    x = 0.68 + k * 0.18
    T.cyl(f"Haakje_{k}", (x, D / 2 - 0.04, 1.42), 0.006, 0.07, P.m("metaal"), rot=(90, 0, 0), seg=6, ol=0)
    mug = [T.cyl(f"Mok_{k}_body", (0, 0, 0), 0.045, 0.1, T.toon(f"mok{k}", mug_cols[k]), seg=18, ol=0),
           T.torus(f"Mok_{k}_oor", (0.05, 0, 0.05), 0.028, 0.008, T.toon(f"mok{k}", mug_cols[k]), rot=(90, 0, 0), seg=16, seg2=6, ol=0)]
    mo = T.merge("Mok_WORLDS_OKAYEST_MOM" if k == 2 else f"Mok_{k + 1}", mug, ol=0.004)
    mo.location = (x, D / 2 - 0.12, 1.25)
    mo.rotation_euler.z = math.radians(-90)
    if k == 2:
        t1 = T.text("Mok_tekst1", "WORLD'S", (x, D / 2 - 0.168, 1.315), 0.016, T.toon("mok_tekst", (0.1, 0.1, 0.12)), extrude=0.001)
        t2 = T.text("Mok_tekst2", "OKAYEST MOM", (x, D / 2 - 0.168, 1.29), 0.012, T.toon("mok_tekst", (0.1, 0.1, 0.12)), extrude=0.001)
# bovenkastjes links
for k in range(2):
    x = X0 + 0.3 + k * 0.62
    T.box(f"Bovenkast_{k}", (x, D / 2 - 0.18, 1.55), (0.6, 0.34, 0.7), CAB, bevel=0.01, ol=0.006)
    T.box(f"Bovenkast_greep_{k}", (x + 0.2, D / 2 - 0.36, 1.6), (0.02, 0.02, 0.14), P.m("metaal"), bevel=0, ol=0)
# koelkast met magneten en kindertekening
FX = W / 2 - 0.42
fr = [T.box("Koelkast_body", (0, 0, 0), (0.75, 0.7, 1.9), T.toon("koelkast", (0.94, 0.94, 0.95)), bevel=0.04, ol=0),
      T.box("Koelkast_naad", (0, -0.351, 1.25), (0.74, 0.01, 0.015), T.toon("naad", (0.6, 0.62, 0.66)), bevel=0, ol=0),
      T.box("Koelkast_greep1", (-0.3, -0.37, 1.35), (0.03, 0.03, 0.35), P.m("metaal"), bevel=0.01, ol=0),
      T.box("Koelkast_greep2", (-0.3, -0.37, 0.8), (0.03, 0.03, 0.35), P.m("metaal"), bevel=0.01, ol=0)]
fridge = T.merge("Koelkast", fr, ol=0.01)
fridge.location = (FX, D / 2 - 0.38, 0)
rnd = random.Random(3)
mag_cols = [(0.9, 0.15, 0.15), (0.15, 0.45, 0.9), (0.98, 0.75, 0.1), (0.2, 0.7, 0.3), (0.9, 0.4, 0.75)]
for k in range(10):
    T.sphere(f"Magneet_{k}", (FX + rnd.uniform(-0.3, 0.3), D / 2 - 0.735, rnd.uniform(0.6, 1.8)), 0.025, T.toon(f"magneet{k % 5}", mag_cols[k % 5]), scale=(1, 0.4, 1), seg=10, ol=0.003)
# kindertekening (van het broertje): huis, zon en drie poppetjes
dr = [T.box("Tekening_papier", (0, 0, 0), (0.26, 0.004, 0.34), P.m("wit"), bevel=0, base=False, ol=0),
      T.sphere("Tekening_zon", (0.08, -0.004, 0.11), 0.035, T.toon("krijt_geel", (0.98, 0.8, 0.1)), scale=(1, 0.1, 1), seg=12, ol=0),
      T.box("Tekening_huis", (-0.04, -0.004, -0.06), (0.12, 0.003, 0.1), T.toon("krijt_rood", (0.9, 0.2, 0.15)), base=False, bevel=0, ol=0),
      T.box("Tekening_gras", (0, -0.004, -0.15), (0.26, 0.003, 0.03), T.toon("krijt_groen", (0.2, 0.7, 0.2)), base=False, bevel=0, ol=0)]
for k in range(3):
    dr.append(T.box(f"Tekening_pop{k}", (0.04 + k * 0.035, -0.004, -0.09), (0.006, 0.003, 0.06), T.toon("krijt_blauw", (0.15, 0.3, 0.9)), base=False, bevel=0, ol=0))
    dr.append(T.sphere(f"Tekening_hoofd{k}", (0.04 + k * 0.035, -0.004, -0.05), 0.012, T.toon("krijt_blauw", (0.15, 0.3, 0.9)), scale=(1, 0.2, 1), seg=8, ol=0))
drawing = T.merge("Kindertekening", dr, ol=0.002)
drawing.location = (FX + 0.05, D / 2 - 0.737, 1.5)
drawing.rotation_euler.y = math.radians(4)

# ---------------------------------------------------------------------------
# Keukentafel met stoelen (4 voor het ontbijt, 6 bij het zondagsdiner)
# ---------------------------------------------------------------------------
T.use_collection(T.collection("Eettafel"))
TX, TY = 0.2, -0.6
TL = 2.2 if DINNER else 1.5
I.table("Keukentafel", (TX, TY, 0), size=(TL, 0.9, 0.76), color=(0.78, 0.55, 0.30))
seats = [(-0.38, -1), (0.38, -1), (-0.38, 1), (0.38, 1)]
if DINNER:
    seats = [(-0.7, -1), (0, -1), (0.7, -1), (-0.7, 1), (0, 1), (0.7, 1)]
for k, (x, s) in enumerate(seats):
    I.chair(f"Stoel_{k + 1}", (TX + x, TY + s * 0.62, 0), rot=0 if s > 0 else 180, color=(0.88, 0.62, 0.30))
if DINNER:
    for k, x in enumerate((-TL / 2 - 0.62, TL / 2 + 0.62)):
        I.chair(f"Stoel_kop_{k + 1}", (TX + x, TY, 0), rot=90 if k else -90, color=(0.88, 0.62, 0.30))
TZ = 0.76


def plate(name, x, y, food=None):
    p = [T.cyl(name + "_bord", (0, 0, 0), 0.13, 0.015, P.m("wit"), seg=24, ol=0)]
    if food == "cornflakes":
        p = [T.cyl(name + "_kom", (0, 0, 0), 0.08, 0.07, T.toon("kom_blauw", (0.3, 0.55, 0.9)), r2=0.1, seg=20, ol=0),
             T.cyl(name + "_vlokken", (0, 0, 0.055), 0.088, 0.012, T.toon("cornflakes", (0.95, 0.70, 0.25)), seg=20, ol=0),
             T.cyl(name + "_lepel", (0.06, 0.02, 0.06), 0.006, 0.16, P.m("metaal"), rot=(0, 60, 20), seg=6, ol=0)]
    elif food == "diner":
        p += [T.sphere(name + "_aardappel1", (0.03, 0.02, 0.02), 0.03, T.toon("aardappel", (0.95, 0.80, 0.40)), seg=10, ol=0),
              T.sphere(name + "_aardappel2", (0.06, -0.03, 0.02), 0.028, T.toon("aardappel", (0.95, 0.80, 0.40)), seg=10, ol=0),
              T.sphere(name + "_boontjes", (-0.05, 0.0, 0.015), 0.05, T.toon("boontjes", (0.25, 0.6, 0.2)), scale=(1, 0.6, 0.3), seg=10, ol=0)]
    o = T.merge(name, p, ol=0.003)
    o.location = (x, y, TZ)
    return o


if not DINNER:
    plate("Ontbijt_broertje", TX + 0.38, TY - 0.25, food="cornflakes")
    plate("Ontbijt_bord", TX - 0.38, TY + 0.25)
    box = T.box("Cornflakes_doos", (TX + 0.55, TY + 0.0, TZ), (0.2, 0.07, 0.3), T.toon("cornflakesdoos", (0.95, 0.35, 0.1)), bevel=0.005, ol=0.004)
    T.box("Cornflakes_label", (TX + 0.55, TY - 0.036, TZ + 0.08), (0.14, 0.002, 0.12), T.toon("label_geel", (0.98, 0.85, 0.2)), bevel=0, ol=0)
    T.box("Melkpak", (TX + 0.25, TY + 0.05, TZ), (0.08, 0.08, 0.22), P.m("wit"), bevel=0.004, ol=0.004)
    T.box("Melkpak_band", (TX + 0.25, TY + 0.05, TZ + 0.08), (0.082, 0.082, 0.05), P.m("lichtblauw"), bevel=0, ol=0)
    # krant van papa
    news = T.box("Krant", (TX - 0.4, TY - 0.2, TZ), (0.45, 0.3, 0.012), T.toon("krantenpapier", (0.90, 0.88, 0.82)), rot=(0, 0, 12), bevel=0, ol=0.003)
    for k in range(5):
        T.box(f"Krant_kolom{k}", (TX - 0.55 + k * 0.08, TY - 0.2, TZ + 0.012), (0.05, 0.22, 0.001), T.toon("krantentekst", (0.55, 0.55, 0.55)), rot=(0, 0, 12), bevel=0, ol=0)
    T.cyl("Koffiemok", (TX - 0.1, TY + 0.25, TZ), 0.045, 0.1, P.m("rood"), seg=16, ol=0.004)
    # fruitschaal
    T.cyl("Fruitschaal", (TX + 0.05, TY + 0.05, TZ), 0.1, 0.06, T.toon("schaal", (0.85, 0.85, 0.9)), r2=0.16, seg=24, ol=0.004)
    for k, (c, dx, dy) in enumerate([((0.85, 0.1, 0.1), -0.05, 0), ((0.95, 0.55, 0.05), 0.05, 0.03), ((0.98, 0.85, 0.15), 0.0, -0.06), ((0.4, 0.75, 0.2), 0.02, 0.07)]):
        T.sphere(f"Fruit_{k}", (TX + 0.05 + dx, TY + 0.05 + dy, TZ + 0.1), 0.045, T.toon(f"fruit{k}", c), seg=12, ol=0.003)
else:
    for k, (x, s) in enumerate(seats):
        plate(f"Bord_{k + 1}", TX + x, TY + s * 0.28, food="diner")
    for k, x in enumerate((-TL / 2 + 0.2, TL / 2 - 0.2)):
        plate(f"Bord_kop_{k + 1}", TX + x, TY, food="diner")
    T.box("Tafelkleed", (TX, TY, TZ - 0.001), (TL + 0.2, 1.05, 0.004), T.toon("tafelkleed", (0.95, 0.94, 0.9)), bevel=0, ol=0.003)
    T.cyl("Ovenschaal", (TX, TY, TZ), 0.22, 0.06, T.toon("ovenschaal", (0.9, 0.9, 0.92)), seg=24, ol=0.004).scale.y = 0.7
    T.sphere("Kip", (TX, TY, TZ + 0.1), 0.12, T.toon("gebraden_kip", (0.80, 0.45, 0.15)), scale=(1.3, 1.0, 0.75), seg=16, ol=0.004)
    T.cyl("Saladeschaal", (TX - 0.55, TY + 0.05, TZ), 0.09, 0.08, T.toon("schaal", (0.85, 0.85, 0.9)), r2=0.14, seg=20, ol=0.004)
    T.sphere("Salade", (TX - 0.55, TY + 0.05, TZ + 0.08), 0.11, T.toon("sla", (0.35, 0.72, 0.22)), scale=(1, 1, 0.4), seg=12, ol=0.003)
    for k, x in enumerate((-0.25, 0.25)):
        T.cyl(f"Kandelaar_{k}", (TX + x, TY + 0.2, TZ), 0.03, 0.05, T.toon("kandelaar", (0.85, 0.7, 0.3)), seg=12, ol=0.003)
        T.cyl(f"Kaars_{k}", (TX + x, TY + 0.2, TZ + 0.05), 0.012, 0.22, P.m("wit"), seg=10, ol=0.002)
        T.sphere(f"Vlammetje_{k}", (TX + x, TY + 0.2, TZ + 0.29), 0.012, T.glow("vlam", (1.0, 0.7, 0.3), 8), scale=(1, 1, 1.8), seg=8, ol=0)
        T.point_light(f"Kaarslicht_{k}", (TX + x, TY + 0.2, TZ + 0.35), color=(1.0, 0.65, 0.35), energy=6, radius=0.02)
    for k, (x, s) in enumerate(seats):
        T.cyl(f"Glas_{k}", (TX + x + 0.15, TY + s * 0.18, TZ), 0.03, 0.11, T.glass("drinkglas", (0.8, 0.9, 1.0), alpha=0.5), seg=14, ol=0.002)

# ---------------------------------------------------------------------------
# Buiten: de achtertuin (zelfde tuin als de tuin-set, dag 4)
# ---------------------------------------------------------------------------
T.use_collection(T.collection("Buiten"))
P.ground("Tuin", (200, 200), (0.24, 0.50, 0.18), z=-0.05)
P.hedge("Schutting", (0, 9, 0), (20, 0.12, 1.8), color="hout")
P.tree("Tuinboom", (-2.5, 7.0, 0), h=6, r=2.0, seed=1)
T.cyl("Trampoline", (2.5, 5.5, 0.5), 1.6, 0.08, T.toon("trampoline", (0.15, 0.15, 0.2)), seg=32, ol=0.02)
T.torus("Trampoline_rand", (2.5, 5.5, 0.58), 1.6, 0.08, T.toon("trampoline_rand", (0.15, 0.45, 0.9)), seg=48, seg2=8, ol=0.01)

T.use_collection(None)
if DINNER:
    T.area_light("Avondlicht_raam", (W / 2 - 2.6, D / 2 - 0.3, 1.6), (0, -1, 0.5), size=(1.3, 0.9), color=(1.0, 0.55, 0.35), energy=30)
else:
    T.area_light("Ochtendlicht_raam", (W / 2 - 2.6, D / 2 - 0.3, 1.6), (0, -1, 0.5), size=(1.3, 0.9), color=(1.0, 0.85, 0.6), energy=60)
    T.area_light("Vullicht", (0, -3.5, 2.2), (0, 0, 1.0), size=(3, 2), color=(0.9, 0.9, 1.0), energy=40)
T.character((1.35, -0.35, 0), rot_z=-30)

cams = [
    T.camera("CAM_01_wide_keuken", (1.6, -4.1, 1.7), (-0.2, 0.6, 1.0), lens=20),
    T.camera("CAM_02_tafel", (TX - 1.6, TY - 1.3, 1.35), (TX, TY, 0.85), lens=28),
    T.camera("CAM_03_aanrecht_mokken", (0.6, 0.4, 1.45), (0.8, D / 2, 1.2), lens=30),
    T.camera("CAM_04_koelkast", (FX - 0.6, 0.2, 1.5), (FX, D / 2 - 0.75, 1.3), lens=30),
]
blend, renders = T.finish(OUT, "keuken_" + MOOD, cams)
print("KLAAR", blend, renders)
