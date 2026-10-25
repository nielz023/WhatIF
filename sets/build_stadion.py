"""Set: Honkbalstadion. Video 1, dag 14. Late middag, gouden licht.

Gebruik:
    blender -b -P sets/build_stadion.py -- [middag] [uitvoermap]
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402,F401
from lib import toon as T  # noqa: E402
from lib import props as P  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
OUT = args[1] if len(args) > 1 else "/mnt/project-files/sets/15_honkbalstadion"
rnd = random.Random(14)

mood = dict(T.MOODS["dag"])
mood.update(sky_top=(0.25, 0.42, 0.85), sky_horizon=(1.0, 0.80, 0.55), sun_color=(1.0, 0.80, 0.52), sun_strength=1.1, sun_rot=(68, 0, -140),
            lit_tint=(1.0, 0.88, 0.70), shadow_tint=(0.48, 0.45, 0.68), fog_color=(1.0, 0.85, 0.65), fog_start=80, fog_end=600, fog_max=0.35)
T.new_scene("Honkbalstadion", mood, samples=32)

# Thuisplaat op (0,0); veld waaiert uit richting +x/+y (45 graden)
T.use_collection(T.collection("Veld"))
GRASS = T.pattern("gras_strepen", (0.22, 0.58, 0.20), (0.26, 0.64, 0.24), size=(6.0, 6.0), kind="schaak")
DIRT = T.toon("gravel", (0.78, 0.50, 0.30))
P.ground("Omgeving", (1200, 1200), (0.30, 0.45, 0.25), z=-0.05)
R_OUT = 110.0
fan = [(0, 0, 0)] + [(R_OUT * math.cos(math.radians(a)), R_OUT * math.sin(math.radians(a)), 0) for a in range(0, 91, 3)]
T.mesh_from("Veld_gras", fan, [tuple(range(len(fan)))], GRASS).location.z = 0.0
# binnenveld: zand-diamant met grasvlak
infield_r = 38.0
arc = [(0, 0, 0.01)] + [(infield_r * math.cos(math.radians(a)), infield_r * math.sin(math.radians(a)), 0.01) for a in range(0, 91, 3)]
T.mesh_from("Binnenveld_zand", arc, [tuple(range(len(arc)))], DIRT)
B = 27.4
diamond = [(1.5, 1.5, 0.02), (B - 1.5, 1.5, 0.02), (B - 1.5, B - 1.5, 0.02), (1.5, B - 1.5, 0.02)]
T.mesh_from("Binnenveld_gras", diamond, [(0, 1, 2, 3)], GRASS)
T.cyl("Werpheuvel", (B / 2, B / 2, 0), 2.7, 0.25, DIRT, r2=2.0, seg=32, ol=0.02)
T.box("Werpersplaat", (B / 2, B / 2, 0.25), (0.6, 0.15, 0.02), P.m("wit"), rot=(0, 0, 45), bevel=0, ol=0.004)
home = T.mesh_from("Thuisplaat", [(0, 0, 0.03), (0.3, 0, 0.03), (0.43, 0.13, 0.03), (0.13, 0.43, 0.03), (0, 0.3, 0.03)], [(0, 1, 2, 3, 4)], P.m("wit"), ol=0.005)
T.cyl("Thuisplaat_cirkel", (0, 0, 0.012), 4.0, 0.01, DIRT, seg=40, ol=0)
for k, (x, y) in enumerate([(B, 0), (B, B), (0, B)]):
    T.box(f"Honk_{k + 1}", (x, y, 0.02), (0.38, 0.38, 0.08), P.m("wit"), rot=(0, 0, 45), bevel=0.02, ol=0.005)
for a in (0, 90):
    d = (math.cos(math.radians(a)), math.sin(math.radians(a)))
    T.plane(f"Foutlijn_{a}", (d[0] * R_OUT / 2, d[1] * R_OUT / 2, 0.03), (0.12 if a else R_OUT, R_OUT if a else 0.12), P.m("wit"))
# outfield-muur met reclameborden
wall = []
ads = [(0.15, 0.45, 0.95), (0.95, 0.25, 0.20), (0.98, 0.75, 0.10), (0.25, 0.70, 0.35), (0.95, 0.95, 0.95)]
for k, a in enumerate(range(0, 90, 6)):
    a0, a1 = math.radians(a), math.radians(a + 6)
    mx, my = R_OUT * math.cos((a0 + a1) / 2), R_OUT * math.sin((a0 + a1) / 2)
    L = 2 * R_OUT * math.sin((a1 - a0) / 2)
    wall.append(T.box(f"Muur_{a}", (mx, my, 0), (L + 0.1, 0.5, 3.0), T.toon("muur_groen", (0.10, 0.30, 0.18)), rot=(0, 0, a + 3 + 90), bevel=0, ol=0))
    wall.append(T.box(f"Reclame_{a}", (mx - 0.27 * math.cos((a0 + a1) / 2), my - 0.27 * math.sin((a0 + a1) / 2), 1.3), (L - 0.6, 0.05, 1.4),
                      T.toon(f"reclame{k % 5}", ads[k % 5]), rot=(0, 0, a + 3 + 90), bevel=0, ol=0))
T.merge("Outfield_muur", wall, ol=0.03)
# dugouts
for k, (x, y, r) in enumerate([(17, -5.5, 0), (-5.5, 17, 90)]):
    T.box(f"Dugout_{k + 1}", (x, y, -0.6), (14, 3, 1.8), T.toon("dugout", (0.15, 0.30, 0.65)), rot=(0, 0, r), bevel=0.05, ol=0.02)

# tribunes rondom (stoelrijen + publiek als stippen)
T.use_collection(T.collection("Tribunes en publiek"))
STAND = T.toon("tribune_beton", (0.70, 0.70, 0.72))
SEATS = [(0.15, 0.35, 0.80), (0.85, 0.15, 0.15)]
crowd_cols = [(0.95, 0.30, 0.25), (0.15, 0.40, 0.90), (0.98, 0.98, 0.98), (0.98, 0.75, 0.15), (0.25, 0.25, 0.30), (0.30, 0.70, 0.40)]
crowd = {i: [] for i in range(len(crowd_cols))}
tiers = []


def stand_ring(r0, a_from, a_to, rows, step=0.9, rise=0.55, z0=0.0, name="Tribune", cx=0.0, cy=0.0):
    for r in range(rows):
        rr = r0 + r * step
        for a in range(a_from, a_to, 4):
            a0, a1 = math.radians(a), math.radians(a + 4)
            mx, my = cx + rr * math.cos((a0 + a1) / 2), cy + rr * math.sin((a0 + a1) / 2)
            L = 2 * rr * math.sin((a1 - a0) / 2)
            tiers.append(T.box(f"{name}_{r}_{a}", (mx, my, 0), (L + 0.08, step, z0 + 0.6 + r * rise), STAND, rot=(0, 0, a + 2 + 90), bevel=0, ol=0))
            n = int(L / 0.65)
            for j in range(n):
                t = (j + 0.5) / n
                aa = a0 + (a1 - a0) * t
                if rnd.random() < 0.88:
                    crowd[rnd.randrange(len(crowd_cols))].append((cx + rr * math.cos(aa), cy + rr * math.sin(aa), z0 + 0.6 + r * rise + 0.5))


stand_ring(R_OUT + 3, 0, 92, 14, name="Tribune_outfield", rise=0.6, z0=0.5)
# tribune achter de thuisplaat (boog om 0,0 heen, van -90 tot 180 graden)
stand_ring(24, 100, 350, 18, name="Tribune_thuis", rise=0.55, z0=0.0)
T.merge("Tribunes", tiers, ol=0.02)
for i, pts in crowd.items():
    P.points_mesh(f"Publiek_{i}", pts, 0.22, T.toon(f"publiek{i}", crowd_cols[i]), seg=6)
    P.points_mesh(f"Publiek_hoofden_{i}", [(x, y, z + 0.35) for x, y, z in pts], 0.12, T.toon("huid_publiek", (0.85, 0.62, 0.45)), seg=6)

# scorebord, lichtmasten, vlaggen
T.use_collection(T.collection("Scorebord en masten"))
sb = [T.box("Scorebord_kast", (0, 0, 0), (26, 2.0, 12), T.toon("scorebord", (0.10, 0.15, 0.25)), bevel=0.1, ol=0),
      T.box("Scorebord_scherm", (0, -1.02, 2.5), (22, 0.05, 7.5), T.glow("scorebord_scherm", (0.15, 0.35, 0.80), 1.4), bevel=0, ol=0)]
for c in range(9):
    for r in range(2):
        sb.append(T.box(f"Scorevak_{c}_{r}", (-8 + c * 2, -1.06, 4.0 + r * 1.6), (1.5, 0.02, 1.1), T.glow("scorevak", (0.95, 0.95, 0.8), 2.0), bevel=0, ol=0))
for x in (-9, 9):
    sb.append(T.box(f"Scorebord_poot{x}", (x, 0, -14), (1.2, 1.2, 14), P.m("metaal"), bevel=0, ol=0))
s_ = T.merge("Scorebord", sb, ol=0.05)
s_.location = (R_OUT * 0.78, R_OUT * 0.78, 22)
s_.rotation_euler.z = math.radians(-45)
T.text("Scorebord_tekst", "HOME 0   AWAY 0", (0, 0, 0), 1.5, T.glow("scoretekst", (1.0, 0.85, 0.3), 3.0), extrude=0.05).parent = s_
bpy.data.objects["Scorebord_tekst"].location = (0, -1.1, 8.6)
for k, a in enumerate((5, 35, 55, 85)):
    x, y = (R_OUT + 20) * math.cos(math.radians(a)), (R_OUT + 20) * math.sin(math.radians(a))
    mast = [T.cyl(f"Mast_{k}_paal", (0, 0, 0), 0.8, 45, P.m("metaal"), r2=0.5, seg=12, ol=0),
            T.box(f"Mast_{k}_rek", (0, 0, 45), (9, 1.0, 5), P.m("metaal"), bevel=0.05, ol=0)]
    for r in range(3):
        for c in range(6):
            mast.append(T.box(f"Mast_{k}_lamp{r}{c}", (-3.75 + c * 1.5, -0.55, 45.8 + r * 1.5), (1.2, 0.1, 1.0), T.toon("lamp_uit", (0.95, 0.95, 0.88)), bevel=0, ol=0))
    m_ = T.merge(f"Lichtmast_{k + 1}", mast, ol=0.06)
    m_.location = (x, y, 0)
    m_.rotation_euler.z = math.radians(a + 90)
for k, a in enumerate(range(10, 85, 15)):
    x, y = (R_OUT + 11) * math.cos(math.radians(a)), (R_OUT + 11) * math.sin(math.radians(a))
    T.cyl(f"Vlaggenmast_{k}", (x, y, 9), 0.08, 8, P.m("wit"), seg=8, ol=0.02)
    T.box(f"Vlag_{k}", (x + 0.9, y, 15.5), (1.8, 0.04, 1.1), T.toon(f"vlag{k % 3}", [(0.85, 0.15, 0.15), (0.15, 0.35, 0.85), (0.98, 0.98, 0.98)][k % 3]), bevel=0, ol=0.01)

T.use_collection(None)
T.character((B / 2, B / 2, 0.25), rot_z=225)
cams = [
    T.camera("CAM_01_stadion_wide", (-14, -14, 9), (40, 40, 3), lens=22),
    T.camera("CAM_02_werpheuvel", (B / 2 + 4.5, B / 2 + 4.5, 1.4), (B / 2, B / 2, 1.2), lens=35),
    T.camera("CAM_03_naar_outfield", (B / 2 - 3, B / 2 - 3, 1.7), (80, 80, 12), lens=24),
]
blend, renders = T.finish(OUT, "honkbalstadion", cams)
print("KLAAR", blend, renders)
