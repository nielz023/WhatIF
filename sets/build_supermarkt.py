"""Set: Supermarkt. Video 1, dag 9. Fel en wit, felle verpakkingskleuren.

Gebruik:
    blender -b -P sets/build_supermarkt.py -- [binnen] [uitvoermap]
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402,F401
import bmesh  # noqa: E402
from mathutils import Vector  # noqa: E402
from lib import toon as T  # noqa: E402
from lib import props as P  # noqa: E402
from lib import interior as I  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
OUT = args[1] if len(args) > 1 else "/mnt/project-files/sets/10_supermarkt"
rnd = random.Random(9)

mood = dict(T.MOODS["binnen"])
mood.update(ambient=(0.50, 0.50, 0.52), shadow_tint=(0.62, 0.64, 0.78), lit_tint=(1.0, 1.0, 1.0), sun_rot=(45, 0, 160), sun_strength=1.0, fog_max=0.0)
T.new_scene("Supermarkt", mood, samples=32)

W, D, H = 30.0, 36.0, 4.5
T.use_collection(T.collection("Winkel"))
room = I.room("Supermarkt", W, D, H, wall_color=(0.94, 0.94, 0.92), floor_color=(0.9, 0.9, 0.88), skirting=False, hide=(),
              holes={"front": [(W / 2 - 3.0, W / 2 + 3.0, 0, 3.0), (2.0, 13.0, 0.6, 3.4)]})
room["floor"].data.materials[0] = T.pattern("winkelvloer", (0.93, 0.93, 0.91), (0.88, 0.89, 0.88), grout=(0.78, 0.78, 0.76), size=(0.6, 0.6), mortar=0.01)
room["ceiling"].data.materials[0] = T.toon("systeemplafond", (0.95, 0.95, 0.95))
# merkkleur-band langs de muren
for side, (loc, rz, L) in {"back": ((0, D / 2 - 0.03, 3.4), 0, W), "left": ((-W / 2 + 0.03, 0, 3.4), 90, D), "right": ((W / 2 - 0.03, 0, 3.4), 90, D)}.items():
    T.box(f"Merkband_{side}", loc, (L, 0.04, 0.5), T.toon("merkband_rood", (0.88, 0.12, 0.12)), rot=(0, 0, rz), bevel=0, ol=0)


def packs_mesh(name, items):
    """Veel verpakkingen (dozen/blikken) als één mesh per kleur, voor snelheid."""
    by_col = {}
    for kind, loc, size, col in items:
        by_col.setdefault((kind, col), []).append((loc, size))
    out = []
    for (kind, col), lst in by_col.items():
        me = bpy.data.meshes.new(name)
        bm = bmesh.new()
        for loc, size in lst:
            if kind == "doos":
                g = bmesh.ops.create_cube(bm, size=1.0)
                for v in g["verts"]:
                    v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2] + size[2] / 2)) + Vector(loc)
            else:
                g = bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=size[0] / 2, radius2=size[0] / 2, depth=size[2])
                for v in g["verts"]:
                    v.co = v.co + Vector((0, 0, size[2] / 2)) + Vector(loc)
        bm.to_mesh(me)
        bm.free()
        me.materials.append(T.toon(f"verpakking_{col}", col))
        o = bpy.data.objects.new(f"{name}_{kind}", me)
        T._link(o)
        out.append(o)
    return T.merge(name, out, ol=0.004)


PACK_COLS = [(0.95, 0.20, 0.15), (0.98, 0.75, 0.10), (0.15, 0.45, 0.95), (0.20, 0.75, 0.30), (0.95, 0.45, 0.10), (0.85, 0.25, 0.65),
             (0.95, 0.95, 0.95), (0.40, 0.25, 0.75), (0.10, 0.65, 0.75)]


def shelf_unit(name, x, y, length=10.0, kind="blik", rot=0):
    """Dubbelzijdig schap met 5 planken."""
    SH = T.toon("schap", (0.92, 0.92, 0.94))
    p = [T.box(name + "_rug", (0, 0, 0), (length, 0.08, 2.1), SH, bevel=0.01, ol=0),
         T.box(name + "_voet", (0, 0, 0), (length, 1.0, 0.15), T.toon("schap_voet", (0.35, 0.36, 0.40)), bevel=0.01, ol=0)]
    items = []
    for lvl in range(5):
        z = 0.15 + lvl * 0.42
        for s in (-1, 1):
            p.append(T.box(f"{name}_plank{lvl}{s}", (0, s * 0.27, z), (length, 0.5, 0.03), SH, bevel=0.005, ol=0))
            p.append(T.box(f"{name}_prijsstrip{lvl}{s}", (0, s * 0.52, z - 0.03), (length, 0.01, 0.05), T.toon("prijsstrip", (0.98, 0.85, 0.15)), bevel=0, ol=0))
            xx = -length / 2 + 0.1
            col = rnd.choice(PACK_COLS)
            while xx < length / 2 - 0.15:
                if kind == "ontbijtgranen":
                    w, h = 0.22, rnd.choice((0.3, 0.34))
                    if rnd.random() < 0.15:
                        col = rnd.choice(PACK_COLS)
                    items.append(("doos", (xx + w / 2, s * 0.27, z + 0.03), (w, 0.08, h), col))
                    xx += w + 0.02
                else:
                    w, h = 0.09, rnd.choice((0.12, 0.16))
                    if rnd.random() < 0.08:
                        col = rnd.choice(PACK_COLS)
                    for d in (-0.1, 0.1):
                        items.append(("blik", (xx + w / 2, s * 0.27 + d, z + 0.03), (w, w, h), col))
                    xx += w + 0.012
    o = T.merge(name, p, ol=0.01)
    pk = packs_mesh(name + "_waren", items)
    pk.parent = o
    o.location = (x, y, 0)
    o.rotation_euler.z = math.radians(rot)
    return o


T.use_collection(T.collection("Schappen"))
aisles = []
for k, x in enumerate((-9, -4.5, 0, 4.5, 9)):
    shelf_unit(f"Schap_{k + 1}", x, 3.0, length=16.0, kind="ontbijtgranen" if k == 2 else "blik", rot=90)
    T.box(f"Gangbord_{k + 1}", (x, -5.5, 2.6), (1.6, 0.06, 0.5), T.toon("gangbord", (0.15, 0.45, 0.85)), bevel=0.02, ol=0.006)
    T.text(f"Gangnummer_{k + 1}", ["CANS", "SOUP", "CEREAL", "SNACKS", "DRINKS"][k], (x, -5.54, 2.68), 0.22, P.m("wit"), extrude=0.01)
# koelingen langs de achterwand
for k in range(6):
    x = -12.5 + k * 5
    fr = [T.box(f"Koeling_{k}_kast", (0, 0, 0), (4.8, 1.0, 2.2), T.toon("koeling", (0.85, 0.88, 0.92)), bevel=0.02, ol=0),
          T.box(f"Koeling_{k}_glas", (0, -0.52, 0.15), (4.6, 0.03, 1.9), T.glass("koelglas", (0.78, 0.9, 1.0), alpha=0.25), bevel=0, ol=0),
          T.box(f"Koeling_{k}_licht", (0, -0.2, 2.0), (4.6, 0.4, 0.05), T.glow("koellicht", (0.9, 0.97, 1.0), 2.5), bevel=0, ol=0)]
    items = []
    for lvl in range(4):
        z = 0.2 + lvl * 0.45
        fr.append(T.box(f"Koeling_{k}_plank{lvl}", (0, 0, z), (4.6, 0.9, 0.02), P.m("metaal"), bevel=0, ol=0))
        xx = -2.2
        while xx < 2.2:
            col = PACK_COLS[(k + lvl) % 9] if rnd.random() < 0.8 else rnd.choice(PACK_COLS)
            items.append(("doos" if lvl % 2 else "blik", (xx + 0.06, -0.1, z + 0.02), (0.1, 0.1, 0.24), col))
            xx += 0.14
    o = T.merge(f"Koeling_{k + 1}", fr, ol=0.01)
    packs_mesh(f"Koeling_{k + 1}_waren", items).parent = o
    o.location = (x, D / 2 - 0.6, 0)
# kassa's
T.use_collection(T.collection("Kassa's"))
for k in range(4):
    x = -10 + k * 4
    ck = [T.box(f"Kassa_{k}_band", (0, 0, 0), (0.9, 3.0, 0.9), T.toon("kassameubel", (0.30, 0.32, 0.38)), bevel=0.02, ol=0),
          T.box(f"Kassa_{k}_rubber", (0, 0.3, 0.9), (0.6, 2.2, 0.02), P.m("zwart"), bevel=0, ol=0),
          T.box(f"Kassa_{k}_scherm", (-0.35, -1.0, 0.9), (0.06, 0.35, 0.3), P.m("zwart"), bevel=0.01, ol=0),
          T.cyl(f"Kassa_{k}_paal", (0.4, -1.4, 0.9), 0.03, 1.2, P.m("metaal"), seg=8, ol=0),
          T.box(f"Kassa_{k}_nummer", (0.4, -1.4, 2.1), (0.4, 0.06, 0.4), T.glow("kassalampje", (0.3, 0.9, 0.4), 2.5), bevel=0.03, ol=0)]
    T.merge(f"Kassa_{k + 1}", ck, ol=0.01).location = (x, -D / 2 + 6.5, 0)
    T.text(f"Kassanummer_{k + 1}", str(k + 1), (x + 0.4, -D / 2 + 6.45 - 1.4, 2.18), 0.22, P.m("wit"), extrude=0.01)


def cart(name, loc, rot=0):
    M = P.m("metaal")
    p = [T.box(name + "_mand", (0, 0, 0.55), (0.55, 0.9, 0.45), T.glass("karmand", (0.75, 0.78, 0.82), alpha=0.55), bevel=0.02, ol=0),
         T.box(name + "_bodem", (0, 0, 0.55), (0.55, 0.9, 0.02), M, bevel=0, ol=0),
         T.box(name + "_handvat", (0, 0.5, 1.05), (0.55, 0.05, 0.05), T.toon("kar_handvat", (0.88, 0.12, 0.12)), bevel=0.02, ol=0),
         T.box(name + "_onderstel", (0, 0, 0.12), (0.5, 0.85, 0.03), M, bevel=0, ol=0)]
    for x in (-0.22, 0.22):
        for y in (-0.38, 0.38):
            p.append(T.cyl(f"{name}_wiel{x}{y}", (x, y, 0.06), 0.06, 0.04, P.m("zwart"), rot=(0, 90, 0), seg=10, ol=0))
            p.append(T.cyl(f"{name}_stang{x}{y}", (x, y, 0.1), 0.012, 0.47, M, seg=6, ol=0))
    o = T.merge(name, p, ol=0.006)
    o.location = loc
    o.rotation_euler.z = math.radians(rot)
    return o


for k in range(6):
    cart(f"Winkelwagen_rij_{k + 1}", (11.5, -D / 2 + 2.0 + k * 0.32, 0), rot=0)
cart("Winkelwagen_held", (1.2, -3.0, 0), rot=-15)
# schuifdeuren + parkeerplaats buiten
T.use_collection(T.collection("Ingang en buiten"))
for k, x in enumerate((-1.2, 1.2)):
    T.box(f"Schuifdeur_{k}", (x + 0.0, -D / 2, 0), (2.3, 0.05, 2.95), T.glass("schuifdeur", (0.75, 0.9, 1.0), alpha=0.3), bevel=0, ol=0.006)
P.ground("Parkeerplaats", (300, 300), (0.30, 0.30, 0.33), z=-0.03)
for k in range(10):
    T.plane(f"Parkeervak_{k}", (-12 + k * 3, -D / 2 - 9, 0.0), (0.12, 5), P.m("wit"))
car_cols = [(0.10, 0.35, 0.80), (0.85, 0.15, 0.12), (0.92, 0.92, 0.92), (0.95, 0.70, 0.10), (0.30, 0.60, 0.35)]
for k, x in enumerate((-10.5, -4.5, 1.5, 7.5)):
    P.car(f"Auto_parkeerplaats_{k}", (x, -D / 2 - 9, 0), rot=90, color=car_cols[k])
for k, x in enumerate((-20, 22)):
    P.tree(f"Boom_parkeerplaats_{k}", (x, -D / 2 - 14, 0), h=7, r=2.5, seed=k)
# TL-armaturen
T.use_collection(T.collection("Licht"))
tl = []
for x in range(-12, 13, 4):
    for y in range(-14, 16, 5):
        tl.append(T.box(f"Armatuur_{x}_{y}", (x, y, H - 0.06), (1.2, 0.3, 0.05), T.glow("armatuur", (1.0, 1.0, 0.98), 3.5), bevel=0, ol=0))
T.merge("Armaturen", tl, ol=0)
T.area_light("Winkellicht", (0, 0, H - 0.1), (0, 0, 0), size=(W - 2, D - 2), color=(1.0, 1.0, 0.98), energy=4500)

T.use_collection(None)
T.character((0.6, -2.4, 0), rot_z=-10)
cams = [
    T.camera("CAM_01_winkel_wide", (13, -16.5, 3.4), (-3, 6, 0.8), lens=20),
    T.camera("CAM_02_gang_ontbijtgranen", (-2.25, -6.5, 1.5), (-2.25, 8, 1.1), lens=26),
    T.camera("CAM_03_kassa", (-12.5, -D / 2 + 3.0, 1.6), (-6, -D / 2 + 7.5, 1.0), lens=24),
    T.camera("CAM_04_parkeerplaats", (14, -D / 2 - 16, 2.0), (2, -D / 2, 2.0), lens=24),
]
T.box("Gevelbord", (7.5, -D / 2 - 0.1, 3.6), (9, 0.2, 0.8), T.toon("merkband_rood", (0.88, 0.12, 0.12)), bevel=0.05, ol=0.01)
T.text("Gevelnaam", "SUPERMARKET", (7.5, -D / 2 - 0.22, 3.75), 0.55, P.m("wit"), extrude=0.03)
blend, renders = T.finish(OUT, "supermarkt", cams)
print("KLAAR", blend, renders)
