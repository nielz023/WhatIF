"""Set (video 3, No Rules): de brug (dag 7) en het lab van de wetenschapper aan de overkant.

Varianten:
    brug      scène 13a-13g: stalen boogbrug over de rivier, schemer met warm tegenlicht en
              lichte mist. Markeringen voor de pestkop + volgelingen en de jongens (10 m uit elkaar).
    lab_buiten scène 13h: klein bakstenen gebouw aan de overkant met één zonnepaneel op het dak
              en één brandende lamp. Deur "Labdeur" draait om z (op een kier -> open).
    lab_binnen scène 13i-13j: rommelig thuislab, kast met het doosje medicijnen
              ("Medicijndoos_kast"), werkbank, één lamp aan, accu's en kabels.

Gebruik:
    python3 sets/build_brug.py <variant> [uitvoermap]
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
VAR = args[0] if args else "brug"
OUT = args[1] if len(args) > 1 else "/mnt/project-files/videos/geen-regels/sets/05_brug_lab"

if VAR == "lab_binnen":
    mood = dict(T.MOODS["binnen"])
    mood.update(ambient=(0.20, 0.20, 0.26), sun_strength=0.0, fog_max=0.0, bloom=0.6, exposure=0.2)
else:
    mood = dict(T.MOODS["zonsondergang"])
    mood.update(fog_start=25.0, fog_end=260.0, fog_max=0.55, sun_rot=(84, 0, 180), sun_strength=1.1,
                sun_disc=dict(color=(1.0, 0.75, 0.40), size=6.0, dir=(0, 4)))
T.new_scene("Brug_" + VAR, mood, samples=32)
rnd = random.Random(13)

# brug loopt langs y; de rivier langs x. Het lab staat aan de noordkant (y > 75).
staal = T.toon("staal_brug_groen", (0.20, 0.38, 0.32))
beton = T.toon("beton_brug", (0.66, 0.64, 0.60))
asfalt = T.toon("asfalt", (0.22, 0.22, 0.25))
BL = 120   # lengte van de overspanning


def omgeving():
    T.use_collection(T.collection("Rivier en oevers"))
    T.plane("Rivier", (0, 0, -4.0), (800, 110), T.toon("water_rivier", (0.18, 0.32, 0.42)))
    for s in (1, -1):
        T.box(f"Oever_{s}", (0, s * (55 + 150), -4.5), (800, 300, 4.5), T.toon("gras_oever", (0.32, 0.50, 0.24)), bevel=0, ol=0)
        T.box(f"Kademuur_{s}", (0, s * 55.5, -4.5), (800, 1.2, 4.6), beton, bevel=0.02, ol=0)
    # stad aan de horizon (zuid) en bomen aan de oevers
    S.skyline("Skyline_zuid", (0, -150), rows=2, per_row=14, seed=31, lit=0.15)
    for i in range(16):
        x = -110 + i * 15
        if abs(x) < 14:
            continue
        P.tree(f"Oeverboom_n{i}", (x, 62 + rnd.uniform(0, 6), 0), h=rnd.uniform(6, 9), r=2.8, seed=i)
        P.tree(f"Oeverboom_z{i}", (x, -62 - rnd.uniform(0, 6), 0), h=rnd.uniform(6, 9), r=2.8, seed=30 + i)


def brug():
    T.use_collection(T.collection("Brug"))
    W = 10.0
    T.box("Brugdek", (0, 0, -0.6), (W, BL, 0.6), beton, bevel=0.03, ol=0)
    T.plane("Brugdek_asfalt", (0, 0, 0.002), (6.4, BL), asfalt)
    for s in (1, -1):
        T.box(f"Stoep_{s}", (s * 4.1, 0, 0), (1.8, BL, 0.18), T.toon("stoep_tegels", (0.58, 0.57, 0.55)), bevel=0.01, ol=0)
        for i in range(-BL // 2, BL // 2, 10):
            T.plane(f"Streep_{s}_{i}", (0, i, 0.006), (0.15, 4.0), T.toon("wegverf_wit", (0.92, 0.92, 0.9))) if s == 1 else None
        # leuning
        P.railing(f"Leuning_{s}", [(s * 4.95, -BL / 2, 0.18), (s * 4.95, BL / 2, 0.18)], h=1.1, posts=2.0, color="metaal", r=0.035)
        # boog met hangers
        pts = [(s * 5.4, -BL / 2 + BL * t, 18 * math.sin(math.pi * t)) for t in [k / 40 for k in range(41)]]
        T.to_mesh(T.tube(f"Boog_{s}", pts, 0.45, staal))
        for k in range(1, 20):
            t = k / 20
            y = -BL / 2 + BL * t
            z = 18 * math.sin(math.pi * t)
            T.to_mesh(T.tube(f"Hanger_{s}_{k}", [(s * 5.4, y, 0.2), (s * 5.4, y, z)], 0.06, staal))
    for k in range(1, 8):  # dwarsverbanden tussen de bogen
        t = 0.25 + k / 16
        y = -BL / 2 + BL * t
        z = 18 * math.sin(math.pi * t)
        T.to_mesh(T.tube(f"Dwarsligger_{k}", [(-5.4, y, z), (5.4, y, z)], 0.18, staal))
    for y in (-BL / 2, BL / 2):
        T.box(f"Landhoofd_{y}", (0, y, -4.5), (12, 6, 4.5), beton, bevel=0.03, ol=0)
        T.box(f"Pijler_{y}", (0, y * 0.98, -4.5), (11, 2.0, 4.0), beton, bevel=0.03, ol=0)
    # aanloopweg aan beide kanten
    for s in (1, -1):
        T.plane(f"Aanloop_{s}", (0, s * (BL / 2 + 40), 0.004), (6.4, 80), asfalt)
    # lantaarns op de brug (uit, dag 7 is er geen stroom)
    for i, y in enumerate(range(-50, 51, 20)):
        S.street_lamp(f"Bruglantaarn_{i}", (4.6 * (1 if i % 2 else -1), y, 0.18), rot_z=-90 if i % 2 else 90, on=False, block="Z", h=5.0)
    # spullen van de pestkop: een kratje als 'tolhuisje' en een karton TOLL
    T.use_collection(T.collection("Tol van de pestkop"))
    T.box("Kratje_tol", (-1.6, 3.0, 0), (0.5, 0.4, 0.35), T.toon("plastic_krat_rood", (0.85, 0.15, 0.12)), bevel=0.03, ol=0)
    S.sign("Bord_TOLL", ["TOLL", "PAY HERE"], (-2.6, 3.6, 0), rot_z=0, w=0.9, h=0.6, bg=(0.78, 0.62, 0.40),
           fg=(0.10, 0.08, 0.08), post_h=0.5, marker=True)
    S.winkelkar("Winkelkar_brug", (2.2, 4.2, 0), rot=60)
    # markeringen voor de animatie
    for i, x in enumerate((-1.8, -0.6, 0.6, 1.8)):
        S.mark(f"MARK_pestkop_rij_{i}", (x, 2.0, 0), rot_z=180)
    S.mark("MARK_jongen", (-0.8, -8.0, 0), rot_z=0)
    S.mark("MARK_vriend_met_fiets", (0.9, -8.2, 0), rot_z=0)
    S.fiets2("Fiets_held", (-1.6, -8.6, 0), rot=90, color=(0.15, 0.35, 0.75))
    S.fiets2("Fiets_vriend", (1.7, -8.6, 0), rot=90, color=(0.85, 0.12, 0.10), sticker=True)


def lab_gebouw():
    T.use_collection(T.collection("Lab buiten"))
    Y = BL / 2 + 22
    steen = T.toon("baksteen_lab", (0.62, 0.32, 0.24))
    T.box("Lab_romp", (9, Y, 0), (10, 8, 4.2), steen, bevel=0.04, ol=0)
    T.box("Lab_dak", (9, Y, 4.2), (10.6, 8.6, 0.3), T.toon("dakrand_zink", (0.45, 0.47, 0.50)), bevel=0.03, ol=0)
    S.zonnepaneel("Zonnepaneel_lab", (10.5, Y + 0.5, 4.5), rot_z=180, w=1.6, d=2.4, tilt=28, legs=True)
    # deur (draait om z) en ramen met dichte luiken op één na
    deur = S._empty("Labdeur", (6.0, Y - 4.1, 0), size=0.2)
    T.box("Labdeur_blad", (0.5, 0, 0), (1.0, 0.06, 2.2), T.toon("deur_lab_blauw", (0.18, 0.30, 0.45)), bevel=0.02, ol=0).parent = deur
    deur.rotation_euler.z = math.radians(-25)   # op een kier
    T.box("Labdeur_kozijn", (6.5, Y - 4.0, 0), (1.25, 0.08, 2.35), T.toon("kozijn_wit", (0.92, 0.92, 0.9)), bevel=0.01, ol=0)
    T.box("Labdeur_binnen_donker", (6.5, Y - 4.05, 0.0), (1.0, 0.02, 2.2), T.toon("binnen_donker", (0.05, 0.05, 0.07)), bevel=0, ol=0)
    for i, x in enumerate((8.8, 11.6)):
        lit = i == 0
        T.box(f"Labraam_{i}", (x, Y - 4.03, 1.1), (1.4, 0.05, 1.3),
              T.glow("raam_lab_warm", (1.0, 0.78, 0.45), 2.5) if lit else T.toon("luik_hout", (0.40, 0.30, 0.22)), bevel=0.01, ol=0)
    T.box("Buitenlamp", (6.5, Y - 4.15, 2.55), (0.18, 0.18, 0.25), S._glowmat("buitenlamp_lab", (1.0, 0.8, 0.5), 10.0), bevel=0.02, ol=0)
    T.point_light("Buitenlamp_licht", (6.5, Y - 4.6, 2.5), color=(1.0, 0.75, 0.45), energy=120, radius=0.1)
    T.point_light("Labraam_licht", (8.8, Y - 4.8, 1.6), color=(1.0, 0.75, 0.45), energy=60, radius=0.3)
    S.sign("Bord_lab", ["DR. LAB", "KNOCK"], (4.6, Y - 4.4, 0), rot_z=0, w=0.6, h=0.35, bg=(0.95, 0.95, 0.92), fg=(0.1, 0.1, 0.12), post_h=1.0)
    for i in range(4):
        T.cyl(f"Accu_{i}", (12.5 + i * 0.5, Y - 4.4, 0), 0.18, 0.4, T.toon("accu_zwart", (0.08, 0.08, 0.09)), seg=12, ol=0)
    T.plane("Erf_lab", (9, Y - 6, 0.008), (14, 4), T.toon("grindpad_aarde", (0.78, 0.68, 0.52)))


def lab_binnen():
    T.use_collection(T.collection("Lab binnen"))
    W, D, H = 7.0, 6.0, 3.0
    vloer = T.pattern("vloer_lab", (0.48, 0.46, 0.44), (0.42, 0.40, 0.38), size=(0.5, 0.5), kind="tegels")
    muur = T.toon("muur_lab", (0.78, 0.76, 0.70))
    T.box("Vloer", (0, 0, -0.1), (W, D, 0.1), vloer, bevel=0, ol=0)
    T.box("Plafond", (0, 0, H), (W, D, 0.1), muur, bevel=0, ol=0)
    T.box("Muur_achter", (0, D / 2, 0), (W, 0.15, H), muur, bevel=0, ol=0)
    T.box("Muur_links", (-W / 2, 0, 0), (0.15, D, H), muur, bevel=0, ol=0)
    T.box("Muur_rechts", (W / 2, 0, 0), (0.15, D, H), muur, bevel=0, ol=0)
    # voormuur met deur (wegklapbaar voor de camera: aparte objecten)
    T.box("Muur_voor_l", (-2.3, -D / 2, 0), (2.4, 0.15, H), muur, bevel=0, ol=0)
    T.box("Muur_voor_r", (2.3, -D / 2, 0), (2.4, 0.15, H), muur, bevel=0, ol=0)
    T.box("Muur_voor_boven", (0, -D / 2, 2.2), (2.2, 0.15, 0.8), muur, bevel=0, ol=0)
    hout = T.toon("hout_werkbank", (0.55, 0.38, 0.24))
    metaal = T.toon("metaal_kast", (0.55, 0.60, 0.62))
    # werkbank met spullen
    T.box("Werkbank", (-1.0, 2.4, 0.9), (3.6, 0.9, 0.06), hout, bevel=0.01, ol=0)
    for x in (-2.7, 0.7):
        for y in (2.05, 2.75):
            T.box(f"Werkbankpoot_{x}_{y}", (x, y, 0), (0.07, 0.07, 0.9), hout, bevel=0.005, ol=0)
    T.box("Microscoop_voet", (-2.0, 2.4, 0.96), (0.25, 0.3, 0.05), metaal, bevel=0.01, ol=0)
    T.to_mesh(T.tube("Microscoop_arm", [(-2.0, 2.52, 0.98), (-2.0, 2.5, 1.3), (-2.0, 2.38, 1.42)], 0.03, metaal))
    for i in range(5):
        T.cyl(f"Reageerbuis_{i}", (-0.9 + i * 0.12, 2.5, 0.96), 0.02, 0.16, T.glass("reageerbuis", (0.7, 0.95, 0.8), alpha=0.4), seg=10, ol=0)
    T.box("Reageerbuisrek", (-0.66, 2.5, 0.96), (0.7, 0.12, 0.06), hout, bevel=0.005, ol=0)
    T.box("Laptop", (0.2, 2.35, 0.96), (0.5, 0.35, 0.02), T.toon("laptop_grijs", (0.35, 0.36, 0.38)), bevel=0.005, ol=0)
    T.box("Laptopscherm", (0.2, 2.53, 0.97), (0.5, 0.02, 0.33), T.toon("laptop_grijs", (0.35, 0.36, 0.38)), rot=(-12, 0, 0), bevel=0.005, ol=0)
    S.batterijen("Batterijen_werkbank", (-1.5, 2.2, 0.96), n=6)
    # bureaulamp (de enige lamp die brandt)
    T.cyl("Bureaulamp_voet", (0.9, 2.5, 0.96), 0.08, 0.02, metaal, seg=16, ol=0)
    T.to_mesh(T.tube("Bureaulamp_arm", [(0.9, 2.5, 0.98), (0.95, 2.45, 1.35), (0.75, 2.3, 1.45)], 0.015, metaal))
    T.cyl("Bureaulamp_kap", (0.75, 2.3, 1.35), 0.09, 0.12, T.toon("lampkap_groen", (0.15, 0.45, 0.30)), r2=0.04, seg=16, ol=0)
    T.spot_light("Bureaulamp_licht", (0.75, 2.3, 1.36), (0.2, 2.2, 0.9), color=(1.0, 0.82, 0.55), energy=180, angle=80)
    T.point_light("Kamer_vul", (0, 0, 2.6), color=(0.55, 0.65, 1.0), energy=180, radius=1.0)
    # medicijnkast met het doosje
    T.box("Medicijnkast", (2.6, 2.7, 0), (1.2, 0.5, 1.9), metaal, bevel=0.02, ol=0)
    for k, z in enumerate((0.5, 0.95, 1.4)):
        T.box(f"Kastplank_{k}", (2.6, 2.44, z), (1.1, 0.02, 0.02), metaal, bevel=0, ol=0)
    deur = S._empty("Medicijnkast_deur", (3.2, 2.44, 0.05), size=0.1)
    T.box("Medicijnkast_deurblad", (-0.6, 0, 0), (1.2, 0.03, 1.8), metaal, bevel=0.01, ol=0).parent = deur
    deur.rotation_euler.z = math.radians(170)   # wijd open, scharnier rechts (uit beeld van CAM_02)
    S.medicijndoos("Medicijndoos_kast", (2.4, 2.4, 1.42), rot_z=0)
    for i in range(3):
        T.box(f"Kastpotje_{i}", (2.65 + i * 0.16, 2.5, 1.42), (0.1, 0.1, 0.14), T.toon("potje_bruin", (0.45, 0.25, 0.12)), bevel=0.01, ol=0)
    # kabels, accu's en een whiteboard
    T.box("Whiteboard", (-W / 2 + 0.08, 0, 1.0), (0.04, 2.2, 1.2), T.toon("whiteboard_wit", (0.96, 0.96, 0.95)), bevel=0.01, ol=0)
    S.label("Whiteboard_tekst", "DAY 7  ?", (-W / 2 + 0.11, 0, 1.6), 0.18, (0.1, 0.2, 0.7), rot=(90, 0, 90), extrude=0.002)
    for i in range(3):
        T.cyl(f"Accu_binnen_{i}", (-2.6 + i * 0.45, -1.6, 0), 0.18, 0.4, T.toon("accu_zwart", (0.08, 0.08, 0.09)), seg=12, ol=0)
    T.to_mesh(T.tube("Kabel_rood", [(-2.6, -1.6, 0.4), (-1.5, 0.0, 0.02), (0.2, 1.8, 0.02), (0.8, 2.4, 0.95)], 0.012,
                     T.toon("kabel_rood", (0.8, 0.1, 0.08))))
    T.box("Toonbank", (0.2, 0.2, 0), (1.8, 0.7, 0.95), hout, bevel=0.02, ol=0)


if VAR == "brug":
    omgeving()
    brug()
    lab_gebouw()
    T.use_collection(None)
    T.character((-0.8, -8.0, 0), rot_z=0)
    cams = [
        T.camera("CAM_01_brug_wide", (0, -34, 2.2), (0, 6, 2.0), lens=30),
        T.camera("CAM_02_pestkop_close", (-0.5, -2.0, 1.5), (-0.6, 2.0, 1.4), lens=50),
        T.camera("CAM_03_jongen_close", (0.4, -4.0, 1.4), (-0.8, -8.0, 1.3), lens=50),
        T.camera("CAM_04_brug_zijkant", (-60, -30, 4), (0, 0, 5), lens=28),
    ]
elif VAR == "lab_buiten":
    omgeving()
    brug()
    lab_gebouw()
    T.use_collection(None)
    Y = BL / 2 + 22
    T.character((5.5, Y - 6.5, 0), rot_z=180)
    cams = [T.camera("CAM_01_lab_wide", (2, Y - 18, 2.0), (9, Y, 2.5), lens=26),
            T.camera("CAM_02_labdeur", (5.8, Y - 8.5, 1.6), (6.4, Y - 4, 1.4), lens=35)]
else:
    lab_binnen()
    T.use_collection(None)
    T.character((-2.4, 0.6, 0), rot_z=-30)
    cams = [T.camera("CAM_01_lab_binnen", (-1.5, -2.7, 1.7), (0.8, 2.2, 1.1), lens=22),
            T.camera("CAM_02_medicijnkast", (1.7, 1.0, 1.5), (2.5, 2.5, 1.4), lens=35)]
blend, renders = T.finish(OUT, VAR, cams)
print("KLAAR", blend, renders)
