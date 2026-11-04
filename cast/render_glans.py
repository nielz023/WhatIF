"""
Glans-look voor de cast: dezelfde figuren uit cast_video1.blend, maar gerenderd zoals
het kanaallogo: gladde glimmende materialen, zachte huid, warm hoofdlicht en blauw
randlicht op een donkere achtergrond.

Gebruik:
    blender -b -P cast/render_glans.py -- --blend pad/cast_video1.blend --out pad/uitvoer
    (of: python cast/render_glans.py --blend ... --out ...)
Opties: --only mama,papa  --samples 128  --no-overview  --no-closeups  --pct 100
De modellen zelf veranderen niet; alleen materialen, licht en camera.
"""
import bpy
import bmesh
import math
import os
import sys
from mathutils import Vector


def lin(hexcol):
    hexcol = hexcol.lstrip("#")
    out = []
    for k in range(3):
        c = int(hexcol[2 * k:2 * k + 2], 16) / 255.0
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return tuple(out)


def is_skin(mat, col):
    r, g, b = col[:3]
    return r > g > b and r > 0.15 and (r - b) > 0.12 and g / max(r, 1e-4) > 0.35 \
        and g / max(r, 1e-4) < 0.75 and "vloer" not in mat.name


# ---------------------------------------------------------------------------
# Glans 2 (vanaf video 3): stofstructuur, haarlokken en zolen in het materiaal.
# De soort stof staat in de materiaalnaam (build_cast: "<figuur>_<stof>_<kleur>").
# Het hoofdpersonage heeft de oude glb-namen Material_N.
# ---------------------------------------------------------------------------
import re

STOFFEN = ("breisel", "fleece", "katoen", "denim", "leer", "haar", "schoen", "rubber",
           "wol", "nylon", "pyjama", "huid", "pluche", "vacht")
HERO_STOF = {0: "katoen", 1: "schoen", 2: "fleece", 3: "katoen", 4: "huid", 5: "huid", 6: "huid",
             7: "huid"}
DETAIL = os.environ.get("GLANS_DETAIL", "1") == "1"


def stof_of(mat):
    n = mat.name.lower()
    for s in STOFFEN:
        if f"_{s}_" in n or n.startswith(s + "_") or f"_{s}." in n or n.endswith("_" + s):
            return s
    m = re.search(r"material_(\d+)(?!\d)", n)
    if m:
        return HERO_STOF.get(int(m.group(1)))
    return None


def _coord(nt):
    """Rustpositie (blijft op de stof plakken als het skelet beweegt); zonder die
    attribuut valt hij terug op objectcoördinaten."""
    at = nt.nodes.new("ShaderNodeAttribute")
    at.attribute_name = "rest_position"
    tc = nt.nodes.new("ShaderNodeTexCoord")
    # rest_position is (0,0,0) als hij ontbreekt: meng met object-coördinaten
    ln = nt.nodes.new("ShaderNodeVectorMath")
    ln.operation = "LENGTH"
    nt.links.new(at.outputs["Vector"], ln.inputs[0])
    gt = nt.nodes.new("ShaderNodeMath")
    gt.operation = "GREATER_THAN"
    gt.inputs[1].default_value = 1e-6
    nt.links.new(ln.outputs["Value"], gt.inputs[0])
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "VECTOR"
    nt.links.new(gt.outputs[0], mix.inputs["Factor"])
    nt.links.new(tc.outputs["Object"], mix.inputs[4])
    nt.links.new(at.outputs["Vector"], mix.inputs[5])
    return mix.outputs[1]


def _bump(nt, b, height, strength, distance=0.002):
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = strength
    bp.inputs["Distance"].default_value = distance
    nt.links.new(height, bp.inputs["Height"])
    prev = b.inputs["Normal"].links[0].from_node if b.inputs["Normal"].is_linked else None
    if prev is not None and prev.type == "BUMP":
        # meerdere lagen reliëf stapelen
        nt.links.new(prev.outputs["Normal"], bp.inputs["Normal"])
    nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    if "Coat Normal" in b.inputs:
        # coat blijft glad: zo houden de figuren hun vinyl-glans
        pass
    return bp


def _wave(nt, co, scale, axis="X", distort=0.0, detail=2.0, profile="SIN"):
    w = nt.nodes.new("ShaderNodeTexWave")
    w.wave_type = "BANDS"
    w.bands_direction = axis
    w.wave_profile = profile
    w.inputs["Scale"].default_value = scale
    w.inputs["Distortion"].default_value = distort
    w.inputs["Detail"].default_value = detail
    nt.links.new(co, w.inputs["Vector"])
    return w.outputs["Fac"]


def _noise(nt, co, scale, detail=3.0, rough=0.55):
    n = nt.nodes.new("ShaderNodeTexNoise")
    n.inputs["Scale"].default_value = scale
    n.inputs["Detail"].default_value = detail
    n.inputs["Roughness"].default_value = rough
    nt.links.new(co, n.inputs["Vector"])
    return n.outputs["Fac"]


def _mul(nt, a, b_, op="MULTIPLY"):
    m = nt.nodes.new("ShaderNodeMath")
    m.operation = op
    if isinstance(a, (int, float)):
        m.inputs[0].default_value = a
    else:
        nt.links.new(a, m.inputs[0])
    if isinstance(b_, (int, float)):
        m.inputs[1].default_value = b_
    else:
        nt.links.new(b_, m.inputs[1])
    return m.outputs[0]


def _tint(nt, b, fac, amount, lighter=True):
    """Kleurvariatie: basiskleur iets lichter/donkerder waar fac hoog is."""
    col = tuple(b.inputs["Base Color"].default_value)
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.blend_type = "MIX"
    mix.inputs[6].default_value = col
    k = 1.25 if lighter else 0.72
    mix.inputs[7].default_value = (min(1, col[0] * k + 0.02), min(1, col[1] * k + 0.02),
                                   min(1, col[2] * k + 0.02), 1)
    nt.links.new(_mul(nt, fac, amount), mix.inputs["Factor"])
    nt.links.new(mix.outputs[2], b.inputs["Base Color"])


def _plooien(nt, b, co, strength=0.22):
    """Grote, zachte plooien in de stof (liggend, zoals bij mouwen en broekspijpen)."""
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1.0, 1.0, 2.8)
    nt.links.new(co, mp.inputs["Vector"])
    n = nt.nodes.new("ShaderNodeTexNoise")
    n.inputs["Scale"].default_value = 7.0
    n.inputs["Detail"].default_value = 1.0
    n.inputs["Distortion"].default_value = 0.6
    nt.links.new(mp.outputs[0], n.inputs["Vector"])
    _bump(nt, b, n.outputs["Fac"], strength, 0.02)


def detail(mat, b, stof):
    """Voegt stofstructuur toe. Micro-reliëf: zichtbaar in close-ups, rustig in wides."""
    if not DETAIL or stof in (None, "huid") or mat.get("glans2"):
        return
    mat["glans2"] = True
    nt = mat.node_tree
    co = _coord(nt)
    if stof in ("breisel", "wol", "fleece", "pyjama", "katoen", "denim", "nylon"):
        _plooien(nt, b, co, 0.12 if stof == "nylon" else 0.2)
    if stof in ("breisel", "wol"):
        # gebreide ribbels (verticaal) met wat wolligheid
        rib = _wave(nt, co, 110, "X", distort=1.5, detail=1.0)
        n = _noise(nt, co, 260, 2.0)
        h = _mul(nt, _mul(nt, rib, 0.7), _mul(nt, n, 0.3), "ADD")
        _bump(nt, b, h, 0.28, 0.003)
        b.inputs["Sheen Weight"].default_value = 0.45
        b.inputs["Sheen Roughness"].default_value = 0.5
        b.inputs["Roughness"].default_value = 0.55
        b.inputs["Coat Weight"].default_value = 0.12
        _tint(nt, b, _noise(nt, co, 18, 2.0), 0.18)
    elif stof in ("fleece", "pyjama", "pluche"):
        n = _noise(nt, co, 380, 3.0, 0.6)
        _bump(nt, b, n, 0.16, 0.002)
        b.inputs["Sheen Weight"].default_value = 0.55
        b.inputs["Sheen Roughness"].default_value = 0.45
        b.inputs["Roughness"].default_value = 0.5
        b.inputs["Coat Weight"].default_value = 0.14
        _tint(nt, b, _noise(nt, co, 9, 2.0), 0.14)
    elif stof == "katoen":
        n = _noise(nt, co, 420, 2.0)
        _bump(nt, b, n, 0.1, 0.0015)
        b.inputs["Sheen Weight"].default_value = 0.3
        b.inputs["Roughness"].default_value = 0.46
        b.inputs["Coat Weight"].default_value = 0.16
        _tint(nt, b, _noise(nt, co, 12, 2.0), 0.1)
    elif stof == "denim":
        # keperbinding: schuine fijne lijnen plus vervaagde plekken
        tw = _wave(nt, co, 300, "DIAGONAL", distort=0.4, detail=0.5)
        _bump(nt, b, tw, 0.18, 0.0015)
        _tint(nt, b, _noise(nt, co, 14, 3.0), 0.35)
        b.inputs["Roughness"].default_value = 0.52
        b.inputs["Coat Weight"].default_value = 0.1
        b.inputs["Sheen Weight"].default_value = 0.2
    elif stof == "nylon":
        n = _noise(nt, co, 60, 2.0)
        _bump(nt, b, n, 0.06, 0.004)
        b.inputs["Roughness"].default_value = 0.28
        b.inputs["Coat Weight"].default_value = 0.35
    elif stof == "leer":
        v = nt.nodes.new("ShaderNodeTexVoronoi")
        v.feature = "DISTANCE_TO_EDGE"
        v.inputs["Scale"].default_value = 160
        nt.links.new(co, v.inputs["Vector"])
        _bump(nt, b, v.outputs["Distance"], 0.12, 0.0015)
        _tint(nt, b, _noise(nt, co, 6, 2.0), 0.3)
        b.inputs["Roughness"].default_value = 0.3
        b.inputs["Coat Weight"].default_value = 0.4
        b.inputs["Coat Roughness"].default_value = 0.12
    elif stof == "haar":
        # gebeeldhouwde lokken zoals bij vinyl-speelgoed: groeven met golving
        lok = _wave(nt, co, 55, "X", distort=4.0, detail=2.0)
        fijn = _wave(nt, co, 210, "X", distort=6.0, detail=1.0)
        h = _mul(nt, _mul(nt, lok, 0.75), _mul(nt, fijn, 0.25), "ADD")
        _bump(nt, b, h, 0.45, 0.004)
        _tint(nt, b, lok, 0.22)
        b.inputs["Roughness"].default_value = 0.32
        b.inputs["Coat Weight"].default_value = 0.35
        b.inputs["Coat Roughness"].default_value = 0.2
        b.inputs["Sheen Weight"].default_value = 0.15
    elif stof == "vacht":
        lok = _wave(nt, co, 140, "Z", distort=8.0, detail=2.0)
        _bump(nt, b, lok, 0.1, 0.002)
        b.inputs["Sheen Weight"].default_value = 0.6
        b.inputs["Roughness"].default_value = 0.5
        b.inputs["Coat Weight"].default_value = 0.1
        _tint(nt, b, _noise(nt, co, 20, 2.0), 0.15)
    elif stof in ("schoen", "rubber"):
        n = _noise(nt, co, 500, 2.0)
        _bump(nt, b, n, 0.05, 0.001)
        b.inputs["Roughness"].default_value = 0.34
        b.inputs["Coat Weight"].default_value = 0.3


def skin_detail(mat, b):
    """Huid: heel lichte poriën en wat variatie in ruwheid, plus iets meer SSS."""
    if not DETAIL or mat.get("glans2"):
        return
    mat["glans2"] = True
    nt = mat.node_tree
    co = _coord(nt)
    n = _noise(nt, co, 700, 2.0)
    _bump(nt, b, n, 0.04, 0.0008)
    r = nt.nodes.new("ShaderNodeMapRange")
    r.inputs["To Min"].default_value = 0.38
    r.inputs["To Max"].default_value = 0.5
    nt.links.new(_noise(nt, co, 25, 2.0), r.inputs["Value"])
    nt.links.new(r.outputs["Result"], b.inputs["Roughness"])
    b.inputs["Subsurface Weight"].default_value = 0.32


def glossify(mat):
    """Maak een Principled-materiaal glad en glimmend zoals het logo."""
    if not mat.use_nodes:
        return
    b = mat.node_tree.nodes.get("Principled BSDF")
    if b is None:
        return
    col = b.inputs["Base Color"].default_value
    metal = b.inputs["Metallic"].default_value
    name = mat.name.lower()
    if metal > 0.5:
        b.inputs["Roughness"].default_value = 0.18
        return
    stof = stof_of(mat)
    if stof == "huid" or (stof is None and is_skin(mat, col)):
        # zachte, egale huid met lichte glans en wat doorschijnendheid
        b.inputs["Roughness"].default_value = 0.42
        b.inputs["Subsurface Weight"].default_value = 0.25
        b.inputs["Subsurface Radius"].default_value = (0.9, 0.35, 0.2)
        b.inputs["Subsurface Scale"].default_value = 0.03
        b.inputs["Coat Weight"].default_value = 0.15
        b.inputs["Coat Roughness"].default_value = 0.3
        skin_detail(mat, b)
        return
    # kleding, haar, schoenen: glad vinyl-speelgoed met een coatlaag
    b.inputs["Roughness"].default_value = 0.38
    b.inputs["Coat Weight"].default_value = 0.25
    b.inputs["Coat Roughness"].default_value = 0.18
    b.inputs["Specular IOR Level"].default_value = 0.55
    b.inputs["Sheen Weight"].default_value = 0.0
    # kleuren iets voller, zoals in het logo
    r, g, bb = col[:3]
    m = (r + g + bb) / 3
    sat = 1.2
    b.inputs["Base Color"].default_value = (max(0, m + (r - m) * sat), max(0, m + (g - m) * sat),
                                            max(0, m + (bb - m) * sat), 1)
    detail(mat, b, stof)


def area(coll, name, energy, size, loc, target, color):
    ld = bpy.data.lights.new(name, "AREA")
    ld.energy = energy
    ld.size = size
    ld.shape = "DISK"
    ld.color = lin(color)
    ob = bpy.data.objects.new(name, ld)
    ob.location = Vector(loc)
    ob.rotation_euler = (Vector(target) - ob.location).to_track_quat("-Z", "Y").to_euler()
    ob.visible_camera = False
    coll.objects.link(ob)
    return ob


def setup_look(samples, pct):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 8
    sc.render.resolution_percentage = pct
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Punchy"
    sc.view_settings.exposure = -0.2

    for m in bpy.data.materials:
        if m.name in ("vloer", "label"):
            continue
        glossify(m)

    # oude studio weg, nieuwe donkere studio
    old = bpy.data.collections.get("studio")
    cam_data = None
    if old:
        for ob in list(old.objects):
            if ob.type == "CAMERA":
                cam_data = ob
                continue
            bpy.data.objects.remove(ob)
    studio = old or bpy.data.collections.new("studio")

    w = sc.world
    w.use_nodes = True
    nt = w.node_tree
    bg = nt.nodes["Background"]
    bg.inputs[0].default_value = (*lin("#0B1430"), 1)
    bg.inputs[1].default_value = 0.15

    # glimmende donkere vloer + gebogen achterwand (geen horizonlijn)
    bm = bmesh.new()
    prof = []
    for k in range(25):
        t = k / 24
        a = t * math.pi / 2
        prof.append((0, 4 + 3 * math.sin(a) - 3, 3 - 3 * math.cos(a)))
    rows = []
    for x in (-25, 25):
        rows.append([bm.verts.new((x, -12 if i == 0 else y, z)) for i, (_, y, z) in
                     enumerate([(0, -12, 0)] + prof + [(0, 4, 12)])])
    for i in range(len(rows[0]) - 1):
        bm.faces.new((rows[0][i], rows[1][i], rows[1][i + 1], rows[0][i + 1]))
    me = bpy.data.meshes.new("decor")
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    decor = bpy.data.objects.new("decor", me)
    studio.objects.link(decor)
    dm = bpy.data.materials.new("decor")
    dm.use_nodes = True
    d = dm.node_tree.nodes["Principled BSDF"]
    d.inputs["Base Color"].default_value = (*lin("#05070F"), 1)
    d.inputs["Roughness"].default_value = 0.45
    # eigen gloed van de wand: donker nachtblauw met een blauwe halo achter de figuur
    nt2 = dm.node_tree
    geo = nt2.nodes.new("ShaderNodeNewGeometry")
    dist = nt2.nodes.new("ShaderNodeVectorMath")
    dist.operation = "DISTANCE"
    dist.inputs[1].default_value = (0.0, 4.0, 1.6)
    ramp = nt2.nodes.new("ShaderNodeValToRGB")
    cr = ramp.color_ramp
    cr.elements[0].position = 0.0
    cr.elements[0].color = (*lin("#1F4FD8"), 1)
    cr.elements[1].position = 1.0
    cr.elements[1].color = (*lin("#03050C"), 1)
    mid = cr.elements.new(0.35)
    mid.color = (*lin("#0B1A4A"), 1)
    rng = nt2.nodes.new("ShaderNodeMapRange")
    rng.inputs["From Max"].default_value = 6.0
    em = nt2.nodes.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = 1.0
    add = nt2.nodes.new("ShaderNodeAddShader")
    outn = nt2.nodes["Material Output"]
    nt2.links.new(geo.outputs["Position"], dist.inputs[0])
    nt2.links.new(dist.outputs["Value"], rng.inputs["Value"])
    nt2.links.new(rng.outputs["Result"], ramp.inputs["Fac"])
    nt2.links.new(ramp.outputs["Color"], em.inputs["Color"])
    nt2.links.new(d.outputs["BSDF"], add.inputs[0])
    nt2.links.new(em.outputs["Emission"], add.inputs[1])
    nt2.links.new(add.outputs["Shader"], outn.inputs["Surface"])
    me.materials.append(dm)

    # licht: warm hoofdlicht, zachte vulling, twee blauwe randlichten, warme tegenrand
    area(studio, "hoofdlicht", 650, 2.5, (-1.6, -4.0, 2.6), (0, 0, 1.3), "#FFE6CC")
    area(studio, "vullicht", 90, 4.0, (3.0, -4.2, 1.4), (0, 0, 1.2), "#E6ECFF")
    area(studio, "rand_blauw_R", 2600, 0.6, (2.0, 2.6, 1.9), (0, 0, 1.45), "#3D8BFF")
    area(studio, "rand_warm_L", 2200, 0.6, (-2.0, 2.6, 1.7), (0, 0, 1.35), "#FF9A3D")
    area(studio, "kruin", 150, 2.0, (0, 1.0, 4.2), (0, 0, 1.6), "#CFE0FF")
    return studio


def aim(cam, loc, target, lens=50):
    cam.location = Vector(loc)
    cam.rotation_euler = (Vector(target) - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = lens


def render(path, rx, ry):
    sc = bpy.context.scene
    sc.render.resolution_x = rx
    sc.render.resolution_y = ry
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print("render:", path)


def instance(coll, loc, rot_z, parent):
    e = bpy.data.objects.new(f"inst_{coll.name}", None)
    e.instance_type = "COLLECTION"
    e.instance_collection = coll
    e.location = Vector(loc)
    e.rotation_euler = (0, 0, rot_z)
    parent.objects.link(e)
    return e


def head_center(coll):
    """Middelpunt van het hoofd-object van een figuur."""
    for ob in coll.objects:
        if ob.type == "MESH" and (ob.name.endswith("_hoofd") or ob.name.endswith("part_28")):
            pts = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
            return sum(pts, Vector()) / 8
    return Vector((0, 0, 1.47))


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    opts = {"--blend": "/mnt/project-files/cast/cast_video1.blend",
            "--out": "/mnt/project-files/cast/glans", "--only": "", "--samples": "128",
            "--pct": "100"}
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
    os.makedirs(out, exist_ok=True)
    only = [k for k in opts["--only"].split(",") if k]

    bpy.ops.wm.open_mainfile(filepath=opts["--blend"])
    sc = bpy.context.scene
    studio = setup_look(int(opts["--samples"]), int(opts["--pct"]))
    cam = sc.camera
    cast = bpy.data.collections["cast"]
    for lc in bpy.context.view_layer.layer_collection.children["cast"].children:
        lc.exclude = True
    tmp = bpy.data.collections.new("glans_tmp")
    sc.collection.children.link(tmp)
    # het studiolicht valt alleen op de figuren; de wand houdt zijn eigen gloed
    for ob in studio.objects:
        if ob.type == "LIGHT" and ob.name != "kruin":
            ob.light_linking.receiver_collection = tmp

    figs = [c for c in cast.children if not only or c.name in only]
    if "--no-closeups" not in flags:
        for c in figs:
            e = instance(c, (0, 0, 0), 0.0, tmp)
            hc = head_center(c)
            # zelfde kader als het logo: hoofd en schouders, iets van opzij
            aim(cam, (hc.x + 0.45, hc.y - 1.75, hc.z - 0.02), (hc.x, hc.y, hc.z - 0.17), lens=55)
            render(os.path.join(out, f"glans_{c.name}.png"), 1200, 1200)
            bpy.data.objects.remove(e)

    if "--no-overview" not in flags and not only:
        items = []
        for c in cast.children:
            zmax = max((o.matrix_world @ Vector(b)).z for o in c.objects if o.type == "MESH"
                       for b in o.bound_box)
            items.append((c, zmax))
        hero = [t for t in items if t[0].name == "hoofdpersonage"]
        rest = sorted([t for t in items if t[0].name != "hoofdpersonage"], key=lambda t: -t[1])
        lineup = hero + rest
        gap = 0.82
        x0 = -(len(lineup) - 1) * gap / 2
        for k, (c, h) in enumerate(lineup):
            instance(c, (x0 + k * gap, 0, 0), 0.0, tmp)
        W = len(lineup) * gap
        # breder licht voor de hele rij
        for ob in studio.objects:
            if ob.type == "LIGHT":
                ob.data.size *= 2.5
                ob.location.x *= 2.6
                ob.data.energy *= 2.2
        aim(cam, (0, -W * 1.5, 1.35), (0, 0, 0.82), lens=50)
        render(os.path.join(out, "glans_00_overzicht.png"), 3200, 1100)


if __name__ == "__main__":
    main()
