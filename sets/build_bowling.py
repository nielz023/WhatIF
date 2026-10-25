"""Set: Bowlingbaan. Video 1, dag 6. Neon in paars en blauw.

Gebruik:
    blender -b -P sets/build_bowling.py -- [neon] [uitvoermap]
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
from lib import street as S  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
OUT = args[1] if len(args) > 1 else "/mnt/project-files/sets/09_bowlingbaan"
rnd = random.Random(6)

mood = dict(T.MOODS["nacht"])
mood.update(ambient=(0.16, 0.12, 0.28), shadow_tint=(0.32, 0.22, 0.58), lit_tint=(0.92, 0.85, 1.0), fog_max=0.0, sun_strength=0.0, bloom=1.0)
T.new_scene("Bowlingbaan", mood, samples=32)

NL = 8
LW, GUT = 1.06, 0.24
PITCH = LW + 2 * GUT + 0.1
W, D, H = NL * PITCH + 8, 30.0, 4.2
T.use_collection(T.collection("Hal"))
room = I.room("Bowlinghal", W, D, H, wall_color=(0.14, 0.10, 0.28), floor_color=(0.18, 0.14, 0.30), skirting=False)
room["floor"].data.materials[0] = T.pattern("bowling_tapijt", (0.20, 0.12, 0.40), (0.12, 0.25, 0.50), size=(0.6, 0.6), kind="schaak")
room["ceiling"].data.materials[0] = T.toon("plafond_donker", (0.08, 0.06, 0.14))

LANE = T.pattern("baan_hout", (0.92, 0.70, 0.42), (0.88, 0.66, 0.38), grout=(0.78, 0.55, 0.30), size=(4.0, 0.035), mortar=0.002, offset=0.5)
GUTM = T.toon("goot", (0.25, 0.25, 0.32))
Y0, Y1 = -D / 2 + 9.0, D / 2 - 2.6  # foutlijn .. pinnen
T.use_collection(T.collection("Banen"))
lanes, gutters = [], []
x0 = -NL * PITCH / 2 + PITCH / 2
for i in range(NL):
    x = x0 + i * PITCH
    lanes.append(T.box(f"Baan_{i + 1}", (x, (Y0 + Y1) / 2, 0), (LW, Y1 - Y0, 0.08), LANE, bevel=0, ol=0))
    for s in (-1, 1):
        gutters.append(T.box(f"Goot_{i + 1}_{s}", (x + s * (LW / 2 + GUT / 2), (Y0 + Y1) / 2, 0), (GUT, Y1 - Y0, 0.03), GUTM, bevel=0, ol=0))
    # pijltjes en foutlijn
    for k in range(7):
        T.box(f"Pijltje_{i}_{k}", (x - 0.45 + k * 0.15, Y0 + 4.5, 0.081), (0.03, 0.12, 0.002), T.toon("pijl", (0.3, 0.2, 0.15)), bevel=0, ol=0)
    T.box(f"Foutlijn_{i}", (x, Y0 + 0.02, 0.081), (LW, 0.04, 0.002), P.m("zwart"), bevel=0, ol=0)
    # tien kegels
    k = 0
    for row in range(4):
        for j in range(row + 1):
            px = x + (j - row / 2) * 0.3
            py = Y1 - 0.9 + row * 0.26
            pin = [T.cyl(f"Kegel_{i}_{k}_voet", (0, 0, 0), 0.04, 0.12, P.m("wit"), r2=0.06, seg=12, ol=0),
                   T.sphere(f"Kegel_{i}_{k}_buik", (0, 0, 0.14), 0.06, P.m("wit"), scale=(1, 1, 1.4), seg=12, ol=0),
                   T.cyl(f"Kegel_{i}_{k}_hals", (0, 0, 0.22), 0.025, 0.1, P.m("wit"), seg=10, ol=0),
                   T.cyl(f"Kegel_{i}_{k}_streep", (0, 0, 0.27), 0.03, 0.03, P.m("rood"), seg=10, ol=0),
                   T.sphere(f"Kegel_{i}_{k}_kop", (0, 0, 0.34), 0.035, P.m("wit"), seg=10, ol=0)]
            T.merge(f"Kegel_baan{i + 1}_{k + 1}", pin, ol=0.004).location = (px, py, 0.08)
            k += 1
T.merge("Banen_hout", lanes, ol=0.006)
T.merge("Goten", gutters, ol=0.004)
# scheidingen + balretour tussen elke twee banen
for i in range(NL // 2):
    x = x0 + (2 * i + 0.5) * PITCH
    ret = [T.box(f"Balretour_{i}_kast", (0, 0, 0), (0.45, 1.2, 0.6), T.toon("retour", (0.15, 0.35, 0.80)), bevel=0.08, ol=0),
           T.box(f"Balretour_{i}_rail", (0, -1.0, 0.0), (0.45, 1.0, 0.25), T.toon("retour", (0.15, 0.35, 0.80)), bevel=0.06, ol=0)]
    rr = T.merge(f"Balretour_{i + 1}", ret, ol=0.01)
    rr.location = (x, Y0 - 1.3, 0)
# pinsetter-machine (achter de kegels) en afscherming met neonrand
T.box("Pinsetter_kap", (0, Y1 + 0.2, 1.1), (NL * PITCH + 0.2, 0.6, 2.2), T.toon("kap_donker", (0.10, 0.08, 0.16)), bevel=0.02, ol=0.015)
T.box("Pinsetter_achter", (0, Y1 + 1.2, 0), (NL * PITCH + 0.2, 1.6, 1.2), T.toon("machine_grijs", (0.30, 0.30, 0.36)), bevel=0.02, ol=0.012)
for i in range(NL):
    x = x0 + i * PITCH
    T.box(f"Pinsetter_licht_{i}", (x, Y1 + 0.38, 0.0), (LW, 0.05, 1.05), T.glow("pinsetter_glow", (0.95, 0.92, 1.0), 1.4), bevel=0, ol=0)
    T.text(f"Baannummer_{i + 1}", str(i + 1), (x, Y1 - 0.11, 1.75), 0.4, T.glow("baannummer", (1.0, 0.95, 0.6), 3), extrude=0.02)
T.box("Neonrand_pinsetter", (0, Y1 - 0.12, 2.15), (NL * PITCH + 0.2, 0.06, 0.08), T.glow("neon_paars", (0.75, 0.25, 1.0), 6), bevel=0, ol=0)

# scoreschermen boven de banen
T.use_collection(T.collection("Scoreschermen"))
for i in range(NL // 2):
    x = x0 + (2 * i + 0.5) * PITCH
    sc = [T.box(f"Scorescherm_{i}_kast", (0, 0, 0), (1.5, 0.12, 0.9), P.m("zwart"), bevel=0.02, ol=0),
          T.box(f"Scorescherm_{i}_beeld", (0, -0.065, 0.06), (1.38, 0.01, 0.78), T.glow("scorescherm", (0.25, 0.45, 1.0), 2.0), bevel=0, ol=0)]
    for r in range(4):
        sc.append(T.box(f"Scorescherm_{i}_regel{r}", (0, -0.072, 0.15 + r * 0.17), (1.25, 0.004, 0.09), T.glow("scoreregel", (0.85, 0.92, 1.0), 2.5), bevel=0, ol=0))
    s_ = T.merge(f"Scorescherm_{i + 1}", sc, ol=0.008)
    s_.location = (x, Y0 - 0.3, 2.6)
    s_.rotation_euler.x = math.radians(12)  # beeld kijkt naar de spelers

# zitjes, balrek, schoenenbalie, ballonnen
T.use_collection(T.collection("Lounge"))
for i in range(NL // 2):
    x = x0 + (2 * i + 0.5) * PITCH
    sofa = [T.box(f"Bank_{i}_zit", (0, 0, 0), (2.4, 0.8, 0.45), T.toon("bank_rood", (0.80, 0.15, 0.30)), bevel=0.12, ol=0),
            T.box(f"Bank_{i}_rug", (0, -0.35, 0.3), (2.4, 0.25, 0.6), T.toon("bank_rood", (0.80, 0.15, 0.30)), bevel=0.1, ol=0)]
    T.merge(f"Zitbank_{i + 1}", sofa, ol=0.01).location = (x, Y0 - 3.2, 0)
rack = [T.box("Balrek_frame", (0, 0, 0), (4.0, 0.5, 0.06), P.m("metaal"), bevel=0, ol=0),
        T.box("Balrek_plank2", (0, 0, 0.55), (4.0, 0.5, 0.06), P.m("metaal"), bevel=0, ol=0)]
ball_cols = [(0.9, 0.15, 0.15), (0.15, 0.45, 0.95), (0.25, 0.8, 0.35), (0.95, 0.75, 0.1), (0.7, 0.2, 0.9), (0.95, 0.45, 0.1), (0.1, 0.1, 0.12)]
for k in range(14):
    rack.append(T.sphere(f"Bowlingbal_{k}", (-1.8 + (k % 7) * 0.6, 0, 0.17 + (k // 7) * 0.55), 0.11, T.toon(f"bowlingbal{k % 7}", ball_cols[k % 7]), seg=14, ol=0))
for x in (-2, 2):
    rack.append(T.box(f"Balrek_poot{x}", (x, 0, 0), (0.06, 0.5, 0.65), P.m("metaal"), bevel=0, ol=0))
br = T.merge("Balrek", rack, ol=0.006)
br.location = (-W / 2 + 0.6, Y0 - 3.0, 0)
br.rotation_euler.z = math.radians(90)
# schoenenbalie
ctr = [T.box("Balie", (0, 0, 0), (5.0, 0.8, 1.1), T.toon("balie", (0.15, 0.35, 0.80)), bevel=0.04, ol=0),
       T.box("Balie_blad", (0, 0, 1.1), (5.2, 0.9, 0.06), T.toon("balie_blad", (0.9, 0.88, 0.85)), bevel=0.01, ol=0),
       T.box("Balie_neon", (0, -0.41, 0.95), (5.0, 0.02, 0.05), T.glow("neon_blauw", (0.2, 0.6, 1.0), 6), bevel=0, ol=0)]
for r in range(3):
    for c in range(8):
        col = [(0.85, 0.15, 0.15), (0.15, 0.4, 0.85), (0.95, 0.95, 0.95)][(r + c) % 3]
        ctr.append(T.box(f"Schoen_{r}_{c}", (-2.1 + c * 0.6, 1.3, 0.5 + r * 0.55), (0.32, 0.14, 0.12), T.toon(f"bowlingschoen{(r + c) % 3}", col), bevel=0.04, ol=0))
    ctr.append(T.box(f"Schoenenplank_{r}", (0, 1.3, 0.45 + r * 0.55), (5.0, 0.4, 0.04), P.m("hout"), bevel=0, ol=0))
ctr.append(T.box("Schoenenkast", (0, 1.5, 0), (5.2, 0.1, 2.3), T.toon("kast_donker", (0.12, 0.10, 0.20)), bevel=0, ol=0))
cto = T.merge("Schoenenbalie", ctr, ol=0.01)
cto.location = (W / 2 - 3.5, -D / 2 + 2.0, 0)
cto.rotation_euler.z = math.pi  # schoenenkast tegen de muur, balie naar de banen
T.text("Balie_bord", "SHOES", (W / 2 - 3.5, -D / 2 + 0.4, 2.5), 0.5, T.glow("neon_roze", (1.0, 0.3, 0.75), 6), rot=(90, 0, 180), extrude=0.03)
for k, x in enumerate((x0 + PITCH * 2.5, x0 + PITCH * 3.5)):
    for o in S.balloons(f"Verjaardagsballonnen_{k}", (x, Y0 - 3.2, 0.9), n=6, seed=k + 4, height=1.2):
        pass

# neon langs wanden en plafond
T.use_collection(T.collection("Neon"))
neon = []
for s in (-1, 1):
    neon.append(T.box(f"Neon_wand_{s}", (s * (W / 2 - 0.05), 0, 2.6), (0.05, D - 0.4, 0.06), T.glow("neon_paars", (0.75, 0.25, 1.0), 6), bevel=0, ol=0))
    neon.append(T.box(f"Neon_wand_laag_{s}", (s * (W / 2 - 0.05), 0, 0.4), (0.05, D - 0.4, 0.04), T.glow("neon_blauw", (0.2, 0.6, 1.0), 6), bevel=0, ol=0))
for y in range(int(Y0) + 1, int(Y1), 3):
    neon.append(T.box(f"Neon_plafond_{y}", (0, y, H - 0.05), (NL * PITCH, 0.06, 0.04), T.glow("neon_blauw", (0.2, 0.6, 1.0), 5), bevel=0, ol=0))
T.merge("Neonbuizen", neon, ol=0)
T.area_light("Neon_paars_licht", (-W / 2 + 1, 0, 3.5), (0, 0, 0), size=(2, 20), color=(0.7, 0.3, 1.0), energy=600)
T.area_light("Neon_blauw_licht", (W / 2 - 1, 0, 3.5), (0, 0, 0), size=(2, 20), color=(0.3, 0.6, 1.0), energy=600)
T.area_light("Banen_licht", (0, (Y0 + Y1) / 2, H - 0.2), (0, (Y0 + Y1) / 2, 0), size=(NL * PITCH, Y1 - Y0), color=(1.0, 0.95, 0.9), energy=900)

T.use_collection(None)
T.character((x0 + PITCH * 3, Y0 - 0.6, 0), rot_z=180)
cams = [
    T.camera("CAM_01_banen_wide", (x0 + PITCH * 4.5, Y0 - 5.5, 2.4), (x0 + PITCH * 2.5, Y1, 0.6), lens=22),
    T.camera("CAM_02_kegels", (x0 + PITCH * 3, Y1 - 4.0, 0.35), (x0 + PITCH * 3, Y1 - 0.5, 0.25), lens=35),
    T.camera("CAM_03_balie", (W / 2 - 6.5, -D / 2 + 7.5, 1.6), (W / 2 - 3.5, -D / 2 + 3.5, 1.3), lens=26),
]
blend, renders = T.finish(OUT, "bowlingbaan", cams)
print("KLAAR", blend, renders)
