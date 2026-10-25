"""Set: Pretpark met de achtbaan THE TITAN.
Video 1, cold open (dag 16, zonsondergang) en dag 16 overdag.

Gebruik:
    blender -b -P sets/build_pretpark.py -- [zonsondergang|dag] [uitvoermap]
of  python3 sets/build_pretpark.py zonsondergang /pad/naar/uitvoer   (met pip-pakket bpy)
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402,F401  (eerst bpy, dan mathutils)
from mathutils import Vector, Matrix  # noqa: E402
from lib import toon as T  # noqa: E402
from lib import props as P  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
MOOD = args[0] if args else "zonsondergang"
OUT = args[1] if len(args) > 1 else "/mnt/project-files/sets/01_pretpark"
LIGHTS_ON = MOOD != "dag"

T.new_scene("Pretpark_" + MOOD, T.MOODS[MOOD], samples=32)

RED = T.toon("titan_rood", (0.80, 0.06, 0.04))
CONCRETE = T.toon("beton", (0.63, 0.62, 0.59))
STEEL = T.toon("staal_donker", (0.20, 0.21, 0.24))

# ---------------------------------------------------------------------------
# Baan van THE TITAN: gesloten Catmull-Rom spline (x, y, z) in meters.
# Rijrichting: station -> optakeling (lift hill) -> grote afdaling -> heuvels ->
# keerpunt -> laatste afdaling -> rechte stuk waar hij staat -> station.
# ---------------------------------------------------------------------------
CTRL = [
    (0, -12, 3), (-20, -12, 3), (-34, -12, 4.5), (-46, -12, 11), (-62, -12, 28), (-78, -12, 45),
    (-88, -10, 47), (-96, -4, 43), (-100, 6, 28), (-96, 18, 8), (-84, 28, 6),
    (-66, 33, 12), (-50, 34, 24), (-34, 34, 14), (-16, 32, 7), (2, 30, 9), (20, 28, 19),
    (38, 27, 10), (60, 25, 6), (84, 22, 9), (100, 12, 16), (104, -2, 22), (96, -12, 26),
    (78, -12, 25), (62, -12, 22), (52, -12, 12), (44, -12, 4), (34, -12, 3), (18, -12, 3),
]


def catmull(pts, samples_per_seg=40):
    out = []
    n = len(pts)
    P_ = [Vector(p) for p in pts]
    for i in range(n):
        p0, p1, p2, p3 = P_[i - 1], P_[i], P_[(i + 1) % n], P_[(i + 2) % n]
        for k in range(samples_per_seg):
            t = k / samples_per_seg
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    return out


def resample(pts, step):
    """Punten op gelijke afstand langs de gesloten lijn."""
    res = [pts[0]]
    acc = 0.0
    ring = pts + [pts[0]]
    for a, b in zip(ring, ring[1:]):
        seg = (b - a).length
        while acc + seg >= step:
            t = (step - acc) / seg
            a = a.lerp(b, t)
            res.append(a)
            seg = (b - a).length
            acc = 0.0
        acc += seg
    return res


path = resample(catmull(CTRL), 0.75)
N = len(path)


def frame(i):
    """Raaklijn, zijwaarts en omhoog op punt i."""
    t = (path[(i + 1) % N] - path[i - 1]).normalized()
    side = t.cross(Vector((0, 0, 1))).normalized()
    up = side.cross(t).normalized()
    return t, side, up


coll_track = T.collection("Titan achtbaan")
T.use_collection(coll_track)

# Middellijn als curve: handig voor een Follow Path-constraint op de trein.
cu_obj = T.tube("Titan_pad (voor animatie)", [tuple(p) for p in path], 0.0, RED, closed=True)
cu_obj.hide_render = True

GAUGE = 0.62
rails_l, rails_r, spine = [], [], []
for i in range(N):
    t, s, u = frame(i)
    rails_l.append(tuple(path[i] + s * GAUGE + u * 0.0))
    rails_r.append(tuple(path[i] - s * GAUGE))
    spine.append(tuple(path[i] - u * 0.55))
for nm, pts, r in (("Titan_rail_links", rails_l, 0.075), ("Titan_rail_rechts", rails_r, 0.075), ("Titan_ruggengraat", spine, 0.22)):
    o = T.tube(nm, pts, r, RED, closed=True)
    o = T.to_mesh(o)
    T.outline(o, 0.03)

# Dwarsliggers: één mesh
import bmesh  # noqa: E402
import bpy  # noqa: E402

me = bpy.data.meshes.new("Titan_dwarsliggers")
bm = bmesh.new()
for i in range(0, N, 2):
    t, s, u = frame(i)
    M = Matrix((s, t, u)).transposed()
    g = bmesh.ops.create_cube(bm, size=1.0)
    for v in g["verts"]:
        lc = Vector((v.co.x * GAUGE * 2.2, v.co.y * 0.16, v.co.z * 0.14))
        v.co = path[i] + M @ lc - u * 0.12
    # verbinding naar ruggengraat
    g = bmesh.ops.create_cube(bm, size=1.0)
    for v in g["verts"]:
        lc = Vector((v.co.x * 0.12, v.co.y * 0.12, v.co.z * 0.45))
        v.co = path[i] + M @ lc - u * 0.35
bm.to_mesh(me)
bm.free()
ties = bpy.data.objects.new("Titan_dwarsliggers", me)
me.materials.append(STEEL)
T._link(ties)

# Betonnen pilaren met rode dwarsbalk; elk ~9 m
pillar_parts, beam_parts = [], []
HERO_I = min(range(N), key=lambda i: (path[i] - Vector((30, -12, 3))).length)
for i in range(0, N, 12):
    p = path[i]
    if p.z < 1.5:
        continue
    t, s, u = frame(i)
    top = p.z - 0.85
    r = 0.38 + p.z * 0.008
    pillar_parts.append(T.cyl(f"pilaar_{i}", (p.x, p.y, 0), r, top, CONCRETE, seg=16, ol=0))
    pillar_parts.append(T.cyl(f"pilaarvoet_{i}", (p.x, p.y, 0), r * 1.9, 0.5, CONCRETE, seg=16, ol=0, r2=r * 1.3))
    yaw = math.degrees(math.atan2(t.y, t.x))
    beam_parts.append(T.box(f"balk_{i}", (p.x, p.y, top - 0.15), (0.5, GAUGE * 2.6, 0.45), RED, rot=(0, 0, yaw), ol=0))
T.merge("Titan_pilaren_beton", pillar_parts, ol=0.03)
T.merge("Titan_dwarsbalken", beam_parts, ol=0.02)

# Bouten op het rechte stuk bij de held (close-ups: "ping, ping, ping")
bolts = []
for i in range(HERO_I - 30, HERO_I + 30, 2):
    t, s, u = frame(i)
    for side in (1, -1):
        q = path[i] + s * GAUGE * side * 1.05 - u * 0.12
        bolts.append(T.cyl(f"bout_{i}_{side}", tuple(q), 0.045, 0.1, T.toon("bout", (0.75, 0.75, 0.72)), seg=6, ol=0))
T.merge("Titan_bouten (close-up)", bolts, ol=0.008)

# ---------------------------------------------------------------------------
# Trein: 6 wagens x 4 stoelen = 24 mensen. Staat bovenaan de optakeling.
# ---------------------------------------------------------------------------
coll_train = T.collection("Titan trein")
T.use_collection(coll_train)
CAR_BODY = T.toon("trein_blauw", (0.06, 0.22, 0.70))
CAR_TRIM = T.toon("trein_geel", (0.98, 0.72, 0.06))
SEAT = T.toon("stoel_zwart", (0.07, 0.07, 0.09))
LIFT_TOP = min(range(N), key=lambda i: (path[i] - Vector((-74, -12, 41))).length)


def build_car(name, front=False):
    p = [T.box(name + "_bak", (0, 0, 0.0), (2.0, 1.55, 0.75), CAR_BODY, bevel=0.15, ol=0),
         T.box(name + "_rand", (0, 0, 0.7), (2.05, 1.6, 0.12), CAR_TRIM, bevel=0.05, ol=0)]
    for k, x in enumerate((0.45, -0.45)):
        for y in (0.38, -0.38):
            p.append(T.box(f"{name}_stoel{k}{y}", (x, y, 0.35), (0.35, 0.6, 0.85), SEAT, bevel=0.1, ol=0))
        p.append(T.tube(f"{name}_beugel{k}", [(x + 0.25, 0.7, 0.9), (x + 0.4, 0.7, 1.15), (x + 0.4, -0.7, 1.15), (x + 0.25, -0.7, 0.9)], 0.04, CAR_TRIM))
    if front:
        p.append(T.box(name + "_neus", (1.1, 0, 0.0), (0.4, 1.5, 0.6), CAR_TRIM, bevel=0.2, ol=0))
    p = [T.to_mesh(o) if o.type == "CURVE" else o for o in p]
    return T.merge(name, p, ol=0.025)


cars = []
for k in range(6):
    i = (LIFT_TOP - k * 3) % N
    t, s, u = frame(i)
    c = build_car(f"Trein_wagen_{k + 1}", front=(k == 0))
    M = Matrix((t, s, u)).transposed().to_4x4()
    M.translation = path[i] + u * 0.25
    c.matrix_world = M
    cars.append(c)

# ---------------------------------------------------------------------------
# Station met THE TITAN-bord en wachtrijrelingen
# ---------------------------------------------------------------------------
coll_park = T.collection("Pretpark")
T.use_collection(coll_park)
T.box("Station_perron", (-10, -14.6, 0), (24, 3.2, 2.3), T.toon("perron", (0.85, 0.80, 0.70)))
T.box("Station_perron2", (-10, -9.4, 0), (24, 3.2, 2.3), T.toon("perron", (0.85, 0.80, 0.70)))
for x in range(-21, 2, 5):
    for y in (-16, -8):
        T.cyl(f"Station_paal_{x}_{y}", (x, y, 2.3), 0.15, 4.2, RED, seg=12)
T.box("Station_dak", (-10, -12, 6.5), (26, 10, 0.5), T.toon("dak_wit", (0.92, 0.90, 0.86)), bevel=0.15, ol=0.03)
T.box("Station_dakrand", (-10, -12, 6.3), (26.4, 10.4, 0.3), RED, bevel=0.08, ol=0.02)
T.box("Bord_achtergrond", (-10, -16.9, 7.0), (14, 0.5, 2.6), T.toon("bord_geel", (0.98, 0.72, 0.06)), bevel=0.2, ol=0.04)
T.text("Bord_THE_TITAN", "THE TITAN", (-10, -17.25, 7.3), 2.0, RED, extrude=0.18, ol=0.035)
# wachtrij voor het station
Q = []
for r in range(5):
    y = -20 - r * 1.4
    Q.append([(-22, y), (-2, y)] if r % 2 == 0 else [(-2, y), (-22, y)])
for r, seg in enumerate(Q):
    P.railing(f"Wachtrij_reling_{r}", [(*seg[0], 0), (*seg[1], 0)], h=1.0, posts=2.5)
T.box("Bord_wachttijd", (-24, -21, 0), (0.15, 1.2, 2.4), T.toon("bord_blauw", (0.08, 0.28, 0.75)), bevel=0.05)

# ---------------------------------------------------------------------------
# Reuzenrad
# ---------------------------------------------------------------------------
coll_ferris = T.collection("Reuzenrad")
T.use_collection(coll_ferris)
R, HUB = 22.0, 25.0
WHITE = T.toon("rad_wit", (0.93, 0.92, 0.90))
fparts = []
for side in (1.6, -1.6):
    fparts.append(T.torus(f"rad_ring_{side}", (side, 0, HUB), R, 0.28, WHITE, rot=(0, 90, 0), seg=96, seg2=8, ol=0))
    fparts.append(T.torus(f"rad_ring_in_{side}", (side, 0, HUB), R * 0.55, 0.16, WHITE, rot=(0, 90, 0), seg=64, seg2=8, ol=0))
    for k in range(16):
        a = 2 * math.pi * k / 16
        fparts.append(T.to_mesh(T.tube(f"spaak_{side}_{k}", [(side, 0, HUB), (side, math.cos(a) * R, HUB + math.sin(a) * R)], 0.09, WHITE)))
fparts.append(T.cyl("rad_as", (-2.2, 0, HUB), 0.8, 4.4, STEEL, rot=(0, 90, 0), seg=20, ol=0))
for side in (2.6, -2.6):
    for fy in (1, -1):
        fparts.append(T.to_mesh(T.tube(f"rad_poot_{side}_{fy}", [(side, fy * 13, 0), (side * 0.9, 0, HUB)], 0.35, WHITE)))
wheel = T.merge("Reuzenrad_frame", fparts, ol=0.05)
gcols = [(0.95, 0.30, 0.25), (0.98, 0.72, 0.08), (0.15, 0.55, 0.90), (0.30, 0.75, 0.30), (0.85, 0.35, 0.75), (1.0, 0.55, 0.15)]
gondolas = []
for k in range(16):
    a = 2 * math.pi * k / 16 + 0.1
    y, z = math.cos(a) * R, HUB + math.sin(a) * R
    gm = T.toon(f"gondel{k % 6}", gcols[k % 6])
    g = [T.cyl(f"gondel_{k}_bak", (0, y, z - 3.2), 1.25, 1.4, gm, seg=16, ol=0, bevel=0.1),
         T.cyl(f"gondel_{k}_dak", (0, y, z - 1.3), 1.4, 0.7, gm, r2=0.2, seg=16, ol=0),
         T.cyl(f"gondel_{k}_glas", (0, y, z - 1.85), 1.15, 0.6, T.toon("gondel_glas", (0.65, 0.85, 0.95)), seg=16, ol=0),
         T.cyl(f"gondel_{k}_stang", (0, y, z - 0.7), 0.06, 0.7, STEEL, seg=6, ol=0)]
    gondolas.append(T.merge(f"Gondel_{k + 1}", g, ol=0.03))
if LIGHTS_ON:
    pts = []
    for side in (1.95, -1.95):
        for k in range(96):
            a = 2 * math.pi * k / 96
            pts.append((side, math.cos(a) * R, HUB + math.sin(a) * R))
        for k in range(16):
            a = 2 * math.pi * k / 16
            for j in range(1, 10):
                pts.append((side, math.cos(a) * R * j / 10, HUB + math.sin(a) * R * j / 10))
    gondolas.append(P.points_mesh("Reuzenrad_lampjes", pts, 0.12, T.glow("rad_lampjes", (1.0, 0.78, 0.45), 5)))
T.group("Reuzenrad", [wheel] + gondolas, loc=(-55, 70, 0), rot=(0, 0, -35))

# ---------------------------------------------------------------------------
# Botsauto's
# ---------------------------------------------------------------------------
coll_bump = T.collection("Botsauto's")
T.use_collection(coll_bump)
bp = [T.box("Botsauto_vloer", (0, 0, 0), (20, 14, 0.25), T.toon("botsvloer", (0.22, 0.22, 0.26)), bevel=0.05),
      T.box("Botsauto_rand", (0, 0, 0), (20.6, 14.6, 0.45), T.toon("botsrand", (0.98, 0.72, 0.06)), bevel=0.08)]
for x in (-9.8, 0, 9.8):
    for y in (-6.8, 6.8):
        bp.append(T.cyl(f"Botsauto_paal_{x}_{y}", (x, y, 0), 0.18, 5.0, T.toon("paars", (0.42, 0.16, 0.65)), seg=12))
bp.append(T.box("Botsauto_dak", (0, 0, 5.0), (21, 15, 0.6), T.toon("botsdak", (0.42, 0.16, 0.65)), bevel=0.1, ol=0.03))
bp.append(T.box("Botsauto_plafond_gaas", (0, 0, 4.9), (19.6, 13.6, 0.05), T.toon("gaas", (0.4, 0.4, 0.45)), bevel=0, ol=0))
for nm, (x, y, rot, w) in {"voor": (0, -7.6, 0, 21), "achter": (0, 7.6, 180, 21), "links": (-10.6, 0, 90, 15), "rechts": (10.6, 0, -90, 15)}.items():
    a = P.striped_awning(f"Botsauto_rand_{nm}", (0, 0, 0), w, 0.8, colors=("rood", "wit"), stripes=int(w / 1.2), tilt=60)
    a.location = (x, y, 5.0)
    a.rotation_euler = (math.radians(-60), 0, math.radians(rot))
T.text("Botsauto_bord", "BUMPER CARS", (0, -7.65, 5.45), 1.1, T.toon("bord_wit", (0.96, 0.95, 0.92)), extrude=0.08, ol=0.02)
bcols = [(0.9, 0.12, 0.10), (0.10, 0.45, 0.90), (0.98, 0.72, 0.08), (0.15, 0.70, 0.30), (0.95, 0.40, 0.70), (1.0, 0.5, 0.1)]
for k, (x, y, r) in enumerate([(-6, -3, 20), (-2, 2, 140), (3, -1, 250), (6, 4, 60), (-5, 4, 300), (2, -4.5, 10)]):
    bm_ = T.toon(f"botsauto{k}", bcols[k])
    c = [T.box(f"bc{k}_bak", (0, 0, 0.25), (1.9, 1.2, 0.45), bm_, bevel=0.2, ol=0),
         T.torus(f"bc{k}_bumper", (0, 0, 0.32), 1.05, 0.13, T.toon("rubber", (0.08, 0.08, 0.08)), seg=32, seg2=8, ol=0),
         T.box(f"bc{k}_stoel", (-0.3, 0, 0.6), (0.5, 0.8, 0.6), SEAT, bevel=0.12, ol=0),
         T.cyl(f"bc{k}_stang", (-0.75, 0, 0.6), 0.04, 4.3, STEEL, seg=6, ol=0)]
    car = T.merge(f"Botsauto_{k + 1}", c, ol=0.02)
    car.location = (x, y, 0.25)
    car.rotation_euler.z = math.radians(r)
    car.scale = (1.0, 1.0, 1.0)
    bp.append(car)
T.group("Botsauto's", bp, loc=(26, 6, 0), rot=(0, 0, 8))

# ---------------------------------------------------------------------------
# Suikerspinkraam en ballonnenverkoper
# ---------------------------------------------------------------------------
coll_stand = T.collection("Kramen")
T.use_collection(coll_stand)
PINK = T.toon("suikerspin_roze", (0.98, 0.55, 0.75))
sp = [T.box("Kraam_body", (0, 0, 0), (3.6, 2.2, 2.4), T.toon("kraam_wit", (0.95, 0.92, 0.88)), bevel=0.06),
      T.box("Kraam_streep", (0, -1.11, 0.4), (3.62, 0.02, 0.35), PINK, bevel=0, ol=0),
      T.box("Kraam_toonbank", (0, -1.35, 1.0), (3.8, 0.5, 0.1), T.toon("toonbank", (0.98, 0.72, 0.06)), bevel=0.03),
      T.box("Kraam_dak", (0, 0, 3.6), (3.9, 2.5, 0.25), PINK, bevel=0.06),
      T.box("Kraam_bord", (0, -0.6, 3.85), (3.2, 0.2, 0.9), T.toon("bord_lichtblauw", (0.45, 0.78, 0.98)), bevel=0.08)]
sp.append(T.text("Kraam_tekst", "COTTON CANDY", (0, -0.72, 4.05), 0.42, T.toon("tekst_roze", (0.9, 0.2, 0.5)), extrude=0.04))
aw = P.striped_awning("Kraam_luifel", (0, -1.1, 2.55), 3.9, 1.1, colors=("roze", "wit"), stripes=7, tilt=22, drop=0.22)
sp.append(aw)
sp.append(T.cyl("Kraam_machine", (0.9, -0.2, 1.05), 0.45, 0.35, T.toon("machine", (0.85, 0.87, 0.9)), seg=20))
for k in range(6):
    x = -1.4 + k * 0.38
    col = PINK if k % 2 == 0 else T.toon("suikerspin_blauw", (0.55, 0.78, 0.98))
    sp.append(T.cyl(f"Spin_stok_{k}", (x, -1.35, 1.05), 0.012, 0.55, T.toon("stokje", (0.95, 0.92, 0.85)), seg=6, ol=0))
    sp.append(T.sphere(f"Spin_{k}", (x, -1.35, 1.75), 0.2, col, scale=(1, 1, 1.25), seg=14, ol=0.01))
T.group("Suikerspinkraam", sp, loc=(6, -20.2, 0), rot=(0, 0, -12))

bl = [T.box("Ballonkar_bak", (0, 0, 0.5), (1.2, 0.8, 0.6), T.toon("kar_rood", (0.85, 0.12, 0.10)), bevel=0.06)]
for x in (-0.45, 0.45):
    bl.append(T.cyl(f"Ballonkar_wiel_{x}", (x, 0.45, 0.28), 0.28, 0.08, P.m("zwart"), rot=(90, 0, 0), seg=14, ol=0.01))
import random  # noqa: E402
rnd = random.Random(4)
ball_cols = [(0.95, 0.15, 0.15), (0.98, 0.75, 0.05), (0.15, 0.55, 0.95), (0.25, 0.80, 0.30), (0.95, 0.45, 0.75), (0.6, 0.3, 0.9)]
for k in range(14):
    q = Vector((rnd.uniform(-0.9, 0.9), rnd.uniform(-0.7, 0.7), rnd.uniform(3.0, 4.2)))
    bl.append(T.sphere(f"Ballon_{k}", tuple(q), 0.32, T.toon(f"ballon{k % 6}", ball_cols[k % 6]), scale=(1, 1, 1.2), seg=14, ol=0.012))
    bl.append(T.to_mesh(T.tube(f"Ballon_touw_{k}", [(0, 0, 1.1), tuple(q - Vector((0, 0, 0.38)))], 0.006, P.m("wit"))))
T.group("Ballonnenverkoper", bl, loc=(-6, -29, 0), rot=(0, 0, 20))

# ---------------------------------------------------------------------------
# Paden, lichtsnoeren, lantaarns, bankjes, bomen, achtergrond
# ---------------------------------------------------------------------------
coll_env = T.collection("Omgeving")
T.use_collection(coll_env)
P.ground("Gras", (900, 900), (0.24, 0.50, 0.18))
T.plane("Hoofdpad", (10, -27, 0.02), (150, 9), T.toon("pad", (0.80, 0.70, 0.58)))
T.plane("Zijpad", (-30, 10, 0.02), (8, 80), T.toon("pad", (0.80, 0.70, 0.58)))
T.plane("Plein_botsauto", (26, 6, 0.015), (34, 26), T.toon("pad", (0.80, 0.70, 0.58)))
T.plane("Plein_rad", (-55, 70, 0.015), (40, 34), T.toon("pad", (0.80, 0.70, 0.58)), rot=(0, 0, -35))

poles = []
for k, x in enumerate(range(-40, 61, 10)):
    for y in (-22.6, -31.4):
        poles.append((x, y))
        P.lamp_post(f"Lantaarn_{x}_{y}", (x, y, 0), h=4.6, on=LIGHTS_ON)
for y in (-22.6, -31.4):
    anchors = [(x, y, 4.6) for x in range(-40, 61, 10)]
    P.string_lights(f"Lichtsnoer_{y}", anchors, sag=0.9, on=LIGHTS_ON)
# kriskras over het pad
zig = []
for k, x in enumerate(range(-40, 61, 10)):
    zig.append((x, -22.6 if k % 2 == 0 else -31.4, 4.6))
P.string_lights("Lichtsnoer_kriskras", zig, sag=1.2, on=LIGHTS_ON)
for k, x in enumerate(range(-35, 60, 20)):
    P.bench(f"Bankje_{k}", (x, -32.5, 0), rot=180)
    P.bin_(f"Prullenbak_{k}", (x + 2, -32.6, 0))

trees = [(-74, -46), (-62, -52), (60, -40), (78, -34), (-110, 30), (-118, 70), (-80, 100), (-20, 105), (30, 100),
         (80, 80), (120, 40), (130, -20), (-130, -20), (12, 60), (-8, 70), (50, 55), (95, 55), (-100, -50), (110, -60)]
for k, (x, y) in enumerate(trees):
    P.tree(f"Boom_{k}", (x, y, 0), h=7 + (k % 3) * 1.5, r=3 + (k % 2), seed=k, kind="rond" if k % 4 else "den")

# Verre achtergrond: heuvels en een tweede attractie (silhouet-achtig door de waas)
for k, (x, y, s) in enumerate([(-250, 300, 120), (-60, 340, 90), (150, 320, 140), (330, 200, 110), (-340, 120, 100)]):
    T.sphere(f"Heuvel_{k}", (x, y, -s * 0.55), s, T.toon("heuvel", (0.20, 0.42, 0.18)), scale=(1.6, 1, 0.6), seg=32, ol=0)
tower = [T.cyl("Valtoren_mast", (0, 0, 0), 1.6, 62, T.toon("toren_wit", (0.9, 0.9, 0.92)), seg=16, ol=0),
         T.cyl("Valtoren_ring", (0, 0, 18), 3.2, 2.2, T.toon("toren_ring", (0.15, 0.45, 0.95)), seg=24, ol=0),
         T.cyl("Valtoren_top", (0, 0, 62), 2.2, 4, RED, r2=0.4, seg=16, ol=0)]
T.group("Valtoren (achtergrond)", [T.merge("Valtoren", tower, ol=0.06)], loc=(70, 120, 0))
if LIGHTS_ON:
    T.sphere("Valtoren_flitser", (70, 120, 66.3), 0.5, T.glow("flits_rood", (1, 0.15, 0.1), 8), ol=0)

# ---------------------------------------------------------------------------
# Hoofdpersonage (schaal) op het rechte stuk na de laatste afdaling
# ---------------------------------------------------------------------------
T.use_collection(None)
hp = path[HERO_I]
T.character((hp.x, hp.y, hp.z + 0.05), rot_z=90)

# ---------------------------------------------------------------------------
# Camera's
# ---------------------------------------------------------------------------
cams = [
    T.camera("CAM_01_wide_park", (78, -78, 16), (-10, 10, 14), lens=24),
    T.camera("CAM_02_lift_hill", (-48, -40, 2.0), (-74, -12, 36), lens=28),
    T.camera("CAM_03_held_op_baan", (hp.x - 9, hp.y - 1.5, hp.z + 1.2), (hp.x + 22, hp.y + 0.5, 16), lens=24),
    T.camera("CAM_04_pilaar_laag", (hp.x - 2, hp.y - 6, 0.6), (hp.x + 3, hp.y, 4.0), lens=20),
    T.camera("CAM_05_kraampjes", (-12, -40, 3.0), (8, -24, 3.0), lens=30),
]
if LIGHTS_ON:
    T.point_light("Kraam_lamp", (6, -22.5, 3.2), energy=150)

blend, renders = T.finish(OUT, "pretpark_" + MOOD, cams)
print("KLAAR", blend, renders)
