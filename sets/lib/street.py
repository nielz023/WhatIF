"""Buitenprops voor de woonwijk: rijtjeshuizen, brievenbus, bushalte,
legertruck, helikopter, springkussen."""
import math
from mathutils import Vector
from . import toon as T
from . import props as P

FRAME = (0.95, 0.95, 0.93)


def terraced_house(name, x, facade_y, width=6.0, depth=9.0, color=(0.72, 0.38, 0.26), door_color=(0.15, 0.35, 0.75),
                   facing=-1, lit=False, broken=False, roof_color=(0.30, 0.18, 0.16)):
    """Rijtjeshuis; gevel op facade_y en kijkt naar -y (facing=-1) of +y (facing=1).
    Nulpunt = midden van de gevel op de grond."""
    wall = T.toon(f"gevel_{name}", color)
    h = 6.0
    parts = [T.box(name + "_romp", (0, depth / 2, 0), (width - 0.06, depth, h), wall, bevel=0.03, ol=0)]
    # nok evenwijdig aan de straat
    roof = T.mesh_from(name + "_dak", [(-width / 2, -0.35, h), (width / 2, -0.35, h), (width / 2, depth / 2, h + 3.2), (-width / 2, depth / 2, h + 3.2),
                                       (-width / 2, depth + 0.35, h), (width / 2, depth + 0.35, h)],
                       [(0, 1, 2, 3), (3, 2, 5, 4), (0, 3, 4), (1, 5, 2)], T.toon(f"dakpannen_{name}", roof_color))
    parts.append(roof)
    parts.append(T.box(name + "_schoorsteen", (width / 2 - 1.0, depth * 0.6, h + 1.5), (0.6, 0.6, 2.4), T.toon("schoorsteen", (0.55, 0.25, 0.18)), bevel=0.02, ol=0))
    glass = T.glow("raam_warm", (1.0, 0.78, 0.42), 1.8) if lit else T.toon("raamglas", (0.55, 0.75, 0.92))
    if broken:
        glass = T.toon("raam_kapot", (0.08, 0.09, 0.12))
    fm = T.toon("kozijn", FRAME)
    wins = [(-1.4, 3.6, 1.5, 1.3), (1.4, 3.6, 1.5, 1.3), (1.2, 1.0, 2.2, 1.5)]
    for k, (wx, wz, ww, wh) in enumerate(wins):
        parts.append(T.box(f"{name}_kozijn{k}", (wx, -0.03, wz), (ww + 0.16, 0.08, wh + 0.16), fm, bevel=0.01, ol=0))
        parts.append(T.box(f"{name}_glas{k}", (wx, -0.075, wz + 0.08), (ww, 0.02, wh), glass, bevel=0, ol=0))
        parts.append(T.box(f"{name}_dorpel{k}", (wx, -0.12, wz - 0.02), (ww + 0.3, 0.2, 0.06), fm, bevel=0.01, ol=0))
        if broken:
            for j in range(3):
                parts.append(T.box(f"{name}_scherf{k}{j}", (wx + (j - 1) * ww * 0.33, -0.08, wz + 0.1 + wh * 0.75 * (j % 2)), (0.25, 0.02, 0.18),
                                   T.toon("glasrand", (0.75, 0.88, 0.95)), rot=(0, 40 * (j - 1), 0), bevel=0, ol=0))
    # voordeur met luifel
    parts.append(T.box(name + "_deurkozijn", (-1.4, -0.03, 0.25), (1.15, 0.08, 2.3), fm, bevel=0.01, ol=0))
    parts.append(T.box(name + "_deur", (-1.4, -0.07, 0.3), (0.95, 0.04, 2.15), T.toon(f"voordeur_{name}", door_color), bevel=0.01, ol=0))
    parts.append(T.box(name + "_bovenlicht", (-1.4, -0.075, 2.3), (0.95, 0.02, 0.15), glass, bevel=0, ol=0))
    parts.append(T.box(name + "_luifel", (-1.4, -0.45, 2.6), (1.6, 0.9, 0.08), fm, bevel=0.02, ol=0))
    parts.append(T.box(name + "_stoep1", (-1.4, -0.45, 0), (1.5, 0.9, 0.15), T.toon("traptree", (0.7, 0.68, 0.64)), bevel=0.01, ol=0))
    parts.append(T.box(name + "_stoep2", (-1.4, -0.3, 0.15), (1.3, 0.6, 0.15), T.toon("traptree", (0.7, 0.68, 0.64)), bevel=0.01, ol=0))
    parts.append(T.sphere(name + "_klink", (-1.05, -0.11, 1.3), 0.04, T.toon("messing", (0.85, 0.68, 0.25)), seg=8, ol=0))
    o = T.merge(name, parts, ol=0.025)
    o.location = (x, facade_y, 0)
    if facing == 1:
        o.rotation_euler.z = math.pi
    return o


def front_garden(name, x, facade_y, depth=4.5, width=6.0, facing=-1, gate_x=-1.4, flowers=True):
    """Voortuin met heggen, tuinpad naar de deur, brievenbus en bloemen.
    facing=-1: tuin ligt aan de -y kant van de gevel (huis kijkt naar -y)."""
    s = facing
    gx = x + gate_x * (-s)  # deur ligt links (gezien vanaf de straat)
    objs = [T.plane(name + "_pad", (gx, facade_y + s * depth / 2, 0.02), (1.3, depth), T.toon("tuinpad", (0.78, 0.72, 0.62)))]
    edge = facade_y + s * (depth - 0.3)
    left_w = (gx - 0.75) - (x - width / 2)
    right_w = (x + width / 2) - (gx + 0.75)
    if left_w > 0.2:
        objs.append(P.hedge(name + "_heg_l", (x - width / 2 + left_w / 2, edge, 0), (left_w, 0.6, 0.9)))
    if right_w > 0.2:
        objs.append(P.hedge(name + "_heg_r", (x + width / 2 - right_w / 2, edge, 0), (right_w, 0.6, 0.9)))
    objs.append(mailbox(name + "_brievenbus", (gx + 1.0, facade_y + s * (depth + 0.1), 0), rot=0 if s == -1 else 180))
    if flowers:
        cols = [(0.95, 0.3, 0.4), (0.98, 0.8, 0.2), (0.9, 0.5, 0.9), (1, 1, 1)]
        pts = {}
        for k in range(14):
            px = gx + 1.0 + (k % 7) * 0.3
            py = facade_y + s * (1.0 + (k // 7) * 0.5)
            pts.setdefault(k % 4, []).append((px, py, 0.3))
        for ci, pl in pts.items():
            objs.append(P.points_mesh(f"{name}_bloemen{ci}", pl, 0.09, T.toon(f"bloem{ci}", cols[ci])))
    return objs


def mailbox(name, loc, rot=0, color=(0.15, 0.20, 0.25)):
    p = [T.cyl(name + "_paal", (0, 0, 0), 0.04, 1.0, P.m("zwart"), seg=8, ol=0),
         T.box(name + "_bak", (0, 0, 1.0), (0.32, 0.22, 0.28), T.toon("brievenbus", color), bevel=0.04, ol=0),
         T.box(name + "_klep", (0, -0.112, 1.18), (0.2, 0.01, 0.04), P.m("metaal"), bevel=0, ol=0)]
    o = T.merge(name, p, ol=0.01)
    o.location = loc
    o.rotation_euler.z = math.radians(rot)
    return o


def bus_stop(name, loc, rot=0):
    p = [T.box(name + "_dak", (0, 0, 2.5), (3.6, 1.6, 0.12), T.toon("abri_dak", (0.2, 0.22, 0.25)), bevel=0.02, ol=0),
         T.box(name + "_achterwand", (0, 0.75, 0.2), (3.4, 0.04, 2.2), T.glass("abri_glas", (0.7, 0.85, 0.95), alpha=0.45), bevel=0, ol=0),
         T.box(name + "_bank", (0, 0.5, 0.45), (2.0, 0.35, 0.06), P.m("metaal"), bevel=0.01, ol=0),
         T.box(name + "_reclame", (-1.75, 0.0, 0.3), (0.06, 1.3, 1.9), T.glow("reclame", (0.95, 0.85, 0.6), 1.2), bevel=0.01, ol=0),
         T.cyl(name + "_bord_paal", (2.1, -0.6, 0), 0.04, 2.8, P.m("metaal"), seg=8, ol=0),
         T.cyl(name + "_bord", (2.1, -0.6, 2.8), 0.28, 0.05, T.toon("busbord", (0.95, 0.75, 0.1)), rot=(90, 0, 0), seg=20, ol=0)]
    for x in (-1.7, 1.7):
        p.append(T.box(f"{name}_paal{x}", (x, 0.75, 0), (0.08, 0.08, 2.5), T.toon("abri_dak", (0.2, 0.22, 0.25)), bevel=0, ol=0))
    o = T.merge(name, p, ol=0.015)
    o.location = loc
    o.rotation_euler.z = math.radians(rot)
    return o


def army_truck(name, loc, rot=0):
    G = T.toon("legergroen", (0.24, 0.30, 0.16))
    G2 = T.toon("legergroen_doek", (0.32, 0.36, 0.22))
    p = [T.box(name + "_chassis", (0, 0, 0.6), (8.0, 2.4, 0.35), P.m("zwart"), bevel=0.03, ol=0),
         T.box(name + "_cabine", (3.0, 0, 0.9), (2.0, 2.4, 1.9), G, bevel=0.1, ol=0),
         T.box(name + "_voorruit", (4.0, 0, 1.9), (0.04, 2.0, 0.75), T.toon("autoruit", (0.12, 0.18, 0.26)), bevel=0, ol=0),
         T.box(name + "_bak", (-1.0, 0, 0.95), (5.6, 2.5, 0.5), G, bevel=0.04, ol=0)]
    bpy_parts = []
    for k in range(6):
        x = -3.7 + k * 1.1
        bpy_parts.append(T.torus(f"{name}_boog{k}", (x, 0, 1.45), 1.25, 0.03, G, rot=(90, 0, 0), seg=24, seg2=6, ol=0))
    p.append(T.box(name + "_huif_d", (-1.0, 0, 1.45), (5.6, 2.5, 1.5), G2, bevel=0.25, ol=0))
    for k, x in enumerate((3.0, -0.4, -2.6)):
        for y in (1.15, -1.15):
            p.append(T.cyl(f"{name}_wiel{k}{y}", (x, y, 0.6), 0.6, 0.45, P.m("zwart"), rot=(90, 0, 0), seg=18, ol=0))
    o = T.merge(name, p, ol=0.03)
    for b in bpy_parts:
        b.parent = o
    o.location = loc
    o.rotation_euler.z = math.radians(rot)
    return o


def helicopter(name, loc, rot=0, color=(0.22, 0.27, 0.16)):
    G = T.toon("heli_" + name, color)
    p = [T.sphere(name + "_romp", (0, 0, 0), 1.5, G, scale=(2.2, 1.0, 1.0), seg=20, ol=0),
         T.sphere(name + "_raam", (1.9, 0, 0.3), 0.9, T.toon("autoruit", (0.12, 0.18, 0.26)), scale=(1.0, 0.95, 0.7), seg=16, ol=0),
         T.cyl(name + "_staart", (-2.5, 0, 0.3), 0.35, 5.5, G, r2=0.15, rot=(0, -88, 0), seg=12, ol=0),
         T.box(name + "_vin", (-7.8, 0, 0.3), (0.8, 0.1, 1.6), G, bevel=0.05, ol=0),
         T.cyl(name + "_mast", (0, 0, 1.3), 0.15, 0.6, P.m("zwart"), seg=10, ol=0)]
    for k in range(4):
        p.append(T.box(f"{name}_blad{k}", (0, 0, 1.9), (13.0, 0.35, 0.05), P.m("zwart"), rot=(0, 0, 45 * k + 20), bevel=0, ol=0, base=False))
    for y in (1.1, -1.1):
        p.append(T.box(f"{name}_ski{y}", (0, y, -1.6), (4.0, 0.12, 0.12), P.m("zwart"), bevel=0.03, ol=0))
    o = T.merge(name, p, ol=0.03)
    o.location = loc
    o.rotation_euler.z = math.radians(rot)
    return o


def bouncy_castle(name, loc, rot=0):
    cols = [(0.95, 0.2, 0.2), (0.15, 0.45, 0.95), (0.98, 0.78, 0.1), (0.2, 0.75, 0.3)]
    p = [T.box(name + "_vloer", (0, 0, 0), (4.0, 4.0, 0.6), T.toon("spring_blauw", cols[1]), bevel=0.25, ol=0)]
    for k, (x, y) in enumerate([(-1.8, -1.8), (1.8, -1.8), (-1.8, 1.8), (1.8, 1.8)]):
        p.append(T.cyl(f"{name}_toren{k}", (x, y, 0), 0.4, 2.6, T.toon(f"spring{k}", cols[k]), seg=16, ol=0, bevel=0.1))
        p.append(T.sphere(f"{name}_bol{k}", (x, y, 2.8), 0.45, T.toon(f"spring{(k + 2) % 4}", cols[(k + 2) % 4]), seg=16, ol=0))
    for k, (x, y, w, d) in enumerate([(0, 1.8, 3.2, 0.35), (-1.8, 0, 0.35, 3.2), (1.8, 0, 0.35, 3.2)]):
        p.append(T.box(f"{name}_wand{k}", (x, y, 0.5), (w, d, 1.5), T.toon("spring_rood", cols[0]), bevel=0.15, ol=0))
    o = T.merge(name, p, ol=0.03)
    o.location = loc
    o.rotation_euler.z = math.radians(rot)
    return o


def balloons(name, anchor, n=6, seed=1, height=1.6):
    import random
    rnd = random.Random(seed)
    cols = [(0.95, 0.15, 0.15), (0.98, 0.75, 0.05), (0.15, 0.55, 0.95), (0.25, 0.80, 0.30), (0.95, 0.45, 0.75)]
    out = []
    a = Vector(anchor)
    for k in range(n):
        q = a + Vector((rnd.uniform(-0.5, 0.5), rnd.uniform(-0.5, 0.5), height + rnd.uniform(0, 0.6)))
        out.append(T.sphere(f"{name}_{k}", tuple(q), 0.25, T.toon(f"ballon{k % 5}", cols[k % 5]), scale=(1, 1, 1.2), seg=12, ol=0.01))
        out.append(T.to_mesh(T.tube(f"{name}_touw{k}", [tuple(a), tuple(q - Vector((0, 0, 0.3)))], 0.006, P.m("wit"))))
    return out
