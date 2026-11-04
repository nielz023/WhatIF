"""Set (video 3, No Rules): de lege snelweg, het dierentuinhek en het tankstation.

Varianten:
    snelweg      scène 12a-12c: lege snelweg vol verlaten auto's met open deuren, vangrails,
                 matrixborden op zwart, aan de rand het open hek van CITY ZOO.
    tankstation  scène 8b: tankstation aan de stadsrand, prijsbord met losse cijfers
                 (Prijsbord_prijs_oud 1.89 / Prijsbord_prijs_nieuw 18.90).

Gebruik:
    python3 sets/build_snelweg.py <variant> [uitvoermap]
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

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
VAR = args[0] if args else "snelweg"
OUT = args[1] if len(args) > 1 else "/mnt/project-files/videos/geen-regels/sets/04_snelweg"

mood = dict(T.MOODS["dag" if VAR == "tankstation" else "bewolkt"])
if VAR == "snelweg":
    mood.update(sun_strength=0.7, sky_top=(0.42, 0.52, 0.66), sky_horizon=(0.86, 0.80, 0.70), fog_start=40.0, fog_end=380.0)
T.new_scene("Snelweg_" + VAR, mood, samples=32)
rnd = random.Random(12)
asfalt = T.toon("asfalt", (0.22, 0.22, 0.25))
verf = T.toon("wegverf_wit", (0.92, 0.92, 0.90))
CAR_COLS = [(0.85, 0.12, 0.10), (0.92, 0.92, 0.92), (0.12, 0.30, 0.75), (0.15, 0.15, 0.17), (0.95, 0.70, 0.10),
            (0.30, 0.60, 0.40), (0.60, 0.62, 0.66), (0.55, 0.20, 0.45)]


def snelweg():
    T.use_collection(T.collection("Snelweg"))
    P.ground("Berm", (900, 900), (0.40, 0.55, 0.26), z=-0.03)
    L = 500
    # twee rijbanen van 3 stroken (11 m) met middenberm
    for s in (1, -1):
        T.plane(f"Rijbaan_{s}", (0, s * 7.5, 0.0), (L, 11), asfalt)
        for k in (1, 2):
            for i in range(-L // 2, L // 2, 12):
                T.plane(f"Streep_{s}_{k}_{i}", (i, s * (2.0 + k * 3.67), 0.005), (4.5, 0.15), verf)
        T.plane(f"Kantstreep_{s}", (0, s * 2.3, 0.005), (L, 0.2), verf)
        T.plane(f"Kantstreep_buiten_{s}", (0, s * 12.7, 0.005), (L, 0.2), verf)
        P.railing(f"Vangrail_{s}", [(-L / 2, s * 13.4, 0), (L / 2, s * 13.4, 0)], h=0.75, posts=4.0, color="metaal", r=0.05)
    T.box("Middenberm", (0, 0, 0), (L, 3.6, 0.12), T.toon("beton_middenberm", (0.66, 0.65, 0.62)), bevel=0.02, ol=0)
    P.railing("Vangrail_midden", [(-L / 2, 0, 0.12), (L / 2, 0, 0.12)], h=0.75, posts=4.0, color="metaal", r=0.05)
    # portaal met matrixborden op zwart
    T.use_collection(T.collection("Portaal"))
    st = T.toon("staal_portaal", (0.55, 0.57, 0.60))
    for y in (-14.5, 14.5):
        T.box(f"Portaal_poot{y}", (60, y, 0), (0.5, 0.5, 7.0), st, bevel=0.02, ol=0)
    T.box("Portaal_ligger", (60, 0, 6.6), (0.6, 30, 0.9), st, bevel=0.02, ol=0)
    for i, y in enumerate((-11, -7.5, -4, 4, 7.5, 11)):
        T.box(f"Matrixbord_{i}", (59.6, y, 5.2), (0.2, 2.2, 1.3), T.toon("matrix_zwart", (0.04, 0.04, 0.05)), bevel=0.02, ol=0)
    S.label("Bord_richting", "CITY CENTRE  12", (59.6, -7.5, 4.2), 0.3, (1, 1, 1), rot=(90, 0, -90), extrude=0.01)
    # verlaten auto's kris-kras, veel met open deuren (scène 12a)
    T.use_collection(T.collection("Verlaten auto's"))
    k = 0
    x = -40
    while x < 170:
        for lane in range(rnd.randint(1, 3)):
            y = rnd.choice((-11.2, -7.5, -3.8, 3.8, 7.5, 11.2)) + rnd.uniform(-0.8, 0.8)
            rot = (0 if y < 0 else 180) + rnd.uniform(-25, 25)
            doors = rnd.choice([(), ("L",), ("R",), ("L", "R")])
            S.car2(f"Auto_{k}", (x + rnd.uniform(-3, 3), y, 0), rot=rot, color=CAR_COLS[k % 8],
                   kind=rnd.choice(["hatch", "sedan", "suv"]), doors_open=doors)
            k += 1
        x += rnd.uniform(9, 16)
    # spullen op de weg
    for i in range(10):
        T.box(f"Koffer_{i}", (rnd.uniform(-30, 150), rnd.uniform(-12, 12), 0), (0.5, 0.25, 0.7),
              T.toon(f"koffer_{i % 3}", [(0.15, 0.25, 0.5), (0.6, 0.15, 0.12), (0.2, 0.2, 0.22)][i % 3]),
              rot=(0, 0, rnd.uniform(0, 180)), bevel=0.04, ol=0)
    # dierentuin naast de snelweg: hek, muur, bord
    T.use_collection(T.collection("Dierentuin"))
    S.zoo_gate("Zoohek", (40, 24, 0), rot_z=0, open_deg=70)
    muur = T.toon("steen_zoo", (0.65, 0.6, 0.52))
    for s in (1, -1):
        T.box(f"Zoomuur_{s}", (40 + s * 23.5, 24, 0), (40, 0.6, 2.6), muur, bevel=0.03, ol=0)
    for i in range(6):
        P.tree(f"Zooboom_{i}", (14 + i * 10, 34, 0), h=8, r=3.2, seed=70 + i, kind="rond")
    T.plane("Zoopad", (40, 18.5, 0.003), (6, 10), T.toon("grindpad_aarde", (0.78, 0.68, 0.52)))
    S.sign("Bord_CITY_ZOO_EXIT", ["CITY ZOO", "EXIT 4"], (20, 14.6, 0), rot_z=-30, w=1.8, h=1.0, bg=(0.10, 0.45, 0.22), post_h=1.8)
    T.use_collection(None)
    T.character((8, -5, 0), rot_z=0)
    return [
        T.camera("CAM_01_track_fietsen", (0, -16, 2.0), (30, -4, 1.0), lens=24),
        T.camera("CAM_02_zoohek", (40, 8, 1.7), (40, 24, 2.4), lens=24),
        T.camera("CAM_03_zebra_tussen_autos", (22, -2, 1.3), (40, 6, 1.0), lens=28),
        T.camera("CAM_04_drone", (-30, -30, 30), (50, 0, 0), lens=28),
    ]


def tankstation():
    T.use_collection(T.collection("Tankstation"))
    P.ground("Terrein", (500, 500), (0.40, 0.55, 0.26), z=-0.03)
    T.plane("Weg", (0, -16, 0), (300, 10), asfalt)
    T.plane("Erf", (0, 2, 0.002), (40, 26), T.toon("beton_erf", (0.62, 0.62, 0.62)))
    st = T.toon("staal_luifel", (0.92, 0.92, 0.92))
    rood = T.toon("tank_rood", (0.88, 0.12, 0.10))
    for x in (-8, 8):
        for y in (-3, 5):
            T.box(f"Luifelpaal_{x}_{y}", (x, y, 0), (0.45, 0.45, 5.0), st, bevel=0.03, ol=0)
    T.box("Luifel", (0, 1, 5.0), (20, 12, 0.9), st, bevel=0.05, ol=0)
    T.box("Luifelband", (0, -5.02, 5.1), (20.05, 0.05, 0.6), rood, bevel=0, ol=0)
    for i, x in enumerate((-5, 0, 5)):
        T.box(f"Pompeiland_{i}", (x, 1, 0), (1.2, 4.5, 0.2), T.toon("beton_eiland", (0.75, 0.75, 0.72)), bevel=0.03, ol=0)
        T.box(f"Pomp_{i}", (x, 1, 0.2), (0.8, 0.6, 1.9), rood, bevel=0.06, ol=0)
        T.box(f"Pomp_scherm_{i}", (x, 0.69, 1.4), (0.5, 0.02, 0.3), T.glow("pompscherm", (0.6, 0.9, 1.0), 2.0), bevel=0, ol=0)
    T.box("Shop", (0, 12, 0), (16, 7, 3.6), T.toon("gevel_shop", (0.95, 0.95, 0.93)), bevel=0.04, ol=0)
    T.box("Shop_pui", (0, 8.45, 0), (12, 0.1, 2.8), T.toon("pui_glas", (0.20, 0.28, 0.36)), bevel=0.02, ol=0)
    S.label("Shop_naam", "FUEL & SHOP", (0, 8.4, 3.0), 0.5, (0.88, 0.12, 0.1), extrude=0.03)
    S.tankstation_bord("Prijsbord", (13, -8.5, 0), rot_z=-20, price="1.89")
    S.car2("Auto_pomp", (-2.5, 1, 0), rot=90, color=(0.12, 0.30, 0.75))
    T.use_collection(None)
    T.character((10.5, -8.0, 0), rot_z=160)
    return [
        T.camera("CAM_01_prijsbord", (10.6, -14.5, 2.6), (13, -8.5, 3.5), lens=35),
        T.camera("CAM_02_tankstation_wide", (-16, -20, 3), (2, 2, 2), lens=24),
    ]


cams = tankstation() if VAR == "tankstation" else snelweg()
blend, renders = T.finish(OUT, "snelweg_" + VAR if VAR != "tankstation" else "tankstation", cams)
print("KLAAR", blend, renders)
