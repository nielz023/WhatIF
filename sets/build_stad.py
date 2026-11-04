"""Set (video 3, No Rules): stadscentrum met kruispunt, reclameborden en een lange laan.

Varianten:
    nacht      scène 1 en 6: cold open. Leeg kruispunt, vier reclameborden op rood
               (THERE ARE NO MORE RULES), verkeerslichten alle drie aan, lichte mist,
               één verlaten auto met een rood oplichtende telefoon op het dashboard.
    middag     scène 3e-3f: drukke stad, voetgangerslicht op rood, geparkeerde auto met bon.
    ochtend    scène 7a-7c: grijze ochtend, een rij auto's (rode auto voorop) voor rood.
    stroom     scène 0 en 10: de lange laan naar huis, 21:12. Skyline in blokken A-H en
               lantaarns per blok, zodat de stad blok voor blok uit kan (zie lib/stad.py).

Schakelbare dingen (voor de animatie):
    Billboard_N_reclame / _alarm      zichtbaarheid wisselen = bord klapt om naar rood
    VKL_*  materialen VKL_*_rood/_oranje/_groen  Emission Strength 0 = uit
    ramen_A..H / lantaarn_A..H en collecties Lantaarnlicht_A..H  (stroomuitval per blok)

Gebruik:
    python3 sets/build_stad.py <variant> [uitvoermap]
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402
from lib import toon as T  # noqa: E402
from lib import props as P  # noqa: E402
from lib import stad as S  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
VAR = args[0] if args else "nacht"
OUT = args[1] if len(args) > 1 else "/mnt/project-files/videos/geen-regels/sets/01_stad"

mood = dict(T.MOODS[{"nacht": "nacht", "middag": "dag", "ochtend": "bewolkt", "stroom": "avond", "winkelstraat": "bewolkt"}[VAR]])
if VAR == "winkelstraat":
    mood.update(sun_strength=0.65, sky_top=(0.46, 0.52, 0.60), exposure=0.05)
if VAR == "nacht":
    mood.update(ambient=(0.12, 0.15, 0.28), fog_start=12.0, fog_end=160.0, fog_max=0.6, exposure=0.1)
if VAR == "ochtend":
    mood.update(sky_top=(0.40, 0.46, 0.56), sky_horizon=(0.78, 0.76, 0.74), sun_strength=0.6, exposure=0.1)
if VAR == "stroom":
    mood.update(sky_top=(0.04, 0.06, 0.22), sky_horizon=(0.30, 0.22, 0.45), exposure=0.15)
T.new_scene("Stad_" + VAR, mood, samples=32)
rnd = random.Random(7)

NIGHT = VAR in ("nacht", "stroom")
LIT = {"nacht": 0.22, "middag": 0.0, "ochtend": 0.08, "stroom": 0.6, "winkelstraat": 0.0}[VAR]
ROAD_W, WALK = 12.0, 4.0          # rijbaan 12 m, stoep 4 m
EDGE = ROAD_W / 2 + WALK          # gevellijn op 10 m van het midden
asfalt = T.toon("asfalt", (0.20, 0.20, 0.23))
stoep = T.toon("stoep_tegels", (0.58, 0.57, 0.55))
band = T.toon("stoeprand_beton", (0.72, 0.71, 0.68))
verf = T.toon("wegverf_wit", (0.92, 0.92, 0.90))
FACADES = [(0.70, 0.56, 0.46), (0.55, 0.58, 0.64), (0.80, 0.72, 0.60), (0.48, 0.50, 0.55), (0.76, 0.48, 0.38),
           (0.86, 0.82, 0.74)]


def road(name, center, length, along="x", gap=0.0):
    """Rijbaan met stoepen en stoepranden. gap > 0: stoep en band onderbroken rond het kruispunt
    (|afstand tot het midden| < gap), zodat ze niet over de andere weg heen lopen."""
    cx, cy = center
    segs = [(cx if along == "x" else cy, length)] if not gap else \
        [((gap + length / 2) / 2 * s, length / 2 - gap) for s in (1, -1)]
    if along == "x":
        T.plane(name, (cx, cy, 0.0), (length, ROAD_W), asfalt)
    else:
        T.plane(name, (cx, cy, 0.0), (ROAD_W, length), asfalt)
    for k, (c, ln) in enumerate(segs):
        for s in (1, -1):
            if along == "x":
                T.box(f"{name}_stoep{s}_{k}", (c, cy + s * (ROAD_W / 2 + WALK / 2), 0), (ln, WALK, 0.15), stoep, bevel=0.0, ol=0)
                T.box(f"{name}_band{s}_{k}", (c, cy + s * (ROAD_W / 2 + 0.1), 0), (ln, 0.2, 0.16), band, bevel=0.03, ol=0)
            else:
                T.box(f"{name}_stoep{s}_{k}", (cx + s * (ROAD_W / 2 + WALK / 2), c, 0), (WALK, ln, 0.15), stoep, bevel=0.0, ol=0)
                T.box(f"{name}_band{s}_{k}", (cx + s * (ROAD_W / 2 + 0.1), c, 0), (0.2, ln, 0.16), band, bevel=0.03, ol=0)


def lane_marks(name, along, start, end, off=0.0, step=6.0):
    k = 0
    v = start
    while v < end:
        if along == "x":
            T.plane(f"{name}_{k}", (v, off, 0.005), (3.0, 0.15), verf)
        else:
            T.plane(f"{name}_{k}", (off, v, 0.005), (0.15, 3.0), verf)
        v += step
        k += 1


def row(name, xs, y, rot, block, shops=()):
    """Rij gebouwen langs een straat; xs = middelpunten, y = gevellijn, rot = richting."""
    out = []
    for i, x in enumerate(xs):
        w = rnd.uniform(10.5, 13.0)
        shop = shops[i] if i < len(shops) else None
        loc = (x, y, 0) if rot in (0, 180) else (y, x, 0)
        out.append(S.building(f"{name}{i}", loc, w=w, d=12, floors=rnd.randint(5, 9), color=rnd.choice(FACADES), lit=LIT,
                              seed=rnd.randint(0, 999), rot_z=rot, shop=shop, block=block,
                              shop_color=rnd.choice([(0.85, 0.15, 0.12), (0.15, 0.35, 0.7), (0.12, 0.5, 0.3), (0.95, 0.6, 0.1)])))
    return out


# ---------------------------------------------------------------------------
# Kruispunt (nacht, middag, ochtend)
# ---------------------------------------------------------------------------
def kruispunt():
    T.use_collection(T.collection("Wegen"))
    P.ground("Ondergrond", (500, 500), (0.30, 0.30, 0.32), z=-0.03)
    road("Weg_x", (0, 0), 220, "x", gap=ROAD_W / 2)
    road("Weg_y", (0, 0), 220, "y", gap=EDGE)
    T.plane("Kruisvlak", (0, 0, 0.002), (ROAD_W, ROAD_W), asfalt)
    for s in (1, -1):
        lane_marks(f"Streep_x{s}", "x", s * 12 if s > 0 else -110, 110 if s > 0 else -12)
        lane_marks(f"Streep_y{s}", "y", s * 12 if s > 0 else -110, 110 if s > 0 else -12)
    S.crosswalk("Zebrapad_N", (0, ROAD_W / 2 + 2.0, 0), ROAD_W, 3.0)
    S.crosswalk("Zebrapad_Z", (0, -ROAD_W / 2 - 2.0, 0), ROAD_W, 3.0)
    S.crosswalk("Zebrapad_O", (ROAD_W / 2 + 2.0, 0, 0), ROAD_W, 3.0, rot_z=90)
    S.crosswalk("Zebrapad_W", (-ROAD_W / 2 - 2.0, 0, 0), ROAD_W, 3.0, rot_z=90)
    for s in (1, -1):  # stopstrepen
        T.plane(f"Stopstreep_x{s}", (s * (ROAD_W / 2 + 4.0), -s * ROAD_W / 4, 0.006), (0.4, ROAD_W / 2), verf)
        T.plane(f"Stopstreep_y{s}", (s * ROAD_W / 4, s * (ROAD_W / 2 + 4.0), 0.006), (ROAD_W / 2, 0.4), verf)

    T.use_collection(T.collection("Gebouwen"))
    xs = [16.5, 29, 41.5, 54, 66.5]
    blocks = {"N": "B", "Z": "A", "O": "C", "W": "D"}
    shops_n = ("CAFE", None, "BOOKS")
    shops_z = ("PIZZA", "SHOES")
    row("Gebouw_N_oost", xs, EDGE, 0, "B", shops_n)
    row("Gebouw_N_west", [-x for x in xs], EDGE, 0, "B", ("BAKERY",))
    row("Gebouw_Z_oost", xs, -EDGE, 180, "A", shops_z)
    row("Gebouw_Z_west", [-x for x in xs], -EDGE, 180, "A", ("PHONES",))
    # langs de y-weg pas na de hoekpanden (vanaf 23 m)
    ys = [29, 41.5, 54, 66.5]
    row("Gebouw_O_noord", ys, EDGE, -90, "C")
    row("Gebouw_O_zuid", [-y for y in ys], EDGE, -90, "C")
    row("Gebouw_W_noord", ys, -EDGE, 90, "D")
    row("Gebouw_W_zuid", [-y for y in ys], -EDGE, 90, "D")
    # sluitstuk aan het eind van de y-weg (achter het kruispunt, groot scherm erop)
    S.building("Gebouw_eind_noord", (0, 82, 0), w=30, d=14, floors=11, color=(0.50, 0.52, 0.58), lit=LIT, seed=4, block="E")
    S.building("Gebouw_eind_zuid", (0, -82, 0), w=30, d=14, floors=8, color=(0.66, 0.58, 0.50), lit=LIT, seed=5, rot_z=180, block="E")
    S.skyline("Skyline", (0, 110), rows=3, per_row=12, seed=9, lit=LIT * 1.2 if NIGHT else 0.0)

    T.use_collection(T.collection("Reclameborden"))
    mode = "alarm" if VAR == "nacht" else "reclame"
    ads = [("SUMMER SALE", "-50%"), ("NEW PHONE", "PRE-ORDER NOW"), ("FRESH COLA", "ICE COLD"), ("CITY ZOO", "OPEN DAILY")]
    adc = [(0.98, 0.75, 0.15), (0.20, 0.55, 0.98), (0.92, 0.18, 0.20), (0.25, 0.80, 0.45)]
    # vier grote schermen op de hoekpanden + één reus op het eindgebouw
    spots = [((16.5, EDGE - 0.2, 0), 0, 11), ((-16.5, EDGE - 0.2, 0), 0, 12), ((16.5, -EDGE + 0.2, 0), 180, 10),
             ((-16.5, -EDGE + 0.2, 0), 180, 11)]
    for i, (loc, rz, z) in enumerate(spots):
        S.billboard(f"Billboard_{i + 1}", loc, rot_z=rz, w=8.5, h=4.6, z=z, ad=ads[i], ad_col=adc[i], mode=mode, wall=True)
    S.billboard("Billboard_groot", (0, 81.6, 0), w=20, h=10, z=24, ad=("THE FUTURE", "IS NOW"), ad_col=(0.55, 0.30, 0.95),
                mode=mode, wall=True)

    T.use_collection(T.collection("Straatmeubilair"))
    state = {"nacht": "alles", "middag": "groen", "ochtend": "rood"}[VAR]
    S.traffic_light("VKL_zuid", (ROAD_W / 2 + 0.6, -ROAD_W / 2 - 4.5, 0.15), rot_z=180, state=state, arm=5.2)
    S.traffic_light("VKL_noord", (-ROAD_W / 2 - 0.6, ROAD_W / 2 + 4.5, 0.15), rot_z=0, state=state, arm=5.2)
    S.traffic_light("VKL_oost", (ROAD_W / 2 + 4.5, ROAD_W / 2 + 0.6, 0.15), rot_z=-90, state="rood" if VAR == "middag" else state, arm=5.2)
    S.traffic_light("VKL_west", (-ROAD_W / 2 - 4.5, -ROAD_W / 2 - 0.6, 0.15), rot_z=90, state="rood" if VAR == "middag" else state, arm=5.2)
    ped = "rood"
    for i, (x, y, rz) in enumerate([(-ROAD_W / 2 - 0.5, -ROAD_W / 2 - 1.0, 180), (ROAD_W / 2 + 0.5, ROAD_W / 2 + 1.0, 0),
                                    (ROAD_W / 2 + 1.0, -ROAD_W / 2 - 0.5, 90), (-ROAD_W / 2 - 1.0, ROAD_W / 2 + 0.5, -90)]):
        S.ped_light(f"Voetgangerslicht_{i}", (x, y, 0.15), rot_z=rz, state=ped)
    k = 0
    for d in (14, 30, 46, 62):
        for s in (1, -1):
            S.street_lamp(f"Lantaarn_x_{k}", (d * s, ROAD_W / 2 + 0.6, 0.15), rot_z=0, on=NIGHT, block="B", energy=380)
            S.street_lamp(f"Lantaarn_y_{k}", (ROAD_W / 2 + 0.6, d * s, 0.15), rot_z=-90, on=NIGHT, block="C", energy=380)
            k += 1
    for i, (x, y) in enumerate([(22, -8.5), (-22, 8.5), (35, 8.5), (-35, -8.5)]):
        P.tree(f"Straatboom_{i}", (x, y, 0.15), h=6.5, r=2.2, seed=i)
        P.bench(f"Bank_{i}", (x + 3, y + (0.9 if y > 0 else -0.9), 0.15), rot=180 if y > 0 else 0)
        P.bin_(f"Prullenbak_{i}", (x - 2.5, y, 0.15))

    T.use_collection(T.collection("Auto's"))
    cols = [(0.85, 0.12, 0.10), (0.92, 0.92, 0.92), (0.12, 0.30, 0.75), (0.15, 0.15, 0.17), (0.95, 0.70, 0.10), (0.30, 0.60, 0.40)]
    if VAR == "nacht":
        # verlaten auto midden op de y-weg met de telefoon die rood oplicht (scène 1d)
        S.car2("Auto_verlaten", (-3.0, 24, 0), rot=95, color=(0.75, 0.78, 0.82), doors_open=("L",), phone=True)
        S.car2("Auto_verlaten2", (40, -2.8, 0), rot=172, color=(0.12, 0.30, 0.75), lights=True)
    elif VAR == "ochtend":
        # rij voor rood op de zuidelijke y-weg, rode auto voorop (scène 7b-7c)
        for i in range(5):
            S.car2(f"Auto_wacht_{i}", (3.0, -ROAD_W / 2 - 6.6 - i * 5.6, 0), rot=90, color=cols[i] if i else cols[0],
                   kind="sedan" if i % 2 else "hatch", lights=True)
        for i in range(3):
            S.car2(f"Auto_wacht_x_{i}", (-ROAD_W / 2 - 6.6 - i * 5.6, -3.0, 0), rot=0, color=cols[(i + 3) % 6], lights=True)
    else:
        # geparkeerd langs de stoep, één auto met een parkeerbon (scène 3e)
        for i, x in enumerate((20, 26, 38, -20, -32, -44)):
            S.car2(f"Auto_geparkeerd_{i}", (x, ROAD_W / 2 - 1.3, 0), rot=180, color=cols[i % 6], kind="sedan" if i % 2 else "hatch")
        T.box("Parkeerbon", (20 - 1.2, ROAD_W / 2 - 1.3, 1.02), (0.12, 0.22, 0.005), T.toon("parkeerbon_wit", (0.97, 0.97, 0.9)),
              rot=(0, -28, 0), bevel=0, ol=0)
        S.car2("Auto_rijdt", (34, 3.0, 0), rot=180, color=cols[2])
        S.sign("Bord_NO_PARKING", ["NO", "PARKING"], (24, ROAD_W / 2 + 0.6, 0.15), rot_z=180, w=0.5, h=0.6,
               bg=(0.95, 0.95, 0.95), fg=(0.85, 0.1, 0.1), post_h=2.0)

    T.use_collection(None)
    T.character((0, -4, 0), rot_z=0)
    if VAR == "nacht":
        T.point_light("Maan_vul", (0, -30, 30), color=(0.45, 0.55, 1.0), energy=6000, radius=8, shadow=False)
        return [
            T.camera("CAM_01_kruispunt_wide", (0, -22, 1.5), (0, 10, 5.5), lens=22),
            T.camera("CAM_02_laag_omhoog", (2.5, -7, 0.4), (0, 8, 9), lens=16),
            T.camera("CAM_03_verkeerslicht", (-0.8, 3.5, 3.4), (-2.7, 10.5, 4.4), lens=40),
            T.camera("CAM_04_auto_telefoon", (-7.5, 21, 1.8), (-3.0, 24, 1.0), lens=30),
        ]
    if VAR == "ochtend":
        return [
            T.camera("CAM_01_rij_voor_rood", (8.5, -5.0, 2.6), (2.0, -22, 1.0), lens=24),
            T.camera("CAM_02_rode_auto", (7.8, -16.0, 1.4), (3.0, -13.0, 1.1), lens=35),
            T.camera("CAM_03_kruispunt_hoog", (-3, -42, 14), (0, 0, 0), lens=24),
        ]
    return [
        T.camera("CAM_01_stoep_wacht", (-ROAD_W / 2 - 2.5, -ROAD_W / 2 - 9, 1.6), (-2, 6, 2.0), lens=24),
        T.camera("CAM_02_parkeerbon", (17.5, ROAD_W / 2 + 1.6, 1.6), (20, ROAD_W / 2 - 1.3, 1.0), lens=30),
        T.camera("CAM_03_kruispunt_wide", (3.5, -34, 6), (0, 4, 3), lens=22),
    ]


# ---------------------------------------------------------------------------
# Lange laan voor de stroomuitval (scène 0 en 10)
# ---------------------------------------------------------------------------
def laan():
    T.use_collection(T.collection("Laan"))
    P.ground("Ondergrond", (900, 900), (0.26, 0.26, 0.28), z=-0.03)
    L = 400
    road("Laan", (0, L / 2 - 30), L, "y")
    lane_marks("Middenstreep", "y", -28, L - 30, off=0.0)
    T.use_collection(T.collection("Gebouwen per blok"))
    # acht blokken van 45 m, A dichtbij de camera, H bij de horizon (golf rolt van H naar A)
    for b in range(8):
        blk = "ABCDEFGH"[b]
        y0 = -20 + b * 45
        ys = [y0 + 6 + i * 12.5 for i in range(3)]
        row(f"Blok{blk}_oost", ys, EDGE, -90, blk, ("WATER POINT",) if b == 0 else ())
        row(f"Blok{blk}_west", ys, -EDGE, 90, blk)
        for k, y in enumerate((y0 + 6, y0 + 28)):
            S.street_lamp(f"Lantaarn_{blk}_{k}o", (ROAD_W / 2 + 0.6, y, 0.15), rot_z=-90, on=True, block=blk, energy=420)
            S.street_lamp(f"Lantaarn_{blk}_{k}w", (-ROAD_W / 2 - 0.6, y + 11, 0.15), rot_z=90, on=True, block=blk, energy=420)
    S.skyline("Skyline", (0, 400), rows=3, per_row=14, seed=21, lit=0.6)
    # achterliggende rijen (voor het droneshot): zelfde blokletters, zodat ze mee uitgaan
    for b in range(8):
        blk = "ABCDEFGH"[b]
        for side in (1, -1):
            for k, off in enumerate((34, 58)):
                for i in range(3):
                    y = -20 + b * 45 + 6 + i * 13 + k * 5
                    S.building(f"Achter{blk}_{side}_{k}_{i}", (side * off, y, 0), w=12, d=12, floors=rnd.randint(4, 8),
                               color=rnd.choice(FACADES), lit=0.6, seed=rnd.randint(0, 999), rot_z=-90 if side > 0 else 90, block=blk)
    T.use_collection(T.collection("Fiets"))
    S.fiets2("Fiets_held", (1.5, 0, 0), rot=90, color=(0.15, 0.35, 0.75), lamp_on=True, jerrycan=True)
    for i, y in enumerate((30, 75, 150)):
        S.car2(f"Auto_geparkeerd_{i}", (ROAD_W / 2 - 1.3, y, 0), rot=90, color=[(0.85, 0.12, 0.1), (0.9, 0.9, 0.9), (0.15, 0.15, 0.17)][i])
    T.use_collection(None)
    T.character((-1.2, 0, 0), rot_z=0)
    T.point_light("Maan_vul", (0, -40, 40), color=(0.45, 0.55, 1.0), energy=9000, radius=8, shadow=False)
    return [
        T.camera("CAM_01_laag_voor_fiets", (1.5, -9, 0.7), (1.5, 30, 3.0), lens=24),
        T.camera("CAM_02_drone_golf", (0, -40, 55), (0, 120, 0), lens=28),
        T.camera("CAM_03_track_naast_fiets", (-3.5, 2.0, 1.2), (2.0, 1.5, 1.0), lens=30),
    ]


def apotheek(name, loc, rot_z):
    """Apotheek met hol interieur (scène 12e-12f): open deur, lege schappen, omgevallen rek,
    toonbank met laatjes (<naam>_la_N, schuiven langs local y). Gevel kijkt naar local -y."""
    root = S._empty(name, size=0.5)
    W, D, H = 8.0, 6.0, 3.4
    muur = T.toon("muur_apotheek", (0.93, 0.95, 0.93))
    gevel = T.toon("gevel_apotheek", (0.80, 0.86, 0.82))
    parts = []
    def add(o):
        o.parent = root
        parts.append(o)
        return o
    add(T.box(name + "_vloer", (0, D / 2, -0.02), (W, D, 0.04), T.pattern("vloer_apotheek", (0.90, 0.90, 0.88), (0.80, 0.84, 0.82), size=(0.4, 0.4), kind="schaak"), bevel=0, ol=0))
    add(T.box(name + "_achter", (0, D, 0), (W, 0.2, H), muur, bevel=0, ol=0))
    for sx in (-1, 1):
        add(T.box(f"{name}_zij{sx}", (sx * W / 2, D / 2, 0), (0.2, D, H), muur, bevel=0, ol=0))
    add(T.box(name + "_plafond", (0, D / 2, H), (W, D, 0.2), muur, bevel=0, ol=0))
    # gevel: deur (links) en een etalage zonder glas (rechts)
    add(T.box(name + "_gevel_l", (-3.5, 0, 0), (1.0, 0.25, H), gevel, bevel=0.01, ol=0))
    add(T.box(name + "_gevel_m", (-1.5, 0, 0), (1.0, 0.25, H), gevel, bevel=0.01, ol=0))
    add(T.box(name + "_gevel_r", (3.75, 0, 0), (0.5, 0.25, H), gevel, bevel=0.01, ol=0))
    add(T.box(name + "_gevel_boven", (0, 0, 2.4), (W, 0.25, H - 2.4 + 2.0), gevel, bevel=0.01, ol=0))
    add(T.box(name + "_etalage_onder", (1.25, 0, 0), (4.5, 0.25, 0.6), gevel, bevel=0.01, ol=0))
    for j in range(5):
        add(T.box(f"{name}_glasscherf_{j}", (rnd.uniform(-0.5, 3.0), -rnd.uniform(0.3, 1.5), 0.005), (0.25, 0.18, 0.01),
                  T.glass("glasscherf", (0.75, 0.88, 0.95), alpha=0.5), rot=(0, 0, rnd.uniform(0, 90)), bevel=0, ol=0))
    deur = S._empty(name + "_deur", (-3.0, -0.1, 0), size=0.2)
    deur.parent = root
    T.box(name + "_deurblad", (0.5, 0, 0), (1.0, 0.05, 2.3), T.glass("deurglas_apotheek", (0.7, 0.85, 0.9), alpha=0.35), bevel=0.01, ol=0).parent = deur
    deur.rotation_euler.z = math.radians(-80)   # staat open
    S.label(name + "_naam", "PHARMACY", (1.0, -0.14, 2.75), 0.45, (0.10, 0.55, 0.30), extrude=0.02).parent = root
    S.apotheekkruis(name + "_kruis", (-3.5, -0.9, 3.4), rot_z=90).parent = root
    # interieur
    hout = T.toon("hout_toonbank", (0.85, 0.78, 0.66))
    add(T.box(name + "_toonbank", (0, 3.4, 0), (4.0, 0.7, 1.0), hout, bevel=0.02, ol=0))
    add(T.box(name + "_toonbankblad", (0, 3.4, 1.0), (4.2, 0.8, 0.05), T.toon("toonbank_blad", (0.95, 0.95, 0.95)), bevel=0.01, ol=0))
    for k in range(6):
        la = S._empty(f"{name}_la_{k}", ((k % 3 - 1) * 1.2, 3.76, 0.55 - (k // 3) * 0.35), size=0.1)
        la.parent = root
        T.box(f"{name}_la_{k}_front", (0, 0, 0), (1.05, 0.03, 0.28), hout, bevel=0.01, ol=0).parent = la
        T.box(f"{name}_la_{k}_greep", (0, 0.03, 0.12), (0.2, 0.03, 0.03), T.toon("metaal_greep", (0.7, 0.7, 0.72)), bevel=0, ol=0).parent = la
        if k == 1:
            la.location.y += 0.35   # deze la staat open
    sch = T.toon("schap_wit", (0.95, 0.95, 0.95))
    for k in range(5):
        add(T.box(f"{name}_wandschap_{k}", (0, D - 0.3, 0.3 + k * 0.5), (7.0, 0.4, 0.03), sch, bevel=0, ol=0))
    for k in range(3):   # nog drie doosjes over
        S.medicijndoos(f"{name}_doosje_{k}", (rnd.uniform(-3, 3), D - 0.3, 0.83 + 0.5 * (k % 2)), rot_z=rnd.uniform(-20, 20)).parent = root
    rek = S._empty(name + "_rek_omgevallen", (2.6, 2.0, 0.0), size=0.2)
    rek.parent = root
    for k in range(4):
        T.box(f"{name}_rek_plank{k}", (0, 0, 0.2 + k * 0.4), (1.4, 0.4, 0.03), sch, bevel=0, ol=0).parent = rek
    for x in (-0.7, 0.7):
        T.box(f"{name}_rek_staander{x}", (x, 0, 0), (0.04, 0.4, 1.6), sch, bevel=0, ol=0).parent = rek
    rek.rotation_euler = (math.radians(-82), 0, math.radians(25))
    rek.location.z = 0.22
    T.point_light(name + "_daglicht", (0, 0, 0), color=(0.9, 0.95, 1.0), energy=120, radius=1.5).parent = root
    bpy.data.objects[name + "_daglicht"].location = (0, 2.5, 2.8)
    root.location = loc
    root.rotation_euler.z = math.radians(rot_z)
    return root


def winkelstraat():
    """Scène 12d: winkelstraat na een week zonder regels: etalages zonder glas, kledingrekken op straat."""
    T.use_collection(T.collection("Winkelstraat"))
    P.ground("Ondergrond", (500, 500), (0.30, 0.30, 0.32), z=-0.03)
    road("Straat", (0, 40), 160, "y")
    T.use_collection(T.collection("Winkels"))
    names_o = ("SHOES", "FASHION", None, "TOYS", "PHONES")
    names_w = ("BAKERY", "JEANS", "BOOKS", None, "SPORT", "CAFE")
    row("Winkel_oost", [4, 18, 46, 58, 70], EDGE, -90, "W", names_o)
    row("Winkel_west", [4, 16, 28, 40, 52, 64], -EDGE, 90, "W", names_w)
    apotheek("Apotheek", (EDGE, 32, 0), -90)
    T.use_collection(T.collection("Rommel"))
    for i in range(5):   # kledingrekken op straat
        y = rnd.uniform(5, 60)
        x = rnd.choice((-1, 1)) * rnd.uniform(3, 8)
        rk = S._empty(f"Kledingrek_{i}", (x, y, 0), size=0.2)
        T.to_mesh(T.tube(f"Kledingrek_{i}_buis", [(-0.7, 0, 0), (-0.7, 0, 1.5), (0.7, 0, 1.5), (0.7, 0, 0)], 0.02,
                         T.toon("chroom_rek", (0.8, 0.82, 0.85)))).parent = rk
        for k in range(5):
            T.box(f"Kledingrek_{i}_kleding{k}", (-0.5 + k * 0.25, 0, 0.75), (0.05, 0.45, 0.7),
                  T.toon(f"stof_kleding_{k}", [(0.85, 0.2, 0.2), (0.2, 0.4, 0.85), (0.95, 0.8, 0.2), (0.3, 0.7, 0.4), (0.9, 0.5, 0.7)][k]),
                  bevel=0.02, ol=0).parent = rk
        rk.rotation_euler.z = math.radians(rnd.uniform(0, 180))
        if i % 2:
            rk.rotation_euler.x = math.radians(85)
            rk.location.z = 0.05
    for i in range(12):
        T.box(f"Papier_{i}", (rnd.uniform(-6, 6), rnd.uniform(0, 70), 0.004), (0.21, 0.29, 0.002), T.toon("papier_wit", (0.97, 0.97, 0.95)),
              rot=(0, 0, rnd.uniform(0, 180)), bevel=0, ol=0)
    S.winkelkar("Winkelkar_straat", (-4, 22, 0), rot=60, tipped=True)
    for i in range(4):
        P.tree(f"Straatboom_{i}", ((-8.5, 8.5)[i % 2], 12 + i * 14, 0.15), h=6.0, r=2.0, seed=i)
    S.fiets2("Fiets_held", (-1.5, 10, 0), rot=90, color=(0.15, 0.35, 0.75))
    S.fiets2("Fiets_vriend", (1.0, 9.0, 0), rot=95, color=(0.85, 0.12, 0.10), sticker=True)
    T.use_collection(None)
    T.character((-2.2, 11, 0), rot_z=0)
    return [T.camera("CAM_01_winkelstraat_pushin", (0, -6, 1.8), (0, 30, 2.5), lens=26),
            T.camera("CAM_02_apotheek_deur", (2.0, 24.5, 1.6), (EDGE, 30.5, 1.3), lens=28),
            T.camera("CAM_03_apotheek_binnen", (EDGE + 1.5, 30.5, 1.5), (EDGE + 4.0, 32, 1.0), lens=22)]


cams = laan() if VAR == "stroom" else winkelstraat() if VAR == "winkelstraat" else kruispunt()
blend, renders = T.finish(OUT, "stad_" + VAR, cams)
print("KLAAR", blend, renders)
