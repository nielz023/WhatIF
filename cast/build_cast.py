"""
Bouwt de bijfiguren (cast) van video 1 "What if you got 2x stronger every day?".

Elke bijfiguur start als kopie van het hoofdpersonage (hoofdpersonage.glb), zodat
koppen, ogen, handen en materialen exact dezelfde stijl hebben. Daarna krijgt elke
figuur een eigen lichaamsbouw, huidskleur, haar, gezichtsuitdrukking, kleding en
accessoires.

Gebruik (Blender 4.2+ / 5.x):
    blender -b -P cast/build_cast.py -- --base pad/naar/hoofdpersonage.glb --out pad/naar/cast
of met de bpy-module:
    python cast/build_cast.py --base ... --out ...

Opties:
    --only mama,papa   bouw/render alleen deze figuren
    --no-render        alleen .blend en .glb maken
    --samples 48       Cycles-samples per render
"""
import bpy
import bmesh
import math
import os
import random
import sys
from mathutils import Vector, Matrix, Euler

# ---------------------------------------------------------------------------
# Maten van het hoofdpersonage (gemeten uit hoofdpersonage.glb)
# ---------------------------------------------------------------------------
HEAD_C = Vector((0.0, 0.0, 1.47))   # middelpunt van het hoofd
HEAD_R = 0.30                       # straal van het hoofd
NECK_PIVOT = Vector((0.0, 0.0, 1.17))
# doorsnede van de romp: (z, halve breedte, halve diepte)
TORSO_PROFILE = [(0.60, 0.129, 0.100), (0.62, 0.170, 0.132), (0.65, 0.184, 0.144),
                 (0.70, 0.189, 0.147), (0.80, 0.191, 0.149), (0.90, 0.190, 0.148),
                 (1.00, 0.199, 0.155), (1.10, 0.194, 0.151), (1.15, 0.167, 0.130),
                 (1.18, 0.119, 0.093), (1.20, 0.068, 0.053)]
EYE_C = {+1: Vector((0.0775, 0.0, 1.496)), -1: Vector((-0.0775, 0.0, 1.496))}
BROW_C = {+1: Vector((0.0735, 0.0, 1.562)), -1: Vector((-0.0735, 0.0, 1.562))}
MOUTH_C = Vector((0.0, 0.0, 1.370))

# Onderdelen van het hoofdpersonage (index = nummer in de glb).
# Let op: -x is de rechterkant van het personage (hij kijkt naar -y).
PART_NAMES = {
    0: "been_R", 1: "schoen_R", 2: "been_L", 3: "schoen_L",
    4: "romp", 5: "capuchon", 6: "koord_R", 7: "koord_R_eind", 8: "koord_R_eind2",
    9: "koord_L", 10: "koord_L_eind", 11: "koord_L_eind2", 12: "buidelzak",
    13: "bovenarm_R", 14: "onderarm_R", 15: "elleboog_R", 16: "manchet_R",
    17: "hand_R", 18: "duim_R", 19: "vingers_R",
    20: "bovenarm_L", 21: "onderarm_L", 22: "elleboog_L", 23: "manchet_L",
    24: "hand_L", 25: "duim_L", 26: "vingers_L",
    27: "nek", 28: "hoofd", 29: "oor_R", 30: "oor_R_binnen", 31: "oor_L", 32: "oor_L_binnen",
    33: "oog_R_lijn", 34: "oog_R_wit", 35: "oog_R_iris", 36: "oog_R_iris2", 37: "oog_R_pupil",
    38: "oog_R_glans", 39: "oog_R_glans2",
    40: "oog_L_lijn", 41: "oog_L_wit", 42: "oog_L_iris", 43: "oog_L_iris2", 44: "oog_L_pupil",
    45: "oog_L_glans", 46: "oog_L_glans2",
    47: "wenkbrauw_R", 48: "wenkbrauw_R_punt", 49: "wenkbrauw_R_punt2",
    50: "wenkbrauw_L", 51: "wenkbrauw_L_punt", 52: "wenkbrauw_L_punt2",
    53: "mond", 54: "tong",
}
HOODIE_EXTRAS = [5, 6, 7, 8, 9, 10, 11, 12]
BROW_PARTS = {-1: [47, 48, 49], +1: [50, 51, 52]}


def part_cat(i):
    if i in (0, 1):
        return "leg-"
    if i in (2, 3):
        return "leg+"
    if 13 <= i <= 19:
        return "arm-"
    if 20 <= i <= 26:
        return "arm+"
    if i >= 28:
        return "head"
    return "torso"


# ---------------------------------------------------------------------------
# Kleine hulpfuncties
# ---------------------------------------------------------------------------
def lin(hexcol):
    """sRGB-hex naar lineaire RGB."""
    hexcol = hexcol.lstrip("#")
    out = []
    for k in range(3):
        c = int(hexcol[2 * k:2 * k + 2], 16) / 255.0
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return tuple(out)


def smoothstep(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def torso_r(z):
    p = TORSO_PROFILE
    if z <= p[0][0]:
        return p[0][1], p[0][2]
    for (z0, x0, y0), (z1, x1, y1) in zip(p, p[1:]):
        if z0 <= z <= z1:
            t = (z - z0) / (z1 - z0)
            return x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
    return p[-1][1], p[-1][2]


def face_point(x, z, lift=0.003):
    """Punt op het oppervlak van het hoofd (voorkant) + normaal."""
    dz = z - HEAD_C.z
    y = -math.sqrt(max(HEAD_R ** 2 - x * x - dz * dz, 1e-6))
    p = Vector((x, y, z))
    n = (p - HEAD_C).normalized()
    return p + n * lift, n


class Mats:
    """Materialen in dezelfde opbouw als het hoofdpersonage."""

    def __init__(self, unlit_template, prefix):
        self.tpl = unlit_template
        self.prefix = prefix
        self.cache = {}

    def pbr(self, hexcol, rough=0.9, metal=0.0, key=None):
        key = key or ("pbr", hexcol, rough, metal)
        if key in self.cache:
            return self.cache[key]
        m = bpy.data.materials.new(f"{self.prefix}_{hexcol.lstrip('#')}")
        m.use_nodes = True
        b = m.node_tree.nodes.get("Principled BSDF")
        b.inputs["Base Color"].default_value = (*lin(hexcol), 1.0)
        b.inputs["Roughness"].default_value = rough
        b.inputs["Metallic"].default_value = metal
        m.diffuse_color = (*lin(hexcol), 1.0)
        self.cache[key] = m
        return m

    def unlit(self, hexcol):
        key = ("unlit", hexcol)
        if key in self.cache:
            return self.cache[key]
        m = self.tpl.copy()
        m.name = f"{self.prefix}_vlak_{hexcol.lstrip('#')}"
        m.node_tree.nodes["Emission"].inputs["Color"].default_value = (*lin(hexcol), 1.0)
        self.cache[key] = m
        return m


# ---------------------------------------------------------------------------
# Geometrie (alles in de coördinaten van het hoofdpersonage, vóór vervorming)
# ---------------------------------------------------------------------------
class Builder:
    def __init__(self, coll, name, mats):
        self.coll = coll
        self.name = name
        self.mats = mats
        self.items = []  # (object, categorie)

    def _obj(self, bm, label, mat, cat, smooth=True):
        me = bpy.data.meshes.new(f"{self.name}_{label}")
        bm.to_mesh(me)
        bm.free()
        for p in me.polygons:
            p.use_smooth = smooth
        ob = bpy.data.objects.new(f"{self.name}_{label}", me)
        self.coll.objects.link(ob)
        me.materials.append(mat)
        self.items.append((ob, cat))
        return ob

    def sphere(self, label, mat, center, scale=(1, 1, 1), rot=(0, 0, 0), cat="head",
               seg=32, rings=16, quat=None):
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, radius=1.0)
        R = quat.to_matrix().to_4x4() if quat is not None else Euler(rot).to_matrix().to_4x4()
        M = Matrix.Translation(Vector(center)) @ R @ Matrix.Diagonal((*scale, 1.0))
        bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
        return self._obj(bm, label, mat, cat)

    def cylinder(self, label, mat, p1, p2, r1, r2=None, cat="torso", seg=24, cap=True,
                 squash=1.0):
        p1, p2 = Vector(p1), Vector(p2)
        r2 = r1 if r2 is None else r2
        d = p2 - p1
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=cap, cap_tris=False, segments=seg,
                              radius1=r1, radius2=r2, depth=d.length)
        q = d.normalized().to_track_quat("Z", "Y")
        M = Matrix.Translation((p1 + p2) / 2) @ q.to_matrix().to_4x4() @ \
            Matrix.Diagonal((1.0, squash, 1.0, 1.0))
        bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
        return self._obj(bm, label, mat, cat)

    def box(self, label, mat, center, size, rot=(0, 0, 0), cat="torso", bevel=0.3):
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        if bevel:
            bmesh.ops.bevel(bm, geom=bm.edges[:], offset=bevel * 0.5,
                            segments=3, affect="EDGES", profile=0.5)
        M = Matrix.Translation(Vector(center)) @ Euler(rot).to_matrix().to_4x4() @ \
            Matrix.Diagonal((*size, 1.0))
        bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
        return self._obj(bm, label, mat, cat, smooth=bool(bevel))

    def torus(self, label, mat, center, R, r, normal=(0, 0, 1), cat="head", seg=40, rseg=12,
              scale=(1, 1, 1), arc=(0.0, 2 * math.pi)):
        bm = bmesh.new()
        full = abs(arc[1] - arc[0] - 2 * math.pi) < 1e-6
        nu = seg if full else seg + 1
        grid = []
        for i in range(nu):
            u = arc[0] + (arc[1] - arc[0]) * i / seg
            row = []
            for j in range(rseg):
                v = 2 * math.pi * j / rseg
                x = (R + r * math.cos(v)) * math.cos(u)
                y = (R + r * math.cos(v)) * math.sin(u)
                z = r * math.sin(v)
                row.append(bm.verts.new((x, y, z)))
            grid.append(row)
        rng = seg if full else seg
        for i in range(rng):
            a, b = grid[i], grid[(i + 1) % nu]
            for j in range(rseg):
                bm.faces.new((a[j], b[j], b[(j + 1) % rseg], a[(j + 1) % rseg]))
        q = Vector(normal).normalized().to_track_quat("Z", "Y")
        M = Matrix.Translation(Vector(center)) @ q.to_matrix().to_4x4() @ \
            Matrix.Diagonal((*scale, 1.0))
        bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        return self._obj(bm, label, mat, cat)

    def shell(self, label, mat, lower, upper=None, arange=None, radius=HEAD_R * 1.035,
              scale=(1, 1, 1), offset=(0, 0, 0), thick=0.012, seg=120, rows=28):
        """Schaal rond het hoofd (haar, baard) met een gladde rand.
        lower(a) en upper(a) geven de grens in n.z als functie van de hoek a rond het
        hoofd (a = 0 is de voorkant, a > 0 richting +x). Zonder upper loopt de schaal
        door tot de kruin. arange=(a0, a1) beperkt de hoek; zonder is hij rondom."""
        full = arange is None
        a0, a1 = (0.0, 2 * math.pi) if full else arange
        ncol = seg if full else seg + 1
        bm = bmesh.new()

        def wrap(a):
            return math.atan2(math.sin(a), math.cos(a))

        def pt(a, nz):
            nz = max(-0.999, min(0.999, nz))
            r = math.sqrt(1 - nz * nz)
            return Vector((math.sin(a) * r, -math.cos(a) * r, nz))

        top = upper is None
        grid = []
        for i in range(ncol):
            a = a0 + (a1 - a0) * i / seg
            lo = lower(wrap(a))
            hi = 0.985 if top else upper(wrap(a))
            e0, e1 = math.asin(max(-0.999, min(0.999, lo))), math.asin(max(-0.999, min(0.999, hi)))
            col = []
            for j in range(rows + 1):
                e = e0 + (e1 - e0) * j / rows
                col.append(bm.verts.new(pt(a, math.sin(e))))
            grid.append(col)
        for i in range(seg if full else seg):
            c0, c1 = grid[i], grid[(i + 1) % ncol]
            for j in range(rows):
                bm.faces.new((c0[j], c1[j], c1[j + 1], c0[j + 1]))
        if top:
            pole = bm.verts.new((0, 0, 1))
            for i in range(seg):
                bm.faces.new((grid[i][rows], grid[(i + 1) % ncol][rows], pole))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        # normalen naar buiten
        f = bm.faces[0] if hasattr(bm.faces, "__getitem__") else None
        bm.faces.ensure_lookup_table()
        f = bm.faces[len(bm.faces) // 2]
        if f.normal.dot(f.calc_center_median()) < 0:
            bmesh.ops.reverse_faces(bm, faces=bm.faces)
        M = Matrix.Translation(HEAD_C + Vector(offset)) @ \
            Matrix.Diagonal((radius * scale[0], radius * scale[1], radius * scale[2], 1.0))
        bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
        ob = self._obj(bm, label, mat, "head")
        if thick:
            mod = ob.modifiers.new("dikte", "SOLIDIFY")
            mod.thickness = thick
            mod.offset = -1.0
            mod.use_even_offset = True
        return ob

    def loft(self, label, mat, rings, seg=72, gap=None, cat="torso", thick=0.008, steps=4):
        """Elliptische buis door ringen (z, halve breedte, halve diepte).
        gap(z) geeft de halve openingshoek (radialen) aan de voorkant, of 0."""
        # extra tussenringen voor een gladde rand
        dense = []
        for (r0, r1) in zip(rings, rings[1:]):
            for s in range(steps):
                t = s / steps
                dense.append(tuple(r0[k] + (r1[k] - r0[k]) * t for k in range(3)))
        dense.append(rings[-1])
        is_open = gap is not None
        bm = bmesh.new()
        grid = []
        for (z, rx, ry) in dense:
            g = max(gap(z), 0.0) if is_open else 0.0
            row = []
            n = seg + 1 if is_open else seg
            for i in range(n):
                a = g + (2 * math.pi - 2 * g) * i / seg  # a = 0 is de voorkant
                row.append(bm.verts.new((rx * math.sin(a), -ry * math.cos(a), z)))
            grid.append(row)
        for k in range(len(dense) - 1):
            a, b = grid[k], grid[k + 1]
            for i in range(seg):
                i2 = i + 1 if is_open else (i + 1) % seg
                bm.faces.new((a[i], a[i2], b[i2], b[i]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        ob = self._obj(bm, label, mat, cat)
        if thick:
            mod = ob.modifiers.new("dikte", "SOLIDIFY")
            mod.thickness = thick
            mod.offset = 0.0
        return ob

    # -- decals op het gezicht ------------------------------------------------
    def face_disc(self, label, mat, x, z, sx, sz, thick=0.002, lift=0.003, roll=0.0):
        p, n = face_point(x, z, lift)
        q = n.to_track_quat("-Y", "Z")
        q = q @ Euler((0, roll, 0)).to_quaternion()
        return self.sphere(label, mat, p, (sx, thick, sz), quat=q, seg=24, rings=12)

    def body_disc(self, label, mat, angle, z, s, thick=0.003, lift=0.004, sz=None):
        rx, ry = torso_r(z)
        p = Vector((rx * math.sin(angle), -ry * math.cos(angle), z))
        n = Vector((math.sin(angle) / rx, -math.cos(angle) / ry, 0)).normalized()
        q = n.to_track_quat("-Y", "Z")
        return self.sphere(label, mat, p + n * lift, (s, thick, sz or s), quat=q,
                           cat="torso", seg=16, rings=8)


def azim(n):
    """Hoek rond het hoofd van richting n (0 = voorkant, > 0 richting +x)."""
    return math.atan2(n.x, -n.y)


def hairline(front, mid, side, back):
    """Haarlijn (n.z) als functie van de hoek a: voorkant, 35°, zijkant, achterkant."""
    pts = [(0.0, front), (math.radians(35), mid), (math.pi / 2, side), (math.pi, back)]

    def thr(a):
        a = abs(a)
        for (a0, t0), (a1, t1) in zip(pts, pts[1:]):
            if a <= a1:
                return t0 + (t1 - t0) * smoothstep((a - a0) / (a1 - a0))
        return back
    return thr


# ---------------------------------------------------------------------------
# Vervorming: lichaamsbouw per figuur
# ---------------------------------------------------------------------------
def make_warp(b):
    leg_s = b.get("leg", 1.0)
    torso_s = b.get("torso", 1.0)
    width = b.get("width", 1.0)
    depth = b.get("depth", width)
    hipw = b.get("hips", 1.0)
    shw = b.get("shoulders", 1.0)
    arm_t = b.get("arm", 1.0)
    leg_t = b.get("legt", arm_t)
    belly = b.get("belly", 0.0)
    head_s = b.get("head", 1.0)

    def Z(z):
        return z * leg_s if z < 0.6 else 0.6 * leg_s + (z - 0.6) * torso_s

    def Zarm(z):
        return 0.6 * leg_s + (z - 0.6) * torso_s

    def tw(z):
        return width * (hipw + (shw - hipw) * smoothstep((z - 0.6) / 0.6))

    def bel(z):
        return belly * math.exp(-((z - 0.82) / 0.17) ** 2)

    def torso(v):
        g = bel(v.z)
        x = v.x * tw(v.z) * (1 + 0.45 * g)
        y = v.y * depth * ((1 + g) if v.y < 0 else (1 + 0.35 * g))
        return Vector((x, y, Z(v.z)))

    def arm(v, side):
        cx = 0.21 * side
        ncx = cx * width * shw + side * 0.19 * width * 0.45 * belly * 0.8
        return Vector((ncx + (v.x - cx) * arm_t, (v.y + 0.03) * arm_t - 0.03, Zarm(v.z)))

    def leg(v, side, shoe=False):
        cx = 0.087 * side
        ncx = cx * width * hipw
        if shoe:
            return Vector((ncx + (v.x - cx) * leg_t, v.y * leg_t, v.z * leg_t))
        return Vector((ncx + (v.x - cx) * leg_t, v.y * leg_t, Z(v.z)))

    pivot_new = Vector((0, 0, Z(NECK_PIVOT.z)))

    def head(v):
        return pivot_new + (v - NECK_PIVOT) * head_s

    def apply(ob, cat):
        me = ob.data
        shoe = ob.get("schoen", False)
        for vert in me.vertices:
            co = vert.co.copy()
            if cat == "head":
                vert.co = head(co)
            elif cat == "torso":
                vert.co = torso(co)
            elif cat.startswith("arm"):
                vert.co = arm(co, +1 if cat[-1] == "+" else -1)
            elif cat.startswith("leg"):
                vert.co = leg(co, +1 if cat[-1] == "+" else -1, shoe)
        me.update()
        for mod in ob.modifiers:
            if mod.type == "SOLIDIFY":
                mod.thickness *= head_s if cat == "head" else 1.0

    return apply, head(HEAD_C)


# ---------------------------------------------------------------------------
# De figuren
# ---------------------------------------------------------------------------
SKIN = {
    "licht": ("#F3C8A6", "#D9A27E"),   # zelfde huidskleur als het hoofdpersonage
    "roze": ("#F1BC9F", "#D59A7C"),
    "olijf": ("#DDB08A", "#BE8D69"),
    "midden": ("#C98E62", "#A8714A"),
    "bruin": ("#9C6644", "#7F5034"),
    "donker": ("#6E4630", "#573524"),
}
EYES = {
    "bruin": ("#8A5A2B", "#774A22"),
    "blauw": ("#4F86C6", "#3B6CA6"),
    "groen": ("#5E8F4E", "#4B763E"),
    "grijs": ("#7D8B99", "#66727F"),
    "donker": ("#4A2E1A", "#3A2313"),
}

CAST = [
    dict(key="mama", naam="Mama", rol="MOM",
         body=dict(leg=1.0, torso=0.98, width=0.94, hips=1.06, shoulders=0.92, arm=0.88, head=0.97),
         skin="licht", eyes="groen", brows=dict(color="#5A3A22"),
         mouth="smile", lashes=True, earrings="#E2B84B",
         shirt=dict(color="#2F9C95", sleeves="long", cuff="#278680"),
         pants="#3E5C8A", shoes="#F2EEE8",
         hair=dict(style="ponytail", color="#7A4B2A")),
    dict(key="papa", naam="Papa", rol="DAD",
         body=dict(leg=1.05, torso=1.06, width=1.12, shoulders=1.04, arm=1.08, belly=0.38, head=1.0),
         skin="licht", eyes="blauw", brows=dict(color="#4A3020", scale=1.15, raise_=0.004),
         mouth="grin",
         shirt=dict(color="#2C8FC9", sleeves="short", dots=("#F6D04D", "#FFFFFF")),
         pants="#C8A97A", shoes="#6B4A31",
         hair=dict(style="short", color="#5B3A24"), beard=dict(color="#5B3A24")),
    dict(key="broertje", naam="Broertje (8)", rol="BROTHER",
         body=dict(leg=0.56, torso=0.6, width=0.86, arm=0.8, legt=0.82, head=0.9),
         skin="licht", eyes="blauw", brows=dict(color="#8A5530", raise_=0.006),
         mouth="grin", freckles=True,
         shirt=dict(color="#F2F2F2", sleeves="short", stripes="#E5483E"),
         shorts="#3D5A80", shoes="#E5483E",
         hair=dict(style="spiky", color="#9B6438")),
    dict(key="opa", naam="Opa", rol="GRANDPA",
         body=dict(leg=0.96, torso=1.0, width=1.06, arm=0.95, belly=0.3, head=1.0),
         skin="roze", eyes="grijs", brows=dict(color="#EDEDED", scale=1.45, angle=9),
         mouth="flat", mustache="#EDEDED",
         glasses=dict(color="#5A3B26", r=0.006),
         shirt=dict(color="#DCE6F0", sleeves="long", cuff="#C9D4E0"), tie="#7B2D26",
         cardigan=dict(color="#6E6B3A", buttons="#3A2A1A"),
         pants="#5D5850", shoes="#3A2A1A",
         hair=dict(style="bald_sides", color="#EDEDED"), hat="flatcap", prop="cane"),
    dict(key="oma", naam="Oma", rol="GRANDMA",
         body=dict(leg=0.9, torso=0.95, width=1.04, hips=1.08, shoulders=0.95, arm=0.92,
                   belly=0.22, head=0.97),
         skin="roze", eyes="blauw", brows=dict(color="#CFCFCF", angle=-10, raise_=0.004),
         mouth="smile", lashes=True, blush="#F08A8A",
         glasses=dict(color="#D4AF37", r=0.005, round_=True),
         shirt=dict(color="#F4E9F2", sleeves="long", cuff="#B58FC9"),
         cardigan=dict(color="#B58FC9", buttons="#F4E9F2"), pearls=True,
         skirt=dict(color="#7A3E6A", bottom=0.16),
         legs="#E8C3A5", shoes="#5B3A4E",
         hair=dict(style="curly_bun", color="#E6E3E0")),
    dict(key="beste_vriend", naam="Beste vriend", rol="FRIEND",
         body=dict(leg=1.04, torso=0.98, width=0.9, arm=0.86, head=1.0),
         skin="donker", eyes="donker", brows=dict(color="#1E1410", raise_=0.006),
         mouth="grin",
         shirt=dict(color="#6CBF4B", sleeves="short"),
         pants="#2E3440", shoes="#E9483B",
         hair=dict(style="curly", color="#1E1410"), prop="phone"),
    dict(key="pestkop", naam="Pestkop", rol="BULLY",
         body=dict(leg=1.06, torso=1.1, width=1.24, shoulders=1.14, hips=0.96, arm=1.3,
                   legt=1.15, head=0.93),
         skin="midden", eyes="bruin", brows=dict(color="#2A1A10", scale=1.25, angle=20,
                                                 raise_=-0.006),
         mouth="smirk",
         shirt=dict(color="#F2F2F2", sleeves="long", sleeve_color="#1F1F22", cuff="#1F1F22"),
         jacket=dict(color="#1F1F22"),
         pants="#4B6A8F", shoes="#F2F2F2",
         hair=dict(style="buzz", color="#2A1A10")),
    dict(key="zusje_pestkop", naam="Zusje van de pestkop", rol="(geen tekst)",
         body=dict(leg=0.46, torso=0.5, width=0.78, arm=0.72, legt=0.72, head=0.86),
         skin="midden", eyes="bruin", brows=dict(color="#2A1A10", raise_=0.008),
         mouth="smile", lashes=True, blush="#F08A8A",
         shirt=dict(color="#F59AC2", sleeves="short"),
         skirt=dict(color="#F59AC2", bottom=0.38, flare=1.4),
         legs="SKIN", shoes="#FFFFFF",
         hair=dict(style="pigtails", color="#2A1A10", ribbon="#FFE14D"), prop="cottoncandy"),
    dict(key="gymleraar", naam="Gymleraar", rol="(geen tekst)",
         body=dict(leg=1.04, torso=1.08, width=1.16, shoulders=1.08, arm=1.12, belly=0.3,
                   head=1.0),
         skin="roze", eyes="blauw", brows=dict(color="#7A5236", scale=1.2),
         mouth="smile", mustache="#7A5236",
         shirt=dict(color="#2257B8", sleeves="long", cuff="#FFFFFF", zipper="#FFFFFF"),
         pants="#2257B8", pant_stripes="#FFFFFF", shoes="#FFFFFF",
         hair=dict(style="receding", color="#7A5236"), whistle=True),
    dict(key="wetenschapper", naam="Wetenschapper", rol="SCIENTIST",
         body=dict(leg=1.02, torso=1.0, width=0.95, hips=1.03, shoulders=0.95, arm=0.9,
                   head=0.98),
         skin="olijf", eyes="donker", brows=dict(color="#1E1612"),
         mouth="smile", lashes=True,
         glasses=dict(color="#1A1A1A", r=0.008),
         shirt=dict(color="#A9C7E8", sleeves="long", sleeve_color="#FAFAFA", cuff="#E8E8E8"),
         labcoat=True,
         pants="#2F3542", shoes="#2F3542",
         hair=dict(style="bun", color="#1E1612"), prop="clipboard"),
    dict(key="nieuwslezeres", naam="Nieuwslezeres", rol="NEWS",
         body=dict(leg=1.04, torso=0.98, width=0.92, hips=1.05, shoulders=0.92, arm=0.86,
                   head=0.97),
         skin="bruin", eyes="donker", brows=dict(color="#24160F"),
         mouth="smile", lashes=True, earrings="#E2B84B",
         shirt=dict(color="#FAFAFA", sleeves="long", sleeve_color="#C8283A", cuff="#C8283A"),
         blazer=dict(color="#C8283A"),
         pants="#23232A", shoes="#23232A",
         hair=dict(style="bob", color="#24160F"), prop="microphone"),
    dict(key="officier", naam="Legerofficier", rol="OFFICER",
         body=dict(leg=1.08, torso=1.1, width=1.18, shoulders=1.12, arm=1.15, head=0.98),
         skin="donker", eyes="donker", brows=dict(color="#1A110C", scale=1.2, angle=8,
                                                  raise_=-0.004),
         mouth="flat",
         shirt=dict(color="#5B6B3A", sleeves="long", cuff="#4E5C32"),
         uniform=True,
         pants="#5B6B3A", shoes="#1A1A1A",
         hair=dict(style="buzz", color="#1A110C"), hat="peaked"),
]


# Video 2 "What IF You Got 10x FASTER Every Day?": nieuwe varianten en figuranten.
# De vaste cast (gezin, vriend, pestkop, wetenschapper, gymleraar) komt uit CAST.
CAST_10X = [
    dict(key="broertje_dino", naam="Broertje in dinopyjama", rol="BROTHER",
         body=dict(leg=0.56, torso=0.6, width=0.9, arm=0.8, legt=0.86, head=0.9),
         skin="licht", eyes="blauw", brows=dict(color="#8A5530", raise_=0.006),
         mouth="grin", freckles=True,
         shirt=dict(color="#5DB045", sleeves="long", cuff="#4E9A3A"),
         pants="#5DB045", shoes="#4E9A3A",
         onesie=dict(color="#5DB045", spikes="#F6A23A", belly="#C9EBA8"),
         hair=dict(style="spiky", color="#9B6438")),
    dict(key="bezorger", naam="Bestelbusbestuurder", rol="(geen tekst)",
         body=dict(leg=1.02, torso=1.06, width=1.12, shoulders=1.06, arm=1.08, belly=0.32, head=1.0),
         skin="bruin", eyes="donker", brows=dict(color="#24160F", scale=1.15),
         mouth="smile", mustache="#24160F",
         shirt=dict(color="#7A4E2D", sleeves="short"), chest_logo="#F2B33D",
         pants="#5A3A22", shoes="#2A2A2A",
         hair=dict(style="buzz", color="#24160F"), hat="cap",
         cap=dict(color="#7A4E2D", visor="#F2B33D", logo="#F2B33D")),
    dict(key="vuilnisman", naam="Vuilniswagenchauffeur", rol="(geen tekst)",
         body=dict(leg=1.04, torso=1.08, width=1.2, shoulders=1.12, arm=1.15, belly=0.36, head=1.0),
         skin="roze", eyes="blauw", brows=dict(color="#8A5530", scale=1.25),
         mouth="flat", mustache="#8A5530",
         shirt=dict(color="#3D4A3F", sleeves="long", cuff="#333D35"),
         vest=dict(color="#FF7A1A", stripes="#DADDE2"),
         pants="#2E3440", pant_stripes="#DADDE2", shoes="#1A1A1A",
         hair=dict(style="buzz", color="#8A5530"), hat="beanie", beanie="#2E3440"),
    dict(key="klasgenoot_a", naam="Klasgenote", rol="(geen tekst)",
         body=dict(leg=0.86, torso=0.86, width=0.86, hips=1.02, arm=0.82, head=0.95),
         skin="olijf", eyes="bruin", brows=dict(color="#3B2416", raise_=0.006),
         mouth="smile", lashes=True,
         shirt=dict(color="#F4F4F4", sleeves="short"), chest_logo="#2257B8",
         shorts="#22325E", shoes="#FFFFFF",
         hair=dict(style="ponytail", color="#3B2416")),
    dict(key="klasgenoot_b", naam="Klasgenoot", rol="(geen tekst)",
         body=dict(leg=0.9, torso=0.88, width=0.92, arm=0.86, head=0.96),
         skin="bruin", eyes="donker", brows=dict(color="#1E1410", raise_=0.004),
         mouth="grin",
         shirt=dict(color="#F4F4F4", sleeves="short"), chest_logo="#2257B8",
         shorts="#22325E", shoes="#F6D04D",
         hair=dict(style="curly", color="#1E1410")),
    dict(key="klasgenoot_c", naam="Klasgenoot", rol="(geen tekst)",
         body=dict(leg=0.84, torso=0.86, width=1.0, arm=0.84, belly=0.15, head=0.96),
         skin="licht", eyes="groen", brows=dict(color="#C9772E", raise_=0.006),
         mouth="smile", freckles=True,
         shirt=dict(color="#F4F4F4", sleeves="short"), chest_logo="#2257B8",
         shorts="#22325E", shoes="#2D6CDF",
         hair=dict(style="short", color="#C9772E")),
]


# ---------------------------------------------------------------------------
# Opbouw van één figuur
# ---------------------------------------------------------------------------
def build_character(spec, base_parts, unlit_tpl, parent_coll):
    key = spec["key"]
    coll = bpy.data.collections.new(key)
    parent_coll.children.link(coll)
    mats = Mats(unlit_tpl, key)
    B = Builder(coll, key, mats)

    skin, skin_dark = SKIN[spec["skin"]]
    M_skin = mats.pbr(skin)
    M_skin_dark = mats.pbr(skin_dark)
    shirt = spec["shirt"]
    M_shirt = mats.pbr(shirt["color"])
    M_sleeve = mats.pbr(shirt.get("sleeve_color", shirt["color"]))
    M_cuff = mats.pbr(shirt.get("cuff", shirt.get("sleeve_color", shirt["color"])))
    pants_col = spec.get("pants") or spec.get("shorts") or "#333333"
    legs_col = spec.get("legs")
    if legs_col == "SKIN" or spec.get("shorts"):
        M_legs = M_skin
    elif legs_col:
        M_legs = mats.pbr(legs_col)
    else:
        M_legs = mats.pbr(pants_col)
    M_shoes = mats.pbr(spec.get("shoes", "#F2EEE8"))
    iris1, iris2 = EYES[spec.get("eyes", "bruin")]
    brows = spec.get("brows", {})
    M_brow = mats.unlit(brows.get("color", "#3B2416"))
    M_line = mats.unlit("#1B1214")
    M_mouth = mats.unlit("#3B2416")

    long_hair = spec.get("hair", {}).get("style") in ("bob",) or bool(spec.get("onesie"))

    # --- 1. kopie van het hoofdpersonage ------------------------------------
    parts = {}
    for i, src in base_parts.items():
        if i in HOODIE_EXTRAS:
            continue
        if long_hair and i in (29, 30, 31, 32):
            continue
        if spec.get("mouth") == "flat" and i in (53, 54):
            continue
        me = src.data.copy()
        me.transform(src.matrix_world)
        ob = bpy.data.objects.new(f"{key}_{PART_NAMES[i]}", me)
        coll.objects.link(ob)
        if i in (1, 3):
            ob["schoen"] = True
        parts[i] = ob
        B.items.append((ob, part_cat(i)))

    def setmat(idx, mat):
        if idx in parts:
            parts[idx].data.materials[0] = mat

    for i in (0, 2):
        setmat(i, M_legs)
    for i in (1, 3):
        setmat(i, M_shoes)
    setmat(4, M_shirt)
    sleeves = shirt.get("sleeves", "long")
    for up, low, elb, cuff in ((13, 14, 15, 16), (20, 21, 22, 23)):
        setmat(up, M_sleeve)
        if sleeves == "short":
            setmat(low, M_skin)
            setmat(elb, M_skin)
            setmat(cuff, M_skin)
        else:
            setmat(low, M_sleeve)
            setmat(elb, M_sleeve)
            setmat(cuff, M_cuff)
    for i in (17, 18, 19, 24, 25, 26, 27, 28, 29, 31):
        setmat(i, M_skin)
    for i in (30, 32):
        setmat(i, M_skin_dark)
    for i in (35, 42):
        setmat(i, mats.unlit(iris1))
    for i in (36, 43):
        setmat(i, mats.unlit(iris2))
    for i in (33, 40):
        setmat(i, M_line)
    for i in (47, 48, 49, 50, 51, 52):
        setmat(i, M_brow)
    setmat(53, M_mouth)

    if sleeves == "short":
        # mouwzoom net boven de elleboog
        for side in (-1, +1):
            B.cylinder(f"mouwzoom_{'L' if side > 0 else 'R'}", M_sleeve,
                       (0.235 * side, -0.035, 0.93), (0.215 * side, -0.02, 1.0), 0.056,
                       cat="arm+" if side > 0 else "arm-")

    # --- 2. gezicht -----------------------------------------------------------
    def transform_parts(idxs, M):
        for i in idxs:
            if i in parts:
                parts[i].data.transform(M)

    def about(c, M):
        return Matrix.Translation(c) @ M @ Matrix.Translation(-c)

    for side in (-1, +1):
        c = face_point(BROW_C[side].x, BROW_C[side].z, 0)[0]
        ang = math.radians(brows.get("angle", 0.0)) * (1 if side < 0 else -1)
        s = brows.get("scale", 1.0)
        M = Matrix.Translation((0, -0.002 * (s - 1) * 10, brows.get("raise_", 0.0))) @ \
            about(c, Matrix.Rotation(ang, 4, "Y") @ Matrix.Scale(s, 4))
        transform_parts(BROW_PARTS[side], M)

    mouth = spec.get("mouth", "smile")
    mc = face_point(MOUTH_C.x, MOUTH_C.z, 0)[0]
    if mouth == "small":
        transform_parts((53, 54), about(mc, Matrix.Scale(0.7, 4)))
    elif mouth == "grin":
        transform_parts((53, 54), about(mc, Matrix.Diagonal((1.2, 1, 1.1, 1))))
    elif mouth == "smirk":
        transform_parts((53, 54), Matrix.Translation((0.012, 0.001, 0.003)) @
                        about(mc, Matrix.Rotation(math.radians(12), 4, "Y") @
                              Matrix.Diagonal((0.9, 1, 0.55, 1))))
    elif mouth == "flat":
        B.face_disc("mond", M_mouth, 0.0, 1.365, 0.036, 0.0055)

    if spec.get("lashes"):
        M_lash = mats.unlit("#1B1214")
        for side in (-1, +1):
            e = EYE_C[side]
            for k, ang in enumerate((25, 55)):
                a = math.radians(ang)
                base = Vector((e.x + side * 0.031, 0, e.z + 0.022 + 0.008 * k))
                d = Vector((side * math.cos(a), 0, math.sin(a)))
                c = base + d * 0.012
                B.face_disc(f"wimper_{'L' if side > 0 else 'R'}{k}", M_lash, c.x, c.z,
                            0.013, 0.0035, lift=0.004, roll=-side * a)
    if spec.get("blush"):
        M_bl = mats.pbr(spec["blush"], rough=1.0)
        for side in (-1, +1):
            B.face_disc(f"blos_{'L' if side > 0 else 'R'}", M_bl, side * 0.145, 1.42,
                        0.038, 0.022, lift=0.002)
    if spec.get("freckles"):
        M_fr = mats.unlit("#B9784E")
        rnd = random.Random(8)
        for side in (-1, +1):
            for k in range(6):
                x = side * (0.12 + rnd.uniform(-0.03, 0.035))
                z = 1.43 + rnd.uniform(-0.025, 0.02)
                B.face_disc(f"sproet_{'L' if side > 0 else 'R'}{k}", M_fr, x, z, 0.006, 0.006)
    if spec.get("earrings") and not long_hair:
        M_g = mats.pbr(spec["earrings"], rough=0.3, metal=1.0)
        for side in (-1, +1):
            B.sphere(f"oorbel_{'L' if side > 0 else 'R'}", M_g, (side * 0.315, -0.03, 1.36),
                     (0.018, 0.018, 0.018))
    elif spec.get("earrings"):
        M_g = mats.pbr(spec["earrings"], rough=0.3, metal=1.0)
        for side in (-1, +1):
            B.sphere(f"oorbel_{'L' if side > 0 else 'R'}", M_g, (side * 0.27, -0.12, 1.31),
                     (0.02, 0.02, 0.02))

    if spec.get("mustache"):
        M_m = mats.pbr(spec["mustache"])
        for side in (-1, +1):
            p, n = face_point(side * 0.034, 1.402, 0.006)
            q = n.to_track_quat("-Y", "Z") @ Euler((0, side * math.radians(14), 0)).to_quaternion()
            B.sphere(f"snor_{'L' if side > 0 else 'R'}", M_m, p, (0.042, 0.016, 0.017), quat=q)

    if spec.get("glasses"):
        g = spec["glasses"]
        M_gl = mats.pbr(g["color"], rough=0.35, metal=0.6 if g.get("round_") else 0.0)
        rr = 0.058 if not g.get("round_") else 0.054
        inner = {}
        for side in (-1, +1):
            e = face_point(EYE_C[side].x, EYE_C[side].z, 0)[0]
            n = (e - HEAD_C).normalized()
            c = HEAD_C + n * (HEAD_R + 0.022)
            sc = (1.0, 1.0, 1.0) if g.get("round_") else (1.12, 0.92, 1.0)
            B.torus(f"bril_glas_{'L' if side > 0 else 'R'}", M_gl, c, rr, g["r"], normal=n,
                    scale=sc)
            inner[side] = c + Vector((-side * rr * sc[0], 0, 0))
            outer = c + Vector((side * rr * sc[0], 0, 0))
            B.cylinder(f"bril_poot_{'L' if side > 0 else 'R'}", M_gl, outer,
                       (side * 0.305, -0.02, 1.50), g["r"] * 0.8, cat="head", seg=10)
        B.cylinder("bril_brug", M_gl, inner[-1] + Vector((0, 0, 0.008)),
                   inner[+1] + Vector((0, 0, 0.008)), g["r"] * 0.8, cat="head", seg=10)

    # --- 3. haar ----------------------------------------------------------------
    hair = spec.get("hair")
    if hair and not spec.get("onesie"):
        M_h = mats.pbr(hair["color"], rough=0.75)
        st = hair["style"]
        if st == "short":
            thr = hairline(0.48, 0.42, 0.18, -0.38)
            B.shell("haar", M_h, thr, scale=(1.0, 1.0, 1.03), thick=0.02)
            B.sphere("haar_kuif", M_h, (0.05, -0.17, 1.72), (0.17, 0.12, 0.07),
                     rot=(math.radians(-25), 0, math.radians(-15)))
        elif st == "buzz":
            thr = hairline(0.5, 0.44, 0.15, -0.4)
            B.shell("haar", M_h, thr, radius=HEAD_R * 1.012, thick=0.004)
        elif st == "receding":
            thr = hairline(0.72, 0.55, 0.12, -0.36)
            B.shell("haar", M_h, thr, radius=HEAD_R * 1.02, thick=0.008)
        elif st == "bald_sides":
            a_end = math.radians(68)

            def lo(a):
                t = smoothstep((abs(a) - a_end) / math.radians(30))
                return -0.3 + 0.32 * (1 - t)

            def hi(a):
                t = smoothstep((abs(a) - a_end) / math.radians(30))
                return 0.02 + 0.26 * t
            B.shell("haar", M_h, lo, hi, arange=(a_end, 2 * math.pi - a_end),
                    radius=HEAD_R * 1.04, thick=0.02, scale=(1.05, 1.0, 1.0))
        elif st == "spiky":
            thr = hairline(0.5, 0.42, 0.15, -0.35)
            B.shell("haar", M_h, thr, radius=HEAD_R * 1.03, thick=0.02)
            rnd = random.Random(3)
            k = 0
            for a_deg in range(-150, 181, 30):
                for el in (60, 78):
                    a = math.radians(a_deg + rnd.uniform(-8, 8) + (15 if el == 78 else 0))
                    e = math.radians(el + rnd.uniform(-5, 5))
                    n = Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)))
                    if n.y < -0.55 and n.z < 0.8:
                        continue
                    p1 = HEAD_C + n * (HEAD_R * 0.98)
                    p2 = HEAD_C + n * (HEAD_R + 0.085 + rnd.uniform(-0.02, 0.02)) + Vector((0, 0.02, 0.0))
                    B.cylinder(f"haar_piek{k}", M_h, p1, p2, 0.055, 0.004, cat="head", seg=12)
                    k += 1
        elif st == "curly":
            thr = hairline(0.5, 0.42, 0.18, -0.3)
            B.shell("haar", M_h, thr, radius=HEAD_R * 1.04, thick=0.02)
            rnd = random.Random(5)
            k = 0
            for _ in range(260):
                n = Vector((rnd.gauss(0, 1), rnd.gauss(0, 1), rnd.gauss(0, 1))).normalized()
                if n.z <= thr(azim(n)) + 0.06:
                    continue
                r = rnd.uniform(0.04, 0.06)
                B.sphere(f"krul{k}", M_h, HEAD_C + n * (HEAD_R + 0.045), (r, r, r), seg=12, rings=8)
                k += 1
        elif st == "ponytail":
            thr = hairline(0.42, 0.36, 0.1, -0.4)

            def lo(a):   # schuine pony over het voorhoofd
                if abs(a) > math.pi / 2:
                    return thr(a)
                return thr(a) - 0.12 * smoothstep((math.sin(a) + 0.4) / 0.8) * math.cos(a)
            B.shell("haar", M_h, lo, radius=HEAD_R * 1.035, thick=0.018, scale=(1.02, 1.03, 1.03))
            B.sphere("haar_elastiek", mats.pbr("#E5483E"), (0, 0.29, 1.58), (0.045, 0.03, 0.045))
            B.sphere("staart", M_h, (0, 0.36, 1.43), (0.085, 0.09, 0.2),
                     rot=(math.radians(-18), 0, 0))
            B.sphere("staart_punt", M_h, (0, 0.38, 1.27), (0.06, 0.07, 0.1),
                     rot=(math.radians(-8), 0, 0))
        elif st == "bun":
            thr = hairline(0.44, 0.38, 0.12, -0.38)
            B.shell("haar", M_h, lambda a: thr(a) - 0.07 * max(0.0, math.cos(a * 2.2)) * (abs(a) < 0.72),
                    radius=HEAD_R * 1.03, thick=0.016)
            B.sphere("knot", M_h, (0, 0.2, 1.77), (0.11, 0.11, 0.1))
            B.torus("knot_band", mats.pbr("#2D6CDF"), (0, 0.17, 1.735), 0.07, 0.012,
                    normal=(0, 0.6, -0.8))
        elif st == "curly_bun":
            thr = hairline(0.48, 0.4, 0.15, -0.3)
            B.shell("haar", M_h, thr, radius=HEAD_R * 1.05, thick=0.02)
            rnd = random.Random(11)
            k = 0
            for _ in range(200):
                n = Vector((rnd.gauss(0, 1), rnd.gauss(0, 1), rnd.gauss(0, 1))).normalized()
                if n.z <= thr(azim(n)) + 0.05:
                    continue
                r = rnd.uniform(0.035, 0.05)
                B.sphere(f"krul{k}", M_h, HEAD_C + n * (HEAD_R * 1.05 + 0.03), (r, r, r), seg=12, rings=8)
                k += 1
            for _ in range(40):
                n = Vector((rnd.gauss(0, 1), rnd.gauss(0, 1), rnd.gauss(0.2, 1))).normalized()
                r = rnd.uniform(0.035, 0.05)
                B.sphere(f"knotkrul{k}", M_h, Vector((0, 0.08, 1.84)) + n * 0.085, (r, r, r),
                         seg=12, rings=8)
                k += 1
        elif st == "bob":
            thr = hairline(0.42, 0.32, -0.55, -0.62)

            def lo(a):   # scheiding opzij
                if abs(a) > math.pi / 2:
                    return thr(a)
                return thr(a) - 0.1 * smoothstep((-math.sin(a) + 0.3) / 0.6) * math.cos(a)
            B.shell("haar", M_h, lo, radius=HEAD_R * 1.04, thick=0.03, scale=(1.1, 1.06, 1.0))
        elif st == "pigtails":
            thr = hairline(0.45, 0.38, 0.1, -0.35)
            B.shell("haar", M_h, thr, radius=HEAD_R * 1.03, thick=0.016)
            M_rb = mats.pbr(hair.get("ribbon", "#FFE14D"))
            for side in (-1, +1):
                s = "L" if side > 0 else "R"
                B.sphere(f"staartje_{s}", M_h, (side * 0.35, 0.05, 1.55), (0.1, 0.085, 0.13),
                         rot=(0, side * math.radians(-30), 0))
                B.sphere(f"strik_{s}", M_rb, (side * 0.29, 0.03, 1.62), (0.035, 0.03, 0.05),
                         rot=(0, side * math.radians(-30), 0))

    if spec.get("beard"):
        M_b = mats.pbr(spec["beard"]["color"], rough=0.8)

        def hi(a):   # onder de mond door, langs de wangen omhoog naar de bakkebaarden
            t = smoothstep((abs(a) - math.radians(16)) / math.radians(52))
            return -0.47 + 0.67 * t
        B.shell("baard", M_b, lambda a: -0.97, hi, arange=(-math.radians(100), math.radians(100)),
                radius=HEAD_R * 1.035, thick=0.022)
        for side in (-1, +1):
            p, n = face_point(side * 0.034, 1.402, 0.005)
            q = n.to_track_quat("-Y", "Z") @ Euler((0, side * math.radians(10), 0)).to_quaternion()
            B.sphere(f"snor_{'L' if side > 0 else 'R'}", M_b, p, (0.04, 0.014, 0.014), quat=q)

    # --- 4. hoofddeksels -------------------------------------------------------
    hat = spec.get("hat")
    if hat == "peaked":
        M_cr = mats.pbr("#5B6B3A")
        M_band = mats.pbr("#2B2A22")
        M_vis = mats.pbr("#141414", rough=0.3)
        M_gold = mats.pbr("#D4AF37", rough=0.3, metal=1.0)
        B.cylinder("pet_band", M_band, (0, 0.0, 1.60), (0, 0.0, 1.71), 0.288, cat="head", seg=48)
        B.sphere("pet_bol", M_cr, (0, 0.02, 1.735), (0.34, 0.355, 0.075), seg=48, rings=16)
        B.sphere("pet_klep", M_vis, (0, -0.27, 1.605), (0.2, 0.15, 0.018),
                 rot=(math.radians(14), 0, 0))
        B.sphere("pet_embleem", M_gold, (0, -0.287, 1.665), (0.028, 0.008, 0.03))
    elif hat == "flatcap":
        M_cap = mats.pbr("#7C6F5E")
        B.sphere("pet", M_cap, (0, 0.02, 1.675), (0.33, 0.345, 0.135), seg=48, rings=20)
        B.sphere("pet_klep", M_cap, (0, -0.28, 1.615), (0.19, 0.12, 0.022),
                 rot=(math.radians(10), 0, 0))
        B.sphere("pet_knoop", M_cap, (0, -0.1, 1.80), (0.022, 0.022, 0.012))

    elif hat == "cap":
        # honkbalpet in de kleur van spec["cap"], klep recht naar voren
        cc = spec.get("cap", {})
        M_cap = mats.pbr(cc.get("color", "#F2B33D"))
        M_vis = mats.pbr(cc.get("visor", cc.get("color", "#F2B33D")))
        B.shell("pet", M_cap, lambda a: 0.36 + 0.08 * math.cos(a), radius=HEAD_R * 1.05,
                scale=(1.0, 1.0, 1.02), thick=0.014)
        B.sphere("pet_klep", M_vis, (0, -0.33, 1.6), (0.17, 0.15, 0.016),
                 rot=(math.radians(-8), 0, 0))
        B.sphere("pet_knoop", M_cap, (0, 0.0, 1.785), (0.022, 0.022, 0.012))
        if cc.get("logo"):
            B.face_disc("pet_logo", mats.pbr(cc["logo"]), 0.0, 1.66, 0.04, 0.03, lift=0.02)
    elif hat == "beanie":
        M_bn = mats.pbr(spec.get("beanie", "#3A3F47"))
        B.shell("muts", M_bn, lambda a: 0.42, radius=HEAD_R * 1.06, scale=(1.0, 1.0, 1.08),
                thick=0.016)
        B.torus("muts_rand", M_bn, (0, 0, HEAD_C.z + HEAD_R * 0.4), HEAD_R * 0.98, 0.028,
                normal=(0, 0, 1), cat="head")

    # --- 4b. dinopyjama (onesie met capuchon, stekels, buik en staart) ----------
    if spec.get("onesie"):
        on = spec["onesie"]
        M_on = mats.pbr(on["color"])
        M_sp = mats.pbr(on.get("spikes", "#F28C28"))
        M_bel = mats.pbr(on.get("belly", "#BFE3A0"))
        M_ew = mats.pbr("#FFFFFF")
        M_ep = mats.unlit("#1B1214")

        def hood_lo(a):
            # open gezicht vooraan, aan de zijkanten en achter tot in de nek
            t = smoothstep((abs(a) - 0.75) / 0.6)
            return 0.5 * (1 - t) - 0.62 * t

        B.shell("capuchon", M_on, hood_lo, radius=HEAD_R * 1.075, thick=0.02)
        # oogjes van de dino bovenop de capuchon
        for side in (-1, +1):
            s_ = "L" if side > 0 else "R"
            c = HEAD_C + Vector((side * 0.11, -0.2, 0.235))
            B.sphere(f"dino_oog_{s_}", M_ew, c, (0.045, 0.04, 0.045))
            B.sphere(f"dino_pupil_{s_}", M_ep, c + Vector((0, -0.036, 0.005)), (0.02, 0.012, 0.024))
        # tandjes langs de rand van de capuchon
        for k in range(7):
            a = -0.55 + 1.1 * k / 6
            n = Vector((math.sin(a) * 0.86, -math.cos(a) * 0.86, 0.5)).normalized()
            p = HEAD_C + n * HEAD_R * 1.075
            B.cylinder(f"dino_tand{k}", M_ew, p, p + Vector((0, -0.004, -0.04)), 0.014, 0.0,
                       cat="head", seg=10)
        # stekels: over de kruin naar achter en dan langs de rug omlaag
        spikes = []
        for k in range(6):
            e = math.radians(112 - 22 * k)
            n = Vector((0, math.cos(e), math.sin(e))).normalized()
            p = HEAD_C + n * HEAD_R * 1.1
            spikes.append((p, n, 0.1 - 0.008 * k))
        for k, z in enumerate((1.08, 0.96, 0.84, 0.72)):
            ry = torso_r(z)[1]
            spikes.append((Vector((0, ry + 0.01, z)), Vector((0, 1, 0.25)).normalized(), 0.065 - 0.006 * k))
        for k, (p, n, h) in enumerate(spikes):
            B.cylinder(f"dino_stekel{k}", M_sp, p - n * 0.01, p + n * h, h * 0.55, 0.004,
                       cat="torso", seg=12, squash=0.45)
        B.body_disc("dino_buik", M_bel, 0.0, 0.84, 0.12, thick=0.006, lift=0.006, sz=0.2)
        # staart
        tail = [(0, 0.14, 0.7), (0, 0.3, 0.6), (0, 0.44, 0.48), (0, 0.55, 0.42)]
        rads = [0.085, 0.065, 0.04, 0.012]
        for k in range(3):
            B.cylinder(f"dino_staart{k}", M_on, tail[k], tail[k + 1], rads[k], rads[k + 1],
                       cat="torso", seg=20)
            B.sphere(f"dino_staart_bol{k}", M_on, tail[k + 1], (rads[k + 1],) * 3, cat="torso",
                     seg=16, rings=8)
        for k in range(3):
            p = Vector(tail[k + 1])
            B.cylinder(f"dino_staart_stekel{k}", M_sp, p, p + Vector((0, 0.01, 0.05 - 0.01 * k)),
                       0.025 - 0.005 * k, 0.003, cat="torso", seg=10, squash=0.45)

    # --- 5. kleding --------------------------------------------------------------
    def torso_ring(z, pad):
        rx, ry = torso_r(z)
        return (z, rx + pad, ry + pad)

    if shirt.get("stripes"):
        M_st = mats.pbr(shirt["stripes"])
        for k, z in enumerate((0.70, 0.82, 0.94, 1.06)):
            B.loft(f"streep{k}", M_st, [torso_ring(z - 0.022, 0.003), torso_ring(z + 0.022, 0.003)],
                   thick=0)
    if shirt.get("dots"):
        rnd = random.Random(2)
        cols = [mats.pbr(c) for c in shirt["dots"]]
        k = 0
        for z in (0.68, 0.76, 0.84, 0.92, 1.0, 1.08):
            for j in range(10):
                a = 2 * math.pi * (j + rnd.uniform(-0.3, 0.3) + (0.5 if k % 2 else 0)) / 10
                B.body_disc(f"bloem{k}_{j}", cols[(j + k) % len(cols)], a, z + rnd.uniform(-0.02, 0.02),
                            0.022)
            k += 1
    if shirt.get("zipper"):
        M_z = mats.pbr(shirt["zipper"])
        for z0, z1 in ((0.62, 1.16),):
            pts = [z0 + (z1 - z0) * t / 12 for t in range(13)]
            for k in range(12):
                za, zb = pts[k], pts[k + 1]
                B.box(f"rits{k}", M_z, (0, -torso_r((za + zb) / 2)[1] - 0.003, (za + zb) / 2),
                      (0.012, 0.006, zb - za + 0.004), bevel=0)
        B.loft("kraag", M_z, [(1.155, 0.17, 0.133), (1.21, 0.1, 0.08)], thick=0.006)

    if spec.get("pant_stripes"):
        M_ps = mats.pbr(spec["pant_stripes"])
        for side in (-1, +1):
            B.box(f"broekstreep_{'L' if side > 0 else 'R'}", M_ps, (side * 0.155, 0.0, 0.4),
                  (0.006, 0.02, 0.62), cat="leg+" if side > 0 else "leg-", bevel=0)

    if spec.get("shorts"):
        M_sh = mats.pbr(spec["shorts"])
        for side in (-1, +1):
            B.cylinder(f"short_{'L' if side > 0 else 'R'}", M_sh, (side * 0.09, 0, 0.44),
                       (side * 0.087, 0, 0.7), 0.082, 0.078, cat="leg+" if side > 0 else "leg-")
        B.loft("short_heup", M_sh, [(0.56, 0.17, 0.12), (0.62, 0.18, 0.14), (0.68, 0.192, 0.15)],
               thick=0)

    if spec.get("tie"):
        M_t = mats.pbr(spec["tie"])
        B.box("das_knoop", M_t, (0, -0.142, 1.135), (0.04, 0.02, 0.035), rot=(math.radians(-25), 0, 0))
        for k, (z0, z1, w0, w1) in enumerate(((1.12, 1.0, 0.035, 0.05), (1.0, 0.86, 0.05, 0.06))):
            zc = (z0 + z1) / 2
            B.box(f"das{k}", M_t, (0, -torso_r(zc)[1] - 0.006, zc), ((w0 + w1) / 2, 0.008, z0 - z1),
                  bevel=0.2)
        B.loft("kraag", mats.pbr(shirt["color"]), [(1.15, 0.168, 0.131), (1.205, 0.095, 0.075)],
               thick=0.006)

    if spec.get("cardigan"):
        c = spec["cardigan"]
        M_c = mats.pbr(c["color"])
        rings = [torso_ring(z, 0.012) for z in (0.62, 0.65, 0.7, 0.8, 0.9, 1.0, 1.1, 1.15, 1.18)]
        rings[0] = (0.62, 0.2, 0.158)
        B.loft("vest", M_c, rings,
               gap=lambda z: math.radians(8 + 22 * smoothstep((z - 0.85) / 0.3)), thick=0.01)
        M_bt = mats.pbr(c.get("buttons", "#333333"), rough=0.4)
        for k, z in enumerate((0.7, 0.78, 0.86)):
            B.body_disc(f"knoop{k}", M_bt, math.radians(11), z, 0.012, thick=0.006, lift=0.016)

    if spec.get("vest"):
        # veiligheidshesje zonder mouwen met twee reflecterende banden
        v = spec["vest"]
        M_v = mats.pbr(v["color"])
        M_ref = mats.pbr(v.get("stripes", "#DADDE2"), rough=0.15, metal=0.6)
        rings = [torso_ring(z, 0.014) for z in (0.62, 0.65, 0.7, 0.8, 0.9, 1.0, 1.1, 1.15)]
        rings[0] = (0.62, 0.2, 0.16)
        B.loft("hesje", M_v, rings, gap=lambda z: math.radians(6 + 20 * smoothstep((z - 0.9) / 0.25)),
               thick=0.01)
        for k, z in enumerate((0.74, 0.86)):
            B.loft(f"hesje_band{k}", M_ref, [torso_ring(z - 0.018, 0.026), torso_ring(z + 0.018, 0.026)],
                   gap=lambda z: math.radians(8), thick=0.004)
        if v.get("logo"):
            B.body_disc("hesje_logo", mats.pbr(v["logo"]), math.radians(28), 1.02, 0.03, thick=0.004,
                        lift=0.026)

    if spec.get("chest_logo"):
        B.body_disc("logo", mats.pbr(spec["chest_logo"]), math.radians(-28), 1.02, 0.032, thick=0.004,
                    lift=0.004, sz=0.026)

    if spec.get("pearls"):
        M_p = mats.pbr("#FBF7EE", rough=0.25)
        for k in range(26):
            t = 2 * math.pi * k / 26
            front = max(0.0, math.cos(t))
            z = 1.17 - 0.06 * front ** 2
            rx, ry = torso_r(z)
            B.sphere(f"parel{k}", M_p, ((rx + 0.01) * math.sin(t), -(ry + 0.01) * math.cos(t), z),
                     (0.013, 0.013, 0.013), seg=12, rings=8)

    if spec.get("jacket") or spec.get("blazer"):
        c = spec.get("jacket") or spec.get("blazer")
        M_j = mats.pbr(c["color"], rough=0.5 if spec.get("jacket") else 0.85)
        rings = [torso_ring(z, 0.013) for z in (0.63, 0.65, 0.7, 0.8, 0.9, 1.0, 1.1, 1.15, 1.18)]
        rings[0] = (0.6, 0.2, 0.158)
        rings.append((1.215, 0.095, 0.08))
        B.loft("jas", M_j, rings, gap=lambda z: math.radians(10 + 30 * smoothstep((z - 0.8) / 0.32)),
               thick=0.012)
        if spec.get("jacket"):
            M_zip = mats.pbr("#B0B0B0", rough=0.3, metal=1.0)
            for side in (-1, +1):
                B.body_disc(f"jas_drukker_{'L' if side > 0 else 'R'}", M_zip, side * math.radians(30),
                            1.05, 0.01, thick=0.006, lift=0.02)

    if spec.get("labcoat"):
        M_lc = mats.pbr("#FAFAFA")
        zs = [0.32, 0.45, 0.6, 0.65, 0.7, 0.8, 0.9, 1.0, 1.1, 1.15, 1.18]
        rings = []
        for z in zs:
            if z < 0.62:
                t = (0.62 - z) / 0.3
                rings.append((z, 0.205 + 0.03 * t, 0.162 + 0.026 * t))
            else:
                rings.append(torso_ring(z, 0.014))
        rings.append((1.215, 0.1, 0.085))
        B.loft("labjas", M_lc, rings, gap=lambda z: math.radians(9 + 26 * smoothstep((z - 0.85) / 0.3)),
               thick=0.01)
        M_pen = mats.pbr("#2D6CDF")
        B.body_disc("labjas_zakje", mats.pbr("#EDEDED"), math.radians(-32), 1.0, 0.04, thick=0.004,
                    lift=0.02, sz=0.035)
        B.cylinder("pen", M_pen, (-0.115, -0.185, 0.99), (-0.115, -0.18, 1.06), 0.007)
        B.body_disc("pasje", mats.pbr("#2D6CDF"), math.radians(30), 1.0, 0.03, thick=0.004,
                    lift=0.02, sz=0.04)

    if spec.get("uniform"):
        M_belt = mats.pbr("#4A3424", rough=0.5)
        M_gold = mats.pbr("#D4AF37", rough=0.3, metal=1.0)
        M_pk = mats.pbr("#4E5C32")
        B.loft("riem", M_belt, [torso_ring(0.66, 0.006), torso_ring(0.71, 0.006)], thick=0.006)
        B.box("gesp", M_gold, (0, -torso_r(0.685)[1] - 0.012, 0.685), (0.05, 0.01, 0.04), bevel=0.2)
        for side in (-1, +1):
            s = "L" if side > 0 else "R"
            B.body_disc(f"borstzak_{s}", M_pk, side * math.radians(30), 1.0, 0.05, thick=0.005,
                        lift=0.006, sz=0.045)
            B.box(f"epaulet_{s}", M_pk, (side * 0.15, 0.0, 1.17), (0.09, 0.07, 0.012),
                  rot=(0, side * math.radians(25), 0), bevel=0.2)
            B.box(f"rang_{s}", M_gold, (side * 0.155, -0.01, 1.178), (0.025, 0.025, 0.008),
                  rot=(0, side * math.radians(25), 0), bevel=0.2)
        for k, z in enumerate((0.78, 0.88, 0.98, 1.08)):
            B.body_disc(f"knoop{k}", M_gold, 0.0, z, 0.01, thick=0.005, lift=0.005)
        M_rib = [mats.pbr(c) for c in ("#C8283A", "#2D6CDF", "#F6D04D")]
        for k in range(3):
            B.body_disc(f"lintje{k}", M_rib[k], math.radians(26 + 7 * k), 1.07, 0.012, thick=0.004,
                        lift=0.008, sz=0.008)

    if spec.get("skirt"):
        sk = spec["skirt"]
        M_sk = mats.pbr(sk["color"])
        bottom = sk.get("bottom", 0.4)
        fl = sk.get("flare", 1.0)
        top = 0.74
        rings = [(top, 0.2, 0.158)]
        for k in range(1, 7):
            t = k / 6
            z = top + (bottom - top) * t
            rings.append((z, 0.2 + (0.06 * fl) * t, 0.158 + (0.05 * fl) * t))
        B.loft("rok", M_sk, rings, thick=0.008)

    if spec.get("whistle"):
        M_wh = mats.pbr("#C0C0C0", rough=0.25, metal=1.0)
        M_lan = mats.pbr("#E5483E")
        zc = 0.98
        yc = -torso_r(zc)[1] - 0.022
        B.cylinder("fluitje", M_wh, (-0.03, yc, zc), (0.03, yc, zc), 0.018, cat="torso")
        B.sphere("fluitje_bol", M_wh, (0.012, yc, zc - 0.018), (0.022, 0.022, 0.022))
        for side in (-1, +1):
            B.cylinder(f"koord_{'L' if side > 0 else 'R'}", M_lan, (side * 0.07, -0.09, 1.19),
                       (side * 0.012, yc + 0.006, zc + 0.012), 0.005, cat="torso", seg=8)

    # --- 6. rekwisieten in de rechterhand (-x) ---------------------------------
    prop = spec.get("prop")
    hand = Vector((-0.265, -0.08, 0.6))
    if prop == "phone":
        B.box("telefoon", mats.pbr("#1A1A1A", rough=0.3), hand + Vector((0.0, -0.06, 0.04)),
              (0.012, 0.075, 0.14), rot=(math.radians(10), 0, 0), cat="arm-", bevel=0.1)
        B.box("telefoon_scherm", mats.unlit("#6FB7FF"), hand + Vector((0.008, -0.06, 0.04)),
              (0.004, 0.065, 0.125), rot=(math.radians(10), 0, 0), cat="arm-", bevel=0)
    elif prop == "microphone":
        B.cylinder("microfoon", mats.pbr("#1A1A1A", rough=0.4), hand + Vector((0, -0.03, -0.04)),
                   hand + Vector((0, -0.03, 0.12)), 0.018, 0.024, cat="arm-")
        B.sphere("microfoon_kop", mats.pbr("#8A8A8A", rough=0.5), hand + Vector((0, -0.03, 0.15)),
                 (0.042, 0.042, 0.042), cat="arm-")
        B.box("microfoon_logo", mats.pbr("#2D6CDF"), hand + Vector((0, -0.03, 0.09)),
              (0.07, 0.07, 0.05), cat="arm-", bevel=0.1)
        B.box("microfoon_logo_tekst", mats.unlit("#FFFFFF"), hand + Vector((0, -0.066, 0.09)),
              (0.045, 0.002, 0.012), cat="arm-", bevel=0)
    elif prop == "clipboard":
        B.box("klembord", mats.pbr("#A0703D"), hand + Vector((-0.02, -0.05, 0.08)),
              (0.012, 0.2, 0.27), rot=(math.radians(-8), 0, 0), cat="arm-", bevel=0.1)
        B.box("klembord_papier", mats.pbr("#FFFFFF"), hand + Vector((-0.03, -0.05, 0.07)),
              (0.004, 0.17, 0.22), rot=(math.radians(-8), 0, 0), cat="arm-", bevel=0)
        B.box("klembord_klem", mats.pbr("#C0C0C0", metal=1.0, rough=0.3),
              hand + Vector((-0.03, -0.035, 0.2)), (0.012, 0.07, 0.03),
              rot=(math.radians(-8), 0, 0), cat="arm-", bevel=0.2)
    elif prop == "cane":
        M_wd = mats.pbr("#6B4A31", rough=0.6)
        B.cylinder("wandelstok", M_wd, (-0.3, -0.13, 0.0), hand + Vector((-0.035, -0.05, 0.03)), 0.016,
                   cat="arm-")
        B.torus("wandelstok_greep", M_wd, hand + Vector((-0.035, -0.0, 0.03)), 0.05, 0.016,
                normal=(1, 0, 0), arc=(0, math.pi), cat="arm-")
    elif prop == "cottoncandy":
        B.cylinder("suikerspin_stok", mats.pbr("#F2E6D0"), hand + Vector((0, -0.04, -0.02)),
                   hand + Vector((0, -0.04, 0.2)), 0.008, cat="arm-")
        rnd = random.Random(4)
        M_cc = mats.pbr("#FF9ECF", rough=1.0)
        for k in range(14):
            n = Vector((rnd.gauss(0, 1), rnd.gauss(0, 1), rnd.gauss(0, 1))).normalized()
            r = rnd.uniform(0.04, 0.06)
            B.sphere(f"suikerspin{k}", M_cc, hand + Vector((0, -0.04, 0.28)) + n * 0.06, (r, r, r),
                     cat="arm-", seg=12, rings=8)

    # --- 7. lichaamsbouw toepassen -------------------------------------------
    apply, head_c = make_warp(spec["body"])
    for ob, cat in B.items:
        apply(ob, cat)

    root = bpy.data.objects.new(key, None)
    coll.objects.link(root)
    root.empty_display_size = 0.3
    for ob, _ in B.items:
        ob.parent = root
    root["naam"] = spec["naam"]
    root["rol"] = spec["rol"]
    zmax = max((ob.matrix_world @ Vector(c)).z for ob, _ in B.items for c in ob.bound_box)
    return coll, root, head_c, zmax


# ---------------------------------------------------------------------------
# Scène, renders en export
# ---------------------------------------------------------------------------
def setup_render(samples):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.render.film_transparent = False
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Medium High Contrast"
    w = bpy.data.worlds.new("studio")
    sc.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (*lin("#DCE3EA"), 1)
    bg.inputs[1].default_value = 0.9

    studio = bpy.data.collections.new("studio")
    sc.collection.children.link(studio)
    floor = bpy.data.meshes.new("vloer")
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=30)
    bm.to_mesh(floor)
    bm.free()
    fo = bpy.data.objects.new("vloer", floor)
    studio.objects.link(fo)
    fm = bpy.data.materials.new("vloer")
    fm.use_nodes = True
    fm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*lin("#E6EBF0"), 1)
    fm.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 1.0
    floor.materials.append(fm)

    def light(name, kind, energy, rot, size=None, color="#FFFFFF"):
        ld = bpy.data.lights.new(name, kind)
        ld.energy = energy
        ld.color = lin(color)
        if size is not None:
            ld.angle = size
        lo = bpy.data.objects.new(name, ld)
        lo.rotation_euler = [math.radians(a) for a in rot]
        studio.objects.link(lo)
        return lo
    light("zon", "SUN", 3.2, (50, 0, 28), size=math.radians(8), color="#FFF4E6")
    light("tegenlicht", "SUN", 1.6, (60, 0, 200), size=math.radians(15), color="#DDEBFF")

    cam = bpy.data.objects.new("camera", bpy.data.cameras.new("camera"))
    studio.objects.link(cam)
    sc.camera = cam
    return cam


def aim(cam, loc, target, lens=50):
    cam.location = Vector(loc)
    cam.rotation_euler = (Vector(target) - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = lens


def set_visible(colls, visible_names):
    vl = bpy.context.view_layer
    for lc in vl.layer_collection.children["cast"].children:
        lc.exclude = lc.name not in visible_names


def render(path, rx, ry):
    sc = bpy.context.scene
    sc.render.resolution_x = rx
    sc.render.resolution_y = ry
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print("render:", path)


def add_label(text, loc, size=0.11, coll=None):
    cu = bpy.data.curves.new("label", "FONT")
    cu.body = text
    cu.size = size
    cu.align_x = "CENTER"
    cu.extrude = 0.004
    ob = bpy.data.objects.new(f"label_{text}", cu)
    ob.location = Vector(loc)
    ob.rotation_euler = (math.radians(90), 0, 0)
    m = bpy.data.materials.new("label")
    m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*lin("#2B2F36"), 1)
    cu.materials.append(m)
    (coll or bpy.context.scene.collection).objects.link(ob)
    return ob


def instance(coll, loc, rot_z=0.0, parent_coll=None):
    e = bpy.data.objects.new(f"inst_{coll.name}", None)
    e.instance_type = "COLLECTION"
    e.instance_collection = coll
    e.location = Vector(loc)
    e.rotation_euler = (0, 0, rot_z)
    (parent_coll or bpy.context.scene.collection).objects.link(e)
    return e


def export_glb(coll, path):
    bpy.ops.object.select_all(action="DESELECT")
    for ob in coll.all_objects:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = next(iter(coll.all_objects))
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", use_selection=True,
                              export_apply=True, export_yup=True)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    here = os.path.dirname(os.path.abspath(__file__))
    opts = {"--base": "/mnt/project-files/hoofdpersonage/hoofdpersonage.glb",
            "--out": os.path.join(here, "output"), "--only": "", "--samples": "48",
            "--cast": "video1"}
    flags = set()
    i = 0
    while i < len(argv):
        if argv[i] in opts:
            opts[argv[i]] = argv[i + 1]
            i += 2
        else:
            flags.add(argv[i])
            i += 1
    out = opts["--out"]
    os.makedirs(os.path.join(out, "renders"), exist_ok=True)
    os.makedirs(os.path.join(out, "glb"), exist_ok=True)
    only = [k for k in opts["--only"].split(",") if k]

    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    bpy.ops.import_scene.gltf(filepath=opts["--base"])
    imported = [o for o in bpy.context.scene.objects]
    base_parts = {}
    for o in imported:
        if o.type == "MESH":
            base_parts[int(o.name.rsplit("_", 1)[1])] = o
    unlit_tpl = base_parts[38].data.materials[0]

    # hoofdpersonage als referentie in een eigen collectie
    cast_coll = bpy.data.collections.new("cast")
    sc.collection.children.link(cast_coll)
    hero = bpy.data.collections.new("hoofdpersonage")
    cast_coll.children.link(hero)
    for o in imported:
        for c in o.users_collection:
            c.objects.unlink(o)
        hero.objects.link(o)
    hero_root = next(o for o in imported if o.type == "EMPTY" and o.parent is None)
    hero_root.name = "hoofdpersonage"

    src = CAST_10X if opts["--cast"] == "10x" else CAST
    specs = [s for s in src if not only or s["key"] in only]
    built = []
    for spec in specs:
        coll, root, head_c, zmax = build_character(spec, base_parts, unlit_tpl, cast_coll)
        built.append((spec, coll, root, head_c, zmax))
        print("gebouwd:", spec["key"], "lengte %.2f m" % zmax)

    cam = setup_render(int(opts["--samples"]))
    blend = "cast_10x_faster.blend" if opts["--cast"] == "10x" else "cast_video1.blend"
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, blend))

    for spec, coll, root, head_c, zmax in built:
        set_visible(None, [coll.name])
        export_glb(coll, os.path.join(out, "glb", f"{spec['key']}.glb"))

    if "--no-render" in flags:
        return

    vl = bpy.context.view_layer
    lab_coll = bpy.data.collections.new("labels")
    sc.collection.children.link(lab_coll)

    # per figuur: drie kanten en close-up
    for n, (spec, coll, root, head_c, zmax) in enumerate(built, start=1):
        set_visible(None, [])
        tmp = []
        for k, rz in enumerate((0, math.radians(90), math.pi)):
            tmp.append(instance(coll, ((k - 1) * 1.15, 0, 0), rz, lab_coll))
        h = zmax
        aim(cam, (0, -max(4.6, 2.9 * h), h * 0.5 + 0.15), (0, 0, h * 0.5), lens=50)
        render(os.path.join(out, "renders", f"{n:02d}_{spec['key']}_drie_kanten.png"), 1800, 1100)
        for t in tmp:
            bpy.data.objects.remove(t)
        set_visible(None, [coll.name])
        hc = head_c
        aim(cam, (hc.x + 0.55, hc.y - 1.55, hc.z + 0.05), (hc.x, hc.y, hc.z - 0.08), lens=50)
        render(os.path.join(out, "renders", f"{n:02d}_{spec['key']}_close-up.png"), 1000, 1000)

    # overzicht: hele cast naast het hoofdpersonage
    set_visible(None, [])
    order = sorted(built, key=lambda b: -b[4])
    lineup = [("hoofdpersonage", hero, 1.77)] + [(b[0]["naam"], b[1], b[4]) for b in order]
    gap = 0.82
    x0 = -(len(lineup) - 1) * gap / 2
    for k, (name, coll, h) in enumerate(lineup):
        x = x0 + k * gap
        instance(coll, (x, 0, 0), 0.0, lab_coll)
        add_label(name.replace(" van de pestkop", "\nvan de pestkop"), (x, -0.45, 0.02),
                  size=0.075, coll=lab_coll)
    width = len(lineup) * gap
    aim(cam, (0, -width * 1.55, 1.4), (0, 0, 0.8), lens=50)
    render(os.path.join(out, "renders", "00_overzicht_cast.png"), 3200, 1100)


if __name__ == "__main__":
    main()
