"""Toon- en glans-stijl voor alle sets van 3D What If Channel.

Sinds video 2 is de glans-look de standaard (SET_LOOK=glans, Cycles): dezelfde
sets en kleuren, maar als glimmend vinyl-speelgoed met een coatlaag, AgX-kleuren
en een oranje en blauw randlicht op het hoofdpersonage. SET_LOOK=toon geeft de
oude look van video 1 terug. Alles hieronder over de toon-shading geldt alleen
voor SET_LOOK=toon.

Eén plek voor de look: toon-shading met drie lichtbanden, dunne donkere
contourlijnen (inverted hull), matte verzadigde kleuren, afgeronde randen en
een lichte waas op afstand. Render met EEVEE (Shader to RGB werkt niet in Cycles).

Elke set-script doet:
    from lib import toon as T
    T.new_scene("pretpark", mood=T.MOODS["zonsondergang"])
    ... bouwen met T.box / T.cyl / props ...
    T.finish(out_dir, "pretpark_zonsondergang", cameras=[...])
"""
import bpy
import bmesh
import math
import os
from mathutils import Vector, Matrix, Euler

# ---------------------------------------------------------------------------
# Lichtstemmingen. Elke set kiest er één; de toon-shader, de lucht, de zon en
# de waas lezen allemaal hieruit. Kleuren zijn lineair RGB.
# ---------------------------------------------------------------------------
MOODS = {
    "dag": dict(
        sky_top=(0.18, 0.42, 0.95), sky_horizon=(0.62, 0.80, 1.0), ground_glow=(0.55, 0.62, 0.70),
        sun_color=(1.0, 0.95, 0.86), sun_strength=1.0, sun_rot=(52, 0, 35),
        ambient=(0.42, 0.46, 0.56), shadow_tint=(0.50, 0.52, 0.74), lit_tint=(1.0, 0.98, 0.94),
        fog_color=(0.66, 0.80, 1.0), fog_start=70.0, fog_end=650.0, fog_max=0.45,
        sun_disc=None, bloom=0.0,
    ),
    "zonsondergang": dict(
        sky_top=(0.20, 0.10, 0.42), sky_horizon=(1.0, 0.42, 0.30), ground_glow=(0.9, 0.45, 0.45),
        sun_color=(1.0, 0.62, 0.38), sun_strength=1.0, sun_rot=(80, 0, -60),
        ambient=(0.42, 0.30, 0.48), shadow_tint=(0.56, 0.40, 0.58), lit_tint=(1.0, 0.82, 0.66),
        fog_color=(0.95, 0.52, 0.48), fog_start=60.0, fog_end=600.0, fog_max=0.45,
        sun_disc=dict(color=(1.0, 0.82, 0.45), size=7.0, dir=(-60, 6)), bloom=0.7,
    ),
    "ochtend": dict(
        sky_top=(0.35, 0.55, 0.95), sky_horizon=(1.0, 0.78, 0.55), ground_glow=(0.8, 0.7, 0.6),
        sun_color=(1.0, 0.78, 0.50), sun_strength=1.1, sun_rot=(70, 0, 110),
        ambient=(0.40, 0.38, 0.44), shadow_tint=(0.48, 0.42, 0.62), lit_tint=(1.0, 0.88, 0.70),
        fog_color=(1.0, 0.82, 0.65), fog_start=30.0, fog_end=400.0, fog_max=0.5,
        sun_disc=None, bloom=0.4,
    ),
    "nacht": dict(
        sky_top=(0.010, 0.014, 0.05), sky_horizon=(0.05, 0.07, 0.17), ground_glow=(0.04, 0.05, 0.1),
        sun_color=(0.55, 0.65, 1.0), sun_strength=0.35, sun_rot=(55, 0, 140),
        ambient=(0.10, 0.12, 0.22), shadow_tint=(0.22, 0.25, 0.50), lit_tint=(0.80, 0.86, 1.0),
        fog_color=(0.05, 0.07, 0.16), fog_start=20.0, fog_end=300.0, fog_max=0.7,
        sun_disc=None, bloom=0.9,
    ),
    "bewolkt": dict(
        sky_top=(0.42, 0.46, 0.50), sky_horizon=(0.68, 0.70, 0.70), ground_glow=(0.45, 0.48, 0.45),
        sun_color=(0.92, 0.95, 1.0), sun_strength=0.45, sun_rot=(40, 0, 30),
        ambient=(0.38, 0.42, 0.42), shadow_tint=(0.50, 0.56, 0.58), lit_tint=(0.92, 0.95, 0.94),
        fog_color=(0.62, 0.65, 0.65), fog_start=30.0, fog_end=300.0, fog_max=0.6,
        sun_disc=None, bloom=0.0,
    ),
    "avond": dict(
        sky_top=(0.06, 0.08, 0.28), sky_horizon=(0.45, 0.30, 0.55), ground_glow=(0.2, 0.15, 0.3),
        sun_color=(0.70, 0.62, 1.0), sun_strength=0.30, sun_rot=(70, 0, -80),
        ambient=(0.16, 0.16, 0.30), shadow_tint=(0.28, 0.28, 0.55), lit_tint=(0.85, 0.82, 1.0),
        fog_color=(0.25, 0.22, 0.42), fog_start=30.0, fog_end=300.0, fog_max=0.6,
        sun_disc=None, bloom=0.8,
    ),
    "binnen": dict(
        sky_top=(0.55, 0.70, 0.95), sky_horizon=(0.85, 0.92, 1.0), ground_glow=(0.7, 0.7, 0.7),
        sun_color=(1.0, 0.97, 0.92), sun_strength=0.6, sun_rot=(50, 0, 30),
        ambient=(0.55, 0.55, 0.60), shadow_tint=(0.55, 0.55, 0.75), lit_tint=(1.0, 0.98, 0.95),
        fog_color=(0.8, 0.85, 0.95), fog_start=60.0, fog_end=400.0, fog_max=0.0,
        sun_disc=None, bloom=0.3,
    ),
}

OUTLINE_COLOR = (0.025, 0.018, 0.035)
LOOK = os.environ.get("SET_LOOK", "glans")
GLANS = LOOK == "glans"
# materialen met deze woorden in de naam worden in de glans-look metaal
METAL_WORDS = ("metaal", "rvs", "chroom", "staal", "kraan", "zilver", "goud")
_mood = None
_mats = {}


# ---------------------------------------------------------------------------
# Scène
# ---------------------------------------------------------------------------
def new_scene(name, mood, res=(1920, 1080), samples=16):
    global _mood
    _mood = dict(mood)
    _mats.clear()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.name = name
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = False
    if GLANS:
        sc.render.engine = "CYCLES"
        sc.cycles.device = "GPU" if os.environ.get("SET_GPU") == "1" else "CPU"
        sc.cycles.samples = int(os.environ.get("SET_SAMPLES", 64))
        sc.cycles.use_denoising = True
        sc.cycles.max_bounces = 6
        sc.cycles.diffuse_bounces = 3
        sc.cycles.glossy_bounces = 3
        sc.cycles.transparent_max_bounces = 16
        sc.cycles.sample_clamp_indirect = 8.0
        sc.view_settings.view_transform = "AgX"
        sc.view_settings.look = "AgX - Punchy"
        sc.view_settings.exposure = mood.get("exposure", -0.2)
    else:
        sc.render.engine = "BLENDER_EEVEE"
        sc.eevee.taa_render_samples = int(os.environ.get("SET_SAMPLES", samples))
        sc.eevee.use_shadows = True
        sc.eevee.shadow_ray_count = 2
        sc.eevee.shadow_step_count = 6
        sc.view_settings.view_transform = "Standard"
        sc.view_settings.look = "None"
    sc.render.image_settings.file_format = "PNG"
    sc.unit_settings.system = "METRIC"
    _toon_group()
    _outline_mat()
    _world()
    _sun()
    if mood.get("bloom"):
        _compositor(mood["bloom"])
    return sc


def collection(name, parent=None):
    c = bpy.data.collections.new(name)
    (parent or bpy.context.scene.collection).children.link(c)
    return c


_active_coll = None


def use_collection(c):
    """Nieuwe objecten komen in deze collectie terecht."""
    global _active_coll
    _active_coll = c


def _link(obj):
    (_active_coll or bpy.context.scene.collection).objects.link(obj)
    return obj


# ---------------------------------------------------------------------------
# Materialen
# ---------------------------------------------------------------------------
def _glans_group():
    """Glans-versie van 'ToonLicht': kleur -> iets voller -> Principled met coat -> waas.
    Zelfde naam en ingang 'Kleur', zodat elk set-script ongewijzigd werkt."""
    m = _mood
    ng = bpy.data.node_groups.new("ToonLicht", "ShaderNodeTree")
    ng.interface.new_socket("Kleur", in_out="INPUT", socket_type="NodeSocketColor")
    r = ng.interface.new_socket("Ruwheid", in_out="INPUT", socket_type="NodeSocketFloat")
    r.default_value = 0.38
    mt = ng.interface.new_socket("Metaal", in_out="INPUT", socket_type="NodeSocketFloat")
    mt.default_value = 0.0
    ng.interface.new_socket("Licht", in_out="OUTPUT", socket_type="NodeSocketShader")
    N, L = ng.nodes, ng.links
    gi = N.new("NodeGroupInput")
    go = N.new("NodeGroupOutput")
    hs = N.new("ShaderNodeHueSaturation")
    hs.inputs["Saturation"].default_value = 1.2
    b = N.new("ShaderNodeBsdfPrincipled")
    b.name = b.label = "Glans"
    b.inputs["Coat Weight"].default_value = 0.25
    b.inputs["Coat Roughness"].default_value = 0.18
    b.inputs["Specular IOR Level"].default_value = 0.55
    L.new(gi.outputs["Kleur"], hs.inputs["Color"])
    L.new(hs.outputs["Color"], b.inputs["Base Color"])
    L.new(gi.outputs["Ruwheid"], b.inputs["Roughness"])
    L.new(gi.outputs["Metaal"], b.inputs["Metallic"])
    # waas op afstand, net als in de toon-look
    cam = N.new("ShaderNodeCameraData")
    mr = N.new("ShaderNodeMapRange")
    mr.name = mr.label = "Waas afstand"
    mr.inputs["From Min"].default_value = m["fog_start"]
    mr.inputs["From Max"].default_value = m["fog_end"]
    mr.inputs["To Max"].default_value = m["fog_max"]
    em = N.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*m["fog_color"], 1)
    mix = N.new("ShaderNodeMixShader")
    L.new(cam.outputs["View Distance"], mr.inputs["Value"])
    L.new(mr.outputs["Result"], mix.inputs[0])
    L.new(b.outputs[0], mix.inputs[1])
    L.new(em.outputs[0], mix.inputs[2])
    L.new(mix.outputs[0], go.inputs["Licht"])
    return ng


def _toon_group():
    """Node group 'ToonLicht': diffuse licht -> 3 banden -> x basiskleur -> waas."""
    if GLANS:
        return _glans_group()
    m = _mood
    ng = bpy.data.node_groups.new("ToonLicht", "ShaderNodeTree")
    ng.interface.new_socket("Kleur", in_out="INPUT", socket_type="NodeSocketColor")
    ng.interface.new_socket("Licht", in_out="OUTPUT", socket_type="NodeSocketShader")
    N, L = ng.nodes, ng.links
    gi = N.new("NodeGroupInput")
    go = N.new("NodeGroupOutput")
    dif = N.new("ShaderNodeBsdfDiffuse")
    s2r = N.new("ShaderNodeShaderToRGB")
    ramp = N.new("ShaderNodeValToRGB")
    ramp.name = ramp.label = "Lichtbanden"
    cr = ramp.color_ramp
    cr.interpolation = "LINEAR"
    sh, li = m["shadow_tint"], m["lit_tint"]
    mid = tuple(sh[i] * 0.35 + li[i] * 0.65 for i in range(3))
    stops = [(0.0, sh), (0.28, sh), (0.36, mid), (0.60, mid), (0.68, li), (1.0, li)]
    cr.elements[0].position, cr.elements[0].color = stops[0][0], (*stops[0][1], 1)
    cr.elements[1].position, cr.elements[1].color = stops[-1][0], (*stops[-1][1], 1)
    for p, c in stops[1:-1]:
        e = cr.elements.new(p)
        e.color = (*c, 1)
    mul = N.new("ShaderNodeMix")
    mul.data_type = "RGBA"
    mul.blend_type = "MULTIPLY"
    mul.inputs["Factor"].default_value = 1.0
    # waas op afstand
    cam = N.new("ShaderNodeCameraData")
    mr = N.new("ShaderNodeMapRange")
    mr.name = mr.label = "Waas afstand"
    mr.inputs["From Min"].default_value = m["fog_start"]
    mr.inputs["From Max"].default_value = m["fog_end"]
    mr.inputs["To Max"].default_value = m["fog_max"]
    fog = N.new("ShaderNodeMix")
    fog.data_type = "RGBA"
    fog.inputs["B"].default_value = (*m["fog_color"], 1)
    em = N.new("ShaderNodeEmission")
    L.new(dif.outputs[0], s2r.inputs[0])
    L.new(s2r.outputs["Color"], ramp.inputs["Fac"])
    L.new(ramp.outputs["Color"], mul.inputs["A"])
    L.new(gi.outputs["Kleur"], mul.inputs["B"])
    L.new(cam.outputs["View Distance"], mr.inputs["Value"])
    L.new(mr.outputs["Result"], fog.inputs["Factor"])
    L.new(mul.outputs["Result"], fog.inputs["A"])
    L.new(fog.outputs["Result"], em.inputs["Color"])
    L.new(em.outputs[0], go.inputs["Licht"])
    return ng


def toon(name, color):
    """Mat toon-materiaal in één kleur. Zelfde naam = zelfde materiaal."""
    key = "toon_" + name
    if key in _mats:
        return _mats[key]
    mt = bpy.data.materials.new(name)
    mt.use_nodes = True
    N = mt.node_tree.nodes
    N.clear()
    out = N.new("ShaderNodeOutputMaterial")
    g = N.new("ShaderNodeGroup")
    g.node_tree = bpy.data.node_groups["ToonLicht"]
    g.inputs["Kleur"].default_value = (*color, 1)
    if GLANS and any(w in name.lower() for w in METAL_WORDS):
        g.inputs["Ruwheid"].default_value = 0.18
        g.inputs["Metaal"].default_value = 1.0
    mt.node_tree.links.new(g.outputs[0], out.inputs["Surface"])
    mt.diffuse_color = (*color, 1)
    _mats[key] = mt
    return mt


def glow(name, color, strength=3.0):
    """Lichtgevend materiaal (lampjes, schermen, neon)."""
    key = "glow_" + name
    if key in _mats:
        return _mats[key]
    mt = bpy.data.materials.new(name)
    mt.use_nodes = True
    N = mt.node_tree.nodes
    N.clear()
    out = N.new("ShaderNodeOutputMaterial")
    em = N.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*color, 1)
    em.inputs["Strength"].default_value = strength
    mt.node_tree.links.new(em.outputs[0], out.inputs["Surface"])
    mt.diffuse_color = (*color, 1)
    _mats[key] = mt
    return mt


def glass(name="glas", color=(0.6, 0.8, 0.95), alpha=0.35):
    """Eenvoudig toon-glas: lichte kleur, half doorzichtig."""
    key = "glass_" + name
    if key in _mats:
        return _mats[key]
    mt = bpy.data.materials.new(name)
    mt.use_nodes = True
    N = mt.node_tree.nodes
    N.clear()
    out = N.new("ShaderNodeOutputMaterial")
    g = N.new("ShaderNodeGroup")
    g.node_tree = bpy.data.node_groups["ToonLicht"]
    g.inputs["Kleur"].default_value = (*color, 1)
    tr = N.new("ShaderNodeBsdfTransparent")
    mix = N.new("ShaderNodeMixShader")
    mix.inputs[0].default_value = alpha
    mt.node_tree.links.new(tr.outputs[0], mix.inputs[1])
    mt.node_tree.links.new(g.outputs[0], mix.inputs[2])
    mt.node_tree.links.new(mix.outputs[0], out.inputs["Surface"])
    mt.surface_render_method = "BLENDED"
    mt.diffuse_color = (*color, alpha)
    _mats[key] = mt
    return mt


def _outline_mat():
    mt = bpy.data.materials.new("Contour")
    mt.use_nodes = True
    N = mt.node_tree.nodes
    N.clear()
    out = N.new("ShaderNodeOutputMaterial")
    em = N.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*OUTLINE_COLOR, 1)
    mt.node_tree.links.new(em.outputs[0], out.inputs["Surface"])
    mt.use_backface_culling = True
    mt.diffuse_color = (*OUTLINE_COLOR, 1)
    _mats["outline"] = mt
    return mt


def outline(obj, width=0.012):
    """Inverted-hull contourlijn. width in meters. Niet in de glans-look."""
    if GLANS:
        return obj
    if obj.type not in ("MESH", "CURVE", "FONT") or width <= 0:
        return obj
    mats = obj.data.materials
    if _mats["outline"].name not in [m.name for m in mats if m]:
        mats.append(_mats["outline"])
    mod = obj.modifiers.new("Contour", "SOLIDIFY")
    mod.thickness = width
    mod.offset = 1.0
    mod.use_flip_normals = True
    mod.use_rim = False
    mod.material_offset = len(mats) - 1
    mod.material_offset_rim = len(mats) - 1
    return obj


# ---------------------------------------------------------------------------
# Wereld, zon, compositor
# ---------------------------------------------------------------------------
def _world():
    m = _mood
    w = bpy.data.worlds.new("Lucht")
    bpy.context.scene.world = w
    w.use_nodes = True
    N, L = w.node_tree.nodes, w.node_tree.links
    N.clear()
    out = N.new("ShaderNodeOutputWorld")
    tc = N.new("ShaderNodeTexCoord")
    sep = N.new("ShaderNodeSeparateXYZ")
    ramp = N.new("ShaderNodeValToRGB")
    ramp.label = "Luchtverloop"
    cr = ramp.color_ramp
    cr.elements[0].position, cr.elements[0].color = 0.0, (*m["ground_glow"], 1)
    cr.elements[1].position, cr.elements[1].color = 1.0, (*m["sky_top"], 1)
    e = cr.elements.new(0.5)
    e.color = (*m["sky_horizon"], 1)
    e2 = cr.elements.new(0.62)
    e2.color = tuple(m["sky_horizon"][i] * 0.5 + m["sky_top"][i] * 0.5 for i in range(3)) + (1,)
    mr = N.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = -1
    mr.inputs["From Max"].default_value = 1
    L.new(tc.outputs["Generated"], sep.inputs[0])
    L.new(sep.outputs["Z"], mr.inputs["Value"])
    L.new(mr.outputs["Result"], ramp.inputs["Fac"])
    sky_col = ramp.outputs["Color"]
    if m.get("sun_disc"):
        d = m["sun_disc"]
        az, el = math.radians(d["dir"][0]), math.radians(d["dir"][1])
        dvec = Vector((math.cos(el) * math.sin(az), -math.cos(el) * math.cos(az), math.sin(el)))
        dot = N.new("ShaderNodeVectorMath")
        dot.operation = "DOT_PRODUCT"
        dot.inputs[1].default_value = dvec
        L.new(tc.outputs["Generated"], dot.inputs[0])
        r1 = N.new("ShaderNodeMapRange")
        cosr = math.cos(math.radians(d["size"] * 0.5))
        r1.inputs["From Min"].default_value = cosr - 0.0004
        r1.inputs["From Max"].default_value = cosr
        L.new(dot.outputs["Value"], r1.inputs["Value"])
        halo = N.new("ShaderNodeMapRange")
        halo.inputs["From Min"].default_value = math.cos(math.radians(d["size"] * 4))
        halo.inputs["From Max"].default_value = 1.0
        halo.inputs["To Max"].default_value = 0.45
        L.new(dot.outputs["Value"], halo.inputs["Value"])
        mh = N.new("ShaderNodeMix")
        mh.data_type = "RGBA"
        mh.inputs["B"].default_value = (*d["color"], 1)
        L.new(halo.outputs["Result"], mh.inputs["Factor"])
        L.new(sky_col, mh.inputs["A"])
        md = N.new("ShaderNodeMix")
        md.data_type = "RGBA"
        md.inputs["B"].default_value = (*(c * 1.6 for c in d["color"]), 1)
        L.new(r1.outputs["Result"], md.inputs["Factor"])
        L.new(mh.outputs["Result"], md.inputs["A"])
        sky_col = md.outputs["Result"]
    bg_cam = N.new("ShaderNodeBackground")
    L.new(sky_col, bg_cam.inputs["Color"])
    bg_amb = N.new("ShaderNodeBackground")
    bg_amb.inputs["Color"].default_value = (*m["ambient"], 1)
    lp = N.new("ShaderNodeLightPath")
    mix = N.new("ShaderNodeMixShader")
    L.new(lp.outputs["Is Camera Ray"], mix.inputs[0])
    L.new(bg_amb.outputs[0], mix.inputs[1])
    L.new(bg_cam.outputs[0], mix.inputs[2])
    L.new(mix.outputs[0], out.inputs["Surface"])


def _sun():
    m = _mood
    ld = bpy.data.lights.new("Zon", "SUN")
    ld.color = m["sun_color"]
    ld.energy = m["sun_strength"] * math.pi  # 1.0 = wit vlak precies "vol" belicht
    ld.angle = math.radians(2.5 if GLANS else 0.6)
    o = bpy.data.objects.new("Zon", ld)
    o.rotation_euler = Euler([math.radians(a) for a in m["sun_rot"]])
    bpy.context.scene.collection.objects.link(o)
    return o


def point_light(name, loc, color=(1, 0.8, 0.55), energy=200, radius=0.1, shadow=True):
    ld = bpy.data.lights.new(name, "POINT")
    ld.color, ld.energy, ld.shadow_soft_size = color, energy, radius
    ld.use_shadow = shadow
    o = bpy.data.objects.new(name, ld)
    o.location = loc
    return _link(o)


def spot_light(name, loc, target, color=(1, 1, 1), energy=500, angle=45, blend=0.3):
    ld = bpy.data.lights.new(name, "SPOT")
    ld.color, ld.energy = color, energy
    ld.spot_size, ld.spot_blend = math.radians(angle), blend
    o = bpy.data.objects.new(name, ld)
    o.location = loc
    _aim(o, target)
    return _link(o)


def area_light(name, loc, target, size=(2, 2), color=(1, 1, 1), energy=300):
    ld = bpy.data.lights.new(name, "AREA")
    ld.shape = "RECTANGLE"
    ld.size, ld.size_y = size
    ld.color, ld.energy = color, energy
    o = bpy.data.objects.new(name, ld)
    o.location = loc
    _aim(o, target)
    return _link(o)


def _compositor(strength):
    sc = bpy.context.scene
    ng = bpy.data.node_groups.new("Gloed", "CompositorNodeTree")
    ng.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    rl = ng.nodes.new("CompositorNodeRLayers")
    gl = ng.nodes.new("CompositorNodeGlare")
    gl.inputs["Type"].default_value = "Bloom"
    gl.inputs["Threshold"].default_value = 1.05
    gl.inputs["Strength"].default_value = strength
    gl.inputs["Size"].default_value = 0.6
    go = ng.nodes.new("NodeGroupOutput")
    ng.links.new(rl.outputs["Image"], gl.inputs["Image"])
    ng.links.new(gl.outputs["Image"], go.inputs[0])
    sc.compositing_node_group = ng
    sc.render.use_compositing = True


# ---------------------------------------------------------------------------
# Vormen. Alles in meters; loc = middelpunt onderkant tenzij anders vermeld.
# ---------------------------------------------------------------------------
def _obj(name, me, mat, loc, rot, ol, bevel=0.0, smooth=False):
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    o = bpy.data.objects.new(name, me)
    if mat:
        me.materials.append(mat)
    o.location = loc
    if rot:
        o.rotation_euler = Euler([math.radians(a) for a in rot])
    _link(o)
    if bevel > 0:
        _bevel(me, bevel)
    if ol:
        outline(o, ol)
    return o


def _bevel(me, width):
    """Afgeronde randen direct in de mesh (sneller dan een modifier en blijft bij samenvoegen)."""
    bm = bmesh.new()
    bm.from_mesh(me)
    edges = [e for e in bm.edges if e.is_manifold and e.calc_face_angle(0) > math.radians(35)]
    if edges:
        bmesh.ops.bevel(bm, geom=edges, offset=width, offset_type="OFFSET", segments=2, profile=0.5,
                        affect="EDGES", clamp_overlap=True)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = False


def box(name, loc, size, mat, rot=None, bevel=0.02, ol=0.012, base=True):
    """Kubus; loc = midden onderkant (base=True) of midden (base=False)."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    sx, sy, sz = size
    for v in bm.verts:
        v.co = Vector((v.co.x * sx, v.co.y * sy, v.co.z * sz + (sz / 2 if base else 0)))
    bm.to_mesh(me)
    bm.free()
    bv = min(bevel, min(size) * 0.3)
    return _obj(name, me, mat, loc, rot, ol, bevel=bv)


def cyl(name, loc, r, h, mat, rot=None, seg=24, ol=0.012, r2=None, bevel=0.0, cap=True):
    """Cilinder (of kegel met r2) staand op loc."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=cap, cap_tris=False, segments=seg,
                          radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts:
        v.co.z += h / 2
    bm.to_mesh(me)
    bm.free()
    o = _obj(name, me, mat, loc, rot, ol, bevel=bevel)
    for p in me.polygons:
        p.use_smooth = len(p.vertices) == 4
    return o


def sphere(name, loc, r, mat, scale=(1, 1, 1), seg=24, ol=0.012, rot=None):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=max(8, seg // 2), radius=r)
    for v in bm.verts:
        v.co = Vector((v.co.x * scale[0], v.co.y * scale[1], v.co.z * scale[2]))
    bm.to_mesh(me)
    bm.free()
    return _obj(name, me, mat, loc, rot, ol, smooth=True)


def torus(name, loc, R, r, mat, rot=None, seg=48, seg2=12, ol=0.012):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    verts = []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        ring = []
        for j in range(seg2):
            b = 2 * math.pi * j / seg2
            x = (R + r * math.cos(b)) * math.cos(a)
            y = (R + r * math.cos(b)) * math.sin(a)
            z = r * math.sin(b)
            ring.append(bm.verts.new((x, y, z)))
        verts.append(ring)
    for i in range(seg):
        for j in range(seg2):
            a, b = verts[i][j], verts[(i + 1) % seg][j]
            c, d = verts[(i + 1) % seg][(j + 1) % seg2], verts[i][(j + 1) % seg2]
            bm.faces.new((a, b, c, d))
    bm.to_mesh(me)
    bm.free()
    return _obj(name, me, mat, loc, rot, ol, smooth=True)


def tube(name, pts, r, mat, ol=0.0, closed=False, res=6):
    """Buis langs een lijst punten (poly-curve met bevel)."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = r
    cu.bevel_resolution = 1 if res <= 6 else 2
    cu.use_fill_caps = True
    sp = cu.splines.new("POLY")
    sp.points.add(len(pts) - 1)
    for p, q in zip(sp.points, pts):
        p.co = (*q, 1)
    sp.use_cyclic_u = closed
    o = bpy.data.objects.new(name, cu)
    cu.materials.append(mat)
    _link(o)
    if ol:
        o = to_mesh(o)
        outline(o, ol)
    return o


def to_mesh(o):
    """Curve -> mesh (zodat contourlijnen werken)."""
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(o.evaluated_get(dg))
    n = bpy.data.objects.new(o.name, me)
    n.matrix_world = o.matrix_world
    for c in o.users_collection:
        c.objects.link(n)
    bpy.data.objects.remove(o)
    return n


def plane(name, loc, size, mat, rot=None, ol=0.0):
    me = bpy.data.meshes.new(name)
    sx, sy = size
    me.from_pydata([(-sx / 2, -sy / 2, 0), (sx / 2, -sy / 2, 0), (sx / 2, sy / 2, 0), (-sx / 2, sy / 2, 0)],
                   [], [(0, 1, 2, 3)])
    return _obj(name, me, mat, loc, rot, ol)


def text(name, body, loc, size, mat, rot=(90, 0, 0), extrude=0.05, align="CENTER", ol=0.0):
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = body
    cu.size = size
    cu.extrude = extrude
    cu.align_x = align
    cu.align_y = "BOTTOM"
    cu.materials.append(mat)
    o = bpy.data.objects.new(name, cu)
    o.location = loc
    o.rotation_euler = Euler([math.radians(a) for a in rot])
    _link(o)
    if ol:
        o = to_mesh(o)
        outline(o, ol)
    return o


def mesh_from(name, verts, faces, mat, ol=0.0, smooth=False, loc=(0, 0, 0)):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.validate()
    return _obj(name, me, mat, loc, None, ol, smooth=smooth)


def merge(name, objs, ol=0.012):
    """Voeg objecten samen tot één object (sneller en overzichtelijker)."""
    objs = [o for o in objs if o]
    if len(objs) == 1:
        o = objs[0]
        o.name = name
        if o.type == "MESH" and o.parent is None:
            o.data.transform(o.matrix_basis)
            o.matrix_basis = Matrix.Identity(4)
        if ol and not any(m.name == "Contour" for m in o.modifiers):
            outline(o, ol)
        return o
    if not objs:
        return None
    for o in objs:
        _apply_mods(o)
    ctx = bpy.context
    for o in ctx.selected_objects:
        o.select_set(False)
    for o in objs:
        o.select_set(True)
    ctx.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    o = objs[0]
    o.name = name
    # nulpunt naar de wereldoorsprong, zodat o.location = ... de hele prop netjes verplaatst
    o.data.transform(o.matrix_basis)
    o.matrix_basis = Matrix.Identity(4)
    ms = o.data.materials
    oi = [i for i, m in enumerate(ms) if m and m.name == "Contour"]
    if oi:
        # contour-slot achteraan houden: faces die er (door de join) op staan krijgen slot 0
        for p in o.data.polygons:
            if p.material_index in oi:
                p.material_index = 0
    if ol:
        if oi:
            ms.pop(index=oi[0])
        outline(o, ol)
    return o


def _apply_mods(o):
    """Bevel toepassen; contour-modifier eraf (wordt na merge opnieuw gezet)."""
    if o.type == "CURVE" or o.type == "FONT":
        return
    has_ol = any(m.type == "SOLIDIFY" and m.name == "Contour" for m in o.modifiers)
    for m in list(o.modifiers):
        if m.name == "Contour":
            o.modifiers.remove(m)
    if o.modifiers:
        me = bpy.data.meshes.new_from_object(o.evaluated_get(bpy.context.evaluated_depsgraph_get()))
        for m in list(o.modifiers):
            o.modifiers.remove(m)
        o.data = me
    o["had_outline"] = has_ol


def instance(o, loc, rot=None, scale=None, name=None):
    """Gekoppelde kopie (deelt mesh): goedkoop voor herhaalde props."""
    n = o.copy()
    if name:
        n.name = name
    n.location = loc
    if rot is not None:
        n.rotation_euler = Euler([math.radians(a) for a in rot])
    if scale is not None:
        n.scale = scale if hasattr(scale, "__len__") else (scale,) * 3
    _link(n)
    return n


def group(name, objs, loc=(0, 0, 0), rot=None):
    """Lege 'ouder' zodat een prop als één geheel te verplaatsen is."""
    e = bpy.data.objects.new(name, None)
    e.empty_display_size = 0.3
    _link(e)
    for o in objs:
        if o and o.parent is None:
            o.parent = e
    e.location = loc
    if rot:
        e.rotation_euler = Euler([math.radians(a) for a in rot])
    return e


# ---------------------------------------------------------------------------
# Camera's en hoofdpersonage
# ---------------------------------------------------------------------------
def _aim(o, target):
    d = Vector(target) - o.location
    o.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def camera(name, loc, target, lens=35, dof=None):
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    cd.clip_start, cd.clip_end = 0.05, 3000
    if dof:
        cd.dof.use_dof = True
        cd.dof.focus_distance = (Vector(target) - Vector(loc)).length
        cd.dof.aperture_fstop = dof
    o = bpy.data.objects.new(name, cd)
    o.location = loc
    _aim(o, target)
    bpy.context.scene.collection.objects.link(o)
    return o


CHARACTER = "/mnt/project-files/hoofdpersonage/hoofdpersonage.glb"


def character(loc, rot_z=0.0, coll_name="Hoofdpersonage (schaal)"):
    """Importeert het hoofdpersonage met toon-materialen, als schaal- en stijlreferentie."""
    if not os.path.exists(CHARACTER):
        return None
    c = collection(coll_name)
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=CHARACTER)
    new = [o for o in bpy.data.objects if o not in before]
    root = bpy.data.objects.new("Hoofdpersonage", None)
    c.objects.link(root)
    for o in new:
        for uc in list(o.users_collection):
            uc.objects.unlink(o)
        c.objects.link(o)
        if o.parent is None:
            o.parent = root
        if o.type == "MESH" and GLANS:
            for slot in o.material_slots:
                if slot.material and not slot.material.get("glans"):
                    _glossify(slot.material)
        elif o.type == "MESH":
            for i, slot in enumerate(o.material_slots):
                ms = slot.material
                if ms and not ms.name.startswith("pers_"):
                    col = (0.8, 0.8, 0.8)
                    if ms.node_tree:
                        b = ms.node_tree.nodes.get("Principled BSDF")
                        if b:
                            col = tuple(b.inputs["Base Color"].default_value)[:3]
                    slot.material = toon("pers_" + ms.name, col)
            outline(o, 0.006)
    root.location = loc
    root.rotation_euler = (0, 0, math.radians(rot_z))
    root["held"] = True
    return root


def _glossify(mat):
    """Glans-materiaal voor de figuren, zelfde regels als cast/render_glans.py."""
    mat["glans"] = True
    b = mat.node_tree.nodes.get("Principled BSDF") if mat.use_nodes else None
    if b is None:
        return
    col = b.inputs["Base Color"].default_value
    if b.inputs["Metallic"].default_value > 0.5:
        b.inputs["Roughness"].default_value = 0.18
        return
    r, g, bb = col[:3]
    skin = r > g > bb and r > 0.15 and (r - bb) > 0.12 and 0.35 < g / max(r, 1e-4) < 0.75
    if skin:
        b.inputs["Roughness"].default_value = 0.42
        b.inputs["Subsurface Weight"].default_value = 0.25
        b.inputs["Subsurface Radius"].default_value = (0.9, 0.35, 0.2)
        b.inputs["Subsurface Scale"].default_value = 0.03
        b.inputs["Coat Weight"].default_value = 0.15
        b.inputs["Coat Roughness"].default_value = 0.3
        return
    b.inputs["Roughness"].default_value = 0.38
    b.inputs["Coat Weight"].default_value = 0.25
    b.inputs["Coat Roughness"].default_value = 0.18
    b.inputs["Specular IOR Level"].default_value = 0.55
    m = (r + g + bb) / 3
    b.inputs["Base Color"].default_value = (max(0, m + (r - m) * 1.2), max(0, m + (g - m) * 1.2),
                                            max(0, m + (bb - m) * 1.2), 1)


def _rim_lights(cam):
    """Glans-look: oranje en blauw randlicht schuin achter elk hoofdpersonage, gezien
    vanuit deze camera. Ze vallen alleen op de figuur (light linking)."""
    for o in [o for o in bpy.data.objects if o.name.startswith("Randlicht_")]:
        bpy.data.objects.remove(o)
    for root in [o for o in bpy.data.objects if o.get("held")]:
        c = root.users_collection[0]
        p = root.matrix_world.translation + Vector((0, 0, 1.3))
        d = cam.matrix_world.translation - p
        d.z = 0
        if d.length < 1e-3:
            continue
        d.normalize()
        side = Vector((-d.y, d.x, 0))
        for tag, s_, col, e in (("oranje", -1, (1.0, 0.33, 0.045), 700), ("blauw", 1, (0.047, 0.24, 1.0), 800)):
            ld = bpy.data.lights.new(f"Randlicht_{tag}", "AREA")
            ld.shape, ld.size, ld.energy, ld.color = "DISK", 0.6, e, col
            lo = bpy.data.objects.new(f"Randlicht_{tag}_{root.name}", ld)
            lo.location = p - d * 1.6 + side * s_ * 1.4 + Vector((0, 0, 0.6))
            _aim(lo, p)
            lo.visible_camera = False
            lo.light_linking.receiver_collection = c
            bpy.context.scene.collection.objects.link(lo)


# ---------------------------------------------------------------------------
# Opslaan en renderen
# ---------------------------------------------------------------------------
def finish(out_dir, name, cameras, percent=100, render=True):
    os.makedirs(out_dir, exist_ok=True)
    sc = bpy.context.scene
    sc.render.resolution_percentage = percent
    render = render and os.environ.get("SET_RENDER", "1") == "1"
    if GLANS:
        for o in bpy.data.objects:
            if o.type == "LIGHT":
                o.visible_camera = False
    if cameras:
        sc.camera = cameras[0]
        if GLANS:
            _rim_lights(cameras[0])
    blend = os.path.join(out_dir, name + ".blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend, compress=True)
    outs = []
    sc.render.resolution_percentage = int(os.environ.get("SET_PCT", percent))
    if render:
        for cam in cameras:
            sc.camera = cam
            if GLANS:
                _rim_lights(cam)
            sc.render.filepath = os.path.join(out_dir, f"{name}__{cam.name}.png")
            bpy.ops.render.render(write_still=True)
            outs.append(sc.render.filepath)
        sc.camera = cameras[0]
        if GLANS:
            _rim_lights(cameras[0])
        sc.render.resolution_percentage = percent  # .blend altijd op de standaardresolutie
        bpy.ops.wm.save_as_mainfile(filepath=blend, compress=True)
    return blend, outs


# ---------------------------------------------------------------------------
# Patronen (tegels, planken, schaakbord) in toon-stijl. Werken op muren én
# vloeren via wereldcoördinaten, dus ook na samenvoegen/roteren.
# ---------------------------------------------------------------------------
def pattern(name, c1, c2, grout=None, size=(0.3, 0.3), kind="tegels", mortar=0.04, offset=0.0):
    key = "pat_" + name
    if key in _mats:
        return _mats[key]
    mt = bpy.data.materials.new(name)
    mt.use_nodes = True
    N, L = mt.node_tree.nodes, mt.node_tree.links
    N.clear()
    out = N.new("ShaderNodeOutputMaterial")
    g = N.new("ShaderNodeGroup")
    g.node_tree = bpy.data.node_groups["ToonLicht"]
    geo = N.new("ShaderNodeNewGeometry")
    sep = N.new("ShaderNodeSeparateXYZ")
    L.new(geo.outputs["Position"], sep.inputs[0])
    nsep = N.new("ShaderNodeSeparateXYZ")
    L.new(geo.outputs["Normal"], nsep.inputs[0])

    def comb(a, b):
        c = N.new("ShaderNodeCombineXYZ")
        L.new(sep.outputs[a], c.inputs[0])
        L.new(sep.outputs[b], c.inputs[1])
        return c.outputs[0]

    def tex(vec):
        if kind == "schaak":
            t = N.new("ShaderNodeTexChecker")
            t.inputs["Color1"].default_value = (*c1, 1)
            t.inputs["Color2"].default_value = (*c2, 1)
            t.inputs["Scale"].default_value = 1.0 / size[0]
            L.new(vec, t.inputs["Vector"])
            return t.outputs["Color"]
        t = N.new("ShaderNodeTexBrick")
        t.offset = offset
        t.offset_frequency = 2
        t.squash = 1.0
        t.inputs["Color1"].default_value = (*c1, 1)
        t.inputs["Color2"].default_value = (*c2, 1)
        t.inputs["Mortar"].default_value = (*(grout or c1), 1)
        t.inputs["Scale"].default_value = 1.0
        t.inputs["Mortar Size"].default_value = mortar if grout else 0.0
        t.inputs["Mortar Smooth"].default_value = 0.0
        t.inputs["Bias"].default_value = 0.0
        t.inputs["Brick Width"].default_value = size[0]
        t.inputs["Row Height"].default_value = size[1]
        L.new(vec, t.inputs["Vector"])
        return t.outputs["Color"]

    floor_c = tex(comb("X", "Y"))
    wall_x = tex(comb("Y", "Z"))   # muren die naar x kijken
    wall_y = tex(comb("X", "Z"))   # muren die naar y kijken
    ax = N.new("ShaderNodeMath")
    ax.operation = "ABSOLUTE"
    L.new(nsep.outputs["X"], ax.inputs[0])
    ay = N.new("ShaderNodeMath")
    ay.operation = "ABSOLUTE"
    L.new(nsep.outputs["Y"], ay.inputs[0])
    az = N.new("ShaderNodeMath")
    az.operation = "ABSOLUTE"
    L.new(nsep.outputs["Z"], az.inputs[0])
    gt = N.new("ShaderNodeMath")
    gt.operation = "GREATER_THAN"
    L.new(ax.outputs[0], gt.inputs[0])
    L.new(ay.outputs[0], gt.inputs[1])
    m1 = N.new("ShaderNodeMix")
    m1.data_type = "RGBA"
    L.new(gt.outputs[0], m1.inputs["Factor"])
    L.new(wall_y, m1.inputs["A"])
    L.new(wall_x, m1.inputs["B"])
    up = N.new("ShaderNodeMath")
    up.operation = "GREATER_THAN"
    up.inputs[1].default_value = 0.6
    L.new(az.outputs[0], up.inputs[0])
    m2 = N.new("ShaderNodeMix")
    m2.data_type = "RGBA"
    L.new(up.outputs[0], m2.inputs["Factor"])
    L.new(m1.outputs["Result"], m2.inputs["A"])
    L.new(floor_c, m2.inputs["B"])
    L.new(m2.outputs["Result"], g.inputs["Kleur"])
    L.new(g.outputs[0], out.inputs["Surface"])
    mt.diffuse_color = (*c1, 1)
    _mats[key] = mt
    return mt


def screen(name, color, strength=2.0, text_=None):
    """Lichtgevend scherm (tv, monitor, scorebord)."""
    return glow(name, color, strength)
