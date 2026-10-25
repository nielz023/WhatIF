"""Set: School, klaslokaal en gang met kluisjes. Video 1, dag 19. Grijs daglicht, gedempt.

Gebruik:
    blender -b -P sets/build_school.py -- [klaslokaal|gang] [uitvoermap]
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
VAR = args[0] if args else "klaslokaal"
OUT = args[1] if len(args) > 1 else "/mnt/project-files/sets/18_school"
rnd = random.Random(19)

mood = dict(T.MOODS["bewolkt"])
mood.update(ambient=(0.40, 0.42, 0.44), sun_strength=0.55, sun_rot=(50, 0, 160), fog_max=0.3, fog_start=20, fog_end=200)
T.new_scene("School_" + VAR, mood, samples=48)

if VAR == "klaslokaal":
    W, D, H = 9.0, 8.0, 3.2
    wins = [(a, a + 1.6, 0.9, 2.6) for a in (0.8, 2.9, 5.0, 7.1)]
    T.use_collection(T.collection("Lokaal"))
    room = I.room("Klaslokaal", W, D, H, wall_color=(0.86, 0.88, 0.80), floor_color=(0.55, 0.62, 0.68), holes={"back": wins})
    room["floor"].data.materials[0] = T.pattern("linoleum", (0.56, 0.63, 0.70), (0.52, 0.60, 0.67), size=(0.5, 0.5), kind="schaak")
    for a0, a1, z0, z1 in wins:
        I.window(f"Lokaalraam_{a0}", W, D, "back", a0, a1, z0, z1)
    # whiteboard op de linkerwand (voor de klas)
    T.box("Whiteboard", (-W / 2 + 0.04, 0, 0.95), (0.05, 3.6, 1.25), P.m("wit"), bevel=0.01, ol=0.008)
    T.box("Whiteboard_rand", (-W / 2 + 0.05, 0, 0.92), (0.07, 3.7, 0.06), P.m("metaal"), bevel=0.01, ol=0.006)
    for k, (z, w, c) in enumerate([(1.85, 2.0, (0.15, 0.3, 0.8)), (1.6, 1.5, (0.15, 0.3, 0.8)), (1.35, 2.4, (0.8, 0.15, 0.15))]):
        T.box(f"Whiteboard_tekst_{k}", (-W / 2 + 0.07, -1.6 + w / 2, z), (0.005, w, 0.05), T.toon(f"stift{k}", c), bevel=0, ol=0)
    T.text("Whiteboard_formule", "F = m x a", (-W / 2 + 0.075, 0.9, 1.3), 0.22, T.toon("stift_zwart", (0.08, 0.08, 0.1)), rot=(90, 0, 90), extrude=0.002)
    # wereldkaart
    wm = [T.box("Wereldkaart_zee", (0, 0, 0), (2.0, 0.015, 1.2), T.toon("kaart_zee", (0.35, 0.62, 0.90)), bevel=0, base=False, ol=0)]
    for k, (x, z, sx, sz) in enumerate([(-0.55, 0.2, 0.4, 0.35), (-0.45, -0.25, 0.2, 0.35), (0.05, 0.22, 0.25, 0.25), (0.1, -0.15, 0.22, 0.35), (0.5, 0.18, 0.55, 0.3), (0.65, -0.35, 0.2, 0.12)]):
        wm.append(T.sphere(f"Continent_{k}", (x, -0.01, z), 1.0, T.toon("kaart_land", (0.45, 0.72, 0.35)), scale=(sx, 0.01, sz), seg=12, ol=0))
    wmo = T.merge("Wereldkaart", wm, ol=0.004)
    wmo.location = (W / 2 - 0.02, 0.5, 1.7)
    wmo.rotation_euler.z = math.radians(90)
    # bureaus in rijen
    T.use_collection(T.collection("Bureaus"))
    for r in range(4):
        for c in range(3):
            x = -1.6 + r * 1.5
            y = -2.4 + c * 2.2
            for s in (-0.38, 0.38):
                I.table(f"Schoolbank_{r}_{c}_{s}", (x, y + s, 0), size=(0.6, 0.7, 0.72), color=(0.80, 0.65, 0.42), rot=90)
                I.chair(f"Schoolstoel_{r}_{c}_{s}", (x + 0.48, y + s, 0), rot=90, color=(0.20, 0.45, 0.75))
                if rnd.random() < 0.6:
                    I.books(f"Schrift_{r}_{c}_{s}", (x, y + s, 0.72), n=rnd.randint(1, 3), rot=rnd.uniform(-20, 20), seed=r * 7 + c)
    I.table("Docentenbureau", (-W / 2 + 1.4, -2.6, 0), size=(1.5, 0.8, 0.76), color=(0.65, 0.48, 0.30), rot=90)
    I.chair("Docentenstoel", (-W / 2 + 0.75, -2.6, 0), rot=-90, color=(0.25, 0.25, 0.3), office=True)
    T.cyl("Prullenbak_klas", (-W / 2 + 0.4, -3.6, 0), 0.18, 0.4, P.m("donkergroen"), seg=14, ol=0.006)
    T.cyl("Klok", (W / 2 - 0.03, -2.0, 2.5), 0.2, 0.04, P.m("wit"), rot=(0, 90, 0), seg=24, ol=0.006)
    tl = [T.box(f"TL_lokaal_{x}_{y}", (x, y, H - 0.05), (1.2, 0.2, 0.05), T.glow("tl_lokaal", (0.95, 0.98, 1.0), 3), bevel=0, ol=0) for x in (-2, 1, 3.5) for y in (-2, 1.5)]
    T.merge("TL_lokaal", tl, ol=0)
    T.area_light("Lokaallicht", (0, 0, H - 0.1), (0, 0, 0), size=(7, 6), color=(0.95, 0.98, 1.0), energy=600)
    # buiten: schoolplein met basketbalpaal
    T.use_collection(T.collection("Schoolplein"))
    P.ground("Schoolplein", (200, 200), (0.50, 0.50, 0.52), z=-0.02)
    T.cyl("Basketpaal_buiten", (2.0, 12.0, 0), 0.1, 3.05, P.m("metaal"), seg=10, ol=0.02)
    T.box("Basketbord_buiten", (2.0, 11.8, 2.9), (1.8, 0.05, 1.05), P.m("wit"), bevel=0.01, ol=0.01)
    T.torus("Basketring_buiten", (2.0, 11.45, 3.05), 0.23, 0.02, T.toon("ring_oranje", (0.95, 0.40, 0.05)), seg=24, seg2=6, ol=0.004)
    P.railing("Schoolhek", [(-20, 22, 0), (20, 22, 0)], h=1.8, posts=2.5, color="donkergroen")
    for k, x in enumerate((-12, -4, 8, 15)):
        P.tree(f"Boom_plein_{k}", (x, 18 + (k % 2) * 3, 0), h=7, r=2.4, seed=k)
    T.use_collection(None)
    T.character((1.4, -0.3, 0), rot_z=180)
    cams = [T.camera("CAM_01_klas_wide", (3.8, -4.3, 1.9), (-2.5, 1.0, 1.0), lens=20),
            T.camera("CAM_02_vanaf_whiteboard", (-W / 2 + 0.8, 2.5, 1.6), (3.0, -1.5, 0.9), lens=22),
            T.camera("CAM_03_raam_plein", (1.0, 1.0, 1.5), (2.0, 12.0, 2.0), lens=26)]
else:
    W, D, H = 4.0, 30.0, 3.2
    T.use_collection(T.collection("Gang"))
    room = I.room("Schoolgang", W, D, H, wall_color=(0.86, 0.88, 0.80), floor_color=(0.60, 0.62, 0.66), hide=("front",))
    room["floor"].data.materials[0] = T.pattern("gangvloer", (0.62, 0.64, 0.68), (0.56, 0.58, 0.62), size=(0.4, 0.4), kind="schaak")
    LOCK_COLS = [(0.15, 0.40, 0.80), (0.85, 0.20, 0.15)]
    for s in (-1, 1):
        lk = []
        for k in range(40):
            y = -D / 2 + 1.0 + k * 0.42
            if s < 0 and abs(y - 0.7) < 0.7:
                continue  # deur van het klaslokaal
            col = T.toon(f"kluisje{(k // 8 + (s > 0)) % 2}", LOCK_COLS[(k // 8 + (s > 0)) % 2])
            lk.append(T.box(f"Kluisje_{s}_{k}", (0, 0, 0.1), (0.5, 0.4, 1.9), col, bevel=0.01, ol=0))
            lk[-1].location = (s * (W / 2 - 0.26), y, 0.1)
            for j in range(4):
                lk.append(T.box(f"Kluis_lucht_{s}_{k}_{j}", (s * (W / 2 - 0.515), y, 1.55 + j * 0.06), (0.01, 0.25, 0.025), T.toon("lucht", (0.1, 0.1, 0.15)), bevel=0, ol=0))
            lk.append(T.box(f"Kluis_greep_{s}_{k}", (s * (W / 2 - 0.52), y + 0.12, 1.0), (0.02, 0.03, 0.12), P.m("metaal"), bevel=0, ol=0))
        T.merge(f"Kluisjes_{'links' if s < 0 else 'rechts'}", lk, ol=0.006)
        T.box(f"Gang_plint_{s}", (s * (W / 2 - 0.26), 0, 0), (0.5, D, 0.1), P.m("zwart"), bevel=0, ol=0)
    I.door("Lokaaldeur", W, D, "left", 15.0 + 0.7, color=(0.80, 0.55, 0.30))
    tl = [T.box(f"TL_gang_{k}", (0, -D / 2 + 2 + k * 3, H - 0.05), (0.3, 1.4, 0.05), T.glow("tl_gang", (0.95, 0.98, 1.0), 3.5), bevel=0, ol=0) for k in range(10)]
    T.merge("TL_gang", tl, ol=0)
    T.area_light("Ganglicht", (0, 0, H - 0.1), (0, 0, 0), size=(3, D - 2), color=(0.95, 0.98, 1.0), energy=1500)
    T.use_collection(None)
    T.character((0.3, -6.0, 0), rot_z=10)
    cams = [T.camera("CAM_01_gang", (0.6, -D / 2 + 0.6, 1.6), (0, 6, 1.3), lens=24),
            T.camera("CAM_02_kluisjes", (-0.5, -8.0, 1.5), (W / 2, -5, 1.2), lens=26)]

blend, renders = T.finish(OUT, VAR, cams)
print("KLAAR", blend, renders)
