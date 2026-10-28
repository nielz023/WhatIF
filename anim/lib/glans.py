"""Glans-look voor geriggede figuren (vanaf video 2), plus de kraai en effecten van
"What IF You Got 10x FASTER Every Day?".

rig.load() geeft figuren toon-materialen en contourlijnen. character(ch) zet die om
naar dezelfde glimmende materialen als cast/render_glans.py (vinyl-speelgoed met een
coatlaag, zachte huid); gezichtsdecals blijven onbelicht.

    import rig as R, glans as G
    ch = R.load("broertje_dino")
    G.character(ch)
    G.studio()                      # donkere studio met logo-belichting (voor los werk)
    kraai = G.crow("kraai", (0, 0, 3), wing=35)
    G.smoke(ch, "foot.L", t0=10, t1=60)
    G.ghosts(ch, frame=1, offsets=[(0.25, 0, 0), (0.5, 0, 0)])
"""
import math
import os
import random
import sys

import bpy
import bmesh
from mathutils import Vector, Matrix, Euler

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "cast"))
import render_glans as RG  # noqa: E402

lin = RG.lin


# ---------------------------------------------------------------------------
# Figuren
# ---------------------------------------------------------------------------
def _toon_color(m):
    """Kleur van een toon-materiaal (ToonLicht-groep) of gewoon de viewport-kleur."""
    if m.node_tree:
        for n in m.node_tree.nodes:
            if n.type == "GROUP" and "Kleur" in n.inputs:
                return tuple(n.inputs["Kleur"].default_value)[:3]
    return tuple(m.diffuse_color)[:3]


def _is_flat(m):
    return m.node_tree is not None and any(n.type == "EMISSION" for n in m.node_tree.nodes) and \
        not any(n.type == "BSDF_PRINCIPLED" for n in m.node_tree.nodes)


_cache = {}


def gloss_material(m):
    """Glans-versie van een (toon-)materiaal; zelfde kleur, één keer per materiaal."""
    if m is None or _is_flat(m) or m.name.startswith(("Contour", "contour", "outline")):
        return m
    if m.name in _cache:
        return _cache[m.name]
    col = _toon_color(m)
    g = bpy.data.materials.new("glans_" + m.name)
    g.use_nodes = True
    b = g.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*col, 1)
    if "metaal" in m.name.lower() or "zilver" in m.name.lower():
        b.inputs["Metallic"].default_value = 1.0
    g.diffuse_color = (*col, 1)
    RG.glossify(g)
    _cache[m.name] = g
    return g


def character(ch):
    """Zet een figuur uit rig.load() om naar de glans-look (geen contourlijn)."""
    objs = [ch.body] + [o for o in ch.rig.children if o.type == "MESH" and o != ch.body]
    for o in objs:
        for md in [md for md in o.modifiers if md.name == "Contour"]:
            o.modifiers.remove(md)
        for slot in o.material_slots:
            slot.material = gloss_material(slot.material)
    return ch


def studio(samples=64, pct=100):
    """Donkere glans-studio (wand met blauwe gloed en logo-licht) in de huidige scène."""
    st = RG.setup_look(samples, pct)
    if st.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(st)
    return st


# ---------------------------------------------------------------------------
# De kraai (cold open: bevroren midden in een vleugelslag boven de straat)
# ---------------------------------------------------------------------------
def _pbr(name, hexcol, rough=0.35, coat=0.3, film=0.0):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*lin(hexcol), 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Coat Weight"].default_value = coat
    b.inputs["Coat Roughness"].default_value = 0.2
    if film and "Thin Film Thickness" in b.inputs:
        # zwart met een blauw-paarse weerschijn, zoals echte kraaienveren
        b.inputs["Thin Film Thickness"].default_value = film
        b.inputs["Thin Film IOR"].default_value = 1.45
        b.inputs["Specular IOR Level"].default_value = 0.8
    m.diffuse_color = (*lin(hexcol), 1)
    return m


def _unlit(name, hexcol):
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
    return m


def _blob(name, mat, center, scale, rot=(0, 0, 0), coll=None, seg=24, rings=14, taper=None):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, radius=1.0)
    if taper:
        # taper(v) -> schaal in x/z langs de y-as (voor druppel- en veervormen)
        for v in bm.verts:
            s = taper(v.co.y)
            v.co.x *= s
            v.co.z *= s
    M = Matrix.Translation(Vector(center)) @ Euler(rot).to_matrix().to_4x4() @ \
        Matrix.Diagonal((*scale, 1))
    bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    (coll or bpy.context.scene.collection).objects.link(ob)
    return ob


def crow(name="kraai", loc=(0, 0, 0), rot_z=0.0, wing=35.0, spread=1.0, scale=1.0, coll=None):
    """Kraai van ~45 cm (snavel tot staart) die naar -y vliegt.
    wing = vleugelhoek in graden (+ omhoog, - omlaag), spread = hoe ver de handpennen
    uitwaaieren (0..1). De vleugels hangen aan de lege objecten <name>_vleugel_L/_R:
    draai die om hun Y-as om te flappen. Geeft het hoofdobject (leeg) terug."""
    c = bpy.data.collections.new("Dier " + name)
    (coll or bpy.context.scene.collection).children.link(c)
    M_f = _pbr("kraai_veren", "#16161C", rough=0.32, coat=0.35, film=380.0)
    M_beak = _pbr("kraai_snavel", "#2A2A2E", rough=0.25, coat=0.5)
    M_eye = _pbr("kraai_oog", "#0A0A0C", rough=0.05, coat=1.0)
    M_glint = _unlit("kraai_glans", "#FFFFFF")

    root = bpy.data.objects.new(name, None)
    root.empty_display_size = 0.2
    c.objects.link(root)
    parts = []
    # romp: druppel, dik bij de borst
    parts.append(_blob(f"{name}_romp", M_f, (0, 0.02, 0), (0.075, 0.16, 0.078), coll=c,
                       taper=lambda y: 1.0 - 0.35 * max(0.0, y)))
    parts.append(_blob(f"{name}_borst", M_f, (0, -0.07, -0.012), (0.07, 0.08, 0.07), coll=c))
    # kop en snavel
    parts.append(_blob(f"{name}_kop", M_f, (0, -0.15, 0.03), (0.052, 0.058, 0.05), coll=c))
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=0.022, radius2=0.002, depth=0.075)
    bmesh.ops.transform(bm, matrix=Matrix.Translation((0, -0.225, 0.022)) @
                        Euler((math.radians(97), 0, 0)).to_matrix().to_4x4() @
                        Matrix.Diagonal((0.85, 1.0, 1.0, 1)), verts=bm.verts)
    me = bpy.data.meshes.new(f"{name}_snavel")
    bm.to_mesh(me)
    bm.free()
    me.materials.append(M_beak)
    beak = bpy.data.objects.new(f"{name}_snavel", me)
    c.objects.link(beak)
    parts.append(beak)
    for s in (-1, 1):
        e = _blob(f"{name}_oog_{'L' if s > 0 else 'R'}", M_eye, (s * 0.04, -0.178, 0.045),
                  (0.011, 0.011, 0.011), coll=c, seg=12, rings=8)
        g = _blob(f"{name}_oogglans_{'L' if s > 0 else 'R'}", M_glint, (s * 0.048, -0.182, 0.05),
                  (0.0035, 0.0035, 0.0035), coll=c, seg=8, rings=6)
        parts += [e, g]
    # staart: waaier van 6 pennen
    for k in range(6):
        a = math.radians(-18 + 36 * k / 5)
        parts.append(_blob(f"{name}_staart{k}", M_f, (math.sin(a) * 0.06, 0.24 + math.cos(a) * 0.04, 0.005),
                           (0.024, 0.09, 0.006), rot=(math.radians(-6), 0, -a), coll=c,
                           taper=lambda y: 1.0 - 0.2 * y))
    # poten opgetrokken onder het lijf
    for s in (-1, 1):
        parts.append(_blob(f"{name}_poot_{'L' if s > 0 else 'R'}", M_beak, (s * 0.03, 0.09, -0.06),
                           (0.012, 0.05, 0.01), rot=(math.radians(20), 0, 0), coll=c))
    for p in parts:
        p.parent = root

    # vleugels: armstuk + 9 handpennen + 6 armpennen, aan een draaipunt bij de schouder
    for s in (-1, 1):
        side = "L" if s > 0 else "R"
        piv = bpy.data.objects.new(f"{name}_vleugel_{side}", None)
        piv.empty_display_size = 0.05
        c.objects.link(piv)
        piv.parent = root
        piv.location = (s * 0.055, -0.04, 0.03)
        wp = []
        # dekveren (de 'arm' van de vleugel)
        wp.append(_blob(f"{name}_dekveren_{side}", M_f, (s * 0.16, 0.02, 0), (0.17, 0.075, 0.014),
                        rot=(0, 0, s * math.radians(-4)), coll=c))
        # armpennen langs de achterrand
        for k in range(6):
            x = s * (0.05 + 0.045 * k)
            wp.append(_blob(f"{name}_armpen{k}_{side}", M_f, (x, 0.1, -0.002), (0.022, 0.08, 0.005),
                            rot=(0, 0, s * math.radians(-6 + 2 * k)), coll=c,
                            taper=lambda y: 1.0 - 0.15 * y))
        # handpennen, uitwaaierend als 'vingers'
        for k in range(9):
            fan = math.radians((-10 + 9 * k) * spread)
            base = Vector((s * 0.31, 0.03 + 0.012 * k, 0))
            L = 0.17 - 0.006 * abs(k - 2)
            d = Vector((s * math.cos(fan), math.sin(fan), 0))
            ctr = base + d * L * 0.5
            yaw = math.atan2(d.y, d.x) - (0 if s > 0 else math.pi)
            wp.append(_blob(f"{name}_handpen{k}_{side}", M_f, ctr, (L * 0.5, 0.018, 0.004),
                            rot=(0, s * math.radians(2 * k), yaw), coll=c,
                            taper=lambda y: 1.0))
        for o in wp:
            o.location -= piv.location
            o.parent = piv
        piv.rotation_euler = (0, -s * math.radians(wing), 0)
        # tweede knik: de handpennen buigen iets verder door (mid-flap)
    root.location = loc
    root.rotation_euler = (0, 0, math.radians(rot_z))
    root.scale = (scale, scale, scale)
    return root


def flap(crow_root, frame, wing):
    """Keyframe de vleugelhoek van een kraai op een frame."""
    for s, side in ((1, "L"), (-1, "R")):
        piv = bpy.data.objects[f"{crow_root.name}_vleugel_{side}"]
        piv.rotation_euler = (0, -s * math.radians(wing), 0)
        piv.keyframe_insert("rotation_euler", frame=frame)


# ---------------------------------------------------------------------------
# Effecten
# ---------------------------------------------------------------------------
def _smoke_mat():
    m = bpy.data.materials.get("rook")
    if m:
        return m
    m = bpy.data.materials.new("rook")
    m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    N.clear()
    out = N.new("ShaderNodeOutputMaterial")
    vol = N.new("ShaderNodeVolumePrincipled")
    vol.inputs["Color"].default_value = (*lin("#BFC3C9"), 1)
    vol.inputs["Density"].default_value = 6.0
    # zachte rand: dichtheid valt af naar de buitenkant van de bol
    geo = N.new("ShaderNodeTexCoord")
    dist = N.new("ShaderNodeVectorMath")
    dist.operation = "LENGTH"
    noise = N.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 3.0
    mr = N.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 1.0
    mr.inputs["From Max"].default_value = 0.2
    mul = N.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    mul2 = N.new("ShaderNodeMath")
    mul2.operation = "MULTIPLY"
    mul2.inputs[1].default_value = 80.0
    L.new(geo.outputs["Object"], dist.inputs[0])
    L.new(dist.outputs["Value"], mr.inputs["Value"])
    L.new(geo.outputs["Object"], noise.inputs["Vector"])
    L.new(mr.outputs["Result"], mul.inputs[0])
    L.new(noise.outputs["Fac"], mul.inputs[1])
    L.new(mul.outputs[0], mul2.inputs[0])
    L.new(mul2.outputs[0], vol.inputs["Density"])
    L.new(vol.outputs[0], out.inputs["Volume"])
    return m


def smoke(ch, bone, t0=1, t1=48, n=8, rise=0.45, size=0.06, seed=1, offset=(0, 0, 0), at="head"):
    """Rookpluimpjes die opstijgen van een bot (rokende schoenen: 'foot.L', mouw: 'forearm.R').
    Frames t0..t1; elke pluim groeit, stijgt op en verdwijnt. Zet de pose van de figuur
    eerst, want de pluimen starten op de plek van het bot (at='head' of 'tail') op dat frame."""
    rnd = random.Random(seed)
    mat = _smoke_mat()
    sc = bpy.context.scene
    pb = ch.pb[bone]
    out = []
    span = max(t1 - t0, 1)
    for k in range(n):
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0)
        me = bpy.data.meshes.new(f"rook_{ch.name}_{bone}_{k}")
        bm.to_mesh(me)
        bm.free()
        me.materials.append(mat)
        ob = bpy.data.objects.new(me.name, me)
        ch.rig.users_collection[0].objects.link(ob)
        start = t0 + int(span * k / n)
        life = int(span * 0.6) + 6
        drift = Vector((rnd.uniform(-0.08, 0.08), rnd.uniform(-0.08, 0.08), 0))
        for f, t in ((start - 1, None), (start, 0.0), (start + life // 2, 0.5), (start + life, 1.0)):
            sc.frame_set(f)
            src = ch.rig.matrix_world @ (pb.head if at == "head" else pb.tail)
            if t is None:
                ob.scale = (0, 0, 0)
                ob.location = src
                ob.keyframe_insert("scale", frame=f)
                ob.keyframe_insert("location", frame=f)
                continue
            s = size * (0.5 + 1.8 * t) * (0 if t == 1.0 else 1)
            ob.scale = (s, s, s)
            ob.location = src + Vector(offset) + drift * t + Vector((0, 0, rise * t + size * 0.5))
            ob.keyframe_insert("scale", frame=f)
            ob.keyframe_insert("location", frame=f)
        out.append(ob)
    return out


def _ghost_mat(alpha, tint="#BFD9FF"):
    name = f"spoor_{alpha:.2f}"
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    N.clear()
    out = N.new("ShaderNodeOutputMaterial")
    em = N.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*lin(tint), 1)
    em.inputs["Strength"].default_value = 1.2
    tr = N.new("ShaderNodeBsdfTransparent")
    fres = N.new("ShaderNodeLayerWeight")
    fres.inputs["Blend"].default_value = 0.6
    mix = N.new("ShaderNodeMixShader")
    mul = N.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    mul.inputs[1].default_value = alpha
    inv = N.new("ShaderNodeMath")
    inv.operation = "SUBTRACT"
    inv.inputs[0].default_value = 1.0
    # alleen het buitenste oppervlak: achter de eerste laag is het spoor helemaal doorzichtig,
    # zodat je geen binnenkant (oogjes, mond, armen) door het lichaam heen ziet
    lp = N.new("ShaderNodeLightPath")
    first = N.new("ShaderNodeMath")
    first.operation = "LESS_THAN"
    first.inputs[1].default_value = 0.5
    gate = N.new("ShaderNodeMath")
    gate.operation = "MULTIPLY"
    L.new(fres.outputs["Facing"], inv.inputs[1])
    L.new(inv.outputs[0], mul.inputs[0])
    L.new(lp.outputs["Transparent Depth"], first.inputs[0])
    L.new(mul.outputs[0], gate.inputs[0])
    L.new(first.outputs[0], gate.inputs[1])
    L.new(gate.outputs[0], mix.inputs[0])
    L.new(tr.outputs[0], mix.inputs[1])
    L.new(em.outputs[0], mix.inputs[2])
    L.new(mix.outputs[0], out.inputs["Surface"])
    m.diffuse_color = (*lin(tint), alpha)
    return m


def ghosts(ch, frame, offsets, alphas=None, tint="#BFD9FF"):
    """Snelheidsspoor: doorzichtige, gloeiende kopieën van de figuur in de pose van `frame`,
    verschoven met `offsets` (wereldruimte, meters). De eerste is het meest zichtbaar."""
    sc = bpy.context.scene
    sc.frame_set(frame)
    dg = bpy.context.evaluated_depsgraph_get()
    ev = ch.body.evaluated_get(dg)
    me = bpy.data.meshes.new_from_object(ev, depsgraph=dg)
    me.transform(ch.body.matrix_world)
    alphas = alphas or [0.8 * (1 - k / (len(offsets) + 1)) for k in range(len(offsets))]
    out = []
    for k, (off, a) in enumerate(zip(offsets, alphas)):
        m2 = me.copy()
        m2.materials.clear()
        m2.materials.append(_ghost_mat(a, tint))
        for p in m2.polygons:
            p.material_index = 0
        ob = bpy.data.objects.new(f"spoor_{ch.name}_{k}", m2)
        ob.location = Vector(off)
        ch.rig.users_collection[0].objects.link(ob)
        out.append(ob)
    return out
