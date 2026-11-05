"""Sets (video 4, Never Die): de toekomst.

Varianten:
    toren2200   scène 13a-13i: glazen kamer hoog in de witte EVERGREEN-toren (bed, glaswand, hologram met
                $40,000,000 PER DOSE), lange witte gang met alarmlichten en een schuifdeur, en het enorme raam
                aan het eind, 200 verdiepingen boven de stad met vliegende auto's.
    straat2200  scène 13j: de straat beneden met de krater in de stoep, glazen torens, hologrammen.
    museum      scène 14b: strak wit toekomstmuseum (jaar 10.000) met glazen vitrines: telefoon, sneaker, fiets
                en in de grootste vitrine een krukje (voor hem). Bordje THE LAST OLD HUMAN.

Schakelbaar voor de animatie:
    - alarm: materiaal "alarm_gang" (Emission Strength 0 = wit licht uit, ~8 = rood alarm) en "ganglicht_wit"
    - schuifdeur: object "Schuifdeur_blad" (location.x: 0 = dicht, 1.3 = open)
    - het raam (13i): "Eindraam_glas" verbergen op het moment dat hij erdoor springt; "Eindraam_scherven" tonen
    - krater (straat2200): "Krater" + "Krater_scherven"

Gebruik:
    python3 sets/build_toekomst.py <variant> [uitvoermap]
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
from lib import stad as S  # noqa: E402
from lib import huis as HU  # noqa: E402
from lib import nooitdood as ND  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
VAR = args[0] if args else "toren2200"
OUT = args[1] if len(args) > 1 else f"/mnt/project-files/videos/nooit-dood/sets/02_{VAR}"
rnd = random.Random(2200)

WIT = (0.95, 0.96, 0.97)
GROEN = (0.12, 0.64, 0.48)   # EVERGREEN-groen


def future_city(z0, n=80, seed=1, center=(0, 120), spread=(500, 400), lit=0.4):
    """Toekomststad: glazen torens in alle maten, ver onder of rond de camera."""
    r = random.Random(seed)
    for k in range(n):
        x = center[0] + r.uniform(-spread[0] / 2, spread[0] / 2)
        y = center[1] + r.uniform(0, spread[1])
        if abs(x) < 20 and y < center[1] + 30:
            continue
        ND.glazen_toren(f"Toren_{k}", (x, y, z0), w=r.uniform(10, 24), h=r.uniform(60, 420), seed=k, round_=(k % 3 == 0),
                        lit=lit, col=[(0.30, 0.50, 0.66), (0.70, 0.78, 0.84), (0.40, 0.58, 0.68), (0.88, 0.90, 0.92)][k % 4],
                        spits=(k % 4 == 1))
    T.plane("Stadsvloer", (center[0], center[1] + spread[1] / 2, z0 - 0.05), (spread[0] * 3, spread[1] * 3),
            T.toon("asfalt_toekomst", (0.18, 0.20, 0.24)))


def flying_cars(n, box, seed=4):
    r = random.Random(seed)
    for k in range(n):
        ND.vliegende_auto(f"Vliegende_auto_{k}", (r.uniform(box[0], box[1]), r.uniform(box[2], box[3]), r.uniform(box[4], box[5]) if len(box) > 4 else 20.0),
                          rot_z=r.choice((0, 180)) + r.uniform(-10, 10),
                          col=[(0.9, 0.92, 0.95), (0.85, 0.15, 0.2), (0.1, 0.12, 0.15), (0.95, 0.75, 0.2)][k % 4])


def hologram(name, loc, lines, w=1.6, h=0.9, col=(0.36, 0.92, 1.0), rot_z=0.0, cells=False):
    root = S._empty(name, size=0.3)
    pane = T.box(name + "_vlak", (0, 0, 0), (w, 0.01, h), ND.pbr(name + "_gloed", col, emit=col, strength=1.4, alpha=0.3), bevel=0, ol=0)
    pane.parent = root
    for k, ln in enumerate(lines):
        t = S.label(f"{name}_tekst{k}", ln, (0, -0.02, h * (0.12 if cells else 0.62) - k * h * 0.22), h * (0.13 if k == 0 else 0.09),
                    col, glow=5.0, extrude=0.002)
        t.parent = root
    if cells:
        gm = ND.pbr(name + "_cel", col, emit=col, strength=4.0, alpha=0.6)
        for k in range(7):
            a = k / 7 * 2 * math.pi
            c = T.sphere(f"{name}_cel{k}", (math.cos(a) * w * 0.18, -0.03, h * 0.62 + math.sin(a) * h * 0.18), h * 0.08, gm,
                         seg=12, ol=0)
            c.parent = root
        T.sphere(f"{name}_cel_kern", (0, -0.03, h * 0.62), h * 0.12, gm, seg=16, ol=0).parent = root
    root.location = loc
    root.rotation_euler.z = math.radians(rot_z)
    return root


if VAR == "toren2200":
    mood = dict(T.MOODS["dag"], sun_rot=(50, 0, 160), sky_top=(0.30, 0.50, 0.95), sky_horizon=(0.80, 0.88, 1.0),
                fog_color=(0.80, 0.88, 1.0), fog_start=250.0, fog_end=3500.0, fog_max=0.6, bloom=0.4, exposure=-0.6,
                ambient=(0.30, 0.33, 0.38))
    T.new_scene("EVERGREEN_toren", mood, samples=32)
    Z = 600.0     # verdieping 200
    # glazen kamer: x -3..3, y -2.5..2.5; voor (+y) en rechts (+x) helemaal glas
    T.use_collection(T.collection("Glazen kamer"))
    W, D, H = 6.0, 5.0, 3.2
    room = I.room("Kamer2200", W, D, H, wall_color=WIT, floor_color=(0.92, 0.93, 0.95), skirting=False,
                  holes={"back": [(0.2, W - 0.2, 0.0, H)], "right": [(0.2, D - 0.2, 0.0, H)], "front": [(2.4, 3.6, 0.0, 2.3)]},
                  hide=())
    for o in room.values():
        o.location.z += Z
    T.box("Kamer2200_glas_voor", (0, D / 2 + 0.05, Z), (W, 0.03, H), T.glass("glas_toren", (0.80, 0.92, 1.0), 0.12), bevel=0, ol=0)
    T.box("Kamer2200_glas_zij", (W / 2 + 0.05, 0, Z), (0.03, D, H), T.glass("glas_toren", (0.80, 0.92, 1.0), 0.12), bevel=0, ol=0)
    T.box("Bed2200", (-1.6, 0.6, Z), (1.1, 2.1, 0.45), T.toon("kunststof_bed_wit", (0.96, 0.97, 0.98)), bevel=0.08, ol=0)
    T.box("Bed2200_matras", (-1.6, 0.6, Z + 0.45), (1.0, 2.0, 0.16), T.toon("matras_mint", (0.70, 0.90, 0.85)), bevel=0.06, ol=0)
    T.box("Bed2200_kussen", (-1.6, 1.35, Z + 0.61), (0.7, 0.35, 0.12), T.toon("kussen_wit", (0.98, 0.98, 0.98)), bevel=0.05, ol=0)
    T.box("Lichtlijn_plafond", (0, 0, Z + H - 0.03), (4.5, 0.08, 0.02), T.glow("ganglicht_wit", (0.95, 0.98, 1.0), 2), bevel=0, ol=0)
    T.box("EVERGREEN_logo_muur", (-W / 2 + 0.07, -0.6, Z + 1.6), (0.02, 1.4, 0.35), T.toon("evergreen_groen", GROEN), bevel=0.01, ol=0)
    S.label("EVERGREEN_tekst", "EVERGREEN", (-W / 2 + 0.09, -0.6, Z + 1.66), 0.2, (1, 1, 1), rot=(90, 0, 90), extrude=0.005)
    hologram("Hologram_cellen", (1.0, -0.4, Z + 0.9), ["$40,000,000", "PER DOSE"], w=1.4, h=1.2, rot_z=-20, cells=True)
    T.area_light("Kamerlicht", (0, 0, Z + H - 0.1), (0, 0, Z), size=(5, 4), color=(0.95, 0.98, 1.0), energy=220)
    # observatieglas met de directeur erachter (voorwand -y heeft een glazen strook)
    T.box("Observatieglas", (0, -D / 2 - 0.05, Z + 0.6), (2.0, 0.03, 1.6), T.glass("glas_obs", (0.75, 0.88, 0.95), 0.2), bevel=0, ol=0)
    # gang: loopt van de kamer naar -y, 30 m lang, eindigt bij het grote raam
    T.use_collection(T.collection("Gang 2200"))
    GL = 30.0
    gy0 = -D / 2 - 0.1
    T.box("Gang_vloer", (0, gy0 - GL / 2, Z - 0.1), (3.4, GL, 0.1), T.pattern("labvloer_toekomst", (0.93, 0.94, 0.96),
                                                                               (0.88, 0.90, 0.93), grout=(0.8, 0.82, 0.86), size=(1.2, 1.2), mortar=0.004), bevel=0, ol=0)
    alarm = ND.pbr("alarm_gang", (0.9, 0.9, 0.92), emit=(1.0, 0.08, 0.05), strength=0.0)
    for s in (-1, 1):
        T.box(f"Gang_wand_{s}", (s * 1.76, gy0 - GL / 2, Z), (0.12, GL, 3.2), T.toon("lab_wit", WIT), bevel=0, ol=0)
        T.box(f"Gang_alarmlijn_{s}", (s * 1.69, gy0 - GL / 2, Z + 2.6), (0.02, GL, 0.08), alarm, bevel=0, ol=0)
        T.box(f"Gang_groene_band_{s}", (s * 1.69, gy0 - GL / 2, Z + 0.9), (0.02, GL, 0.06), T.toon("evergreen_groen", GROEN), bevel=0, ol=0)
        for k in range(5):
            T.box(f"Gang_paneel_{s}_{k}", (s * 1.69, gy0 - 3 - k * 5.5, Z + 0.3), (0.03, 2.4, 2.0), T.toon("paneel_wit", (0.90, 0.92, 0.95)),
                  bevel=0.03, ol=0)
    T.box("Gang_plafond", (0, gy0 - GL / 2, Z + 3.2), (3.6, GL, 0.1), T.toon("lab_wit", WIT), bevel=0, ol=0)
    gl_ = [T.box(f"Gang_lamp_{k}", (0, gy0 - 1.5 - k * 3, Z + 3.17), (0.5, 1.6, 0.04), T.glow("ganglicht_wit", (0.95, 0.98, 1.0), 5),
                 bevel=0, ol=0) for k in range(10)]
    T.merge("Gang_lampen", gl_, ol=0)
    T.area_light("Ganglicht", (0, gy0 - GL / 2, Z + 3.1), (0, gy0 - GL / 2, Z), size=(3, GL - 2), color=(0.95, 0.98, 1.0), energy=550)
    # schuifdeur halverwege (13f2)
    sd = [T.box("Schuifdeur_paneel", (0, 0, 0), (1.4, 0.08, 2.4), T.toon("staal_deur", (0.80, 0.83, 0.86)), bevel=0.02, ol=0),
          T.box("Schuifdeur_streep", (0, -0.045, 1.2), (1.3, 0.01, 0.06), T.toon("evergreen_groen", GROEN), bevel=0, ol=0)]
    sdo = T.merge("Schuifdeur_blad", sd, ol=0)
    sdo.location = (0.35, gy0 - 14, Z)
    T.box("Schuifdeur_kozijn", (0, gy0 - 14, Z + 2.4), (3.4, 0.2, 0.8), T.toon("lab_wit", WIT), bevel=0, ol=0)
    for s in (-1, 1):
        T.box(f"Schuifdeur_post_{s}", (s * 1.25, gy0 - 14, Z), (0.9, 0.2, 2.4), T.toon("lab_wit", WIT), bevel=0, ol=0)
    sdo.location.x = 0.0
    sdo.location.x = 0.35   # half dicht; 0 = helemaal dicht (opening 1.6 m)
    # eindraam
    ey = gy0 - GL
    T.box("Eindraam_kozijn", (0, ey, Z - 0.1), (3.6, 0.3, 0.2), T.toon("lab_wit", WIT), bevel=0, ol=0)
    T.box("Eindraam_kozijn_boven", (0, ey, Z + 3.0), (3.6, 0.3, 0.3), T.toon("lab_wit", WIT), bevel=0, ol=0)
    T.box("Eindraam_glas", (0, ey, Z), (3.4, 0.04, 3.0), T.glass("glas_eindraam", (0.80, 0.92, 1.0), 0.15), bevel=0, ol=0)
    sc = []
    gm = T.glass("glas_scherf", (0.85, 0.95, 1.0), 0.3)
    for k in range(60):
        sc.append(T.sphere(f"Scherf_{k}", (rnd.uniform(-1.6, 1.6), ey - rnd.uniform(0.2, 3.0), Z + rnd.uniform(0.2, 2.8)),
                           rnd.uniform(0.05, 0.16), gm, scale=(1, 0.15, 0.8), seg=8, ol=0,
                           rot=(rnd.uniform(0, 90), rnd.uniform(0, 90), rnd.uniform(0, 90))))
    sco = T.merge("Eindraam_scherven", sc, ol=0)
    sco.hide_render = sco.hide_viewport = True
    # de toren zelf (wit) en de stad ver beneden
    T.use_collection(T.collection("Toren en stad"))
    # gevel (+x en +y) gelijk met het glas van de kamer, achterkant (-y) gelijk met het eindraam van de gang
    tx0, tx1, ty0, ty1 = -21.0, W / 2 + 0.07, ey - 0.16, D / 2 + 0.07
    tc, tw = ((tx0 + tx1) / 2, (ty0 + ty1) / 2), (tx1 - tx0, ty1 - ty0)
    T.box("Toren_romp", (tc[0], tc[1], 0), (tw[0], tw[1], Z - 0.2), T.toon("gevel_toren_wit", (0.92, 0.93, 0.95)), bevel=0.2, ol=0)
    T.box("Toren_top", (tc[0], tc[1], Z + 3.25), (tw[0], tw[1], 40), T.toon("gevel_toren_wit", (0.92, 0.93, 0.95)), bevel=0.2, ol=0)
    # ramenbanden op de gevel zodat je ziet hoe hoog het is
    rb = [T.box(f"Toren_raamband_{k}", (tc[0], tc[1], Z - 4 - k * 4.0), (tw[0] + 0.06, tw[1] + 0.06, 0.5),
                T.toon("glas_raamband", (0.45, 0.62, 0.78)), bevel=0, ol=0) for k in range(40)]
    T.merge("Toren_raambanden", rb, ol=0)
    future_city(0.0, n=110, seed=3, center=(0, 40), spread=(1400, 1100), lit=0.3)
    future_city(-0.3, n=90, seed=5, center=(0, -1250), spread=(1400, 1150), lit=0.3)   # achter de toren (13g/13i: uitzicht uit het eindraam)
    flying_cars(22, (-120, 120, -140, 160), seed=9)
    for k in range(22):
        o = bpy.data.objects.get(f"Vliegende_auto_{k}")
        o.location.z = Z + rnd.uniform(-60, 20)
    T.use_collection(None)
    T.character((-0.75, 0.3, Z), rot_z=200)   # 13a: zit op de bedrand (pose in de animatie)
    cams = [T.camera("CAM_13a_KAMER_WIJD", (2.6, -2.1, Z + 1.8), (-1.4, 1.2, Z + 0.8), lens=20),
            T.camera("CAM_13a_VAN_BUITEN", (12, 14, Z + 2.5), (-0.5, 0.0, Z + 1.0), lens=28),
            T.camera("CAM_13b_HOLOGRAM", (0.1, -2.3, Z + 1.55), (1.0, -0.4, Z + 1.45), lens=30),
            T.camera("CAM_13f_GANG", (0, gy0 - 3, Z + 1.5), (0, ey, Z + 1.2), lens=26),
            T.camera("CAM_13g_RAAM", (0.3, ey + 0.7, Z + 1.6), (0, ey - 200, Z - 150), lens=24),
            T.camera("CAM_13i_SPRONG_BUITEN", (14, ey - 18, Z - 6), (0, ey - 2, Z + 1), lens=22)]
    blend, renders = T.finish(OUT, "toren2200", cams)

elif VAR == "straat2200":
    mood = dict(T.MOODS["dag"], sun_rot=(55, 0, 150), sky_horizon=(0.82, 0.90, 1.0), fog_start=80.0, bloom=0.5)
    T.new_scene("Straat_2200", mood, samples=32)
    T.use_collection(T.collection("Straat 2200"))
    T.plane("Rijbaan_licht", (0, 0, 0.0), (16, 400), T.toon("asfalt_toekomst", (0.18, 0.20, 0.24)))
    for s in (-1, 1):
        T.box(f"Stoep_{s}", (s * 13, 0, 0), (10, 400, 0.15), T.toon("stoep_toekomst", (0.82, 0.84, 0.86)), bevel=0.02, ol=0)
        T.box(f"Lichtstrook_{s}", (s * 8.1, 0, 0.0), (0.12, 400, 0.02), S._glowmat("lichtstrook_weg", (0.4, 0.9, 1.0), 6), bevel=0, ol=0)
    for k in range(26):
        s = 1 if k % 2 else -1
        y = -80 + (k // 2) * 26
        ND.glazen_toren(f"Toren_straat_{k}", (s * 30, y, 0), w=rnd.uniform(18, 26), h=rnd.uniform(80, 300), seed=k, round_=(k % 3 == 0),
                        lit=0.3, col=[(0.30, 0.50, 0.66), (0.70, 0.78, 0.84), (0.88, 0.90, 0.92)][k % 3])
    future_city(0.0, n=40, seed=5, center=(0, 200), spread=(800, 600), lit=0.3)
    # krater in de stoep waar hij landde
    kx, ky = 10.5, 4.0
    T.cyl("Krater", (kx, ky, 0.1), 1.9, 0.06, T.toon("beton_krater", (0.40, 0.40, 0.42)), r2=1.2, seg=32, ol=0)
    T.cyl("Krater_rand", (kx, ky, 0.0), 2.3, 0.22, T.toon("beton_krater_rand", (0.66, 0.67, 0.68)), r2=1.8, seg=32, ol=0)
    sc = [T.box(f"Krater_brok_{k}", (kx + math.cos(a) * rnd.uniform(1.8, 3.5), ky + math.sin(a) * rnd.uniform(1.8, 3.5), 0.15),
                (rnd.uniform(0.15, 0.45),) * 3, T.toon("stoep_toekomst", (0.82, 0.84, 0.86)),
                rot=(rnd.uniform(0, 60), rnd.uniform(0, 60), rnd.uniform(0, 90)), bevel=0.03, ol=0)
          for k, a in enumerate([rnd.uniform(0, 6.28) for _ in range(18)])]
    T.merge("Krater_scherven", sc, ol=0)
    for k in range(8):
        hologram(f"Straathologram_{k}", ((1 if k % 2 else -1) * 15.5, -30 + k * 12, 3.5), ["SALE" if k % 3 == 0 else "EVERGREEN",
                                                                                     "LIVE LONGER" if k % 3 else "-50%"],
                 w=3.0, h=1.8, rot_z=90 if k % 2 else -90, col=[(0.36, 0.92, 1.0), (1.0, 0.36, 0.84), (0.7, 1.0, 0.36)][k % 3])
    flying_cars(16, (-20, 20, -60, 200), seed=11)
    for k in range(16):
        o = bpy.data.objects.get(f"Vliegende_auto_{k}")
        o.location.z = rnd.uniform(8, 40)
    T.use_collection(None)
    T.character((kx, ky, 0.1), rot_z=200)
    cams = [T.camera("CAM_13j_KRATER", (2.5, -8.0, 1.9), (kx, ky + 1, 0.9), lens=24),
            T.camera("CAM_13j_HOOG", (-4, -20, 14), (kx, ky + 8, 0), lens=24)]
    blend, renders = T.finish(OUT, "straat2200", cams)

else:  # museum
    mood = dict(T.MOODS["binnen"], ambient=(0.22, 0.23, 0.26), sun_strength=0.0, fog_max=0.0, bloom=0.3, exposure=-0.5)
    T.new_scene("Museum_10000", mood, samples=32)
    T.use_collection(T.collection("Museumzaal"))
    W, D, H = 22.0, 14.0, 6.5
    room = I.room("Museum", W, D, H, wall_color=(0.97, 0.97, 0.98), floor_color=(0.93, 0.94, 0.95), skirting=False)
    room["floor"].data.materials[0] = T.pattern("museumvloer", (0.95, 0.95, 0.96), (0.91, 0.92, 0.94), grout=(0.86, 0.87, 0.9),
                                                size=(2.0, 2.0), mortar=0.003)
    T.box("Plafondlicht", (0, 0, H - 0.05), (W - 3, D - 3, 0.04), T.glow("plafond_museum", (0.96, 0.98, 1.0), 1.0), bevel=0, ol=0)
    T.area_light("Museumlicht", (0, 0, H - 0.2), (0, 0, 0), size=(W - 4, D - 4), color=(0.96, 0.98, 1.0), energy=1500)
    glas = T.glass("glas_vitrine", (0.88, 0.94, 1.0), 0.1)
    voet = T.toon("kunststof_vitrinevoet", (0.98, 0.98, 0.99))
    acc = S._glowmat("vitrine_rand", (0.55, 0.9, 1.0), 3.0)

    def vitrine(name, loc, size=(1.0, 1.0, 1.2), sokkel=0.9, label=None):
        x, y = loc
        T.box(name + "_sokkel", (x, y, 0), (size[0], size[1], sokkel), voet, bevel=0.03, ol=0)
        T.box(name + "_glas", (x, y, sokkel), size, glas, bevel=0.02, ol=0)
        T.box(name + "_lichtrand", (x, y, sokkel - 0.02), (size[0] + 0.02, size[1] + 0.02, 0.02), acc, bevel=0, ol=0)
        if label:
            T.box(name + "_bordje", (x, y - size[1] / 2 - 0.01, sokkel * 0.55), (size[0] * 0.8, 0.02, 0.22),
                  T.toon("bordje_zwart", (0.08, 0.08, 0.1)), bevel=0.005, ol=0)
            for k, ln in enumerate(label):
                S.label(f"{name}_bordtekst{k}", ln, (x, y - size[1] / 2 - 0.025, sokkel * 0.55 + 0.13 - k * 0.07), 0.045,
                        (0.95, 0.95, 0.95), extrude=0.001)
        return sokkel
    # kleine vitrines met spullen uit 2026
    z = vitrine("Vitrine_telefoon", (-7, 2.5), (0.8, 0.8, 0.8), 1.0, ["PHONE", "c. 2020"])
    T.box("Oude_telefoon", (-7, 2.5, z + 0.05), (0.075, 0.01, 0.15), T.toon("plastic_telefoon_zwart", (0.05, 0.05, 0.06)),
          rot=(-75, 0, 20), bevel=0.01, ol=0)
    T.box("Telefoon_standaard", (-7, 2.55, z), (0.12, 0.08, 0.05), T.toon("plexi_standaard", (0.9, 0.92, 0.95)), bevel=0.01, ol=0)
    z = vitrine("Vitrine_sneaker", (-3.5, 2.5), (0.9, 0.8, 0.8), 1.0, ["SHOE", "c. 2020"])
    HU.kapotte_sneaker("Oude_sneaker", (-3.5, 2.5, z), rot=30, color=(0.92, 0.92, 0.92))
    z = vitrine("Vitrine_fiets", (-6.5, -2.5), (2.2, 1.0, 1.4), 0.4, ["BICYCLE", "c. 2020"])
    S.fiets2("Oude_fiets", (-6.5, -2.5, z), rot=0, color=(0.85, 0.12, 0.10))
    # de grootste vitrine: hij op een krukje
    z = vitrine("Vitrine_hoofdpersonage", (4.0, 1.0), (2.4, 2.4, 2.8), 0.35, None)
    T.cyl("Krukje", (4.0, 1.1, z), 0.2, 0.5, T.toon("hout_krukje", (0.62, 0.42, 0.22)), seg=16, ol=0)
    T.box("Bordje_groot", (4.0, -0.25, 0.55), (2.0, 0.04, 0.42), T.toon("bordje_zwart", (0.08, 0.08, 0.1)), rot=(-20, 0, 0),
          bevel=0.01, ol=0)
    for k, ln in enumerate(["THE LAST OLD HUMAN.", "PLEASE DO NOT TAP THE GLASS."]):
        S.label(f"Bordje_groot_tekst{k}", ln, (4.0, -0.29 - k * 0.02, 0.74 - k * 0.12), 0.085 if k == 0 else 0.06,
                (0.95, 0.95, 0.95), rot=(70, 0, 0), extrude=0.002)
    for k in range(4):
        hologram(f"Museumhologram_{k}", (-10.9, -4 + k * 2.8, 2.6), [["2026", "THE PAST"], ["HUMANS", "USED TO AGE"],
                                                                      ["TUESDAY?", "UNKNOWN"], ["SPEAK", "ENGLISH?"]][k],
                 w=2.2, h=1.3, rot_z=-90, col=[(0.36, 0.92, 1.0), (1.0, 0.36, 0.84), (0.7, 1.0, 0.36), (1.0, 0.85, 0.4)][k])
    T.use_collection(None)
    T.character((4.0, 1.1, z + 0.5 - 0.45), rot_z=0)
    cams = [T.camera("CAM_14b_a_ZAAL", (-9.5, -6.2, 2.4), (3.0, 1.5, 1.4), lens=22),
            T.camera("CAM_14b_b_BORDJE", (4.0, -1.6, 0.85), (4.0, -0.25, 0.65), lens=45),
            T.camera("CAM_14b_c_VITRINE", (1.2, -3.5, 1.4), (4.0, 1.0, 1.6), lens=30)]
    blend, renders = T.finish(OUT, "museum", cams)
print("KLAAR", blend, renders)
