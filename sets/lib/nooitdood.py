"""Props en decor voor video 4 "What IF You Could Never Die?".

Alles in de glans-look (via toon.py). Wat de animatie moet kunnen bewegen of schakelen heeft
een eigen object of materiaal met een duidelijke naam:

Zakhorloge (opa's gouden horloge), nulpunt = midden van de kast, wijzerplaat kijkt naar +Z,
de kroon zit op 12 uur (+Y), het scharnier van de klep op 9 uur (-X):
- `<naam>_klep`            rotation_euler.y: 0 = dicht, -2.8 (ongeveer -160 graden) = open
- `<naam>_kroon`           rotation_euler.y draaien = opwinden (scène 21a)
- `<naam>_wijzer_uur/_min/_sec`  rotation_euler.z (negatief = met de klok mee); 0 = 12 uur
- `<naam>_ketting`         hangt vanaf het oog langs -Z; draaien om het oog
- `<naam>_barst`           gebarsten glas (19c, verborgen; hide_render keyframen)
- `<naam>_rijp`            rijp op het glas (15d, verborgen)
- materiaal `<naam>_lume`     lichtgevende wijzers, Emission Strength 0 (uit) .. 4 (21a-21i)
- materiaal `<naam>_gravure`  de gravure in de klep, Emission Strength 0 .. 3 (22c2: licht op)

Sterrenveld (ruimte): één object met duizenden sterren. Elke ster heeft een eigen uit-moment
(attribuut `uit`, 0..1). Waarde `Sterren_uit` in het materiaal (node "Sterren uit") van 0 naar 1
keyframen = de sterren gaan één voor één uit, in willekeurige volgorde.
"""
import math
import random

import bpy
import bmesh
from mathutils import Vector, Euler, Matrix

from . import toon as T
from . import stad as S


def _m(name, col):
    return T.toon(name, col)


def pbr(name, base, rough=0.4, metal=0.0, emit=(1, 1, 1), strength=0.0, alpha=1.0, coat=0.0):
    """Eigen Principled-materiaal met een te keyframen Emission Strength (lume, gravure, gloed)."""
    mt = bpy.data.materials.get(name)
    if mt:
        return mt
    mt = bpy.data.materials.new(name)
    mt.use_nodes = True
    b = mt.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*base, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    b.inputs["Emission Color"].default_value = (*emit, 1)
    b.inputs["Emission Strength"].default_value = strength
    b.inputs["Coat Weight"].default_value = coat
    if alpha < 1:
        b.inputs["Alpha"].default_value = alpha
        mt.surface_render_method = "BLENDED"
    mt.diffuse_color = (*base, 1)
    mt["glans"] = True
    return mt


def _hide(o, hidden=True):
    o.hide_render = hidden
    o.hide_viewport = hidden


def _parent_keep(o, par):
    mw = o.matrix_world.copy()
    o.parent = par
    o.matrix_parent_inverse = par.matrix_world.inverted()
    o.matrix_world = mw


# ---------------------------------------------------------------------------
# Opa's gouden zakhorloge
# ---------------------------------------------------------------------------
GRAVURE = ("TIME IS THE", "ONE THING", "NOBODY GETS", "MORE OF.")


def zakhorloge(name="Zakhorloge", loc=(0, 0, 0), rot=(0, 0, 0), open_=0.0, tijd=(10, 10, 32),
               barst=False, rijp=False, lume=0.0, gravure_gloed=0.0, ketting=True, oud=False):
    """Gouden savonnette van 52 mm. open_ = 0 (dicht) .. 1 (helemaal open, ~160 graden).
    tijd = (uur, minuut, seconde) van de wijzers. oud=True: doffer goud (miljoenen jaren later)."""
    R = 0.026
    gold = _m("goud_horloge_oud" if oud else "goud_horloge", (0.62, 0.42, 0.16) if oud else (0.95, 0.66, 0.26))
    gold_d = _m("goud_horloge_donker", (0.55, 0.34, 0.10))
    root = S._empty(name, size=0.04)
    parts = []
    # kast: bolle achterkant, middenband en een rand
    parts.append(T.sphere(name + "_achterkant", (0, 0, -0.0022), R * 0.99, gold, scale=(1, 1, 0.22), seg=48, ol=0))  # top onder de wijzerplaat
    parts.append(T.cyl(name + "_band", (0, 0, -0.0035), R, 0.0074, gold, seg=64, ol=0, bevel=0.0012))  # dekseltje onder de wijzerplaat
    parts.append(T.torus(name + "_rand", (0, 0, 0.005), R * 0.97, 0.0016, gold, seg=64, seg2=10, ol=0))
    # geribbelde band (fijne groefjes)
    for k in range(48):
        a = 2 * math.pi * k / 48
        parts.append(T.box(f"{name}_groef{k}", (math.cos(a) * R * 1.003, math.sin(a) * R * 1.003, -0.0025),
                           (0.0007, 0.0007, 0.006), gold_d, rot=(0, 0, math.degrees(a)), bevel=0, ol=0))
    # pendant, kroon en beugel op 12 uur
    parts.append(T.cyl(name + "_pendant", (0, R * 0.96, 0.001), 0.0035, 0.006, gold, rot=(-90, 0, 0), seg=20, ol=0))
    kast = T.merge(name + "_kast", parts, ol=0)
    kast.parent = root
    kroon_parts = [T.cyl(name + "_kroon_k", (0, 0, 0), 0.0042, 0.0045, gold, rot=(-90, 0, 0), seg=24, ol=0)]
    for k in range(16):
        a = 2 * math.pi * k / 16
        kroon_parts.append(T.box(f"{name}_kroon_r{k}", (math.cos(a) * 0.0043, 0.00225, math.sin(a) * 0.0043),
                                 (0.0007, 0.0045, 0.0007), gold, rot=(0, -math.degrees(a), 0), bevel=0, ol=0, base=False))
    kroon = T.merge(name + "_kroon", kroon_parts, ol=0)
    kroon.location = (0, R * 0.96 + 0.006, 0.001)
    kroon.parent = root
    beugel = T.torus(name + "_beugel", (0, R + 0.0155, 0.001), 0.0065, 0.0011, gold, rot=(0, 90, 0), seg=32, seg2=8, ol=0)
    beugel.parent = root
    # wijzerplaat: crème email, minutenrand, cijfers en een klein secondenwijzertje in het midden
    dz = 0.0046
    email = _m("wijzerplaat_email", (0.93, 0.89, 0.78))
    zwart = _m("wijzerplaat_inkt", (0.05, 0.04, 0.035))
    dial = [T.cyl(name + "_plaat", (0, 0, dz - 0.0006), R * 0.9, 0.0006, email, seg=64, ol=0)]
    for k in range(60):
        a = math.pi / 2 - 2 * math.pi * k / 60
        L = 0.0022 if k % 5 == 0 else 0.0011
        w = 0.0006 if k % 5 == 0 else 0.0003
        rr = R * 0.86 - L / 2
        dial.append(T.box(f"{name}_streep{k}", (math.cos(a) * rr, math.sin(a) * rr, dz), (w, L, 0.0002), zwart,
                          rot=(0, 0, math.degrees(a) - 90), bevel=0, ol=0))
    dial.append(T.torus(name + "_minutenring", (0, 0, dz), R * 0.865, 0.00012, zwart, seg=64, seg2=4, ol=0))
    plaat = T.merge(name + "_wijzerplaat", dial, ol=0)
    plaat.parent = root
    cijfers = []
    for k in range(1, 13):
        a = math.pi / 2 - 2 * math.pi * k / 12
        rr = R * 0.66
        t = S.label(f"{name}_cijfer{k}", str(k), (math.cos(a) * rr, math.sin(a) * rr - 0.0019, dz), 0.0048,
                    (0.05, 0.04, 0.035), rot=(0, 0, 0), extrude=0.0001)
        cijfers.append(t)
    for t in cijfers:
        t.parent = root
    # wijzers (gebruind staal) met lume
    staal = _m("staal_gebruind", (0.08, 0.10, 0.22))
    lume_m = pbr(name + "_lume", (0.85, 0.85, 0.72), rough=0.5, emit=(0.75, 1.0, 0.55), strength=lume)
    h, mi, se = tijd

    def hand(tag, length, width, z, ang, lume_on=True):
        p = [T.box(f"{name}_{tag}_blad", (0, length / 2 - length * 0.12, 0), (width, length, 0.00035), staal, bevel=0,
                   ol=0, base=False),
             T.cyl(f"{name}_{tag}_as", (0, 0, -0.0002), width * 0.9, 0.0005, staal, seg=16, ol=0)]
        if lume_on:
            p.append(T.box(f"{name}_{tag}_lume", (0, length * 0.42, 0.00025), (width * 0.55, length * 0.5, 0.0002),
                           lume_m, bevel=0, ol=0, base=False))
        o = T.merge(f"{name}_wijzer_{tag}", p, ol=0)
        o.location = (0, 0, z)
        o.rotation_euler.z = -ang
        o.parent = root
        return o
    hand("uur", R * 0.52, 0.0016, dz + 0.0005, 2 * math.pi * ((h % 12) + mi / 60) / 12)
    hand("min", R * 0.76, 0.0012, dz + 0.0009, 2 * math.pi * (mi + se / 60) / 60)
    hand("sec", R * 0.82, 0.00045, dz + 0.0013, 2 * math.pi * se / 60, lume_on=False)
    T.cyl(name + "_dopje", (0, 0, dz + 0.0013), 0.0008, 0.0006, gold, seg=16, ol=0).parent = root
    # glas
    glas = T.sphere(name + "_glas", (0, 0, 0.0042), R * 0.9, T.glass("horlogeglas", (0.9, 0.95, 1.0), 0.12),
                    scale=(1, 1, 0.14), seg=48, ol=0)
    glas.parent = root
    # barsten in het glas (19c): lijntjes vanuit een inslagpunt
    rnd = random.Random(19)
    barst_m = pbr("horlogeglas_barst", (0.95, 0.97, 1.0), rough=0.2, emit=(1, 1, 1), strength=0.4)
    lines = []
    c0 = Vector((R * 0.25, R * 0.3, 0))
    for k in range(9):
        a = rnd.uniform(0, 2 * math.pi)
        p = c0.copy()
        pts = []
        for s_ in range(6):
            pts.append(p.copy())
            a += rnd.uniform(-0.5, 0.5)
            p = p + Vector((math.cos(a), math.sin(a), 0)) * R * rnd.uniform(0.1, 0.22)
            if p.length > R * 0.88:
                break
        pts3 = [(q.x, q.y, 0.0042 + R * 0.14 * math.sqrt(max(0, 1 - (q.length / (R * 0.9)) ** 2)) + 0.0001) for q in pts]
        if len(pts3) > 1:
            lines.append(T.to_mesh(T.tube(f"{name}_barstlijn{k}", pts3, 0.00012, barst_m)))
    barst_o = T.merge(name + "_barst", lines, ol=0)
    barst_o.parent = root
    _hide(barst_o, not barst)
    rijp_o = T.sphere(name + "_rijp", (0, 0, 0.0045), R * 0.9,
                      pbr("horloge_rijp", (0.92, 0.96, 1.0), rough=0.9, alpha=0.75), scale=(1, 1, 0.15), seg=48, ol=0)
    rijp_o.parent = root
    _hide(rijp_o, not rijp)
    # klep met scharnier op 9 uur en gravure aan de binnenkant
    klep = S._empty(name + "_klep", (-R, 0, 0.0085), size=0.01)
    klep.parent = root
    kp = [T.sphere(name + "_klep_bol", (R, 0, 0.0021), R * 0.99, gold, scale=(1, 1, 0.12), seg=48, ol=0),
          T.cyl(name + "_klep_rand", (R, 0, -0.0012), R * 1.0, 0.0018, gold, seg=64, ol=0, bevel=0.0006),
          T.cyl(name + "_scharnier", (0, -0.006, -0.0005), 0.0014, 0.012, gold, rot=(-90, 0, 0), seg=16, ol=0)]
    # sierringen op de buitenkant
    for k, rr in enumerate((0.55, 0.78)):
        kp.append(T.torus(f"{name}_klep_sier{k}", (R, 0, 0.0028 - 0.0012 * k), R * rr, 0.0003, gold_d, seg=64, seg2=6,
                          ol=0))
    kp.append(T.cyl(name + "_klep_schildje", (R, 0, 0.0028), R * 0.3, 0.0004, gold_d, seg=40, ol=0))
    klep_o = T.merge(name + "_klep_kap", kp, ol=0)
    klep_o.location = (0, 0, 0)
    gr_m = pbr(name + "_gravure", (0.45, 0.28, 0.08), rough=0.35, metal=1.0, emit=(1.0, 0.75, 0.35),
               strength=gravure_gloed)
    gtxt = []
    for k, line in enumerate(GRAVURE):
        t = S.label(f"{name}_gravure{k}", line, (0, 0, 0), 0.0036, (0.45, 0.28, 0.08), rot=(180, 0, 0),
                    extrude=0.00012)
        t.data.materials[0] = gr_m
        t.location = (R + (len(GRAVURE) / 2 - k - 0.5) * 0.0052 * 0 + 0.0, (len(GRAVURE) / 2 - k - 0.65) * 0.0052,
                      -0.0024)
        t.rotation_euler = Euler((math.pi, 0, -math.pi / 2))
        gtxt.append(t)
    # binnenkant gepolijst, dunne rand om de tekst
    binnen = T.cyl(name + "_klep_binnen", (R, 0, -0.00125), R * 0.92, 0.0002, _m("goud_horloge_binnen", (0.98, 0.78, 0.4)),
                   seg=64, ol=0)
    for o in [klep_o, binnen] + gtxt:
        o.parent = klep
    # gravure-tekst loopt van het scharnier af; positie in klep-ruimte (x = langs de klep)
    for k, t in enumerate(gtxt):
        t.location = (R + 0.0, (len(GRAVURE) / 2 - k - 0.6) * -0.0054 * -1, -0.00132)
        t.rotation_euler = Euler((0, math.pi, 0))   # leesbaar (niet gespiegeld) als de klep open ligt
    klep.rotation_euler.y = -math.radians(160) * open_
    klep["open_dicht"] = 0.0
    klep["open_helemaal"] = -math.radians(160)
    # ketting met T-staafje
    if ketting:
        links = []
        top = Vector((0, R + 0.022, 0.001))
        n = 34
        for k in range(n):
            t = k / (n - 1)
            p = top + Vector((0.004 * math.sin(t * 3.0), 0.012 * t, -0.2 * t + 0.03 * math.sin(t * math.pi)))
            links.append(T.torus(f"{name}_schakel{k}", tuple(p), 0.0028, 0.0007, gold, seg=16, seg2=6, ol=0,
                                 rot=(0, 90 if k % 2 else 0, 0)))
        end = top + Vector((0.004 * math.sin(3.0), 0.012, -0.2))
        links.append(T.cyl(name + "_tstaaf", tuple(end + Vector((-0.012, 0, -0.003))), 0.0012, 0.024, gold,
                           rot=(0, 90, 0), seg=12, ol=0))
        k_o = T.merge(name + "_ketting", links, ol=0)
        # nulpunt op het oog, zodat de ketting om het oog kan draaien
        k_o.data.transform(Matrix.Translation(-top))
        k_o.location = top
        k_o.parent = root
    root.location = loc
    root.rotation_euler = Euler([math.radians(a) for a in rot])
    root["prop"] = "zakhorloge"
    return root


def horlogedoosje(name="Horlogedoosje", loc=(0, 0, 0), rot_z=0.0, open_=0.0):
    """Klein leren doosje (scène 5b-5c). Deksel `<naam>_deksel` scharniert achter (rotation_euler.x)."""
    root = S._empty(name, size=0.05)
    leer = _m("leer_doosje_bordeaux", (0.32, 0.05, 0.06))
    fluweel = _m("stof_fluweel_creme", (0.85, 0.80, 0.68))
    w, d, h = 0.085, 0.085, 0.03
    p = [T.box(name + "_bak", (0, 0, 0), (w, d, h), leer, bevel=0.004, ol=0),
         T.box(name + "_fluweel", (0, 0, h - 0.004), (w - 0.008, d - 0.008, 0.0042), fluweel, bevel=0.002, ol=0),
         T.box(name + "_kussentje", (0, 0, h - 0.002), (0.05, 0.05, 0.006), fluweel, bevel=0.003, ol=0)]
    bak = T.merge(name + "_onder", p, ol=0)
    bak.parent = root
    dek = S._empty(name + "_deksel", (0, d / 2, h), size=0.02)
    dek.parent = root
    dp = [T.box(name + "_deksel_kap", (0, -d / 2, 0), (w, d, 0.018), leer, bevel=0.005, ol=0),
          T.box(name + "_deksel_satijn", (0, -d / 2, -0.0004), (w - 0.008, d - 0.008, 0.001), fluweel, bevel=0, ol=0),
          T.box(name + "_slotje", (0, -d - 0.0005, -0.004), (0.012, 0.003, 0.008), _m("goud_slotje", (0.95, 0.7, 0.3)),
                bevel=0.001, ol=0)]
    kap = T.merge(name + "_deksel_mesh", dp, ol=0)
    kap.parent = dek
    dek.rotation_euler.x = -math.radians(105) * open_
    root.location = loc
    root.rotation_euler.z = math.radians(rot_z)
    return root


def politiepenning(name="Politiepenning", loc=(0, 0, 0), rot=(0, 0, 0), kras=True):
    """Oude politiepenning van de pestkop (12d3): schild met OFFICER en een kras erover. Plat, kijkt naar +Z."""
    root = S._empty(name, size=0.03)
    goud = _m("goud_penning", (0.85, 0.62, 0.25))
    pts = []
    for k in range(40):
        t = k / 40 * 2 * math.pi
        x = 0.03 * math.sin(t)
        y = 0.036 * math.cos(t) * (1.0 if math.cos(t) > 0 else 1.2) - 0.004
        pts.append((x, y))
    bm = bmesh.new()
    vs = [bm.verts.new((x, y, 0)) for x, y in pts]
    f = bm.faces.new(vs)
    ex = bmesh.ops.extrude_face_region(bm, geom=[f])
    for v in [e for e in ex["geom"] if isinstance(e, bmesh.types.BMVert)]:
        v.co.z += 0.003
    me = bpy.data.meshes.new(name + "_schild")
    bm.to_mesh(me)
    bm.free()
    sch = T._obj(name + "_schild", me, goud, (0, 0, 0), None, 0, bevel=0.0006)
    sch.parent = root
    ster = []
    for k in range(10):
        a = math.pi / 2 + k * math.pi / 5
        r = 0.011 if k % 2 == 0 else 0.0045
        ster.append((math.cos(a) * r, math.sin(a) * r + 0.006, 0.0032))
    st = T.mesh_from(name + "_ster", ster + [(0, 0.006, 0.0042)], [(i, (i + 1) % 10, 10) for i in range(10)],
                     _m("zilver_penning", (0.80, 0.82, 0.85)))
    st.parent = root
    t = S.label(name + "_OFFICER", "OFFICER", (0, -0.016, 0.0031), 0.0075, (0.12, 0.10, 0.08), rot=(0, 0, 0),
                extrude=0.0003)
    t.parent = root
    if kras:
        k = T.box(name + "_kras", (0.002, -0.004, 0.0033), (0.055, 0.0009, 0.0003),
                  _m("zilver_kras", (0.95, 0.95, 0.92)), rot=(0, 0, 28), bevel=0, ol=0, base=False)
        k.parent = root
    root.location = loc
    root.rotation_euler = Euler([math.radians(a) for a in rot])
    return root


def rolstoel(name="Rolstoel", loc=(0, 0, 0), rot_z=0.0):
    """Ouderwetse rolstoel (2110). Kijkt naar -Y; zitting op 0,48 m. Wielen `<naam>_wiel_L/_R`."""
    root = S._empty(name, size=0.3)
    chroom = _m("chroom_rolstoel", (0.75, 0.77, 0.80))
    zit = _m("stof_rolstoel", (0.12, 0.22, 0.38))
    zwart = _m("rubber_zwart", (0.04, 0.04, 0.045))
    p = [T.box(name + "_zitting", (0, 0, 0.44), (0.46, 0.44, 0.05), zit, bevel=0.015, ol=0),
         T.box(name + "_rug", (0, 0.22, 0.5), (0.46, 0.04, 0.42), zit, bevel=0.015, ol=0)]
    for sx in (-1, 1):
        p += [T.tube(f"{name}_frame{sx}", [(sx * 0.24, 0.24, 0.95), (sx * 0.24, 0.24, 0.44), (sx * 0.24, -0.2, 0.44),
                                           (sx * 0.24, -0.3, 0.12), (sx * 0.18, -0.36, 0.1)], 0.012, chroom),
              T.tube(f"{name}_handvat{sx}", [(sx * 0.24, 0.24, 0.95), (sx * 0.24, 0.36, 0.97)], 0.016, zwart),
              T.tube(f"{name}_armleuning{sx}", [(sx * 0.24, 0.2, 0.44), (sx * 0.24, 0.18, 0.66), (sx * 0.24, -0.16, 0.66),
                                                (sx * 0.24, -0.18, 0.44)], 0.011, chroom),
              T.box(f"{name}_voetsteun{sx}", (sx * 0.12, -0.38, 0.08), (0.16, 0.12, 0.015), zwart, bevel=0.004, ol=0),
              T.cyl(f"{name}_zwenkwiel{sx}", (sx * 0.2, -0.28, 0.06), 0.06, 0.03, zwart, rot=(0, 90, 0), seg=20, ol=0)]
    p = [T.to_mesh(o) if o.type == "CURVE" else o for o in p]
    frame = T.merge(name + "_frame", p, ol=0)
    frame.parent = root
    for sx, tag in ((-1, "R"), (1, "L")):
        w = [T.torus(f"{name}_band{tag}", (0, 0, 0), 0.29, 0.016, zwart, rot=(0, 90, 0), seg=48, seg2=10, ol=0),
             T.torus(f"{name}_hoepel{tag}", (sx * 0.025, 0, 0), 0.265, 0.007, chroom, rot=(0, 90, 0), seg=48, seg2=8, ol=0),
             T.cyl(f"{name}_naaf{tag}", (-0.02, 0, 0), 0.03, 0.04, chroom, rot=(0, 90, 0), seg=16, ol=0)]
        for k in range(12):
            a = k / 12 * 180
            w.append(T.box(f"{name}_spaak{tag}{k}", (0, 0, 0), (0.002, 0.002, 0.56), chroom, rot=(a, 0, 0), bevel=0, ol=0,
                           base=False))
        wo = T.merge(f"{name}_wiel_{tag}", w, ol=0)
        wo.location = (sx * 0.29, 0.06, 0.3)
        wo.parent = root
    root.location = loc
    root.rotation_euler.z = math.radians(rot_z)
    return root


def bloemen(name="Bloemen", loc=(0, 0, 0), rot_z=0.0, kleur=(0.95, 0.95, 0.92), seed=1, verwelkt=0.0):
    """Bosje bloemen met papier eromheen (bij de bank, voor wie er niet meer is)."""
    rnd = random.Random(seed)
    root = S._empty(name, size=0.1)
    steel = _m("blad_steel", (0.16, 0.42, 0.12))
    bl = _m(f"bloem_{'%.2f%.2f%.2f' % kleur}", kleur)
    hart = _m("bloem_hart", (0.95, 0.75, 0.15))
    p = [T.cyl(name + "_papier", (0, 0, 0.0), 0.03, 0.22, _m("papier_bloemen", (0.92, 0.88, 0.80)), r2=0.08, seg=12,
               ol=0)]
    for k in range(9):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0, 0.05)
        top = (math.cos(a) * r, math.sin(a) * r, 0.3 + rnd.uniform(-0.03, 0.04) - verwelkt * 0.08)
        p.append(T.to_mesh(T.tube(f"{name}_steel{k}", [(0, 0, 0.02), top], 0.003, steel)))
        p.append(T.sphere(f"{name}_kop{k}", top, 0.028, bl, scale=(1, 1, 0.55), seg=12, ol=0))
        p.append(T.sphere(f"{name}_hart{k}", (top[0], top[1], top[2] + 0.012), 0.009, hart, seg=8, ol=0))
    o = T.merge(name + "_bos", p, ol=0)
    o.parent = root
    root.location = loc
    root.rotation_euler = (math.radians(70), 0, math.radians(rot_z))  # ligt schuin op de grond
    root.location.z += 0.03
    return root


def snoepzak(name="Snoepzak", loc=(0, 0, 0), rot_z=0.0):
    root = S._empty(name, size=0.05)
    p = [T.box(name + "_zak", (0, 0, 0), (0.12, 0.07, 0.17), _m("papier_snoepzak", (0.85, 0.72, 0.52)), bevel=0.008, ol=0)]
    rnd = random.Random(3)
    for k in range(8):
        p.append(T.sphere(f"{name}_snoep{k}", (rnd.uniform(-0.04, 0.04), rnd.uniform(-0.02, 0.02), 0.17 + rnd.uniform(0, 0.02)),
                          0.012, _m(f"snoep{k % 4}", [(0.9, 0.1, 0.2), (0.1, 0.6, 0.9), (0.95, 0.8, 0.1), (0.3, 0.8, 0.2)][k % 4]),
                          seg=10, ol=0))
    o = T.merge(name + "_mesh", p, ol=0)
    o.parent = root
    root.location = loc
    root.rotation_euler.z = math.radians(rot_z)
    return root


def peperbakje(name="Peperbakje", loc=(0, 0, 0), rot_z=0.0):
    """Rood bakje met de heetste peper van de winkel en een doodshoofd-etiket (6d)."""
    root = S._empty(name, size=0.05)
    rood = _m("plastic_peperbakje", (0.75, 0.04, 0.04))
    p = [T.box(name + "_bak", (0, 0, 0), (0.12, 0.09, 0.04), rood, bevel=0.008, ol=0)]
    rnd = random.Random(6)
    for k in range(4):
        pts = [(rnd.uniform(-0.04, 0.04), rnd.uniform(-0.025, 0.025), 0.045)]
        a = rnd.uniform(0, 6.28)
        for s_ in range(4):
            q = pts[-1]
            pts.append((q[0] + math.cos(a) * 0.012, q[1] + math.sin(a) * 0.012, q[2] + 0.003 - s_ * 0.002))
            a += 0.3
        p.append(T.to_mesh(T.tube(f"{name}_peper{k}", pts, 0.008 - k * 0.0005, _m("peper_rood", (0.85, 0.05, 0.02)))))
        p.append(T.to_mesh(T.tube(f"{name}_steeltje{k}", [pts[0], (pts[0][0], pts[0][1] - 0.006, pts[0][2] + 0.008)], 0.0025,
                                  _m("blad_peper", (0.15, 0.45, 0.1)))))
    o = T.merge(name + "_mesh", p, ol=0)
    o.parent = root
    et = T.box(name + "_etiket", (0, -0.0455, 0.008), (0.07, 0.002, 0.026), _m("papier_etiket_zwart", (0.03, 0.03, 0.03)),
               bevel=0, ol=0)
    et.parent = root
    # doodshoofdje
    wit = _m("etiket_wit", (0.95, 0.95, 0.92))
    sk = [T.sphere(name + "_schedel", (-0.022, -0.047, 0.023), 0.006, wit, scale=(1, 0.3, 1), seg=12, ol=0),
          T.box(name + "_kaak", (-0.022, -0.047, 0.014), (0.006, 0.002, 0.004), wit, bevel=0, ol=0)]
    T.merge(name + "_doodshoofd", sk, ol=0).parent = root
    t = S.label(name + "_tekst", "HOT!", (0.01, -0.0475, 0.015), 0.009, (0.95, 0.2, 0.05), rot=(90, 0, 0), extrude=0.0005)
    t.parent = root
    root.location = loc
    root.rotation_euler.z = math.radians(rot_z)
    return root


def kwalletje(name="Kwalletje", loc=(0, 0, 0), scale=1.0, gloed=3.0):
    """Turritopsis-kwal: doorzichtig klokje met een rode maag en tentakels, gloeit zacht (materiaal `<naam>_gloed`)."""
    root = S._empty(name, size=0.02)
    gl = pbr(name + "_gloed", (0.85, 0.92, 1.0), rough=0.1, emit=(0.55, 0.85, 1.0), strength=gloed, alpha=0.55)
    maag = pbr(name + "_maag", (0.85, 0.15, 0.1), rough=0.3, emit=(1.0, 0.35, 0.2), strength=gloed * 0.6)
    p = [T.sphere(name + "_klok", (0, 0, 0), 0.01, gl, scale=(1, 1, 0.8), seg=24, ol=0),
         T.sphere(name + "_maag", (0, 0, -0.001), 0.0035, maag, scale=(1, 1, 1.3), seg=12, ol=0)]
    rnd = random.Random(11)
    for k in range(16):
        a = 2 * math.pi * k / 16
        pts = []
        for s_ in range(8):
            t = s_ / 7
            pts.append((math.cos(a) * (0.0095 + 0.002 * t), math.sin(a) * (0.0095 + 0.002 * t),
                        -0.002 - 0.018 * t + 0.002 * math.sin(t * 6 + k)))
        p.append(T.to_mesh(T.tube(f"{name}_tentakel{k}", pts, 0.0004, gl)))
    o = T.merge(name + "_lijf", p, ol=0)
    # klok open aan de onderkant: onderste helft van de bol weg
    bm = bmesh.new()
    bm.from_mesh(o.data)
    kill = [v for v in bm.verts if v.co.z < -0.0035 and Vector((v.co.x, v.co.y)).length > 0.007 and v.co.z > -0.0081]
    bmesh.ops.delete(bm, geom=kill, context="VERTS")
    bm.to_mesh(o.data)
    bm.free()
    o.parent = root
    root.location = loc
    root.scale = (scale,) * 3
    return root


def kwallenbak(name="Kwallenbak", loc=(0, 0, 0), rot_z=0.0):
    """Glazen bak met water en het gloeiende kwalletje (7c-7d2)."""
    root = S._empty(name, size=0.1)
    glas = T.glass("glas_bak", (0.85, 0.93, 1.0), 0.15)
    p = [T.box(name + "_glas", (0, 0, 0.02), (0.3, 0.2, 0.25), glas, bevel=0.006, ol=0),
         T.box(name + "_voet", (0, 0, 0), (0.32, 0.22, 0.02), _m("metaal_bak", (0.2, 0.22, 0.25)), bevel=0.004, ol=0),
         T.box(name + "_deksel", (0, 0, 0.27), (0.32, 0.22, 0.012), _m("metaal_bak", (0.2, 0.22, 0.25)), bevel=0.003, ol=0)]
    T.merge(name + "_bak", p, ol=0).parent = root
    w = T.box(name + "_water", (0, 0, 0.025), (0.29, 0.19, 0.22), pbr("water_kwallenbak", (0.55, 0.8, 0.95), rough=0.05,
                                                                       emit=(0.2, 0.5, 0.9), strength=0.08, alpha=0.08),
              bevel=0.004, ol=0)
    w.parent = root
    led = T.box(name + "_led", (0, 0, 0.0205), (0.26, 0.16, 0.002), pbr("led_kwallenbak", (0.3, 0.6, 1.0), emit=(0.3, 0.65, 1.0),
                                                                      strength=6.0), bevel=0, ol=0)
    led.parent = root
    k = kwalletje(name + "_kwal", (0, 0, 0.15), scale=2.2)
    k.parent = root
    root.location = loc
    root.rotation_euler.z = math.radians(rot_z)
    return root


def oude_foto(name="Gezinsfoto", loc=(0, 0, 0), rot=(0, 0, 0), image=None, vergeling=0.0, verbleking=0.0,
              kreuk=0.0, w=0.15, h=0.105):
    """Foto van de 14e verjaardag. vergeling 0..1 (2086: ~0.5), verbleking 0..1 (50.000 jaar: ~0.8, het gezicht
    van mama is bijna weg). Waarden staan in de nodes 'Vergeling' en 'Verbleking' (te keyframen)."""
    root = S._empty(name, size=0.05)
    me = bpy.data.meshes.new(name + "_vel")
    bm = bmesh.new()
    nx, ny = 24, 16
    vs = [[bm.verts.new(((i / nx - 0.5) * w, (j / ny - 0.5) * h, 0)) for i in range(nx + 1)] for j in range(ny + 1)]
    for j in range(ny):
        for i in range(nx):
            bm.faces.new((vs[j][i], vs[j][i + 1], vs[j + 1][i + 1], vs[j + 1][i]))
    rnd = random.Random(5)
    if kreuk:
        for v in bm.verts:
            v.co.z = kreuk * 0.004 * (math.sin(v.co.x * 90 + 1.3) * math.cos(v.co.y * 70) + rnd.uniform(-0.3, 0.3))
    uv = bm.loops.layers.uv.new("UVMap")
    for f in bm.faces:
        for lp in f.loops:
            lp[uv].uv = (lp.vert.co.x / w + 0.5, lp.vert.co.y / h + 0.5)
    bm.to_mesh(me)
    bm.free()
    mt = bpy.data.materials.new(name + "_foto")
    mt.use_nodes = True
    N, L = mt.node_tree.nodes, mt.node_tree.links
    b = N.get("Principled BSDF")
    b.inputs["Roughness"].default_value = 0.35
    b.inputs["Coat Weight"].default_value = 0.3 * (1 - vergeling)
    if image:
        tex = N.new("ShaderNodeTexImage")
        tex.image = bpy.data.images.load(image, check_existing=True)
        col = tex.outputs["Color"]
    else:
        rgb = N.new("ShaderNodeRGB")
        rgb.outputs[0].default_value = (0.6, 0.5, 0.4, 1)
        col = rgb.outputs[0]
    vg = N.new("ShaderNodeValue")
    vg.name = vg.label = "Vergeling"
    vg.outputs[0].default_value = vergeling
    vb = N.new("ShaderNodeValue")
    vb.name = vb.label = "Verbleking"
    vb.outputs[0].default_value = verbleking
    m1 = N.new("ShaderNodeMix")
    m1.data_type = "RGBA"
    m1.blend_type = "MULTIPLY"
    m1.inputs["B"].default_value = (1.0, 0.82, 0.52, 1)
    L.new(vg.outputs[0], m1.inputs["Factor"])
    L.new(col, m1.inputs["A"])
    # verbleken: vlekkerig naar papierkleur (ruis), zodat gezichten wegvallen
    nz = N.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 6.0
    mr = N.new("ShaderNodeMapRange")
    L.new(nz.outputs["Fac"], mr.inputs["Value"])
    mr.inputs["From Min"].default_value = 0.35
    mr.inputs["From Max"].default_value = 0.65
    mul = N.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    L.new(vb.outputs[0], mul.inputs[0])
    mul2 = N.new("ShaderNodeMath")
    mul2.operation = "ADD"
    L.new(mr.outputs["Result"], mul2.inputs[0])
    mul2.inputs[1].default_value = 0.6
    L.new(mul2.outputs[0], mul.inputs[1])
    cl = N.new("ShaderNodeClamp")
    L.new(mul.outputs[0], cl.inputs["Value"])
    m2 = N.new("ShaderNodeMix")
    m2.data_type = "RGBA"
    m2.inputs["B"].default_value = (0.85, 0.78, 0.62, 1)
    L.new(cl.outputs[0], m2.inputs["Factor"])
    L.new(m1.outputs["Result"], m2.inputs["A"])
    L.new(m2.outputs["Result"], b.inputs["Base Color"])
    mt["glans"] = True
    me.materials.append(mt)
    o = bpy.data.objects.new(name + "_vel", me)
    T._link(o)
    sol = o.modifiers.new("dikte", "SOLIDIFY")
    sol.thickness = 0.0006
    # witte rand achterkant
    back = T.box(name + "_achterkant", (0, 0, -0.0007), (w + 0.006, h + 0.006, 0.0004), _m("papier_foto_rand", (0.95, 0.93, 0.88)),
                 bevel=0, ol=0, base=False)
    for x in (o, back):
        x.parent = root
    root.location = loc
    root.rotation_euler = Euler([math.radians(a) for a in rot])
    return root


# ---------------------------------------------------------------------------
# De heuvel: eik, bank, stenen bank, bankvoet
# ---------------------------------------------------------------------------
def eik(name="Eik", loc=(0, 0, 0), seizoen="zomer", schaal=1.0, seed=7, sneeuw=False, klimop=False):
    """Grote eik met een echte kroon van takken. seizoen: zomer, herfst, winter (kaal), lente, groen, verkoold."""
    rnd = random.Random(seed)
    stam_m = _m("stam_eik_verkoold" if seizoen == "verkoold" else "stam_eik", (0.03, 0.025, 0.02) if seizoen == "verkoold"
                else (0.28, 0.19, 0.12))
    loof = {"zomer": [(0.14, 0.38, 0.10), (0.20, 0.46, 0.12)],
            "herfst": [(0.80, 0.34, 0.06), (0.92, 0.58, 0.10), (0.62, 0.22, 0.06)],
            "lente": [(0.34, 0.66, 0.16), (0.48, 0.74, 0.22)],
            "groen": [(0.10, 0.44, 0.12), (0.16, 0.52, 0.10)]}.get(seizoen)
    parts = []
    H = 5.2
    # stam met wortelvoet
    parts.append(T.cyl(name + "_stam", (0, 0, -0.3), 0.62, 3.3, stam_m, r2=0.42, seg=18, ol=0))
    for k in range(6):
        a = 2 * math.pi * k / 6 + rnd.uniform(-0.2, 0.2)
        parts.append(T.to_mesh(T.tube(f"{name}_wortel{k}", [(0, 0, 0.5), (math.cos(a) * 0.9, math.sin(a) * 0.9, 0.05),
                                                           (math.cos(a) * 1.5, math.sin(a) * 1.5, -0.15)], 0.22, stam_m)))
    tips = []

    def branch(p0, d, L, r, depth, tag):
        p1 = p0 + d * L
        mid = p0 + d * L * 0.5 + Vector((rnd.uniform(-0.3, 0.3), rnd.uniform(-0.3, 0.3), rnd.uniform(-0.1, 0.25))) * L * 0.4
        parts.append(T.to_mesh(T.tube(f"{name}_tak{tag}", [tuple(p0), tuple(mid), tuple(p1)], r, stam_m)))
        if depth == 0:
            tips.append((p1, L))
            return
        n = 3 if depth > 1 else rnd.choice((2, 3))
        for k in range(n):
            nd = (d + Vector((rnd.uniform(-0.9, 0.9), rnd.uniform(-0.9, 0.9), rnd.uniform(-0.1, 0.5)))).normalized()
            if nd.z < -0.1:
                nd.z = -0.1
                nd.normalize()
            branch(p1, nd, L * rnd.uniform(0.55, 0.72), r * 0.6, depth - 1, f"{tag}_{k}")
    for k in range(5):
        a = 2 * math.pi * k / 5 + rnd.uniform(-0.3, 0.3)
        d = Vector((math.cos(a) * 0.75, math.sin(a) * 0.75, 0.75)).normalized()
        branch(Vector((0, 0, 2.6 + rnd.uniform(-0.2, 0.4))), d, rnd.uniform(2.0, 2.6), 0.24, 3, str(k))
    parts.append(T.to_mesh(T.tube(name + "_top", [(0, 0, 2.8), (0.2, 0.1, 4.2), (0.1, -0.2, 5.6)], 0.26, stam_m)))
    tips.append((Vector((0.1, -0.2, 5.6)), 1.2))
    stam = T.merge(name + "_stam_takken", parts, ol=0)
    stam.parent = None
    objs = [stam]
    if loof:
        clumps = []
        tex = bpy.data.textures.get("eik_loof_ruis") or bpy.data.textures.new("eik_loof_ruis", "CLOUDS")
        tex.noise_scale = 0.6
        for k, (p, L) in enumerate(tips):
            for j in range(2):
                r = rnd.uniform(0.9, 1.4) * (1.0 if j == 0 else 0.75)
                off = Vector((rnd.uniform(-0.5, 0.5), rnd.uniform(-0.5, 0.5), rnd.uniform(0.0, 0.6)))
                mt = _m(f"blad_eik_{seizoen}_{(k + j) % len(loof)}", loof[(k + j) % len(loof)])
                s = T.sphere(f"{name}_loof{k}_{j}", tuple(p + off), r, mt, scale=(1, 1, 0.82), seg=16, ol=0)
                dm = s.modifiers.new("ruis", "DISPLACE")
                dm.texture = tex
                dm.strength = 0.45
                dm.texture_coords = "GLOBAL"
                clumps.append(s)
        objs.append(T.merge(name + "_loof", clumps, ol=0))
    if sneeuw:
        sn = []
        snm = _m("sneeuw_tak", (0.92, 0.95, 1.0))
        for k, (p, L) in enumerate(tips[::2]):
            sn.append(T.sphere(f"{name}_sneeuw{k}", tuple(p + Vector((0, 0, 0.05))), 0.12, snm, scale=(1.6, 1.6, 0.35), seg=10, ol=0))
        objs.append(T.merge(name + "_sneeuw", sn, ol=0))
    if klimop:
        km = _m("blad_klimop", (0.10, 0.34, 0.10))
        kl = []
        for k in range(60):
            a = rnd.uniform(0, 6.28)
            z = rnd.uniform(0.0, 3.0)
            r = 0.62 - z * 0.06
            kl.append(T.sphere(f"{name}_klimop{k}", (math.cos(a) * r, math.sin(a) * r, z), 0.16, km, scale=(1, 1, 0.6), seg=8, ol=0))
        objs.append(T.merge(name + "_klimop", kl, ol=0))
    root = S._empty(name, size=1.0)
    for o in objs:
        o.parent = root
    root.location = loc
    root.scale = (schaal,) * 3
    root.rotation_euler.z = rnd.uniform(0, 6.28)
    return root


def heuvelbank(name="Bank", loc=(0, 0, 0), rot_z=0.0, sneeuw=False, plaatje=True):
    """Houten parkbank met gietijzeren poten; zit naar -Y (rug aan +Y). Zitting op 0,45 m, 1,9 m breed."""
    root = S._empty(name, size=0.4)
    hout = _m("hout_bank", (0.50, 0.30, 0.15))
    ijzer = _m("metaal_gietijzer", (0.06, 0.07, 0.07))
    p = []
    for k in range(4):
        p.append(T.box(f"{name}_zitlat{k}", (0, -0.2 + k * 0.13, 0.43), (1.9, 0.11, 0.035), hout, bevel=0.012, ol=0))
    for k in range(3):
        p.append(T.box(f"{name}_ruglat{k}", (0, 0.27 + k * 0.025, 0.58 + k * 0.13), (1.9, 0.03, 0.1), hout, rot=(-14, 0, 0),
                       bevel=0.01, ol=0))
    T.merge(name + "_hout", p, ol=0).parent = root
    q = []
    for sx in (-0.8, 0.8):
        q += [T.to_mesh(T.tube(f"{name}_poot{sx}", [(sx, -0.25, 0), (sx, -0.22, 0.42), (sx, 0.24, 0.42), (sx, 0.28, 0),
                                                   ], 0.025, ijzer)),
              T.to_mesh(T.tube(f"{name}_rugsteun{sx}", [(sx, 0.24, 0.42), (sx, 0.32, 0.95)], 0.022, ijzer)),
              T.to_mesh(T.tube(f"{name}_leuning{sx}", [(sx * 1.17, 0.26, 0.45), (sx * 1.17, -0.1, 0.65), (sx * 1.17, -0.3, 0.6),
                                                      (sx * 1.17, -0.26, 0.42)], 0.02, ijzer))]
    T.merge(name + "_ijzer", q, ol=0).parent = root
    if plaatje:
        pl = T.box(name + "_plaatje", (0, 0.33, 0.7), (0.18, 0.006, 0.05), _m("messing_plaatje", (0.85, 0.65, 0.3)),
                   rot=(-14, 0, 0), bevel=0.002, ol=0)
        pl.parent = root
    if sneeuw:
        snm = _m("sneeuw_bank", (0.93, 0.96, 1.0))
        s = [T.box(name + "_sneeuw_zit", (0, -0.0, 0.465), (1.88, 0.5, 0.05), snm, bevel=0.02, ol=0),
             T.box(name + "_sneeuw_rug", (0, 0.33, 0.92), (1.88, 0.07, 0.035), snm, bevel=0.012, ol=0)]
        T.merge(name + "_sneeuw", s, ol=0).parent = root
    root.location = loc
    root.rotation_euler.z = math.radians(rot_z)
    return root


def stenen_bank(name="Stenen_bank", loc=(0, 0, 0), rot_z=0.0, alleen_voet=False, mos=0.0, verkoold=False):
    """Nieuwe stenen bank (2110). alleen_voet=True: alleen de stenen voet is nog over (3026 en later)."""
    root = S._empty(name, size=0.4)
    col = (0.06, 0.05, 0.05) if verkoold else (0.70, 0.68, 0.64)
    steen = _m("steen_bank_verkoold" if verkoold else "steen_bank", col)
    p = [T.box(name + "_voet", (0, 0, 0), (1.5, 0.42, 0.38), steen, bevel=0.03, ol=0)]
    if not alleen_voet:
        p += [T.box(name + "_zitting", (0, 0, 0.38), (2.0, 0.5, 0.08), steen, bevel=0.025, ol=0),
              T.box(name + "_rug", (0, 0.24, 0.46), (2.0, 0.1, 0.42), steen, rot=(-8, 0, 0), bevel=0.025, ol=0)]
    else:
        p += [T.box(name + "_brokstuk", (0.55, 0.0, 0.38), (0.5, 0.42, 0.06), steen, rot=(0, 4, 8), bevel=0.02, ol=0)]
    o = T.merge(name + "_steen", p, ol=0)
    o.parent = root
    if mos:
        rnd = random.Random(4)
        mm = _m("gras_mos", (0.18, 0.38, 0.10))
        ms = [T.sphere(f"{name}_mos{k}", (rnd.uniform(-0.7, 0.7), rnd.uniform(-0.2, 0.2), rnd.uniform(0.1, 0.4)), 0.09, mm,
                       scale=(1.4, 1, 0.5), seg=8, ol=0) for k in range(int(20 * mos))]
        T.merge(name + "_mos", ms, ol=0).parent = root
    root.location = loc
    root.rotation_euler.z = math.radians(rot_z)
    return root


# ---------------------------------------------------------------------------
# Toekomst en verre toekomst
# ---------------------------------------------------------------------------
def glazen_toren(name, loc, w=10.0, h=90.0, col=(0.35, 0.55, 0.70), lit=0.4, seed=0, spits=True, round_=False):
    """Moderne glazen toren met lichtbanden; nulpunt = midden onderkant."""
    rnd = random.Random(seed)
    root = S._empty(name, size=2.0)
    gl = _m(f"glas_toren_{'%.2f%.2f%.2f' % col}", col)
    p = []
    if round_:
        p.append(T.cyl(name + "_romp", (0, 0, 0), w / 2, h, gl, r2=w * 0.38, seg=32, ol=0))
    else:
        p.append(T.box(name + "_romp", (0, 0, 0), (w, w, h), gl, bevel=0.3, ol=0))
    if spits:
        p.append(T.cyl(name + "_spits", (0, 0, h), w * 0.06, h * 0.18, _m("staal_spits", (0.8, 0.82, 0.85)), r2=0.05, seg=12, ol=0))
    o = T.merge(name + "_toren", p, ol=0)
    o.parent = root
    bands = []
    lm = S._glowmat("toren_licht", (0.9, 0.95, 1.0), 2.5)
    for k in range(int(h / 6)):
        if rnd.random() < lit:
            z = 3 + k * 6
            rr = (w / 2 if not round_ else (w / 2 - (w / 2 - w * 0.38) * z / h)) + 0.05
            if round_:
                bands.append(T.cyl(f"{name}_band{k}", (0, 0, z), rr, 0.4, lm, seg=32, ol=0))
            else:
                bands.append(T.box(f"{name}_band{k}", (0, 0, z), (w + 0.1, w + 0.1, 0.4), lm, bevel=0, ol=0))
    if bands:
        T.merge(name + "_lichtbanden", bands, ol=0).parent = root
    root.location = loc
    return root


def vliegende_lichtjes(name, center, spread=(300, 120, 30), n=60, seed=8, col=(1.0, 0.85, 0.5), z0=20):
    """Vliegende auto's als lichtjes boven de daken (2086)."""
    rnd = random.Random(seed)
    m_ = S._glowmat("vliegend_licht", col, 12.0)
    pts = [T.sphere(f"{name}_{k}", (center[0] + rnd.uniform(-spread[0] / 2, spread[0] / 2),
                                    center[1] + rnd.uniform(-spread[1] / 2, spread[1] / 2),
                                    center[2] + z0 + rnd.uniform(0, spread[2])), rnd.uniform(0.3, 0.6), m_, seg=8, ol=0)
           for k in range(n)]
    return T.merge(name, pts, ol=0)


def vliegende_auto(name, loc, rot_z=0.0, col=(0.9, 0.92, 0.95)):
    """Vliegende auto (2200): druppelvorm met cockpit en blauwe straalpods."""
    root = S._empty(name, size=1.0)
    lak = _m(f"lak_vliegauto_{'%.2f%.2f%.2f' % col}", col)
    p = [T.sphere(name + "_romp", (0, 0, 0), 1.0, lak, scale=(2.2, 1.0, 0.55), seg=24, ol=0),
         T.sphere(name + "_cockpit", (0.3, 0, 0.35), 0.75, _m("glas_cockpit_donker", (0.05, 0.08, 0.12)), scale=(1.3, 0.8, 0.5), seg=20, ol=0)]
    T.merge(name + "_mesh", p, ol=0).parent = root
    gm = S._glowmat("straal_blauw", (0.3, 0.7, 1.0), 10)
    for sy in (-1, 1):
        T.cyl(f"{name}_pod{sy}", (-1.2, sy * 1.0, -0.2), 0.3, 0.6, lak, rot=(0, 90, 0), seg=16, ol=0).parent = root
        T.cyl(f"{name}_straal{sy}", (-1.25, sy * 1.0, -0.2), 0.22, 0.05, gm, rot=(0, 90, 0), seg=16, ol=0).parent = root
    root.location = loc
    root.rotation_euler.z = math.radians(rot_z)
    return root


def grazer(name, loc, rot_z=0.0, schaal=1.0, col=(0.36, 0.30, 0.24), seed=0):
    """Vreemd groot vogelachtig graasdier (1 miljoen jaar): ovaal lijf, lange nek, twee lange poten."""
    rnd = random.Random(seed)
    root = S._empty(name, size=1.0)
    huid = _m(f"huid_grazer_{'%.2f%.2f%.2f' % col}", col)
    buik = _m("huid_grazer_buik", (0.70, 0.62, 0.50))
    neck_up = rnd.uniform(-0.6, 0.6)
    head = (1.6, 0, 2.7 + neck_up)
    p = [T.sphere(name + "_lijf", (0, 0, 2.2), 1.0, huid, scale=(1.5, 0.75, 0.8), seg=18, ol=0),
         T.sphere(name + "_buik", (0.1, 0, 1.9), 0.7, buik, scale=(1.4, 0.7, 0.5), seg=14, ol=0),
         T.to_mesh(T.tube(name + "_nek", [(1.2, 0, 2.5), (1.5, 0, 3.2 + neck_up * 0.5), head], 0.22, huid)),
         T.sphere(name + "_kop", head, 0.32, huid, scale=(1.5, 0.8, 0.8), seg=12, ol=0),
         T.to_mesh(T.tube(name + "_staart", [(-1.4, 0, 2.3), (-2.2, 0, 2.6), (-2.6, 0, 2.2)], 0.12, huid))]
    if neck_up < -0.2:  # graast: kop omlaag
        p[2] = T.to_mesh(T.tube(name + "_nek2", [(1.2, 0, 2.5), (1.9, 0, 2.0), (2.1, 0, 0.6)], 0.2, huid))
        p[3] = T.sphere(name + "_kop2", (2.15, 0, 0.45), 0.3, huid, scale=(1.2, 0.8, 1.4), seg=12, ol=0)
    for sy in (-0.35, 0.35):
        p.append(T.to_mesh(T.tube(f"{name}_poot{sy}", [(0.1, sy, 1.8), (0.5, sy, 1.0), (0.2, sy, 0.0)], 0.1, huid)))
    T.merge(name + "_mesh", p, ol=0).parent = root
    root.location = loc
    root.rotation_euler.z = math.radians(rot_z)
    root.scale = (schaal,) * 3
    return root


def ruimteschip(name, loc, hoogte=180.0, vlam=True, rot_z=0.0, scherm=None):
    """Kolossaal kolonieschip (1 miljoen jaar). Nulpunt = onderkant. vlam=True: lange vuurstaart (materiaal
    `<naam>_vlam`, Emission Strength keyframen). scherm=tekst op een groot scherm op de zijkant."""
    root = S._empty(name, size=5.0)
    w = hoogte * 0.22
    rompm = _m("metaal_schip_wit", (0.86, 0.87, 0.88))
    donker = _m("metaal_schip_donker", (0.22, 0.24, 0.28))
    p = [T.cyl(name + "_romp", (0, 0, hoogte * 0.12), w / 2, hoogte * 0.68, rompm, r2=w * 0.42, seg=40, ol=0),
         T.cyl(name + "_neus", (0, 0, hoogte * 0.8), w * 0.42, hoogte * 0.2, rompm, r2=w * 0.04, seg=40, ol=0),
         T.cyl(name + "_motor", (0, 0, 0), w * 0.36, hoogte * 0.12, donker, r2=w / 2, seg=40, ol=0)]
    for k in range(4):
        a = k * 90 + 45
        p.append(T.box(f"{name}_vin{k}", (math.cos(math.radians(a)) * w * 0.55, math.sin(math.radians(a)) * w * 0.55, 0),
                       (w * 0.5, w * 0.06, hoogte * 0.3), donker, rot=(0, 0, a), bevel=0.4, ol=0))
    for k in range(10):
        p.append(T.cyl(f"{name}_ring{k}", (0, 0, hoogte * (0.18 + k * 0.06)), w / 2 * (1 - k * 0.012) + 0.15, 0.6,
                       donker, seg=40, ol=0))
    T.merge(name + "_romp_mesh", p, ol=0).parent = root
    ramen = S._glowmat("ramen_schip", (1.0, 0.85, 0.55), 4.0)
    rp = []
    for k in range(10):
        for j in range(16):
            a = j / 16 * 2 * math.pi
            z = hoogte * (0.2 + k * 0.055) + 2
            rr = w / 2 * (1 - (z - hoogte * 0.12) / (hoogte * 0.68) * 0.16) + 0.05
            rp.append(T.box(f"{name}_raam{k}_{j}", (math.cos(a) * rr, math.sin(a) * rr, z), (1.6, 0.2, 1.0), ramen,
                            rot=(0, 0, math.degrees(a) + 90), bevel=0, ol=0))
    T.merge(name + "_ramen", rp, ol=0).parent = root
    if vlam:
        vm = pbr(name + "_vlam", (1.0, 0.6, 0.2), emit=(1.0, 0.55, 0.18), strength=25.0)
        v = T.cyl(name + "_vlamstaart", (0, 0, -hoogte * 1.2), w * 0.12, hoogte * 1.2, vm, r2=w * 0.36, seg=24, ol=0)
        v.parent = root
        rook = _m("rook_schip", (0.85, 0.82, 0.78))
        rk = [T.sphere(f"{name}_rook{k}", (math.cos(k) * w * 0.4 * (1 + k * 0.1), math.sin(k) * w * 0.4, -hoogte * 1.2 - k * 3),
                       w * (0.5 + k * 0.05), rook, seg=12, ol=0) for k in range(8)]
        T.merge(name + "_rookwolk", rk, ol=0).parent = root
    if scherm:
        sc = T.box(name + "_scherm", (0, -w * 0.47, hoogte * 0.45), (w * 0.62, 0.3, w * 0.32), S._glowmat(name + "_scherm_achter",
                                                                                                      (0.03, 0.05, 0.12), 1.0),
                   bevel=0, ol=0)
        sc.parent = root
        for k, line in enumerate(scherm):
            t = S.label(f"{name}_scherm_tekst{k}", line, (0, -w * 0.47 - 0.2, hoogte * 0.45 + w * (0.2 - k * 0.11)),
                        w * (0.07 if k == 0 else 0.05), (0.9, 0.95, 1.0), glow=6.0, extrude=0.05)
            t.parent = root
    root.location = loc
    root.rotation_euler.z = math.radians(rot_z)
    return root


def loopplank(name, loc, rot_z=0.0, lengte=9.0, open_=1.0):
    """Loopplank naar het schip; `<naam>_plank` draait om de bovenkant (rotation_euler.x) = omhoog schuiven."""
    root = S._empty(name, size=1.0)
    piv = S._empty(name + "_plank", (0, 0, 0), size=0.5)
    piv.parent = root
    p = [T.box(name + "_vlak", (0, -lengte / 2, -0.1), (2.4, lengte, 0.2), _m("metaal_schip_wit", (0.86, 0.87, 0.88)), bevel=0.05, ol=0)]
    lm = S._glowmat("loopplank_licht", (0.5, 0.85, 1.0), 6.0)
    for sx in (-1.15, 1.15):
        p.append(T.box(f"{name}_lichtlijn{sx}", (sx, -lengte / 2, 0.0), (0.06, lengte, 0.04), lm, bevel=0, ol=0))
    T.merge(name + "_mesh", p, ol=0).parent = piv
    ang = math.atan2(3.5, lengte)
    piv.rotation_euler.x = -ang * open_ + (1 - open_) * math.radians(80)
    root.location = loc
    root.rotation_euler.z = math.radians(rot_z)
    return root


# ---------------------------------------------------------------------------
# Ruimte: sterrenveld, sterrenstelsels, zwarte gaten
# ---------------------------------------------------------------------------
def sterrenveld(name="Sterrenveld", n=4000, radius=900.0, seed=42, center=(0, 0, 0)):
    """Duizenden sterren in één object. Waarde-node 'Sterren uit' (0..1) zet ze één voor één uit."""
    rnd = random.Random(seed)
    bm = bmesh.new()
    uit = bm.verts.layers.float.new("uit")
    helder = bm.verts.layers.float.new("helder")
    tint = bm.verts.layers.float.new("tint")
    for k in range(n):
        d = Vector((rnd.gauss(0, 1), rnd.gauss(0, 1), rnd.gauss(0, 1))).normalized()
        # band van de melkweg: iets dichter rond een schuine cirkel
        if rnd.random() < 0.45:
            a = rnd.uniform(0, 2 * math.pi)
            d = Vector((math.cos(a), math.sin(a) * 0.5, math.sin(a) * 0.86 + rnd.gauss(0, 0.12))).normalized()
        c = Vector(center) + d * radius * rnd.uniform(0.9, 1.1)
        s = radius * 0.0016 * (rnd.random() ** 3 * 2.4 + 0.5)
        res = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=s, matrix=Matrix.Translation(c))
        u, h_, t_ = rnd.random(), rnd.uniform(0.5, 1.0) ** 2, rnd.random()
        for v in res["verts"]:
            v[uit] = u
            v[helder] = h_
            v[tint] = t_
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    mt = bpy.data.materials.new(name + "_mat")
    mt.use_nodes = True
    N, L = mt.node_tree.nodes, mt.node_tree.links
    N.clear()
    out = N.new("ShaderNodeOutputMaterial")
    em = N.new("ShaderNodeEmission")
    a_uit = N.new("ShaderNodeAttribute")
    a_uit.attribute_name = "uit"
    a_h = N.new("ShaderNodeAttribute")
    a_h.attribute_name = "helder"
    a_t = N.new("ShaderNodeAttribute")
    a_t.attribute_name = "tint"
    val = N.new("ShaderNodeValue")
    val.name = val.label = "Sterren uit"
    val.outputs[0].default_value = 0.0
    cmp = N.new("ShaderNodeMath")
    cmp.operation = "GREATER_THAN"   # 1 = ster brandt nog
    L.new(a_uit.outputs["Fac"], cmp.inputs[0])
    L.new(val.outputs[0], cmp.inputs[1])
    mul = N.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    L.new(cmp.outputs[0], mul.inputs[0])
    L.new(a_h.outputs["Fac"], mul.inputs[1])
    mul2 = N.new("ShaderNodeMath")
    mul2.operation = "MULTIPLY"
    mul2.inputs[1].default_value = 14.0
    mul2.name = mul2.label = "Helderheid"
    L.new(mul.outputs[0], mul2.inputs[0])
    ramp = N.new("ShaderNodeValToRGB")
    cr = ramp.color_ramp
    cr.elements[0].color = (1.0, 0.62, 0.42, 1)
    cr.elements[1].color = (0.62, 0.78, 1.0, 1)
    e = cr.elements.new(0.55)
    e.color = (1.0, 0.97, 0.92, 1)
    L.new(a_t.outputs["Fac"], ramp.inputs["Fac"])
    L.new(ramp.outputs["Color"], em.inputs["Color"])
    L.new(mul2.outputs[0], em.inputs["Strength"])
    L.new(em.outputs[0], out.inputs["Surface"])
    me.materials.append(mt)
    o = bpy.data.objects.new(name, me)
    o.visible_shadow = False
    T._link(o)
    return o


def sterrenstelsel(name, loc, r=40.0, kleur=(0.85, 0.75, 1.0), seed=1, rot=(60, 0, 20), n=900):
    """Spiraalstelsel als wolkje gloeiende puntjes (kan als geheel wegdrijven)."""
    rnd = random.Random(seed)
    bm = bmesh.new()
    for k in range(n):
        arm = k % 2
        t = rnd.random() ** 0.7
        a = t * 4.5 + arm * math.pi + rnd.gauss(0, 0.25)
        rr = t * r
        c = Vector((math.cos(a) * rr, math.sin(a) * rr, rnd.gauss(0, r * 0.02)))
        bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r * 0.006 * rnd.uniform(0.5, 1.5), matrix=Matrix.Translation(c))
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r * 0.08)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(S._glowmat(f"stelsel_{'%.2f%.2f%.2f' % kleur}", kleur, 6.0))
    o = bpy.data.objects.new(name, me)
    o.visible_shadow = False
    T._link(o)
    o.location = loc
    o.rotation_euler = Euler([math.radians(a) for a in rot])
    return o


def zwart_gat(name, loc, r=6.0, rot=(70, 0, 0), gloed=8.0):
    """Zwart gat: zwarte bol met een dunne gloeiende ring (materiaal `<naam>_ring`, verdampen = sterkte naar 0)."""
    root = S._empty(name, size=r)
    T.sphere(name + "_kern", (0, 0, 0), r, S._glowmat("zwart_absoluut", (0, 0, 0), 0.0), seg=24, ol=0).parent = root
    rm = pbr(name + "_ring", (1.0, 0.6, 0.3), emit=(1.0, 0.62, 0.32), strength=gloed)
    T.torus(name + "_schijf", (0, 0, 0), r * 1.9, r * 0.12, rm, seg=64, seg2=8, ol=0).parent = root
    T.torus(name + "_fotonring", (0, 0, 0), r * 1.12, r * 0.03, rm, rot=(90, 0, 0), seg=64, seg2=6, ol=0).parent = root
    root.location = loc
    root.rotation_euler = Euler([math.radians(a) for a in rot])
    return root
