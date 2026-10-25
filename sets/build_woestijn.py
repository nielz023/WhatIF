"""Sets: woestijnbasis van het leger en omgeving.
Varianten:
    bunker         dag 22: kale betonnen bunker, matras, één lamp, telefoon op de grond, zware deur met grendel
    basis_dag      dag 24 en 37: hangars, legertenten, zandzakken, radarschotel, jeeps, whiteboard met formules, rotsen, struiken, duinen
    testterrein    dag 27: sensoren op palen, seismograaf onder een tent, vlaggen op afstand, rotsen en duinen
    nachtlucht     dag 30: woestijn 's nachts, sterren, volle maan, lichten van de basis, gloed van de stad aan de horizon
    basis_schemer  dag 35: de basis in de schemering (paars en roze), zandzakken met paal halverwege, jeeps, tenten

Gebruik:
    blender -b -P sets/build_woestijn.py -- <variant> [uitvoermap]
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
VAR = args[0] if args else "basis_dag"
OUT = args[1] if len(args) > 1 else ("/mnt/project-files/sets/19_bunker" if VAR == "bunker" else
                                     "/mnt/project-files/sets/21_nachtlucht_woestijn" if VAR == "nachtlucht" else "/mnt/project-files/sets/20_woestijnbasis")
rnd = random.Random(24)

SAND = (0.88, 0.70, 0.42)
DESERT_DAY = dict(T.MOODS["dag"])
DESERT_DAY.update(sky_top=(0.20, 0.45, 0.92), sky_horizon=(0.95, 0.88, 0.72), ground_glow=(0.9, 0.75, 0.5), sun_color=(1.0, 0.93, 0.78), sun_strength=1.2,
                  sun_rot=(38, 0, 40), ambient=(0.42, 0.38, 0.36), shadow_tint=(0.62, 0.48, 0.55), lit_tint=(1.0, 0.95, 0.85),
                  fog_color=(0.95, 0.86, 0.70), fog_start=60, fog_end=900, fog_max=0.55)


def jeep(name, loc, rot=0):
    G = T.toon("jeep_zand", (0.62, 0.55, 0.38))
    p = [T.box(name + "_body", (0, 0, 0.45), (3.8, 1.8, 0.8), G, bevel=0.1, ol=0),
         T.box(name + "_kap", (1.0, 0, 1.25), (1.5, 1.7, 0.08), G, bevel=0.02, ol=0),
         T.box(name + "_ruit", (0.35, 0, 1.2), (0.05, 1.6, 0.55), T.toon("autoruit", (0.12, 0.18, 0.26)), rot=(0, -10, 0), bevel=0, ol=0),
         T.box(name + "_rolbeugel", (-0.6, 0, 1.25), (0.08, 1.7, 0.7), P.m("zwart"), bevel=0.02, ol=0),
         T.cyl(name + "_reservewiel", (-1.95, 0, 1.0), 0.38, 0.25, P.m("zwart"), rot=(0, 90, 0), seg=16, ol=0)]
    for x in (1.2, -1.2):
        for y in (0.85, -0.85):
            p.append(T.cyl(f"{name}_wiel{x}{y}", (x, y - 0.12 * (1 if y > 0 else -1), 0.4), 0.4, 0.3, P.m("zwart"), rot=(90, 0, 0), seg=16, ol=0))
    o = T.merge(name, p, ol=0.02)
    o.location = loc
    o.rotation_euler.z = math.radians(rot)
    return o


def sandbag_wall(name, start, end, rows=3, gap=None):
    a, b = start, end
    L = math.hypot(b[0] - a[0], b[1] - a[1])
    ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
    bags = []
    n = int(L / 0.62)
    for r in range(rows):
        for k in range(n):
            t = (k + 0.5 + (0.5 if r % 2 else 0)) / n
            if t > 1:
                continue
            x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            bags.append(T.box(f"{name}_{r}_{k}", (x, y, r * 0.24), (0.6, 0.38, 0.25), T.toon("zandzak", (0.70, 0.62, 0.42)), rot=(0, 0, ang + rnd.uniform(-4, 4)), bevel=0.08, ol=0))
    return T.merge(name, bags, ol=0.015)


def tent(name, loc, rot=0, size=(6, 4, 3)):
    sx, sy, h = size
    tt = T.mesh_from(name, [(-sx / 2, -sy / 2, 0), (sx / 2, -sy / 2, 0), (sx / 2, sy / 2, 0), (-sx / 2, sy / 2, 0), (-sx / 2, 0, h), (sx / 2, 0, h)],
                     [(0, 1, 5, 4), (3, 4, 5, 2), (0, 4, 3), (1, 2, 5)], T.toon("tentdoek", (0.45, 0.48, 0.30)), ol=0.03)
    tt.location = loc
    tt.rotation_euler.z = math.radians(rot)
    return tt


def hangar(name, loc, rot=0, L=30, R=11):
    pts = []
    faces = []
    seg = 16
    for i in range(seg + 1):
        a = math.pi * i / seg
        pts.append((-L / 2, R * math.cos(a), R * math.sin(a) * 0.8))
        pts.append((L / 2, R * math.cos(a), R * math.sin(a) * 0.8))
    for i in range(seg):
        faces.append((2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2))
    h = T.mesh_from(name + "_dak", pts, faces, T.toon("hangar_golfplaat", (0.70, 0.68, 0.62)), ol=0.04)
    back = T.mesh_from(name + "_achter", [p for p in pts[1::2]], [tuple(range(seg + 1))], T.toon("hangar_wand", (0.62, 0.60, 0.55)), ol=0.04)
    door = T.box(name + "_deur", (-L / 2 + 0.1, 0, 0), (0.2, R * 1.3, R * 0.65), T.toon("hangardeur", (0.30, 0.32, 0.28)), bevel=0.02, ol=0.03)
    o = T.merge(name, [h, back, door], ol=0.04)
    o.location = loc
    o.rotation_euler.z = math.radians(rot)
    return o


def desert_ground(dunes=True, size=1600):
    P.ground("Woestijnzand", (size, size), SAND, z=0.0)
    if dunes:
        for k in range(26):
            a = rnd.uniform(0, 2 * math.pi)
            d = rnd.uniform(140, 600)
            s = rnd.uniform(30, 90)
            T.sphere(f"Duin_{k}", (d * math.cos(a), d * math.sin(a), -s * 0.75), s, T.toon("duin", (0.92, 0.72, 0.42) if k % 2 else (0.86, 0.64, 0.36)),
                     scale=(1.8, 1.0, 0.95), rot=(0, 0, math.degrees(a)), seg=32, ol=0)
        # rotsformaties (mesa's)
        for k in range(8):
            a = rnd.uniform(0, 2 * math.pi)
            d = rnd.uniform(250, 700)
            h = rnd.uniform(30, 80)
            T.cyl(f"Rotsformatie_{k}", (d * math.cos(a), d * math.sin(a), 0), rnd.uniform(25, 60), h, T.toon("rots_rood", (0.72, 0.38, 0.22)), r2=rnd.uniform(18, 45), seg=9, ol=0.2)
    rocks = []
    for k in range(60):
        a = rnd.uniform(0, 2 * math.pi)
        d = rnd.uniform(25, 160)
        rocks.append(T.sphere(f"Steen_{k}", (d * math.cos(a), d * math.sin(a), 0.1), rnd.uniform(0.3, 1.5), T.toon("steen", (0.62, 0.48, 0.34)),
                              scale=(1.3, 1.0, 0.6), seg=7, ol=0))
    T.merge("Stenen", rocks, ol=0.03)
    shrubs = []
    for k in range(90):
        a = rnd.uniform(0, 2 * math.pi)
        d = rnd.uniform(15, 200)
        shrubs.append((d * math.cos(a), d * math.sin(a), 0.3))
    P.points_mesh("Droge_struiken", shrubs, 0.45, T.toon("struik_droog", (0.55, 0.52, 0.28)), seg=6)


def base(lights_on=False, dusk=False):
    T.use_collection(T.collection("Basis"))
    hangar("Hangar_1", (-40, 30, 0), rot=10)
    hangar("Hangar_2", (-10, 55, 0), rot=10)
    for k, (x, y) in enumerate([(15, 25), (24, 20), (33, 15), (18, 38), (28, 33)]):
        tent(f"Legertent_{k + 1}", (x, y, 0), rot=10 + rnd.uniform(-5, 5))
    # radarschotel
    rd = [T.cyl("Radar_voet", (0, 0, 0), 1.6, 3.0, T.toon("radar_wit", (0.92, 0.92, 0.9)), r2=1.0, seg=16, ol=0),
          T.sphere("Radar_schotel", (0, 0, 6.0), 4.5, T.toon("radar_wit", (0.92, 0.92, 0.9)), scale=(1, 0.3, 1), seg=24, ol=0),
          T.cyl("Radar_arm", (0, -0.5, 3.0), 0.25, 3.0, P.m("metaal"), seg=10, ol=0)]
    r_ = T.merge("Radarschotel", rd, ol=0.05)
    r_.location = (45, 50, 0)
    r_.rotation_euler = (math.radians(-30), 0, math.radians(200))
    # jeeps
    for k, (x, y, r) in enumerate([(6, 8, 20), (10, 4, 35), (-5, 12, -10)]):
        jeep(f"Jeep_{k + 1}", (x, y, 0), rot=r)
    # zandzakkenlinie met een paaltje halverwege het hek
    sandbag_wall("Zandzakken_linie", (-12, -6), (12, -6), rows=3)
    for k, x in enumerate(range(-30, 31, 4)):
        T.cyl(f"Hekpaal_{k}", (x, -12, 0), 0.06, 1.8, P.m("metaal"), seg=6, ol=0.01)
    T.to_mesh(T.tube("Hekdraad_1", [(-30, -12, 1.2), (30, -12, 1.2)], 0.012, P.m("metaal")))
    T.to_mesh(T.tube("Hekdraad_2", [(-30, -12, 0.6), (30, -12, 0.6)], 0.012, P.m("metaal")))
    T.cyl("Hekpaal_halverwege", (0, -40, 0), 0.08, 1.6, T.toon("paal_rood_wit", (0.85, 0.15, 0.12)), seg=8, ol=0.02)
    # whiteboard met formules (bij de tenten)
    wb = [T.box("Whiteboard_bord", (0, 0, 1.0), (2.4, 0.05, 1.3), P.m("wit"), bevel=0.01, ol=0),
          T.box("Whiteboard_poot_l", (-1.1, 0, 0), (0.05, 0.6, 1.1), P.m("metaal"), bevel=0, ol=0),
          T.box("Whiteboard_poot_r", (1.1, 0, 0), (0.05, 0.6, 1.1), P.m("metaal"), bevel=0, ol=0)]
    wbo = T.merge("Whiteboard_formules", wb, ol=0.01)
    wbo.location = (13, 14, 0)
    wbo.rotation_euler.z = math.radians(200)
    for k, line in enumerate(["F = m x a", "2^n", "g = 9.81", "v = ?"]):
        t = T.text(f"Formule_{k}", line, (0, -0.03, 2.0 - k * 0.25), 0.16, T.toon("stift_blauw", (0.1, 0.25, 0.8)), extrude=0.002)
        t.parent = wbo
    # lantaarns / bouwlampen
    for k, (x, y) in enumerate([(-20, 10), (5, 18), (25, 5), (-30, 45), (40, 30)]):
        mast = [T.cyl(f"Bouwlamp_{k}_mast", (0, 0, 0), 0.1, 7, P.m("metaal"), seg=8, ol=0),
                T.box(f"Bouwlamp_{k}_kop", (0, 0, 7), (1.2, 0.3, 0.6), P.m("metaal"), bevel=0.03, ol=0)]
        T.merge(f"Bouwlamp_{k + 1}", mast, ol=0.02).location = (x, y, 0)
        if lights_on:
            T.box(f"Bouwlamp_{k}_glas", (x, y - 0.16, 7.1), (1.0, 0.02, 0.4), T.glow("bouwlamp", (1.0, 0.92, 0.75), 8), bevel=0, ol=0)
            T.point_light(f"Bouwlamp_licht_{k}", (x, y - 1.0, 6.5), color=(1.0, 0.85, 0.6), energy=3000 if dusk else 6000, radius=0.4)
    # vlaggenmast
    T.cyl("Vlaggenmast", (0, 20, 0), 0.08, 10, P.m("metaal"), seg=8, ol=0.02)
    T.box("Vlag", (1.0, 20, 8.8), (2.0, 0.04, 1.2), T.toon("vlag_groen", (0.25, 0.35, 0.22)), bevel=0, ol=0.01)


if VAR == "bunker":
    mood = dict(T.MOODS["nacht"])
    mood.update(ambient=(0.03, 0.03, 0.035), shadow_tint=(0.25, 0.25, 0.32), lit_tint=(1.0, 0.92, 0.75), sun_strength=0.0, fog_max=0.0, bloom=0.8)
    T.new_scene("Bunker", mood, samples=64)
    W, D, H = 5.0, 6.0, 2.8
    T.use_collection(T.collection("Bunker"))
    room = I.room("Bunker", W, D, H, wall_color=(0.55, 0.55, 0.53), floor_color=(0.45, 0.45, 0.44), skirting=False, holes={"back": [(2.0, 3.2, 0, 2.1)]})
    CON = T.pattern("bunkerbeton", (0.56, 0.56, 0.54), (0.53, 0.53, 0.51), grout=(0.46, 0.46, 0.45), size=(1.2, 0.6), mortar=0.004, offset=0.5)
    for side in ("back", "left", "right", "front"):
        room[side].data.materials[0] = CON
    # zware deur met grendel
    dr = [T.box("Bunkerdeur_blad", (0, 0, 0), (1.2, 0.18, 2.1), T.toon("staal_donker", (0.30, 0.32, 0.30)), bevel=0.02, ol=0),
          T.box("Bunkerdeur_grendel", (0.2, -0.12, 1.1), (0.9, 0.08, 0.1), P.m("metaal"), bevel=0.02, ol=0),
          T.box("Bunkerdeur_grendelhouder", (0.62, -0.12, 1.1), (0.12, 0.12, 0.22), P.m("metaal"), bevel=0.02, ol=0),
          T.cyl("Bunkerdeur_wiel", (-0.25, -0.12, 1.4), 0.2, 0.04, P.m("metaal"), rot=(90, 0, 0), seg=16, ol=0)]
    for z in (0.3, 1.8):
        dr.append(T.box(f"Bunkerdeur_scharnier_{z}", (-0.62, -0.1, z), (0.08, 0.12, 0.25), P.m("metaal"), bevel=0.01, ol=0))
    T.merge("Bunkerdeur", dr, ol=0.01).location = (0.1, D / 2 - 0.02, 0)
    # matras op de vloer, telefoon op de grond
    T.box("Matras", (-1.4, -0.3, 0), (0.95, 2.0, 0.18), T.toon("matras", (0.80, 0.82, 0.86)), bevel=0.06, ol=0.01)
    T.box("Deken", (-1.4, -0.6, 0.15), (0.98, 1.2, 0.06), T.toon("deken_grijs", (0.40, 0.45, 0.42)), bevel=0.03, ol=0.008)
    T.box("Kussen", (-1.4, 0.45, 0.17), (0.6, 0.35, 0.1), P.m("wit"), bevel=0.04, ol=0.006)
    T.box("Telefoon_vloer", (-0.6, -1.1, 0.0), (0.075, 0.15, 0.01), P.m("zwart"), rot=(0, 0, 25), bevel=0.004, ol=0.003)
    T.box("Telefoon_scherm", (-0.6, -1.1, 0.011), (0.066, 0.14, 0.002), T.glow("telefoonscherm", (0.45, 0.65, 1.0), 4), rot=(0, 0, 25), bevel=0, ol=0)
    # één lamp: kooilamp aan het plafond met lichtkegel
    T.cyl("Kooilamp_kap", (0, -0.3, H - 0.25), 0.18, 0.2, P.m("metaal"), r2=0.08, seg=16, ol=0.006, cap=False)
    T.sphere("Kooilamp_peer", (0, -0.3, H - 0.3), 0.06, T.glow("peer", (1, 0.85, 0.6), 12), seg=10, ol=0)
    T.spot_light("Lichtkegel", (0, -0.3, H - 0.32), (0, -0.3, 0), color=(1.0, 0.85, 0.6), energy=260, angle=70, blend=0.15)
    cone = T.cyl("Lichtkegel_zichtbaar", (0, -0.3, 0.0), 1.55, H - 0.32, T.glass("lichtbundel", (1.0, 0.85, 0.55), alpha=0.08), r2=0.12, seg=32, ol=0, cap=False)
    cone.visible_shadow = False
    T.use_collection(None)
    T.character((-0.9, -0.6, 0), rot_z=-150)
    cams = [T.camera("CAM_01_bunker_wide", (1.8, -2.9, 1.7), (-0.8, 0.8, 0.7), lens=20),
            T.camera("CAM_02_telefoon_vloer", (-0.2, -1.6, 0.25), (-0.6, -1.1, 0.0), lens=35),
            T.camera("CAM_03_deur", (-1.5, -1.5, 1.4), (0.1, D / 2, 1.1), lens=26)]

elif VAR in ("basis_dag", "basis_schemer", "testterrein"):
    mood = dict(DESERT_DAY)
    if VAR == "basis_schemer":
        mood.update(sky_top=(0.18, 0.12, 0.42), sky_horizon=(0.98, 0.50, 0.55), ground_glow=(0.7, 0.4, 0.5), sun_color=(1.0, 0.55, 0.50), sun_strength=0.6,
                    sun_rot=(84, 0, 200), ambient=(0.36, 0.26, 0.42), shadow_tint=(0.52, 0.38, 0.62), lit_tint=(1.0, 0.75, 0.70),
                    fog_color=(0.88, 0.50, 0.60), fog_max=0.6, sun_disc=dict(color=(1.0, 0.7, 0.5), size=6.0, dir=(200, 3)), bloom=0.7)
    T.new_scene("Woestijn_" + VAR, mood, samples=32)
    T.use_collection(T.collection("Woestijn"))
    desert_ground()
    if VAR == "testterrein":
        T.use_collection(T.collection("Testterrein"))
        for k in range(10):
            a = math.radians(-30 + k * 7)
            d = 18 + (k % 3) * 9
            x, y = d * math.cos(a), d * math.sin(a)
            T.cyl(f"Sensorpaal_{k}", (x, y, 0), 0.05, 2.2, P.m("metaal"), seg=8, ol=0.01)
            T.box(f"Sensor_{k}", (x, y, 2.2), (0.3, 0.2, 0.25), T.toon("sensor_geel", (0.98, 0.75, 0.1)), bevel=0.03, ol=0.01)
            T.sphere(f"Sensorlampje_{k}", (x, y - 0.11, 2.35), 0.03, T.glow("sensorled", (1, 0.15, 0.1), 6), seg=8, ol=0)
        for k, d in enumerate((10, 25, 50, 100, 200)):
            T.cyl(f"Afstandsvlag_paal_{d}", (d, -6, 0), 0.04, 2.4, P.m("wit"), seg=6, ol=0.01)
            T.box(f"Afstandsvlag_{d}", (d + 0.45, -6, 1.9), (0.9, 0.03, 0.55), T.toon("vlag_oranje", (0.98, 0.45, 0.1)), bevel=0, ol=0.008)
            T.text(f"Afstand_{d}m", f"{d} m", (d, -6.05, 2.5), 0.4, P.m("zwart"), extrude=0.01)
        tent("Seismograaftent", (-6, 6, 0), rot=20, size=(4, 3, 2.4))
        sg = [T.box("Seismograaf_tafel", (0, 0, 0.0), (1.4, 0.7, 0.75), T.toon("tafel_klap", (0.85, 0.85, 0.82)), bevel=0.01, ol=0),
              T.box("Seismograaf", (0, 0, 0.75), (0.6, 0.4, 0.25), T.toon("apparaat", (0.25, 0.28, 0.32)), bevel=0.02, ol=0),
              T.box("Seismograaf_papier", (0, -0.25, 0.78), (0.5, 0.25, 0.01), P.m("wit"), rot=(10, 0, 0), bevel=0, ol=0)]
        T.merge("Seismograaf_opstelling", sg, ol=0.008).location = (-6, 6, 0)
        jeep("Jeep_test", (-12, 2, 0), rot=60)
        T.use_collection(None)
        T.character((0, 0, 0), rot_z=-90)
        cams = [T.camera("CAM_01_testterrein_wide", (-14, -16, 3.0), (20, 5, 1.0), lens=24),
                T.camera("CAM_02_sensor", (17, -4, 2.0), (20, 2, 2.0), lens=30),
                T.camera("CAM_03_seismograaf", (-4.5, 4.4, 1.4), (-6, 6, 0.9), lens=30)]
    else:
        base(lights_on=VAR == "basis_schemer", dusk=VAR == "basis_schemer")
        T.use_collection(None)
        T.character((0, -8.5, 0), rot_z=180)
        cams = [T.camera("CAM_01_basis_wide", (-35, -35, 8), (10, 20, 2), lens=24),
                T.camera("CAM_02_zandzakken", (0, 0, 1.6), (0, -30, 1.0), lens=28),
                T.camera("CAM_03_whiteboard", (10, 10.5, 1.6), (13, 14, 1.5), lens=30)]

else:  # nachtlucht
    mood = dict(T.MOODS["nacht"])
    mood.update(sky_top=(0.01, 0.015, 0.06), sky_horizon=(0.10, 0.12, 0.28), ground_glow=(0.08, 0.08, 0.16), sun_color=(0.70, 0.80, 1.0), sun_strength=0.45,
                sun_rot=(60, 0, -30), ambient=(0.10, 0.12, 0.22), shadow_tint=(0.22, 0.26, 0.48), lit_tint=(0.75, 0.82, 1.0), fog_color=(0.08, 0.10, 0.22),
                fog_start=100, fog_end=1500, fog_max=0.6, bloom=1.0)
    T.new_scene("Nachtlucht_woestijn", mood, samples=32)
    T.use_collection(T.collection("Woestijn"))
    desert_ground(size=4000)
    base(lights_on=True)
    T.use_collection(T.collection("Lucht"))
    stars = []
    for k in range(1500):
        az = rnd.uniform(0, 2 * math.pi)
        el = math.asin(rnd.uniform(0.03, 1.0))
        r = 2500
        stars.append((r * math.cos(el) * math.cos(az), r * math.cos(el) * math.sin(az), r * math.sin(el)))
    P.points_mesh("Sterren", stars, 2.2, T.glow("ster", (1.0, 1.0, 0.95), 6), seg=4)
    T.sphere("Volle_maan", (-1200, 1800, 900), 90, T.glow("maan", (0.95, 0.95, 0.88), 2.5), seg=32, ol=0)
    # gloed van de stad aan de horizon
    city = []
    for k in range(400):
        x = rnd.uniform(-900, -300)
        city.append((x, 2600 + rnd.uniform(-60, 60), rnd.uniform(0, 25)))
    P.points_mesh("Stadslichten", city, 3.0, T.glow("stadslicht", (1.0, 0.75, 0.4), 6), seg=4)
    T.sphere("Stadsgloed", (-600, 2700, -200), 500, T.glow("stadsgloed", (0.9, 0.5, 0.3), 0.6), scale=(1.4, 0.2, 0.5), seg=24, ol=0)
    T.use_collection(None)
    T.character((0, 0, 120), rot_z=180)  # vliegend boven de woestijn
    cams = [T.camera("CAM_01_vliegend", (6, -14, 122), (0, 40, 112), lens=24),
            T.camera("CAM_02_basis_onder", (40, -60, 150), (0, 30, 0), lens=24),
            T.camera("CAM_03_maan_horizon", (0, -6, 121), (-600, 2000, 500), lens=30)]

blend, renders = T.finish(OUT, VAR, cams)
print("KLAAR", blend, renders)
