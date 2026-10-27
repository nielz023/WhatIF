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
    if is_skin(mat, col):
        # zachte, egale huid met lichte glans en wat doorschijnendheid
        b.inputs["Roughness"].default_value = 0.42
        b.inputs["Subsurface Weight"].default_value = 0.25
        b.inputs["Subsurface Radius"].default_value = (0.9, 0.35, 0.2)
        b.inputs["Subsurface Scale"].default_value = 0.03
        b.inputs["Coat Weight"].default_value = 0.15
        b.inputs["Coat Roughness"].default_value = 0.3
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
