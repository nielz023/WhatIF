"""Set: Badkamer. Video 1, dag 1 (helder wit, koel).

Gebruik:
    blender -b -P sets/build_badkamer.py -- [binnen] [uitvoermap]
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402,F401
from lib import toon as T  # noqa: E402
from lib import props as P  # noqa: E402
from lib import interior as I  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
MOOD = args[0] if args else "binnen"
OUT = args[1] if len(args) > 1 else "/mnt/project-files/sets/03_badkamer"

mood = dict(T.MOODS["binnen"])
mood.update(ambient=(0.42, 0.45, 0.52), shadow_tint=(0.55, 0.60, 0.78), lit_tint=(1.0, 1.0, 1.0), sun_rot=(50, 0, -60), sun_strength=1.2)
T.new_scene("Badkamer", mood, samples=48)

W, D, H = 2.8, 2.5, 2.5
WIN = (0.9, 1.6, 1.3, 2.1)  # linkerwand
T.use_collection(T.collection("Kamer"))
room = I.room("Badkamer", W, D, H, wall_color=(0.93, 0.94, 0.95), floor_color=(0.5, 0.52, 0.56), holes={"left": [WIN]})
TILE = T.pattern("witte_tegels", (0.95, 0.96, 0.97), (0.92, 0.94, 0.96), grout=(0.78, 0.82, 0.88), size=(0.2, 0.2), mortar=0.008)
FLOOR = T.pattern("vloertegels", (0.30, 0.34, 0.42), (0.88, 0.89, 0.92), size=(0.3, 0.3), kind="schaak")
for side in ("back", "left", "right", "front"):
    room[side].data.materials[0] = TILE
room["floor"].data.materials[0] = FLOOR
I.window("Raampje", W, D, "left", *WIN, frame_color=(0.96, 0.96, 0.96))
bpy.data.objects["Raampje_glas"].data.materials[0] = T.glass("matglas", (0.85, 0.92, 0.98), alpha=0.85)
# plantje op de vensterbank
T.cyl("Plant_pot", (-W / 2 + 0.12, -D / 2 + 1.25, 1.29), 0.07, 0.12, T.toon("pot_terra", (0.80, 0.40, 0.25)), r2=0.055, seg=12, ol=0.005)
for k in range(6):
    a = math.radians(k * 60)
    T.sphere(f"Plant_blad{k}", (-W / 2 + 0.12 + 0.05 * math.cos(a), -D / 2 + 1.25 + 0.05 * math.sin(a), 1.47), 0.06, P.m("boomblad2"), scale=(0.5, 0.5, 1.5), rot=(25 * math.cos(a), 25 * math.sin(a), 0), seg=10, ol=0.004)

# ---------------------------------------------------------------------------
# Wastafel met grote spiegel, tandenborstelbeker, zeep, tandpasta
# ---------------------------------------------------------------------------
T.use_collection(T.collection("Wastafel en spiegel"))
SX = -0.55
vanity = [T.box("Meubel_kast", (0, 0, 0.1), (0.9, 0.48, 0.72), T.toon("badmeubel", (0.35, 0.62, 0.72)), bevel=0.02, ol=0),
          T.box("Meubel_blad", (0, 0, 0.82), (0.94, 0.52, 0.05), P.m("wit"), bevel=0.01, ol=0),
          T.box("Meubel_plint", (0, 0.02, 0), (0.86, 0.44, 0.1), T.toon("plint_donker", (0.25, 0.3, 0.35)), bevel=0, ol=0)]
for x in (-0.22, 0.22):
    vanity.append(T.box(f"Meubel_deur{x}", (x, -0.245, 0.14), (0.42, 0.01, 0.64), T.toon("badmeubel_deur", (0.40, 0.68, 0.78)), bevel=0.005, ol=0))
    vanity.append(T.box(f"Meubel_greep{x}", (x + (0.15 if x < 0 else -0.15), -0.26, 0.6), (0.02, 0.02, 0.14), P.m("metaal"), bevel=0, ol=0))
sink = T.cyl("Wasbak", (0, 0, 0.86), 0.24, 0.1, P.m("wit"), seg=32, ol=0)
sink.scale.y = 0.75
vanity.append(sink)
vanity.append(T.cyl("Wasbak_binnen", (0, 0, 0.9), 0.2, 0.07, T.toon("wasbak_binnen", (0.80, 0.84, 0.90)), seg=32, ol=0))
vanity[-1].scale.y = 0.72
vanity.append(T.cyl("Kraan_voet", (0, 0.2, 0.87), 0.025, 0.2, P.m("metaal"), seg=10, ol=0))
vanity.append(T.cyl("Kraan_tuit", (0, 0.2, 1.05), 0.02, 0.14, P.m("metaal"), rot=(90, 0, 0), seg=10, ol=0))
T.group("Wastafelmeubel", [T.merge("Wastafel", vanity, ol=0.006)], loc=(SX, D / 2 - 0.25, 0))

mirror = [T.box("Spiegel_lijst", (0, 0, 0), (0.95, 0.04, 0.85), T.toon("spiegellijst", (0.85, 0.85, 0.87)), bevel=0.02, ol=0),
          T.box("Spiegel_glas", (0, -0.025, 0.04), (0.87, 0.01, 0.77), T.toon("spiegel", (0.70, 0.82, 0.92)), bevel=0, ol=0)]
for k, (x, w) in enumerate([(-0.18, 0.08), (-0.05, 0.03)]):
    mirror.append(T.box(f"Spiegel_glans{k}", (x, -0.032, 0.25), (w, 0.004, 0.55), T.toon("spiegelglans", (0.93, 0.97, 1.0)), rot=(0, 30, 0), bevel=0, ol=0))
mo = T.merge("Grote_spiegel", mirror, ol=0.006)
mo.location = (SX, D / 2 - 0.03, 1.15)
T.box("Spiegellamp", (SX, D / 2 - 0.08, 2.05), (0.7, 0.08, 0.06), T.glow("spiegellamp", (1.0, 0.97, 0.9), 3), bevel=0.02, ol=0.005)

cup = T.cyl("Tandenborstelbeker", (SX + 0.33, D / 2 - 0.13, 0.87), 0.045, 0.11, T.toon("beker_geel", (0.98, 0.78, 0.2)), seg=14, ol=0.005)
for k, (c, a) in enumerate([((0.15, 0.45, 0.95), 10), ((0.95, 0.25, 0.25), -12), ((0.2, 0.75, 0.35), 4)]):
    b = T.merge(f"Tandenborstel_{k + 1}", [
        T.cyl(f"tb{k}_steel", (0, 0, 0), 0.007, 0.19, T.toon(f"tandenborstel{k}", c), seg=6, ol=0),
        T.box(f"tb{k}_kop", (0, 0.008, 0.17), (0.012, 0.012, 0.03), P.m("wit"), bevel=0, ol=0)], ol=0.003)
    b.location = (SX + 0.33, D / 2 - 0.13, 0.88)
    b.rotation_euler = (math.radians(a * 0.6), math.radians(a), 0)
tube = T.merge("Tandpasta", [T.box("tp_tube", (0, 0, 0), (0.17, 0.045, 0.03), T.toon("tandpasta", (0.95, 0.95, 0.98)), bevel=0.012, ol=0),
                              T.box("tp_streep", (0, 0, 0.0), (0.12, 0.047, 0.032), T.toon("tandpasta_blauw", (0.15, 0.4, 0.9)), bevel=0.01, ol=0),
                              T.cyl("tp_dop", (0.09, 0, 0.015), 0.015, 0.03, T.toon("tandpasta_dop", (0.9, 0.2, 0.2)), rot=(0, 90, 0), seg=10, ol=0)], ol=0.003)
tube.location = (SX - 0.3, D / 2 - 0.12, 0.87)
tube.rotation_euler.z = math.radians(15)
T.box("Zeep", (SX + 0.2, D / 2 - 0.35, 0.87), (0.08, 0.05, 0.03), T.toon("zeep", (0.98, 0.6, 0.75)), bevel=0.015, ol=0.004)

# Handdoek aan een haak (naast de wastafel)
T.cyl("Haak", (0.15, D / 2 - 0.03, 1.55), 0.015, 0.06, P.m("metaal"), rot=(90, 0, 0), seg=8, ol=0.003)
T.box("Handdoek", (0.15, D / 2 - 0.07, 0.95), (0.4, 0.06, 0.62), T.toon("handdoek", (0.95, 0.55, 0.20)), bevel=0.025, ol=0.008)
T.box("Handdoek_streep", (0.15, D / 2 - 0.1, 1.05), (0.41, 0.01, 0.06), P.m("wit"), bevel=0, ol=0)

# ---------------------------------------------------------------------------
# Douche met gestreept gordijn, wc, badmat
# ---------------------------------------------------------------------------
T.use_collection(T.collection("Douche en wc"))
SHX0 = W / 2 - 0.95
T.box("Douchebak", (W / 2 - 0.47, D / 2 - 0.47, 0), (0.92, 0.92, 0.08), P.m("wit"), bevel=0.02, ol=0.006)
T.cyl("Douchestang", (W / 2 - 0.05, D / 2 - 0.05, 0.08), 0.015, 2.0, P.m("metaal"), seg=8, ol=0.003)
T.cyl("Douchekop_arm", (W / 2 - 0.05, D / 2 - 0.05, 1.95), 0.012, 0.3, P.m("metaal"), rot=(60, 0, 135), seg=8, ol=0.003)
T.cyl("Douchekop", (W / 2 - 0.22, D / 2 - 0.22, 1.98), 0.08, 0.03, P.m("metaal"), rot=(30, 0, 135), seg=16, ol=0.004)
SHY = D / 2 - 0.95
T.cyl("Gordijnroede", (SHX0, SHY, 2.05), 0.012, 0.95, P.m("metaal"), rot=(0, 90, 0), seg=8, ol=0.003)
stripes = [(0.12, 0.40, 0.85), (0.96, 0.96, 0.98), (0.98, 0.70, 0.10), (0.96, 0.96, 0.98)]
folds = []
for k in range(14):
    x = W / 2 - 0.06 - k * 0.045  # dicht aan de muurkant, open aan de kant van de wastafel
    folds.append(T.cyl(f"Gordijnplooi_{k}", (x, SHY + 0.035 * ((k % 2) * 2 - 1), 0.25), 0.04, 1.78, T.toon(f"douchegordijn{k % 4}", stripes[k % 4]), seg=8, ol=0))
T.merge("Douchegordijn_gestreept", folds, ol=0.006)

toilet = [T.box("WC_reservoir", (0, 0.12, 0.42), (0.42, 0.18, 0.4), P.m("wit"), bevel=0.04, ol=0),
          T.cyl("WC_pot", (0, -0.12, 0), 0.19, 0.4, P.m("wit"), r2=0.2, seg=24, ol=0),
          T.cyl("WC_bril", (0, -0.14, 0.4), 0.21, 0.04, P.m("wit"), seg=24, ol=0),
          T.cyl("WC_knop", (0, 0.12, 0.82), 0.03, 0.015, P.m("metaal"), seg=12, ol=0)]
for o in toilet[1:3]:
    o.scale.y = 1.25
wc = T.merge("WC", toilet, ol=0.01)
wc.location = (W / 2 - 0.25, -0.55, 0)
wc.rotation_euler.z = math.radians(-90)
I.rug("Badmat", (-0.45, 0.35, 0), (0.75, 0.48), (0.40, 0.70, 0.85))
T.cyl("Wasmand", (-W / 2 + 0.3, -0.6, 0), 0.2, 0.5, T.toon("wasmand", (0.85, 0.75, 0.55)), seg=16, ol=0.008)
I.ceiling_lamp("Plafondlamp", (0, 0, H), on=False)

T.use_collection(None)
T.area_light("Raamlicht", (-W / 2 + 0.3, -D / 2 + 1.25, 1.7), (0.5, 0, 0.8), size=(0.7, 0.8), color=(0.85, 0.92, 1.0), energy=60)
T.area_light("Plafondvul", (0, -0.3, H - 0.1), (0, -0.3, 0), size=(1.6, 1.6), color=(1.0, 1.0, 1.0), energy=60)
T.character((-0.75, -0.55, 0), rot_z=200)

cams = [
    T.camera("CAM_01_wide_badkamer", (0.35, -2.75, 1.6), (-0.2, 0.7, 1.0), lens=22),
    T.camera("CAM_02_spiegel", (-0.4, -0.6, 1.5), (SX, D / 2, 1.3), lens=30),
    T.camera("CAM_03_wastafel_close", (SX + 0.05, D / 2 - 0.95, 1.25), (SX + 0.1, D / 2 - 0.15, 0.9), lens=40),
]
blend, renders = T.finish(OUT, "badkamer", cams)
print("KLAAR", blend, renders)
