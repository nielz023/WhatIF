"""Sets: dag 40 en outro.
Varianten:
    hangar   hangar met het drukpak op een rek
    ruimte   wolken, donkerblauwe lucht, zwarte ruimte, de kromming van de aarde met dunne blauwe rand,
             zonsopkomst boven de horizon, sterren, en de gelijmde mok die voor de aarde zweeft (outro)

Gebruik:
    blender -b -P sets/build_ruimte.py -- <variant> [uitvoermap]
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402,F401
from mathutils import Vector  # noqa: E402
from lib import toon as T  # noqa: E402
from lib import props as P  # noqa: E402
from lib import interior as I  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
VAR = args[0] if args else "ruimte"
OUT = args[1] if len(args) > 1 else "/mnt/project-files/sets/22_ruimte"
rnd = random.Random(40)


def mug(name, loc, rot=(0, 0, 0), scale=1.0):
    """De WORLD'S OKAYEST MOM-mok, gelijmd (scheurlijnen)."""
    p = [T.cyl(name + "_body", (0, 0, 0), 0.045, 0.1, P.m("wit"), seg=24, ol=0),
         T.torus(name + "_oor", (0.05, 0, 0.05), 0.028, 0.008, P.m("wit"), rot=(90, 0, 0), seg=16, seg2=6, ol=0),
         T.cyl(name + "_koffie", (0, 0, 0.088), 0.041, 0.005, T.toon("koffie", (0.30, 0.18, 0.10)), seg=24, ol=0)]
    crack = [(-0.046 * math.sin(a), -0.046 * math.cos(a), z) for a, z in [(-0.6, 0.0), (-0.4, 0.025), (-0.55, 0.045), (-0.2, 0.07), (-0.35, 0.1)]]
    p.append(T.to_mesh(T.tube(name + "_lijmnaad1", crack, 0.0015, T.toon("lijm", (0.75, 0.62, 0.35)))))
    crack2 = [(-0.046 * math.sin(a), -0.046 * math.cos(a), z) for a, z in [(0.3, 0.1), (0.45, 0.06), (0.3, 0.035)]]
    p.append(T.to_mesh(T.tube(name + "_lijmnaad2", crack2, 0.0015, T.toon("lijm", (0.75, 0.62, 0.35)))))
    o = T.merge(name, p, ol=0.002)
    T.text(name + "_tekst1", "WORLD'S", (0, -0.047, 0.065), 0.016, T.toon("mok_tekst", (0.1, 0.1, 0.12)), extrude=0.001).parent = o
    T.text(name + "_tekst2", "OKAYEST MOM", (0, -0.047, 0.04), 0.012, T.toon("mok_tekst", (0.1, 0.1, 0.12)), extrude=0.001).parent = o
    o.location = loc
    o.rotation_euler = [math.radians(a) for a in rot]
    o.scale = (scale,) * 3
    return o


if VAR == "hangar":
    mood = dict(T.MOODS["binnen"])
    mood.update(ambient=(0.20, 0.22, 0.26), shadow_tint=(0.40, 0.44, 0.58), lit_tint=(1.0, 0.97, 0.92), sun_strength=0.0, fog_max=0.0, bloom=0.6)
    T.new_scene("Hangar_drukpak", mood, samples=48)
    W, D, H = 24.0, 30.0, 12.0
    T.use_collection(T.collection("Hangar"))
    room = I.room("Hangar", W, D, H, wall_color=(0.62, 0.64, 0.60), floor_color=(0.45, 0.46, 0.46), skirting=False, ceiling=False)
    room["floor"].data.materials[0] = T.pattern("hangarvloer", (0.48, 0.49, 0.49), (0.45, 0.46, 0.46), grout=(0.38, 0.38, 0.38), size=(3.0, 3.0), mortar=0.004)
    for side in ("back", "left", "right"):
        room[side].data.materials[0] = T.pattern("golfplaat", (0.64, 0.66, 0.62), (0.60, 0.62, 0.58), grout=(0.52, 0.54, 0.50), size=(0.25, 12.0), mortar=0.02)
    spants = [T.box(f"Spant_{y}", (0, y, H), (W, 0.4, 0.5), P.m("metaal"), bevel=0, ol=0) for y in range(-14, 15, 4)]
    T.merge("Dakspanten", spants, ol=0.02)
    T.box("Dak", (0, 0, H + 0.5), (W + 0.4, D + 0.4, 0.2), T.toon("dak_donker", (0.25, 0.26, 0.28)), bevel=0, ol=0)
    T.plane("Gele_lijn", (0, 0, 0.005), (0.15, D - 2), T.toon("waarschuwing_geel", (0.98, 0.80, 0.08)))
    # drukpak op een rek
    T.use_collection(T.collection("Drukpak"))
    SUIT = T.toon("drukpak_wit", (0.94, 0.94, 0.92))
    ORANGE = T.toon("drukpak_oranje", (0.98, 0.45, 0.10))
    rk = [T.box("Rek_voet", (0, 0, 0), (1.4, 1.0, 0.1), P.m("metaal"), bevel=0.02, ol=0),
          T.cyl("Rek_paal", (0, 0.35, 0.1), 0.05, 2.1, P.m("metaal"), seg=10, ol=0),
          T.box("Rek_schouder", (0, 0.35, 2.1), (0.9, 0.08, 0.06), P.m("metaal"), bevel=0, ol=0)]
    suit = [T.sphere("Pak_romp", (0, 0, 1.45), 0.36, SUIT, scale=(1.0, 0.75, 1.25), seg=20, ol=0),
            T.box("Pak_borstplaat", (0, -0.27, 1.55), (0.38, 0.06, 0.25), ORANGE, bevel=0.03, ol=0),
            T.cyl("Pak_halsring", (0, 0, 1.9), 0.2, 0.08, P.m("metaal"), seg=24, ol=0),
            T.sphere("Pak_helm", (0, 0, 2.15), 0.27, SUIT, seg=24, ol=0),
            T.sphere("Pak_vizier", (0, -0.1, 2.15), 0.22, T.toon("vizier_goud", (0.85, 0.62, 0.20)), scale=(1.0, 0.8, 0.85), seg=24, ol=0)]
    for s in (-1, 1):
        suit.append(T.sphere(f"Pak_arm_{s}", (s * 0.45, 0, 1.35), 0.12, SUIT, scale=(1, 1, 3.0), rot=(0, s * 10, 0), seg=14, ol=0))
        suit.append(T.sphere(f"Pak_handschoen_{s}", (s * 0.5, 0, 0.95), 0.1, ORANGE, seg=12, ol=0))
        suit.append(T.sphere(f"Pak_been_{s}", (s * 0.17, 0, 0.6), 0.15, SUIT, scale=(1, 1, 3.2), seg=14, ol=0))
        suit.append(T.box(f"Pak_laars_{s}", (s * 0.17, -0.05, 0.1), (0.2, 0.32, 0.18), P.m("zwart"), bevel=0.06, ol=0))
    rack = T.merge("Drukpakrek", rk, ol=0.01)
    pak = T.merge("Drukpak", suit, ol=0.01)
    rack.location = pak.location = (0, 6, 0)
    T.box("Zuurstofkist", (1.5, 6, 0), (0.8, 0.6, 0.7), T.toon("kist_groen", (0.25, 0.40, 0.30)), bevel=0.03, ol=0.01)
    for k in range(3):
        T.cyl(f"Zuurstoffles_{k}", (-1.4 + k * 0.3, 6.3, 0), 0.12, 1.3, T.toon("fles_blauw", (0.15, 0.40, 0.85)), seg=14, ol=0.01)
    I.table("Werktafel", (3.2, 4.0, 0), size=(2.0, 0.9, 0.9), color=(0.55, 0.58, 0.64))
    T.box("Laptop_hangar", (3.2, 4.0, 0.9), (0.4, 0.3, 0.02), P.m("zwart"), bevel=0.005, ol=0.004)
    # lampen
    lamps = [T.cyl(f"Hallamp_{x}_{y}", (x, y, H - 1.6), 0.5, 0.5, P.m("metaal"), r2=0.15, seg=16, ol=0, cap=False) for x in (-6, 0, 6) for y in (-8, 0, 8)]
    T.merge("Hallampen", lamps, ol=0.02)
    for x in (-6, 0, 6):
        for y in (-8, 0, 8):
            T.point_light(f"Hallicht_{x}_{y}", (x, y, H - 1.8), color=(1.0, 0.95, 0.85), energy=2500, radius=0.3)
    T.spot_light("Spot_drukpak", (0, 0, 7), (0, 6, 1.4), color=(1.0, 0.97, 0.9), energy=3500, angle=30, blend=0.4)
    T.use_collection(None)
    T.character((-1.2, 4.6, 0), rot_z=-20)
    cams = [T.camera("CAM_01_hangar_wide", (8, -12, 3.5), (-1, 6, 1.6), lens=24),
            T.camera("CAM_02_drukpak", (0.6, 3.4, 1.7), (0, 6, 1.6), lens=35)]
else:
    mood = dict(T.MOODS["nacht"])
    mood.update(sky_top=(0.0, 0.0, 0.005), sky_horizon=(0.01, 0.02, 0.06), ground_glow=(0.0, 0.0, 0.0), sun_color=(1.0, 0.98, 0.95), sun_strength=1.3,
                sun_rot=(118.7, 0, 90), ambient=(0.02, 0.025, 0.05), shadow_tint=(0.10, 0.14, 0.30), lit_tint=(1.0, 1.0, 0.98), fog_max=0.0, bloom=1.0)
    T.new_scene("Ruimte", mood, samples=48)
    R = 1500.0
    C = Vector((0, 0, -R))
    T.use_collection(T.collection("Aarde"))
    earth = T.sphere("Aarde", tuple(C), R, T.toon("oceaan", (0.06, 0.28, 0.75)), seg=128, ol=0)
    # continenten: platte schijven op het oppervlak
    land = []
    for k in range(70):
        th = rnd.uniform(0, 2 * math.pi)
        ph = rnd.uniform(0.0, 1.2)
        n = Vector((math.sin(ph) * math.cos(th), math.sin(ph) * math.sin(th), math.cos(ph)))
        s = rnd.uniform(40, 180)
        o = T.sphere(f"Land_{k}", tuple(C + n * (R + 0.5)), s, T.toon("land_groen" if k % 4 else "land_bruin", (0.25, 0.55, 0.22) if k % 4 else (0.62, 0.50, 0.30)),
                     scale=(1.0, rnd.uniform(0.5, 1.0), 0.01), seg=16, ol=0)
        o.rotation_mode = "QUATERNION"
        o.rotation_quaternion = n.to_track_quat("Z", "Y")
        land.append(o)
    T.merge("Continenten", land, ol=0)
    clouds = []
    for k in range(220):
        th = rnd.uniform(0, 2 * math.pi)
        ph = rnd.uniform(0.0, 1.3)
        n = Vector((math.sin(ph) * math.cos(th), math.sin(ph) * math.sin(th), math.cos(ph)))
        s = rnd.uniform(15, 70)
        o = T.sphere(f"Wolk_{k}", tuple(C + n * (R + 6 + rnd.uniform(0, 4))), s, T.toon("wolk", (0.97, 0.97, 1.0)), scale=(1.6, 1.0, 0.12), seg=12, ol=0)
        o.rotation_mode = "QUATERNION"
        o.rotation_quaternion = n.to_track_quat("Z", "Y")
        clouds.append(o)
    T.merge("Wolken", clouds, ol=0)
    # dampkring: blauwe rand (fresnel-gloed)
    atm = bpy.data.materials.new("dampkring")
    atm.use_nodes = True
    N, L = atm.node_tree.nodes, atm.node_tree.links
    N.clear()
    out = N.new("ShaderNodeOutputMaterial")
    lw = N.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.35
    ramp = N.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.55
    ramp.color_ramp.elements[0].color = (0, 0, 0, 1)
    ramp.color_ramp.elements[1].position = 0.97
    ramp.color_ramp.elements[1].color = (1, 1, 1, 1)
    em = N.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (0.35, 0.65, 1.0, 1)
    em.inputs["Strength"].default_value = 3.0
    tr = N.new("ShaderNodeBsdfTransparent")
    mx = N.new("ShaderNodeMixShader")
    L.new(lw.outputs["Facing"], ramp.inputs["Fac"])
    L.new(ramp.outputs["Color"], mx.inputs[0])
    L.new(tr.outputs[0], mx.inputs[1])
    L.new(em.outputs[0], mx.inputs[2])
    L.new(mx.outputs[0], out.inputs["Surface"])
    atm.surface_render_method = "BLENDED"
    a_ = T.sphere("Dampkring", tuple(C), R * 1.025, atm, seg=128, ol=0)
    a_.visible_shadow = False
    # zon (zonsopkomst boven de horizon) en sterren
    T.use_collection(T.collection("Zon en sterren"))
    sun_dir = Vector((0.876, 0.0, -0.46)).normalized()  # net boven de horizon gezien vanaf 400 m "hoogte"
    T.sphere("Zon", tuple(sun_dir * 9000), 120, T.glow("zon", (1.0, 0.95, 0.85), 30), seg=24, ol=0)
    stars = []
    for k in range(2500):
        v = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-0.2, 1))).normalized()
        stars.append(tuple(v * 12000))
    P.points_mesh("Sterren", stars, 9, T.glow("ster", (1.0, 1.0, 0.95), 6), seg=4)
    # de gelijmde mok, zwevend voor de aarde (outro)
    T.use_collection(T.collection("Mok (outro)"))
    mug("Mok_gelijmd", (0, -0.6, 400.0), rot=(12, -18, 25), scale=1.0)
    T.use_collection(None)
    T.character((0, 0, 398.5), rot_z=0)
    cams = [T.camera("CAM_01_aarde_kromming", (0, -6, 401), (0, 600, 121), lens=24),
            T.camera("CAM_02_zonsopkomst", (3, -4, 399.5), (2000, 300, -900), lens=28),
            T.camera("CAM_03_mok_voor_aarde", (0.05, -0.95, 400.08), (0, -0.6, 400.03), lens=50),
            T.camera("CAM_04_wolken_stratosfeer", (0, -40, 30), (0, 800, -60), lens=24)]
    for c in cams:
        c.data.clip_end = 30000
        c.data.clip_start = 0.01

blend, renders = T.finish(OUT, VAR, cams)
print("KLAAR", blend, renders)
