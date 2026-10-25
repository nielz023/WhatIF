"""Herbruikbare props in de toon-stijl. Elke functie geeft één object of een
lege 'ouder' terug, met het nulpunt op de grond in het midden."""
import math
import random
from mathutils import Vector
from . import toon as T

C = dict(
    beton=(0.62, 0.61, 0.58), asfalt=(0.16, 0.16, 0.18), stoep=(0.55, 0.53, 0.50),
    gras=(0.22, 0.50, 0.16), boomblad=(0.16, 0.45, 0.14), boomblad2=(0.30, 0.58, 0.16),
    stam=(0.30, 0.17, 0.08), hout=(0.55, 0.32, 0.14), hout_licht=(0.78, 0.55, 0.30),
    metaal=(0.45, 0.47, 0.50), donkergroen=(0.06, 0.18, 0.12), zwart=(0.04, 0.04, 0.05),
    wit=(0.90, 0.90, 0.88), rood=(0.78, 0.07, 0.05), geel=(0.95, 0.70, 0.08),
    blauw=(0.08, 0.28, 0.75), roze=(0.95, 0.42, 0.62), oranje=(0.95, 0.38, 0.06),
    paars=(0.42, 0.16, 0.65), groen=(0.12, 0.60, 0.22), lichtblauw=(0.35, 0.65, 0.90),
)


def m(name):
    return T.toon(name, C[name])


def tree(name, loc, h=6.0, r=2.4, seed=0, kind="rond"):
    """Toon-boom: stam + 3-4 bollen loof."""
    rnd = random.Random(seed)
    parts = [T.cyl(name + "_stam", (0, 0, 0), 0.22 * h / 6, h * 0.55, m("stam"), r2=0.15 * h / 6, seg=10, ol=0.02)]
    leaf = m("boomblad") if seed % 2 == 0 else m("boomblad2")
    if kind == "rond":
        for i in range(4):
            a = rnd.uniform(0, 6.28)
            d = r * 0.35 if i else 0
            parts.append(T.sphere(f"{name}_loof{i}", (math.cos(a) * d, math.sin(a) * d, h * 0.62 + (r * 0.3 if i == 0 else rnd.uniform(-0.2, 0.3) * r)),
                                  r * (1.0 if i == 0 else rnd.uniform(0.6, 0.8)), leaf, seg=14, ol=0.03))
    else:  # den
        for i in range(3):
            parts.append(T.cyl(f"{name}_kegel{i}", (0, 0, h * (0.25 + i * 0.22)), r * (1 - i * 0.25), h * 0.4, leaf, r2=0.05, seg=10, ol=0.03))
    o = T.merge(name, parts, ol=0.025)
    o.location = loc
    o.rotation_euler.z = rnd.uniform(0, 6.28)
    return o


def lamp_post(name, loc, h=4.5, on=False, color=(1.0, 0.75, 0.4)):
    p = [T.cyl(name + "_paal", (0, 0, 0), 0.07, h, m("donkergroen"), seg=10, ol=0.012),
         T.cyl(name + "_voet", (0, 0, 0), 0.16, 0.5, m("donkergroen"), r2=0.09, seg=10, ol=0.012),
         T.cyl(name + "_kap", (0, 0, h + 0.35), 0.28, 0.12, m("donkergroen"), r2=0.05, seg=12, ol=0.012)]
    o = T.merge(name, p, ol=0.012)
    bulb = T.sphere(name + "_lamp", (0, 0, h + 0.2), 0.2, T.glow("lamp_warm", color, 5) if on else T.toon("lamp_uit", (0.95, 0.92, 0.8)), seg=12, ol=0.01)
    bulb.parent = o
    o.location = loc
    return o


def bench(name, loc, rot=0):
    p = [T.box(name + "_zit", (0, 0, 0.42), (1.8, 0.45, 0.06), m("hout")),
         T.box(name + "_rug", (0, 0.22, 0.55), (1.8, 0.05, 0.35), m("hout"), rot=(-10, 0, 0)),
         T.box(name + "_poot1", (-0.75, 0, 0), (0.06, 0.45, 0.42), m("zwart")),
         T.box(name + "_poot2", (0.75, 0, 0), (0.06, 0.45, 0.42), m("zwart"))]
    o = T.merge(name, p)
    o.location = loc
    o.rotation_euler.z = math.radians(rot)
    return o


def bin_(name, loc, color="donkergroen"):
    o = T.cyl(name, (0, 0, 0), 0.28, 0.9, m(color), seg=16, ol=0.012)
    o.location = loc
    return o


def railing(name, pts, h=1.0, posts=2.0, color="metaal", r=0.035):
    """Hekwerk / wachtrijreling langs punten."""
    parts = []
    pts = [Vector(p) for p in pts]
    parts.append(T.tube(name + "_boven", [(p.x, p.y, h) for p in pts], r, m(color)))
    parts.append(T.tube(name + "_midden", [(p.x, p.y, h * 0.5) for p in pts], r * 0.8, m(color)))
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        n = max(1, int((b - a).length / posts))
        for k in range(n + (1 if i == len(pts) - 2 else 0)):
            q = a.lerp(b, k / n)
            parts.append(T.cyl(f"{name}_p{i}_{k}", (q.x, q.y, 0), r * 1.2, h, m(color), seg=8, ol=0))
    parts = [T.to_mesh(o) if o.type == "CURVE" else o for o in parts]
    return T.merge(name, parts, ol=0.01)


def catenary(a, b, sag, n=24):
    a, b = Vector(a), Vector(b)
    pts = []
    for i in range(n + 1):
        t = i / n
        q = a.lerp(b, t)
        q.z -= sag * 4 * t * (1 - t)
        pts.append(q)
    return pts


def string_lights(name, anchors, sag=0.6, spacing=0.6, on=True, colors=None):
    """Lichtsnoer tussen ankerpunten: draad + lampjes (één object per kleur)."""
    colors = colors or [(1.0, 0.75, 0.35), (1.0, 0.45, 0.30), (1.0, 0.85, 0.5), (0.6, 0.85, 1.0)]
    wire_pts, bulbs = [], [[] for _ in colors]
    k = 0
    for i in range(len(anchors) - 1):
        seg = catenary(anchors[i], anchors[i + 1], sag)
        wire_pts.append(seg)
        L = (Vector(anchors[i + 1]) - Vector(anchors[i])).length
        n = max(2, int(L / spacing))
        for j in range(1, n):
            t = j / n
            q = Vector(anchors[i]).lerp(Vector(anchors[i + 1]), t)
            q.z -= sag * 4 * t * (1 - t) + 0.08
            bulbs[k % len(colors)].append(q)
            k += 1
    wires = [T.tube(f"{name}_draad{i}", s, 0.012, m("zwart")) for i, s in enumerate(wire_pts)]
    out = [T.merge(name + "_draad", [T.to_mesh(w) for w in wires], ol=0)]
    for ci, pts in enumerate(bulbs):
        if not pts:
            continue
        col = colors[ci]
        mt = T.glow(f"lampje{ci}", col, 6) if on else T.toon(f"lampje_uit{ci}", tuple(0.55 + c * 0.4 for c in col))
        out.append(points_mesh(f"{name}_lampjes{ci}", pts, 0.07, mt))
    return out


def points_mesh(name, pts, r, mat, seg=8):
    """Veel kleine bolletjes als één mesh (lampjes, ballonnen e.d.)."""
    import bmesh
    import bpy
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    for p in pts:
        g = bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=max(4, seg // 2), radius=r)
        for v in g["verts"]:
            v.co += Vector(p)
    bm.to_mesh(me)
    bm.free()
    for f in me.polygons:
        f.use_smooth = True
    me.materials.append(mat)
    o = bpy.data.objects.new(name, me)
    T._link(o)
    return o


def striped_awning(name, loc, width, depth, colors=("rood", "wit"), stripes=8, tilt=18, drop=0.25):
    """Gestreepte luifel met geschulpte rand."""
    parts = []
    w = width / stripes
    for i in range(stripes):
        c = m(colors[i % len(colors)])
        x = -width / 2 + w * (i + 0.5)
        parts.append(T.box(f"{name}_s{i}", (x, depth / 2, 0), (w, depth, 0.05), c, bevel=0.0, ol=0, base=False))
        parts.append(T.cyl(f"{name}_f{i}", (x, depth, -drop), w / 2, drop, c, rot=(0, 0, 0), seg=12, ol=0))
    o = T.merge(name, parts, ol=0.015)
    o.location = loc
    o.rotation_euler.x = math.radians(-tilt)
    return o


def car(name, loc, rot=0, color=(0.1, 0.35, 0.8), kind="hatch"):
    """Simpele toon-auto (4.2 m)."""
    body = T.toon(f"auto_{name}", color)
    p = [T.box(name + "_onder", (0, 0, 0.32), (4.1, 1.75, 0.65), body, bevel=0.12, ol=0),
         T.box(name + "_cabine", (-0.2 if kind == "hatch" else 0, 0, 0.95), (2.3 if kind == "hatch" else 2.0, 1.55, 0.6), body, bevel=0.12, ol=0),
         T.box(name + "_ruit_v", (0.82, 0, 1.0), (0.12, 1.45, 0.48), T.toon("autoruit", (0.12, 0.18, 0.26)), bevel=0.03, ol=0, rot=(0, -28, 0)),
         T.box(name + "_ruit_z", (-0.2 if kind == "hatch" else 0, 0, 1.02), (2.32 if kind == "hatch" else 2.02, 1.58, 0.4), T.toon("autoruit", (0.12, 0.18, 0.26)), bevel=0.03, ol=0)]
    for i, (x, y) in enumerate([(1.3, 0.8), (-1.3, 0.8), (1.3, -0.8), (-1.3, -0.8)]):
        p.append(T.cyl(f"{name}_wiel{i}", (x, y - 0.12 * (1 if y > 0 else -1), 0.34), 0.34, 0.24, m("zwart"), rot=(90, 0, 0), seg=16, ol=0))
    for y in (0.6, -0.6):
        p.append(T.sphere(f"{name}_koplamp{y}", (2.04, y, 0.55), 0.12, T.toon("koplamp", (1, 0.97, 0.85)), scale=(0.4, 1, 0.7), seg=10, ol=0))
    o = T.merge(name, p, ol=0.02)
    o.location = loc
    o.rotation_euler.z = math.radians(rot)
    return o


def hedge(name, loc, size, color="boomblad"):
    o = T.box(name, loc, size, m(color), bevel=0.18, ol=0.02)
    return o


def ground(name, size, color, loc=(0, 0, 0), z=0.0):
    return T.plane(name, (loc[0], loc[1], z), size, T.toon(name, color))
