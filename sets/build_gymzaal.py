"""Set: Gymzaal van school. Video 1, dag 3 (armpje drukken). Fel TL-licht, oranje vloer.

Gebruik:
    blender -b -P sets/build_gymzaal.py -- [binnen] [uitvoermap]
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
OUT = args[1] if len(args) > 1 else "/mnt/project-files/sets/06_gymzaal"

mood = dict(T.MOODS["binnen"])
mood.update(ambient=(0.45, 0.45, 0.48), sun_rot=(40, 0, 20), sun_strength=0.9, shadow_tint=(0.58, 0.58, 0.72))
T.new_scene("Gymzaal", mood, samples=32)

W, D, H = 28.0, 17.0, 8.0
wins = [(a, a + 2.4, 5.6, 7.4) for a in [1.5 + k * 3.2 for k in range(8)]]
T.use_collection(T.collection("Zaal"))
room = I.room("Gymzaal", W, D, H, wall_color=(0.86, 0.84, 0.78), floor_color=(0.85, 0.55, 0.25),
              holes={"back": wins}, skirting=False)
room["floor"].data.materials[0] = T.pattern("sportvloer", (0.90, 0.58, 0.26), (0.86, 0.54, 0.23), grout=(0.70, 0.42, 0.18), size=(2.0, 0.12), mortar=0.004, offset=0.5)
# onderste helft van de muren: steen / lambrisering
for side, (loc, rz, L) in {"back": ((0, D / 2 - 0.02, 0), 0, W), "left": ((-W / 2 + 0.02, 0, 0), 90, D), "right": ((W / 2 - 0.02, 0, 0), 90, D)}.items():
    T.box(f"Lambrisering_{side}", loc, (L, 0.04, 2.2), T.toon("lambrisering", (0.30, 0.50, 0.72)), rot=(0, 0, rz), bevel=0, ol=0)
for a0, a1, z0, z1 in wins:
    I.window(f"Hoog_raam_{int(a0)}", W, D, "back", a0, a1, z0, z1)

# lijnen op de vloer (basketbalveld)
LINE = T.toon("vloerlijn_wit", (0.97, 0.97, 0.95))
BLUE = T.toon("vloerlijn_blauw", (0.10, 0.35, 0.85))
RED = T.toon("vloerlijn_rood", (0.85, 0.12, 0.10))
for (x, y, w, d, m) in [(0, 6.5, 24, 0.08, LINE), (0, -6.5, 24, 0.08, LINE), (12, 0, 0.08, 13, LINE), (-12, 0, 0.08, 13, LINE), (0, 0, 0.08, 13, LINE),
                        (0, 7.6, 26, 0.06, BLUE), (0, -7.6, 26, 0.06, BLUE), (13, 0, 0.06, 15.2, RED), (-13, 0, 0.06, 15.2, RED)]:
    T.plane(f"Lijn_{x}_{y}_{w}", (x, y, 0.004), (w, d), m)
T.torus("Middencirkel", (0, 0, 0.004), 1.8, 0.04, LINE, seg=64, seg2=4, ol=0).scale.z = 0.05
for s in (-1, 1):
    arc = [(s * 12 - s * 5.6 * math.cos(math.radians(a)), 5.6 * math.sin(math.radians(a)), 0.004) for a in range(-80, 81, 4)]
    T.tube(f"Driepuntsboog_{s}", arc, 0.04, LINE).scale.z = 0.05
    T.box(f"Bucket_{s}", (s * 9.9, 0, 0.0), (4.2, 3.6, 0.006), T.toon("bucket", (0.85, 0.30, 0.15)), bevel=0, ol=0)

# ---------------------------------------------------------------------------
# Sporttoestellen
# ---------------------------------------------------------------------------
T.use_collection(T.collection("Toestellen"))
WOOD = T.toon("gym_hout", (0.85, 0.62, 0.35))
# wandrekken langs de linkerwand
for k in range(5):
    y = -5 + k * 1.2
    parts = [T.box(f"Wandrek_{k}_stijl1", (0, -0.5, 0), (0.08, 0.08, 2.8), WOOD, bevel=0.01, ol=0),
             T.box(f"Wandrek_{k}_stijl2", (0, 0.5, 0), (0.08, 0.08, 2.8), WOOD, bevel=0.01, ol=0)]
    for j in range(16):
        parts.append(T.cyl(f"Wandrek_{k}_sport{j}", (0, -0.5, 0.2 + j * 0.16), 0.022, 1.0, WOOD, rot=(-90, 0, 0), seg=8, ol=0))
    T.merge(f"Wandrek_{k + 1}", parts, ol=0.01).location = (-W / 2 + 0.15, y, 0)
# optrekstang
T.cyl("Optrekstang_stang", (-W / 2 + 0.1, 3.5, 2.5), 0.025, 1.3, P.m("metaal"), rot=(-90, 0, 0), seg=10, ol=0.008)
for y in (3.5, 4.8):
    T.box(f"Optrekstang_beugel_{y}", (-W / 2 + 0.25, y, 2.45), (0.5, 0.06, 0.1), P.m("metaal"), bevel=0.01, ol=0.006)
# gestapelde blauwe matten
for k in range(6):
    T.box(f"Mat_{k + 1}", (-W / 2 + 2.2, -7.0 + k * 0.01, k * 0.12), (2.0, 1.2, 0.11), T.toon("mat_blauw", (0.12, 0.35, 0.80)), rot=(0, 0, k * 2.5 - 6), bevel=0.04, ol=0.01)
for k in range(3):
    T.box(f"Dikke_mat_{k + 1}", (-W / 2 + 5.2, -7.2, k * 0.4), (3.0, 1.8, 0.38), T.toon("mat_rood", (0.85, 0.20, 0.15)), rot=(0, 0, k * 3), bevel=0.08, ol=0.012)
# basketbalborden (aan de zijwanden)
for s in (-1, 1):
    x = s * (W / 2 - 0.2)
    b = [T.box(f"Bord_arm_{s}", (-s * 0.6, 0, 3.4), (1.2, 0.12, 0.12), P.m("metaal"), bevel=0.01, ol=0),
         T.box(f"Bord_plaat_{s}", (-s * 1.2, 0, 2.95), (0.05, 1.8, 1.05), P.m("wit"), bevel=0.01, ol=0),
         T.box(f"Bord_vak_{s}", (-s * 1.23, 0, 3.08), (0.01, 0.6, 0.45), RED, bevel=0, ol=0),
         T.box(f"Bord_vak_in_{s}", (-s * 1.235, 0, 3.12), (0.01, 0.52, 0.37), P.m("wit"), bevel=0, ol=0),
         T.torus(f"Ring_{s}", (-s * 1.48, 0, 3.05), 0.23, 0.018, T.toon("ring_oranje", (0.95, 0.40, 0.05)), seg=24, seg2=6, ol=0)]
    net = []
    for j in range(12):
        a = 2 * math.pi * j / 12
        net.append(T.to_mesh(T.tube(f"Netje_{s}_{j}", [(-s * 1.48 + 0.23 * math.cos(a), 0.23 * math.sin(a), 3.05), (-s * 1.48 + 0.14 * math.cos(a + 0.4), 0.14 * math.sin(a + 0.4), 2.65)], 0.005, P.m("wit"))))
    T.merge(f"Basketbalbord_{'links' if s < 0 else 'rechts'}", b + net, ol=0.008).location = (x, 0, 0)
# houten bankjes langs de achterwand
for k, x in enumerate((-8, -3, 3, 8)):
    bp = [T.box(f"Gymbank_{k}_zit", (0, 0, 0.32), (3.5, 0.28, 0.05), WOOD, bevel=0.01, ol=0),
          T.box(f"Gymbank_{k}_balk", (0, 0, 0.12), (3.2, 0.06, 0.1), WOOD, bevel=0.01, ol=0)]
    for xx in (-1.5, 1.5):
        bp.append(T.box(f"Gymbank_{k}_poot{xx}", (xx, 0, 0), (0.08, 0.36, 0.32), WOOD, bevel=0.01, ol=0))
    T.merge(f"Gymbank_{k + 1}", bp, ol=0.01).location = (x, D / 2 - 0.5, 0)
# klok aan de muur
T.cyl("Wandklok", (0, D / 2 - 0.05, 4.4), 0.38, 0.06, P.m("wit"), rot=(90, 0, 0), seg=32, ol=0.012)
T.torus("Wandklok_rand", (0, D / 2 - 0.09, 4.4), 0.38, 0.03, P.m("zwart"), rot=(90, 0, 0), seg=32, seg2=6, ol=0)
T.box("Wandklok_wijzer_uur", (0.0, D / 2 - 0.1, 4.4), (0.025, 0.01, 0.2), P.m("zwart"), bevel=0, ol=0)
T.box("Wandklok_wijzer_min", (0.0, D / 2 - 0.1, 4.4), (0.02, 0.01, 0.3), P.m("zwart"), rot=(0, 110, 0), bevel=0, ol=0)
# klaptafel voor het armpje drukken
ft = [T.box("Klaptafel_blad", (0, 0, 0.72), (1.2, 0.7, 0.04), T.toon("klaptafel", (0.92, 0.92, 0.9)), bevel=0.01, ol=0)]
for x in (-0.5, 0.5):
    ft.append(T.to_mesh(T.tube(f"Klaptafel_poot{x}", [(x, -0.3, 0), (x, 0, 0.72), (x, 0.3, 0)], 0.018, P.m("metaal"))))
T.merge("Klaptafel_armpje_drukken", ft, ol=0.008).location = (2.0, -1.0, 0)
for k, y in enumerate((-1.75, -0.25)):
    I.chair(f"Klapstoel_{k + 1}", (2.0, y, 0), rot=180 if k == 0 else 0, color=(0.25, 0.30, 0.38))
# ballen
for k, (x, y, c) in enumerate([(6, 3, (0.92, 0.42, 0.10)), (6.4, 3.3, (0.92, 0.42, 0.10)), (-6, -4, (0.95, 0.95, 0.9))]):
    T.sphere(f"Bal_{k + 1}", (x, y, 0.12), 0.12, T.toon(f"bal{k}", c), seg=14, ol=0.006)

# TL-buizen aan het plafond
T.use_collection(T.collection("Licht"))
tl = []
for x in range(-11, 12, 4):
    for y in (-4, 0, 4):
        tl.append(T.box(f"TL_{x}_{y}", (x, y, H - 0.35), (2.4, 0.12, 0.06), T.glow("tl_buis", (0.95, 0.98, 1.0), 4), bevel=0, ol=0))
T.merge("TL_buizen", tl, ol=0)
T.area_light("TL_licht", (0, 0, H - 0.5), (0, 0, 0), size=(24, 12), color=(0.95, 0.98, 1.0), energy=2500)

T.use_collection(None)
T.character((0.8, -1.0, 0), rot_z=90)
cams = [
    T.camera("CAM_01_zaal_wide", (9, -8.2, 3.2), (-2, 2, 1.3), lens=18),
    T.camera("CAM_02_armpje_drukken", (2.0, -3.6, 1.2), (2.0, -1.0, 0.9), lens=32),
    T.camera("CAM_03_wandrek", (-6, -3, 1.6), (-W / 2, 1, 1.6), lens=26),
]
blend, renders = T.finish(OUT, "gymzaal", cams)
print("KLAAR", blend, renders)
