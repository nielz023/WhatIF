"""Overzicht van de nieuwe props voor video 2 ("What IF You Got 10x FASTER Every Day?"),
in de glans-studio (nachtblauwe achtergrond, warm hoofdlicht, oranje en blauw randlicht).

Gebruik:
    blender -b -P sets/build_props_10x.py -- [klein|voertuigen] [uitvoermap]
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402
from lib import toon as T  # noqa: E402
from lib import props as P  # noqa: E402
from lib import street as S  # noqa: E402
from lib import huis as H  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
VAR = args[0] if args else "klein"
OUT = args[1] if len(args) > 1 else "/mnt/project-files/videos/10x-sneller/sets/00_props"

mood = dict(T.MOODS["nacht"])
mood.update(ambient=(0.03, 0.045, 0.1), sun_strength=0.0, fog_max=0.0, bloom=0.4, exposure=0.0)
T.new_scene("Props_" + VAR, mood)
SC = 1.0 if VAR == "klein" else 9.0  # studio-schaal


def studio(scale, licht=1.0):
    """Gebogen achterwand met blauwe gloed, zoals cast/render_glans.py."""
    T.use_collection(T.collection("Studio"))
    import bmesh
    bm = bmesh.new()
    prof = [(0, -12, 0)] + [(0, 4 + 3 * math.sin(k / 24 * math.pi / 2) - 3, 3 - 3 * math.cos(k / 24 * math.pi / 2)) for k in range(25)] + [(0, 4, 12)]
    rows = [[bm.verts.new((x * scale, y * scale, z * scale)) for _, y, z in prof] for x in (-25, 25)]
    for i in range(len(prof) - 1):
        bm.faces.new((rows[0][i], rows[1][i], rows[1][i + 1], rows[0][i + 1]))
    me = bpy.data.meshes.new("decor")
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    dm = bpy.data.materials.new("decor")
    dm.use_nodes = True
    nt = dm.node_tree
    d = nt.nodes["Principled BSDF"]
    d.inputs["Base Color"].default_value = (0.0015, 0.002, 0.005, 1)
    d.inputs["Roughness"].default_value = 0.45
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    dist = nt.nodes.new("ShaderNodeVectorMath")
    dist.operation = "DISTANCE"
    dist.inputs[1].default_value = (0.0, 4.0 * scale, 1.2 * scale)
    rng = nt.nodes.new("ShaderNodeMapRange")
    rng.inputs["From Max"].default_value = 6.0 * scale
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    cr = ramp.color_ramp
    cr.elements[0].color = (0.013, 0.08, 0.69, 1)
    cr.elements[1].color = (0.001, 0.0015, 0.004, 1)
    cr.elements.new(0.35).color = (0.004, 0.011, 0.07, 1)
    em = nt.nodes.new("ShaderNodeEmission")
    add = nt.nodes.new("ShaderNodeAddShader")
    nt.links.new(geo.outputs["Position"], dist.inputs[0])
    nt.links.new(dist.outputs["Value"], rng.inputs["Value"])
    nt.links.new(rng.outputs["Result"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], em.inputs["Color"])
    nt.links.new(d.outputs["BSDF"], add.inputs[0])
    nt.links.new(em.outputs["Emission"], add.inputs[1])
    nt.links.new(add.outputs["Shader"], nt.nodes["Material Output"].inputs["Surface"])
    me.materials.append(dm)
    o = bpy.data.objects.new("decor", me)
    T._link(o)
    T.use_collection(None)
    s = scale
    for nm, e, size, loc, tgt, col in [("hoofdlicht", 650, 2.5, (-1.6, -4.0, 2.6), (0, 0, 0.6), (1.0, 0.79, 0.6)),
                                         ("vullicht", 90, 4.0, (3.0, -4.2, 1.4), (0, 0, 0.5), (0.79, 0.84, 1.0)),
                                         ("rand_blauw", 2600, 0.6, (2.0, 2.6, 1.9), (0, 0, 0.6), (0.047, 0.24, 1.0)),
                                         ("rand_oranje", 2200, 0.6, (-2.0, 2.6, 1.7), (0, 0, 0.6), (1.0, 0.33, 0.045)),
                                         ("kruin", 150, 2.0, (0, 1.0, 4.2), (0, 0, 0.8), (0.62, 0.75, 1.0))]:
        ld = bpy.data.lights.new(nm, "AREA")
        ld.energy, ld.size, ld.shape, ld.color = e * s * s * licht, size * s, "DISK", col
        lo = bpy.data.objects.new(nm, ld)
        lo.location = Vector(loc) * s
        lo.rotation_euler = (Vector(tgt) * s - lo.location).to_track_quat("-Z", "Y").to_euler()
        lo.visible_camera = False
        bpy.context.scene.collection.objects.link(lo)


studio(SC, licht=1.0 if VAR == "klein" else 0.3)
T.use_collection(T.collection("Props"))
if VAR == "klein":
    # tafeltje als ondergrond voor de kleine props
    T.box("Toonbank", (0, 0.1, 0), (2.6, 0.9, 0.7), T.toon("toonbank", (0.05, 0.06, 0.1)), bevel=0.02, ol=0)
    Z = 0.7
    wb = H.whiteboard("Whiteboard", (-1.05, 0.45, Z + 0.33))
    H.whiteboard_tekst(wb, [("TUESDAY 9:00", 0.055, "blauw", 0.3), ("-> CANDLES!!", 0.06, "rood", 0.08),
                            ("8 -> 9", 0.09, "blauw", -0.22)])
    cake, _ = H.taart("Verjaardagstaart", (-0.45, 0.2, Z))
    H.kraanvogels_hoop("Kraanvogel", (0.15, 0.25), (0.45, 0.3), 40, height=0.12, seed=4, z0=Z)
    H.kraanvogel("Kraanvogel_zielige_duif", (0.05, -0.12, Z), 6, rot=(0, 0, -30), droevig=True)
    H.kraanvogel("Kraanvogel_groot", (0.3, -0.15, Z), 1, rot=(0, 0, -40), s=1.6)
    H.laptop("Laptop", (0.72, 0.25, Z), rot_z=-20)
    H.knijpfles("Knijpfles", (1.0, -0.12, Z))
    H.waterglas("Waterglas", (0.85, -0.2, Z))
    H.kapotte_sneaker("Kapotte_sneaker", (1.12, 0.3, Z), rot=-140)
    H.aansteker("Aansteker", (-0.15, -0.2, Z + 0.018), rot=(0, 0, 20))
    H.cadeau("Cadeau", (-0.85, -0.1, Z), rot_z=20)
    H.papierstapels("Papierstapels", (-0.05, 0.35, Z), n=3)
    H.hogesnelheidscamera("Hogesnelheidscamera", (1.75, 0.6, 0), rot_z=200)
    cams = [T.camera("CAM_01_props_klein", (0.15, -2.6, 1.55), (0.15, 0.2, 0.85), lens=34)]
else:
    S.garbage_truck("Vuilniswagen", (-6.5, 2.0, 0), rot=-25, lights=True)
    S.delivery_van("Bestelbus", (3.5, 0.5, 0), rot=-35)
    S.city_bus("Stadsbus", (1.0, 10.0, 0), rot=-15)
    S.bicycle("Fiets", (9.0, -2.0, 0), rot=-60)
    S.bird("Kraai", (-1.5, -2.5, 3.2), rot_z=-60)
    S.plastic_bag("Plastic_zak", (-0.5, -3.5, 1.6))
    cams = [T.camera("CAM_01_voertuigen", (0, -22, 6.5), (0.5, 1.5, 1.6), lens=30)]
T.use_collection(None)
blend, renders = T.finish(OUT, "props_" + VAR, cams)
print("KLAAR", blend, renders)
