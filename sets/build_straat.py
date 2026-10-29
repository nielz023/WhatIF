"""Set: Straat en woonwijk met het huis van de hoofdrolspeler.
Varianten (één script, verschillende .blend-bestanden):
    zonnig    dag 2 en 12: zonnig, blauwe lucht
    suvs      dag 15: drie zwarte SUV's voor het huis
    avond     dag 10: voordeur en veranda, buitenlamp aan, gevallen boodschappentassen
    lente     dag 18: bloesembomen, pollen in de lucht, springkussen bij de buren
    scherven  dag 18 na de nies: alle ramen kapot, glas overal
    konvooi   dag 20: bewolkt, legertrucks, dranghekken, helikopter, de gezinsauto

Video 2 (10x sneller):
    grijs     dag 3-4 en cold open: grijze ochtend, vuilniswagen met koplampen aan, kraai en plastic
              zak die stilhangen, kliko's aan de straat, mama's tekst op het voorraam
    dageraad  dag 2 bij zonsopkomst: lege straat, bestelbus, stadsbus bij de halte, fiets, vogels

Gebruik:
    blender -b -P sets/build_straat.py -- <variant> [uitvoermap]
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
from lib import street as S  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
VAR = args[0] if args else "zonnig"
V2 = VAR in ("grijs", "dageraad")
OUT = args[1] if len(args) > 1 else ("/mnt/project-files/videos/10x-sneller/sets/05_straat" if V2 else "/mnt/project-files/sets/05_straat")

mood_name = {"zonnig": "dag", "suvs": "dag", "lente": "dag", "scherven": "dag", "avond": "avond", "konvooi": "bewolkt",
             "grijs": "bewolkt", "dageraad": "ochtend"}[VAR]
mood = dict(T.MOODS[mood_name])
if VAR == "lente":
    mood.update(sky_horizon=(0.80, 0.86, 1.0), lit_tint=(1.0, 0.97, 0.95))
if VAR == "grijs":
    mood.update(sky_top=(0.22, 0.25, 0.30), sky_horizon=(0.46, 0.48, 0.52), ground_glow=(0.3, 0.32, 0.34),
                sun_strength=0.3, ambient=(0.26, 0.28, 0.31), fog_color=(0.48, 0.50, 0.54), fog_start=15.0, fog_end=160.0,
                fog_max=0.65, bloom=0.5)
if VAR == "dageraad":
    mood.update(sun_rot=(80, 0, 95), sun_strength=0.9, sky_top=(0.30, 0.42, 0.80), sky_horizon=(1.0, 0.66, 0.42),
                ambient=(0.30, 0.28, 0.34), fog_start=25.0, fog_end=260.0, fog_max=0.5, bloom=0.6)
T.new_scene("Straat_" + VAR, mood, samples=32)
rnd = random.Random(11)

# ---------------------------------------------------------------------------
# Wegprofiel (y): huizen noord op y=13, tuinen 8.5..13, stoep 6..8.5, fietspad 4.5..6,
# rijbaan -3.5..4.5, stoep -6..-3.5, tuinen -10.5..-6, huizen zuid op y=-10.5
# ---------------------------------------------------------------------------
T.use_collection(T.collection("Straat"))
LEN = 160
P.ground("Gras", (600, 600), (0.24, 0.50, 0.18), z=-0.02)
T.plane("Rijbaan", (0, 0.5, 0.0), (LEN, 8), T.toon("asfalt", (0.22, 0.22, 0.25)))
for k in range(-LEN // 2 + 2, LEN // 2, 6):
    T.plane(f"Middenstreep_{k}", (k, 0.5, 0.005), (3, 0.15), P.m("wit"))
T.plane("Fietspad", (0, 5.25, 0.01), (LEN, 1.5), T.toon("fietspad", (0.62, 0.25, 0.20)))
T.plane("Stoep_noord", (0, 7.25, 0.12), (LEN, 2.5), T.pattern("stoeptegels", (0.66, 0.65, 0.62), (0.63, 0.62, 0.60), grout=(0.5, 0.5, 0.5), size=(0.5, 0.5), mortar=0.02))
T.plane("Stoep_zuid", (0, -4.75, 0.12), (LEN, 2.5), T.pattern("stoeptegels", (0.66, 0.65, 0.62), (0.63, 0.62, 0.60), grout=(0.5, 0.5, 0.5), size=(0.5, 0.5), mortar=0.02))
T.box("Stoeprand_noord", (0, 6.0, 0), (LEN, 0.15, 0.13), T.toon("stoeprand", (0.75, 0.74, 0.72)), bevel=0.01, ol=0)
T.box("Stoeprand_zuid", (0, -3.5, 0), (LEN, 0.15, 0.13), T.toon("stoeprand", (0.75, 0.74, 0.72)), bevel=0.01, ol=0)
T.box("Stoeprand_fietspad", (0, 4.5, 0), (LEN, 0.15, 0.06), T.toon("stoeprand", (0.75, 0.74, 0.72)), bevel=0.01, ol=0)
T.plane("Tuinen_noord", (0, 10.75, 0.01), (LEN, 4.5), T.toon("gras_tuin", (0.28, 0.56, 0.20)))
T.plane("Tuinen_zuid", (0, -8.25, 0.01), (LEN, 4.5), T.toon("gras_tuin", (0.28, 0.56, 0.20)))

# ---------------------------------------------------------------------------
# Rijtjeshuizen aan beide kanten. Het huis van de hoofdrolspeler: noord, x = 0.
# ---------------------------------------------------------------------------
T.use_collection(T.collection("Huizen"))
BRICKS = [(0.72, 0.38, 0.26), (0.80, 0.55, 0.38), (0.62, 0.30, 0.22), (0.85, 0.75, 0.60), (0.70, 0.45, 0.35), (0.92, 0.88, 0.80)]
DOORS = [(0.15, 0.35, 0.75), (0.80, 0.15, 0.12), (0.15, 0.55, 0.35), (0.95, 0.75, 0.15), (0.35, 0.25, 0.55)]
lit = VAR in ("avond", "grijs")
lit_p = 0.25 if VAR == "grijs" else 0.7
broken = VAR == "scherven"
for side, fy, facing in (("noord", 13.0, -1), ("zuid", -10.5, 1)):
    for k, x in enumerate(range(-66, 67, 6)):
        hero = side == "noord" and x == 0
        nm = "Huis_hoofdpersonage" if hero else f"Huis_{side}_{x}"
        S.terraced_house(nm, x, fy, color=(0.95, 0.88, 0.72) if hero else BRICKS[(k * 7 + (side == "zuid")) % 6],
                         door_color=(0.85, 0.20, 0.15) if hero else DOORS[(k * 3 + (side == "zuid")) % 5],
                         facing=facing, lit=lit and rnd.random() < lit_p or (VAR == "avond" and hero), broken=broken and abs(x) < 50)
        if abs(x) < 40:
            S.front_garden(nm + "_tuin", x, fy, depth=4.5, facing=facing, flowers=abs(x) < 20)

# ---------------------------------------------------------------------------
# Straatmeubilair: lantaarnpalen, bomen, bushalte, geparkeerde auto's
# ---------------------------------------------------------------------------
T.use_collection(T.collection("Straatmeubilair"))
for x in range(-60, 61, 15):
    P.lamp_post(f"Lantaarn_n_{x}", (x + 3, 6.4, 0.12), h=5, on=lit)
    P.lamp_post(f"Lantaarn_z_{x}", (x - 4, -3.9, 0.12), h=5, on=lit)
BLOSSOM = VAR == "lente"
for k, x in enumerate(range(-63, 64, 10)):
    for y in (7.9, -5.4):
        t = P.tree(f"Straatboom_{x}_{y}", (x + (2 if y < 0 else 0), y, 0.12), h=7.0, r=2.2, seed=k + (y < 0))
        if BLOSSOM:
            for i, ms in enumerate(t.material_slots):
                if ms.material and ms.material.name.startswith("boomblad"):
                    ms.material = T.toon("bloesem", (0.98, 0.62, 0.78) if (k % 2) else (1.0, 0.80, 0.88))
S.bus_stop("Bushalte", (24, 7.6, 0.12), rot=0)
car_cols = [(0.10, 0.35, 0.80), (0.85, 0.15, 0.12), (0.92, 0.92, 0.92), (0.15, 0.15, 0.18), (0.95, 0.70, 0.10), (0.30, 0.60, 0.35)]
if VAR != "konvooi":
    for k, x in enumerate([-38, -26, -9, 14, 31, 47]):
        P.car(f"Auto_geparkeerd_{k}", (x, 3.4, 0), rot=180, color=car_cols[k % 6])
    for k, x in enumerate([-44, -18, 6, 40]):
        P.car(f"Auto_overkant_{k}", (x, -2.4, 0), rot=0, color=car_cols[(k + 3) % 6])

# ---------------------------------------------------------------------------
# Varianten
# ---------------------------------------------------------------------------
T.use_collection(T.collection("Variant_" + VAR))
porch_light = None
if VAR in ("avond", "zonnig", "suvs", "lente", "scherven"):
    # veranda van het huis: deurmat, buitenlamp, potplanten (voordeur op x = -1.4)
    T.box("Deurmat", (-1.4, 11.75, 0.02), (0.9, 0.55, 0.02), T.toon("deurmat", (0.55, 0.35, 0.18)), bevel=0.005, ol=0.004)
    lampm = T.glow("veranda_lamp", (1.0, 0.8, 0.45), 6) if lit else T.toon("veranda_lamp_uit", (0.95, 0.92, 0.8))
    T.box("Buitenlamp_houder", (-0.5, 12.93, 1.9), (0.16, 0.1, 0.32), P.m("zwart"), bevel=0.02, ol=0.005)
    T.box("Buitenlamp_glas", (-0.5, 12.86, 1.93), (0.12, 0.06, 0.24), lampm, bevel=0.01, ol=0)
    if lit:
        T.point_light("Verandalicht", (-0.5, 12.6, 1.9), color=(1.0, 0.72, 0.4), energy=60, radius=0.1)
    for k, x in enumerate((-2.55, -0.25)):
        T.cyl(f"Potplant_pot_{k}", (x, 12.5, 0.0), 0.2, 0.4, T.toon("pot_terra", (0.80, 0.40, 0.25)), r2=0.16, seg=16, ol=0.008)
        T.sphere(f"Potplant_{k}", (x, 12.5, 0.63), 0.3, P.m("boomblad2"), seg=14, ol=0.01)

if VAR == "avond":
    # dag 10: boodschappentassen gevallen, appels rollen weg
    for k, (x, y, r) in enumerate([(-1.0, 11.4, 70), (-1.9, 11.2, -40)]):
        bag = T.box(f"Boodschappentas_{k + 1}", (x, y, 0.02), (0.38, 0.24, 0.45), T.toon("papieren_tas", (0.78, 0.60, 0.38)), rot=(0, 75 if k == 0 else 0, r), bevel=0.02, ol=0.006)
    apples = [(-1.4 + rnd.uniform(-0.8, 0.8), 11.1 - rnd.uniform(0, 2.4), 0.065 if i < 5 else 0.185) for i in range(9)]
    P.points_mesh("Appels", apples, 0.045, T.toon("appel_rood", (0.85, 0.1, 0.08)), seg=12)

if VAR == "suvs":
    for k, x in enumerate((-6.5, 0.5, 7.5)):
        suv = P.car(f"SUV_zwart_{k + 1}", (x, 3.2, 0), rot=180, color=(0.05, 0.05, 0.06), kind="suv")
        suv.scale = (1.15, 1.12, 1.25)

if VAR == "lente":
    S.bouncy_castle("Springkussen_buren", (-6.2, 10.6, 0.02), rot=8)
    for k, x in enumerate((-8.6, -3.6)):
        for o in S.balloons(f"Ballonnen_tuin_{k}", (x, 8.7, 0.9), n=5, seed=k):
            pass
    pollen = [(rnd.uniform(-25, 25), rnd.uniform(-4, 14), rnd.uniform(0.3, 6)) for _ in range(900)]
    P.points_mesh("Pollen", pollen, 0.025, T.glow("pollen", (1.0, 0.92, 0.55), 1.4), seg=6)
    petals = [(rnd.uniform(-25, 25), rnd.uniform(-5, 14), 0.14) for _ in range(500)]
    P.points_mesh("Bloesemblaadjes_grond", petals, 0.05, T.toon("bloesem", (0.98, 0.62, 0.78)), seg=6).scale.z = 0.2

if VAR == "scherven":
    shards = []
    for _ in range(1400):
        side = rnd.choice((-1, 1))
        y = rnd.uniform(6.2, 12.6) if side > 0 else rnd.uniform(-10.2, -3.7)
        shards.append((rnd.uniform(-45, 45), y, 0.14))
    P.points_mesh("Glasscherven", shards, 0.06, T.toon("glasscherf", (0.75, 0.90, 0.98)), seg=4).scale.z = 0.15
    # ook de auto's: ruiten eruit
    for o in bpy.data.objects:
        for ms in o.material_slots:
            if ms.material and ms.material.name == "autoruit":
                ms.material = T.toon("raam_kapot", (0.08, 0.09, 0.12))

if VAR == "konvooi":
    G = T.toon("legergroen", (0.24, 0.30, 0.16))
    for k, x in enumerate((-30, -18, -6, 12, 24)):
        S.army_truck(f"Legertruck_{k + 1}", (x, 2.2 if k % 2 else -1.2, 0), rot=180 if k % 2 else 0)
    # gezinsauto in het konvooi (het broertje zwaait door de achterruit)
    fam = P.car("Gezinsauto", (3.5, -1.2, 0), rot=0, color=(0.15, 0.45, 0.80))
    for k, x in enumerate(range(-40, 41, 3)):
        for y in (6.6, -4.2):
            P.railing(f"Dranghek_{x}_{y}", [(x - 1.25, y, 0.12), (x + 1.25, y, 0.12)], h=1.1, posts=2.5, color="metaal")
    S.helicopter("Helikopter", (8, 2, 32), rot=-15)
    for k, x in enumerate((-12, 0, 8)):
        T.box(f"Legerjeep_{k + 1}", (x - 40, -1.5, 0.5), (4.4, 2.0, 1.3), G, bevel=0.2, ol=0.02)

if VAR == "grijs":
    from lib import huis as HU  # noqa: E402
    S.garbage_truck("Vuilniswagen", (-13.0, 1.5, 0), rot=0, lights=True)
    S.bird("Kraai", (-4.0, 2.2, 4.3), rot_z=30, wings_up=40)
    S.plastic_bag("Plastic_zak", (-2.6, 1.6, 1.7))
    # vuilnisdag: kliko's aan de stoeprand
    for k, x in enumerate((-19.5, -7.6, 4.4, 10.5, 16.4)):
        kl = [T.box(f"Kliko_{k}_bak", (0, 0, 0.06), (0.58, 0.72, 0.98), T.toon("kliko_grijs", (0.32, 0.34, 0.36)), bevel=0.04),
              T.box(f"Kliko_{k}_deksel", (0, 0.02, 1.04), (0.62, 0.78, 0.05), T.toon("kliko_deksel", (0.15, 0.50, 0.25)), bevel=0.02)]
        T.merge(f"Kliko_{k + 1}", kl, ol=0.012).location = (x, 6.45, 0.12)
    # mama schrijft achterstevoren op het voorraam, zodat hij het buiten kan lezen
    for k, (tx, z) in enumerate((("COME INSIDE.", 2.12), ("WE'RE NOT", 1.84), ("SCARED.", 1.56))):
        HU.marker_text(f"Raamtekst_regel{k + 1}", tx, (1.2, 12.905, z), 0.17, "blauw")
    # markeringen voor de animatie (lege objecten)
    for nm, loc in (("Markering_broertje_oversteek", (-1.4, 1.2, 0.0)), ("Markering_stoeprand_dag3", (-10.0, 6.15, 0.12))):
        e = bpy.data.objects.new(nm, None)
        e.empty_display_type = "SINGLE_ARROW"
        e.location = loc
        T._link(e)

if VAR == "dageraad":
    S.delivery_van("Bestelbus", (-6.0, 1.5, 0), rot=0)
    S.city_bus("Stadsbus", (23.0, 1.45, 0), rot=0)
    S.bicycle("Fiets", (-22.0, 5.25, 0.01), rot=0)
    for k in range(12):
        S.bird(f"Vogel_{k + 1}", (2 + rnd.uniform(-6, 6), 1 + rnd.uniform(-3, 3), 9 + rnd.uniform(-1.5, 2.5)),
               rot_z=rnd.uniform(-30, 30), span=0.35, color=(0.12, 0.12, 0.15), wings_up=rnd.uniform(-20, 50))

# ---------------------------------------------------------------------------
# Hoofdpersonage en camera's
# ---------------------------------------------------------------------------
T.use_collection(None)
if VAR == "avond":
    T.character((-1.5, 10.6, 0.0), rot_z=0)
elif VAR == "konvooi":
    T.character((-1.0, 7.0, 0.12), rot_z=0)
elif VAR == "dageraad":
    T.character((-1.0, 5.25, 0.01), rot_z=90)
else:
    T.character((-2.0, 7.0, 0.12), rot_z=-10)

cams = {
    "zonnig": [T.camera("CAM_01_straat_wide", (-26, -1.5, 2.2), (6, 6, 2.5), lens=24),
               T.camera("CAM_02_huis_voorkant", (2.5, -2.0, 1.7), (0.0, 12.0, 3.0), lens=26),
               T.camera("CAM_03_stoep_laag", (-8, 6.8, 0.6), (4, 7.8, 1.4), lens=24)],
    "suvs": [T.camera("CAM_01_suvs_voor_huis", (-14, -2.0, 2.0), (2, 6, 1.6), lens=26),
             T.camera("CAM_02_vanuit_raam", (1.2, 12.5, 4.0), (1.0, 2.5, 0.8), lens=26)],
    "avond": [T.camera("CAM_01_veranda", (1.2, 7.6, 1.5), (-1.3, 12.6, 1.1), lens=26),
              T.camera("CAM_02_straat_avond", (-20, -1.5, 2.2), (4, 7, 2.5), lens=24)],
    "lente": [T.camera("CAM_01_lente_wide", (-22, -1.5, 2.0), (2, 7, 3.0), lens=24),
              T.camera("CAM_02_springkussen", (-1.5, 4.5, 1.6), (-6, 10.5, 1.2), lens=26)],
    "scherven": [T.camera("CAM_01_na_de_nies", (-22, -1.5, 2.0), (2, 7, 3.0), lens=24),
                 T.camera("CAM_02_scherven_laag", (-4, 6.8, 0.5), (2, 9.5, 1.2), lens=22)],
    "konvooi": [T.camera("CAM_01_konvooi_wide", (-38, 5.0, 4.0), (0, 0, 2.0), lens=24),
                T.camera("CAM_02_helikopter", (2, 4.9, 1.5), (8, 2, 30), lens=22),
                T.camera("CAM_03_gezinsauto", (-0.8, -1.4, 1.5), (3.5, -1.2, 1.1), lens=30)],
    "grijs": [T.camera("CAM_01_cold_open", (2.5, -2.2, 1.3), (-6.0, 2.6, 1.6), lens=24),
              T.camera("CAM_02_koplampen", (-2.8, 0.0, 0.6), (-13.0, 1.5, 1.5), lens=24),
              T.camera("CAM_03_raam_mama", (1.0, 9.6, 1.7), (1.2, 13.0, 1.85), lens=30),
              T.camera("CAM_04_stoeprand_wide", (12.0, -2.6, 1.7), (-8.0, 6.5, 1.6), lens=24)],
    "dageraad": [T.camera("CAM_01_lange_weg", (-40.0, 0.2, 1.1), (20.0, 1.6, 1.8), lens=35),
                 T.camera("CAM_02_bestelbus", (0.2, -0.3, 1.5), (-4.0, 1.5, 1.6), lens=26),
                 T.camera("CAM_03_bus_halte", (8.0, -2.2, 1.5), (24.0, 3.0, 1.8), lens=28)],
}[VAR]
blend, renders = T.finish(OUT, "straat_" + VAR, cams)
print("KLAAR", blend, renders)
