"""Bouwstenen voor binnenruimtes: kamer met muren, ramen, deuren en meubels."""
import math
from mathutils import Vector
from . import toon as T
from . import props as P

WALL_T = 0.12


def _wall(name, length, h, holes, mat):
    """Muur langs x (0..length), dikte in y, met gaten (a0, a1, z0, z1)."""
    parts = []
    holes = sorted(holes)
    a = 0.0
    for (a0, a1, z0, z1) in holes:
        if a0 > a:
            parts.append(T.box(f"{name}_d{len(parts)}", ((a + a0) / 2, 0, 0), (a0 - a, WALL_T, h), mat, bevel=0, ol=0))
        if z0 > 0:
            parts.append(T.box(f"{name}_o{len(parts)}", ((a0 + a1) / 2, 0, 0), (a1 - a0, WALL_T, z0), mat, bevel=0, ol=0))
        if z1 < h:
            parts.append(T.box(f"{name}_b{len(parts)}", ((a0 + a1) / 2, 0, z1), (a1 - a0, WALL_T, h - z1), mat, bevel=0, ol=0))
        a = a1
    if a < length:
        parts.append(T.box(f"{name}_d{len(parts)}", ((a + length) / 2, 0, 0), (length - a, WALL_T, h), mat, bevel=0, ol=0))
    return T.merge(name, parts, ol=0.01)


def room(name, w, d, h, wall_color, floor_color, holes=None, hide=("front",), ceiling=True, skirting=True):
    """Kamer gecentreerd op (0,0). Muren: back (+y), front (-y), left (-x), right (+x).
    holes = {"back": [(a0, a1, z0, z1)], ...} met a gemeten van links naar rechts
    gezien vanuit het midden van de kamer. Muren in 'hide' blokkeren wel licht,
    maar de camera ziet erdoorheen."""
    holes = holes or {}
    wm = T.toon(name + "_muur", wall_color)
    out = {}
    specs = {
        # (lengte, positie van a=0, rotatie z)
        "back": (w, Vector((-w / 2, d / 2 + WALL_T / 2, 0)), 0),
        "front": (w, Vector((w / 2, -d / 2 - WALL_T / 2, 0)), 180),
        "left": (d, Vector((-w / 2 - WALL_T / 2, -d / 2, 0)), 90),
        "right": (d, Vector((w / 2 + WALL_T / 2, d / 2, 0)), -90),
    }
    for side, (L, origin, rz) in specs.items():
        o = _wall(f"{name}_muur_{side}", L, h, holes.get(side, []), wm)
        o.location = origin
        o.rotation_euler.z = math.radians(rz)
        if side in hide:
            o.visible_camera = False
            o.visible_shadow = True
        out[side] = o
    out["floor"] = T.box(name + "_vloer", (0, 0, -0.1), (w + 0.3, d + 0.3, 0.1), T.toon(name + "_vloer", floor_color), bevel=0, ol=0)
    if ceiling:
        c = T.box(name + "_plafond", (0, 0, h), (w + 0.3, d + 0.3, 0.1), T.toon(name + "_plafond", (0.93, 0.92, 0.9)), bevel=0, ol=0)
        out["ceiling"] = c
    if skirting:
        sk = T.toon("plint", (0.95, 0.94, 0.92))
        place = {"back": ((0, d / 2 - 0.015, 0), 0, w), "front": ((0, -d / 2 + 0.015, 0), 0, w),
                 "left": ((-w / 2 + 0.015, 0, 0), 90, d), "right": ((w / 2 - 0.015, 0, 0), 90, d)}
        for side, (loc, rz, L) in place.items():
            if side not in hide:
                T.box(f"{name}_plint_{side}", loc, (L, 0.03, 0.08), sk, rot=(0, 0, rz), bevel=0, ol=0)
    return out


def wall_point(w, d, side, a, z=0.0, inset=0.0):
    """Wereldpositie op de binnenkant van een muur (zie room())."""
    if side == "back":
        return Vector((-w / 2 + a, d / 2 - inset, z)), 0
    if side == "front":
        return Vector((w / 2 - a, -d / 2 + inset, z)), 180
    if side == "left":
        return Vector((-w / 2 + inset, -d / 2 + a, z)), 90
    return Vector((w / 2 - inset, d / 2 - a, z)), -90


def window(name, w, d, side, a0, a1, z0, z1, frame_color=(0.95, 0.95, 0.93), curtains=None, open_frac=0.5):
    """Raamkozijn + glas + vensterbank (+ gordijnen) in een gat van room()."""
    fm = T.toon("kozijn", frame_color)
    W, H = a1 - a0, z1 - z0
    p = [T.box(name + "_k_o", (0, 0, -0.04), (W + 0.1, 0.16, 0.08), fm, bevel=0.01, ol=0),
         T.box(name + "_k_b", (0, 0, H - 0.04), (W + 0.1, 0.16, 0.08), fm, bevel=0.01, ol=0),
         T.box(name + "_k_l", (-W / 2, 0, 0), (0.08, 0.16, H), fm, bevel=0.01, ol=0),
         T.box(name + "_k_r", (W / 2, 0, 0), (0.08, 0.16, H), fm, bevel=0.01, ol=0),
         T.box(name + "_k_m", (0, 0, 0), (0.05, 0.12, H), fm, bevel=0.01, ol=0),
         T.box(name + "_bank", (0, -0.12, -0.06), (W + 0.3, 0.26, 0.05), fm, bevel=0.01, ol=0)]
    frame = T.merge(name + "_kozijn", p, ol=0.008)
    gl = T.box(name + "_glas", (0, 0, 0), (W, 0.01, H), T.glass(), bevel=0, ol=0)
    gl.visible_shadow = False
    objs = [frame, gl]
    if curtains:
        cm = T.toon(name + "_gordijn", curtains)
        cw = W * (1 - open_frac) / 2 + 0.25
        for s in (-1, 1):
            folds = []
            n = max(3, int(cw / 0.12))
            for k in range(n):
                x = s * (W / 2 + 0.25 - cw * (k + 0.5) / n)
                folds.append(T.cyl(f"{name}_plooi_{s}_{k}", (x, -0.18, -0.3), 0.075, H + 0.6, cm, seg=8, ol=0))
            objs.append(T.merge(f"{name}_gordijn_{'l' if s < 0 else 'r'}", folds, ol=0.008))
        objs.append(T.cyl(name + "_roede", (-(W / 2 + 0.4), -0.18, H + 0.32), 0.02, W + 0.8, P.m("metaal"), rot=(0, 90, 0), seg=8, ol=0))
    pos, rz = wall_point(w, d, side, (a0 + a1) / 2, z0, inset=-WALL_T / 2)
    return T.group(name, objs, loc=tuple(pos), rot=(0, 0, rz))


def door(name, w, d, side, a, color=(0.95, 0.94, 0.92), width=0.9, height=2.05):
    p = [T.box(name + "_blad", (0, 0, 0), (width, 0.05, height), T.toon("deur_" + name, color), bevel=0.01, ol=0),
         T.box(name + "_kozijn_l", (-width / 2 - 0.04, 0, 0), (0.08, 0.08, height + 0.06), T.toon("kozijn", (0.95, 0.95, 0.93)), bevel=0, ol=0),
         T.box(name + "_kozijn_r", (width / 2 + 0.04, 0, 0), (0.08, 0.08, height + 0.06), T.toon("kozijn", (0.95, 0.95, 0.93)), bevel=0, ol=0),
         T.box(name + "_kozijn_b", (0, 0, height), (width + 0.16, 0.08, 0.08), T.toon("kozijn", (0.95, 0.95, 0.93)), bevel=0, ol=0),
         T.sphere(name + "_klink", (width / 2 - 0.1, -0.06, 1.0), 0.035, P.m("metaal"), seg=10, ol=0)]
    o = T.merge(name, p, ol=0.008)
    pos, rz = wall_point(w, d, side, a, 0, inset=0.03)
    o.location = pos
    o.rotation_euler.z = math.radians(rz)
    return o


def chair(name, loc, rot=0, color=(0.55, 0.32, 0.14), office=False):
    cm = T.toon("stoel_" + name, color)
    if office:
        p = [T.box(name + "_zit", (0, 0, 0.45), (0.48, 0.48, 0.08), cm, bevel=0.03, ol=0),
             T.box(name + "_rug", (0, 0.24, 0.55), (0.46, 0.06, 0.5), cm, bevel=0.03, ol=0),
             T.cyl(name + "_kolom", (0, 0, 0.08), 0.03, 0.37, P.m("zwart"), seg=8, ol=0)]
        for k in range(5):
            a = 2 * math.pi * k / 5
            p.append(T.box(f"{name}_poot{k}", (math.cos(a) * 0.15, math.sin(a) * 0.15, 0.06), (0.3, 0.04, 0.03), P.m("zwart"), rot=(0, 0, math.degrees(a)), bevel=0, ol=0))
            p.append(T.sphere(f"{name}_wiel{k}", (math.cos(a) * 0.28, math.sin(a) * 0.28, 0.03), 0.03, P.m("zwart"), seg=8, ol=0))
    else:
        p = [T.box(name + "_zit", (0, 0, 0.44), (0.44, 0.44, 0.05), cm, bevel=0.02, ol=0),
             T.box(name + "_rug", (0, 0.2, 0.49), (0.44, 0.04, 0.42), cm, bevel=0.02, ol=0)]
        for x in (-0.19, 0.19):
            for y in (-0.19, 0.19):
                p.append(T.box(f"{name}_poot{x}{y}", (x, y, 0), (0.04, 0.04, 0.44), cm, bevel=0, ol=0))
    o = T.merge(name, p, ol=0.008)
    o.location = loc
    o.rotation_euler.z = math.radians(rot)
    return o


def table(name, loc, size=(1.4, 0.8, 0.75), color=(0.6, 0.38, 0.18), rot=0):
    tm = T.toon("tafel_" + name, color)
    sx, sy, h = size
    p = [T.box(name + "_blad", (0, 0, h - 0.04), (sx, sy, 0.04), tm, bevel=0.01, ol=0)]
    for x in (-sx / 2 + 0.06, sx / 2 - 0.06):
        for y in (-sy / 2 + 0.06, sy / 2 - 0.06):
            p.append(T.box(f"{name}_poot{x}{y}", (x, y, 0), (0.05, 0.05, h - 0.04), tm, bevel=0, ol=0))
    o = T.merge(name, p, ol=0.008)
    o.location = loc
    o.rotation_euler.z = math.radians(rot)
    return o


def books(name, loc, n=5, rot=0, flat=True, seed=0):
    import random
    rnd = random.Random(seed)
    cols = [(0.8, 0.15, 0.1), (0.1, 0.35, 0.75), (0.95, 0.7, 0.1), (0.2, 0.6, 0.3), (0.55, 0.2, 0.6), (0.9, 0.45, 0.1)]
    p = []
    z = 0.0
    for k in range(n):
        if flat:
            t = rnd.uniform(0.025, 0.045)
            p.append(T.box(f"{name}_{k}", (rnd.uniform(-0.02, 0.02), rnd.uniform(-0.02, 0.02), z), (0.30, 0.22, t), T.toon(f"boek{k % 6}", cols[(k + seed) % 6]), bevel=0.004, ol=0, rot=(0, 0, rnd.uniform(-8, 8))))
            z += t
        else:
            t = rnd.uniform(0.025, 0.05)
            hgt = rnd.uniform(0.2, 0.28)
            p.append(T.box(f"{name}_{k}", (z, 0, 0), (t, 0.18, hgt), T.toon(f"boek{k % 6}", cols[(k + seed) % 6]), bevel=0.004, ol=0))
            z += t + 0.002
    o = T.merge(name, p, ol=0.005)
    o.location = loc
    o.rotation_euler.z = math.radians(rot)
    return o


def rug(name, loc, size, color, rot=0, round_=False):
    rm = T.toon("kleed_" + name, color)
    if round_:
        o = T.cyl(name, loc, size[0] / 2, 0.012, rm, seg=48, ol=0.006)
        o.scale.y = size[1] / size[0]
    else:
        o = T.box(name, loc, (size[0], size[1], 0.012), rm, bevel=0.004, ol=0.006)
    o.rotation_euler.z = math.radians(rot)
    return o


def ceiling_lamp(name, loc, on=False):
    p = [T.cyl(name + "_snoer", (0, 0, -0.5), 0.008, 0.5, P.m("zwart"), seg=6, ol=0),
         T.cyl(name + "_kap", (0, 0, -0.72), 0.22, 0.22, T.toon("lampenkap", (0.95, 0.93, 0.88)), r2=0.08, seg=20, ol=0, cap=False)]
    o = T.merge(name, p, ol=0.006)
    o.location = loc
    b = T.sphere(name + "_peer", (loc[0], loc[1], loc[2] - 0.7), 0.06, T.glow("peer", (1, 0.85, 0.6), 6) if on else T.toon("peer_uit", (0.97, 0.95, 0.9)), seg=10, ol=0)
    return o
