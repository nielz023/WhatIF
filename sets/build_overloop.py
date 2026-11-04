"""Set (video 3, No Rules): de overloop boven, 's nachts (scène 5d-5g).
Vier deuren (jongen, broertje, opa, ouders), een trapgat met leuning, een klein raam met maanlicht.

Gebruik:
    blender -b -P sets/build_overloop.py -- [nacht] [uitvoermap]
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402,F401
from mathutils import Matrix, Vector  # noqa: E402
from lib import toon as T  # noqa: E402
from lib import props as P  # noqa: E402
from lib import interior as I  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
VAR = args[0] if args else "nacht"
OUT = args[1] if len(args) > 1 else "/mnt/project-files/videos/geen-regels/sets/22_overloop"

mood = dict(T.MOODS["nacht"])
mood.update(sun_rot=(58, 0, 170), sun_strength=0.2, ambient=(0.07, 0.08, 0.14))
T.new_scene("Overloop_" + VAR, mood, samples=48)

W, D, H = 5.6, 2.6, 2.6
T.use_collection(T.collection("Overloop"))
# deuren in de achterwand (a van links naar rechts): jongen 0.9, broertje 2.6, opa 4.4; ouders in de rechterwand
I.room("Overloop", W, D, H, wall_color=(0.80, 0.74, 0.62), floor_color=(0.55, 0.38, 0.24),
       holes={"back": [(0.45, 1.35, 0, 2.08), (2.15, 3.05, 0, 2.08), (3.95, 4.85, 0, 2.08)],
              "right": [(0.85, 1.75, 0, 2.08)], "left": [(0.9, 1.9, 1.1, 1.9)]})
DONKER = T.toon("kamer_donker", (0.05, 0.05, 0.08))


def door(name, side, a, width=0.9, height=2.05):
    """Kozijn (vast) + deurblad met het scharnier als oorsprong (Deur_x_blad, rotation z +graden = open naar de kamer),
    met een donkere kamer erachter zodat een open deur nooit in het niets kijkt."""
    km = T.toon("kozijn", (0.95, 0.95, 0.93))
    p = [T.box(name + "_kozijn_l", (-width / 2 - 0.04, 0, 0), (0.08, 0.08, height + 0.06), km, bevel=0, ol=0),
         T.box(name + "_kozijn_r", (width / 2 + 0.04, 0, 0), (0.08, 0.08, height + 0.06), km, bevel=0, ol=0),
         T.box(name + "_kozijn_b", (0, 0, height), (width + 0.16, 0.08, 0.08), km, bevel=0, ol=0)]
    pos, rz = I.wall_point(W, D, side, a, 0, inset=0.03)
    R = Matrix.Rotation(math.radians(rz), 4, "Z")
    fr = T.merge(name, p, ol=0.008)
    fr.location = pos
    fr.rotation_euler.z = math.radians(rz)
    leaf = T.merge(name + "_blad", [T.box(name + "_b", (width / 2, 0, 0), (width - 0.02, 0.045, height - 0.02),
                                          T.toon("deur_" + name, (0.93, 0.92, 0.88)), bevel=0.01, ol=0),
                                    T.sphere(name + "_klink", (width - 0.1, -0.06, 1.0), 0.035, P.m("metaal"), seg=10, ol=0)], ol=0.008)
    leaf.location = pos + R @ Vector((-width / 2, 0, 0))
    leaf.rotation_euler.z = math.radians(rz)
    # donkere kamer achter de deur (achterwand, zijwanden, vloer, plafond)
    for nm, c, sz in (("achter", (0, 1.35, 0), (2.2, 0.1, 2.6)), ("l", (-1.1, 0.7, 0), (0.1, 1.3, 2.6)),
                      ("r", (1.1, 0.7, 0), (0.1, 1.3, 2.6)), ("vloer", (0, 0.7, -0.05), (2.2, 1.3, 0.05)),
                      ("plafond", (0, 0.7, 2.6), (2.2, 1.3, 0.05))):
        b = T.box(f"{name}_kamer_{nm}", (0, 0, 0), sz, DONKER, bevel=0, ol=0)
        b.location = pos + R @ Vector(c)
        b.rotation_euler.z = math.radians(rz)
    return fr, leaf


door("Deur_jongen", "back", 0.9)
door("Deur_broertje", "back", 2.6)
door("Deur_opa", "back", 4.4)
door("Deur_ouders", "right", 1.3)
I.window("Raampje", W, D, "left", 0.9, 1.9, 1.1, 1.9, curtains=None)
I.ceiling_lamp("Overlooplamp", (0.6, 0, H), on=False)
I.rug("Loper", (0.2, -0.2, 0), (3.6, 0.9), (0.55, 0.15, 0.15))
# trapgat met leuning vooraan links (spijlen), zodat de ruimte echt een overloop is
hout = T.toon("trapleuning", (0.62, 0.42, 0.24))
x0, x1, y = -W / 2 + 0.2, -0.6, -D / 2 + 0.55
T.box("Leuning_ligger", ((x0 + x1) / 2, y, 0.95), (x1 - x0, 0.07, 0.06), hout, bevel=0.01, ol=0.006)
n = 9
for k in range(n):
    x = x0 + (x1 - x0) * k / (n - 1)
    T.box(f"Leuning_spijl_{k}", (x, y, 0), (0.035, 0.035, 0.95), hout, bevel=0.005, ol=0.004)
T.box("Leuning_paal", (x1, y, 0), (0.09, 0.09, 1.05), hout, bevel=0.01, ol=0.006)
T.box("Trapgat", ((x0 + x1) / 2, (y - D / 2) / 2 - 0.02, -0.02), (x1 - x0 + 0.1, abs(y + D / 2) + 0.02, 0.03),
      T.toon("trapgat_donker", (0.08, 0.06, 0.05)), bevel=0, ol=0)
# een paar dingen aan de muur: lijstjes en een kastje
for k, (a, z) in enumerate(((1.8, 1.55), (3.5, 1.6))):
    T.box(f"Lijstje_{k}", (-W / 2 + a, D / 2 - 0.02, z), (0.38, 0.03, 0.3), T.toon(f"lijstje_{k}", (0.25 + 0.3 * k, 0.4, 0.55)),
          bevel=0.01, ol=0.004)
T.box("Kastje", (W / 2 - 0.35, -D / 2 + 0.35, 0), (0.5, 0.35, 0.8), T.toon("kastje", (0.85, 0.83, 0.78)), bevel=0.02, ol=0.006)
T.area_light("Maanlicht_raampje", (-W / 2 + 0.3, 0.0, 1.6), (0.0, 0.0, -0.4), size=(1.0, 0.8), color=(0.45, 0.55, 1.0), energy=25)
T.area_light("Vullicht_blauw", (0.0, -2.6, 2.2), (0, 0.6, 1.0), size=(3, 2), color=(0.45, 0.55, 1.0), energy=18)

cams = [T.camera("CAM_01_overloop_wide", (0.0, -2.9, 1.6), (0.0, 0.6, 1.1), lens=20)]
blend, renders = T.finish(OUT, "overloop_" + VAR, cams)
print("KLAAR", blend, renders)
