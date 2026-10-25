"""Set: Winkelcentrum en parkeergarage. Video 1, dag 5.
Varianten:
    winkelcentrum   twee verdiepingen, glazen dak, roltrappen, etalages, fontein, palmen, arcadehal met grijpmachine
    parkeergarage   betonnen pilaren, gele vakken, TL-buizen, rijen auto's, groen uitgangsbord

Gebruik:
    blender -b -P sets/build_winkelcentrum.py -- <variant> [uitvoermap]
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
VAR = args[0] if args else "winkelcentrum"
OUT = args[1] if len(args) > 1 else "/mnt/project-files/sets/08_winkelcentrum"
rnd = random.Random(8)

if VAR == "parkeergarage":
    mood = dict(T.MOODS["binnen"])
    mood.update(ambient=(0.20, 0.26, 0.24), shadow_tint=(0.42, 0.52, 0.50), lit_tint=(0.88, 0.98, 0.94), sun_strength=0.0, bloom=0.6)
else:
    mood = dict(T.MOODS["dag"])
    mood.update(ambient=(0.42, 0.42, 0.46), sun_rot=(35, 0, 30), fog_max=0.0)
T.new_scene(VAR.capitalize(), mood, samples=32)


def mannequin(name, loc, rot=0, color=(0.95, 0.4, 0.3)):
    W_ = T.toon("paspop", (0.95, 0.95, 0.95))
    p = [T.sphere(name + "_hoofd", (0, 0, 1.68), 0.11, W_, seg=12, ol=0),
         T.cyl(name + "_romp", (0, 0, 1.0), 0.17, 0.55, T.toon("kleding_" + name, color), r2=0.2, seg=12, ol=0),
         T.cyl(name + "_benen", (0, 0, 0.12), 0.12, 0.9, T.toon("broek", (0.15, 0.2, 0.35)), r2=0.15, seg=10, ol=0),
         T.cyl(name + "_voet", (0, 0, 0), 0.22, 0.04, P.m("zwart"), seg=16, ol=0),
         T.cyl(name + "_nek", (0, 0, 1.55), 0.04, 0.1, W_, seg=8, ol=0)]
    o = T.merge(name, p, ol=0.008)
    o.location = loc
    o.rotation_euler.z = math.radians(rot)
    return o


def palm(name, loc):
    p = [T.cyl(name + "_bak", (0, 0, 0), 0.45, 0.6, T.toon("plantenbak", (0.85, 0.85, 0.82)), seg=16, ol=0),
         T.cyl(name + "_stam", (0, 0, 0.6), 0.1, 2.4, T.toon("palmstam", (0.55, 0.38, 0.20)), r2=0.07, seg=8, ol=0)]
    for k in range(7):
        a = 2 * math.pi * k / 7
        p.append(T.sphere(f"{name}_blad{k}", (0.6 * math.cos(a), 0.6 * math.sin(a), 2.85), 0.18, P.m("boomblad2"), scale=(4.0, 1.0, 0.25), rot=(0, 25, math.degrees(a)), seg=10, ol=0))
    o = T.merge(name, p, ol=0.012)
    o.location = loc
    return o


if VAR == "winkelcentrum":
    W, D, H = 44.0, 26.0, 11.0
    T.use_collection(T.collection("Hal"))
    room = I.room("Winkelcentrum", W, D, H, wall_color=(0.95, 0.93, 0.88), floor_color=(0.9, 0.88, 0.84), ceiling=False, skirting=False,
                  hide=("front", "back"))  # de winkels vormen zelf de lange wanden
    room["floor"].data.materials[0] = T.pattern("marmervloer", (0.93, 0.91, 0.87), (0.86, 0.84, 0.80), grout=(0.75, 0.73, 0.70), size=(1.0, 1.0), kind="tegels", mortar=0.01)
    # glazen dak: frame + glas
    roof = [T.box(f"Dakspant_{k}", (x, 0, H), (0.25, D, 0.3), T.toon("dakspant", (0.92, 0.92, 0.94)), bevel=0.02, ol=0) for k, x in enumerate(range(-20, 21, 4))]
    roof += [T.box(f"Dakregel_{y}", (0, y, H + 0.05), (W, 0.18, 0.2), T.toon("dakspant", (0.92, 0.92, 0.94)), bevel=0.02, ol=0) for y in range(-12, 13, 3)]
    T.merge("Glazen_dak_frame", roof, ol=0.02)
    g = T.box("Glazen_dak_glas", (0, 0, H + 0.1), (W, D, 0.02), T.glass("dakglas", (0.75, 0.9, 1.0), alpha=0.25), bevel=0, ol=0)
    g.visible_shadow = False
    # galerij op de eerste verdieping (beide lange zijden)
    FLOOR2 = 5.0
    for s in (-1, 1):
        y = s * (D / 2 - 3.5)
        T.box(f"Galerij_{s}", (0, y, FLOOR2 - 0.4), (W, 7.0, 0.4), T.toon("galerij", (0.95, 0.94, 0.92)), bevel=0.02, ol=0.02)
        T.box(f"Galerij_balustrade_{s}", (0, y - s * 3.5, FLOOR2), (W, 0.06, 1.0), T.glass("balustrade", (0.7, 0.88, 0.95), alpha=0.35), bevel=0, ol=0.008)
        T.box(f"Galerij_leuning_{s}", (0, y - s * 3.5, FLOOR2 + 1.0), (W, 0.1, 0.06), P.m("metaal"), bevel=0.01, ol=0.006)
        for x in range(-18, 19, 6):
            T.cyl(f"Galerij_zuil_{s}_{x}", (x, y - s * 3.2, 0), 0.3, FLOOR2 - 0.4, T.toon("zuil", (0.95, 0.94, 0.92)), seg=20, ol=0.012)
    # winkels met etalages (beide verdiepingen)
    shop_cols = [(0.90, 0.25, 0.25), (0.15, 0.50, 0.90), (0.95, 0.70, 0.10), (0.25, 0.70, 0.40), (0.70, 0.30, 0.75), (0.95, 0.50, 0.15)]
    names = ["SHOES", "TECH", "TOYS", "FASHION", "BOOKS", "SPORT", "GAMES", "CAFE"]
    T.use_collection(T.collection("Winkels"))
    FAC = T.toon("gevel_binnen", (0.95, 0.93, 0.88))
    for s in (-1, 1):
        wy = s * (D / 2 - 0.1)
        fill = [T.box(f"Pui_band_{s}", (0, wy, 3.3), (W, 0.3, 1.7), FAC, bevel=0, ol=0),
                T.box(f"Pui_boven_{s}", (0, wy, 8.3), (W, 0.3, H - 8.3), FAC, bevel=0, ol=0)]
        for x in [-22.0 + 0.0] + [v + 4.5 for v in range(-18, 19, 9)]:
            fill.append(T.box(f"Pui_penant_{s}_{x}", (x, wy, 0), (0.5 if abs(x) < 22 else 1.2, 0.3, H), FAC, bevel=0, ol=0))
        fill.append(T.box(f"Pui_rand_{s}", (-21.7, wy, 0), (0.8, 0.3, H), FAC, bevel=0, ol=0))
        T.merge(f"Winkelgevel_{'voor' if s < 0 else 'achter'}", fill, ol=0.015)
        for fl, z0 in enumerate((0.0, FLOOR2)):
            for k, x in enumerate(range(-18, 19, 9)):
                c = shop_cols[(k + fl * 2 + (s > 0)) % 6]
                T.box(f"Winkelpui_{s}_{fl}_{k}", (x, wy - s * 0.05, z0 + 3.4), (8.6, 0.25, 1.0), T.toon(f"pui{c}", c), bevel=0.03, ol=0.012)
                T.text(f"Winkelnaam_{s}_{fl}_{k}", names[(k + fl * 3 + (s > 0) * 5) % 8], (x, wy - s * 0.2, z0 + 3.6), 0.55, P.m("wit"), rot=(90, 0, 0 if s > 0 else 180), extrude=0.03)
                T.box(f"Etalage_{s}_{fl}_{k}", (x, wy - s * 0.05, z0), (8.0, 0.08, 3.3), T.glass("etalage", (0.75, 0.88, 0.95), alpha=0.25), bevel=0, ol=0.008)
                T.box(f"Winkel_binnen_{s}_{fl}_{k}", (x, wy + s * 2.0, z0), (8.6, 4.0, 3.3), T.toon(f"winkel_binnen{c}", tuple(0.55 + v * 0.4 for v in c)), bevel=0, ol=0)
                if fl == 0:
                    for j in range(3):
                        mannequin(f"Paspop_{s}_{k}_{j}", (x - 2 + j * 2, wy + s * 0.8, 0), rot=0 if s > 0 else 180, color=shop_cols[(j + k) % 6])
    # roltrappen
    T.use_collection(T.collection("Roltrappen en fontein"))
    for k, (x, d) in enumerate(((-10, 1), (10, -1))):
        L = 9.0
        esc = [T.box(f"Roltrap_{k}_band", (0, 0, 0), (L, 1.2, 0.3), T.toon("roltrap", (0.35, 0.36, 0.40)), bevel=0.02, ol=0),
               T.box(f"Roltrap_{k}_zijkant_l", (0, 0.65, 0.2), (L, 0.1, 1.0), T.glass("roltrap_glas", (0.7, 0.88, 0.95), alpha=0.35), bevel=0, ol=0),
               T.box(f"Roltrap_{k}_zijkant_r", (0, -0.65, 0.2), (L, 0.1, 1.0), T.glass("roltrap_glas", (0.7, 0.88, 0.95), alpha=0.35), bevel=0, ol=0),
               T.box(f"Roltrap_{k}_leuning_l", (0, 0.65, 1.2), (L, 0.14, 0.08), P.m("zwart"), bevel=0.03, ol=0),
               T.box(f"Roltrap_{k}_leuning_r", (0, -0.65, 1.2), (L, 0.14, 0.08), P.m("zwart"), bevel=0.03, ol=0),
               T.box(f"Roltrap_{k}_onder", (0, 0, -0.5), (L, 1.4, 0.5), T.toon("roltrap_onder", (0.85, 0.85, 0.88)), bevel=0.02, ol=0)]
        steps = [T.box(f"Roltrap_{k}_trede{j}", (-L / 2 + j * 0.45, 0, 0.3), (0.42, 1.1, 0.04), T.toon("trede", (0.55, 0.56, 0.60)), bevel=0, ol=0) for j in range(20)]
        e = T.merge(f"Roltrap_{k + 1}", esc + steps, ol=0.012)
        ang = math.atan2(FLOOR2, 7.6)
        e.rotation_euler = (0, -ang, math.radians(90 * d))  # loopt omhoog naar de galerij
        e.location = (x, 2.2 * d, FLOOR2 / 2 - 0.1)
    # fontein
    ft = [T.cyl("Fontein_bak", (0, 0, 0), 3.2, 0.6, T.toon("fontein_steen", (0.85, 0.83, 0.78)), seg=48, ol=0),
          T.cyl("Fontein_water", (0, 0, 0.45), 3.0, 0.12, T.toon("water", (0.35, 0.65, 0.95)), seg=48, ol=0),
          T.cyl("Fontein_zuil", (0, 0, 0.5), 0.35, 1.4, T.toon("fontein_steen", (0.85, 0.83, 0.78)), seg=20, ol=0),
          T.cyl("Fontein_schaal", (0, 0, 1.9), 1.0, 0.25, T.toon("fontein_steen", (0.85, 0.83, 0.78)), r2=1.2, seg=32, ol=0)]
    T.merge("Fontein", ft, ol=0.015).location = (0, 0, 0)
    jets = []
    for k in range(10):
        a = 2 * math.pi * k / 10
        jets.append(T.to_mesh(T.tube(f"Straal_{k}", [(0, 0, 2.2), (0.6 * math.cos(a), 0.6 * math.sin(a), 3.2), (1.3 * math.cos(a), 1.3 * math.sin(a), 2.15)], 0.05, T.toon("waterstraal", (0.65, 0.85, 1.0)))))
    T.merge("Fontein_stralen", jets, ol=0)
    for x, y in ((-4.8, -4.5), (4.8, -4.5), (-4.8, 4.5), (4.8, 4.5)):
        palm(f"Palm_{x}_{y}", (x, y, 0))
    for k, x in enumerate((-17.5, 17.5)):
        P.bench(f"Bankje_{k}", (x, -1.6, 0), rot=0)
        P.bench(f"Bankje_b{k}", (x, 1.6, 0), rot=180)
    # arcadehal met grijpmachine
    T.use_collection(T.collection("Arcade"))
    AX, AY = -18.0, -9.0
    claw = [T.box("Grijpmachine_kast", (0, 0, 0), (1.0, 1.0, 1.0), T.toon("grijp_rood", (0.9, 0.15, 0.2)), bevel=0.04, ol=0),
            T.box("Grijpmachine_glas", (0, 0, 1.0), (0.96, 0.96, 1.0), T.glass("grijp_glas", (0.8, 0.92, 1.0), alpha=0.2), bevel=0, ol=0),
            T.box("Grijpmachine_top", (0, 0, 2.0), (1.04, 1.04, 0.35), T.toon("grijp_geel", (0.98, 0.78, 0.1)), bevel=0.04, ol=0),
            T.cyl("Grijpmachine_kabel", (0.1, 0.1, 1.5), 0.008, 0.5, P.m("metaal"), seg=6, ol=0),
            T.box("Grijpmachine_paneel", (0, -0.55, 0.8), (0.8, 0.2, 0.18), P.m("zwart"), bevel=0.02, ol=0),
            T.cyl("Grijpmachine_joystick", (-0.2, -0.55, 0.98), 0.015, 0.12, P.m("metaal"), seg=6, ol=0),
            T.sphere("Grijpmachine_knop", (-0.2, -0.55, 1.12), 0.035, P.m("rood"), seg=8, ol=0)]
    for j in range(3):
        a = 2 * math.pi * j / 3
        claw.append(T.to_mesh(T.tube(f"Grijper_{j}", [(0.1, 0.1, 1.5), (0.1 + 0.12 * math.cos(a), 0.1 + 0.12 * math.sin(a), 1.38), (0.1 + 0.06 * math.cos(a), 0.1 + 0.06 * math.sin(a), 1.28)], 0.012, P.m("metaal"))))
    plush = [(rnd.uniform(-0.38, 0.38), rnd.uniform(-0.38, 0.38), 1.05 + rnd.uniform(0, 0.15)) for _ in range(16)]
    cm = T.merge("Grijpmachine", claw, ol=0.01)
    knuffels = P.points_mesh("Knuffels", plush, 0.11, T.toon("knuffel", (0.95, 0.65, 0.75)), seg=10)
    knuffels.parent = cm
    cm.location = (AX, AY, 0)
    for k in range(4):
        cab = [T.box(f"Arcadekast_{k}_body", (0, 0, 0), (0.8, 0.8, 1.9), T.toon(f"arcade{k}", shop_cols[k]), bevel=0.03, ol=0),
               T.box(f"Arcadekast_{k}_scherm", (0, -0.41, 1.15), (0.6, 0.02, 0.5), T.glow(f"arcadescherm{k}", (0.3 + k * 0.15, 0.8, 1.0 - k * 0.2), 2.5), bevel=0, ol=0)]
        T.merge(f"Arcadekast_{k + 1}", cab, ol=0.01).location = (AX + 1.6 + k * 1.0, AY - 1.0, 0)
    T.box("Arcade_bord", (AX + 2.5, -D / 2 + 3.6, 3.9), (6, 0.2, 0.9), T.glow("arcade_neon", (1.0, 0.3, 0.8), 2.5), bevel=0.05, ol=0.01)
    T.use_collection(None)
    T.character((-3.0, -4.5, 0), rot_z=20)
    cams = [T.camera("CAM_01_hal_wide", (16, -10.5, 3.0), (-6, 2, 4.0), lens=20),
            T.camera("CAM_02_fontein", (-6, -6, 1.6), (0, 0, 1.8), lens=26),
            T.camera("CAM_03_grijpmachine", (AX + 1.8, AY - 2.6, 1.5), (AX, AY, 1.2), lens=30),
            T.camera("CAM_04_roltrap", (2.0, -6.0, 1.7), (-6, -2.5, 3.0), lens=24)]
else:
    W, D, H = 50.0, 34.0, 2.9
    T.use_collection(T.collection("Garage"))
    room = I.room("Parkeergarage", W, D, H, wall_color=(0.60, 0.62, 0.60), floor_color=(0.42, 0.44, 0.44), skirting=False)
    room["ceiling"].data.materials[0] = T.toon("plafond_beton", (0.58, 0.60, 0.58))
    CON = T.toon("beton_garage", (0.66, 0.67, 0.64))
    YEL = T.toon("parkeerlijn_geel", (0.98, 0.80, 0.10))
    pil, lines, tl = [], [], []
    for x in range(-20, 21, 8):
        for y in (-9, 9):
            pil.append(T.box(f"Pilaar_{x}_{y}", (x, y, 0), (0.6, 0.6, H), CON, bevel=0.03, ol=0))
            pil.append(T.box(f"Pilaar_streep_{x}_{y}", (x, y, 0.3), (0.62, 0.62, 0.3), YEL, bevel=0.01, ol=0))
    for x in range(-22, 23, 3):
        for y0 in (-13.5, 13.5):
            lines.append(T.plane(f"Vak_{x}_{y0}", (x - 1.5, y0, 0.004), (0.1, 5.0), YEL))
    lines.append(T.plane("Rijbaan_lijn", (0, 0, 0.004), (46, 0.12), T.toon("rijbaan_wit", (0.92, 0.92, 0.9))))
    for x in range(-20, 21, 6):
        for k, y in enumerate((-8, 0, 8)):
            tl.append(T.box(f"TL_{x}_{y}", (x, y, H - 0.12), (1.5, 0.1, 0.06), T.glow("tl_garage", (0.85, 1.0, 0.95), 5), bevel=0, ol=0))
    T.merge("Pilaren", pil, ol=0.012)
    T.merge("Parkeerlijnen", lines, ol=0)
    T.merge("TL_buizen", tl, ol=0)
    T.area_light("TL_licht_1", (-10, 0, H - 0.2), (-10, 0, 0), size=(20, 24), color=(0.85, 1.0, 0.95), energy=1200)
    T.area_light("TL_licht_2", (10, 0, H - 0.2), (10, 0, 0), size=(20, 24), color=(0.85, 1.0, 0.95), energy=1200)
    car_cols = [(0.10, 0.35, 0.80), (0.85, 0.15, 0.12), (0.92, 0.92, 0.92), (0.15, 0.15, 0.18), (0.95, 0.70, 0.10), (0.30, 0.60, 0.35), (0.6, 0.6, 0.65)]
    T.use_collection(T.collection("Auto's"))
    k = 0
    for x in range(-21, 22, 3):
        for y, r in ((-13.5, 90), (13.5, -90)):
            if rnd.random() < 0.72:
                P.car(f"Auto_{k}", (x, y, 0), rot=r + rnd.uniform(-3, 3), color=car_cols[k % 7], kind="hatch" if k % 3 else "sedan")
            k += 1
    # groen uitgangsbord
    ex = [T.box("Uitgang_bord", (0, 0, 0), (1.4, 0.12, 0.45), T.glow("uitgang_groen", (0.1, 0.85, 0.35), 3), bevel=0.02, ol=0)]
    exo = T.merge("Uitgangsbord", ex, ol=0.01)
    exo.location = (20, 0, H - 0.65)
    exo.rotation_euler.z = math.radians(90)
    T.text("Uitgang_tekst", "EXIT", (19.93, 0, H - 0.6), 0.3, P.m("wit"), rot=(90, 0, -90), extrude=0.01)
    T.point_light("Uitgang_gloed", (19.6, 0, H - 0.5), color=(0.2, 1.0, 0.4), energy=30)
    T.use_collection(None)
    T.character((-4.0, -2.0, 0), rot_z=30)
    cams = [T.camera("CAM_01_garage_wide", (-22, -4, 1.6), (6, 2, 1.0), lens=22),
            T.camera("CAM_02_auto_laag", (-6, -8.5, 0.7), (-2, -13, 0.7), lens=24),
            T.camera("CAM_03_naar_uitgang", (8, 1.5, 1.6), (20, 0, 2.2), lens=28)]

blend, renders = T.finish(OUT, VAR, cams)
print("KLAAR", blend, renders)
