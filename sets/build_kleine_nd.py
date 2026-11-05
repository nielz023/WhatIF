"""Kleine sets (video 4, Never Die), eenvoudig gehouden.

Varianten:
    schuur      scène 4: achtertuin met schuur; voetbal in de dakgoot, mos op de dakpannen, wasmand bij de achterdeur
    skate       scène 6a-6c: skatehelling (halfpipe + hoge helling) in het park
    club        scène 8c-8d: ingang van een club bij nacht, rij, neonbord, fluwelen koord
    bruiloft    scène 9a-9c2: bruiloftstuin met boog, stoelen, ronde tafels met lichtjes
    brand       scène 10a-10c2: flatgebouw in brand bij nacht, brandweerwagens, vuur en rook (materiaal "vuur_gloed")
    vliegtuig   scène 10e: open deur van een testvliegtuig hoog boven de wolken
    maisveld    scène 10g-10h: krater in een maïsveld

Gebruik:
    python3 sets/build_kleine_nd.py <variant> [uitvoermap]
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402,F401
from lib import toon as T  # noqa: E402
from lib import props as P  # noqa: E402
from lib import stad as S  # noqa: E402
from lib import street as ST  # noqa: E402
from lib import nooitdood as ND  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
VAR = args[0] if args else "schuur"
OUT = args[1] if len(args) > 1 else f"/mnt/project-files/videos/nooit-dood/sets/04_{VAR}"
rnd = random.Random(4)
M = T.MOODS
mood = {"schuur": dict(M["ochtend"]), "skate": dict(M["dag"]), "club": dict(M["nacht"], bloom=1.0),
        "bruiloft": dict(M["zonsondergang"], sun_rot=(75, 0, 140)), "brand": dict(M["nacht"], bloom=1.2),
        "vliegtuig": dict(M["dag"], sky_top=(0.10, 0.30, 0.85), sky_horizon=(0.75, 0.88, 1.0), sun_strength=1.3),
        "maisveld": dict(M["dag"], sun_rot=(50, 0, 60))}[VAR]
T.new_scene("Klein_" + VAR, mood, samples=32)
T.use_collection(T.collection(VAR))


def ball(name, loc):
    p = [T.sphere(name, loc, 0.11, T.toon("bal_wit", (0.95, 0.95, 0.95)), seg=20, ol=0)]
    for k in range(6):
        a = k / 6 * 2 * math.pi
        p.append(T.sphere(f"{name}_vlak{k}", (loc[0] + math.cos(a) * 0.1, loc[1] + math.sin(a) * 0.1, loc[2] + 0.02 * (k % 2)), 0.035,
                          T.toon("bal_zwart", (0.05, 0.05, 0.06)), scale=(1, 1, 0.4), seg=8, ol=0))
    return T.merge(name, p, ol=0)


if VAR == "schuur":
    P.ground("Gazon", (60, 60), (0.30, 0.55, 0.20), z=0)
    T.box("Terras_tegels", (0, -3.5, 0), (8, 4, 0.04), T.pattern("stoeptegel_terras", (0.66, 0.64, 0.60), (0.62, 0.60, 0.57),
                                                               grout=(0.5, 0.5, 0.48), size=(0.6, 0.6)), bevel=0, ol=0)
    T.box("Huis_achtergevel", (0, -6.0, 0), (12, 0.4, 6), T.toon("baksteen_gevel", (0.62, 0.32, 0.22)), bevel=0, ol=0)
    T.box("Achterdeur", (-2.0, -5.79, 0), (0.95, 0.06, 2.1), T.toon("deur_achter", (0.95, 0.94, 0.92)), bevel=0.01, ol=0)
    T.box("Raam_keuken", (1.5, -5.78, 1.0), (1.8, 0.05, 1.3), T.glass("glas_keuken", (0.6, 0.75, 0.9), 0.4), bevel=0, ol=0)
    # schuur, 3 m hoog dak (de val van 3 meter)
    sx, sy = 3.2, 1.2
    T.box("Schuur_wanden", (sx, sy, 0), (3.0, 2.6, 2.2), T.toon("hout_schuur", (0.45, 0.30, 0.18)), bevel=0.02, ol=0)
    for s in (-1, 1):
        T.box(f"Schuur_dak_{s}", (sx, sy + s * 0.68, 2.55), (3.4, 1.6, 0.08), T.toon("dakpan_mos", (0.48, 0.22, 0.16)),
              rot=(s * -28, 0, 0), bevel=0.02, ol=0)
    mos = [T.sphere(f"Mos_{k}", (sx + rnd.uniform(-1.5, 1.5), sy - 0.7 + rnd.uniform(-0.5, 0.5), 2.62 - 0.3 * rnd.random()), 0.08,
                    T.toon("gras_mos", (0.25, 0.42, 0.12)), scale=(1.5, 1, 0.3), seg=8, ol=0) for k in range(40)]
    T.merge("Mos_dak", mos, ol=0)
    T.cyl("Dakgoot", (sx - 1.7, sy - 1.42, 2.1), 0.07, 3.4, T.toon("metaal_dakgoot", (0.7, 0.72, 0.74)), rot=(0, 90, 0), seg=12, ol=0)
    ball("Voetbal", (sx + 0.4, sy - 1.42, 2.17))
    T.box("Schuur_deur", (sx, sy - 1.31, 0), (0.9, 0.04, 1.9), T.toon("hout_schuur_deur", (0.35, 0.22, 0.12)), bevel=0.01, ol=0)
    T.box("Wasmand", (-2.6, -5.2, 0), (0.55, 0.4, 0.35), T.toon("plastic_wasmand", (0.35, 0.65, 0.85)), bevel=0.05, ol=0)
    T.box("Wasgoed", (-2.6, -5.2, 0.33), (0.5, 0.35, 0.1), T.toon("stof_wasgoed", (0.95, 0.95, 0.92)), bevel=0.04, ol=0)
    for k in range(8):
        T.box(f"Schutting_{k}", (-6 + k * 2, 7, 0), (1.95, 0.08, 1.8), T.toon("hout_schutting", (0.55, 0.38, 0.22)), bevel=0.01, ol=0)
    P.tree("Tuinboom", (-4, 4, 0), h=6, r=2.4, seed=2)
    T.character((sx + 0.2, sy - 0.75, 2.45), rot_z=0)
    cams = [T.camera("CAM_4a_WIJD", (-3.5, -4.0, 1.8), (sx, sy, 1.8), lens=22),
            T.camera("CAM_4c_LAAG", (sx - 3.0, sy - 4.0, 0.3), (sx, sy - 1.5, 1.6), lens=20)]
elif VAR == "skate":
    P.ground("Gras_park", (120, 120), (0.30, 0.56, 0.20), z=-0.02)
    beton = T.toon("beton_skatepark", (0.70, 0.70, 0.72))
    T.box("Skatevloer", (0, 0, -0.01), (24, 16, 0.04), beton, bevel=0, ol=0)
    # hoge helling (quarter pipe) met platform: de pestkop staat erbovenop
    qp = []
    for k in range(12):
        a0 = k / 12 * math.pi / 2
        r_ = 3.2
        y = 3 - (r_ - r_ * math.cos(a0))
        z = r_ * math.sin(a0)
        qp.append(T.box(f"Helling_{k}", (0, 4.0 - r_ * math.sin(a0 + math.pi / 24) * 0, 0), (6, 0.1, 0.1), beton, bevel=0, ol=0))
    for o in qp:
        bpy.data.objects.remove(o)
    T.box("Helling_blok", (0, 5.5, 0), (6, 3.0, 3.2), beton, bevel=0.05, ol=0)
    T.box("Helling_platform", (0, 6.0, 3.2), (6, 2.0, 0.1), T.toon("staal_platform", (0.55, 0.57, 0.6)), bevel=0.01, ol=0)
    # de schuine helling als wig: boven op het blok (y 4, z 3.2) tot op de vloer (y 0.8)
    me = bpy.data.meshes.new("Helling_schuin")
    vs = [(x, y, z) for x in (-3.0, 3.0) for (y, z) in ((4.0, 0.0), (4.0, 3.2), (0.8, 0.0))]
    me.from_pydata(vs, [], [(0, 1, 2), (5, 4, 3), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)])
    me.validate()
    T._obj("Helling_schuin", me, beton, (0, 0, 0), None, 0)
    P.railing("Hekje_platform", [(-3, 6.9, 3.3), (3, 6.9, 3.3)], h=1.0)
    T.box("Funbox", (-6, -2, 0), (3, 2, 0.6), beton, bevel=0.05, ol=0)
    for k in range(6):
        P.tree(f"Parkboom_{k}", (rnd.uniform(-30, 30), rnd.uniform(12, 30), 0), h=rnd.uniform(6, 9), r=3, seed=k)
    S.sign("Bord_skatepark", ["SKATE PARK"], (8, -6, 0), rot_z=-20, w=1.2, h=0.4)
    T.character((0.6, 6.0, 3.25), rot_z=180)
    cams = [T.camera("CAM_6a_WIJD", (7, -6, 2.2), (0, 4.0, 2.4), lens=24),
            T.camera("CAM_6b_HELLING", (-11, -1.5, 2.0), (0, 3.6, 2.2), lens=24)]
elif VAR == "club":
    T.plane("Stoep_club", (0, 0, 0), (40, 12), T.toon("stoep_nacht", (0.30, 0.30, 0.32)))
    T.plane("Straat_club", (0, -9, -0.1), (60, 8), T.toon("asfalt_nacht", (0.10, 0.10, 0.12)))
    T.box("Club_gevel", (0, 6, 0), (24, 1.0, 9), T.toon("gevel_club_zwart", (0.08, 0.08, 0.10)), bevel=0, ol=0)
    T.box("Club_deur", (0, 5.45, 0), (2.0, 0.1, 2.6), T.toon("metaal_clubdeur", (0.18, 0.18, 0.2)), bevel=0.02, ol=0)
    S.label("Neon_CLUB", "NOVA", (0, 5.4, 3.4), 1.0, (1.0, 0.25, 0.75), glow=12.0, extrude=0.05)
    T.box("Neon_lijn", (0, 5.42, 3.2), (4.2, 0.05, 0.05), S._glowmat("neon_blauw", (0.2, 0.6, 1.0), 10), bevel=0, ol=0)
    for x in (-1.6, 1.6, 3.2, 4.8):
        T.cyl(f"Paaltje_{x}", (x, 3.0, 0), 0.04, 0.95, T.toon("chroom_paaltje", (0.8, 0.82, 0.85)), seg=12, ol=0)
    for a, b in ((1.6, 3.2), (3.2, 4.8)):
        T.to_mesh(T.tube(f"Koord_{a}", [(a, 3.0, 0.9), ((a + b) / 2, 3.0, 0.72), (b, 3.0, 0.9)], 0.025, T.toon("stof_fluweel_rood", (0.6, 0.04, 0.08))))
    T.point_light("Clublicht_roze", (0, 3.5, 3.0), color=(1.0, 0.3, 0.8), energy=600, radius=0.5)
    T.point_light("Lantaarn", (-6, 0, 5), color=(1.0, 0.75, 0.45), energy=900, radius=0.3)
    P.lamp_post("Lantaarnpaal", (-6, 0.5, 0), on=True)
    T.character((0.2, 1.6, 0), rot_z=10)
    cams = [T.camera("CAM_8c_DOLLY", (-6, -4, 1.7), (0.5, 4.0, 1.4), lens=24)]
elif VAR == "bruiloft":
    P.ground("Gazon_bruiloft", (80, 80), (0.30, 0.55, 0.20), z=0)
    T.to_mesh(T.tube("Trouwboog", [(-1.4, 6, 0), (-1.4, 6, 2.2), (0, 6, 2.9), (1.4, 6, 2.2), (1.4, 6, 0)], 0.07,
                     T.toon("hout_boog_wit", (0.95, 0.94, 0.9))))
    bl = [T.sphere(f"Boogbloem_{k}", (math.cos(a) * 1.45, 6, 2.2 + math.sin(a) * 0.7 if 0 < a < math.pi else 1.0), 0.16,
                   T.toon(["bloem_wit", "bloem_roze"][k % 2], [(0.97, 0.97, 0.95), (0.95, 0.6, 0.7)][k % 2]), seg=10, ol=0)
          for k, a in enumerate([i / 14 * math.pi for i in range(15)])]
    T.merge("Boogbloemen", bl, ol=0)
    for row in range(4):
        for s in (-1, 1):
            for k in range(4):
                T.box(f"Stoel_{row}_{s}_{k}", (s * (1.2 + k * 0.6), 3.0 - row * 1.0, 0), (0.45, 0.45, 0.45),
                      T.toon("hout_stoel_wit", (0.95, 0.95, 0.93)), bevel=0.02, ol=0)
    for k in range(3):
        x = -6 + k * 6
        T.cyl(f"Ronde_tafel_{k}", (x, -6, 0), 0.9, 0.76, T.toon("stof_tafelkleed", (0.97, 0.97, 0.95)), seg=32, ol=0)
        ND.bloemen(f"Tafelbloemen_{k}", (x, -6, 0.76), rot_z=k * 40, seed=k).rotation_euler.x = 0
    P.string_lights("Lichtsnoer_bruiloft", [(-9, -9, 3.0), (-3, -3, 3.3), (3, -3, 3.3), (9, -9, 3.0)], sag=0.4)
    for k in range(6):
        P.tree(f"Tuinboom_{k}", (rnd.uniform(-20, 20), rnd.uniform(9, 20), 0), h=rnd.uniform(6, 9), r=3, seed=k)
    T.character((0.6, 5.2, 0), rot_z=180)
    cams = [T.camera("CAM_9a_WIJD", (0, -3.5, 1.7), (0, 6, 1.3), lens=26),
            T.camera("CAM_9c_TAFEL", (-3.5, -8.5, 1.4), (-6, -6, 1.0), lens=35)]
elif VAR == "brand":
    T.plane("Straat_brand", (0, 0, 0), (80, 20), T.toon("asfalt_nacht", (0.10, 0.10, 0.12)))
    T.box("Stoep_brand", (0, 7, 0), (80, 4, 0.15), T.toon("stoep_nacht", (0.30, 0.30, 0.32)), bevel=0.02, ol=0)
    S.building("Brandende_flat", (0, 9.5, 0), w=18, d=12, floors=7, color=(0.62, 0.55, 0.50), lit=0.15, seed=4)
    vuur = ND.pbr("vuur_gloed", (1.0, 0.5, 0.1), emit=(1.0, 0.48, 0.1), strength=18.0)
    rook = T.toon("rook_donker", (0.12, 0.11, 0.11))
    vl, rk = [], []
    for k in range(8):
        x, z = rnd.uniform(-7, 7), 1.0 + rnd.randint(1, 6) * 3.1 + 0.6
        vl.append(T.sphere(f"Vlam_{k}", (x, 9.4, z + 0.6), rnd.uniform(0.5, 0.9), vuur, scale=(1, 0.4, 1.8), seg=10, ol=0))
        for j in range(4):
            rk.append(T.sphere(f"Rook_{k}_{j}", (x + rnd.uniform(-1, 1), 9.0 + j * 0.4, z + 2 + j * 1.6), 1.0 + j * 0.5, rook, seg=10, ol=0))
    T.merge("Vlammen", vl, ol=0)
    T.merge("Rookwolken", rk, ol=0)
    for k in range(5):
        T.point_light(f"Vuurlicht_{k}", (rnd.uniform(-7, 7), 8.0, rnd.uniform(4, 20)), color=(1.0, 0.45, 0.12), energy=2500, radius=1.0)
    for k, x in enumerate((-12, 12)):
        T.box(f"Brandweerwagen_{k}", (x, 2.5, 0.3), (8, 2.5, 2.6), T.toon("lak_brandweer_rood", (0.75, 0.05, 0.04)), bevel=0.15, ol=0)
        T.box(f"Brandweerwagen_{k}_ladder", (x, 2.5, 2.95), (7, 0.6, 0.25), T.toon("metaal_ladder", (0.75, 0.77, 0.8)), bevel=0.02, ol=0)
        T.box(f"Zwaailicht_{k}", (x + 3.2, 2.5, 2.9), (0.6, 1.6, 0.18), S._glowmat("zwaailicht_blauw", (0.2, 0.4, 1.0), 15), bevel=0.02, ol=0)
        for wx in (-2.8, 2.8):
            T.cyl(f"Brandweerwiel_{k}_{wx}", (x + wx, 1.2, 0.5), 0.5, 0.3, T.toon("rubber_band", (0.04, 0.04, 0.05)), rot=(90, 0, 0), seg=18, ol=0)
    T.character((2.0, 5.0, 0.15), rot_z=180)
    cams = [T.camera("CAM_10a_WIJD", (-4, -12, 2.2), (0, 9, 8), lens=22),
            T.camera("CAM_10c_DEUR", (3.5, -1.5, 1.3), (0.5, 9.0, 1.2), lens=28)]
elif VAR == "vliegtuig":
    T.box("Romp_binnen_vloer", (0, 0, 0), (2.2, 6, 0.1), T.toon("metaal_vloer_traanplaat", (0.45, 0.47, 0.5)), bevel=0, ol=0)
    for s in (-1, 1):
        T.box(f"Romp_wand_{s}", (s * 1.1, 0, 0), (0.1, 6, 2.1), T.toon("metaal_romp_binnen", (0.62, 0.64, 0.66)), bevel=0, ol=0)
    T.box("Romp_plafond", (0, 0, 2.1), (2.3, 6, 0.1), T.toon("metaal_romp_binnen", (0.62, 0.64, 0.66)), bevel=0, ol=0)
    T.box("Romp_buiten", (0, 0, -0.3), (2.6, 14, 2.8), T.toon("metaal_romp_wit", (0.88, 0.89, 0.9)), bevel=0.4, ol=0).visible_camera = False
    # deuropening in de rechterwand
    bpy.data.objects["Romp_wand_1"].scale.y = 0.55
    bpy.data.objects["Romp_wand_1"].location.y = -1.4
    for k in range(5):
        T.box(f"Monitor_wetenschapper_{k}", (-0.95, -2.2 + k * 0.8, 1.0), (0.1, 0.6, 0.4),
              S._glowmat("labscherm_vliegtuig", (0.2, 0.6, 1.0), 2.5), bevel=0.01, ol=0)
    wm = T.toon("wolk_wit", (0.97, 0.97, 0.98))
    wl = [T.sphere(f"Wolk_{k}", (rnd.uniform(-400, 400) + 300, rnd.uniform(-400, 400), -600 + rnd.uniform(-20, 20)), rnd.uniform(25, 70),
                   wm, scale=(1.6, 1.2, 0.5), seg=12, ol=0) for k in range(120)]
    T.merge("Wolkendek", wl, ol=0)
    T.character((0.85, 1.5, 0.05), rot_z=-90)
    cams = [T.camera("CAM_10e_DEUR", (-0.7, -2.6, 1.5), (1.6, 2.0, 0.6), lens=20)]
else:  # maisveld
    P.ground("Akker", (300, 300), (0.48, 0.38, 0.22), z=0)
    mm = T.toon("blad_mais", (0.42, 0.62, 0.18))
    ms = []
    for i in range(70):
        for j in range(40):
            x, y = -35 + i * 1.0, -10 + j * 0.8
            if math.hypot(x, y - 4) < 4.5:
                continue
            ms.append(T.cyl(f"Mais_{i}_{j}", (x + rnd.uniform(-0.1, 0.1), y, 0), 0.04, rnd.uniform(1.8, 2.3), mm, r2=0.01, seg=5, ol=0))
    T.merge("Maisplanten", ms, ol=0)
    T.cyl("Krater_mais", (0, 4, -0.6), 3.2, 0.62, T.toon("aarde_krater", (0.32, 0.22, 0.13)), r2=4.4, seg=32, ol=0)
    T.cyl("Kraterwal", (0, 4, 0), 4.6, 0.35, T.toon("aarde_wal", (0.40, 0.29, 0.17)), r2=4.0, seg=32, ol=0)
    stof = [T.sphere(f"Stofwolk_{k}", (rnd.uniform(-4, 4), 4 + rnd.uniform(-3, 3), rnd.uniform(1, 5)), rnd.uniform(1.2, 2.6),
                     ND.pbr("stof_wolk", (0.65, 0.55, 0.42), rough=1.0, alpha=0.18), seg=12, ol=0) for k in range(14)]
    T.merge("Stofwolk", stof, ol=0)
    T.character((0.3, 3.0, -0.1), rot_z=200)
    cams = [T.camera("CAM_10g_WIJD", (-14, -14, 6), (0, 4, 1), lens=24),
            T.camera("CAM_10h_KRATER", (4.8, -3.8, 1.5), (0.3, 3.2, 0.5), lens=32)]
blend, renders = T.finish(OUT, VAR, cams)
print("KLAAR", blend, renders)
