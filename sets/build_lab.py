"""Set: Het lab. Video 1, dag 15. Klinisch wit met blauwe accenten.
Lange witte gang, hydraulische pers, monitoren met grafieken, glazen wand met wetenschappers (silhouetten).

Gebruik:
    blender -b -P sets/build_lab.py -- [lab] [uitvoermap]
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
OUT = args[1] if len(args) > 1 else "/mnt/project-files/sets/16_lab"
rnd = random.Random(15)

mood = dict(T.MOODS["binnen"])
mood.update(ambient=(0.50, 0.55, 0.62), shadow_tint=(0.62, 0.70, 0.86), lit_tint=(0.98, 1.0, 1.0), sun_strength=0.0, fog_max=0.0, bloom=0.6)
T.new_scene("Lab", mood, samples=48)

WHITE = T.toon("lab_wit", (0.95, 0.96, 0.97))
BLUE = T.toon("lab_blauw", (0.10, 0.45, 0.95))
GREY = T.toon("lab_grijs", (0.55, 0.58, 0.64))

# testhal: x -8..8, y -6..8; gang loopt van de hal naar -y (x -1.5..1.5, y -30..-6)
W, D, H = 16.0, 14.0, 6.0
T.use_collection(T.collection("Testhal"))
room = I.room("Testhal", W, D, H, wall_color=(0.95, 0.96, 0.97), floor_color=(0.88, 0.90, 0.93), skirting=False,
              holes={"front": [(6.5, 9.5, 0, 3.0)], "left": [(4.0, 12.0, 1.0, 3.6)]}, hide=("front",))
room["floor"].data.materials[0] = T.pattern("labvloer", (0.90, 0.92, 0.95), (0.86, 0.88, 0.92), grout=(0.78, 0.80, 0.85), size=(1.0, 1.0), mortar=0.006)
for o in list(room.values()):  # hal 1 m naar achteren schuiven
    o.location.y += 1.0
T.box("Blauwe_band", (0, D / 2 + 1.0 - 0.03, 2.4), (W, 0.04, 0.12), BLUE, bevel=0, ol=0)
# glazen wand (linkerwand) met wetenschappers erachter
T.box("Glazen_wand", (-W / 2, 1.0 - D / 2 + 8.0, 1.0), (0.06, 8.0, 2.6), T.glass("labglas", (0.75, 0.90, 1.0), alpha=0.3), bevel=0, ol=0.01)
T.box("Observatieruimte_vloer", (-W / 2 - 3, 1.0 - D / 2 + 8.0, -0.1), (6, 8.5, 0.1), GREY, bevel=0, ol=0)
T.box("Observatieruimte_muur", (-W / 2 - 6, 1.0 - D / 2 + 8.0, 0), (0.2, 8.5, H), T.toon("obs_muur", (0.82, 0.86, 0.92)), bevel=0, ol=0)
COAT = T.toon("labjas", (0.97, 0.97, 0.98))
for k in range(5):
    y = 1.0 - D / 2 + 5.0 + k * 1.4
    sc = [T.cyl(f"Wetenschapper_{k}_lijf", (0, 0, 0), 0.28, 1.45, COAT, r2=0.22, seg=14, ol=0),
          T.sphere(f"Wetenschapper_{k}_hoofd", (0, 0, 1.68), 0.17, T.toon("huid_npc", (0.88, 0.66, 0.50)), seg=12, ol=0),
          T.box(f"Wetenschapper_{k}_klembord", (0.25, 0, 1.0), (0.04, 0.24, 0.32), T.toon("klembord", (0.55, 0.38, 0.22)), bevel=0.01, ol=0)]
    s_ = T.merge(f"Wetenschapper_silhouet_{k + 1}", sc, ol=0.01)
    s_.location = (-W / 2 - 1.2 - (k % 2) * 0.6, y, 0)
    s_.rotation_euler.z = math.radians(-90)

# hydraulische pers in het midden
T.use_collection(T.collection("Hydraulische pers"))
PR = T.toon("pers_blauw", (0.12, 0.40, 0.85))
pr = [T.box("Pers_voet", (0, 0, 0), (3.2, 2.4, 0.8), GREY, bevel=0.05, ol=0),
      T.box("Pers_tafel", (0, 0, 0.8), (2.4, 1.8, 0.25), T.toon("staal_licht", (0.75, 0.78, 0.82)), bevel=0.03, ol=0),
      T.box("Pers_kop", (0, 0, 4.2), (3.4, 2.4, 1.0), PR, bevel=0.08, ol=0),
      T.cyl("Pers_zuiger", (0, 0, 2.3), 0.45, 1.9, T.toon("chroom", (0.85, 0.88, 0.92)), seg=24, ol=0),
      T.box("Pers_plaat", (0, 0, 2.1), (2.0, 1.5, 0.2), T.toon("staal_licht", (0.75, 0.78, 0.82)), bevel=0.02, ol=0)]
for x in (-1.45, 1.45):
    for y in (-0.95, 0.95):
        pr.append(T.cyl(f"Pers_kolom_{x}_{y}", (x, y, 0.8), 0.16, 3.5, T.toon("chroom", (0.85, 0.88, 0.92)), seg=16, ol=0))
pr.append(T.box("Pers_waarschuwing", (0, -1.21, 4.4), (2.6, 0.02, 0.4), T.toon("waarschuwing_geel", (0.98, 0.80, 0.08)), bevel=0, ol=0))
for k in range(7):
    pr.append(T.box(f"Pers_streep_{k}", (-1.2 + k * 0.4, -1.225, 4.4), (0.12, 0.01, 0.5), P.m("zwart"), rot=(0, 40, 0), bevel=0, ol=0))
T.merge("Hydraulische_pers", pr, ol=0.02).location = (0, 3.5, 0)
T.text("Pers_label", "500 TON", (0, 3.5 - 1.25, 4.55), 0.3, P.m("zwart"), extrude=0.01)
# gele veiligheidslijn op de vloer
for (x, y, w, d) in [(0, 1.3, 5.0, 0.12), (0, 5.7, 5.0, 0.12), (-2.5, 3.5, 0.12, 4.5), (2.5, 3.5, 0.12, 4.5)]:
    T.plane(f"Veiligheidslijn_{x}_{y}", (x, y, 0.005), (w, d), T.toon("waarschuwing_geel", (0.98, 0.80, 0.08)))

# monitoren met grafieken
T.use_collection(T.collection("Monitoren"))
for k in range(4):
    x = 3.5 + (k % 2) * 1.6
    z = 1.4 + (k // 2) * 1.0
    m_ = [T.box(f"Monitor_{k}_kast", (0, 0, 0), (1.5, 0.08, 0.9), P.m("zwart"), bevel=0.02, ol=0),
          T.box(f"Monitor_{k}_beeld", (0, -0.045, 0.05), (1.4, 0.01, 0.8), T.glow("labscherm", (0.06, 0.12, 0.25), 1.2), bevel=0, ol=0)]
    pts = []
    for j in range(25):
        t = j / 24
        yv = 0.15 + 0.5 * (t ** (2 + k)) + 0.03 * math.sin(j * 1.7 + k)
        pts.append((-0.65 + t * 1.3, -0.056, 0.1 + yv))
    m_.append(T.to_mesh(T.tube(f"Monitor_{k}_grafiek", pts, 0.008, T.glow("grafiek", (0.2, 0.9, 1.0), 4.0))))
    for j in range(5):
        m_.append(T.box(f"Monitor_{k}_raster{j}", (0, -0.052, 0.15 + j * 0.15), (1.3, 0.002, 0.005), T.glow("raster", (0.15, 0.35, 0.6), 1.5), bevel=0, ol=0))
    o = T.merge(f"Monitor_{k + 1}", m_, ol=0.006)
    o.location = (x, D / 2 + 1.0 - 0.1, z)
T.box("Bedieningspaneel", (4.3, D / 2 + 1.0 - 0.6, 0), (3.4, 0.8, 1.0), WHITE, bevel=0.03, ol=0.01)
for k in range(10):
    T.cyl(f"Knop_{k}", (3.0 + k * 0.28, D / 2 + 1.0 - 0.8, 1.0), 0.05, 0.03, T.glow(f"knop{k % 3}", [(1, 0.2, 0.2), (0.2, 1, 0.4), (1, 0.85, 0.2)][k % 3], 3), seg=10, ol=0)

# lange witte gang
T.use_collection(T.collection("Gang"))
GL = 24.0
gy0 = 1.0 - D / 2  # gang sluit aan op de hal (y = -6)
T.box("Gang_vloer", (0, gy0 - GL / 2, -0.1), (3.0, GL, 0.1), T.pattern("labvloer", (0.90, 0.92, 0.95), (0.86, 0.88, 0.92), grout=(0.78, 0.80, 0.85), size=(1.0, 1.0)), bevel=0, ol=0)
for s in (-1, 1):
    T.box(f"Gang_wand_{s}", (s * 1.56, gy0 - GL / 2, 0), (0.12, GL, 3.0), WHITE, bevel=0, ol=0.01)
    T.box(f"Gang_blauwe_band_{s}", (s * 1.49, gy0 - GL / 2, 1.0), (0.02, GL, 0.1), BLUE, bevel=0, ol=0)
    for k in range(4):
        T.box(f"Gang_deur_{s}_{k}", (s * 1.49, gy0 - 4 - k * 5.5, 0), (0.04, 1.0, 2.2), T.toon("labdeur", (0.85, 0.88, 0.92)), bevel=0.01, ol=0.006)
        T.box(f"Gang_deurraam_{s}_{k}", (s * 1.47, gy0 - 4 - k * 5.5, 1.3), (0.02, 0.3, 0.5), T.glass("deurraam", (0.7, 0.85, 1.0), alpha=0.4), bevel=0, ol=0)
T.box("Gang_plafond", (0, gy0 - GL / 2, 3.0), (3.2, GL, 0.1), WHITE, bevel=0, ol=0)
gl = [T.box(f"Gang_lamp_{k}", (0, gy0 - 1.5 - k * 3, 2.97), (0.6, 1.4, 0.04), T.glow("ganglamp", (0.95, 0.98, 1.0), 4), bevel=0, ol=0) for k in range(8)]
T.merge("Gang_lampen", gl, ol=0)
T.area_light("Ganglicht", (0, gy0 - GL / 2, 2.9), (0, gy0 - GL / 2, 0), size=(2.5, GL - 2), color=(0.95, 0.98, 1.0), energy=1500)
T.area_light("Hallicht", (0, 2.0, H - 0.1), (0, 2.0, 0), size=(W - 2, D - 2), color=(0.95, 0.98, 1.0), energy=3500)
T.box("Hal_plafondlampen", (0, 2.0, H - 0.04), (10, 0.3, 0.04), T.glow("hallamp", (0.95, 0.98, 1.0), 4), bevel=0, ol=0)

T.use_collection(None)
T.character((0.0, 3.5, 1.05), rot_z=180)  # op de perstafel
cams = [
    T.camera("CAM_01_pers_wide", (5.5, -5.0, 2.6), (0, 3.5, 2.0), lens=22),
    T.camera("CAM_02_gang", (0, gy0 - GL + 1.0, 1.6), (0, gy0 + 2, 1.4), lens=28),
    T.camera("CAM_03_glazen_wand", (-W / 2 + 0.6, -1.5, 1.7), (0, 3.5, 1.5), lens=24),
    T.camera("CAM_04_monitoren", (2.5, 4.5, 1.6), (4.3, D / 2 + 1.0, 1.6), lens=30),
]
blend, renders = T.finish(OUT, "lab", cams)
print("KLAAR", blend, renders)
