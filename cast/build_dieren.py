"""
Dieren voor video 3 "What IF There Were NO RULES?": het hondje (jong en oud, met
grijze snuit) en de zebra. Zelfde speelgoedstijl als de cast (glans-look), met een
eenvoudig skelet en kant-en-klare cycli, zodat de animatie echte poten laat lopen.

Gebruik:
    python cast/build_dieren.py --out pad/uitvoer [--no-render] [--samples 48]
Uitvoer: dieren.blend (alle dieren + acties), glb/<dier>.glb, renders/*.png

Elk dier is een armature "<dier>_rig" met de onderdelen eraan vast (botten-ouder,
dus niets vervormt of scheurt). Acties (met fake user, dus ze blijven bewaard):
    hondje: hond_loop (32 beelden), hond_draf (16), hond_kwispel (12), hond_snuffel (48)
    zebra:  zebra_loop (40), zebra_draf (24), zebra_schrik (24, zijsprong met kop omhoog)
Pas-lengte per cyclus staat als eigenschap op de rig ("pas_loop", "pas_draf"), zodat
de scène de rig precies zo snel kan laten voortbewegen als de poten lopen.
In een scène: anim/lib/dieren.py (D.load("hondje", ...), D.cycle(...)).
Kijkrichting: -y, zoals de figuren.
"""
import bpy
import bmesh
import math
import os
import sys
from mathutils import Vector, Matrix, Euler

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import render_glans as RG  # noqa: E402

lin = RG.lin


# ---------------------------------------------------------------------------
# Materialen
# ---------------------------------------------------------------------------
def pbr(name, hexcol, rough=0.45, metal=0.0):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*lin(hexcol), 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    m.diffuse_color = (*lin(hexcol), 1)
    return m


def unlit(name, hexcol):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    N = m.node_tree.nodes
    N.clear()
    e = N.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = (*lin(hexcol), 1)
    o = N.new("ShaderNodeOutputMaterial")
    m.node_tree.links.new(e.outputs[0], o.inputs[0])
    m.diffuse_color = (*lin(hexcol), 1)
    return m


def zebra_mat(name, axis="X", scale=7.0, distort=2.5):
    """Zwart-witte strepen, procedureel op de rustpositie (ze plakken op het dier)."""
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = pbr(name, "#F2EEE6", 0.4)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    co = RG._coord(nt)
    w = nt.nodes.new("ShaderNodeTexWave")
    w.wave_type = "BANDS"
    w.bands_direction = axis
    w.wave_profile = "SIN"
    w.inputs["Scale"].default_value = scale
    w.inputs["Distortion"].default_value = distort
    w.inputs["Detail"].default_value = 1.5
    w.inputs["Detail Scale"].default_value = 0.6
    nt.links.new(co, w.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.46
    ramp.color_ramp.elements[0].color = (*lin("#F2EEE6"), 1)
    ramp.color_ramp.elements[1].position = 0.54
    ramp.color_ramp.elements[1].color = (*lin("#17151A"), 1)
    nt.links.new(w.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Sheen Weight"].default_value = 0.4
    b.inputs["Coat Weight"].default_value = 0.2
    b.inputs["Coat Roughness"].default_value = 0.2
    m["glans2"] = True   # niet nog eens door glossify
    return m


# ---------------------------------------------------------------------------
# Vormen
# ---------------------------------------------------------------------------
class Kit:
    def __init__(self, name, coll):
        self.name = name
        self.coll = coll
        self.parts = []   # (obj, bone)

    def _ob(self, bm, label, mat, bone, smooth=True):
        me = bpy.data.meshes.new(f"{self.name}_{label}")
        bm.to_mesh(me)
        bm.free()
        for p in me.polygons:
            p.use_smooth = smooth
        me.materials.append(mat)
        ob = bpy.data.objects.new(f"{self.name}_{label}", me)
        self.coll.objects.link(ob)
        self.parts.append((ob, bone))
        return ob

    def blob(self, label, mat, c, s, bone, rot=(0, 0, 0), seg=32, rings=18, taper=None):
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, radius=1.0)
        if taper:
            for v in bm.verts:
                k = taper(v.co.y)
                v.co.x *= k
                v.co.z *= k
        M = Matrix.Translation(Vector(c)) @ Euler(rot).to_matrix().to_4x4() @ Matrix.Diagonal((*s, 1))
        bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
        return self._ob(bm, label, mat, bone)

    def limb(self, label, mat, a, b, r1, r2=None, bone=None, seg=20):
        """Afgeronde staaf van a naar b (capsule-achtig, met bolle uiteinden)."""
        a, b = Vector(a), Vector(b)
        r2 = r1 if r2 is None else r2
        d = b - a
        L = d.length
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=False, segments=seg, radius1=r1, radius2=r2, depth=L)
        for cap, r, z in ((0, r1, -L / 2), (1, r2, L / 2)):
            sp = bmesh.new()
            bmesh.ops.create_uvsphere(sp, u_segments=seg, v_segments=10, radius=r)
            bmesh.ops.translate(sp, verts=sp.verts, vec=(0, 0, z))
            tmp = bpy.data.meshes.new("tmp")
            sp.to_mesh(tmp)
            sp.free()
            bm.from_mesh(tmp)
            bpy.data.meshes.remove(tmp)
        q = d.to_track_quat("Z", "Y")
        M = Matrix.Translation((a + b) / 2) @ q.to_matrix().to_4x4()
        bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
        return self._ob(bm, label, mat, bone)

    def disc(self, label, mat, c, n, r, bone, sz=None, thick=0.003):
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=10, radius=1.0)
        q = Vector(n).normalized().to_track_quat("-Y", "Z")
        M = Matrix.Translation(Vector(c)) @ q.to_matrix().to_4x4() @ Matrix.Diagonal((r, thick, sz or r, 1))
        bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
        return self._ob(bm, label, mat, bone)

    def torus(self, label, mat, c, R, r, bone, normal=(0, 0, 1), seg=40):
        bm = bmesh.new()
        for i in range(seg):
            a = 2 * math.pi * i / seg
            for j in range(10):
                b = 2 * math.pi * j / 10
                bm.verts.new(((R + r * math.cos(b)) * math.cos(a), (R + r * math.cos(b)) * math.sin(a),
                              r * math.sin(b)))
        bm.verts.ensure_lookup_table()
        for i in range(seg):
            for j in range(10):
                i2, j2 = (i + 1) % seg, (j + 1) % 10
                bm.faces.new([bm.verts[i * 10 + j], bm.verts[i2 * 10 + j], bm.verts[i2 * 10 + j2],
                              bm.verts[i * 10 + j2]])
        q = Vector(normal).normalized().to_track_quat("Z", "Y")
        bmesh.ops.transform(bm, matrix=Matrix.Translation(Vector(c)) @ q.to_matrix().to_4x4(), verts=bm.verts)
        return self._ob(bm, label, mat, bone)

    def eyes(self, c_left, n_left, r, bone, iris="#3A2313"):
        """Ogen in de stijl van de cast: wit, iris, pupil en twee glansjes (onbelicht)."""
        W, I, P, G = unlit("dier_oogwit", "#FBF8F2"), unlit(f"dier_iris_{iris}", iris), \
            unlit("dier_pupil", "#120C0A"), unlit("dier_glans", "#FFFFFF")
        for side in (+1, -1):
            c = Vector((c_left[0] * side, c_left[1], c_left[2]))
            n = Vector((n_left[0] * side, n_left[1], n_left[2])).normalized()
            s = "L" if side > 0 else "R"
            self.disc(f"oog_{s}_wit", W, c, n, r, bone, thick=r * 0.35)
            self.disc(f"oog_{s}_iris", I, c + n * r * 0.3, n, r * 0.7, bone, thick=r * 0.12)
            self.disc(f"oog_{s}_pupil", P, c + n * r * 0.4, n, r * 0.4, bone, thick=r * 0.1)
            up = Vector((0, 0, 1))
            side_v = n.cross(up).normalized()
            self.disc(f"oog_{s}_glans", G, c + n * r * 0.5 + up * r * 0.32 + side_v * r * 0.25, n,
                      r * 0.2, bone, thick=r * 0.06)
            self.disc(f"oog_{s}_glans2", G, c + n * r * 0.5 - up * r * 0.28 - side_v * r * 0.25, n,
                      r * 0.09, bone, thick=r * 0.04)


# ---------------------------------------------------------------------------
# Skelet
# ---------------------------------------------------------------------------
def make_rig(name, coll, bones):
    """bones: lijst (naam, kop, staart, ouder)."""
    arm = bpy.data.armatures.new(name + "_rig")
    rig = bpy.data.objects.new(name + "_rig", arm)
    coll.objects.link(rig)
    bpy.context.view_layer.objects.active = rig
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    rig.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    eb = arm.edit_bones
    for bn, h, t, par in bones:
        b = eb.new(bn)
        b.head, b.tail = Vector(h), Vector(t)
        b.roll = 0.0
        if par:
            b.parent = eb[par]
            b.use_connect = False
    bpy.ops.object.mode_set(mode="OBJECT")
    arm.display_type = "STICK"
    return rig


def attach(rig, parts):
    bpy.context.view_layer.update()
    for ob, bone in parts:
        mw = ob.matrix_world.copy()
        ob.parent = rig
        ob.parent_type = "BONE"
        ob.parent_bone = bone
        bpy.context.view_layer.update()
        ob.matrix_world = mw


# ---------------------------------------------------------------------------
# Het hondje
# ---------------------------------------------------------------------------
def build_hond(coll, key="hondje", oud=False):
    K = Kit(key, coll)
    fur = pbr(f"{key}_vacht_C98A4B", "#C98A4B", 0.5)
    wit = pbr(f"{key}_vacht_F4EBDD", "#F4EBDD", 0.5)
    snuit = pbr(f"{key}_vacht_B8B2AA", "#B8B2AA", 0.5) if oud else wit
    neus = pbr(f"{key}_neus", "#1A1416", 0.25)
    oor = pbr(f"{key}_vacht_8A5A2E", "#8A5A2E", 0.5)
    halsband = pbr(f"{key}_leer_D8352B", "#D8352B", 0.35)
    goud = pbr(f"{key}_goud", "#E2B84B", 0.25, 1.0)
    tong = pbr(f"{key}_tong", "#E8727A", 0.35)

    H = 0.24     # hoogte van de rug
    # romp en borst
    K.blob("romp", fur, (0, 0.02, H), (0.13, 0.22, 0.12), "romp")
    K.blob("borst", wit, (0, -0.13, H - 0.01), (0.1, 0.07, 0.1), "romp")
    # nek en kop (groot, zoals de chibi-figuren)
    K.limb("nek", fur, (0, -0.14, H + 0.04), (0, -0.19, H + 0.13), 0.075, 0.07, "nek")
    hc = Vector((0, -0.22, H + 0.2))
    K.blob("kop", fur, hc, (0.135, 0.13, 0.125), "kop")
    K.blob("snuit", snuit, hc + Vector((0, -0.12, -0.04)), (0.075, 0.07, 0.055), "kop")
    K.blob("neus", neus, hc + Vector((0, -0.19, -0.015)), (0.03, 0.022, 0.022), "kop")
    K.blob("tong", tong, hc + Vector((0, -0.165, -0.085)), (0.028, 0.02, 0.012), "kop",
           rot=(math.radians(-20), 0, 0))
    K.blob("bles", wit, hc + Vector((0, -0.085, 0.085)), (0.028, 0.045, 0.022), "kop",
           rot=(math.radians(40), 0, 0))
    if oud:
        for s in (+1, -1):
            K.blob(f"wenkbrauw_{'L' if s > 0 else 'R'}", snuit,
                   hc + Vector((0.045 * s, -0.115, 0.06)), (0.025, 0.012, 0.01), "kop")
    K.eyes((0.06, hc.y - 0.112, hc.z + 0.032), (0.45, -0.87, 0.2), 0.024, "kop")
    # flaporen
    for s in (+1, -1):
        sd = "L" if s > 0 else "R"
        K.blob(f"oor_{sd}", oor, hc + Vector((0.115 * s, 0.01, 0.02)), (0.035, 0.06, 0.085),
               f"oor.{sd}", rot=(math.radians(10), math.radians(-25 * s), 0))
    # halsband met penning
    K.torus("halsband", halsband, (0, -0.165, H + 0.085), 0.072, 0.014, "nek", normal=(0, -0.55, 1))
    K.blob("penning", goud, (0, -0.235, H + 0.035), (0.018, 0.006, 0.022), "nek")
    K.blob("lijnring", goud, (0, -0.125, H + 0.13), (0.012, 0.004, 0.012), "nek")
    # poten: boven- en onderbeen + voetje
    legs = {"vl": (0.065, -0.12), "vr": (-0.065, -0.12), "al": (0.07, 0.14), "ar": (-0.07, 0.14)}
    for k, (x, y) in legs.items():
        top = Vector((x, y, H - 0.04))
        knee = Vector((x, y + (0.01 if k[0] == "v" else 0.025), 0.11))
        foot = Vector((x, y - 0.01, 0.03))
        K.limb(f"poot_{k}_boven", fur, top, knee, 0.042, 0.032, f"poot_{k}_boven")
        K.limb(f"poot_{k}_onder", fur if k[0] == "a" else wit, knee, foot, 0.03, 0.028,
               f"poot_{k}_onder")
        K.blob(f"voet_{k}", wit, foot + Vector((0, -0.018, -0.006)), (0.036, 0.046, 0.026),
               f"poot_{k}_onder")
    # staart (twee delen, krul omhoog)
    K.limb("staart1", fur, (0, 0.2, H + 0.04), (0, 0.27, H + 0.12), 0.026, 0.022, "staart1")
    K.limb("staart2", fur, (0, 0.27, H + 0.12), (0, 0.27, H + 0.21), 0.022, 0.014, "staart2")
    K.blob("staartpunt", wit, (0, 0.27, H + 0.215), (0.02, 0.02, 0.025), "staart2")

    bones = [("root", (0, 0, 0), (0, 0.15, 0), None),
             ("romp", (0, 0.12, H), (0, -0.12, H), "root"),
             ("nek", (0, -0.14, H + 0.04), (0, -0.19, H + 0.13), "romp"),
             ("kop", (0, -0.19, H + 0.13), (0, -0.19, H + 0.3), "nek"),
             ("oor.L", (0.1, -0.21, H + 0.27), (0.12, -0.21, H + 0.16), "kop"),
             ("oor.R", (-0.1, -0.21, H + 0.27), (-0.12, -0.21, H + 0.16), "kop"),
             ("staart1", (0, 0.2, H + 0.04), (0, 0.27, H + 0.12), "romp"),
             ("staart2", (0, 0.27, H + 0.12), (0, 0.27, H + 0.21), "staart1")]
    for k, (x, y) in legs.items():
        knee_y = y + (0.01 if k[0] == "v" else 0.025)
        bones.append((f"poot_{k}_boven", (x, y, H - 0.04), (x, knee_y, 0.11), "romp"))
        bones.append((f"poot_{k}_onder", (x, knee_y, 0.11), (x, y - 0.01, 0.03), f"poot_{k}_boven"))
    rig = make_rig(key, coll, bones)
    attach(rig, K.parts)
    rig["pas_loop"] = 0.26   # meter per loopcyclus
    rig["pas_draf"] = 0.42
    rig["dier"] = "hond"
    return rig


# ---------------------------------------------------------------------------
# De zebra
# ---------------------------------------------------------------------------
def build_zebra(coll, key="zebra"):
    K = Kit(key, coll)
    lijf = zebra_mat("zebra_streep_lijf", "X", 6.5, 2.2)
    nek = zebra_mat("zebra_streep_nek", "Z", 9.0, 1.5)
    poot = zebra_mat("zebra_streep_poot", "Z", 14.0, 0.8)
    zwart = pbr("zebra_vacht_17151A", "#17151A", 0.4)
    snuit = pbr("zebra_vacht_5A5458", "#5A5458", 0.4)
    hoef = pbr("zebra_hoef", "#2A2420", 0.3)
    roze = pbr("zebra_oor_binnen", "#C9A79E", 0.5)

    H = 1.05   # rughoogte
    K.blob("romp", lijf, (0, 0.05, H), (0.28, 0.62, 0.32), "romp")
    # nek schuin omhoog, kop iets groter dan echt (speelgoedstijl)
    K.limb("nek", nek, (0, -0.42, H + 0.12), (0, -0.62, H + 0.55), 0.2, 0.15, "nek")
    hc = Vector((0, -0.72, H + 0.68))
    K.blob("kop", nek, hc, (0.17, 0.22, 0.19), "kop")
    K.blob("snuit", snuit, hc + Vector((0, -0.26, -0.1)), (0.12, 0.15, 0.11), "kop",
           rot=(math.radians(-15), 0, 0))
    K.blob("snuitpunt", zwart, hc + Vector((0, -0.37, -0.13)), (0.1, 0.05, 0.075), "kop",
           rot=(math.radians(-15), 0, 0))
    for s in (+1, -1):
        sd = "L" if s > 0 else "R"
        K.blob(f"neusgat_{sd}", zwart, hc + Vector((0.055 * s, -0.395, -0.09)), (0.022, 0.01, 0.016), "kop")
        K.blob(f"oor_{sd}", nek, hc + Vector((0.1 * s, 0.06, 0.2)), (0.05, 0.03, 0.12), f"oor.{sd}",
               rot=(0, math.radians(-18 * s), 0))
        K.blob(f"oor_{sd}_binnen", roze, hc + Vector((0.1 * s, 0.035, 0.205)), (0.032, 0.012, 0.085),
               f"oor.{sd}", rot=(0, math.radians(-18 * s), 0))
    K.eyes((0.14, hc.y - 0.06, hc.z + 0.04), (0.8, -0.6, 0.1), 0.04, "kop")
    # manen: rij plukjes over de nek (zwart-wit)
    for i in range(9):
        t = i / 8
        p = Vector((0, -0.42, H + 0.12)).lerp(Vector((0, -0.66, H + 0.78)), t)
        p += Vector((0, 0.13, 0.12)) * (1 - 0.3 * t)
        K.blob(f"manen{i}", zwart if i % 2 else pbr("zebra_vacht_F2EEE6", "#F2EEE6", 0.45),
               p, (0.03, 0.06, 0.09), "nek" if t < 0.85 else "kop", rot=(math.radians(-35), 0, 0))
    # poten met hoeven
    legs = {"vl": (0.15, -0.42), "vr": (-0.15, -0.42), "al": (0.16, 0.48), "ar": (-0.16, 0.48)}
    for k, (x, y) in legs.items():
        top = Vector((x, y, H - 0.12))
        knee = Vector((x, y + (-0.02 if k[0] == "v" else 0.06), 0.46))
        foot = Vector((x, y, 0.09))
        K.limb(f"poot_{k}_boven", lijf if k[0] == "a" else poot, top, knee, 0.1, 0.065, f"poot_{k}_boven")
        K.limb(f"poot_{k}_onder", poot, knee, foot, 0.055, 0.05, f"poot_{k}_onder")
        K.blob(f"hoef_{k}", hoef, (x, y - 0.01, 0.05), (0.065, 0.075, 0.055), f"poot_{k}_onder")
    # staart met pluim
    K.limb("staart1", lijf, (0, 0.62, H + 0.08), (0, 0.72, H - 0.25), 0.04, 0.03, "staart1")
    K.limb("staart2", zwart, (0, 0.72, H - 0.25), (0, 0.74, H - 0.5), 0.03, 0.06, "staart2")

    bones = [("root", (0, 0, 0), (0, 0.4, 0), None),
             ("romp", (0, 0.5, H), (0, -0.45, H), "root"),
             ("nek", (0, -0.42, H + 0.12), (0, -0.64, H + 0.6), "romp"),
             ("kop", (0, -0.64, H + 0.6), (0, -1.0, H + 0.55), "nek"),
             ("oor.L", (0.1, -0.66, H + 0.8), (0.12, -0.66, H + 1.0), "kop"),
             ("oor.R", (-0.1, -0.66, H + 0.8), (-0.12, -0.66, H + 1.0), "kop"),
             ("staart1", (0, 0.62, H + 0.08), (0, 0.72, H - 0.25), "romp"),
             ("staart2", (0, 0.72, H - 0.25), (0, 0.74, H - 0.5), "staart1")]
    for k, (x, y) in legs.items():
        ky = y + (-0.02 if k[0] == "v" else 0.06)
        bones.append((f"poot_{k}_boven", (x, y, H - 0.12), (x, ky, 0.46), "romp"))
        bones.append((f"poot_{k}_onder", (x, ky, 0.46), (x, y, 0.09), f"poot_{k}_boven"))
    rig = make_rig(key, coll, bones)
    attach(rig, K.parts)
    rig["pas_loop"] = 1.1
    rig["pas_draf"] = 1.9
    rig["dier"] = "zebra"
    return rig


# ---------------------------------------------------------------------------
# Cycli
# ---------------------------------------------------------------------------
def _key(pb, frame, rot=None, loc=None):
    if rot is not None:
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = Euler([math.radians(a) for a in rot])
        pb.keyframe_insert("rotation_euler", frame=frame)
    if loc is not None:
        pb.location = Vector(loc)
        pb.keyframe_insert("location", frame=frame)


def make_cycle(rig, name, n, phases, swing, knee, bob, head, tail, extra=None):
    """Loopcyclus van n beelden. phases: fase per poot (0-1). swing/knee in graden.
    De poten zwaaien om de x-as (naar voren = negatieve hoek, want ze kijken naar -y)."""
    act = bpy.data.actions.new(name)
    act.use_fake_user = True
    rig.animation_data_create()
    rig.animation_data.action = act
    pbs = rig.pose.bones
    steps = 8
    for i in range(steps + 1):
        t = i / steps
        f = 1 + t * n
        for leg, ph in phases.items():
            a = 2 * math.pi * (t + ph)
            up = pbs[f"poot_{leg}_boven"]
            lo = pbs[f"poot_{leg}_onder"]
            # bovenbeen zwaait; onderbeen buigt alleen in de zwaaifase (poot vooruit)
            _key(up, f, rot=(swing * math.sin(a), 0, 0))
            lift = max(0.0, math.cos(a))   # zwaaifase
            k = knee * lift if leg[0] == "v" else -knee * lift
            _key(lo, f, rot=(k, 0, 0))
        b = math.cos(4 * math.pi * t)
        _key(pbs["romp"], f, loc=(0, 0, bob * b), rot=(0, 0, 0))
        _key(pbs["kop"], f, rot=(head * math.cos(4 * math.pi * t + 0.6), 0, 0))
        _key(pbs["nek"], f, rot=(head * 0.5 * math.cos(4 * math.pi * t), 0, 0))
        _key(pbs["staart1"], f, rot=(0, tail * math.sin(2 * math.pi * t), 0))
        _key(pbs["staart2"], f, rot=(0, tail * 1.2 * math.sin(2 * math.pi * t - 0.8), 0))
        for e in ("oor.L", "oor.R"):
            _key(pbs[e], f, rot=(0, 0, 6 * math.sin(4 * math.pi * t)))
        if extra:
            extra(pbs, t, f)
    for fc in act.fcurves if hasattr(act, "fcurves") else _fcurves(act):
        mod = fc.modifiers.new("CYCLES")
    rig.animation_data.action = None
    return act


def _fcurves(act):
    out = []
    for layer in getattr(act, "layers", []):
        for strip in layer.strips:
            for bag in strip.channelbags:
                out.extend(bag.fcurves)
    return out


def make_pose_action(rig, name, n, fn):
    act = bpy.data.actions.new(name)
    act.use_fake_user = True
    rig.animation_data_create()
    rig.animation_data.action = act
    pbs = rig.pose.bones
    steps = 12
    for i in range(steps + 1):
        t = i / steps
        fn(pbs, t, 1 + t * n)
    rig.animation_data.action = None
    return act


def reset_pose(rig):
    for pb in rig.pose.bones:
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = (0, 0, 0)
        pb.location = (0, 0, 0)


def hond_acties(rig):
    walk = dict(al=0.0, vl=0.25, ar=0.5, vr=0.75)
    trot = dict(vl=0.0, ar=0.0, vr=0.5, al=0.5)
    make_cycle(rig, "hond_loop", 32, walk, 24, 38, 0.006, 4, 22)
    make_cycle(rig, "hond_draf", 16, trot, 32, 50, 0.012, 6, 30)

    def kwispel(pbs, t, f):
        a = 2 * math.pi * t
        _key(pbs["staart1"], f, rot=(-15, 0, 45 * math.sin(2 * a)))
        _key(pbs["staart2"], f, rot=(0, 0, 50 * math.sin(2 * a - 0.9)))
        _key(pbs["romp"], f, rot=(0, 0, 4 * math.sin(2 * a)))
        _key(pbs["kop"], f, rot=(0, 0, -5 * math.sin(2 * a)))
    make_pose_action(rig, "hond_kwispel", 12, kwispel)

    def snuffel(pbs, t, f):
        d = math.sin(math.pi * min(1, t * 1.6)) if t < 0.62 else 0.0
        down = 0.5 - 0.5 * math.cos(2 * math.pi * t)
        _key(pbs["nek"], f, rot=(38 * down, 0, 0))
        _key(pbs["kop"], f, rot=(22 * down + 4 * math.sin(14 * math.pi * t) * down, 0,
                                 8 * math.sin(4 * math.pi * t) * down))
        _key(pbs["staart1"], f, rot=(0, 0, 25 * math.sin(6 * math.pi * t)))
        _ = d
    make_pose_action(rig, "hond_snuffel", 48, snuffel)


def zebra_acties(rig):
    walk = dict(al=0.0, vl=0.25, ar=0.5, vr=0.75)
    trot = dict(vl=0.0, ar=0.0, vr=0.5, al=0.5)
    make_cycle(rig, "zebra_loop", 40, walk, 20, 40, 0.02, 3, 12)
    make_cycle(rig, "zebra_draf", 24, trot, 28, 60, 0.05, 5, 18)

    def schrik(pbs, t, f):
        # anticipatie (zakt even), kop omhoog, zijsprong
        e = math.sin(math.pi * t)
        ant = -math.sin(math.pi * min(1, t / 0.25)) if t < 0.25 else 0.0
        _key(pbs["root"], f, loc=(0.6 * (0.5 - 0.5 * math.cos(math.pi * t)), 0, 0.08 * ant + 0.22 * max(0, e)))
        _key(pbs["romp"], f, rot=(0, -10 * e, 0))
        _key(pbs["nek"], f, rot=(-30 * e, 0, 12 * e))
        _key(pbs["kop"], f, rot=(-15 * e, 0, 0))
        for leg in ("vl", "vr"):
            _key(pbs[f"poot_{leg}_boven"], f, rot=(-35 * e, 0, 0))
            _key(pbs[f"poot_{leg}_onder"], f, rot=(70 * e, 0, 0))
        for leg in ("al", "ar"):
            _key(pbs[f"poot_{leg}_boven"], f, rot=(15 * e, 0, 0))
            _key(pbs[f"poot_{leg}_onder"], f, rot=(-20 * e, 0, 0))
        _key(pbs["staart1"], f, rot=(-40 * e, 0, 0))
        for o in ("oor.L", "oor.R"):
            _key(pbs[o], f, rot=(-20 * e, 0, 0))
    make_pose_action(rig, "zebra_schrik", 24, schrik)


# ---------------------------------------------------------------------------
def export_glb(objs, path):
    bpy.ops.object.select_all(action="DESELECT")
    for ob in objs:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", use_selection=True,
                              export_apply=False, export_yup=True, export_animations=True,
                              export_animation_mode="ACTIONS")


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    opts = {"--out": os.path.join(HERE, "output_dieren"), "--samples": "48"}
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
    os.makedirs(os.path.join(out, "glb"), exist_ok=True)
    os.makedirs(os.path.join(out, "renders"), exist_ok=True)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.fps = 30
    root = bpy.data.collections.new("dieren")
    sc.collection.children.link(root)
    rigs = {}
    for key, fn in (("hondje", lambda c: build_hond(c, "hondje")),
                    ("hondje_oud", lambda c: build_hond(c, "hondje_oud", oud=True)),
                    ("zebra", build_zebra)):
        c = bpy.data.collections.new(key)
        root.children.link(c)
        rigs[key] = fn(c)
    hond_acties(rigs["hondje"])
    hond_acties(rigs["hondje_oud"]) if False else None   # zelfde botten: deel de acties van hondje
    zebra_acties(rigs["zebra"])
    for r in rigs.values():
        reset_pose(r)
    rigs["hondje_oud"].location.x = 0.7
    rigs["zebra"].location.x = 2.4

    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, "dieren.blend"))
    print("opgeslagen:", os.path.join(out, "dieren.blend"))
    for key, r in rigs.items():
        loc = r.location.copy()
        r.location = (0, 0, 0)
        export_glb([r] + list(r.children), os.path.join(out, "glb", key + ".glb"))
        r.location = loc

    if "--no-render" in flags:
        return
    if sc.world is None:
        sc.world = bpy.data.worlds.new("World")
    studio = RG.setup_look(int(opts["--samples"]), 100)
    if studio.name not in sc.collection.children:
        sc.collection.children.link(studio)
    cam_d = bpy.data.cameras.new("cam")
    cam = bpy.data.objects.new("cam", cam_d)
    sc.collection.objects.link(cam)
    sc.camera = cam
    for ob in studio.objects:
        if ob.type == "LIGHT":
            ob.location.x += 1.2
    # stilstaand + midden in de draf
    RG.aim(cam, (2.4, -7.0, 1.7), (1.3, 0, 0.9), lens=40)
    RG.render(os.path.join(out, "renders", "00_dieren_overzicht.png"), 1800, 1000)
    for key, act in (("hondje", "hond_draf"), ("zebra", "zebra_draf")):
        r = rigs[key]
        r.animation_data_create()
        r.animation_data.action = bpy.data.actions[act]
        sc.frame_set(5)
    sc.frame_set(5)
    RG.render(os.path.join(out, "renders", "01_dieren_draf.png"), 1800, 1000)
    rigs["zebra"].animation_data.action = None
    rigs["hondje"].animation_data.action = None
    reset_pose(rigs["zebra"])
    reset_pose(rigs["hondje"])
    for key, (cl, tg) in (("hondje", ((0.35, -1.1, 0.5), (0, -0.15, 0.38))),
                          ("hondje_oud", ((1.05, -1.1, 0.5), (0.7, -0.15, 0.38))),
                          ("zebra", ((3.4, -3.0, 1.7), (2.4, -0.4, 1.3)))):
        RG.aim(cam, cl, tg, lens=50)
        RG.render(os.path.join(out, "renders", f"02_{key}_close-up.png"), 1200, 1200)


if __name__ == "__main__":
    main()
