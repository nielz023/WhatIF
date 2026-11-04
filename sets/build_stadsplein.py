"""Set (video 3, No Rules): het stadsplein met de raadszaal, regelborden en grote schermen.

Varianten:
    jaar1        scène 18f: zonnig voorjaar, één enorm houten bord vol handgeschreven regels,
                 een ladder ertegen (iemand schrijft er nog één bij).
    jaar10       scène 20a-20f: avond, het plein vol regelborden, ronde tafel van de stadsraad,
                 lampjes aan, klok aan de raadszaal op 23:59:58 (wijzers draaien om y).
                 Bovenaan het grote bord in oma's handschrift: 1. NOBODY GOES HUNGRY. (zie RULES).
    middernacht  scène 21a-21k: zelfde plein, alle schermen rood met TEST COMPLETE.
                 Tekstlagen per scherm (zichtbaarheid wisselen): Scherm_N_tekst_test / _result / _phase.
                 Blauwe streep van de ochtend aan de horizon.

Gebruik:
    python3 sets/build_stadsplein.py <variant> [uitvoermap]
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
VAR = args[0] if args else "jaar10"
OUT = args[1] if len(args) > 1 else "/mnt/project-files/videos/geen-regels/sets/06_stadsplein"

if VAR == "jaar1":
    mood = dict(T.MOODS["dag"])
    mood.update(sky_horizon=(0.80, 0.88, 1.0), lit_tint=(1.0, 0.98, 0.92), exposure=0.1)
elif VAR == "jaar10":
    mood = dict(T.MOODS["avond"])
    mood.update(ambient=(0.20, 0.20, 0.34), exposure=0.15)
else:
    mood = dict(T.MOODS["nacht"])
    mood.update(sky_horizon=(0.10, 0.20, 0.45), ambient=(0.12, 0.14, 0.26), exposure=0.15)
T.new_scene("Stadsplein_" + VAR, mood, samples=32)
rnd = random.Random(20)
NIGHT = VAR != "jaar1"

RULES = ["1. NOBODY GOES HUNGRY.", "2. SHARE THE WATER.", "3. NO TAKING WHAT ISN'T YOURS.", "4. HELP YOUR NEIGHBOUR.",
         "5. KIDS GO TO SCHOOL.", "6. BIKES ON THE LEFT.", "7. QUIET AFTER 10 PM.", "8. FIX WHAT YOU BREAK.",
         "9. EVERYONE GETS A VOTE.", "10. NO DOGS IN THE GARDENS.", "11. PLANT BEFORE YOU HARVEST.",
         "12. BE HOME BEFORE DARK.", "13. SWAP, DON'T STEAL.", "14. LIGHTS OUT AT MIDNIGHT."]

# ---------------------------------------------------------------------------
# Plein: klinkers, raadszaal (noord), gevels rondom, fontein
# ---------------------------------------------------------------------------
T.use_collection(T.collection("Plein"))
P.ground("Ondergrond", (500, 500), (0.42, 0.40, 0.38), z=-0.03)
T.plane("Klinkers", (0, 0, 0.0), (60, 50), T.pattern("klinkers_plein", (0.62, 0.52, 0.44), (0.55, 0.46, 0.40), size=(0.4, 0.2), kind="tegels"))
steen = T.toon("steen_raadszaal", (0.86, 0.80, 0.70))
T.box("Raadszaal", (0, 29, 0), (26, 12, 12), steen, bevel=0.05, ol=0)
T.box("Raadszaal_trap", (0, 21.4, 0), (12, 3.6, 0.5), steen, bevel=0.02, ol=0)
for i, x in enumerate((-4.5, -1.5, 1.5, 4.5)):
    T.cyl(f"Zuil_{i}", (x, 21.6, 0.5), 0.45, 7.0, T.toon("zuil_wit", (0.94, 0.92, 0.88)), seg=20, ol=0)
T.box("Fronton", (0, 21.5, 7.5), (11, 1.4, 1.2), steen, bevel=0.03, ol=0)
S.label("Raadszaal_naam", "CITY HALL", (0, 20.75, 7.85), 0.7, (0.35, 0.28, 0.22), extrude=0.03)
T.box("Raadszaal_deur", (0, 22.95, 0.5), (2.6, 0.1, 3.6), T.toon("deur_eiken", (0.40, 0.26, 0.15)), bevel=0.02, ol=0)
for i, x in enumerate((-10, -7, 7, 10)):
    for j, z in enumerate((2.0, 6.5)):
        T.box(f"Raadszaal_raam_{i}_{j}", (x, 22.95, z), (1.6, 0.1, 2.6),
              T.glow("raam_raadszaal_warm", (1.0, 0.78, 0.45), 2.2) if NIGHT else T.toon("raam_raadszaal", (0.40, 0.55, 0.70)), bevel=0.02, ol=0)
S.muurklok("Raadsklok", (0, 22.85, 10.0), rot_z=0, hh=23, mm=59, r=1.1)
# gevels rond het plein
for i, x in enumerate((-50, -30, 30, 50)):
    S.building(f"Pleingevel_O{i}" if x > 0 else f"Pleingevel_W{i}", (x, 22, 0), w=18, d=10, floors=rnd.randint(4, 6),
               color=[(0.72, 0.60, 0.50), (0.55, 0.58, 0.64), (0.80, 0.72, 0.60), (0.76, 0.48, 0.38)][i], lit=0.5 if NIGHT else 0.0,
               seed=80 + i, block="P")
for i, y in enumerate((-18, 2)):
    S.building(f"Pleingevel_oost_{i}", (30, y, 0), w=18, d=10, floors=5, color=(0.70, 0.62, 0.55), lit=0.5 if NIGHT else 0.0,
               seed=90 + i, rot_z=-90, block="P", shop="MARKET" if i else None)
    S.building(f"Pleingevel_west_{i}", (-30, y, 0), w=18, d=10, floors=5, color=(0.58, 0.60, 0.66), lit=0.5 if NIGHT else 0.0,
               seed=95 + i, rot_z=90, block="P", shop="BAKERY" if i else None)
T.cyl("Fontein_bak", (0, -6, 0), 3.0, 0.6, steen, seg=40, ol=0)
T.cyl("Fontein_water", (0, -6, 0.0), 2.75, 0.55, T.toon("water_fontein", (0.25, 0.50, 0.70)), seg=40, ol=0)
T.cyl("Fontein_zuil", (0, -6, 0.5), 0.35, 1.8, steen, seg=16, ol=0)
for i, (x, y) in enumerate([(-14, -14), (14, -14), (-14, 6), (14, 6)]):
    P.tree(f"Pleinboom_{i}", (x, y, 0), h=6.5, r=2.4, seed=100 + i)
    P.bench(f"Pleinbank_{i}", (x + (2.5 if x < 0 else -2.5), y, 0), rot=90 if x < 0 else -90)
# zonnepanelen op de daken (jaar 10)
if VAR != "jaar1":
    for i in range(8):
        S.zonnepaneel(f"Dakpaneel_{i}", (-9 + i * 2.5, 30, 12.1), rot_z=180, w=1.2, d=2.0, tilt=25, legs=True)

# ---------------------------------------------------------------------------
# Regelborden
# ---------------------------------------------------------------------------
T.use_collection(T.collection("Regelborden"))
if VAR == "jaar1":
    S.regelbord("Regelbord_groot", (0, 12, 0), rot_z=0, w=6.5, h=4.2, rules=RULES[:12], title="OUR RULES", size=0.16)
    S.ladder("Ladder_regelbord", (2.2, 11.6, 0), rot_z=0, h=3.6, lean=14)
else:
    S.regelbord("Regelbord_groot", (0, 12, 0), rot_z=0, w=7.0, h=4.6, rules=RULES, title="OUR RULES", size=0.15)
    kleine = [("NEIGHBOURHOOD 4", ["BIKES ONLY", "NO MUSIC AFTER 10", "COMPOST ON FRIDAY"]),
              ("SCHOOL RULES", ["NO RUNNING", "RAISE YOUR HAND", "SHARE YOUR LUNCH"]),
              ("MARKET RULES", ["FAIR SWAPS ONLY", "NO PUSHING", "QUEUE HERE"]),
              ("WATER RULES", ["2 BUCKETS A DAY", "CLOSE THE TAP"]),
              ("GARDEN RULES", ["NO DOGS", "WATER AT DAWN", "TAKE ONLY 3"]),
              ("BRIDGE RULES", ["FREE FOR ALL", "WALK YOUR BIKE"])]
    spots = [(-12, 8, 25), (12, 8, -25), (-18, -4, 50), (18, -4, -50), (-9, -16, 10), (9, -16, -10)]
    for i, ((title, rules), (x, y, rz)) in enumerate(zip(kleine, spots)):
        S.regelbord(f"Regelbord_{i}", (x, y, 0), rot_z=rz, w=2.4, h=1.6, rules=rules, title=title, size=0.13)
    # ronde tafel van de stadsraad
    T.use_collection(T.collection("Stadsraad"))
    hout = T.toon("hout_raadstafel", (0.55, 0.36, 0.22))
    T.cyl("Raadstafel_blad", (0, 4, 0.74), 1.6, 0.06, hout, seg=40, ol=0)
    T.cyl("Raadstafel_poot", (0, 4, 0), 0.18, 0.74, hout, seg=16, ol=0)
    T.cyl("Raadstafel_voet", (0, 4, 0), 0.6, 0.05, hout, seg=24, ol=0)
    for k in range(7):
        a = k / 7 * math.tau + 0.2
        x, y = math.cos(a) * 2.15, 4 + math.sin(a) * 2.15
        T.box(f"Raadsstoel_{k}", (x, y, 0.0), (0.45, 0.45, 0.46), hout, rot=(0, 0, math.degrees(a) + 90), bevel=0.02, ol=0)
        T.box(f"Raadsstoel_leuning_{k}", (math.cos(a) * 2.4, 4 + math.sin(a) * 2.4, 0.46), (0.45, 0.06, 0.5), hout,
              rot=(0, 0, math.degrees(a) + 90), bevel=0.02, ol=0)
        T.box(f"Papier_{k}", (math.cos(a) * 1.25, 4 + math.sin(a) * 1.25, 0.8), (0.21, 0.29, 0.003), T.toon("papier_wit", (0.97, 0.97, 0.95)),
              rot=(0, 0, math.degrees(a) + 90), bevel=0, ol=0)
    T.cyl("Pen_jongen", (math.cos(0.2) * 1.15 + 0.1, 4 + math.sin(0.2) * 1.15, 0.805), 0.006, 0.14, T.toon("pen_blauw", (0.1, 0.2, 0.7)),
          rot=(0, 90, 20), seg=8, ol=0)
    for k in range(3):
        S.kaars(f"Kaars_tafel_{k}", (math.cos(k * 2.1) * 0.5, 4 + math.sin(k * 2.1) * 0.5, 0.8), lit=True)
    # lichtsnoeren over het plein
    for i, (a, b) in enumerate([((-14, -14, 4.5), (14, 6, 4.5)), ((14, -14, 4.5), (-14, 6, 4.5))]):
        P.string_lights(f"Lichtsnoer_{i}", [a, b], sag=1.2, spacing=0.8, on=True)
    for i, x in enumerate((-20, 20)):
        P.lamp_post(f"Pleinlamp_{i}", (x, -10, 0), on=True)

# ---------------------------------------------------------------------------
# Schermen (jaar 10: uit/zwart; middernacht: rood met TEST COMPLETE)
# ---------------------------------------------------------------------------
if VAR != "jaar1":
    T.use_collection(T.collection("Schermen"))
    texts = {"test": ["TEST COMPLETE."], "result": ["RESULT:", "HUMANS CREATE NEW RULES", "WITHIN 9 DAYS."],
             "phase": ["PHASE 2 BEGINS", "AT SUNRISE."]}
    screens = [((0, 22.9, 0), 0, 12.3, 9, 3.6), ((-29.85, -18, 0), 90, 8, 6, 3.4), ((29.85, -18, 0), -90, 8, 6, 3.4)]
    # scherm op de raadszaal + twee op de zijgevels
    for i, (loc, rz, z, w, h) in enumerate(screens):
        nm = f"Scherm_{i + 1}"
        root = S._empty(nm, size=0.5)
        T.box(nm + "_frame", (0, 0.06, z - 0.15), (w + 0.3, 0.2, h + 0.3), T.toon("billboard_frame", (0.14, 0.15, 0.17)), bevel=0.04, ol=0).parent = root
        on = VAR == "middernacht"
        T.box(nm + "_vlak", (0, -0.06, z), (w, 0.04, h), S._glowmat(nm + "_licht", (0.85, 0.02, 0.02) if on else (0.02, 0.02, 0.03),
                                                                          2.6 if on else 0.2), bevel=0, ol=0).parent = root
        for key, lines in texts.items():
            g = S._empty(f"{nm}_tekst_{key}", size=0.2)
            g.parent = root
            n = len(lines)
            s = min(h / (n + 1) * 0.75, w / max(len(l) for l in lines) * 1.3)
            for j, ln in enumerate(lines):
                tz = z + h - (j + 1) * h / (n + 1) - s * 0.35
                S.label(f"{nm}_{key}_{j}", ln, (0, -0.09, tz), s, (1.0, 0.95, 0.9), glow=9.0, extrude=0.004).parent = g
            vis = on and key == "test"
            for o in [g] + list(g.children):
                o.hide_render = not vis
                o.hide_viewport = not vis
        root.location = loc
        root.rotation_euler.z = math.radians(rz)
        if on:
            lt = T.area_light(nm + "_rood_schijnsel", (0, 0, 0), (0, -1, 0), size=(w, h), color=(1.0, 0.05, 0.03), energy=3500)
            lt.parent = root
            lt.location = (0, -0.8, z)
            lt.rotation_euler = (math.radians(90), 0, 0)
    if VAR == "middernacht":
        # eerste blauwe streep van de ochtend aan de horizon (zuid)
        T.plane("Ochtendstreep", (0, -260, 18), (900, 40), S._glowmat("ochtendstreep", (0.25, 0.45, 1.0), 1.2), rot=(90, 0, 0))

T.use_collection(None)
T.character((1.2, 1.2, 0), rot_z=180 if VAR != "jaar1" else 0)
if VAR == "jaar1":
    cams = [T.camera("CAM_01_pullback_regelbord", (4, -6, 2.0), (0, 12, 2.8), lens=26),
            T.camera("CAM_02_ladder", (4.5, 7.0, 1.8), (1.8, 12, 3.2), lens=30)]
elif VAR == "jaar10":
    cams = [T.camera("CAM_01_crane_plein", (8, -24, 9), (0, 6, 1.5), lens=24),
            T.camera("CAM_02_raadstafel", (3.2, 0.2, 1.4), (0, 4.5, 0.9), lens=32),
            T.camera("CAM_03_regel_1", (0.5, 8.5, 3.2), (-2, 12, 4.8), lens=40),
            T.camera("CAM_04_klok", (0, 15, 9.6), (0, 22.85, 10.0), lens=45)]
else:
    cams = [T.camera("CAM_01_plein_bevroren", (6, -22, 4), (0, 10, 7), lens=24),
            T.camera("CAM_02_scherm_detail", (0, 10, 11.5), (0, 22.9, 14.1), lens=35),
            T.camera("CAM_03_pullback_horizon", (0, 18, 6), (0, -60, 4), lens=24)]
blend, renders = T.finish(OUT, "stadsplein_" + VAR, cams)
print("KLAAR", blend, renders)
