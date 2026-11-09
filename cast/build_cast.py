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


def pants_stof(hexcol):
    """Blauwige broeken zijn spijkerstof, de rest katoen."""
    r, g, b = (int(hexcol.lstrip("#")[k:k + 2], 16) for k in (0, 2, 4))
    return "denim" if b > r + 25 and b > g and r < 140 else "katoen"


class Mats:
    """Materialen in dezelfde opbouw als het hoofdpersonage."""

    def __init__(self, unlit_template, prefix):
        self.tpl = unlit_template
        self.prefix = prefix
        self.cache = {}

    def pbr(self, hexcol, rough=0.9, metal=0.0, key=None, stof=None):
        key = key or ("pbr", hexcol, rough, metal, stof)
        if key in self.cache:
            return self.cache[key]
        tag = f"_{stof}" if stof else ""
        m = bpy.data.materials.new(f"{self.prefix}{tag}_{hexcol.lstrip('#')}")
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
    "hero": ("#4A2E1A", "#3A2313"),   # niet gebruikt: hoofdpersonage houdt zijn eigen ogen
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


# Video 3 "What IF There Were NO RULES?": het hoofdpersonage in vier versies, nieuwe
# figuren en grijzere ouders. Bouwen met --cast nr (bouwt ook de vaste CAST opnieuw,
# met de details van glans 2).
_HERO = dict(hoodie=True, eyes="hero", brows=dict(keep=True), skin="licht", mouth="smile",
             shirt=dict(color="#EB7A2B", sleeves="long", cuff="#F6F2E9", stof="fleece"),
             pants="#3B3F49", pants_stof="katoen", shoes="#F4F1E9")


def _hero(key, naam, **kw):
    d = dict(_HERO, key=key, naam=naam, rol="(hoofdpersonage)")
    d.update(kw)
    return d


def _variant(base_key, key, naam, **kw):
    d = dict(next(c for c in CAST if c["key"] == base_key))
    d.update(key=key, naam=naam)
    for k, v in kw.items():
        if isinstance(v, dict) and isinstance(d.get(k), dict):
            d[k] = dict(d[k], **v)
        else:
            d[k] = v
    return d


CAST_NR = [
    _hero("hoofdpersonage_kind", "Hoofdpersonage (kind)", body=dict()),
    _hero("hoofdpersonage_pyjama", "Hoofdpersonage in pyjamabroek", body=dict(),
          pants="#4F6FB8", pants_stof="pyjama", pant_stripes="#DCE6FA", shoes="#8C96A3",
          sole="#5C6470"),
    _hero("hoofdpersonage_tiener", "Hoofdpersonage (tiener, jaar 5)",
          body=dict(leg=1.12, torso=1.06, width=1.02, shoulders=1.07, arm=1.1, legt=1.06, head=0.94),
          pants="#34507A", pants_stof="denim"),
    _hero("hoofdpersonage_volwassen", "Hoofdpersonage (jongvolwassen, jaar 10)",
          body=dict(leg=1.2, torso=1.12, width=1.08, shoulders=1.16, arm=1.18, legt=1.12, head=0.9),
          shirt=dict(color="#EB7A2B", sleeves="long", sleeve_color="#22314F", cuff="#EB7A2B",
                     stof="fleece", sleeve_stof="wol"),
          blazer=dict(color="#22314F"), pants="#2E3440", shoes="#5A3B26",
          beard=dict(color="#6B4A33")),
    _variant("pestkop", "pestkop_volwassen", "Pestkop (volwassen, jaar 10)",
             body=dict(leg=1.14, torso=1.14, width=1.26, shoulders=1.2, arm=1.32, legt=1.16,
                       head=0.88, belly=0.15),
             mouth="smile", beard=dict(color="#2A1A10"),
             shirt=dict(color="#E8E4DA", sleeves="long", sleeve_color="#3B3B40", cuff="#3B3B40"),
             jacket=dict(color="#3B3B40", stof="wol")),
    dict(key="volgeling_a", naam="Volgeling 1 (muts)", rol="(geen tekst)",
         body=dict(leg=1.06, torso=1.0, width=0.88, shoulders=0.92, arm=0.95, head=0.95),
         skin="olijf", eyes="bruin", brows=dict(color="#2A1A10", angle=12, raise_=-0.004),
         mouth="smirk",
         shirt=dict(color="#7C8591", sleeves="long", stof="fleece"),
         pants="#34507A", shoes="#1F1F22",
         hair=dict(style="buzz", color="#2A1A10"), hat="beanie", beanie="#2E3440"),
    dict(key="volgeling_b", naam="Volgeling 2 (pet)", rol="(geen tekst)",
         body=dict(leg=1.02, torso=1.04, width=1.04, shoulders=1.06, arm=1.06, head=0.95),
         skin="donker", eyes="donker", brows=dict(color="#1A110C", angle=15, raise_=-0.004),
         mouth="flat",
         shirt=dict(color="#1F1F22", sleeves="long", sleeve_color="#3B4A2F", cuff="#2A3321"),
         jacket=dict(color="#3B4A2F", stof="nylon"),
         pants="#2E3440", shoes="#F2F2F2",
         hair=dict(style="buzz", color="#1A110C"), hat="cap",
         cap=dict(color="#C8283A", visor="#1F1F22")),
    dict(key="volgeling_c", naam="Volgeling 3 (groot)", rol="(geen tekst)",
         body=dict(leg=1.08, torso=1.1, width=1.22, shoulders=1.16, arm=1.24, legt=1.14,
                   head=0.92, belly=0.2),
         skin="licht", eyes="blauw", brows=dict(color="#A87B3A", scale=1.2, angle=10),
         mouth="flat",
         shirt=dict(color="#B3362C", sleeves="long", stof="fleece"),
         pants="#4B4F57", shoes="#1F1F22",
         hair=dict(style="short", color="#C9A25A")),
    dict(key="agent", naam="Agent", rol="AGENT",
         body=dict(leg=1.06, torso=1.08, width=1.12, shoulders=1.1, arm=1.12, belly=0.22, head=0.98),
         skin="midden", eyes="bruin", brows=dict(color="#2A1A10", scale=1.15),
         mouth="smile", mustache="#2A1A10",
         shirt=dict(color="#2B4170", sleeves="long", cuff="#22345E", stof="katoen"),
         pants="#1D2742", pants_stof="katoen", pant_stripes="#E2B84B", shoes="#141414",
         hair=dict(style="short", color="#2A1A10"), hat="peaked",
         peaked=dict(color="#1D2742", band="#E8E8E8"), badge=True, whistle=True,
         uniform=dict(pocket="#22345E", belt="#141414", metal="#C9CCD1", ribbons=False)),
    dict(key="kassiere", naam="Kassière", rol="CASHIER",
         body=dict(leg=1.0, torso=0.98, width=0.98, hips=1.06, shoulders=0.94, arm=0.9, head=0.97),
         skin="bruin", eyes="donker", brows=dict(color="#24160F", raise_=0.004),
         mouth="smile", lashes=True, earrings="#E2B84B",
         shirt=dict(color="#2F9C5A", sleeves="short"), chest_logo="#F6D04D", name_tag=True,
         pants="#2E3440", shoes="#1F1F22",
         hair=dict(style="ponytail", color="#24160F")),
    dict(key="buurman", naam="Buurman", rol="NEIGHBOR",
         body=dict(leg=0.98, torso=1.08, width=1.16, shoulders=1.06, arm=1.08, belly=0.42, head=1.0),
         skin="roze", eyes="blauw", brows=dict(color="#6B5A4A", scale=1.3, angle=14, raise_=-0.004),
         mouth="flat", mustache="#7A6A5A",
         glasses=dict(color="#2A2A2A", r=0.007),
         shirt=dict(color="#8A3B2E", sleeves="long", cuff="#6E2F25", stof="katoen"),
         vest=dict(color="#5B6B4A", stripes="#5B6B4A"),
         pants="#6B5A45", shoes="#3A2A1A",
         hair=dict(style="receding", color="#7A6A5A")),
    dict(key="ruilmarktverkoper", naam="Ruilmarktverkoper", rol="TRADER",
         body=dict(leg=0.96, torso=1.0, width=1.04, arm=1.0, head=1.0),
         skin="olijf", eyes="groen", brows=dict(color="#9A9A9A", scale=1.2),
         mouth="smile", beard=dict(color="#A8A39B"),
         shirt=dict(color="#4A6B8A", sleeves="long", cuff="#3C5A75", stof="katoen"),
         cardigan=dict(color="#7A5A3A", buttons="#2A1A10"),
         pants="#4B4F57", shoes="#3A2A1A",
         hair=dict(style="buzz", color="#A8A39B"), hat="beanie", beanie="#B0562E"),
    dict(key="strandwacht", naam="Strandwacht", rol="(fluit)",
         body=dict(leg=1.08, torso=1.06, width=1.06, shoulders=1.12, arm=1.1, head=0.97),
         skin="midden", eyes="bruin", brows=dict(color="#2A1A10"),
         mouth="smile",
         shirt=dict(color="#E5483E", sleeves="short"), chest_logo="#FFFFFF",
         shorts="#E5483E", shoes="#F6D04D", sole="#E9B93A",
         hair=dict(style="short", color="#2A1A10"), whistle=True,
         hat="cap", cap=dict(color="#FFFFFF", visor="#E5483E", logo="#E5483E")),
    dict(key="hondenbaas", naam="Man met het hondje", rol="(geen tekst)",
         body=dict(leg=1.0, torso=1.02, width=1.0, arm=0.98, head=1.0),
         skin="licht", eyes="grijs", brows=dict(color="#8E8E8E", scale=1.15),
         mouth="smile", mustache="#8E8E8E",
         shirt=dict(color="#E8E2D2", sleeves="long", sleeve_color="#5D7A5B", cuff="#4E6A4C"),
         cardigan=dict(color="#5D7A5B", buttons="#E8E2D2"),
         pants="#5A5E66", shoes="#5A3B26",
         hair=dict(style="bald_sides", color="#B5B5B5"), hat="flatcap"),
    dict(key="figurant_a", naam="Figurant: vrouw met horloge", rol="(geen tekst)",
         body=dict(leg=1.02, torso=0.98, width=0.94, hips=1.06, shoulders=0.92, arm=0.88, head=0.97),
         skin="midden", eyes="bruin", brows=dict(color="#2A1A10"),
         mouth="flat", lashes=True,
         shirt=dict(color="#F2C14E", sleeves="long", cuff="#E0AE3C"),
         pants="#3E5C8A", shoes="#C8283A", hair=dict(style="bob", color="#2A1A10")),
    dict(key="figurant_b", naam="Figurant: man in pak", rol="(geen tekst)",
         body=dict(leg=1.06, torso=1.04, width=1.04, shoulders=1.04, arm=1.04, head=0.98),
         skin="licht", eyes="blauw", brows=dict(color="#5B3A24"),
         mouth="flat",
         shirt=dict(color="#F2F4F8", sleeves="long", sleeve_color="#5F6670", cuff="#5F6670"),
         blazer=dict(color="#5F6670"), tie="#2D6CDF",
         pants="#5F6670", pants_stof="wol", shoes="#1A1A1A",
         hair=dict(style="short", color="#5B3A24")),
    dict(key="figurant_c", naam="Figurant: sportieve vrouw", rol="(geen tekst)",
         body=dict(leg=1.04, torso=0.96, width=0.9, hips=1.04, shoulders=0.92, arm=0.88, head=0.96),
         skin="licht", eyes="groen", brows=dict(color="#C9772E"),
         mouth="smile", lashes=True, freckles=True,
         shirt=dict(color="#E86FA0", sleeves="short", stof="nylon"),
         pants="#2E3440", pants_stof="nylon", shoes="#FFFFFF",
         hair=dict(style="ponytail", color="#C9772E")),
    dict(key="figurant_d", naam="Figurant: tiener met krullen", rol="(geen tekst)",
         body=dict(leg=0.98, torso=0.94, width=0.9, arm=0.9, head=0.96),
         skin="donker", eyes="donker", brows=dict(color="#1E1410"),
         mouth="grin",
         shirt=dict(color="#7A5BC9", sleeves="long", stof="fleece"),
         pants="#3B3F49", shoes="#F6D04D",
         hair=dict(style="curly", color="#1E1410")),
    dict(key="figurant_e", naam="Figurant: strandganger", rol="(geen tekst)",
         body=dict(leg=1.0, torso=1.04, width=1.08, arm=1.02, belly=0.3, head=1.0),
         skin="roze", eyes="blauw", brows=dict(color="#C9A25A"),
         mouth="grin",
         shirt=dict(color="#2D9CDB", sleeves="short", dots=("#FFFFFF", "#F6D04D")),
         shorts="#F2B33D", shoes="#2D6CDF",
         hair=dict(style="short", color="#C9A25A")),
    dict(key="figurant_f", naam="Figurant: vrouw met tas", rol="(geen tekst)",
         body=dict(leg=0.96, torso=1.0, width=1.04, hips=1.1, shoulders=0.96, arm=0.92,
                   belly=0.2, head=0.98),
         skin="olijf", eyes="bruin", brows=dict(color="#3B2416"),
         mouth="smile", lashes=True, earrings="#E2B84B",
         shirt=dict(color="#F4E9F2", sleeves="long", cuff="#2F9C95"),
         cardigan=dict(color="#2F9C95", buttons="#F4E9F2"),
         skirt=dict(color="#3B4A6B", bottom=0.2), legs="#E8C3A5", shoes="#5B3A4E",
         hair=dict(style="curly_bun", color="#3B2416")),
    dict(key="kind_a", naam="Kind op het klimrek", rol="(geen tekst)",
         body=dict(leg=0.54, torso=0.58, width=0.84, arm=0.78, legt=0.8, head=0.88),
         skin="bruin", eyes="donker", brows=dict(color="#1E1410", raise_=0.006),
         mouth="grin", shirt=dict(color="#F6D04D", sleeves="short"),
         shorts="#2D6CDF", shoes="#E5483E", hair=dict(style="curly", color="#1E1410")),
    dict(key="kind_b", naam="Kind met staartjes", rol="(geen tekst)",
         body=dict(leg=0.5, torso=0.55, width=0.8, arm=0.75, legt=0.76, head=0.87),
         skin="licht", eyes="blauw", brows=dict(color="#C9A25A", raise_=0.008),
         mouth="smile", lashes=True, blush="#F08A8A",
         shirt=dict(color="#5DB045", sleeves="short"),
         skirt=dict(color="#2F9C95", bottom=0.36, flare=1.3), legs="SKIN", shoes="#F59AC2",
         hair=dict(style="pigtails", color="#C9A25A", ribbon="#E5483E")),
    _variant("broertje", "broertje_tiener", "Broertje (tiener, jaar 10)",
             body=dict(leg=0.98, torso=0.94, width=0.94, arm=0.95, legt=0.96, head=0.95),
             shirt=dict(color="#2D6CDF", sleeves="long", stof="fleece", stripes=None),
             shorts=None, pants="#34507A"),
    _variant("mama", "mama_grijs", "Mama (grijze plukken, jaar 5)",
             hair=dict(color="#A2907E")),
    _variant("papa", "papa_grijs", "Papa (grijzer, jaar 5)",
             hair=dict(color="#8F857B"), beard=dict(color="#8F857B")),
]


# Video 4 "What IF You Could Never Die?": het hoofdpersonage per tijdperk (hij blijft 14),
# leeftijdsvarianten van de vaste cast en nieuwe figuren. Bouwen met --cast nd; dat bouwt ook
# de vaste cast opnieuw (met de wetenschapper als man) plus de vuilnisman en de agent.
def _nr(key):
    return dict(next(c for c in CAST_NR if c["key"] == key))


def _10x(key):
    return dict(next(c for c in CAST_10X if c["key"] == key))


_FUT_A = "#5CF2FF"   # cyaan
_FUT_B = "#FF5CD6"   # magenta
_FUT_C = "#B6FF5C"   # limoen
CAST_ND = [
    # --- hoofdpersonage, altijd 14 ---
    _hero("hoofdpersonage_kind", "Hoofdpersonage 2026 (hoodie)", body=dict()),
    _hero("hoofdpersonage_pak", "Hoofdpersonage 2051 (te groot zwart pak)", body=dict(), hoodie=False,
          shirt=dict(color="#F4F4F4", sleeves="long", sleeve_color="#1F2128", cuff="#1F2128", stof="katoen",
                     sleeve_stof="wol"),
          blazer=dict(color="#1F2128"), tie="#1F2128", sleeve_over=True,
          pants="#1F2128", pants_stof="wol", shoes="#141414"),
    _hero("hoofdpersonage_2200", "Hoofdpersonage 2200 (toekomstjas)", body=dict(),
          jacket=dict(color="#E9EEF2", stof="nylon"), glow=dict(color=_FUT_A, rings=(0.68,), angle=24),
          pants="#3B3F49", shoes="#E9EEF2", sole="#5CC9D6"),
    _hero("hoofdpersonage_ijs", "Hoofdpersonage 50.000 (winterjas, sjaal, wanten)", body=dict(),
          jacket=dict(color="#6B4E36", stof="wol"), scarf=dict(color="#B3362C", stripes="#E8DCC8"),
          mittens="#B3362C", hat="beanie", beanie="#B3362C", pants="#4B4F57", shoes="#3A2A1A"),
    _hero("hoofdpersonage_zwerver", "Hoofdpersonage 1 miljoen jaar (versleten)", body=dict(),
          shirt=dict(color="#B8612E", sleeves="long", cuff="#D9C9B0", stof="fleece"),
          rafels=dict(stains=5, patches=2), pants="#4A4D55", shoes="#9A938A"),
    _hero("hoofdpersonage_rafels", "Hoofdpersonage 1 miljard jaar (rafels)", body=dict(),
          shirt=dict(color="#8A4A2A", sleeves="long", cuff="#9A8A70", stof="fleece"),
          rafels=dict(stains=9, patches=3, patch="#5A4A3A"), pants=None, shorts="#4A4740", shoes="#7A7268"),
    # --- gezin ---
    _variant("mama", "mama_oud", "Mama (grijs, 2051)", hair=dict(color="#C9C4BE"), wrinkles=True,
             glasses=dict(color="#7A4E8A", r=0.006), cardigan=dict(color="#2F9C95", buttons="#F2EEE8"),
             shirt=dict(color="#F2EEE8", sleeves="long", cuff="#2F9C95")),
    _variant("papa", "papa_oud", "Papa (grijs, 2051)", hair=dict(style="receding", color="#D2CEC8"),
             beard=dict(color="#D2CEC8"), wrinkles=True, glasses=dict(color="#2A2A2A", r=0.007),
             body=dict(belly=0.45), shirt=dict(color="#2C8FC9", sleeves="long", cuff="#246F9C", dots=None),
             blazer=dict(color="#5A5F6B"), pants="#5A5F6B"),
    dict(key="broertje_oud", naam="Broertje (bijna 70, 2086)", rol="BROTHER",
         body=dict(leg=1.0, torso=1.02, width=1.06, shoulders=1.0, arm=1.02, belly=0.28, head=0.98),
         skin="licht", eyes="blauw", brows=dict(color="#E6E3E0", scale=1.3, angle=6), mouth="smile",
         freckles=True, wrinkles=True, glasses=dict(color="#5A3B26", r=0.006),
         shirt=dict(color="#DCE6F0", sleeves="long", sleeve_color="#3E4A5E", cuff="#34405A", sleeve_stof="wol"),
         jacket=dict(color="#3E4A5E", stof="wol"), scarf=dict(color="#E5483E", stripes="#F2F2F2"),
         pants="#5D5850", pants_stof="wol", shoes="#3A2A1A",
         hair=dict(style="receding", color="#E6E3E0"), beard=dict(color="#E6E3E0"), prop="cane"),
    # --- beste vriend ---
    dict(key="beste_vriend_20", naam="Beste vriend (20, 2032)", rol="FRIEND",
         body=dict(leg=1.14, torso=1.06, width=0.98, shoulders=1.07, arm=0.96, legt=1.04, head=0.93),
         skin="donker", eyes="donker", brows=dict(color="#1E1410", raise_=0.004), mouth="grin",
         goatee="#1E1410",
         shirt=dict(color="#6CBF4B", sleeves="long", sleeve_color="#3E5F8A", cuff="#34507A", sleeve_stof="denim"),
         jacket=dict(color="#3E5F8A", stof="denim"),
         pants="#2E3440", shoes="#E9483B", hair=dict(style="curly", color="#1E1410"), prop="keys"),
    dict(key="beste_vriend_40", naam="Beste vriend (bijna 40, bruidegom 2051)", rol="FRIEND",
         body=dict(leg=1.14, torso=1.08, width=1.04, shoulders=1.07, arm=0.98, legt=1.04, belly=0.14, head=0.92),
         skin="donker", eyes="donker", brows=dict(color="#2A2420", raise_=0.004), mouth="grin",
         goatee="#5A544E", wrinkles=True,
         shirt=dict(color="#FAFAFA", sleeves="long", sleeve_color="#2A2F3A", cuff="#2A2F3A", sleeve_stof="wol"),
         blazer=dict(color="#2A2F3A"), tie="#C8A13A", flower="#FFFFFF",
         pants="#2A2F3A", pants_stof="wol", shoes="#141414", hair=dict(style="curly", color="#46413D")),
    # --- pestkop ---
    dict(key="pestkop_agent", naam="Pestkop als agent (50+, 2066)", rol="BULLY",
         body=dict(leg=1.06, torso=1.12, width=1.28, shoulders=1.16, hips=1.0, arm=1.28, legt=1.15, head=0.92,
                   belly=0.42),
         skin="midden", eyes="bruin", brows=dict(color="#4A3A30", scale=1.25, angle=8), mouth="flat",
         mustache="#5A4A40", wrinkles=True,
         shirt=dict(color="#2B4170", sleeves="long", cuff="#22345E", stof="katoen"),
         pants="#1D2742", pants_stof="katoen", pant_stripes="#E2B84B", shoes="#141414",
         hair=dict(style="buzz", color="#6A5E56"), hat="peaked", peaked=dict(color="#1D2742", band="#E8E8E8"),
         badge=True, uniform=dict(pocket="#22345E", belt="#141414", metal="#C9CCD1", ribbons=False)),
    dict(key="pestkop_oud", naam="Pestkop (98, rolstoel, 2110)", rol="BULLY",
         body=dict(leg=0.98, torso=1.0, width=1.06, shoulders=1.0, hips=0.98, arm=1.1, legt=1.0, head=0.9),
         skin="midden", eyes="bruin", brows=dict(color="#EDEDED", scale=1.4, angle=-4), mouth="smile",
         wrinkles=True, glasses=dict(color="#C9CCD1", r=0.006, round_=True),
         shirt=dict(color="#E8E4DA", sleeves="long", sleeve_color="#6E6B5A", cuff="#5E5B4A"),
         cardigan=dict(color="#6E6B5A", buttons="#3A2A1A"),
         pants="#5A5E66", shoes="#3A2A1A", hair=dict(style="bald_sides", color="#F2F2F2")),
    dict(key="verpleger", naam="Verpleger (2110)", rol="(geen tekst)",
         body=dict(leg=1.04, torso=1.02, width=1.0, arm=1.0, head=0.98),
         skin="olijf", eyes="bruin", brows=dict(color="#2A1A10"), mouth="smile",
         shirt=dict(color="#4FB3A9", sleeves="short", stof="katoen"), name_tag=True,
         pants="#4FB3A9", pants_stof="katoen", shoes="#F2F2F2", hair=dict(style="short", color="#2A1A10")),
    # --- wetenschapper (man, zoals in video 3) ---
    dict(key="wetenschapper", naam="Wetenschapper (man)", rol="SCIENTIST",
         body=dict(leg=1.02, torso=1.02, width=1.0, shoulders=1.0, arm=0.96, head=0.98),
         skin="olijf", eyes="donker", brows=dict(color="#1E1612", scale=1.1), mouth="smile",
         glasses=dict(color="#1A1A1A", r=0.008),
         shirt=dict(color="#A9C7E8", sleeves="long", sleeve_color="#FAFAFA", cuff="#E8E8E8"), tie="#2D6CDF",
         labcoat=True, pants="#2F3542", shoes="#2F3542",
         hair=dict(style="short", color="#2A211C"), beard=dict(color="#2A211C"), prop="clipboard"),
    # --- 2032-2066 ---
    dict(key="portier", naam="Portier van de club", rol="BOUNCER",
         body=dict(leg=1.08, torso=1.12, width=1.32, shoulders=1.24, hips=1.0, arm=1.34, legt=1.18, head=0.9),
         skin="bruin", eyes="donker", brows=dict(color="#1A110C", scale=1.2, angle=12, raise_=-0.004),
         mouth="flat", earpiece=True,
         shirt=dict(color="#1A1A1E", sleeves="short"), chest_logo="#E8E8E8",
         pants="#1A1A1E", shoes="#141414", hair=dict(style="buzz", color="#1A110C")),
    dict(key="tante", naam="Oude tante (bruiloft)", rol="AUNT",
         body=dict(leg=0.9, torso=0.95, width=1.06, hips=1.1, shoulders=0.95, arm=0.92, belly=0.25, head=0.97),
         skin="roze", eyes="blauw", brows=dict(color="#BDBDBD", angle=-10, raise_=0.006), mouth="grin",
         lashes=True, blush="#F08A8A", wrinkles=True, pearls=True,
         glasses=dict(color="#C8283A", r=0.006),
         shirt=dict(color="#9B59B6", sleeves="long", cuff="#8A4AA5", dots=("#F59AC2", "#FFFFFF")),
         skirt=dict(color="#9B59B6", bottom=0.16), legs="#E8C3A5", shoes="#5B3A4E",
         hair=dict(style="curly_bun", color="#D6D2CE"), hat="flowerhat", flowerhat=dict(color="#B58FC9")),
    dict(key="brandweerman", naam="Brandweerman", rol="FIREFIGHTER",
         body=dict(leg=1.06, torso=1.1, width=1.18, shoulders=1.14, arm=1.16, belly=0.15, head=0.97),
         skin="licht", eyes="blauw", brows=dict(color="#8A5530", scale=1.2), mouth="flat", mustache="#8A5530",
         shirt=dict(color="#C9A24A", sleeves="long", cuff="#2A2A2A", stof="nylon"),
         vest=dict(color="#C9A24A", stripes="#E8F05A"),
         pants="#C9A24A", pants_stof="nylon", pant_stripes="#E8F05A", shoes="#1A1A1A",
         hair=dict(style="short", color="#8A5530"), hat="fire"),
    dict(key="meisje_brand", naam="Meisje uit de brand (6)", rol="(geen tekst)",
         body=dict(leg=0.5, torso=0.55, width=0.8, arm=0.75, legt=0.76, head=0.87),
         skin="bruin", eyes="donker", brows=dict(color="#1E1410", raise_=0.008), mouth="small",
         lashes=True, blush="#E07A6A",
         shirt=dict(color="#F59AC2", sleeves="long", cuff="#FFFFFF", stof="pyjama", dots=("#FFFFFF", "#FFE14D")),
         pants="#F59AC2", pants_stof="pyjama", shoes="#FFFFFF",
         hair=dict(style="pigtails", color="#1E1410", ribbon="#FFE14D")),
    dict(key="moeder_meisje", naam="Moeder van het meisje", rol="MOTHER",
         body=dict(leg=1.0, torso=0.98, width=0.96, hips=1.06, shoulders=0.92, arm=0.88, head=0.97),
         skin="bruin", eyes="donker", brows=dict(color="#1E1410", raise_=0.004), mouth="smile", lashes=True,
         shirt=dict(color="#F2EEE8", sleeves="long", cuff="#C97A4A"), cardigan=dict(color="#C97A4A", buttons="#F2EEE8"),
         pants="#5A6E8A", pants_stof="pyjama", shoes="#9A7A6A", hair=dict(style="ponytail", color="#1E1410")),
    # --- 2200: EVERGREEN ---
    dict(key="directeur", naam="EVERGREEN-directeur (wit pak)", rol="DIRECTOR",
         body=dict(leg=1.08, torso=1.04, width=1.0, shoulders=1.04, arm=1.0, head=0.96),
         skin="licht", eyes="grijs", brows=dict(color="#BFC4C9", angle=6), mouth="smirk",
         shirt=dict(color="#F7F7F7", sleeves="long", sleeve_color="#F2F2F2", cuff="#E2E2E2", sleeve_stof="wol"),
         blazer=dict(color="#F2F2F2"), tie="#1FA37A", chest_logo="#1FA37A",
         pants="#F2F2F2", pants_stof="wol", shoes="#E8E8E8", sole="#B0B0B0",
         hair=dict(style="short", color="#2A211C")),
    dict(key="bewaker_a", naam="EVERGREEN-bewaker 1", rol="(geen tekst)",
         body=dict(leg=1.1, torso=1.1, width=1.18, shoulders=1.18, arm=1.18, legt=1.12, head=0.94),
         skin="midden", eyes="bruin", brows=dict(color="#2A1A10", angle=14, raise_=-0.004), mouth="flat",
         shirt=dict(color="#E6EAEE", sleeves="long", cuff="#9AA3AD", stof="nylon"),
         vest=dict(color="#B8C0C8", stripes="#1FA37A"), glow=dict(color=_FUT_C, rings=(0.68,), stripe=False),
         pants="#3A3F47", pants_stof="nylon", shoes="#1A1A1E", hat="guard", helmet="#EEF1F4"),
    dict(key="bewaker_b", naam="EVERGREEN-bewaker 2", rol="(geen tekst)",
         body=dict(leg=1.08, torso=1.12, width=1.24, shoulders=1.2, arm=1.2, legt=1.12, head=0.94, belly=0.12),
         skin="licht", eyes="blauw", brows=dict(color="#7A5236", angle=14, raise_=-0.004), mouth="flat",
         shirt=dict(color="#E6EAEE", sleeves="long", cuff="#9AA3AD", stof="nylon"),
         vest=dict(color="#B8C0C8", stripes="#1FA37A"), glow=dict(color=_FUT_C, rings=(0.68,), stripe=False),
         pants="#3A3F47", pants_stof="nylon", shoes="#1A1A1E", hat="guard", helmet="#EEF1F4"),
    dict(key="mens_2200_a", naam="Voorbijganger 2200 (vrouw)", rol="(geen tekst)",
         body=dict(leg=1.06, torso=0.98, width=0.92, hips=1.04, shoulders=0.92, arm=0.88, head=0.96),
         skin="olijf", eyes="groen", brows=dict(color="#3B2416"), mouth="flat", lashes=True,
         shirt=dict(color="#2A2F3A", sleeves="long", cuff="#2A2F3A", stof="nylon"),
         glow=dict(color=_FUT_A, rings=(0.9,), angle=-20), prop="holo",
         pants="#E9EEF2", pants_stof="nylon", shoes="#2A2F3A", hair=dict(style="bob", color="#E9EEF2")),
    dict(key="mens_2200_b", naam="Voorbijganger 2200 (man)", rol="(geen tekst)",
         body=dict(leg=1.08, torso=1.04, width=1.02, shoulders=1.04, arm=1.0, head=0.96),
         skin="bruin", eyes="donker", brows=dict(color="#1E1410"), mouth="flat",
         shirt=dict(color="#E9EEF2", sleeves="long", sleeve_color="#3B3F49", cuff="#3B3F49", stof="nylon"),
         jacket=dict(color="#3B3F49", stof="nylon"), glow=dict(color=_FUT_B, rings=(0.68,), angle=30),
         prop="holo", pants="#3B3F49", pants_stof="nylon", shoes="#E9EEF2", hair=dict(style="buzz", color="#1E1410")),
    # --- 3026 en later: toekomstmensen ---
    dict(key="toekomst_a", naam="Graver 3026 (lichtgevende overall)", rol="(geen tekst)",
         body=dict(leg=1.12, torso=1.0, width=0.94, shoulders=0.98, arm=0.96, head=0.92),
         skin="bruin", eyes="groen", brows=dict(color="#E9EEF2"), mouth="flat",
         shirt=dict(color="#3A2A5A", sleeves="long", cuff="#3A2A5A", stof="nylon"),
         glow=dict(color=_FUT_B, rings=(0.66, 0.9, 1.12), angle=0),
         pants="#3A2A5A", pants_stof="nylon", shoes="#E9EEF2", hair=dict(style="buzz", color="#E9EEF2")),
    dict(key="toekomst_b", naam="Graver 3026 (vrouw)", rol="(geen tekst)",
         body=dict(leg=1.12, torso=0.98, width=0.9, hips=1.02, shoulders=0.92, arm=0.9, head=0.92),
         skin="licht", eyes="blauw", brows=dict(color="#5CB8FF"), mouth="flat", lashes=True,
         shirt=dict(color="#F2F5F8", sleeves="long", cuff="#5CB8FF", stof="nylon"),
         glow=dict(color=_FUT_A, rings=(0.7, 1.0), angle=-24),
         pants="#5A6B7A", pants_stof="nylon", shoes="#5CB8FF", hair=dict(style="ponytail", color="#5CB8FF")),
    dict(key="kind_holo", naam="Kind met hologramtelefoon (3026)", rol="KID",
         body=dict(leg=0.6, torso=0.62, width=0.84, arm=0.8, legt=0.82, head=0.9),
         skin="olijf", eyes="bruin", brows=dict(color="#2A1A10", raise_=0.008), mouth="grin", freckles=True,
         shirt=dict(color="#F6D04D", sleeves="long", cuff="#3A2A5A", stof="nylon"),
         glow=dict(color=_FUT_A, rings=(0.7, 1.0), angle=20), prop="holo",
         pants="#3A2A5A", pants_stof="nylon", shoes="#F6D04D", hair=dict(style="spiky", color="#2A1A10")),
    dict(key="museumkind_a", naam="Museumkind 1 (jaar 10.000)", rol="(geen tekst)",
         body=dict(leg=0.56, torso=0.6, width=0.82, arm=0.78, legt=0.8, head=0.9),
         skin="midden", eyes="groen", brows=dict(color="#E9EEF2", raise_=0.008), mouth="grin",
         shirt=dict(color="#FFFFFF", sleeves="long", cuff="#FF5CD6", stof="nylon"),
         glow=dict(color=_FUT_B, rings=(0.7,), angle=0), pants="#FFFFFF", pants_stof="nylon", shoes="#FF5CD6",
         hair=dict(style="buzz", color="#FF5CD6")),
    dict(key="museumkind_b", naam="Museumkind 2 (jaar 10.000)", rol="(geen tekst)",
         body=dict(leg=0.52, torso=0.56, width=0.8, arm=0.75, legt=0.76, head=0.88),
         skin="licht", eyes="blauw", brows=dict(color="#5CF2FF", raise_=0.008), mouth="small", lashes=True,
         shirt=dict(color="#2A2F3A", sleeves="long", cuff="#5CF2FF", stof="nylon"),
         glow=dict(color=_FUT_A, rings=(0.68, 0.95), angle=-20),
         skirt=dict(color="#2A2F3A", bottom=0.36, flare=1.2), legs="#5CF2FF", shoes="#2A2F3A",
         hair=dict(style="pigtails", color="#5CF2FF", ribbon="#FFFFFF")),
    dict(key="museumkind_c", naam="Museumkind 3 (jaar 10.000)", rol="(geen tekst)",
         body=dict(leg=0.58, torso=0.6, width=0.9, arm=0.8, legt=0.82, head=0.9, belly=0.12),
         skin="donker", eyes="donker", brows=dict(color="#B6FF5C", raise_=0.006), mouth="grin",
         shirt=dict(color="#B6FF5C", sleeves="long", cuff="#2A2F3A", stof="nylon"),
         glow=dict(color=_FUT_C, rings=(0.72,), angle=24), pants="#2A2F3A", pants_stof="nylon", shoes="#B6FF5C",
         hair=dict(style="curly", color="#1E1410")),
    dict(key="toekomstvrouw", naam="Lange toekomstvrouw (1 miljoen jaar)", rol="FUTURE HUMAN",
         body=dict(leg=1.4, torso=1.18, width=0.82, hips=0.96, shoulders=0.9, arm=1.2, legt=0.92, head=0.84),
         skin="olijf", eyes="grijs", brows=dict(color="#E8E4DA", raise_=0.004), mouth="flat", lashes=True,
         shirt=dict(color="#F2EEE6", sleeves="long", cuff="#D4AF37", stof="nylon"),
         glow=dict(color="#FFD27A", rings=(0.7, 1.12), angle=0, stripe=False),
         skirt=dict(color="#F2EEE6", bottom=0.05, flare=0.8, stof="nylon"), legs="#E8E4DA", shoes="#D4AF37",
         hair=dict(style="bob", color="#E8E4DA"), earrings="#D4AF37"),
]

# Wie er in --cast nd zit: vaste cast (wetenschapper als man), vuilnisman, agent en CAST_ND
def _cast_nd():
    base = [c for c in CAST if c["key"] not in ("wetenschapper", "officier", "gymleraar", "zusje_pestkop")]
    return base + [_10x("vuilnisman"), _nr("agent")] + CAST_ND


# Video 5 "What IF You Could See How Many Days Everyone Has Left?": varianten van de vaste cast
# (opa aan het meer, gezin in rouwkleding) en de nieuwe bijfiguren. Bouwen met --cast dl.
_BLACK = dict(shirt=dict(color="#F4F4F4", sleeves="long", sleeve_color="#1F2128", cuff="#1F2128",
                         stof="katoen", sleeve_stof="wol"),
              blazer=dict(color="#1F2128"), pants="#1F2128", pants_stof="wol", shoes="#141414")


def _nd(key):
    return dict(next(c for c in CAST_ND if c["key"] == key))


CAST_DL = [
    # --- hoofdpersonage (14) ---
    _hero("hoofdpersonage_kind", "Hoofdpersonage (hoodie)", body=dict()),
    _hero("hoofdpersonage_rugzak", "Hoofdpersonage met rugzak (school)", body=dict(), backpack="#2D6CDF"),
    _hero("hoofdpersonage_ziekenhuis", "Hoofdpersonage in ziekenhuishemd (dag 14)", body=dict(), hoodie=False,
          shirt=dict(color="#BFD8E8", sleeves="short", stof="katoen", dots=("#8FB4CF", "#FFFFFF")),
          pants="#BFD8E8", pants_stof="pyjama", shoes="#E8E8E8", sole="#B8B8B8"),
    dict(_nd("hoofdpersonage_pak"), key="hoofdpersonage_pak", naam="Hoofdpersonage in zwart pak (begrafenis)"),
    _hero("hoofdpersonage_pleister", "Hoofdpersonage met pleister (dag 41)", body=dict(), plaster=True,
          backpack="#2D6CDF"),
    # --- opa: meer, thuis, jong (foto) ---
    _variant("opa", "opa_vissen", "Opa aan het meer (vissershoed, bodywarmer)", hat="bucket",
             bucket=dict(color="#7C8A5A", band="#5A4A32"), prop=None, tie=None, cardigan=None,
             shirt=dict(color="#C9D9E6", sleeves="long", cuff="#B3C4D2", stof="katoen"),
             vest=dict(color="#4F6B4A", stripes="#4F6B4A"), pants="#6B5E4A", pants_stof="katoen"),
    _variant("opa", "opa_thuis", "Opa thuis (vest, geen pet)", hat=None, prop=None),
    dict(key="opa_jong", naam="Opa als jongen van 14 (zwart-witfoto 1964)", rol="(foto)",
         body=dict(), skin="roze", eyes="grijs", brows=dict(color="#6A4A30", scale=1.2), mouth="grin",
         freckles=True,
         shirt=dict(color="#E8E2D2", sleeves="short", stof="katoen"), suspenders="#5A4A3A",
         shorts="#5D5850", shoes="#3A2A1A", hair=dict(style="short", color="#6A4A30"), hat="flatcap"),
    dict(key="oma_jong", naam="Oma als meisje op de fiets (foto 1966)", rol="(foto)",
         body=dict(leg=0.86, torso=0.88, width=0.88, hips=1.02, shoulders=0.88, arm=0.86, head=0.95),
         skin="roze", eyes="blauw", brows=dict(color="#8A5A30", raise_=0.006), mouth="grin", lashes=True,
         freckles=True, blush="#F08A8A",
         shirt=dict(color="#F2E6D6", sleeves="short", dots=("#C8283A", "#FFFFFF")),
         skirt=dict(color="#C8283A", bottom=0.3), legs="#F1BC9F", shoes="#3A2A1A",
         hair=dict(style="pigtails", color="#8A5A30", ribbon="#FFFFFF")),
    # --- gezin in rouwkleding (begrafenis, dag 40) ---
    _variant("mama", "mama_zwart", "Mama (zwart, begrafenis)", shirt=dict(color="#1F2128", sleeves="long",
             cuff="#1F2128", stof="wol"), pants="#1F2128", shoes="#141414", earrings="#C9CCD1"),
    _variant("papa", "papa_zwart", "Papa (zwart pak, begrafenis)", **_BLACK, tie="#1F2128"),
    _variant("oma", "oma_zwart", "Oma (zwart, begrafenis)", shirt=dict(color="#2A2A30", sleeves="long",
             cuff="#2A2A30", stof="wol"), cardigan=dict(color="#1F2128", buttons="#C9CCD1"),
             skirt=dict(color="#1F2128", bottom=0.12)),
    _variant("broertje", "broertje_zwart", "Broertje (zwart, begrafenis)",
             shirt=dict(color="#F4F4F4", sleeves="long", sleeve_color="#1F2128", cuff="#1F2128"),
             blazer=dict(color="#1F2128"), shorts=None, pants="#1F2128", shoes="#141414"),
    # --- vaste cast ---
    _variant("beste_vriend", "beste_vriend_koptelefoon", "Beste vriend met koptelefoon",
             headphones=dict(color="#E5483E", cup="#1A1A1A"), backpack="#F6D04D", prop="phone"),
    dict(_nd("wetenschapper"), key="dokter", naam="Dokter (wetenschapper, man) met stethoscoop", rol="DOCTOR",
         prop=None, stethoscope=True),
    _variant("gymleraar", "wiskundeleraar", "Wiskundeleraar (gymleraar in overhemd)", whistle=False,
             shirt=dict(color="#E8EEF6", sleeves="long", cuff="#D0D8E4", stof="katoen"), tie="#7B2D26",
             pants="#4B4F57", pant_stripes=None, shoes="#3A2A1A", glasses=dict(color="#2A2A2A", r=0.007)),
    # --- nieuwe bijfiguren ---
    dict(key="directeur_school", naam="Schooldirecteur (vrouw)", rol="PRINCIPAL",
         body=dict(leg=1.0, torso=1.0, width=0.98, hips=1.08, shoulders=0.94, arm=0.9, belly=0.12, head=0.97),
         skin="midden", eyes="bruin", brows=dict(color="#2A1A10", angle=8), mouth="flat", lashes=True,
         glasses=dict(color="#8A2A3A", r=0.007), earrings="#E2B84B",
         shirt=dict(color="#F2EEE8", sleeves="long", cuff="#7A3B5A"), cardigan=dict(color="#7A3B5A", buttons="#E2B84B"),
         skirt=dict(color="#3B3F49", bottom=0.18), legs="#C98E62", shoes="#2A2A2A",
         hair=dict(style="curly_bun", color="#2A1A10")),
    dict(key="man_pak", naam="Man in pak met koffie (dag 5)", rol="MAN",
         body=dict(leg=1.08, torso=1.04, width=1.04, shoulders=1.06, arm=1.04, head=0.97),
         skin="bruin", eyes="donker", brows=dict(color="#1E1410"), mouth="flat",
         shirt=dict(color="#F2F4F8", sleeves="long", sleeve_color="#2F3A55", cuff="#2F3A55", sleeve_stof="wol"),
         blazer=dict(color="#2F3A55"), tie="#C8A13A", pants="#2F3A55", pants_stof="wol", shoes="#1A1A1A",
         hair=dict(style="buzz", color="#1E1410"), prop="coffee"),
    dict(key="moeder_kinderwagen", naam="Moeder met kinderwagen (dag 6)", rol="(geen tekst)",
         body=dict(leg=1.02, torso=0.98, width=0.94, hips=1.06, shoulders=0.92, arm=0.88, head=0.97),
         skin="licht", eyes="blauw", brows=dict(color="#C9A25A"), mouth="smile", lashes=True,
         shirt=dict(color="#F4F4F4", sleeves="long", sleeve_color="#E86FA0", cuff="#E86FA0"),
         jacket=dict(color="#E86FA0", stof="nylon"), pants="#3E5C8A", shoes="#F2EEE8",
         hair=dict(style="ponytail", color="#E0C27A")),
    dict(key="baby", naam="Baby in de kinderwagen", rol="(geen tekst)",
         body=dict(leg=0.34, torso=0.42, width=0.86, arm=0.62, legt=0.82, head=0.78, belly=0.2),
         skin="roze", eyes="blauw", brows=dict(color="#E0C27A", raise_=0.01), mouth="small", blush="#F08A8A",
         shirt=dict(color="#F6E7A8", sleeves="long", cuff="#F6E7A8", stof="pyjama"),
         pants="#F6E7A8", pants_stof="pyjama", shoes="#F6E7A8", hat="beanie", beanie="#9BD3E8"),
    dict(key="jongen_zwembad", naam="Jongen bij het zwembad (dag 6)", rol="(geen tekst)",
         body=dict(leg=0.86, torso=0.86, width=0.9, arm=0.86, head=0.94),
         skin="olijf", eyes="bruin", brows=dict(color="#2A1A10", raise_=0.006), mouth="grin",
         shirt=dict(color="#4FC3E8", sleeves="short", stof="nylon"), shorts="#F2B33D", shoes="#2D6CDF",
         hair=dict(style="spiky", color="#2A1A10")),
    dict(key="oude_man_winkel", naam="Oude man in de supermarkt (dag 7)", rol="(geen tekst)",
         body=dict(leg=0.94, torso=0.98, width=1.0, arm=0.96, belly=0.18, head=0.98),
         skin="licht", eyes="grijs", brows=dict(color="#F2F2F2", scale=1.4), mouth="smile", wrinkles=True,
         mustache="#F2F2F2", glasses=dict(color="#C9CCD1", r=0.006, round_=True),
         shirt=dict(color="#C9B89A", sleeves="long", cuff="#B0A080"), cardigan=dict(color="#8A5A3A", buttons="#E8E2D2"),
         pants="#5A5E66", shoes="#3A2A1A", hair=dict(style="bald_sides", color="#F2F2F2"), hat="flatcap"),
    dict(key="concierge", naam="Conciërge met bezem", rol="(geen tekst)",
         body=dict(leg=1.0, torso=1.04, width=1.1, arm=1.04, belly=0.3, head=1.0),
         skin="bruin", eyes="donker", brows=dict(color="#C9C9C9"), mouth="smile", mustache="#C9C9C9",
         shirt=dict(color="#3E5C8A", sleeves="long", cuff="#34507A", stof="katoen"), name_tag=True,
         pants="#3E5C8A", pants_stof="katoen", shoes="#2A2A2A", hair=dict(style="buzz", color="#C9C9C9"),
         hat="cap", cap=dict(color="#3E5C8A", visor="#2A3E5E"), prop="broom"),
    dict(key="scooterrijder", naam="Scooterrijder met helm (dag 5)", rol="(geen tekst)",
         body=dict(leg=1.04, torso=1.02, width=1.0, arm=1.0, head=0.98),
         skin="licht", eyes="blauw", brows=dict(color="#5B3A24"), mouth="flat",
         shirt=dict(color="#2A2A30", sleeves="long", cuff="#2A2A30", stof="nylon"),
         jacket=dict(color="#C8283A", stof="nylon"), pants="#2E3440", shoes="#1A1A1A",
         hat="guard", helmet="#F2F2F2"),
    dict(key="vrouw_hond", naam="Vrouw met hond (dag 1)", rol="(geen tekst)",
         body=dict(leg=1.04, torso=0.98, width=0.92, hips=1.04, shoulders=0.92, arm=0.88, head=0.96),
         skin="donker", eyes="donker", brows=dict(color="#1E1410"), mouth="smile", lashes=True,
         shirt=dict(color="#F6D04D", sleeves="long", cuff="#E0AE3C", stof="breisel"), pants="#2E3440",
         shoes="#F2F2F2", hair=dict(style="curly", color="#1E1410"), scarf=dict(color="#2F9C95", stripes="#F2F2F2")),
    dict(key="postbode", naam="Postbode op de fiets (dag 1)", rol="(geen tekst)",
         body=dict(leg=1.04, torso=1.02, width=1.0, arm=1.0, head=0.98),
         skin="olijf", eyes="groen", brows=dict(color="#3B2416"), mouth="smile",
         shirt=dict(color="#E5483E", sleeves="short", stof="katoen"), chest_logo="#F6D04D",
         shorts="#2B4170", shoes="#1A1A1A", hair=dict(style="short", color="#3B2416"),
         hat="cap", cap=dict(color="#E5483E", visor="#2B4170"), backpack="#E5483E"),
    _variant("oma", "oude_dame_bus", "Oude dame die de bus haalt (dag 1)", skin="olijf",
             hair=dict(style="curly_bun", color="#E8E4DA"), cardigan=dict(color="#C97A4A", buttons="#F2EEE8"),
             skirt=dict(color="#5A4A6B", bottom=0.2), prop="bag"),
]
# leerlingen voor het schoolplein en de gymzaal (300 instanties met kleurvariatie in de animatie)
for _k, (_sk, _hc, _hs, _sh, _pt) in enumerate((
        ("licht", "#5B3A24", "short", "#2D6CDF", "#3B3F49"), ("bruin", "#1E1410", "curly", "#E5483E", "#2E3440"),
        ("roze", "#C9772E", "ponytail", "#6CBF4B", "#3E5C8A"), ("olijf", "#2A1A10", "bob", "#F6D04D", "#4B4F57"),
        ("donker", "#1E1410", "buzz", "#7A5BC9", "#2E3440"), ("midden", "#3B2416", "pigtails", "#E86FA0", "#3B3F49"))):
    CAST_DL.append(dict(key=f"leerling_{'abcdef'[_k]}", naam=f"Leerling {_k + 1} (schoolplein, gymzaal)",
                        rol="(geen tekst)",
                        body=dict(leg=0.9 + 0.03 * (_k % 3), torso=0.9, width=0.9 + 0.04 * (_k % 2), arm=0.9,
                                  head=0.95),
                        skin=_sk, eyes=("bruin", "blauw", "groen")[_k % 3], brows=dict(color=_hc),
                        mouth=("smile", "grin", "flat")[_k % 3], lashes=_hs in ("ponytail", "bob", "pigtails"),
                        shirt=dict(color=_sh, sleeves="long" if _k % 2 else "short", stof="katoen"),
                        pants=_pt, shoes=("#F4F1E9", "#E5483E", "#1A1A1A")[_k % 3],
                        hair=dict(style=_hs, color=_hc), backpack=("#2D6CDF", "#F6D04D", "#3A3F47")[_k % 3]))


def _cast_dl():
    keep = ("mama", "papa", "oma", "broertje", "pestkop", "nieuwslezeres", "opa")
    base = [c for c in CAST if c["key"] in keep]
    nr = [_nr(k) for k in ("figurant_a", "figurant_b", "figurant_c", "figurant_d", "figurant_e", "figurant_f")]
    return base + [_10x("broertje_dino"), _10x("bezorger")] + nr + CAST_DL


# ---------------------------------------------------------------------------
# Opbouw van één figuur
# ---------------------------------------------------------------------------
DETAILS = True


def _darker(hexcol, k=0.82):
    r, g, b = (int(hexcol.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02X%02X%02X" % (int(r * k), int(g * k), int(b * k))


def _lighter(hexcol, k=0.35):
    r, g, b = (int(hexcol.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02X%02X%02X" % tuple(int(c + (255 - c) * k) for c in (r, g, b))


def slice_part(B, src, label, mat, keep, offset, cat, schoen=False):
    """Kopie van een deel van een mesh (vlakken waarvan het midden voldoet aan keep(co)),
    een paar mm naar buiten geschoven: zolen, zomen, boorden die precies passen."""
    bm = bmesh.new()
    bm.from_mesh(src.data)
    bm.transform(src.matrix_world)
    bm.normal_update()
    kill = [f for f in bm.faces if not keep(f.calc_center_median())]
    bmesh.ops.delete(bm, geom=kill, context="FACES")
    loose = [v for v in bm.verts if not v.link_faces]
    bmesh.ops.delete(bm, geom=loose, context="VERTS")
    if not bm.faces:
        bm.free()
        return None
    for v in bm.verts:
        v.co += v.normal * offset
    ob = B._obj(bm, label, mat, cat)
    if schoen:
        ob["schoen"] = True
    return ob


def add_details(spec, B, parts, mats, M_shirt, M_legs):
    key = spec["key"]
    shoe = spec.get("shoes", "#F2EEE8")
    r, g, b = (int(shoe.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    dark = (r + g + b) / 3 < 110
    sole = spec.get("sole") or ("#3A2E26" if dark and spec.get("dress_shoes", True) else "#EEEAE2")
    if (r + g + b) / 3 > 215 and not spec.get("sole"):
        sole = "#C9CDD3"   # witte sneakers: grijze zool zodat hij te zien is
    M_sole = mats.pbr(sole, stof="rubber")
    for i, s in ((1, "R"), (3, "L")):
        if i not in parts:
            continue
        o = parts[i]
        zmin = min((o.matrix_world @ Vector(c)).z for c in o.bound_box)
        slice_part(B, o, f"schoen_zool_{s}", M_sole, lambda c, z=zmin: c.z < z + 0.032, 0.0035,
                   part_cat(i), schoen=True)
        if not dark:
            # neus van de sneaker in de zoolkleur
            ymin = min((o.matrix_world @ Vector(c)).y for c in o.bound_box)
            slice_part(B, o, f"schoen_neus_{s}", M_sole,
                       lambda c, z=zmin, y=ymin: c.y < y + 0.045 and c.z < z + 0.07, 0.0025,
                       part_cat(i), schoen=True)
    # zoom onderaan de broekspijpen (niet bij korte broek, rok of blote benen)
    if not (spec.get("shorts") or spec.get("legs") or spec.get("skirt") or spec.get("onesie")):
        pc = spec.get("pants") or "#333333"
        M_z = mats.pbr(_darker(pc, 0.8), stof=pants_stof(pc))
        for i, s in ((0, "R"), (2, "L")):
            if i in parts:
                o = parts[i]
                zmin = min((o.matrix_world @ Vector(c)).z for c in o.bound_box)
                slice_part(B, o, f"been_zoom_{s}", M_z, lambda c, z=zmin: c.z < z + 0.035, 0.003,
                           part_cat(i))
    # boord onderaan het shirt/de trui en om de hals (niet onder jassen en jurken)
    covered = any(spec.get(k) for k in ("labcoat", "uniform", "blazer", "jacket", "onesie",
                                        "cardigan", "vest", "shorts", "skirt"))
    sh = spec["shirt"]
    if not covered and 4 in parts:
        o = parts[4]
        M_rib = mats.pbr(_darker(sh["color"], 0.86), stof="breisel")
        slice_part(B, o, "romp_boord", M_rib, lambda c: c.z < 0.655, 0.0035, "torso")
        if not spec.get("tie") and not sh.get("zipper") and not spec.get("hoodie"):
            slice_part(B, o, "romp_halsboord", M_rib, lambda c: c.z > 1.165, 0.003, "torso")


def build_character(spec, base_parts, unlit_tpl, parent_coll):
    key = spec["key"]
    coll = bpy.data.collections.new(key)
    parent_coll.children.link(coll)
    mats = Mats(unlit_tpl, key)
    B = Builder(coll, key, mats)

    skin, skin_dark = SKIN[spec["skin"]]
    M_skin = mats.pbr(skin, stof="huid")
    M_skin_dark = mats.pbr(skin_dark, stof="huid")
    shirt = spec["shirt"]
    st_shirt = shirt.get("stof", "katoen")
    M_shirt = mats.pbr(shirt["color"], stof=st_shirt)
    M_sleeve = mats.pbr(shirt.get("sleeve_color", shirt["color"]),
                        stof=shirt.get("sleeve_stof", st_shirt))
    M_cuff = mats.pbr(shirt.get("cuff", shirt.get("sleeve_color", shirt["color"])),
                      stof=shirt.get("sleeve_stof", st_shirt))
    pants_col = spec.get("pants") or spec.get("shorts") or "#333333"
    legs_col = spec.get("legs")
    if legs_col == "SKIN" or spec.get("shorts"):
        M_legs = M_skin
    elif legs_col:
        M_legs = mats.pbr(legs_col, stof="nylon")
    else:
        M_legs = mats.pbr(pants_col, stof=spec.get("pants_stof") or pants_stof(pants_col))
    M_shoes = mats.pbr(spec.get("shoes", "#F2EEE8"), stof="schoen")
    iris1, iris2 = EYES[spec.get("eyes", "bruin")]
    brows = spec.get("brows", {})
    M_brow = mats.unlit(brows.get("color", "#3B2416"))
    M_line = mats.unlit("#1B1214")
    M_mouth = mats.unlit("#3B2416")

    long_hair = spec.get("hair", {}).get("style") in ("bob",) or bool(spec.get("onesie"))

    # --- 1. kopie van het hoofdpersonage ------------------------------------
    parts = {}
    for i, src in base_parts.items():
        if i in HOODIE_EXTRAS and not spec.get("hoodie"):
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
    if spec.get("eyes") != "hero":
        for i in (35, 42):
            setmat(i, mats.unlit(iris1))
        for i in (36, 43):
            setmat(i, mats.unlit(iris2))
        for i in (33, 40):
            setmat(i, M_line)
    if not brows.get("keep"):
        for i in (47, 48, 49, 50, 51, 52):
            setmat(i, M_brow)
        setmat(53, M_mouth)
    if spec.get("hoodie"):
        # capuchon en buidelzak in de trui-kleur, koordjes in de kleur van de manchetten
        for i in (5, 12):
            setmat(i, M_shirt)
        for i in (6, 7, 8, 9, 10, 11):
            setmat(i, M_cuff)

    # --- 1b. details (glans 2): rubberzolen, zomen ----------------------------
    if DETAILS:
        add_details(spec, B, parts, mats, M_shirt, M_legs)

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
    if not spec.get("blush") and not spec.get("no_blush") and DETAILS:
        # glans 2: iedereen een heel zachte blos, afgeleid van de eigen huidskleur
        sr, sg, sb = (int(skin.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
        spec = dict(spec, blush="#%02X%02X%02X" % (int(sr * 0.7 + 0xE8 * 0.3),
                                                   int(sg * 0.7 + 0x70 * 0.3),
                                                   int(sb * 0.7 + 0x5F * 0.3)))
    if spec.get("blush"):
        M_bl = mats.pbr(spec["blush"], rough=1.0, stof="huid")
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
        M_m = mats.pbr(spec["mustache"], stof="haar")
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
        M_h = mats.pbr(hair["color"], rough=0.75, stof="haar")
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
        M_b = mats.pbr(spec["beard"]["color"], rough=0.8, stof="haar")

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
        pk = spec.get("peaked", {})
        M_cr = mats.pbr(pk.get("color", "#5B6B3A"), stof="wol")
        M_band = mats.pbr(pk.get("band", "#2B2A22"))
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
        M_bn = mats.pbr(spec.get("beanie", "#3A3F47"), stof="breisel")
        B.shell("muts", M_bn, lambda a: 0.42, radius=HEAD_R * 1.06, scale=(1.0, 1.0, 1.08),
                thick=0.016)
        B.torus("muts_rand", M_bn, (0, 0, HEAD_C.z + HEAD_R * 0.4), HEAD_R * 0.98, 0.028,
                normal=(0, 0, 1), cat="head")

    # --- 4b. dinopyjama (onesie met capuchon, stekels, buik en staart) ----------
    if spec.get("onesie"):
        on = spec["onesie"]
        M_on = mats.pbr(on["color"], stof="pluche")
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
        M_sh = mats.pbr(spec["shorts"], stof=pants_stof(spec["shorts"]))
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
        M_c = mats.pbr(c["color"], stof="breisel")
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
        M_v = mats.pbr(v["color"], stof="nylon")
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
        M_j = mats.pbr(c["color"], rough=0.5 if spec.get("jacket") else 0.85,
                       stof=c.get("stof", "leer" if spec.get("jacket") else "wol"))
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
        M_lc = mats.pbr("#FAFAFA", stof="katoen")
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
        uf = spec["uniform"] if isinstance(spec["uniform"], dict) else {}
        M_belt = mats.pbr(uf.get("belt", "#4A3424"), rough=0.5, stof="leer")
        M_gold = mats.pbr(uf.get("metal", "#D4AF37"), rough=0.3, metal=1.0)
        M_pk = mats.pbr(uf.get("pocket", "#4E5C32"), stof="katoen")
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
        for k in range(3 if uf.get("ribbons", True) else 0):
            B.body_disc(f"lintje{k}", M_rib[k], math.radians(26 + 7 * k), 1.07, 0.012, thick=0.004,
                        lift=0.008, sz=0.008)

    if spec.get("skirt"):
        sk = spec["skirt"]
        M_sk = mats.pbr(sk["color"], stof=sk.get("stof", "katoen"))
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
        B.sphere("fluitje_bol", M_wh, (0.012, yc, zc - 0.018), (0.022, 0.022, 0.022), cat="torso")
        for side in (-1, +1):
            B.cylinder(f"fluitkoord_{'L' if side > 0 else 'R'}", M_lan, (side * 0.07, -0.09, 1.19),
                       (side * 0.012, yc + 0.006, zc + 0.012), 0.005, cat="torso", seg=8)

    if spec.get("badge"):
        # politiepenning: los object "badge", zodat hij later weg kan (drop=("badge",))
        M_bd = mats.pbr("#D4AF37", rough=0.3, metal=1.0)
        B.body_disc("badge", M_bd, math.radians(30), 1.105, 0.034, thick=0.007, lift=0.012,
                    sz=0.04)
        B.body_disc("badge_ster", mats.pbr("#F3D46A", rough=0.25, metal=1.0), math.radians(30),
                    1.105, 0.016, thick=0.004, lift=0.019)
    if spec.get("name_tag"):
        B.body_disc("naamkaartje", mats.pbr("#FFFFFF"), math.radians(-26), 1.04, 0.026,
                    thick=0.004, lift=0.006, sz=0.014)

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

    # --- 6b. video 4 (Never Die): ouderdom, sjaal, sikje, helmen, gloeiende stof, rafels ---
    def part_center(i):
        o = parts.get(i)
        if o is None:
            return None
        cs = [o.matrix_world @ Vector(c) for c in o.bound_box]
        return sum(cs, Vector()) / 8, max((c - sum(cs, Vector()) / 8).length for c in cs)

    if spec.get("wrinkles"):
        # rimpels: lijntjes op het voorhoofd, kraaienpootjes en lachlijnen (in de donkere huidtint)
        M_wr = mats.unlit(_darker(skin_dark, 0.92))
        for k, (z, w) in enumerate(((1.628, 0.07), (1.648, 0.06))):
            B.face_disc(f"rimpel_voorhoofd{k}", M_wr, 0.0, z, w, 0.0032, lift=0.003)
        for side in (-1, +1):
            s_ = "L" if side > 0 else "R"
            for k, ang in enumerate((-18, 0, 18)):
                a = math.radians(ang)
                B.face_disc(f"kraaienpoot_{s_}{k}", M_wr, side * 0.142, 1.497 + 0.012 * k - 0.012, 0.017, 0.0028,
                            lift=0.003, roll=side * a)
            B.face_disc(f"lachlijn_{s_}", M_wr, side * 0.062, 1.395, 0.03, 0.003, lift=0.003,
                        roll=-side * math.radians(62))

    if spec.get("goatee"):
        M_g = mats.pbr(spec["goatee"], stof="haar")
        p, n = face_point(0.0, 1.318, 0.008)
        B.sphere("sikje", M_g, p, (0.04, 0.02, 0.036), quat=n.to_track_quat("-Y", "Z"))
        for side in (-1, +1):
            p, n = face_point(side * 0.032, 1.402, 0.006)
            q = n.to_track_quat("-Y", "Z") @ Euler((0, side * math.radians(12), 0)).to_quaternion()
            B.sphere(f"snorretje_{'L' if side > 0 else 'R'}", M_g, p, (0.034, 0.011, 0.011), quat=q)

    if spec.get("scarf"):
        sc_ = spec["scarf"]
        M_sc = mats.pbr(sc_["color"], stof="breisel")
        B.torus("sjaal", M_sc, (0, 0.0, 1.19), 0.112, 0.042, normal=(0, 0.12, 1), cat="torso",
                scale=(1.0, 0.92, 1.0))
        yy = -torso_r(1.05)[1] - 0.03
        B.box("sjaal_eind", M_sc, (0.07, yy, 1.02), (0.075, 0.026, 0.3), rot=(math.radians(-6), 0, math.radians(-4)),
              cat="torso", bevel=0.4)
        if sc_.get("stripes"):
            M_ss = mats.pbr(sc_["stripes"], stof="breisel")
            for k, z in enumerate((0.93, 0.98)):
                B.box(f"sjaal_streep{k}", M_ss, (0.07, yy - 0.002, z), (0.078, 0.026, 0.018), cat="torso", bevel=0.4)

    if spec.get("earpiece"):
        M_ep = mats.pbr("#1A1A1A", rough=0.3)
        B.sphere("oortje", M_ep, (-0.312, -0.01, 1.455), (0.016, 0.016, 0.02))
        B.cylinder("oortje_draad", M_ep, (-0.31, -0.0, 1.43), (-0.17, 0.05, 1.17), 0.004, cat="head", seg=8)

    if spec.get("flower"):
        # corsage op de revers (bruidegom)
        M_fl = mats.pbr(spec["flower"], rough=0.6)
        B.body_disc("corsage", M_fl, math.radians(-30), 1.08, 0.026, thick=0.018, lift=0.03)
        B.body_disc("corsage_hart", mats.pbr("#F2C94C"), math.radians(-30), 1.08, 0.009, thick=0.01, lift=0.045)

    hat = spec.get("hat")
    if hat == "fire":
        # brandweerhelm: rood met brede klep achter en een gele schild-voorkant
        M_h = mats.pbr(spec.get("helmet", "#C8283A"), rough=0.3)
        B.shell("helm", M_h, lambda a: 0.18, radius=HEAD_R * 1.1, scale=(1.0, 1.04, 1.05), thick=0.02)
        B.cylinder("helm_rand", M_h, (0, 0.04, HEAD_C.z + 0.05), (0, 0.04, HEAD_C.z + 0.068), HEAD_R * 1.32,
                   cat="head", seg=48, squash=1.12)
        B.box("helm_kam", M_h, (0, 0.0, HEAD_C.z + HEAD_R * 1.12), (0.03, 0.42, 0.04), cat="head", bevel=0.4)
        B.box("helm_schild", mats.pbr("#F6D04D", rough=0.4), (0, -HEAD_R * 1.12, HEAD_C.z + 0.2),
              (0.11, 0.012, 0.09), rot=(math.radians(-18), 0, 0), cat="head", bevel=0.2)
    elif hat == "guard":
        # helm van de bewakers: wit met een donker vizier boven de ogen
        M_h = mats.pbr(spec.get("helmet", "#EEF1F4"), rough=0.25)
        B.shell("helm", M_h, lambda a: 0.12 + 0.1 * math.cos(a), radius=HEAD_R * 1.08, scale=(1.0, 1.02, 1.04),
                thick=0.02)
        B.shell("helm_vizier", mats.pbr("#141B24", rough=0.08), lambda a: 0.22, lambda a: 0.42,
                arange=(-math.radians(70), math.radians(70)), radius=HEAD_R * 1.12, thick=0.012)
        if spec.get("glow"):
            B.shell("helm_streep", mats.unlit(spec["glow"]["color"]), lambda a: 0.47, lambda a: 0.5,
                    arange=(-math.radians(80), math.radians(80)), radius=HEAD_R * 1.11, thick=0.006)
    elif hat == "bucket":
        # vissershoedje: zachte bol met een schuin aflopende rand en een band
        bk = spec.get("bucket", {})
        M_h = mats.pbr(bk.get("color", "#7C8A5A"), stof="katoen")
        B.shell("vissershoed", M_h, lambda a: 0.34, radius=HEAD_R * 1.07, scale=(1.0, 1.0, 1.06), thick=0.016)
        B.cylinder("vissershoed_rand", M_h, (0, 0, HEAD_C.z + HEAD_R * 0.36),
                   (0, 0, HEAD_C.z + HEAD_R * 0.36 - 0.06), HEAD_R * 1.04, HEAD_R * 1.42, cat="head", seg=48,
                   cap=False)
        B.cylinder("vissershoed_band", mats.pbr(bk.get("band", "#5A4A32"), stof="katoen"),
                   (0, 0, HEAD_C.z + HEAD_R * 0.4), (0, 0, HEAD_C.z + HEAD_R * 0.47), HEAD_R * 1.075,
                   cat="head", seg=48)
    elif hat == "flowerhat":
        hf = spec.get("flowerhat", {})
        M_h = mats.pbr(hf.get("color", "#B58FC9"), stof="wol")
        B.shell("hoed", M_h, lambda a: 0.38, radius=HEAD_R * 1.06, scale=(1.0, 1.0, 1.08), thick=0.016)
        B.cylinder("hoed_rand", M_h, (0, 0, HEAD_C.z + HEAD_R * 0.36), (0, 0, HEAD_C.z + HEAD_R * 0.36 + 0.014),
                   HEAD_R * 1.6, cat="head", seg=48)
        for k, (a, c) in enumerate(((0.5, "#F59AC2"), (0.8, "#FFFFFF"), (1.1, "#F6D04D"))):
            B.sphere(f"hoed_bloem{k}", mats.pbr(c, rough=0.6),
                     (math.sin(a) * HEAD_R * 1.04, -math.cos(a) * HEAD_R * 1.04, HEAD_C.z + HEAD_R * 0.48),
                     (0.035, 0.035, 0.03))

    def torso_ring2(z, pad):
        rx, ry = torso_r(z)
        return (z, rx + pad, ry + pad)

    if spec.get("glow"):
        # toekomstkleding: gloeiende banden om de romp en een streep over de borst
        gl = spec["glow"]
        M_gw = mats.unlit(gl["color"])
        pad = 0.03 if any(spec.get(k) for k in ("jacket", "blazer", "vest", "labcoat", "cardigan")) else 0.006
        for k, z in enumerate(gl.get("rings", (0.66, 1.1))):
            B.loft(f"gloei_band{k}", M_gw, [torso_ring2(z - 0.008, pad), torso_ring2(z + 0.008, pad)], thick=0)
        if gl.get("stripe", True):
            for k, z in enumerate((0.74, 0.8, 0.86, 0.92, 0.98, 1.04)):
                B.body_disc(f"gloei_streep{k}", M_gw, math.radians(gl.get("angle", 22)), z, 0.009, thick=0.003,
                            lift=pad + 0.004, sz=0.03)
        for i in (16, 23):
            c = part_center(i)
            if c:
                side = 1 if i == 23 else -1
                B.torus(f"gloei_manchet_{'L' if side > 0 else 'R'}", M_gw, c[0], c[1] * 0.62, 0.006,
                        normal=(0, 0, 1), cat="arm+" if side > 0 else "arm-")

    if spec.get("sleeve_over"):
        # te groot pak: de mouwen hangen half over de handen
        for cuff_i, hand_i, side in ((16, 17, -1), (23, 24, +1)):
            c, h = part_center(cuff_i), part_center(hand_i)
            if not (c and h):
                continue
            a = c[0]
            b = c[0] + (h[0] - c[0]) * 0.62
            B.cylinder(f"mouw_te_lang_{'L' if side > 0 else 'R'}", M_sleeve, a, b, c[1] * 0.78, c[1] * 0.86,
                       cat="arm+" if side > 0 else "arm-", seg=20)

    if spec.get("mittens"):
        M_mt = mats.pbr(spec["mittens"], stof="breisel")
        for hand_i, side in ((17, -1), (24, +1)):
            h = part_center(hand_i)
            if h:
                B.sphere(f"want_{'L' if side > 0 else 'R'}", M_mt, h[0] + Vector((0, 0, -0.012)),
                         (0.055, 0.05, 0.075), cat="arm+" if side > 0 else "arm-")

    if spec.get("rafels"):
        # versleten kleren: donkere vlekken, lapjes en rafels aan de zoom
        rf = spec["rafels"] if isinstance(spec["rafels"], dict) else {}
        rnd = random.Random(hash(key) & 0xFFFF)
        M_vl = mats.pbr(_darker(shirt["color"], 0.6), stof=st_shirt)
        M_lap = mats.pbr(rf.get("patch", "#6B5A45"), stof="katoen")
        for k in range(rf.get("stains", 6)):
            B.body_disc(f"vlek{k}", M_vl, rnd.uniform(-1.4, 1.4), rnd.uniform(0.7, 1.08), rnd.uniform(0.02, 0.04),
                        thick=0.002, lift=0.003, sz=rnd.uniform(0.015, 0.035))
        for k in range(rf.get("patches", 2)):
            B.body_disc(f"lapje{k}", M_lap, rnd.uniform(-1.0, 1.0), rnd.uniform(0.72, 1.0), 0.04, thick=0.004,
                        lift=0.005, sz=0.035)
        M_hem = mats.pbr(_darker(shirt["color"], 0.85), stof=st_shirt)
        for k in range(28):
            t = 2 * math.pi * k / 28 + rnd.uniform(-0.05, 0.05)
            rx, ry = torso_r(0.62)
            L = rnd.uniform(0.02, 0.055)
            B.box(f"rafel{k}", M_hem, ((rx + 0.004) * math.sin(t), -(ry + 0.004) * math.cos(t), 0.62 - L / 2),
                  (0.022, 0.006, L), rot=(0, 0, -t), cat="torso", bevel=0)

    if prop == "keys":
        M_k = mats.pbr("#C9CCD1", rough=0.25, metal=1.0)
        B.torus("sleutelring", M_k, hand + Vector((0.0, -0.06, -0.05)), 0.022, 0.003, normal=(1, 0, 0), cat="arm-")
        for k, ang in enumerate((-25, 10)):
            a = math.radians(ang)
            B.box(f"sleutel{k}", M_k, hand + Vector((0.0, -0.06 + 0.03 * math.sin(a), -0.09 - 0.02 * math.cos(a))),
                  (0.004, 0.012, 0.05), rot=(a, 0, 0), cat="arm-", bevel=0.2)
        B.box("autosleutel", mats.pbr("#1A1A1A", rough=0.4), hand + Vector((0.0, -0.075, -0.035)),
              (0.012, 0.025, 0.04), cat="arm-", bevel=0.4)
    elif prop == "holo":
        # zwevend hologramscherm boven de hand (toekomst)
        M_ho = mats.unlit(spec.get("glow", {}).get("color", "#5CF2FF"))
        B.box("hologram", M_ho, hand + Vector((0.0, -0.12, 0.2)), (0.004, 0.16, 0.11),
              rot=(math.radians(-10), 0, 0), cat="arm-", bevel=0)
        B.box("hologram_band", mats.pbr("#2A2F3A", rough=0.3), hand + Vector((0.0, 0.0, 0.07)), (0.07, 0.07, 0.02),
              cat="arm-", bevel=0.4)

    # --- 6b. accessoires video 5 (koptelefoon, stethoscoop, rugzak, pleister, bretels, props) ---
    if spec.get("headphones"):
        hp = spec["headphones"] if isinstance(spec["headphones"], dict) else {}
        M_hb = mats.pbr(hp.get("color", "#E5483E"), rough=0.3)
        M_hc = mats.pbr(hp.get("cup", "#1A1A1A"), rough=0.35)
        R_b = HEAD_R * 1.1
        pts = [HEAD_C + Vector((math.sin(t) * R_b, 0.01, math.cos(t) * R_b))
               for t in [math.radians(a) for a in range(-96, 97, 12)]]
        for k in range(len(pts) - 1):
            B.cylinder(f"koptelefoon_band{k}", M_hb, pts[k], pts[k + 1], 0.016, cat="head", seg=12)
        for side in (-1, +1):
            s_ = "L" if side > 0 else "R"
            c = HEAD_C + Vector((side * HEAD_R * 1.02, 0.01, -0.02))
            B.cylinder(f"koptelefoon_schelp_{s_}", M_hc, c, c + Vector((side * 0.07, 0, 0)), 0.088, 0.08,
                       cat="head", seg=28)
            B.cylinder(f"koptelefoon_kussen_{s_}", mats.pbr("#2A2A2A", rough=0.9), c - Vector((side * 0.012, 0, 0)),
                       c + Vector((side * 0.004, 0, 0)), 0.082, cat="head", seg=28)
            B.cylinder(f"koptelefoon_logo_{s_}", M_hb, c + Vector((side * 0.07, 0, 0)),
                       c + Vector((side * 0.074, 0, 0)), 0.04, cat="head", seg=20)

    if spec.get("stethoscope"):
        M_st = mats.pbr("#1A1A1A", rough=0.35)
        M_sm = mats.pbr("#C9CCD1", rough=0.2, metal=1.0)
        z0 = 1.15
        rx, ry = torso_r(z0)
        B.torus("stethoscoop_nek", M_st, (0, 0.0, z0), (rx + ry) / 2 + 0.03, 0.009, normal=(0, 0, 1),
                cat="torso", arc=(math.radians(-60), math.radians(240)))
        for side in (-1, +1):
            a = Vector((side * 0.13, -ry - 0.02, z0 - 0.01))
            b = Vector((side * 0.11, -torso_r(0.95)[1] - 0.035, 0.95))
            B.cylinder(f"stethoscoop_slang_{'L' if side > 0 else 'R'}", M_st, a, b, 0.009, cat="torso", seg=10)
        B.cylinder("stethoscoop_borststuk", M_sm, (0.11, -torso_r(0.93)[1] - 0.04, 0.93),
                   (0.11, -torso_r(0.93)[1] - 0.055, 0.93), 0.028, cat="torso", seg=20)

    if spec.get("backpack"):
        M_bp = mats.pbr(spec["backpack"], stof="nylon")
        M_bs = mats.pbr(_darker(spec["backpack"], 0.7), stof="nylon")
        rx, ry = torso_r(0.88)
        B.box("rugzak", M_bp, (0, ry + 0.07, 0.86), (0.3, 0.15, 0.36), cat="torso", bevel=0.35)
        B.box("rugzak_vak", M_bs, (0, ry + 0.15, 0.8), (0.22, 0.05, 0.16), cat="torso", bevel=0.4)
        pad = 0.022 if any(spec.get(k) for k in ("hoodie", "jacket", "blazer", "cardigan", "vest")) else 0.01
        for side in (-1, +1):
            s_ = "L" if side > 0 else "R"
            # schouderband: plat op de borst, van de schouder naar de onderkant van de rugzak
            B.body_disc(f"rugzak_band_{s_}", M_bs, math.radians(side * 26), 0.98, 0.024, thick=0.006,
                        lift=pad, sz=0.17)
            B.body_disc(f"rugzak_gesp_{s_}", mats.pbr("#2A2A2A", rough=0.4), math.radians(side * 26), 0.88, 0.02,
                        thick=0.006, lift=pad + 0.005, sz=0.014)
            B.sphere(f"rugzak_schouder_{s_}", M_bs, (side * 0.13, 0.0, 1.13), (0.03, 0.17, 0.02), cat="torso")

    if spec.get("suspenders"):
        M_su = mats.pbr(spec["suspenders"], stof="katoen")
        for side in (-1, +1):
            B.body_disc(f"bretel_{'L' if side > 0 else 'R'}", M_su, math.radians(side * 22), 0.88, 0.016,
                        thick=0.004, lift=0.006, sz=0.24)

    if spec.get("plaster"):
        M_pl = mats.pbr("#E9C9A6", rough=0.6)
        B.face_disc("pleister", M_pl, 0.15, 1.43, 0.05, 0.022, thick=0.004, lift=0.004, roll=math.radians(20))

    if prop == "coffee":
        M_cu = mats.pbr("#F2EEE6", rough=0.5)
        B.cylinder("koffiebeker", M_cu, hand + Vector((0, -0.05, -0.04)), hand + Vector((0, -0.05, 0.1)),
                   0.034, 0.042, cat="arm-", seg=24)
        B.cylinder("koffiebeker_hoes", mats.pbr("#8A5A3A", rough=0.8), hand + Vector((0, -0.05, 0.0)),
                   hand + Vector((0, -0.05, 0.05)), 0.0395, 0.0415, cat="arm-", seg=24)
        B.cylinder("koffiebeker_deksel", mats.pbr("#2A2A2A", rough=0.4), hand + Vector((0, -0.05, 0.1)),
                   hand + Vector((0, -0.05, 0.115)), 0.044, 0.04, cat="arm-", seg=24)
    elif prop == "broom":
        M_wd = mats.pbr("#B58A5A", rough=0.6)
        B.cylinder("bezemsteel", M_wd, hand + Vector((0, -0.03, 0.35)), (-0.36, -0.2, 0.08), 0.014, cat="arm-")
        B.box("bezem_kop", mats.pbr("#3A3A3A", rough=0.5), (-0.37, -0.21, 0.06), (0.36, 0.06, 0.05), cat="arm-",
              bevel=0.3)
        B.box("bezem_haren", mats.pbr("#C9A24A", rough=0.95), (-0.37, -0.21, 0.02), (0.34, 0.05, 0.05),
              cat="arm-", bevel=0.1)
    elif prop == "bag":
        M_bg = mats.pbr("#2F9C95", stof="katoen")
        B.box("boodschappentas", M_bg, hand + Vector((0, -0.02, -0.17)), (0.07, 0.24, 0.26), cat="arm-", bevel=0.3)
        B.torus("boodschappentas_hengsel", M_bg, hand + Vector((0, -0.02, -0.03)), 0.06, 0.007, normal=(1, 0, 0),
                arc=(0, math.pi), cat="arm-")
        B.sphere("boodschappentas_brood", mats.pbr("#D9A55A", rough=0.8), hand + Vector((0, -0.05, -0.02)),
                 (0.03, 0.03, 0.07), cat="arm-")

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

    src = {"10x": CAST_10X, "nr": CAST + CAST_NR, "nd": _cast_nd(), "dl": _cast_dl()}.get(opts["--cast"], CAST)
    specs = [s for s in src if not only or s["key"] in only]
    built = []
    for spec in specs:
        coll, root, head_c, zmax = build_character(spec, base_parts, unlit_tpl, cast_coll)
        built.append((spec, coll, root, head_c, zmax))
        print("gebouwd:", spec["key"], "lengte %.2f m" % zmax)

    cam = setup_render(int(opts["--samples"]))
    blend = {"10x": "cast_10x_faster.blend", "nr": "cast_no_rules.blend", "nd": "cast_never_die.blend",
             "dl": "cast_days_left.blend"}.get(opts["--cast"],
                                                                             "cast_video1.blend")
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
