"""Sets voor video 5, "What If You Could See How Many Days Everyone Has Left?".

Regel voor ELKE set (script bijlage A en G.10): de set is DICHT. Binnen: vier muren, vloer en plafond
(geen verborgen voormuur meer: I.room(..., hide=())), ramen met een buitenbeeld. Buiten: in elke
kijkrichting gebouwen, bomen of heuvels tot aan de horizon. Na het bouwen draait lib/setcheck.py vanuit
elke camera (64x36 stralen) en schrijft setcheck.txt; een set is pas klaar als daar SCHOON staat.

Varianten (scènes):
    props               overzicht van alle props (getallen, kom, pan, beker, kinderwagen, hengel, brief ...)
    kruispunt_laat      0, 18   late middag, laag warm licht, 4 hoeken bebouwd, school op de NO-hoek
    kruispunt_grijs     8       grijze ochtend, zelfde set
    steiger_zomer       1b, 10  houten steiger in het meer, riet, bos rondom
    steiger_herfst      15a-e   eind zomer / eerste gele blaadjes
    steiger_mist        15e     mist over het water
    opa_avond           16a-e   opa's woonkamer: leunstoel, haardvuur, lamp, boekenkast
    opa_ochtend         16f     zelfde kamer, vuur uit, deken op de stoel, koud ochtendlicht
    begraafplaats       17a-b   grasheuvel, grafstenen, bomen, hek, stad op de achtergrond, motregen
    schoolwc            6a-b    tegels, wastafels, spiegels (echt spiegelend), tl-licht
    directeur           12a-c   kantoor directeur met raam op het schoolplein
    ziekenhuis          14      bed, monitor, gordijn, raam met stad, tv (MYSTERY KID SAVES 300)
    zwembad             9c      buitenbad: tegels, water, hek, ligstoelen
    gymzaal             13a-f, 13h2  300 stoelen, podium, tribune, plafond in losse panelen + lichtkoepels
    schoolplein         1a, 11  plein, hekken, bomen, gymzaal met plat dak in losse delen (bewolkt)
    schoolplein_regen   13g-j   zelfde, stortregen

Animatie-afspraken (namen in de .blend):
    PLEK_*                 empties waar personages staan (richting = pijl)
    Dak_deel_<i>_<j>       losse dakdelen gymzaal (instorten, 13h)
    Plafond_paneel_<i>_<j> losse plafondpanelen binnen (doorbuigen 13b, 13f3)
    Lichtkoepel_<k>        lichtkoepels (scheuren, 13f3)
    Bestelbus + PLEK_chauffeur   de chauffeur zit ALTIJD in beeld achter het stuur (G.12)
    VKL_* / VGL_*          verkeerslichten (materiaal <naam>_rood/_oranje/_groen, Emission Strength)

Gebruik:
    python3 sets/build_dagen_over.py <variant> [uitvoermap]
    SET_PCT=25 SET_SAMPLES=24 voor een snelle preview, SET_RENDER=0 voor alleen .blend + setcheck
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
from lib import interior as I  # noqa: E402
from lib import huis as H  # noqa: E402
from lib import nooitdood as ND  # noqa: E402
from lib import dagenover as D  # noqa: E402
from lib import setcheck  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
VAR = args[0] if args else "kruispunt_laat"
NR = {"props": "00", "kruispunt_laat": "01", "kruispunt_grijs": "01", "steiger_zomer": "02", "steiger_herfst": "02",
      "steiger_mist": "02", "opa_avond": "03", "opa_ochtend": "03", "begraafplaats": "04", "schoolwc": "05",
      "directeur": "06", "ziekenhuis": "07", "zwembad": "08", "gymzaal": "09", "schoolplein": "10",
      "schoolplein_regen": "10"}[VAR]
OUT = args[1] if len(args) > 1 else f"/mnt/project-files/videos/dagen-over/sets/{NR}_{VAR}"
rnd = random.Random(5)
M = T.MOODS

LAAT = dict(M["dag"], sun_color=(1.0, 0.78, 0.52), sun_strength=1.15, sun_rot=(74, 0, -55), lit_tint=(1.0, 0.86, 0.68),
            sky_horizon=(1.0, 0.80, 0.62), ambient=(0.40, 0.38, 0.44), fog_color=(1.0, 0.82, 0.66), bloom=0.35)
GRIJS = dict(M["bewolkt"], sun_strength=0.4)
MIST = dict(M["bewolkt"], fog_color=(0.80, 0.82, 0.84), fog_start=4.0, fog_end=60.0, fog_max=0.92, sun_strength=0.35)
REGEN = dict(M["bewolkt"], sky_top=(0.28, 0.31, 0.35), sky_horizon=(0.48, 0.50, 0.52), sun_strength=0.25,
             fog_start=10.0, fog_end=160.0, fog_max=0.7)
BINNEN = dict(M["binnen"])
mood = {"props": dict(M["binnen"], bloom=0.5), "kruispunt_laat": LAAT, "kruispunt_grijs": GRIJS,
        "steiger_zomer": dict(M["dag"], sun_rot=(48, 0, -30)), "steiger_herfst": dict(LAAT, sun_strength=0.95),
        "steiger_mist": MIST,
        "opa_avond": dict(M["avond"], ambient=(0.10, 0.09, 0.14), sun_strength=0.15, bloom=0.6),
        "opa_ochtend": dict(M["ochtend"], sun_color=(0.85, 0.90, 1.0), lit_tint=(0.90, 0.94, 1.0), sun_strength=0.7),
        "begraafplaats": dict(REGEN, fog_start=20.0, fog_end=220.0), "schoolwc": BINNEN,
        "directeur": BINNEN, "ziekenhuis": dict(M["ochtend"], sun_strength=0.9), "zwembad": dict(M["dag"], sun_rot=(40, 0, 20)),
        "gymzaal": dict(BINNEN, sun_strength=0.3, sky_top=(0.30, 0.33, 0.37), sky_horizon=(0.50, 0.52, 0.55)),
        "schoolplein": dict(M["bewolkt"], sun_strength=0.6), "schoolplein_regen": REGEN}[VAR]
T.new_scene("DagenOver_" + VAR, mood, samples=32)
T.use_collection(T.collection(VAR))
BINNEN_SET = VAR in {"props", "opa_avond", "opa_ochtend", "schoolwc", "directeur", "ziekenhuis", "gymzaal"}


def mt(name, col, rough=0.5, metal=0.0, coat=0.1):
    return ND.pbr(name, col, rough=rough, metal=metal, coat=coat)


def bomenring(prefix, center, r0, r1, n, seed=1, h=(6, 10), herfst=False):
    """Bomen in een ring rond 'center' zodat er in elke kijkrichting iets staat."""
    rr = random.Random(seed)
    out = []
    for k in range(n):
        a = k / n * 2 * math.pi + rr.uniform(-0.1, 0.1)
        r = rr.uniform(r0, r1)
        loc = (center[0] + math.cos(a) * r, center[1] + math.sin(a) * r, 0)
        hh = rr.uniform(*h)
        if herfst and k % 3 == 0:
            o = ND.eik(f"{prefix}_eik{k}", loc, seizoen="herfst", schaal=hh / 9, seed=k)
        else:
            o = P.tree(f"{prefix}_{k}", loc, h=hh, r=hh * 0.38, seed=k, kind="den" if k % 4 == 1 else "rond")
        out.append(o)
    return out


def heuvels(prefix, center, r, n=14, h=(14, 30), col=(0.26, 0.42, 0.22), seed=2):
    rr = random.Random(seed)
    m = mt(prefix + "_gras_heuvel", col, rough=0.9, coat=0)
    for k in range(n):
        a = k / n * 2 * math.pi
        T.sphere(f"{prefix}_{k}", (center[0] + math.cos(a) * r, center[1] + math.sin(a) * r, -rr.uniform(4, 8)), rr.uniform(25, 40), m,
                 scale=(1.6, 1.0, rr.uniform(*h) / 35), seg=20, ol=0)


def stad_rondom(prefix, center=(0, 0), r=125.0, n=36, rijen=2, seed=4, lit=0.05):
    """Ring van flats op afstand r rond 'center', gevels naar binnen: de horizon is in ELKE richting
    gevuld (vervangt S.skyline, die maar naar één kant loopt)."""
    rr = random.Random(seed)
    cols = [(0.62, 0.58, 0.55), (0.52, 0.55, 0.62), (0.70, 0.62, 0.50), (0.45, 0.48, 0.52), (0.78, 0.74, 0.68)]
    for rij in range(rijen):
        R = r + rij * 22
        for k in range(n):
            a = (k + 0.5 * rij) / n * 2 * math.pi
            S.building(f"{prefix}_{rij}_{k}", (center[0] + math.cos(a) * R, center[1] + math.sin(a) * R, 0), w=rr.uniform(15, 20) * R / 125,
                       d=12, floors=rr.randint(4 + 2 * rij, 9 + 3 * rij), color=rr.choice(cols), lit=lit, seed=seed * 100 + rij * 50 + k,
                       rot_z=math.degrees(a) - 90, block="ABCDEFGH"[rij])


def buiten_door_raam(center, rz=0.0, afstand=8.0, stad=True):
    """Buitenbeeld achter een raam: grond, bomen en gevels, zodat het raam nooit in het niets kijkt."""
    cx, cy = center
    c, s = math.cos(math.radians(rz)), math.sin(math.radians(rz))

    def at(dx, dy):
        return (cx + dx * c - dy * s, cy + dx * s + dy * c)
    P.ground("Buiten_grond", (3000, 3000), (0.32, 0.50, 0.24), loc=(cx, cy), z=-0.12)
    for k in range(7):
        x, y = at(-18 + k * 6, afstand + 4 + (k % 2) * 3)
        P.tree(f"Buiten_boom_{k}", (x, y, -0.1), h=rnd.uniform(6, 9), r=2.6, seed=k)
    if stad:
        for k in range(6):
            x, y = at(-30 + k * 12, afstand + 22)
            S.building(f"Buiten_flat_{k}", (x, y, -0.1), w=11, d=10, floors=rnd.randint(3, 7), color=rnd.choice(
                [(0.72, 0.60, 0.50), (0.62, 0.66, 0.70), (0.80, 0.74, 0.62)]), lit=0.1, seed=k, rot_z=rz)


cams = []

# ---------------------------------------------------------------------------
if VAR == "props":
    room = I.room("Studio", 9, 7, 4, (0.16, 0.18, 0.24), (0.20, 0.22, 0.28), hide=(), skirting=False)
    T.area_light("Studio_key", (2, -3, 3.5), (0, 0, 0.6), size=(3, 3), energy=700)
    T.area_light("Studio_fill", (-3, -2, 2.5), (0, 0, 0.5), size=(3, 3), color=(0.8, 0.85, 1.0), energy=250)
    tafel = T.box("Tafel_props", (0, 0.4, 0), (6.4, 2.6, 0.75), mt("tafel_studio", (0.55, 0.52, 0.5)), bevel=0.02, ol=0)
    z = 0.75
    cam_tgt = (0, 0.4, 1.0)
    cam = T.camera("CAM_PROPS", (0, -5.2, 2.2), cam_tgt, lens=30)
    # getallen in de drie kleuren
    for k, v in enumerate((25550, 34, 1, 0)):
        D.getal(f"Getal_voorbeeld_{k}", v, (-2.4 + k * 0.6, -0.6, 1.55), camera=cam)
    D.goudviskom("Goudviskom", (-2.6, 0.2, z))
    D.pannenkoekenpan("Pan", (-1.8, 0.0, z), rot_z=-20)
    D.pannenkoekstapel("Stapel_pannenkoeken", (-1.6, 0.8, z))
    D.sapkan("Sapkan", (-2.1, 0.9, z))
    D.krant("Krant_opa", (-1.0, 0.9, z), rot_z=15)
    D.koffiebeker("Koffiebeker", (-0.9, -0.1, z), plas=False)
    D.koffiebeker("Koffiebeker_val", (-0.6, 0.35, z), plas=True)
    D.blikkenstapel("Blikken", (0.0, 1.1, z), rijen=5)
    D.brandalarm("Brandalarm", (0.9, 1.62, z + 0.6))
    T.box("Brandalarm_muurtje", (0.9, 1.68, z), (0.5, 0.1, 1.0), mt("muurtje", (0.85, 0.84, 0.8)), bevel=0, ol=0)
    D.tekening("Tekening", (0.6, -0.3, z + 0.004), rot=(0, 0, 8))
    D.envelop_brief("Brief", (1.4, -0.35, z + 0.002), rot_z=-5)
    D.grafsteen("Grafsteen", (2.6, 1.1, z))
    D.paraplu("Paraplu", (2.0, 0.6, z + 0.12), tilt=0)
    D.klapkrukje("Klapkrukje", (1.6, 0.9, z))
    D.schepnet("Schepnet", (2.0, -0.5, z + 0.02), rot_z=180)
    D.vishengel("Vishengel", grip=(0.2, 0.6, z + 0.05), tip=(1.4, 1.4, z + 0.9), dobber=(1.7, 1.1, z + 0.03))
    D.kinderwagen("Kinderwagen", (-3.6, -0.6, 0), rot_z=30)
    D.scooter("Scooter", (3.4, -0.9, 0), rot_z=-150)
    D.leunstoel("Leunstoel", (-3.6, 1.8, 0), rot_z=-20, deken=True)
    cams = [cam, T.camera("CAM_PROPS_TAFEL", (0, -2.4, 1.9), (0, 0.4, 0.8), lens=26),
            T.camera("CAM_PROPS_BRIEF", (1.42, -0.45, 1.25), (1.42, -0.33, z), lens=50)]

# ---------------------------------------------------------------------------
elif VAR.startswith("kruispunt"):
    laat = VAR == "kruispunt_laat"
    asf = T.pattern("asfalt_kruispunt", (0.20, 0.20, 0.22), (0.18, 0.18, 0.20), size=(0.5, 0.5), mortar=0.0)
    stoep = T.pattern("stoeptegel_kruispunt", (0.66, 0.64, 0.60), (0.62, 0.60, 0.57), grout=(0.5, 0.5, 0.48), size=(0.3, 0.3))
    T.plane("Asfalt", (0, 0, 0), (400, 400), asf)
    P.ground("Grond_ver", (3000, 3000), (0.30, 0.45, 0.24), z=-0.02)
    RW = 4.5  # halve wegbreedte
    for sx in (-1, 1):
        for sy in (-1, 1):
            T.box(f"Stoep_{sx}_{sy}", (sx * (RW + 100), sy * (RW + 100), 0), (200, 200, 0.15), stoep, bevel=0.02, ol=0)
            T.box(f"Stoeprand_{sx}_{sy}_x", (sx * (RW + 100), sy * (RW + 0.06), 0), (200, 0.12, 0.16), mt("stoeprand", (0.75, 0.75, 0.73)), bevel=0.01, ol=0)
            T.box(f"Stoeprand_{sx}_{sy}_y", (sx * (RW + 0.06), sy * (RW + 100), 0), (0.12, 200, 0.16), mt("stoeprand", (0.75, 0.75, 0.73)), bevel=0.01, ol=0)
    # wegmarkering: middenstrepen en stopstrepen
    wit = mt("wegverf", (0.92, 0.92, 0.9), rough=0.6)
    for k in range(30):
        for ax in (0, 1):
            d = RW + 4 + k * 4
            for s in (-1, 1):
                loc = (s * d, 0, 0.004) if ax == 0 else (0, s * d, 0.004)
                T.plane(f"Middenstreep_{ax}_{s}_{k}", loc, (2.0, 0.12) if ax == 0 else (0.12, 2.0), wit)
    S.crosswalk("Zebrapad_W", (-RW - 2.2, 0, 0), 2 * RW, 3.0, rot_z=90)
    S.crosswalk("Zebrapad_N", (0, RW + 2.2, 0), 2 * RW, 3.0, rot_z=0)
    # verkeerslichten + voetgangerslichten (zebrapad W is het pad van de beste vriend)
    S.traffic_light("VKL_ZO", (RW + 0.6, -RW - 0.6, 0.15), rot_z=180, state="groen")
    S.traffic_light("VKL_NW", (-RW - 0.6, RW + 0.6, 0.15), rot_z=0, state="groen")
    S.ped_light("VGL_W_noord", (-RW - 3.9, RW + 0.4, 0.15), rot_z=180, state="groen" if laat else "rood")
    S.ped_light("VGL_W_zuid", (-RW - 0.5, -RW - 0.5, 0.15), rot_z=0, state="groen" if laat else "rood")
    S.ped_light("VGL_N_oost", (RW + 0.4, RW + 3.9, 0.15), rot_z=90, state="rood")
    ST.bus_stop("Bushokje", (-14, -RW - 1.6, 0.15), rot=180)
    for k, x in enumerate((-28, -20, 14, 22, 30)):
        P.tree(f"Straatboom_Z_{k}", (x, -RW - 1.6, 0.15), h=7, r=2.4, seed=k)
    for k, y in enumerate((-30, -22, -14, 16, 24)):
        P.tree(f"Straatboom_O_{k}", (RW + 1.6, y, 0.15), h=7, r=2.4, seed=k + 9)
    for k, (x, y) in enumerate(((-RW - 1.3, -10), (RW + 1.3, 10), (-10, RW + 1.3), (12, -RW - 1.3))):
        S.street_lamp(f"Lantaarn_{k}", (x, y, 0.15), rot_z=[90, -90, 180, 0][k], on=False)
    # vier hoeken bebouwd. NO-hoek = school (laag gebouw + hek + bord), de rest stadsflats met winkels
    kleuren = [(0.72, 0.60, 0.50), (0.62, 0.66, 0.70), (0.80, 0.74, 0.62), (0.70, 0.45, 0.35), (0.85, 0.82, 0.75)]
    winkels = ["BAKERY", "PHARMACY", "BOOKS", "PIZZA", "FLOWERS", "TV & AUDIO"]
    bi = 0
    for qx in (-1, 1):
        for qy in (-1, 1):
            if qx == 1 and qy == 1:
                continue
            for k in range(4):
                x = qx * (RW + 3.5 + 6 + k * 12.5)
                S.building(f"Flat_{qx}_{qy}_{k}", (x, qy * (RW + 3.5), 0.15), w=12, d=12, floors=rnd.randint(3, 6), color=kleuren[bi % 5],
                           lit=0.05, seed=bi, rot_z=0 if qy > 0 else 180, shop=winkels[bi % 6] if k < 2 else None,
                           shop_color=[(0.15, 0.35, 0.7), (0.15, 0.55, 0.3), (0.7, 0.2, 0.2)][bi % 3])
                bi += 1
            for k in range(3):
                y = qy * (RW + 3.5 + 18 + k * 12.5)
                S.building(f"Flat_arm_{qx}_{qy}_{k}", (qx * (RW + 3.5), y, 0.15), w=12, d=12, floors=rnd.randint(3, 6), color=kleuren[bi % 5],
                           lit=0.05, seed=bi, rot_z=-90 if qx > 0 else 90)
                bi += 1
    # school op de NO-hoek
    sch = mt("gevel_school", (0.78, 0.42, 0.30), rough=0.8)
    T.box("School_gebouw", (RW + 30, RW + 26, 0.15), (40, 30, 9), sch, bevel=0.05, ol=0)
    for f in range(2):
        for k in range(12):
            T.box(f"School_raam_{f}_{k}", (RW + 13 + k * 3.2, RW + 10.95, 1.6 + f * 3.6), (2.2, 0.1, 2.0), mt("raam_school", (0.35, 0.48, 0.6), rough=0.1), bevel=0, ol=0)
    S.label("School_naam", "RIVERSIDE SCHOOL", (RW + 30, RW + 10.9, 7.2), 1.0, (0.95, 0.95, 0.9))
    P.railing("Schoolhek_Z", [(RW + 1.5, RW + 2.0, 0.15), (RW + 60, RW + 2.0, 0.15)], h=1.6, posts=2.5, color="donkergroen")
    P.railing("Schoolhek_W", [(RW + 2.0, RW + 1.5, 0.15), (RW + 2.0, RW + 60, 0.15)], h=1.6, posts=2.5, color="donkergroen")
    T.box("Schoolplein_tegels", (RW + 31, RW + 6, 0.151), (58, 8, 0.01), mt("plein_tegels", (0.60, 0.58, 0.55), rough=0.8), bevel=0, ol=0)
    for k in range(4):
        P.tree(f"Schoolboom_{k}", (RW + 8 + k * 10, RW + 7, 0.15), h=8, r=2.8, seed=k + 20)
    # verder weg: skyline in alle richtingen
    stad_rondom("Skyline", (0, 0), r=120, n=40)
    # verkeer: bestelbus (chauffeur!) en in de grijze ochtend een vrachtwagen + fietser
    vx, vy = (RW + 6, -2.2) if laat else (RW + 18, -2.2)
    ST.delivery_van("Bestelbus", (vx, vy, 0), rot=180)
    D.plek("PLEK_chauffeur", (vx - 1.5, vy + 0.45, 0.85), rot_z=180)
    if not laat:
        ST.garbage_truck("Vrachtwagen", (-RW - 12, 2.2, 0), rot=0, lights=True)
        D.plek("PLEK_vrachtwagen_chauffeur", (-RW - 9.6, 2.6, 1.3), rot_z=0)
        ST.bicycle("Fiets_figurant", (2.5, -RW - 8, 0), rot=90)
        D.scooter("Scooter", (-RW - 22, -2.2, 0), rot_z=0)
    D.plek("PLEK_held", (-RW - 0.9, RW + 2.6, 0.15), rot_z=-90)
    D.plek("PLEK_vriend", (-RW - 0.4, RW + 1.0, 0.15), rot_z=-90)
    for k in range(6):
        D.plek(f"PLEK_figurant_{k}", (-RW - 1.5 - k * 1.3, -RW - 2.5 - (k % 2), 0.15), rot_z=0)
    cams = [T.camera("CAM_0a_CLOSE", (-RW - 1.9, RW + 4.4, 1.55), (-RW - 1.0, RW + 2.6, 1.55), lens=50, dof=2.8),
            T.camera("CAM_0b_MEDIUM", (-RW - 7.5, -1.5, 1.4), (-RW - 2.2, 0.5, 1.3), lens=35),
            T.camera("CAM_0c_LAAG", (-RW - 1.0, -RW - 1.2, 0.35), (RW + 4, -2.2, 1.0), lens=24),
            T.camera("CAM_8a_WIDE", (-RW - 20, -1.5, 5.5), (0, 1.0, 1.0), lens=24),
            T.camera("CAM_18e_WIDE", (-RW - 7.5, -1.5, 1.4), (-RW - 2.2, 0.5, 1.3), lens=28)]

# ---------------------------------------------------------------------------
elif VAR.startswith("steiger"):
    herfst = VAR == "steiger_herfst"
    mist = VAR == "steiger_mist"
    meer = ND.pbr("meerwater", (0.05, 0.16, 0.20) if not mist else (0.30, 0.34, 0.36), rough=0.06, coat=0.9)
    w = T.plane("Meer", (0, 25, -0.25), (260, 260), meer)
    w.modifiers.new("sub", "SUBSURF").levels = 0
    # golfjes: bump via ruis
    nt = meer.node_tree
    b = nt.nodes["Principled BSDF"]
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 18.0
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.08
    nt.links.new(nz.outputs["Fac"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    # oever: zandstrook + gras, het meer is omringd door land en bos (geen lege horizon)
    gras = mt("gras_oever", (0.30, 0.48, 0.20) if not herfst else (0.42, 0.48, 0.22), rough=0.9, coat=0)
    T.box("Oever_zuid", (0, -40, -0.6), (300, 70, 0.8), gras, bevel=0, ol=0)
    P.ground("Land_ver", (3000, 3000), (0.24, 0.38, 0.20), z=-0.4)
    T.box("Oever_zand", (0, -5.5, -0.45), (60, 3.0, 0.4), mt("zand_oever", (0.70, 0.60, 0.44), rough=0.95, coat=0), rot=(-6, 0, 0), bevel=0, ol=0)
    T.to_mesh(T.tube("Oever_ring", [(math.cos(a) * 95, 25 + math.sin(a) * 75, -0.3) for a in [k / 40 * 2 * math.pi for k in range(41)]], 6.0, gras))
    bomenring("Bos", (0, 25), 80, 110, 70, seed=3, h=(9, 15), herfst=herfst)
    rr = random.Random(5)
    for k in range(18):  # bomen op de oever achter de steiger (alleen aan land, nooit in het water)
        x, y = rr.uniform(-30, 30), rr.uniform(-28, -9)
        if abs(x) < 4 and y > -14:
            continue
        hh = rr.uniform(6, 10)
        if herfst and k % 3 == 0:
            ND.eik(f"Bos_oever_eik{k}", (x, y, -0.2), seizoen="herfst", schaal=hh / 9, seed=k)
        else:
            P.tree(f"Bos_oever_{k}", (x, y, -0.2), h=hh, r=hh * 0.38, seed=k)
    heuvels("Heuvels", (0, 25), 150, n=16, col=(0.22, 0.36, 0.20))
    # steiger: 2 m breed, 12 m het water in, planken met naden, palen
    hout = T.pattern("planken_steiger", (0.50, 0.38, 0.26), (0.46, 0.34, 0.23), grout=(0.25, 0.18, 0.12), size=(0.16, 2.0), mortar=0.06, kind="planken")
    T.box("Steiger_dek", (0, 1.0, 0.25), (2.0, 13.0, 0.08), hout, bevel=0.01, ol=0)
    paalmat = mt("hout_paal_nat", (0.28, 0.20, 0.14), rough=0.8)
    for y in range(-5, 8, 2):
        for s in (-1, 1):
            T.cyl(f"Steiger_paal_{s}_{y}", (s * 0.95, y + 0.5, -1.5), 0.1, 2.0, paalmat, seg=12, ol=0)
    T.box("Steiger_balk_L", (-0.95, 1.0, 0.13), (0.12, 13, 0.14), paalmat, bevel=0, ol=0)
    T.box("Steiger_balk_R", (0.95, 1.0, 0.13), (0.12, 13, 0.14), paalmat, bevel=0, ol=0)
    # riet langs de oever (los, wiegt) en een paar waterlelies
    riet = mt("riet", (0.45, 0.50, 0.22) if not herfst else (0.62, 0.52, 0.25), rough=0.8, coat=0)
    for k in range(4):
        sts = []
        cx = [-6, -3.5, 3.5, 6.5][k]
        for i in range(70):
            x = cx + rnd.gauss(0, 0.9)
            y = -3.8 + rnd.gauss(0, 0.6)
            h = rnd.uniform(1.0, 1.9)
            lean = rnd.uniform(-0.15, 0.15)
            sts.append(T.to_mesh(T.tube(f"Riet_{k}_{i}", [(x, y, -0.3), (x + lean * 0.5, y, h * 0.6), (x + lean, y + 0.05, h)], 0.008, riet, res=3)))
            if i % 4 == 0:
                sts.append(T.cyl(f"Rietpluim_{k}_{i}", (x + lean, y + 0.05, h), 0.02, 0.18, mt("rietpluim", (0.40, 0.28, 0.18), rough=0.9), seg=6, ol=0))
        T.merge(f"Rietkraag_{k}", sts, ol=0)
    for k in range(8):
        T.cyl(f"Waterlelie_{k}", (rnd.uniform(-8, 8) + (4 if k % 2 else -4), rnd.uniform(5, 12), -0.245), rnd.uniform(0.2, 0.35), 0.01,
              mt("lelieblad", (0.18, 0.42, 0.16), rough=0.5), seg=16, ol=0)
    # opa's spullen
    D.klapkrukje("Krukje_opa", (-0.45, 6.4, 0.29), rot_z=0)
    D.klapkrukje("Krukje_held", (0.45, 6.4, 0.29), rot_z=0)
    D.vishengel("Hengel_opa", grip=(-0.45, 6.75, 0.85), tip=(-0.9, 9.8, 2.6), dobber=(-1.4, 14.5, -0.24))
    D.schepnet("Schepnet", (0.95, 5.8, 0.29), rot_z=90)
    T.box("Viskist", (0.0, 5.6, 0.29), (0.45, 0.3, 0.28), mt("kunststof_viskist", (0.15, 0.40, 0.55)), bevel=0.03, ol=0)
    if herfst:
        bl = [T.box(f"Blad_steiger_{k}", (rnd.uniform(-0.9, 0.9), rnd.uniform(-4, 7), 0.295), (0.07, 0.05, 0.003),
                    mt(["blad_geel", "blad_oranje"][k % 2], [(0.95, 0.70, 0.12), (0.85, 0.40, 0.08)][k % 2], rough=0.7, coat=0),
                    rot=(0, 0, rnd.uniform(0, 360)), bevel=0, ol=0) for k in range(40)]
        T.merge("Bladeren_steiger", bl, ol=0)
    ST.bird("Reiger_ver", (14, 30, 6), rot_z=200, span=1.6, color=(0.5, 0.52, 0.56), wings_up=10)
    D.plek("PLEK_opa", (-0.45, 6.4, 0.72), rot_z=0)
    D.plek("PLEK_held", (0.45, 6.4, 0.72), rot_z=0)
    cams = [T.camera("CAM_10d_WIDE", (3.5, -6.0, 2.4), (0, 6.0, 0.9), lens=28),
            T.camera("CAM_10e_ACHTER", (0.0, 3.2, 1.3), (0, 9.0, 0.8), lens=30),
            T.camera("CAM_10f_OPA", (-1.6, 8.8, 1.1), (-0.45, 6.4, 1.15), lens=50, dof=2.8),
            T.camera("CAM_15a_VAST", (-9, 4.0, 1.6), (0, 6.2, 0.8), lens=35)]

# ---------------------------------------------------------------------------
elif VAR.startswith("opa"):
    avond = VAR == "opa_avond"
    W, Dd, Hh = 6.0, 5.0, 2.7
    room = I.room("Opa_woonkamer", W, Dd, Hh, (0.62, 0.52, 0.40), (0.42, 0.28, 0.16), hide=(),
                  holes={"left": [(1.4, 3.4, 0.85, 2.25)], "front": [(4.6, 5.5, 0, 2.05)]})
    room["floor"].data.materials[0] = T.pattern("visgraat_opa", (0.45, 0.30, 0.17), (0.40, 0.26, 0.15), size=(0.12, 0.6), mortar=0.02, kind="planken")
    # behang met streep
    T.box("Behang_lambrisering", (0, Dd / 2 - 0.01, 0), (W, 0.02, 0.9), mt("lambrisering_opa", (0.35, 0.22, 0.13), rough=0.6), bevel=0, ol=0)
    I.window("Raam_opa", W, Dd, "left", 1.4, 3.4, 0.85, 2.25, curtains=(0.55, 0.20, 0.15), open_frac=0.6)
    I.door("Deur_opa", W, Dd, "front", 5.05, color=(0.45, 0.30, 0.18))
    buiten_door_raam((-W / 2 - 2, 0), rz=90, afstand=4, stad=False)
    # open haard aan de achtermuur
    steen = T.pattern("baksteen_haard", (0.55, 0.28, 0.20), (0.50, 0.25, 0.18), grout=(0.75, 0.72, 0.66), size=(0.22, 0.07), offset=0.5)
    T.box("Haard_mantel", (0.6, Dd / 2 - 0.25, 0), (1.6, 0.5, 1.15), steen, bevel=0.01, ol=0)
    T.box("Haard_plank", (0.6, Dd / 2 - 0.27, 1.15), (1.8, 0.55, 0.07), mt("hout_schoorsteenmantel", (0.32, 0.20, 0.11)), bevel=0.01, ol=0)
    T.box("Haard_gat", (0.6, Dd / 2 - 0.49, 0.12), (0.8, 0.05, 0.62), mt("roet_zwart", (0.03, 0.03, 0.03), rough=0.95, coat=0), bevel=0, ol=0)
    T.box("Haard_rookkanaal", (0.6, Dd / 2 - 0.2, 1.22), (1.1, 0.4, Hh - 1.22), steen, bevel=0, ol=0)
    hout = [T.cyl(f"Haardhout_{k}", (0.6 + (k - 1) * 0.18, Dd / 2 - 0.35, 0.18), 0.05, 0.42, mt("haardhout", (0.30, 0.20, 0.12), rough=0.9),
                  rot=(90, 0, (k - 1) * 18), seg=10, ol=0) for k in range(3)]
    T.merge("Haardhout", hout, ol=0)
    if avond:
        vuur = ND.pbr("vuur_haard", (1.0, 0.5, 0.1), emit=(1.0, 0.45, 0.08), strength=14.0)
        for k in range(5):
            T.sphere(f"Vlam_{k}", (0.45 + k * 0.08, Dd / 2 - 0.35, 0.3 + (k % 2) * 0.05), 0.07, vuur, scale=(0.7, 0.5, 1.8), seg=10, ol=0)
        T.point_light("Haardvuur_licht", (0.6, Dd / 2 - 0.8, 0.45), color=(1.0, 0.52, 0.2), energy=180, radius=0.25)
    else:
        T.box("As_haard", (0.6, Dd / 2 - 0.35, 0.12), (0.5, 0.25, 0.04), mt("as_grijs", (0.55, 0.55, 0.53), rough=1.0, coat=0), bevel=0.02, ol=0)
    for k, (x, kleur) in enumerate(((0.15, (0.85, 0.80, 0.70)), (0.55, (0.70, 0.75, 0.80)), (1.0, (0.80, 0.78, 0.65)))):
        ND.oude_foto(f"Foto_mantel_{k}", (x, Dd / 2 - 0.3, 1.19), rot=(80, 0, 0))
    # boekenkast tegen de rechtermuur
    kast = mt("hout_boekenkast", (0.36, 0.22, 0.12), rough=0.55)
    T.box("Boekenkast", (W / 2 - 0.2, 0.4, 0), (0.4, 1.8, 2.2), kast, bevel=0.01, ol=0)
    for k in range(5):
        T.box(f"Boekenkast_plank_{k}", (W / 2 - 0.42, 0.4, 0.15 + k * 0.45), (0.05, 1.7, 0.03), kast, bevel=0, ol=0)
        I.books(f"Boeken_{k}", (W / 2 - 0.22, 0.4 - 0.75, 0.18 + k * 0.45), n=12, rot=90, flat=False, seed=k)
    D.leunstoel("Leunstoel_opa", (-0.6, 0.3, 0), rot_z=200, deken=not avond)
    D.leunstoel("Stoel_held", (1.5, -0.5, 0), rot_z=150, kleur=(0.30, 0.34, 0.40))
    I.rug("Vloerkleed_opa", (0.3, 0.0, 0.005), (2.6, 1.8), (0.45, 0.15, 0.12))
    T.box("Bijzettafel", (0.4, -0.6, 0), (0.45, 0.45, 0.5), mt("hout_bijzettafel", (0.36, 0.22, 0.12)), bevel=0.01, ol=0)
    D.krant("Krant_bijzettafel", (0.4, -0.6, 0.5), rot_z=20)
    T.cyl("Theekop", (0.5, -0.5, 0.5), 0.04, 0.07, mt("porselein", (0.95, 0.94, 0.9), coat=0.6), seg=20, ol=0)
    # staande lamp
    T.cyl("Staande_lamp_voet", (-1.4, 1.2, 0), 0.16, 0.03, mt("messing", (0.75, 0.6, 0.3), metal=1, rough=0.3), seg=20, ol=0)
    T.cyl("Staande_lamp_stang", (-1.4, 1.2, 0), 0.014, 1.55, mt("messing", (0.75, 0.6, 0.3), metal=1, rough=0.3), seg=10, ol=0)
    kap = T.cyl("Staande_lamp_kap", (-1.4, 1.2, 1.45), 0.25, 0.3, ND.pbr("lampenkap_opa", (0.95, 0.85, 0.65), emit=(1.0, 0.8, 0.5),
                                                                         strength=1.6 if avond else 0.0), r2=0.15, seg=24, ol=0, cap=False)
    kap.modifiers.new("dikte", "SOLIDIFY").thickness = 0.006
    if avond:
        T.point_light("Staande_lamp_licht", (-1.4, 1.2, 1.5), color=(1.0, 0.76, 0.48), energy=90, radius=0.15)
    else:
        T.area_light("Ochtendlicht_raam", (-W / 2 - 0.5, 0, 1.6), (0, 0, 0.8), size=(2, 1.4), color=(0.85, 0.9, 1.0), energy=260)
    T.box("Wandklok_opa", (-1.0, Dd / 2 - 0.05, 1.7), (0.3, 0.08, 0.5), mt("hout_klok", (0.30, 0.18, 0.1)), bevel=0.02, ol=0)
    D.plek("PLEK_opa", (-0.6, 0.25, 0.45), rot_z=200)
    D.plek("PLEK_held", (1.5, -0.5, 0.45), rot_z=150)
    cams = [T.camera("CAM_16a_WIDE", (2.6, -2.2, 1.55), (-0.4, 0.6, 0.8), lens=24),
            T.camera("CAM_16b_OPA", (0.9, -0.7, 1.15), (-0.6, 0.3, 1.1), lens=45, dof=2.8),
            T.camera("CAM_16c_HELD", (-0.3, 0.0, 1.15), (1.5, -0.5, 1.05), lens=45, dof=2.8)]

# ---------------------------------------------------------------------------
elif VAR == "begraafplaats":
    gras = mt("gras_begraafplaats", (0.24, 0.40, 0.18), rough=0.9, coat=0.05)
    P.ground("Grasveld", (3000, 3000), (0.24, 0.40, 0.18), z=0)
    T.sphere("Grasheuvel", (0, 6, -14), 22, gras, scale=(1.4, 1.0, 0.75), seg=40, ol=0)
    for k in range(22):
        x = -12 + (k % 11) * 2.4 + rnd.uniform(-0.2, 0.2)
        y = -2 + (k // 11) * 4.5
        if abs(x) < 1.4 and k // 11 == 0:
            continue
        D.grafsteen(f"Graf_{k}", (x, y, 0), rot_z=rnd.uniform(-4, 4))
    D.grafsteen("Graf_opa", (0, -2, 0), nieuw=True)
    T.box("Graf_opa_aarde", (0, -3.2, 0), (0.9, 1.9, 0.08), mt("aarde_vers", (0.25, 0.17, 0.10), rough=1.0, coat=0), bevel=0.04, ol=0)
    for k in range(5):
        ND.bloemen(f"Bloemen_graf_{k}", (-0.35 + k * 0.18, -2.5 - (k % 2) * 0.2, 0.08), rot_z=k * 30, seed=k)
    P.railing("Hek_begraafplaats", [(-30, -14, 0), (30, -14, 0)], h=1.4, posts=2.5, color="zwart")
    for k in range(6):
        ND.eik(f"Eik_bp_{k}", (-24 + k * 9.5, 14 + rnd.uniform(-2, 2), 0), seizoen="zomer", schaal=0.9, seed=k)
    bomenring("Bomen_bp", (0, 0), 35, 55, 40, seed=7)
    stad_rondom("Stad_ver", (0, 0), r=110, n=34, rijen=1)
    H.regendruppels("Motregen", ((-8, 8), (-10, 6), (0, 9)), 2500, seed=3, r=0.004, rek=3.0)
    for k, (x, y) in enumerate(((-1.8, -5.0), (-0.6, -5.4), (0.7, -5.3), (1.9, -5.0), (-1.2, -6.2), (1.2, -6.3), (0.0, -6.5))):
        D.paraplu(f"Paraplu_{k}", (x, y, 1.15), kleur=(0.05, 0.05, 0.07), tilt=rnd.uniform(4, 10))
        D.plek(f"PLEK_rouw_{k}", (x, y, 0), rot_z=90 + rnd.uniform(-10, 10))
    cams = [T.camera("CAM_17a_CRANE", (0, -16, 7.0), (0, -3, 0.8), lens=30),
            T.camera("CAM_17b_MEDIUM", (3.2, -8.5, 1.5), (0, -4.5, 1.3), lens=35)]

# ---------------------------------------------------------------------------
elif VAR == "schoolwc":
    W, Dd, Hh = 5.0, 4.0, 2.8
    room = I.room("Schoolwc", W, Dd, Hh, (0.90, 0.92, 0.92), (0.55, 0.58, 0.60), hide=(), holes={"front": [(3.6, 4.5, 0, 2.05)]})
    tegel = T.pattern("wandtegel_wc", (0.88, 0.93, 0.95), (0.84, 0.90, 0.93), grout=(0.7, 0.74, 0.76), size=(0.15, 0.15))
    for side, (loc, rz, L) in {"back": ((0, Dd / 2 - 0.01, 0), 0, W), "left": ((-W / 2 + 0.01, 0, 0), 90, Dd), "right": ((W / 2 - 0.01, 0, 0), 90, Dd)}.items():
        T.box(f"Tegels_{side}", loc, (L, 0.02, 1.6), tegel, rot=(0, 0, rz), bevel=0, ol=0)
    room["floor"].data.materials[0] = T.pattern("vloertegel_wc", (0.45, 0.48, 0.52), (0.40, 0.43, 0.47), grout=(0.3, 0.3, 0.32), size=(0.3, 0.3))
    I.door("Deur_wc", W, Dd, "front", 4.05, color=(0.30, 0.55, 0.80))
    spiegel = ND.pbr("spiegel", (0.95, 0.95, 0.95), rough=0.02, metal=1.0)
    for k in range(3):
        x = -1.6 + k * 1.2
        T.box(f"Wastafel_{k}", (x, Dd / 2 - 0.3, 0.78), (0.55, 0.45, 0.12), mt("porselein_wc", (0.96, 0.96, 0.95), coat=0.6), bevel=0.04, ol=0)
        T.cyl(f"Kraan_{k}", (x, Dd / 2 - 0.12, 0.9), 0.018, 0.2, mt("chroom", (0.85, 0.86, 0.88), metal=1, rough=0.15), seg=10, ol=0)
        T.box(f"Spiegel_{k}", (x, Dd / 2 - 0.025, 1.15), (0.6, 0.012, 0.8), spiegel, bevel=0, ol=0)
        T.box(f"Spiegel_lijst_{k}", (x, Dd / 2 - 0.02, 1.13), (0.64, 0.01, 0.84), mt("aluminium", (0.6, 0.62, 0.65), metal=1, rough=0.3), bevel=0, ol=0)
    for k in range(3):
        y = -1.2 + k * 1.0
        T.box(f"Wc_hokje_wand_{k}", (W / 2 - 0.75, y - 0.48, 0.12), (1.5, 0.04, 1.9), mt("hokje_blauw", (0.25, 0.50, 0.78), coat=0.3), bevel=0.005, ol=0)
        T.box(f"Wc_hokje_deur_{k}", (W / 2 - 1.5, y, 0.12), (0.04, 0.9, 1.9), mt("hokje_blauw", (0.25, 0.50, 0.78), coat=0.3), bevel=0.005, ol=0)
    for k in range(2):
        T.box(f"Tl_armatuur_{k}", (-0.8 + k * 1.8, 0, Hh - 0.06), (1.3, 0.2, 0.05), mt("tl_armatuur", (0.9, 0.9, 0.9)), bevel=0.01, ol=0)
        T.box(f"Tl_buis_{k}", (-0.8 + k * 1.8, 0, Hh - 0.09), (1.2, 0.08, 0.03), T.glow("tl_licht", (0.95, 0.98, 1.0), 6), bevel=0.01, ol=0)
        T.area_light(f"Tl_licht_{k}", (-0.8 + k * 1.8, 0, Hh - 0.15), (-0.8 + k * 1.8, 0, 0), size=(1.2, 0.3), color=(0.92, 0.97, 1.0), energy=220)
    D.plek("PLEK_held", (-0.4, Dd / 2 - 0.85, 0), rot_z=0)
    cams = [T.camera("CAM_6a_SPIEGEL", (0.6, 0.3, 1.5), (-0.6, Dd / 2, 1.35), lens=32),
            T.camera("CAM_6b_DETAIL", (-0.4, 0.9, 1.5), (-0.4, Dd / 2, 1.45), lens=50)]

# ---------------------------------------------------------------------------
elif VAR == "directeur":
    W, Dd, Hh = 5.0, 4.2, 2.8
    room = I.room("Kamer_directeur", W, Dd, Hh, (0.82, 0.84, 0.80), (0.35, 0.40, 0.48), hide=(),
                  holes={"back": [(1.0, 4.0, 0.9, 2.3)], "front": [(0.5, 1.4, 0, 2.05)]})
    I.window("Raam_directeur", W, Dd, "back", 1.0, 4.0, 0.9, 2.3, curtains=None)
    I.door("Deur_directeur", W, Dd, "front", 0.95, color=(0.55, 0.38, 0.22))
    # uitzicht op het schoolplein
    T.box("Plein_buiten", (0, Dd / 2 + 12, -0.12), (60, 22, 0.02), mt("plein_tegels", (0.60, 0.58, 0.55), rough=0.8), bevel=0, ol=0)
    buiten_door_raam((0, Dd / 2), rz=0, afstand=14, stad=True)
    T.box("Gymzaal_buiten", (6, Dd / 2 + 18, -0.1), (14, 10, 6), mt("gevel_gymzaal", (0.75, 0.70, 0.62), rough=0.8), bevel=0.03, ol=0)
    T.box("Bureau", (0, 0.4, 0), (1.8, 0.85, 0.75), mt("hout_bureau", (0.45, 0.30, 0.18)), bevel=0.02, ol=0)
    I.chair("Stoel_directeur", (0, 1.1, 0), rot=180, office=True)
    I.chair("Stoel_bezoeker_L", (-0.5, -0.6, 0), rot=0, color=(0.25, 0.35, 0.55))
    I.chair("Stoel_bezoeker_R", (0.5, -0.6, 0), rot=0, color=(0.25, 0.35, 0.55))
    H.laptop("Laptop_directeur", (0.3, 0.45, 0.75), rot_z=180)
    H.papierstapels("Papieren_bureau", (-0.55, 0.45, 0.75), n=3)
    T.box("Archiefkast", (-W / 2 + 0.3, 0.6, 0), (0.5, 1.6, 1.9), mt("metaal_archief", (0.55, 0.58, 0.60), metal=0.4), bevel=0.01, ol=0)
    T.box("Prikbord", (W / 2 - 0.02, 0, 1.0), (0.03, 1.4, 0.9), mt("kurk_prikbord", (0.70, 0.52, 0.32), rough=0.9), bevel=0, ol=0)
    S.wall_sign("Bord_principal", ["PRINCIPAL"], (0, 0.04, 1.4), rot_z=0, w=0.5, h=0.12)
    T.area_light("Plafondlicht_directeur", (0, 0, Hh - 0.1), (0, 0, 0), size=(1.2, 1.2), color=(1.0, 0.97, 0.92), energy=180)
    D.plek("PLEK_directeur", (0, 1.1, 0), rot_z=180)
    D.plek("PLEK_held", (-0.5, -0.6, 0), rot_z=0)
    cams = [T.camera("CAM_12a_MEDIUM", (1.9, -1.6, 1.45), (-0.2, 0.6, 1.0), lens=30),
            T.camera("CAM_12b_RAAM", (-0.6, -1.4, 1.2), (0.6, Dd / 2 + 4, 1.4), lens=30)]

# ---------------------------------------------------------------------------
elif VAR == "ziekenhuis":
    W, Dd, Hh = 5.0, 4.5, 2.8
    room = I.room("Ziekenhuiskamer", W, Dd, Hh, (0.86, 0.90, 0.88), (0.70, 0.72, 0.70), hide=(),
                  holes={"right": [(1.0, 3.2, 0.9, 2.3)], "front": [(3.7, 4.6, 0, 2.05)]})
    I.window("Raam_zh", W, Dd, "right", 1.0, 3.2, 0.9, 2.3, curtains=(0.65, 0.78, 0.82), open_frac=0.7)
    I.door("Deur_zh", W, Dd, "front", 4.15, color=(0.85, 0.85, 0.82), width=1.0)
    buiten_door_raam((W / 2, 0), rz=-90, afstand=10, stad=True)
    wit = mt("ziekenhuis_wit", (0.94, 0.95, 0.95), coat=0.3)
    T.box("Bed_frame", (-0.4, 0.6, 0.35), (1.0, 2.1, 0.25), mt("bed_metaal", (0.75, 0.78, 0.8), metal=0.5, rough=0.35), bevel=0.03, ol=0)
    T.box("Bed_matras", (-0.4, 0.6, 0.6), (0.92, 2.0, 0.15), wit, bevel=0.05, ol=0)
    T.box("Bed_hoofdeind", (-0.4, 1.68, 0.35), (1.05, 0.06, 0.75), mt("bed_metaal", (0.75, 0.78, 0.8), metal=0.5, rough=0.35), bevel=0.02, ol=0)
    T.box("Bed_kussen", (-0.4, 1.38, 0.75), (0.6, 0.35, 0.12), wit, bevel=0.05, ol=0)
    T.box("Bed_deken", (-0.4, 0.2, 0.75), (0.96, 1.25, 0.06), mt("stof_deken_zh", (0.55, 0.72, 0.85), rough=0.85), bevel=0.03, ol=0)
    for x, y in ((-0.85, -0.35), (0.05, -0.35), (-0.85, 1.6), (0.05, 1.6)):
        T.cyl(f"Bed_poot_{x}_{y}", (x, y, 0.08), 0.025, 0.28, mt("bed_metaal", (0.75, 0.78, 0.8), metal=0.5), seg=8, ol=0)
        T.sphere(f"Bed_wiel_{x}_{y}", (x, y, 0.05), 0.05, mt("rubber_wiel", (0.05, 0.05, 0.05), rough=0.8), seg=10, ol=0)
    # monitor met hartslag
    T.cyl("Monitor_paal", (-1.3, 1.3, 0), 0.02, 1.4, mt("bed_metaal", (0.75, 0.78, 0.8), metal=0.5), seg=8, ol=0)
    T.box("Monitor_kast", (-1.3, 1.3, 1.35), (0.35, 0.12, 0.28), mt("monitor_grijs", (0.25, 0.27, 0.3)), bevel=0.02, ol=0)
    T.box("Monitor_scherm", (-1.3, 1.235, 1.38), (0.3, 0.005, 0.22), T.screen("monitor_scherm", (0.05, 0.12, 0.08), 1.5), bevel=0, ol=0)
    hart = [(-1.43 + i * 0.013, 1.231, 1.47 + (0.06 if i % 12 == 5 else -0.03 if i % 12 == 6 else 0)) for i in range(21)]
    T.to_mesh(T.tube("Monitor_hartslag", hart, 0.0025, T.glow("hartslag_groen", (0.2, 1.0, 0.4), 5)))
    # tv aan de muur met het nieuws
    T.box("Tv_zh", (0.8, Dd / 2 - 0.06, 1.75), (0.9, 0.06, 0.52), mt("tv_zwart", (0.03, 0.03, 0.04)), bevel=0.01, ol=0)
    T.box("Tv_zh_scherm", (0.8, Dd / 2 - 0.092, 1.78), (0.84, 0.004, 0.46), T.screen("tv_nieuws", (0.10, 0.20, 0.45), 1.6), bevel=0, ol=0)
    T.box("Tv_zh_balk", (0.8, Dd / 2 - 0.096, 1.58), (0.84, 0.004, 0.08), T.glow("nieuwsbalk_rood", (0.85, 0.08, 0.06), 1.5), bevel=0, ol=0)
    S.label("Tv_zh_tekst", "MYSTERY KID SAVES 300", (0.8, Dd / 2 - 0.1, 1.597), 0.038, (1, 1, 1), glow=2.0)
    T.box("Nachtkastje", (0.45, 1.4, 0), (0.45, 0.4, 0.65), wit, bevel=0.02, ol=0)
    H.waterglas("Waterglas_zh", (0.35, 1.38, 0.65))
    D.tekening("Tekening_broertje", (0.55, 1.42, 0.651), rot=(0, 0, 12))
    I.chair("Stoel_bezoek", (0.9, 0.2, 0), rot=-100, color=(0.25, 0.45, 0.6))
    T.area_light("Plafondlicht_zh", (0, 0, Hh - 0.1), (0, 0, 0), size=(1.2, 1.2), color=(0.98, 1.0, 1.0), energy=120)
    D.plek("PLEK_held_bed", (-0.4, 0.8, 0.7), rot_z=0)
    D.plek("PLEK_mama", (0.9, 0.2, 0), rot_z=-100)
    cams = [T.camera("CAM_14a_MEDIUM", (1.6, -1.6, 1.5), (-0.4, 0.8, 0.85), lens=30),
            T.camera("CAM_14c_PUSHIN", (0.6, -0.9, 1.25), (-0.4, 1.2, 0.95), lens=40, dof=3.5)]

# ---------------------------------------------------------------------------
elif VAR == "zwembad":
    tegel = T.pattern("tegel_zwembadrand", (0.88, 0.88, 0.85), (0.84, 0.84, 0.81), grout=(0.7, 0.7, 0.68), size=(0.3, 0.3))
    blauw = T.pattern("tegel_zwembad_blauw", (0.25, 0.60, 0.85), (0.22, 0.55, 0.80), grout=(0.85, 0.9, 0.95), size=(0.15, 0.15))
    P.ground("Gras_zwembad", (3000, 3000), (0.30, 0.52, 0.22), z=0)
    T.box("Bad_rand", (0, 0, 0), (32, 20, 0.05), tegel, bevel=0, ol=0)
    # uitgehold bad: bodem en wanden blauw, water ervoor
    T.box("Bad_bodem", (0, 0, -1.8), (25, 12.5, 0.05), blauw, bevel=0, ol=0)
    for s in (-1, 1):
        T.box(f"Bad_wand_x{s}", (s * 12.5, 0, -1.8), (0.1, 12.5, 1.86), blauw, bevel=0, ol=0)
        T.box(f"Bad_wand_y{s}", (0, s * 6.25, -1.8), (25, 0.1, 1.86), blauw, bevel=0, ol=0)
    bpy.data.objects["Bad_rand"].modifiers.new("gat", "BOOLEAN")
    snij = T.box("Bad_snijder", (0, 0, -0.5), (25, 12.5, 1.0), tegel, bevel=0, ol=0)
    bpy.data.objects["Bad_rand"].modifiers["gat"].object = snij
    bpy.data.objects["Bad_rand"].modifiers["gat"].operation = "DIFFERENCE"
    T._apply_mods(bpy.data.objects["Bad_rand"])
    bpy.data.objects.remove(snij)
    zw = H.water("water_zwembad")
    wa = T.plane("Zwembadwater", (0, 0, -0.12), (24.9, 12.4), zw)
    for k in range(6):
        T.to_mesh(T.tube(f"Baanlijn_{k}", [(-12.4, -5.2 + k * 2.08, -0.1), (12.4, -5.2 + k * 2.08, -0.1)], 0.05,
                         mt("baanlijn", [(0.9, 0.1, 0.1), (0.95, 0.95, 0.95)][k % 2], coat=0.5), res=4))
    P.railing("Trapleuning", [(11.8, -5.0, 0.05), (11.8, -5.0, 1.0), (12.3, -5.0, 1.0), (12.3, -5.0, -0.8)], h=0.05, posts=5, color="metaal")
    for k in range(6):
        x = -9 + k * 3.6
        T.box(f"Ligstoel_{k}", (x, 8.2, 0.05), (0.7, 1.9, 0.35), mt("ligstoel_wit", (0.95, 0.95, 0.93), coat=0.5), bevel=0.05, ol=0)
        T.box(f"Ligstoel_rug_{k}", (x, 9.0, 0.35), (0.7, 0.5, 0.06), mt("ligstoel_wit", (0.95, 0.95, 0.93)), rot=(-40, 0, 0), bevel=0.02, ol=0)
        S.handdoek(f"Handdoek_{k}", (x, 8.1, 0.41), color=[(0.95, 0.4, 0.2), (0.2, 0.6, 0.9), (0.95, 0.85, 0.2)][k % 3])
    P.railing("Hek_zwembad", [(-16, -10, 0), (16, -10, 0), (16, 10, 0), (-16, 10, 0), (-16, -10, 0)], h=1.8, posts=2.0, color="donkergroen")
    bomenring("Bomen_zwembad", (0, 0), 22, 34, 30, seed=11)
    stad_rondom("Stad_zwembad", (0, 0), r=90, n=30, rijen=1, lit=0.0)
    S.strandwachtstoel("Badmeesterstoel", (13.5, 2, 0.05), rot_z=-90)
    D.plek("PLEK_jongen", (-3, -6.6, 0.05), rot_z=0)
    D.plek("PLEK_held", (2, -8.5, 0.05), rot_z=150)
    cams = [T.camera("CAM_9c_WIDE", (8, -9.5, 2.2), (-3, -5, 0.3), lens=26)]

# ---------------------------------------------------------------------------
elif VAR == "gymzaal":
    W, Dd, Hh = 28.0, 20.0, 8.0
    wins = [(a, a + 2.4, 5.6, 7.4) for a in [1.5 + k * 3.2 for k in range(8)]]
    room = I.room("Gymzaal", W, Dd, Hh, (0.86, 0.84, 0.78), (0.85, 0.55, 0.25), hide=(), ceiling=False, skirting=False,
                  holes={"back": wins, "front": [(12.5, 15.5, 0, 2.4)], "left": [(2.0, 3.6, 0, 2.2)]})
    room["floor"].data.materials[0] = T.pattern("sportvloer", (0.90, 0.58, 0.26), (0.86, 0.54, 0.23), grout=(0.70, 0.42, 0.18), size=(2.0, 0.12), mortar=0.004, offset=0.5)
    for a0, a1, z0, z1 in wins:
        I.window(f"Hoog_raam_{int(a0)}", W, Dd, "back", a0, a1, z0, z1)
    buiten_door_raam((0, Dd / 2), rz=0, afstand=6, stad=True)
    for side, (loc, rz, L) in {"back": ((0, Dd / 2 - 0.02, 0), 0, W), "left": ((-W / 2 + 0.02, 0, 0), 90, Dd), "right": ((W / 2 - 0.02, 0, 0), 90, Dd),
                               "front": ((0, -Dd / 2 + 0.02, 0), 0, W)}.items():
        T.box(f"Lambrisering_{side}", loc, (L, 0.04, 2.2), mt("lambrisering_gym", (0.30, 0.50, 0.72)), rot=(0, 0, rz), bevel=0, ol=0)
    # plafond: losse panelen tussen stalen balken + 4 lichtkoepels (het breekbare deel, 13b/13f3)
    pnl = mt("plafondpaneel", (0.90, 0.90, 0.88), rough=0.85)
    nx_, ny_ = 7, 5
    for i in range(nx_):
        for j in range(ny_):
            x = -W / 2 + (i + 0.5) * W / nx_
            y = -Dd / 2 + (j + 0.5) * Dd / ny_
            if (i, j) in ((1, 2), (3, 1), (3, 3), (5, 2)):
                T.box(f"Lichtkoepel_{i}_{j}", (x, y, Hh), (W / nx_ - 0.1, Dd / ny_ - 0.1, 0.08),
                      ND.pbr("lichtkoepel_glas", (0.85, 0.9, 0.95), rough=0.2, emit=(0.75, 0.8, 0.85), strength=0.6), bevel=0, ol=0)
                T.box(f"Lichtkoepel_kap_{i}_{j}", (x, y, Hh + 0.08), (W / nx_ - 0.3, Dd / ny_ - 0.3, 0.6),
                      ND.pbr("lichtkoepel_glas", (0.85, 0.9, 0.95)), bevel=0.25, ol=0)
            else:
                T.box(f"Plafond_paneel_{i}_{j}", (x, y, Hh), (W / nx_ - 0.04, Dd / ny_ - 0.04, 0.1), pnl, bevel=0, ol=0)
    staal = mt("staal_balk", (0.35, 0.38, 0.42), metal=0.6, rough=0.4)
    for i in range(nx_ + 1):
        T.box(f"Balk_{i}", (-W / 2 + i * W / nx_, 0, Hh - 0.45), (0.25, Dd, 0.45), staal, bevel=0, ol=0)
    T.box("Dak_buitenkant", (0, 0, Hh + 0.12), (W + 0.4, Dd + 0.4, 0.2), mt("dakbedekking", (0.25, 0.25, 0.27), rough=0.9), bevel=0, ol=0)
    bpy.data.objects["Dak_buitenkant"].visible_camera = False  # alleen tegen licht/regen van boven
    for i in range(nx_):
        for j in (1, 3):
            x = -W / 2 + (i + 0.5) * W / nx_
            T.box(f"Tl_gym_{i}_{j}", (x, -Dd / 2 + (j + 0.5) * Dd / ny_ + 2.0, Hh - 0.6), (1.6, 0.25, 0.08), T.glow("tl_gym", (0.97, 0.98, 1.0), 5), bevel=0.01, ol=0)
    for i in range(4):
        T.area_light(f"Zaallicht_{i}", (-10.5 + i * 7, 0, Hh - 0.7), (-10.5 + i * 7, 0, 0), size=(6, 14), color=(0.95, 0.97, 1.0), energy=1400)
    # podium + microfoon + spandoek
    T.box("Podium", (0, Dd / 2 - 2.2, 0), (10, 4, 0.9), mt("hout_podium", (0.45, 0.28, 0.16)), bevel=0.02, ol=0)
    T.box("Podium_trap", (-5.6, Dd / 2 - 3.6, 0), (1.2, 1.0, 0.45), mt("hout_podium", (0.45, 0.28, 0.16)), bevel=0.02, ol=0)
    T.cyl("Microfoon_standaard", (0, Dd / 2 - 3.4, 0.9), 0.012, 1.45, mt("chroom", (0.85, 0.86, 0.88), metal=1, rough=0.2), seg=8, ol=0)
    T.cyl("Microfoon_voet", (0, Dd / 2 - 3.4, 0.9), 0.15, 0.02, mt("chroom", (0.85, 0.86, 0.88), metal=1), seg=16, ol=0)
    T.sphere("Microfoon_kop", (0, Dd / 2 - 3.4, 2.38), 0.035, mt("mic_zwart", (0.08, 0.08, 0.09), rough=0.6), seg=12, ol=0)
    T.box("Spandoek", (0, Dd / 2 - 0.08, 3.6), (8, 0.03, 1.2), mt("spandoek_blauw", (0.10, 0.25, 0.60), rough=0.8), bevel=0, ol=0)
    S.label("Spandoek_tekst", "MONDAY ASSEMBLY", (0, Dd / 2 - 0.1, 3.95), 0.55, (1, 1, 1))
    # tribune langs de rechterwand
    for r in range(4):
        T.box(f"Tribune_trede_{r}", (W / 2 - 1.0 - r * 0.9, 0, 0), (0.9, Dd - 6, 0.5 + r * 0.5), mt("tribune_hout", (0.55, 0.40, 0.25)), bevel=0.01, ol=0)
        bpy.data.objects[f"Tribune_trede_{r}"].location.x = W / 2 - 0.45 - (3 - r) * 0.9
    # 300 stoelen: 15 rijen x 20, als gekoppelde instanties
    stoel_src = T.merge("Stoel_assembly", [T.box("Stoel_zit", (0, 0, 0.42), (0.44, 0.42, 0.04), mt("stoel_kunststof", (0.15, 0.30, 0.55), coat=0.4), bevel=0.01, ol=0),
                                           T.box("Stoel_rug", (0, 0.2, 0.46), (0.44, 0.03, 0.4), mt("stoel_kunststof", (0.15, 0.30, 0.55), coat=0.4), bevel=0.01, ol=0)]
                        + [T.cyl(f"Stoel_poot_{a}{b}", (a * 0.19, b * 0.18, 0), 0.012, 0.42, mt("chroom", (0.85, 0.86, 0.88), metal=1), seg=6, ol=0)
                           for a in (-1, 1) for b in (-1, 1)], ol=0)
    stoel_src.location = (-100, -100, 0)
    stoel_src.hide_render = True
    n = 0
    for r in range(15):
        for c in range(20):
            x = -10.3 + c * 0.95 + (1.2 if c >= 10 else 0) - 0.6
            y = Dd / 2 - 5.2 - r * 0.85
            T.instance(stoel_src, (x, y, 0), rot=(0, 0, 0), name=f"Stoel_{r:02d}_{c:02d}").hide_render = False
            n += 1
    D.brandalarm("Brandalarm_gym", (-W / 2 + 0.02, -3.0, 1.4), rot_z=-90)
    for k, (x, y, rz) in enumerate(((0, -Dd / 2 + 0.07, 0), (-W / 2 + 0.07, 2.8, 90))):
        S.wall_sign(f"Exit_{k}", ["EXIT"], (x, y, 2.6), rot_z=rz, w=0.6, h=0.22, bg=(0.05, 0.6, 0.25), fg=(1, 1, 1))
    for k in range(2):
        T.box(f"Basketbalbord_{k}", ((k * 2 - 1) * (W / 2 - 0.6), 0, 3.0), (0.05, 1.8, 1.05), mt("bord_wit", (0.96, 0.96, 0.94)), bevel=0.01, ol=0)
    D.plek("PLEK_directeur", (0, Dd / 2 - 3.6, 0.9), rot_z=180)
    D.plek("PLEK_held", (-6.0, -1.0, 0), rot_z=0)
    cams = [T.camera("CAM_13a_TRIBUNE", (W / 2 - 1.2, -Dd / 2 + 2.5, 3.6), (-2, 3, 1.0), lens=22),
            T.camera("CAM_13b_PLAFOND", (-4.0, -2.0, 1.4), (-4.0, 0.0, Hh), lens=24),
            T.camera("CAM_13f_WIDE", (0, -Dd / 2 + 0.8, 2.2), (0, 4, 1.5), lens=20),
            T.camera("CAM_13h2_LEEG", (-W / 2 + 1.5, -Dd / 2 + 1.5, 1.6), (3, 3, 1.5), lens=22)]

# ---------------------------------------------------------------------------
elif VAR.startswith("schoolplein"):
    regen = VAR == "schoolplein_regen"
    tegels = T.pattern("plein_tegels_v5", (0.60, 0.58, 0.55), (0.56, 0.54, 0.51), grout=(0.45, 0.44, 0.42), size=(0.3, 0.3))
    T.box("Plein", (0, 0, -0.05), (70, 50, 0.05), tegels, bevel=0, ol=0)
    P.ground("Gras_rond", (3000, 3000), (0.30, 0.50, 0.22), z=-0.06)
    sch = mt("gevel_school", (0.78, 0.42, 0.30), rough=0.8)
    raam = mt("raam_school", (0.35, 0.48, 0.6), rough=0.1)
    # schoolgebouw aan drie kanten (U-vorm)
    for nm, loc, size in (("School_achter", (0, 22, 0), (60, 12, 10)), ("School_links", (-32, 4, 0), (12, 34, 10)), ("School_rechts_laag", (32, 10, 0), (12, 16, 7))):
        T.box(nm, loc, size, sch, bevel=0.05, ol=0)
    for f in range(2):
        for k in range(16):
            T.box(f"Raam_achter_{f}_{k}", (-26 + k * 3.5, 15.95, 1.6 + f * 3.8), (2.4, 0.1, 2.2), raam, bevel=0, ol=0)
        for k in range(8):
            T.box(f"Raam_links_{f}_{k}", (-25.95, -10 + k * 3.8, 1.6 + f * 3.8), (0.1, 2.4, 2.2), raam, bevel=0, ol=0)
    T.box("School_deur", (0, 15.9, 0), (2.4, 0.2, 2.6), mt("deur_school", (0.15, 0.35, 0.70)), bevel=0.02, ol=0)
    # gymzaal (rechtsvoor) met plat dak in LOSSE DELEN (instorten 13h). Dak 6 x 4 delen, binnenkant donker.
    gx, gy, gw, gd, gh = 22, -10, 22, 16, 7.5
    gm = mt("gevel_gymzaal", (0.75, 0.70, 0.62), rough=0.8)
    for nm, loc, size in (("Gymzaal_wand_voor", (gx, gy - gd / 2, 0), (gw, 0.3, gh)), ("Gymzaal_wand_achter", (gx, gy + gd / 2, 0), (gw, 0.3, gh)),
                          ("Gymzaal_wand_links", (gx - gw / 2, gy, 0), (0.3, gd, gh)), ("Gymzaal_wand_rechts", (gx + gw / 2, gy, 0), (0.3, gd, gh))):
        T.box(nm, loc, size, gm, bevel=0.02, ol=0)
    T.box("Gymzaal_vloer", (gx, gy, -0.04), (gw - 0.4, gd - 0.4, 0.05), mt("sportvloer_buiten", (0.85, 0.55, 0.25)), bevel=0, ol=0)
    for k in range(6):
        T.box(f"Gymzaal_raam_{k}", (gx - gw / 2 + 2 + k * 3.6, gy - gd / 2 - 0.16, 5.0), (2.4, 0.05, 1.6), raam, bevel=0, ol=0)
    S.label("Gymzaal_bord", "GYM", (gx, gy - gd / 2 - 0.17, 3.2), 0.9, (0.95, 0.95, 0.92))
    dak = mt("dakbedekking", (0.25, 0.25, 0.27), rough=0.9)
    for i in range(6):
        for j in range(4):
            T.box(f"Dak_deel_{i}_{j}", (gx - gw / 2 + (i + 0.5) * gw / 6, gy - gd / 2 + (j + 0.5) * gd / 4, gh), (gw / 6 - 0.02, gd / 4 - 0.02, 0.25),
                  dak, bevel=0, ol=0)
    T.box("Dakrand_gym", (gx, gy, gh + 0.25), (gw + 0.3, gd + 0.3, 0.12), mt("dakrand_alu", (0.7, 0.72, 0.74), metal=0.6), bevel=0, ol=0)
    bpy.data.objects["Dakrand_gym"].modifiers.new("hol", "SOLIDIFY")
    # hekken, fietsenrek, bomen, klimrek
    P.railing("Hek_voor", [(-36, -24, 0), (36, -24, 0)], h=1.8, posts=2.5, color="donkergroen")
    S.klimrek("Klimrek", (-14, -6, 0), rot_z=20)
    for k in range(8):
        P.tree(f"Pleinboom_{k}", (-26 + k * 6.5, -20, 0), h=8, r=2.8, seed=k)
    for k in range(10):
        ST.bicycle(f"Fiets_rek_{k}", (-24 + k * 0.8, 13.5, 0), rot=90, color=[(0.85, 0.15, 0.12), (0.15, 0.35, 0.85), (0.1, 0.1, 0.1)][k % 3])
    bomenring("Bomen_school", (0, 0), 50, 75, 40, seed=13)
    stad_rondom("Wijk", (0, 0), r=120, n=36, rijen=1)
    if regen:
        H.regendruppels("Stortregen", ((-20, 30), (-26, 6), (0, 14)), 9000, seed=5, r=0.006, rek=4.0)
        T.box("Plassen", (0, -4, -0.002), (40, 20, 0.003), ND.pbr("plas_water", (0.25, 0.28, 0.3), rough=0.02, coat=1.0), bevel=0, ol=0)
    D.plek("PLEK_held", (8, -20, 0), rot_z=60)
    cams = [T.camera("CAM_11a_DRONE", (-10, -40, 18), (8, -4, 2), lens=24),
            T.camera("CAM_11d_LAAG", (3, -22.5, 0.4), (gx, gy, 5), lens=22),
            T.camera("CAM_13h_LAAG", (4, -26, 1.2), (gx, gy, 6), lens=24)]

# ---------------------------------------------------------------------------
setcheck.check(cams, OUT, binnen=BINNEN_SET)
T.finish(OUT, f"{NR}_{VAR}", cams)
