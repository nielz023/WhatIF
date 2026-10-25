"""Sets: kleinere binnenruimtes.
Varianten:
    werkplaats  dag 12: garagewerkplaats van de beste vriend (staalplaten, fietskettingen, emmer tie-wraps, werkbank, gereedschapsbord)
    dokter      dag 13: dokterspraktijk (onderzoekstafel met papierrol, kastjes, skeletposter, bloeddrukmeter, wastafel, krukje, bakje kromme naalden)
    kelder      dag 17: kelder (betonvloer, wasmachine en droger, opslagdozen, oude fietsen, trap omhoog, één peertje, twee gaten in het plafond)

Gebruik:
    blender -b -P sets/build_kleine_interieurs.py -- <variant> [uitvoermap]
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
VAR = args[0] if args else "werkplaats"
OUT = args[1] if len(args) > 1 else {"werkplaats": "/mnt/project-files/sets/13_werkplaats", "dokter": "/mnt/project-files/sets/14_dokterspraktijk",
                                     "kelder": "/mnt/project-files/sets/17_kelder"}[VAR]
rnd = random.Random(13)


def bike(name, loc, rot=0, color=(0.85, 0.15, 0.12)):
    F = T.toon("fietsframe_" + name, color)
    p = []
    for x in (-0.55, 0.55):
        p.append(T.torus(f"{name}_wiel{x}", (x, 0, 0.35), 0.33, 0.025, P.m("zwart"), rot=(90, 0, 0), seg=32, seg2=6, ol=0))
        p.append(T.cyl(f"{name}_naaf{x}", (x, -0.03, 0.35), 0.03, 0.06, P.m("metaal"), rot=(90, 0, 0), seg=8, ol=0))
    pts = [(-0.55, 0, 0.35), (-0.1, 0, 0.35), (0.45, 0, 0.8), (-0.15, 0, 0.82), (-0.1, 0, 0.35)]
    p.append(T.to_mesh(T.tube(f"{name}_frame", pts, 0.022, F)))
    p.append(T.to_mesh(T.tube(f"{name}_achtervork", [(-0.55, 0, 0.35), (-0.15, 0, 0.82)], 0.018, F)))
    p.append(T.to_mesh(T.tube(f"{name}_voorvork", [(0.55, 0, 0.35), (0.45, 0, 0.8), (0.42, 0, 0.98)], 0.02, F)))
    p.append(T.box(f"{name}_stuur", (0.42, 0, 0.98), (0.04, 0.5, 0.03), P.m("zwart"), bevel=0, ol=0))
    p.append(T.box(f"{name}_zadel", (-0.17, 0, 0.88), (0.22, 0.1, 0.05), P.m("zwart"), bevel=0.02, ol=0))
    p.append(T.cyl(f"{name}_zadelpen", (-0.15, 0, 0.8), 0.012, 0.09, P.m("metaal"), seg=6, ol=0))
    o = T.merge(name, p, ol=0.006)
    o.location = loc
    o.rotation_euler.z = math.radians(rot)
    return o


if VAR == "werkplaats":
    mood = dict(T.MOODS["dag"])
    mood.update(ambient=(0.30, 0.30, 0.32), sun_rot=(55, 0, 200), sun_strength=1.1, fog_max=0.0)
    T.new_scene("Werkplaats", mood, samples=48)
    W, D, H = 6.0, 7.0, 2.8
    T.use_collection(T.collection("Garage"))
    room = I.room("Werkplaats", W, D, H, wall_color=(0.75, 0.74, 0.70), floor_color=(0.55, 0.55, 0.53),
                  holes={"front": [(0.5, 5.5, 0, 2.4)], "right": [(2.0, 3.2, 1.2, 2.1)]}, skirting=False)
    room["floor"].data.materials[0] = T.pattern("garagevloer", (0.56, 0.56, 0.54), (0.53, 0.53, 0.51), grout=(0.45, 0.45, 0.44), size=(1.5, 1.5), mortar=0.006)
    I.window("Garageraam", W, D, "right", 2.0, 3.2, 1.2, 2.1)
    # opgerolde garagedeur bovenin de opening
    T.box("Garagedeur_rol", (0, -D / 2 + 0.25, 2.4), (5.2, 0.45, 0.4), T.toon("garagedeur", (0.85, 0.85, 0.88)), bevel=0.15, ol=0.01)
    # werkbank tegen de achterwand
    T.use_collection(T.collection("Werkbank en gereedschap"))
    WB = T.toon("werkbank_hout", (0.72, 0.50, 0.28))
    wb = [T.box("Werkbank_blad", (0, 0, 0.88), (3.0, 0.75, 0.07), WB, bevel=0.01, ol=0),
          T.box("Werkbank_plank", (0, 0, 0.25), (2.9, 0.7, 0.04), WB, bevel=0.005, ol=0)]
    for x in (-1.4, 1.4):
        for y in (-0.32, 0.32):
            wb.append(T.box(f"Werkbank_poot{x}{y}", (x, y, 0), (0.07, 0.07, 0.88), WB, bevel=0, ol=0))
    T.merge("Werkbank", wb, ol=0.01).location = (0, D / 2 - 0.4, 0)
    T.box("Bankschroef", (1.2, D / 2 - 0.65, 0.95), (0.2, 0.25, 0.14), T.toon("bankschroef", (0.15, 0.35, 0.75)), bevel=0.02, ol=0.006)
    # gereedschapsbord (pegboard) met silhouetten van gereedschap
    T.box("Gereedschapsbord", (0, D / 2 - 0.03, 1.15), (2.6, 0.03, 1.2), T.toon("pegboard", (0.80, 0.68, 0.48)), bevel=0, ol=0.006)
    tools = [((-1.0, 1.5), (0.05, 0.45), (0.85, 0.15, 0.12)), ((-0.8, 1.5), (0.05, 0.4), (0.15, 0.45, 0.85)), ((-0.55, 1.45), (0.18, 0.05), (0.2, 0.2, 0.22)),
             ((-0.3, 1.6), (0.06, 0.35), (0.98, 0.75, 0.1)), ((0.0, 1.5), (0.3, 0.06), (0.4, 0.4, 0.45)), ((0.35, 1.55), (0.05, 0.5), (0.2, 0.6, 0.3)),
             ((0.6, 1.5), (0.05, 0.42), (0.85, 0.15, 0.12)), ((0.9, 1.4), (0.22, 0.22), (0.4, 0.4, 0.45))]
    for k, ((x, z), (w, h), c) in enumerate(tools):
        T.box(f"Gereedschap_{k}", (x, D / 2 - 0.06, z), (w, 0.03, h), T.toon(f"gereedschap{k}", c), bevel=0.01, ol=0.004)
    # staalplaten tegen de muur, fietskettingen, emmer tie-wraps
    for k in range(4):
        T.box(f"Staalplaat_{k + 1}", (-W / 2 + 0.15 + k * 0.05, -0.5 + k * 0.1, 0), (0.02, 1.2, 1.6), T.toon("staal", (0.62, 0.65, 0.70)), rot=(0, -8, 0), bevel=0.005, ol=0.006)
    for k in range(3):
        pts = [(math.cos(a) * (0.25 + 0.02 * k), math.sin(a) * (0.12 + 0.01 * k), 0.03 + 0.012 * k) for a in [i * 0.4 for i in range(17)]]
        ch = T.tube(f"Fietsketting_{k + 1}", pts, 0.012, T.toon("ketting", (0.30, 0.30, 0.34)), closed=True)
        ch.location = (-0.6 + k * 0.15, D / 2 - 0.45, 0.92)
    em = [T.cyl("Emmer", (0, 0, 0), 0.16, 0.3, T.toon("emmer_oranje", (0.95, 0.45, 0.1)), r2=0.19, seg=20, ol=0, cap=True),
          T.torus("Emmer_hengsel", (0, 0, 0.3), 0.18, 0.006, P.m("metaal"), rot=(90, 0, 0), seg=20, seg2=4, ol=0)]
    emo = T.merge("Emmer_tie_wraps", em, ol=0.006)
    emo.location = (1.6, D / 2 - 1.2, 0)
    P.points_mesh("Tie_wraps", [(1.6 + rnd.uniform(-0.14, 0.14), D / 2 - 1.2 + rnd.uniform(-0.14, 0.14), 0.3 + rnd.uniform(0, 0.06)) for _ in range(40)], 0.025, T.toon("tie_wrap", (0.1, 0.1, 0.1)), seg=4)
    bike("Fiets_oud", (2.1, -0.8, 0), rot=95, color=(0.15, 0.55, 0.85))
    T.box("Gereedschapskist", (-1.6, D / 2 - 0.5, 0.0), (0.6, 0.45, 0.8), T.toon("gereedschapskist", (0.85, 0.12, 0.12)), bevel=0.02, ol=0.008)
    I.ceiling_lamp("TL_werkplaats", (0, 0, H), on=True)
    T.point_light("Werklamp", (0, 0.5, H - 0.8), color=(1.0, 0.95, 0.85), energy=300, radius=0.2)
    # oprit buiten
    T.use_collection(T.collection("Buiten"))
    P.ground("Oprit", (100, 100), (0.6, 0.58, 0.55), z=-0.03)
    T.use_collection(None)
    T.character((-0.4, 0.2, 0), rot_z=160)
    cams = [T.camera("CAM_01_werkplaats_wide", (1.8, -4.6, 1.7), (-0.4, 1.8, 1.0), lens=22),
            T.camera("CAM_02_werkbank", (0.3, 1.2, 1.45), (0, D / 2, 1.1), lens=28)]

elif VAR == "dokter":
    mood = dict(T.MOODS["binnen"])
    mood.update(ambient=(0.45, 0.50, 0.56), shadow_tint=(0.60, 0.68, 0.82), lit_tint=(0.96, 1.0, 1.0), sun_rot=(50, 0, -110), sun_strength=1.0, fog_max=0.0)
    T.new_scene("Dokterspraktijk", mood, samples=48)
    W, D, H = 4.4, 4.0, 2.7
    T.use_collection(T.collection("Kamer"))
    room = I.room("Praktijk", W, D, H, wall_color=(0.86, 0.93, 0.97), floor_color=(0.75, 0.82, 0.86), holes={"right": [(1.2, 2.6, 1.0, 2.1)]})
    room["floor"].data.materials[0] = T.pattern("praktijkvloer", (0.80, 0.86, 0.90), (0.76, 0.83, 0.88), grout=(0.68, 0.74, 0.80), size=(0.5, 0.5), mortar=0.006)
    I.window("Praktijkraam", W, D, "right", 1.2, 2.6, 1.0, 2.1, curtains=(0.65, 0.82, 0.92), open_frac=0.6)
    I.door("Praktijkdeur", W, D, "left", 1.0)
    T.use_collection(T.collection("Inrichting"))
    # onderzoekstafel met papierrol
    BL = T.toon("tafel_lichtblauw", (0.45, 0.70, 0.88))
    et = [T.box("Onderzoekstafel_kussen", (0, 0, 0.7), (0.7, 1.9, 0.12), BL, bevel=0.04, ol=0),
          T.box("Onderzoekstafel_hoofd", (0, 0.75, 0.82), (0.7, 0.5, 0.1), BL, rot=(25, 0, 0), bevel=0.04, ol=0),
          T.box("Onderzoekstafel_kast", (0, 0, 0), (0.6, 1.7, 0.7), T.toon("kast_wit", (0.94, 0.95, 0.96)), bevel=0.02, ol=0),
          T.box("Papier", (0, -0.1, 0.825), (0.52, 1.6, 0.004), P.m("wit"), bevel=0, ol=0),
          T.cyl("Papierrol", (-0.3, -0.95, 0.88), 0.07, 0.6, P.m("wit"), rot=(0, 90, 0), seg=16, ol=0)]
    T.merge("Onderzoekstafel", et, ol=0.01).location = (-1.1, 0.7, 0)
    # kastjes met verband
    for k in range(3):
        T.box(f"Kastje_{k}", (0.2 + k * 0.62, D / 2 - 0.25, 0), (0.6, 0.48, 0.88), T.toon("kast_wit", (0.94, 0.95, 0.96)), bevel=0.02, ol=0.008)
    T.box("Werkblad", (0.82, D / 2 - 0.25, 0.88), (1.9, 0.52, 0.04), T.toon("werkblad_grijs", (0.75, 0.78, 0.82)), bevel=0.01, ol=0.006)
    T.box("Wandkast", (0.82, D / 2 - 0.18, 1.5), (1.9, 0.34, 0.7), T.toon("kast_wit", (0.94, 0.95, 0.96)), bevel=0.02, ol=0.008)
    for k in range(4):
        T.cyl(f"Verbandrol_{k}", (0.1 + k * 0.12, D / 2 - 0.3, 0.92), 0.04, 0.09, P.m("wit"), seg=12, ol=0.003)
    T.box("Pleisterdoos", (0.65, D / 2 - 0.3, 0.92), (0.16, 0.08, 0.1), T.toon("pleisterdoos", (0.9, 0.2, 0.2)), bevel=0.01, ol=0.003)
    # wastafel
    T.box("Wastafel", (1.6, D / 2 - 0.25, 0.86), (0.45, 0.4, 0.08), P.m("wit"), bevel=0.02, ol=0.005)
    T.cyl("Kraan", (1.6, D / 2 - 0.08, 0.9), 0.015, 0.25, P.m("metaal"), seg=8, ol=0.003)
    # skeletposter
    sk = [T.box("Poster_vlak", (0, 0, 0), (0.6, 0.012, 0.9), T.toon("poster_licht", (0.95, 0.96, 0.92)), bevel=0, base=False, ol=0),
          T.sphere("Poster_schedel", (0, -0.008, 0.33), 0.06, P.m("wit"), scale=(1, 0.2, 1.1), seg=10, ol=0)]
    BONE = T.toon("bot", (0.75, 0.72, 0.65))
    sk.append(T.box("Poster_ruggengraat", (0, -0.008, 0.02), (0.02, 0.006, 0.5), BONE, base=False, bevel=0, ol=0))
    for r in range(5):
        sk.append(T.box(f"Poster_rib{r}", (0, -0.008, 0.18 - r * 0.045), (0.2 - r * 0.02, 0.006, 0.015), BONE, base=False, bevel=0, ol=0))
    for s in (-1, 1):
        sk.append(T.box(f"Poster_arm{s}", (s * 0.14, -0.008, 0.05), (0.015, 0.006, 0.35), BONE, rot=(0, s * 15, 0), base=False, bevel=0, ol=0))
        sk.append(T.box(f"Poster_been{s}", (s * 0.06, -0.008, -0.3), (0.018, 0.006, 0.4), BONE, rot=(0, -s * 5, 0), base=False, bevel=0, ol=0))
    so = T.merge("Skeletposter", sk, ol=0.003)
    so.location = (-1.1, D / 2 - 0.01, 1.55)
    # bloeddrukmeter aan de muur
    T.box("Bloeddrukmeter", (-W / 2 + 0.03, -0.2, 1.4), (0.04, 0.22, 0.3), T.toon("meter_grijs", (0.85, 0.87, 0.9)), bevel=0.02, ol=0.005)
    T.cyl("Bloeddrukmeter_wijzer", (-W / 2 + 0.06, -0.2, 1.6), 0.08, 0.02, P.m("wit"), rot=(0, 90, 0), seg=20, ol=0.004)
    T.to_mesh(T.tube("Bloeddrukmeter_slang", [(-W / 2 + 0.05, -0.2, 1.4), (-W / 2 + 0.2, -0.3, 1.0), (-W / 2 + 0.1, -0.5, 0.9)], 0.01, P.m("zwart")))
    T.box("Manchet", (-W / 2 + 0.12, -0.55, 0.88), (0.12, 0.3, 0.06), T.toon("manchet", (0.15, 0.3, 0.6)), bevel=0.02, ol=0.004)
    # draaikrukje en bureau
    I.chair("Draaikrukje", (0.4, 0.2, 0), office=True, color=(0.2, 0.45, 0.75))
    I.table("Bureau", (1.4, -0.9, 0), size=(1.2, 0.65, 0.75), color=(0.92, 0.92, 0.94), rot=90)
    T.box("Monitor", (1.55, -0.9, 0.75), (0.06, 0.5, 0.35), P.m("zwart"), bevel=0.01, ol=0.005)
    T.box("Monitor_beeld", (1.52, -0.9, 0.8), (0.005, 0.45, 0.27), T.glow("monitor", (0.5, 0.75, 1.0), 1.5), bevel=0, ol=0)
    # bakje met kromme naalden
    T.box("Naaldenbakje", (0.55, D / 2 - 0.35, 0.92), (0.22, 0.14, 0.04), T.toon("bakje_rvs", (0.75, 0.78, 0.82)), bevel=0.01, ol=0.003)
    for k in range(6):
        pts = [(0.47 + k * 0.03, D / 2 - 0.4, 0.95), (0.48 + k * 0.03, D / 2 - 0.35, 0.97), (0.49 + k * 0.03 + 0.02 * (k % 2), D / 2 - 0.31, 0.955)]
        T.to_mesh(T.tube(f"Kromme_naald_{k + 1}", pts, 0.003, P.m("metaal")))
    T.area_light("Plafondlicht", (0, 0, H - 0.05), (0, 0, 0), size=(1.5, 1.2), color=(0.95, 1.0, 1.0), energy=220)
    T.use_collection(None)
    T.character((-0.35, -0.4, 0), rot_z=-160)
    cams = [T.camera("CAM_01_praktijk_wide", (0.9, -3.7, 1.6), (-0.6, 0.9, 1.0), lens=20),
            T.camera("CAM_02_naalden_close", (0.55, D / 2 - 0.85, 1.25), (0.55, D / 2 - 0.35, 0.93), lens=45),
            T.camera("CAM_03_onderzoekstafel", (0.9, 0.2, 1.4), (-1.1, 0.9, 0.85), lens=26)]

else:  # kelder
    mood = dict(T.MOODS["nacht"])
    mood.update(ambient=(0.05, 0.045, 0.05), shadow_tint=(0.28, 0.22, 0.32), lit_tint=(1.0, 0.85, 0.62), sun_strength=0.0, fog_max=0.0, bloom=0.9)
    T.new_scene("Kelder", mood, samples=64)
    W, D, H = 6.0, 5.5, 2.3
    T.use_collection(T.collection("Kelder"))
    room = I.room("Kelder", W, D, H, wall_color=(0.55, 0.53, 0.50), floor_color=(0.50, 0.49, 0.47), skirting=False)
    room["floor"].data.materials[0] = T.pattern("kelderbeton", (0.52, 0.51, 0.49), (0.49, 0.48, 0.46), grout=(0.42, 0.41, 0.40), size=(2.0, 2.0), mortar=0.004)
    for k, side in enumerate(("back", "left", "right")):
        room[side].data.materials[0] = T.pattern("betonblokken", (0.58, 0.57, 0.54), (0.55, 0.54, 0.51), grout=(0.45, 0.44, 0.42), size=(0.4, 0.2), mortar=0.006, offset=0.5)
    # twee versplinterde gaten in het plafond (hij is er doorheen gezakt)
    ceil = room["ceiling"]
    bpy.data.objects.remove(ceil)
    planks = []
    holes = [(-0.6, 0.5), (0.5, 0.2)]
    for x in [i * 0.25 - W / 2 for i in range(int(W / 0.25) + 1)]:
        y = -D / 2
        segs = []
        cut = [h for h in holes if abs(h[0] - x) < 0.45]
        if cut:
            hy = cut[0][1]
            segs = [(-D / 2, hy - 0.45 + rnd.uniform(-0.1, 0.1)), (hy + 0.45 + rnd.uniform(-0.1, 0.1), D / 2)]
        else:
            segs = [(-D / 2, D / 2)]
        for a, b in segs:
            planks.append(T.box(f"Plafondplank_{x:.2f}_{a:.1f}", (x, (a + b) / 2, H), (0.23, b - a, 0.06), T.toon("plafondhout", (0.55, 0.40, 0.26)), bevel=0.005, ol=0))
    T.merge("Plafond_met_gaten", planks, ol=0.006)
    for k, (hx, hy) in enumerate(holes):
        for j in range(7):
            a = j / 7 * 2 * math.pi
            T.box(f"Splinter_{k}_{j}", (hx + 0.42 * math.cos(a), hy + 0.42 * math.sin(a), H - 0.08), (0.04, 0.2, 0.03), T.toon("splinter", (0.75, 0.58, 0.38)),
                  rot=(30, 0, math.degrees(a) + 90), bevel=0, ol=0.003)
        P.points_mesh(f"Gruis_{k}", [(hx + rnd.uniform(-0.5, 0.5), hy + rnd.uniform(-0.5, 0.5), 0.02) for _ in range(30)], 0.03, T.toon("gruis", (0.6, 0.5, 0.4)), seg=4)
    # balken
    for y in (-1.5, 1.5):
        T.box(f"Balk_{y}", (0, y, H - 0.25), (W, 0.18, 0.25), T.toon("balk", (0.45, 0.32, 0.20)), bevel=0.01, ol=0.006)
    T.use_collection(T.collection("Inhoud"))
    for k, x in enumerate((-2.4, -1.75)):
        wm = [T.box(f"Witgoed_{k}_body", (0, 0, 0), (0.6, 0.6, 0.85), T.toon("witgoed", (0.92, 0.92, 0.94)), bevel=0.03, ol=0),
              T.cyl(f"Witgoed_{k}_deur", (0, -0.3, 0.42), 0.2, 0.03, T.toon("deur_glas", (0.4, 0.5, 0.6)), rot=(90, 0, 0), seg=24, ol=0),
              T.torus(f"Witgoed_{k}_rand", (0, -0.32, 0.42), 0.21, 0.025, P.m("metaal"), rot=(90, 0, 0), seg=24, seg2=6, ol=0),
              T.box(f"Witgoed_{k}_paneel", (0, -0.3, 0.75), (0.56, 0.02, 0.08), T.toon("paneel", (0.7, 0.72, 0.75)), bevel=0, ol=0)]
        T.merge("Wasmachine" if k == 0 else "Droger", wm, ol=0.008).location = (x, D / 2 - 0.4, 0)
    BOX = T.toon("verhuisdoos", (0.78, 0.60, 0.38))
    for k in range(9):
        x, y, z = 1.2 + (k % 3) * 0.55, D / 2 - 0.35, (k // 3) * 0.4
        if k in (5, 8):
            continue
        T.box(f"Opslagdoos_{k + 1}", (x + rnd.uniform(-0.04, 0.04), y, z), (0.5, 0.45, 0.4), BOX, rot=(0, 0, rnd.uniform(-5, 5)), bevel=0.01, ol=0.006)
        T.box(f"Doostape_{k + 1}", (x, y, z + 0.4), (0.5, 0.08, 0.005), T.toon("tape", (0.85, 0.72, 0.45)), bevel=0, ol=0)
    bike("Oude_fiets_1", (W / 2 - 0.35, -0.6, 0), rot=90, color=(0.5, 0.15, 0.12))
    bike("Oude_fiets_2", (W / 2 - 0.55, 0.4, 0), rot=95, color=(0.2, 0.35, 0.3))
    # trap omhoog
    for k in range(10):
        T.box(f"Traptree_{k}", (-W / 2 + 0.5, -D / 2 + 0.5 + k * 0.25, k * 0.22), (0.9, 0.28, 0.06), T.toon("traphout", (0.60, 0.44, 0.28)), bevel=0.005, ol=0.006)
    T.to_mesh(T.tube("Trapleuning", [(-W / 2 + 0.95, -D / 2 + 0.4, 0.9), (-W / 2 + 0.95, -D / 2 + 2.9, 3.1)], 0.025, T.toon("traphout", (0.60, 0.44, 0.28))))
    # één kaal peertje
    T.cyl("Peertje_snoer", (0, 0, H - 0.4), 0.006, 0.4, P.m("zwart"), seg=6, ol=0)
    T.sphere("Peertje", (0, 0, H - 0.45), 0.06, T.glow("peertje", (1.0, 0.82, 0.55), 12), scale=(1, 1, 1.3), seg=12, ol=0)
    T.point_light("Peertje_licht", (0, 0, H - 0.5), color=(1.0, 0.75, 0.45), energy=90, radius=0.05)
    T.use_collection(None)
    T.character((-0.5, 0.4, 0), rot_z=-160)
    cams = [T.camera("CAM_01_kelder_wide", (1.0, -2.6, 1.4), (-0.6, 0.8, 1.0), lens=20),
            T.camera("CAM_02_gaten_plafond", (1.0, -0.6, 1.1), (-0.05, 0.35, H), lens=20)]

blend, renders = T.finish(OUT, VAR, cams)
print("KLAAR", blend, renders)
