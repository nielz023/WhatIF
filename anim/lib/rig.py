"""Rig, gezicht en materialen voor de figuren van 3D What If Channel.

Laadt een figuur (hoofdpersonage of bijfiguur uit de cast, .glb) in een scène en
maakt er een animeerbaar personage van:

- alle onderdelen worden één mesh met een Armature-modifier (benen buigen in de
  knie, de romp buigt mee, armen, handen en hoofd zijn stijf aan hun bot);
- een skelet met IK voor de voeten (blijven op de grond staan) en schakelbare
  IK voor de handen (iets vastpakken);
- een gezicht met knipperende ogen, kijkrichting, wenkbrauwen en een nieuwe mond
  met vormen (open, lach, verdrietig, O, breed, grijns) voor lipsync;
- toon-materialen en contourlijnen in dezelfde stijl als de sets.

Alle gezichtsknoppen zijn eigenschappen op het rig-object (bijvoorbeeld
rig["mond_open"]), zodat je ze in Blender gewoon kunt keyframen.

Assen van elk bot (handig bij het poseren): Y loopt langs het bot, Z wijst naar
voren (waar het personage naartoe kijkt) en X naar opzij. Positieve X-rotatie
buigt een bot naar voren (heup, schouder, elleboog, rug, hoofd knikt). Voor de
knie is buigen dus een negatieve X-rotatie.
"""
import math
import os
import sys

import bpy
import bmesh
from mathutils import Vector, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "sets"))
from lib import toon as T  # noqa: E402

ASSETS = os.environ.get("WHATIF_ASSETS", os.path.join(REPO, "assets"))
HERO_GLB = os.path.join(ASSETS, "hoofdpersonage.glb")


def cast_glb(name):
    return os.path.join(ASSETS, "cast", name + ".glb")


# Onderdelen van het hoofdpersonage (index = nummer in de glb, zie cast/build_cast.py)
HERO_PARTS = {
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

# Gezichtsknoppen op het rig-object: naam -> (standaard, min, max)
FACE_PROPS = {
    "knipper": (0.0, 0.0, 1.0), "knipper_L": (0.0, 0.0, 1.0), "knipper_R": (0.0, 0.0, 1.0),
    "ogen_wijd": (0.0, 0.0, 1.0), "ogen_knijp": (0.0, 0.0, 1.0), "pupil_klein": (0.0, 0.0, 1.0),
    "kijk_x": (0.0, -1.0, 1.0), "kijk_y": (0.0, -1.0, 1.0),
    "wenkbrauw_op": (0.0, -1.0, 1.0), "wenkbrauw_boos": (0.0, -1.0, 1.0),
    "wenkbrauw_op_L": (0.0, -1.0, 1.0), "wenkbrauw_op_R": (0.0, -1.0, 1.0),
    "mond_open": (0.0, 0.0, 1.0), "mond_lach": (0.0, 0.0, 1.0), "mond_verdrietig": (0.0, 0.0, 1.0),
    "mond_O": (0.0, 0.0, 1.0), "mond_breed": (0.0, 0.0, 1.0), "mond_grijns": (0.0, 0.0, 1.0),
}
MOUTH_KEYS = ["mond_open", "mond_lach", "mond_verdrietig", "mond_O", "mond_breed", "mond_grijns"]


# ---------------------------------------------------------------------------
# Hulpjes
# ---------------------------------------------------------------------------
def _bbox(objs):
    pts = [o.matrix_world @ v.co for o in objs for v in o.data.vertices]
    mn = Vector([min(p[i] for p in pts) for i in range(3)])
    mx = Vector([max(p[i] for p in pts) for i in range(3)])
    return mn, mx, pts


def _center(objs):
    mn, mx, _ = _bbox(objs)
    return (mn + mx) / 2


def _axis_ends(o):
    """Twee uiteinden van een langwerpig onderdeel (hoofdas via PCA)."""
    pts = [o.matrix_world @ v.co for v in o.data.vertices]
    c = sum(pts, Vector()) / len(pts)
    cov = [[0.0] * 3 for _ in range(3)]
    for p in pts:
        d = p - c
        for i in range(3):
            for j in range(3):
                cov[i][j] += d[i] * d[j]
    v = Vector((0.1, 0.2, 1.0))
    M = Matrix(cov)
    for _ in range(40):
        v = (M @ v).normalized()
    proj = [(p - c).dot(v) for p in pts]
    a, b = c + v * min(proj), c + v * max(proj)
    return (a, b) if a.z > b.z else (b, a)   # (boven, onder)


def _seg_dist(p, a, b):
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-9)))
    return (a + ab * t - p).length


def _smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


# ---------------------------------------------------------------------------
# Importeren
# ---------------------------------------------------------------------------
def _import(glb, name):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=glb)
    new = [o for o in bpy.data.objects if o not in before]
    parts = {}
    is_hero = any(o.name.startswith("Bram_part_") for o in new)
    prefix = None
    if not is_hero:
        roots = [o for o in new if o.parent is None]
        if roots:
            prefix = roots[0].name + "_"
    for o in new:
        if o.type != "MESH":
            continue
        mw = o.matrix_world.copy()
        o.parent = None
        o.matrix_world = mw
        if is_hero:
            idx = int(o.name.split("_")[-1].split(".")[0])
            pn = HERO_PARTS.get(idx, f"deel{idx}")
        else:
            pn = o.name.split(".")[0]
            if prefix and pn.startswith(prefix):
                pn = pn[len(prefix):]
        o.name = f"{name}_{pn}"
        parts[pn] = o
    # bake transforms
    for o in parts.values():
        o.data = o.data.copy()
        o.data.transform(o.matrix_world)
        o.matrix_world = Matrix.Identity(4)
    for o in new:
        if o.type != "MESH":
            bpy.data.objects.remove(o, do_unlink=True)
    return parts


FLAT_PARTS = ("oog_", "wenkbrauw", "wimper", "mond", "tong")


def _toon_materials(parts):
    for pn, o in parts.items():
        flat = pn.startswith(FLAT_PARTS)
        for slot in o.material_slots:
            ms = slot.material
            if not ms or ms.name.startswith("pers_"):
                continue
            col = tuple(ms.diffuse_color)[:3]
            if ms.node_tree:
                b = ms.node_tree.nodes.get("Principled BSDF")
                if b:
                    col = tuple(b.inputs["Base Color"].default_value)[:3]
            key = "pers_" + ms.name + f"_{col[0]:.2f}{col[1]:.2f}{col[2]:.2f}"
            slot.material = T.glow(key + "_vlak", col, 1.0) if flat else T.toon(key, col)


# ---------------------------------------------------------------------------
# Skelet
# ---------------------------------------------------------------------------
def _joints(parts):
    J = {}
    legs = {s: parts["been_" + s] for s in "LR"}
    for s, o in legs.items():
        mn, mx, _ = _bbox([o])
        cx = (mn.x + mx.x) / 2
        cy = (mn.y + mx.y) / 2
        top, bot = mx.z - 0.045, mn.z + 0.04
        J["hip." + s] = Vector((cx, cy, top))
        J["knee." + s] = Vector((cx, cy - 0.005, bot + (top - bot) * 0.48))
        J["ankle." + s] = Vector((cx, cy, bot))
        smn, smx, _ = _bbox([parts["schoen_" + s]])
        J["toe." + s] = Vector((cx, smn.y + 0.02, smn.z + 0.035))
        J["floor"] = smn.z
    rmn, rmx, _ = _bbox([parts["romp"]])
    J["pelvis"] = Vector((0, (rmn.y + rmx.y) / 2, (J["hip.L"].z + J["hip.R"].z) / 2))
    J["spine"] = Vector((0, J["pelvis"].y, rmn.z + (rmx.z - rmn.z) * 0.42))
    J["chest"] = Vector((0, J["pelvis"].y, rmn.z + (rmx.z - rmn.z) * 0.80))
    nmn, nmx, _ = _bbox([parts["nek"]])
    J["neck"] = Vector((0, (nmn.y + nmx.y) / 2, nmn.z))
    J["neck_top"] = Vector((0, (nmn.y + nmx.y) / 2, nmx.z))
    hmn, hmx, _ = _bbox([parts["hoofd"]])
    J["head_c"] = (hmn + hmx) / 2
    J["head_r"] = (hmx - hmn) / 2
    J["head_top"] = Vector((0, J["head_c"].y, hmx.z))
    for s in "LR":
        top, bot = _axis_ends(parts["bovenarm_" + s])
        sh = top + (bot - top).normalized() * 0.035
        J["shoulder." + s] = sh
        J["elbow." + s] = _center([parts["elleboog_" + s]])
        hand_objs = [parts[k] for k in ("hand_" + s, "vingers_" + s, "duim_" + s) if k in parts]
        hmn_, hmx_, _ = _bbox(hand_objs)
        cuff = _center([parts["manchet_" + s]]) if ("manchet_" + s) in parts else None
        hc = _center([parts["hand_" + s]])
        wrist = Vector((hc.x, hc.y, hmx_.z - 0.01))
        if cuff is not None:
            wrist = (wrist + cuff) / 2
        J["wrist." + s] = wrist
        J["hand_tip." + s] = Vector((hc.x, hc.y, hmn_.z + 0.01))
        J["eye." + s] = _center([parts["oog_%s_wit" % s]])
        w = parts["oog_%s_wit" % s]
        n = sum((w.matrix_world.to_3x3() @ p.normal for p in w.data.polygons), Vector()).normalized()
        if n.y > 0:
            n = -n
        J["eye_n." + s] = n
        J["brow." + s] = _center([parts["wenkbrauw_" + s]])
    J["mouth"] = _center([parts["mond"]])
    mmn, mmx, _ = _bbox([parts["mond"]])
    J["mouth_top"] = mmx.z
    J["mouth_w"] = (mmx.x - mmn.x) / 2
    return J


FWD = Vector((0, -1, 0))   # personages kijken naar -y


def _add_bone(eb, name, head, tail, parent=None, deform=True, roll_to=FWD, connect=False):
    b = eb.new(name)
    b.head, b.tail = head, tail
    b.align_roll(roll_to)
    b.use_deform = deform
    if parent:
        b.parent = eb[parent]
        b.use_connect = connect
    return b


def _build_armature(name, J, coll):
    arm = bpy.data.armatures.new(name + "_skelet")
    arm.display_type = "STICK"
    rig = bpy.data.objects.new("RIG_" + name, arm)
    coll.objects.link(rig)
    bpy.context.view_layer.objects.active = rig
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    rig.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    eb = arm.edit_bones
    up = Vector((0, 0, 1))
    _add_bone(eb, "root", Vector((0, 0, 0)), Vector((0, 0.35, 0)), deform=False, roll_to=up)
    _add_bone(eb, "hips", J["pelvis"], J["spine"], "root")
    _add_bone(eb, "spine", J["spine"], J["chest"], "hips", connect=True)
    _add_bone(eb, "chest", J["chest"], J["neck"], "spine", connect=True)
    _add_bone(eb, "neck", J["neck"], J["neck_top"], "chest")
    _add_bone(eb, "head", J["neck_top"], J["head_top"], "neck", connect=True)
    for s in "LR":
        _add_bone(eb, "thigh." + s, J["hip." + s], J["knee." + s], "hips")
        _add_bone(eb, "shin." + s, J["knee." + s], J["ankle." + s], "thigh." + s, connect=True)
        _add_bone(eb, "foot." + s, J["ankle." + s], J["toe." + s], "shin." + s, roll_to=up, connect=True)
        _add_bone(eb, "upper_arm." + s, J["shoulder." + s], J["elbow." + s], "chest")
        _add_bone(eb, "forearm." + s, J["elbow." + s], J["wrist." + s], "upper_arm." + s, connect=True)
        _add_bone(eb, "hand." + s, J["wrist." + s], J["hand_tip." + s], "forearm." + s, connect=True)
        # IK-doelen
        _add_bone(eb, "foot_ik." + s, J["ankle." + s], J["toe." + s], "root", deform=False, roll_to=up)
        kp = J["knee." + s] + FWD * 0.6
        _add_bone(eb, "knee_pole." + s, kp, kp + FWD * 0.1, "root", deform=False)
        _add_bone(eb, "hand_ik." + s, J["wrist." + s], J["hand_tip." + s], "root", deform=False)
        ep = J["elbow." + s] + Vector((0, 0.5, 0)) + Vector((0.15 if s == "L" else -0.15, 0, 0))
        _add_bone(eb, "elbow_pole." + s, ep, ep + Vector((0, 0.1, 0)), "chest", deform=False)
        # gezicht
        e = J["eye." + s]
        n = J["eye_n." + s]
        _add_bone(eb, "eye." + s, e, e + n * 0.05, "head", roll_to=up)
        _add_bone(eb, "pupil." + s, e, e + n * 0.04, "eye." + s, roll_to=up)
        b = J["brow." + s]
        _add_bone(eb, "brow." + s, b, b + FWD * 0.05, "head", roll_to=up)
    m = J["mouth"]
    _add_bone(eb, "mouth", m, m + FWD * 0.05, "head", roll_to=up)
    bpy.ops.object.mode_set(mode="OBJECT")
    for pb in rig.pose.bones:
        pb.rotation_mode = "XYZ"
    return rig


def _setup_ik(rig):
    pbs = rig.pose.bones
    for s in "LR":
        c = pbs["shin." + s].constraints.new("IK")
        c.target, c.subtarget = rig, "foot_ik." + s
        c.pole_target, c.pole_subtarget = rig, "knee_pole." + s
        c.chain_count = 2
        c.pole_angle = math.radians(-90)
        cr = pbs["foot." + s].constraints.new("COPY_ROTATION")
        cr.target, cr.subtarget = rig, "foot_ik." + s
        c = pbs["forearm." + s].constraints.new("IK")
        c.name = "Hand_IK"
        c.target, c.subtarget = rig, "hand_ik." + s
        c.pole_target, c.pole_subtarget = rig, "elbow_pole." + s
        c.chain_count = 2
        c.pole_angle = math.radians(-90)
        c.influence = 0.0
        c.use_stretch = True
        # armen mogen een beetje rekken als iets net buiten bereik ligt (cartoon)
        pbs["upper_arm." + s].ik_stretch = 0.12
        pbs["forearm." + s].ik_stretch = 0.12
        cr = pbs["hand." + s].constraints.new("COPY_ROTATION")
        cr.name = "Hand_IK_rot"
        cr.target, cr.subtarget = rig, "hand_ik." + s
        cr.influence = 0.0
    # beste poolhoek zoeken: rustpose moet gelijk blijven
    bpy.context.view_layer.update()
    for s in "LR":
        for bone, cname in (("shin." + s, "IK"), ("forearm." + s, "Hand_IK")):
            c = pbs[bone].constraints[cname]
            old_inf = c.influence
            c.influence = 1.0
            best, err_best = None, 1e9
            for ang in (-90, 0, 90, 180):
                c.pole_angle = math.radians(ang)
                bpy.context.view_layer.update()
                par = pbs[bone].parent
                err = (par.matrix.to_3x3() - rig.data.bones[par.name].matrix_local.to_3x3())
                e = sum(abs(err[i][j]) for i in range(3) for j in range(3))
                if e < err_best:
                    best, err_best = ang, e
            c.pole_angle = math.radians(best)
            c.influence = old_inf
    bpy.context.view_layer.update()


# ---------------------------------------------------------------------------
# Mond (nieuw opgebouwd, met vormen)
# ---------------------------------------------------------------------------
NCOL = 24


def _mouth_curves(J, shape):
    """Boven- en onderlip (lijst x, z) voor een mondvorm."""
    W = J["mouth_w"] * shape.get("w", 0.62)
    top = J["mouth_top"] - 0.010
    up, lo = [], []
    for i in range(NCOL + 1):
        u = -1 + 2 * i / NCOL
        x = u * W
        curve = shape.get("c", 0.010) * u * u + shape.get("skew", 0.0) * (u + 1) * 0.5 * u * u
        open_ = shape.get("open", 0.0) * math.sqrt(max(0.0, 1 - u * u))
        lift = shape.get("lift", 0.0) * math.sqrt(max(0.0, 1 - u * u))
        flat = shape.get("flat", 0.0)
        zu = top + curve + lift
        zl = top + curve - 0.0055 - open_ * (1 - flat) - flat * shape.get("open", 0.0) * (1 if abs(u) < 0.9 else 0.5)
        up.append((x, zu))
        lo.append((x, zl))
    return up, lo


MOUTH_SHAPES = {
    "basis": dict(w=0.62, c=0.008),
    "mond_open": dict(w=0.80, c=0.002, open=0.046, lift=0.004),
    "mond_lach": dict(w=0.95, c=0.026, open=0.014),
    "mond_verdrietig": dict(w=0.62, c=-0.016),
    "mond_O": dict(w=0.30, c=0.0, open=0.034, lift=0.012),
    "mond_breed": dict(w=1.05, c=-0.002, open=0.010, flat=0.7),
    "mond_grijns": dict(w=0.75, c=0.004, skew=0.030),
}


def _surface_y(J, x, z, off=0.0018):
    c, r = J["head_c"], J["head_r"]
    t = 1 - (x / r.x) ** 2 - ((z - c.z) / r.z) ** 2
    return c.y - r.y * math.sqrt(max(t, 0.0)) - off


def _build_mouth(name, J, mat_in, mat_tongue, coll):
    up, lo = _mouth_curves(J, MOUTH_SHAPES["basis"])
    bm = bmesh.new()
    vu = [bm.verts.new((x, 0, z)) for x, z in up]
    vl = [bm.verts.new((x, 0, z)) for x, z in lo]
    for i in range(NCOL):
        bm.faces.new((vu[i], vu[i + 1], vl[i + 1], vl[i]))
    # tong: ellips onderin de mond
    nt = 16
    tc = bm.verts.new((0, 0, 0))
    ring = [bm.verts.new((0, 0, 0)) for _ in range(nt)]
    for i in range(nt):
        f = bm.faces.new((tc, ring[i], ring[(i + 1) % nt]))
        f.material_index = 1
    me = bpy.data.meshes.new(name + "_mond")
    bm.to_mesh(me)
    bm.free()
    me.materials.append(mat_in)
    me.materials.append(mat_tongue)
    o = bpy.data.objects.new(name + "_mond", me)
    coll.objects.link(o)

    def coords(shape, tongue_open):
        up, lo = _mouth_curves(J, shape)
        pts = []
        for x, z in up + lo:
            pts.append(Vector((x, _surface_y(J, x, z), z)))
        # tong
        bottom = min(z for _, z in lo)
        topz = max(z for _, z in up)
        w = (up[-1][0] - up[0][0]) * 0.22 * tongue_open
        h = (topz - bottom) * 0.30 * tongue_open
        cz = bottom + h * 0.8
        tcen = Vector((0, _surface_y(J, 0, cz, 0.0026), cz))
        pts.append(tcen)
        for i in range(nt):
            a = 2 * math.pi * i / nt
            x, z = math.cos(a) * w, cz + math.sin(a) * h
            z = max(z, bottom + 0.001)
            pts.append(Vector((x, _surface_y(J, x, z, 0.0026), z)))
        return pts

    base = coords(MOUTH_SHAPES["basis"], 0.0)
    for v, p in zip(me.vertices, base):
        v.co = p
    o.shape_key_add(name="Basis")
    for key in MOUTH_KEYS:
        sk = o.shape_key_add(name=key, from_mix=False)
        tongue = {"mond_open": 1.0}.get(key, 0.0)
        for i, p in enumerate(coords(MOUTH_SHAPES[key], tongue)):
            sk.data[i].co = p
    return o


# ---------------------------------------------------------------------------
# Gewichten
# ---------------------------------------------------------------------------
def _bone_for(pn, o, J, segs):
    s = "L" if pn.endswith("_L") or "_L_" in pn or pn.endswith("_L0") or pn.endswith("_L1") else (
        "R" if pn.endswith("_R") or "_R_" in pn or pn.endswith("_R0") or pn.endswith("_R1") else None)
    if pn.startswith("oog_") and s:
        sub = pn.split("_", 2)[2] if pn.count("_") >= 2 else ""
        return "eye." + s if sub in ("lijn", "wit") else "pupil." + s
    if pn.startswith("wimper") and s:
        return "eye." + s
    if pn.startswith("wenkbrauw") and s:
        return "brow." + s
    if pn in ("mond", "tong"):
        return "mouth"
    if pn.startswith("schoen") and s:
        return "foot." + s
    if pn.startswith("bovenarm") or pn.startswith("mouwzoom"):
        return "upper_arm." + s
    if pn.startswith(("onderarm", "elleboog", "manchet")):
        return "forearm." + s
    if pn.startswith(("hand_", "duim", "vingers")):
        return "hand." + s
    if pn == "nek":
        return "neck"
    c = _center([o])
    if c.z > J["neck_top"].z - 0.02 or pn in ("hoofd",):
        return "head"
    if pn.startswith(("telefoon", "wandelstok")):
        # dichtstbijzijnde hand
        return min(("hand.L", "hand.R"), key=lambda b: _seg_dist(c, *segs[b]))
    return None   # romp-achtig: gemengd


def _weights(rig, parts, J):
    bones = rig.data.bones
    segs = {b.name: (b.head_local.copy(), b.tail_local.copy()) for b in bones}
    for pn, o in parts.items():
        groups = {}

        def g(b):
            if b not in groups:
                groups[b] = o.vertex_groups.new(name=b)
            return groups[b]
        b = _bone_for(pn, o, J, segs)
        if pn.startswith("been_"):
            s = pn[-1]
            hz, kz = J["hip." + s].z, J["knee." + s].z
            for v in o.data.vertices:
                z = v.co.z
                t = _smooth((z - (kz - 0.06)) / 0.12)    # 0 = scheen, 1 = dij
                th = _smooth((z - (hz - 0.02)) / 0.08)   # bovenin mee met heupen
                w_hip = th
                w_thigh = t * (1 - th)
                w_shin = 1 - t
                for bn, w in (("hips", w_hip), ("thigh." + s, w_thigh), ("shin." + s, w_shin)):
                    if w > 0.001:
                        g(bn).add([v.index], w, "REPLACE")
            continue
        if b:
            g(b).add([v.index for v in o.data.vertices], 1.0, "REPLACE")
            continue
        # romp en kleding: heupen -> rug -> borst
        z0, z1, z2 = J["pelvis"].z + 0.05, J["spine"].z, J["chest"].z
        for v in o.data.vertices:
            z = v.co.z
            a = _smooth((z - z0) / max(z1 - z0, 0.01))
            c = _smooth((z - z1) / max(z2 - z1, 0.01))
            w_h, w_s, w_c = 1 - a, a * (1 - c), a * c
            for bn, w in (("hips", w_h), ("spine", w_s), ("chest", w_c)):
                if w > 0.001:
                    g(bn).add([v.index], w, "REPLACE")


# ---------------------------------------------------------------------------
# Drivers voor het gezicht
# ---------------------------------------------------------------------------
def _driver(owner, path, index, expr, rig, props):
    fc = owner.driver_add(path, index) if index is not None else owner.driver_add(path)
    d = fc.driver
    d.type = "SCRIPTED"
    for p in props:
        var = d.variables.new()
        var.name = p
        var.targets[0].id = rig
        var.targets[0].data_path = f'["{p}"]'
    d.expression = expr
    return fc


def _face_drivers(rig, body, J):
    for k, (dflt, lo, hi) in FACE_PROPS.items():
        rig[k] = dflt
        ui = rig.id_properties_ui(k)
        ui.update(min=lo, max=hi, soft_min=lo, soft_max=hi)
    pbs = rig.pose.bones
    # bot-assen: eye/pupil/brow/mouth wijzen naar voren (Y = -y wereld), Z = omhoog
    for s in "LR":
        pb = pbs["eye." + s]
        _driver(pb, "scale", 2, f"max(0.06, 1 - 0.94*min(1, knipper + knipper_{s}) ) * (1 + 0.22*ogen_wijd - 0.38*ogen_knijp)",
                rig, ["knipper", "knipper_" + s, "ogen_wijd", "ogen_knijp"])
        _driver(pb, "scale", 0, "1 + 0.10*ogen_wijd", rig, ["ogen_wijd"])
        pp = pbs["pupil." + s]
        sx = -1 if s == "R" else 1
        _driver(pp, "location", 0, "-kijk_x*0.016", rig, ["kijk_x"])
        _driver(pp, "location", 2, "kijk_y*0.011", rig, ["kijk_y"])
        for ax in (0, 2):
            _driver(pp, "scale", ax, "1 - 0.40*pupil_klein", rig, ["pupil_klein"])
        pb = pbs["brow." + s]
        _driver(pb, "location", 2, f"(wenkbrauw_op + wenkbrauw_op_{s})*0.018 - 0.006*wenkbrauw_boos + 0.008*ogen_wijd",
                rig, ["wenkbrauw_op", "wenkbrauw_op_" + s, "wenkbrauw_boos", "ogen_wijd"])
        # binnenkant omlaag bij boos: rotatie om de as naar voren
        _driver(pb, "rotation_euler", 1, f"{sx}*0.40*wenkbrauw_boos", rig, ["wenkbrauw_boos"])
    keys = body.data.shape_keys
    for k in MOUTH_KEYS:
        kb = keys.key_blocks[k]
        _driver(kb, "value", None, k, rig, [k])


# ---------------------------------------------------------------------------
# Hoofdfunctie
# ---------------------------------------------------------------------------
class Character:
    def __init__(self, name, rig, body, J):
        self.name, self.rig, self.body, self.J = name, rig, body, J

    @property
    def pb(self):
        return self.rig.pose.bones


SHIRT_PARTS = ("romp", "bovenarm", "mouwzoom", "elleboog", "onderarm", "manchet", "jas", "labjas", "kraag")
PANTS_PARTS = ("been", "short", "rok", "broek")


def _outfit(parts, label, outfit):
    """Andere kleren voor figuranten: outfit = dict(shirt=kleur, broek=kleur, haar=kleur).
    Huid (de kleur van het hoofd) blijft altijd zoals hij is."""
    skin = parts["hoofd"].material_slots[0].material.name if "hoofd" in parts else None
    groups = (("shirt", SHIRT_PARTS), ("broek", PANTS_PARTS), ("haar", ("haar", "staart", "knot")))
    for key, prefixes in groups:
        col = outfit.get(key)
        if col is None:
            continue
        for pn, o in parts.items():
            if not pn.startswith(prefixes):
                continue
            for slot in o.material_slots:
                if slot.material and slot.material.name != skin:
                    slot.material = T.toon(f"pers_{label}_{key}", col)


def load(name, glb=None, loc=(0, 0, 0), rot_z=0.0, scale=1.0, outline=0.006, label=None, outfit=None, drop=()):
    """Laad een figuur en maak hem animeerbaar. name: 'hoofdpersonage' of een castnaam.
    label: eigen naam (om dezelfde castfiguur vaker te laden), outfit: andere kleren,
    drop: onderdelen weglaten (bijvoorbeeld rekwisieten als 'microfoon')."""
    glb = glb or (HERO_GLB if name == "hoofdpersonage" else cast_glb(name))
    name = label or name
    coll = bpy.data.collections.new("Figuur " + name)
    bpy.context.scene.collection.children.link(coll)
    parts = _import(glb, name)
    for pn in [p for p in parts if p.startswith(tuple(drop))]:
        bpy.data.objects.remove(parts.pop(pn), do_unlink=True)
    for o in parts.values():
        for uc in list(o.users_collection):
            uc.objects.unlink(o)
        coll.objects.link(o)
    _toon_materials(parts)
    if outfit:
        _outfit(parts, name, outfit)
    J = _joints(parts)
    # nieuwe mond
    mo = parts.pop("mond")
    to = parts.pop("tong", None)
    mat_in = mo.material_slots[0].material
    mat_t = to.material_slots[0].material if to else T.toon("tong", (0.85, 0.35, 0.35))
    bpy.data.objects.remove(mo, do_unlink=True)
    if to:
        bpy.data.objects.remove(to, do_unlink=True)
    mouth = _build_mouth(name, J, mat_in, mat_t, coll)

    rig = _build_armature(name, J, coll)
    _weights(rig, parts, J)
    mouth.vertex_groups.new(name="mouth").add([v.index for v in mouth.data.vertices], 1.0, "REPLACE")

    # alles samenvoegen tot één mesh; de mond eerst (actief), zodat de vormen blijven
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    objs = list(parts.values())
    for o in objs:
        o.select_set(True)
    mouth.select_set(True)
    bpy.context.view_layer.objects.active = mouth
    bpy.ops.object.join()
    body = mouth
    body.name = name + "_lichaam"
    body.data.name = name + "_lichaam"
    for p in body.data.polygons:
        p.use_smooth = True
    mod = body.modifiers.new("Skelet", "ARMATURE")
    mod.object = rig
    body.parent = rig
    T.outline(body, outline)
    _setup_ik(rig)
    _face_drivers(rig, body, J)
    rig.location = loc
    rig.rotation_euler = (0, 0, math.radians(rot_z))
    rig.scale = (scale, scale, scale)
    rig.show_in_front = True
    rig.hide_render = True
    return Character(name, rig, body, J)
