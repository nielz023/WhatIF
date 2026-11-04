"""Set (video 3, No Rules): het winkelcentrum als 'koninkrijk' van de pestkop (dag 14).

Varianten:
    ingang   scène 15e: gevel van het winkelcentrum, barricade van winkelkarren, groot bord
             20 RULES (bovenaan 1. THE BOSS IS ALWAYS RIGHT.), de rode fiets van de vriend bij de deur.
    troon    scène 15f-15g: binnen in het atrium, troon van winkelkarren op een podium van pallets,
             kartonnen kroon op het kussen, regelbanier, roltrap stil, lege etalages.

Gebruik:
    python3 sets/build_koninkrijk.py <variant> [uitvoermap]
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
VAR = args[0] if args else "ingang"
OUT = args[1] if len(args) > 1 else "/mnt/project-files/videos/geen-regels/sets/07_winkelcentrum"

if VAR == "troon":
    mood = dict(T.MOODS["binnen"])
    mood.update(ambient=(0.26, 0.26, 0.32), sun_strength=0.35, bloom=0.3, exposure=-0.9)
else:
    mood = dict(T.MOODS["bewolkt"])
    mood.update(sun_strength=0.7, exposure=0.05)
T.new_scene("Koninkrijk_" + VAR, mood, samples=32)
rnd = random.Random(15)

RULES20 = ["1. THE BOSS IS ALWAYS RIGHT.", "2. BOW WHEN YOU ENTER.", "3. PAY TO GET IN.", "4. NO CRYING.",
           "5. THE BOSS EATS FIRST.", "6. NO LAUGHING AT THE CROWN.", "7. CARTS BELONG TO THE BOSS.",
           "8. KNOCK TWICE.", "9. NO SHOES ON THE THRONE.", "10. SAY PLEASE, BOSS.", "11. NO SITTING.",
           "12. NO RUNNING IN MY MALL!", "13. NO WHISPERING.", "14. LINE UP FOR SNACKS.", "15. THE BOSS PICKS MUSIC.",
           "16. NO ASKING WHY.", "17. ONE WISH PER WEEK.", "18. NO BIKES. (EXCEPT MINE)", "19. CLAP FOR THE BOSS.",
           "20. SEE RULE 1."]


def ingang():
    T.use_collection(T.collection("Gevel"))
    P.ground("Parkeerterrein", (400, 400), (0.32, 0.32, 0.35), z=-0.03)
    for k in range(12):
        T.plane(f"Parkeervak_{k}", (-20 + k * 3.6, -16, 0.0), (0.12, 5), T.toon("wegverf_wit", (0.92, 0.92, 0.9)))
    gevel = T.toon("gevel_mall", (0.86, 0.84, 0.80))
    T.box("Mall_romp", (0, 12, 0), (60, 24, 11), gevel, bevel=0.05, ol=0)
    T.box("Mall_luifel", (0, -0.8, 4.2), (18, 3.2, 0.4), T.toon("luifel_mall", (0.20, 0.45, 0.72)), bevel=0.04, ol=0)
    T.box("Mall_glaspui", (0, -0.05, 0), (14, 0.12, 4.2), T.glass("mall_glas", (0.55, 0.70, 0.85), alpha=0.35), bevel=0.01, ol=0)
    T.box("Mall_binnen_donker", (0, 0.6, 0), (14, 0.1, 4.2), T.toon("binnen_schemer", (0.15, 0.16, 0.20)), bevel=0, ol=0)
    S.label("Mall_naam", "CITY MALL", (0, -0.15, 6.2), 1.4, (0.20, 0.45, 0.72), extrude=0.05)
    # karton eroverheen geplakt
    T.box("Karton_MALL", (6.2, -0.24, 6.0), (6.0, 0.03, 1.8), T.toon("karton", (0.78, 0.62, 0.40)), rot=(0, 3, 0), bevel=0.01, ol=0)
    from lib import huis as HU
    HU.marker_text("Karton_KINGDOM", "KINGDOM", (6.2, -0.27, 6.55), 0.75, "zwart")
    # barricade: winkelkarren, planken, verkeersbord
    T.use_collection(T.collection("Barricade"))
    for i in range(9):
        x = -12 + i * 1.0 if i < 4 else 4.5 + (i - 4) * 1.0
        S.winkelkar(f"Barricade_kar_{i}", (x, -4.2 + rnd.uniform(-0.2, 0.2), 0), rot=rnd.uniform(-20, 20), tipped=(i % 4 == 1))
    plank = T.toon("plank_steigerhout", (0.70, 0.56, 0.36))
    for i, (x, rz) in enumerate(((-9.5, 4), (-7.8, -6), (6.5, 3), (8.3, -5))):
        T.box(f"Barricade_plank_{i}", (x, -4.25, 0.75), (2.6, 0.06, 0.22), plank, rot=(0, rz, 0), bevel=0.01, ol=0)
    S.sign("Barricade_STOP", ["STOP"], (-4.6, -4.4, 0), rot_z=0, w=0.65, h=0.65, bg=(0.85, 0.1, 0.1), post_h=1.2)
    # het grote regelbord naast de deur
    T.use_collection(T.collection("20 RULES"))
    S.regelbord("Regelbord_20_RULES", (-12.5, -1.6, 0), rot_z=8, w=4.6, h=3.4, rules=RULES20, title="20 RULES", size=0.1)
    # de rode fiets van de vriend bij de deur
    T.use_collection(T.collection("Rode fiets"))
    S.fiets2("Fiets_vriend_rood", (3.6, -1.1, 0), rot=-8, color=(0.85, 0.12, 0.10), sticker=True)
    S.vlag("Vlag_koninkrijk_l", (-7.5, -2.8, 0), color=(0.95, 0.75, 0.15), h=3.4)
    S.vlag("Vlag_koninkrijk_r", (7.5, -2.8, 0), color=(0.95, 0.75, 0.15), h=3.4)
    T.use_collection(None)
    T.character((1.5, -8, 0), rot_z=0)
    return [T.camera("CAM_01_ingang_pushin", (0, -20, 1.8), (0, 0, 3.2), lens=26),
            T.camera("CAM_02_regelbord", (-10.5, -6.5, 1.8), (-12.5, -1.6, 2.4), lens=35),
            T.camera("CAM_03_rode_fiets", (5.2, -4.0, 1.0), (3.6, -1.1, 0.7), lens=35)]


def troon():
    T.use_collection(T.collection("Atrium"))
    W, D, H = 30.0, 26.0, 11.0
    vloer = T.pattern("vloer_mall", (0.88, 0.86, 0.82), (0.80, 0.78, 0.74), size=(1.0, 1.0), kind="tegels")
    muur = T.toon("muur_mall", (0.92, 0.90, 0.86))
    T.box("Vloer", (0, 0, -0.1), (W, D, 0.1), vloer, bevel=0, ol=0)
    for nm, loc, size in (("Muur_achter", (0, D / 2, 0), (W, 0.3, H)), ("Muur_links", (-W / 2, 0, 0), (0.3, D, H)),
                          ("Muur_rechts", (W / 2, 0, 0), (0.3, D, H))):
        T.box(nm, loc, size, muur, bevel=0, ol=0)
    # tweede verdieping (galerij) met balustrade
    T.box("Galerij_l", (-W / 2 + 3, 0, 4.6), (6, D, 0.4), muur, bevel=0.02, ol=0)
    T.box("Galerij_r", (W / 2 - 3, 0, 4.6), (6, D, 0.4), muur, bevel=0.02, ol=0)
    for s in (1, -1):
        T.box(f"Balustrade_{s}", (s * (W / 2 - 6), 0, 5.0), (0.08, D, 1.0), T.glass("balustrade_glas", (0.7, 0.85, 0.95), alpha=0.3), bevel=0, ol=0)
    # glazen dak (licht valt binnen)
    T.box("Glasdak", (0, 0, H), (W, D, 0.1), T.glass("glasdak", (0.80, 0.90, 1.0), alpha=0.2), bevel=0, ol=0)
    for k in range(7):
        T.box(f"Dakligger_{k}", (0, -D / 2 + k * D / 6, H - 0.3), (W, 0.25, 0.3), T.toon("staal_wit", (0.9, 0.9, 0.9)), bevel=0, ol=0)
    T.area_light("Daklicht", (0, 0, H - 0.5), (0, 0, 0), size=(W - 4, D - 4), color=(1.0, 0.98, 0.95), energy=1800)
    # lege etalages
    for i, y in enumerate((-8, 0, 8)):
        for s in (1, -1):
            T.box(f"Etalage_{s}_{i}", (s * (W / 2 - 0.25), y, 0), (0.1, 6.5, 3.6), T.toon("etalage_donker", (0.16, 0.18, 0.22)), bevel=0, ol=0)
            S.label(f"Etalagenaam_{s}_{i}", ["SHOES", "TOYS", "PHONES", "SPORT", "BOOKS", "CANDY"][i + (3 if s > 0 else 0)],
                    (s * (W / 2 - 0.35), y, 3.9), 0.5, (0.2, 0.45, 0.72), rot=(90, 0, -90 * s), extrude=0.02)
    # roltrap (stil)
    T.box("Roltrap", (-6.5, 4, 0), (1.4, 8.0, 0.2), T.toon("metaal_roltrap", (0.6, 0.62, 0.65)), rot=(30, 0, 0), bevel=0.02, ol=0)
    # podium van pallets met de troon
    T.use_collection(T.collection("Troon"))
    pal = T.toon("hout_pallet", (0.78, 0.64, 0.44))
    for i in range(3):
        for j in range(2):
            T.box(f"Pallet_{i}_{j}", (-1.25 + i * 1.25, 6.0 + j * 1.0, 0), (1.2, 0.8, 0.15), pal, bevel=0.01, ol=0)
            T.box(f"Pallet_{i}_{j}_b", (-1.25 + i * 1.25, 6.0 + j * 1.0, 0.15), (1.2, 0.8, 0.15), pal, bevel=0.01, ol=0)
    S.troon("Troon_pestkop", (0, 6.6, 0.3), rot_z=0)
    S.kroon("Kroon_karton", (0.0, 6.55, 1.43), rot_z=0)
    T.box("Loper_rood", (0, 1.0, 0.001), (1.6, 9.0, 0.01), T.toon("stof_loper_rood", (0.75, 0.08, 0.12)), bevel=0, ol=0)
    S.regelbord("Regelbanier_20", (0, 12.6, 1.8), rot_z=0, w=6.0, h=4.2, rules=RULES20, title="20 RULES", size=0.13, stand=False)
    for i, x in enumerate((-4, 4)):
        S.vlag(f"Vlag_troon_{i}", (x, 7.0, 0), color=(0.95, 0.75, 0.15), h=3.0)
    for i, (x, y) in enumerate([(-3, 2), (3, 2), (-2, -1), (2, -1)]):
        S.mark(f"MARK_volgeling_{i}", (x, y, 0), rot_z=180)
    S.winkelkar("Snackkar", (3.2, 5.4, 0), rot=-30)
    T.use_collection(None)
    T.character((2.2, 4.6, 0), rot_z=180)
    return [T.camera("CAM_01_troon_medium", (0, -2.0, 1.6), (0, 6.6, 1.3), lens=30),
            T.camera("CAM_02_atrium_wide", (6, -11.5, 3.5), (0, 6, 2.0), lens=22),
            T.camera("CAM_03_kroon_close", (0.4, 4.6, 1.5), (0, 6.75, 1.5), lens=50)]


cams = troon() if VAR == "troon" else ingang()
blend, renders = T.finish(OUT, "winkelcentrum_" + VAR, cams)
print("KLAAR", blend, renders)
