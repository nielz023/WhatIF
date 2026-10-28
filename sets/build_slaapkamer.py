"""Set: Slaapkamer van de hoofdrolspeler.
Video 1, dag 1 (titel, warm ochtendlicht) en dag 7 (nacht, blauw telefoonlicht).
Video 2 (10x sneller):
    dag2      dag 2, 06:20: vroeg licht, wekker op 06:20, glas water op het nachtkastje
    broertje  dag 1 's avonds: de kamer van het broertje, mintgroen, dinoposter, origami op het bureau

Gebruik:
    blender -b -P sets/build_slaapkamer.py -- [ochtend|nacht|dag2|broertje] [uitvoermap]
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402,F401
from lib import toon as T  # noqa: E402
from lib import props as P  # noqa: E402
from lib import interior as I  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
MOOD = args[0] if args else "ochtend"
BRO = MOOD == "broertje"
DAG2 = MOOD == "dag2"
V2 = BRO or DAG2
OUT = args[1] if len(args) > 1 else ("/mnt/project-files/videos/10x-sneller/sets/02_slaapkamer" if V2 else "/mnt/project-files/sets/02_slaapkamer")
NIGHT = MOOD in ("nacht", "broertje")

mood = dict(T.MOODS["nacht" if NIGHT else "ochtend"])
if DAG2:
    mood.update(sun_rot=(84, 0, 140), sun_strength=0.8, sky_top=(0.30, 0.40, 0.75), sky_horizon=(0.95, 0.70, 0.55),
                ambient=(0.22, 0.22, 0.30))
elif not NIGHT:
    mood.update(sun_rot=(45, 0, 140), sun_strength=1.5, ambient=(0.30, 0.27, 0.30))
elif BRO:
    mood.update(sky_top=(0.03, 0.04, 0.14), sky_horizon=(0.20, 0.16, 0.35), sun_rot=(58, 0, 170), sun_strength=0.2,
                ambient=(0.08, 0.08, 0.14))
else:
    mood.update(sun_rot=(58, 0, 170), sun_strength=0.25, ambient=(0.06, 0.07, 0.13))
T.new_scene("Slaapkamer_" + MOOD, mood, samples=48)

W, D, H = 4.2, 3.8, 2.6
WIN = (2.4, 3.8, 0.95, 2.15)  # achterwand, a0, a1, z0, z1
DOOR_A = 3.0

T.use_collection(T.collection("Kamer"))
I.room("Slaapkamer", W, D, H, wall_color=(0.66, 0.86, 0.72) if BRO else (0.86, 0.76, 0.56),
       floor_color=(0.62, 0.42, 0.24),
       holes={"back": [WIN], "right": [(DOOR_A - 0.5, DOOR_A + 0.5, 0, 2.12)]})
I.window("Raam", W, D, "back", *WIN, curtains=(0.25, 0.45, 0.85) if BRO else (0.95, 0.82, 0.35), open_frac=0.45)
I.door("Deur", W, D, "right", DOOR_A)
I.ceiling_lamp("Plafondlamp", (0, 0, H), on=BRO)
I.rug("Vloerkleed", (0.25, -0.35, 0), (2.0, 1.4), (0.95, 0.75, 0.2) if BRO else (0.85, 0.35, 0.25), round_=True)

# ---------------------------------------------------------------------------
# Bed met blauw dekbed (hoofdeinde tegen de achterwand, links)
# ---------------------------------------------------------------------------
T.use_collection(T.collection("Bed en nachtkastje"))
BX, BY = -1.52, 0.86
wood = T.toon("bed_hout", (0.72, 0.48, 0.26))
bed = [T.box("Bed_frame", (0, 0, 0.12), (1.06, 2.06, 0.25), wood, bevel=0.03, ol=0),
       T.box("Bed_hoofdeinde", (0, 1.02, 0), (1.06, 0.07, 0.95), wood, bevel=0.03, ol=0),
       T.box("Bed_voeteneinde", (0, -1.02, 0), (1.06, 0.07, 0.55), wood, bevel=0.03, ol=0)]
for x in (-0.48, 0.48):
    for y in (-0.98, 0.98):
        bed.append(T.box(f"Bed_poot{x}{y}", (x, y, 0), (0.07, 0.07, 0.15), wood, bevel=0, ol=0))
bed_o = T.merge("Bed", bed, ol=0.012)
mat = T.box("Matras", (0, 0, 0.37), (1.0, 1.98, 0.18), P.m("wit"), bevel=0.06, ol=0.01)
pillow = T.box("Kussen", (0, 0.72, 0.55), (0.72, 0.42, 0.16), T.toon("kussen", (0.96, 0.96, 0.98)), bevel=0.07, ol=0.01)
DUV = T.toon("dekbed_groen", (0.25, 0.62, 0.30)) if BRO else T.toon("dekbed_blauw", (0.12, 0.32, 0.78))
duvet = T.box("Dekbed_groen" if BRO else "Dekbed_blauw", (0, -0.25, 0.52), (1.1, 1.5, 0.14), DUV, bevel=0.06, ol=0.012)
duvet_fold = T.box("Dekbed_omslag", (0, 0.42, 0.53), (1.1, 0.22, 0.17), T.toon("dekbed_geel", (0.98, 0.85, 0.35)) if BRO else T.toon("dekbed_licht", (0.80, 0.86, 0.96)), bevel=0.07, ol=0.01)
# een paar bobbels voor een beslapen dekbed
lumps = [T.sphere(f"Dekbed_bobbel{k}", (x, y, 0.62), 0.22, DUV, scale=(1.4, 1.2, 0.35), seg=16, ol=0.01)
         for k, (x, y) in enumerate([(-0.2, -0.1), (0.18, -0.5), (-0.1, -0.75)])]
T.group("Bed (geheel)", [bed_o, mat, pillow, duvet, duvet_fold] + lumps, loc=(BX, BY, 0))

ns = [T.box("Nachtkastje_body", (0, 0, 0), (0.46, 0.4, 0.55), T.toon("nachtkastje", (0.92, 0.90, 0.85)), bevel=0.02, ol=0),
      T.box("Nachtkastje_la", (0, -0.2, 0.3), (0.38, 0.02, 0.16), T.toon("nachtkastje_la", (0.85, 0.80, 0.72)), bevel=0.01, ol=0),
      T.sphere("Nachtkastje_knop", (0, -0.22, 0.38), 0.02, P.m("metaal"), seg=8, ol=0)]
ns_o = T.merge("Nachtkastje", ns, ol=0.01)
clock = [T.box("Wekker_body", (0, 0, 0), (0.16, 0.08, 0.11), T.toon("wekker_rood", (0.85, 0.12, 0.10)), bevel=0.03, ol=0),
         T.box("Wekker_scherm", (0, -0.041, 0.025), (0.12, 0.005, 0.06), T.glow("wekker_cijfers", (1.0, 0.25, 0.15), 2.5) if NIGHT else T.toon("wekker_scherm", (0.1, 0.1, 0.1)), bevel=0, ol=0)]
clock_o = T.merge("Wekker", clock, ol=0.006)
if DAG2:
    T.text("Wekker_tijd", "06:20", (0, -0.0445, 0.034), 0.034, T.glow("wekker_cijfers", (1.0, 0.25, 0.15), 6), extrude=0.001).parent = clock_o
clock_o.location = (0.09, -0.05, 0.55)
clock_o.rotation_euler.z = math.radians(-15)
lamp = [T.cyl("Leeslamp_voet", (0, 0, 0), 0.07, 0.03, P.m("zwart"), seg=16, ol=0),
        T.cyl("Leeslamp_stang", (0, 0, 0.03), 0.012, 0.3, P.m("zwart"), seg=8, ol=0),
        T.cyl("Leeslamp_kap", (0, 0, 0.28), 0.12, 0.14, T.toon("leeslamp_kap", (0.98, 0.78, 0.25)), r2=0.06, seg=20, ol=0, cap=False)]
lamp_o = T.merge("Leeslamp", lamp, ol=0.006)
lamp_o.location = (-0.12, 0.08, 0.55)
T.group("Nachtkastje (geheel)", [ns_o, clock_o, lamp_o], loc=(-0.72, 1.62, 0))
phone = T.box("Telefoon", (-0.62, 1.52, 0.555), (0.075, 0.15, 0.01), P.m("zwart"), bevel=0.004, ol=0.003)
if DAG2:
    from lib import huis as HU  # noqa: E402
    HU.waterglas("Glas_water", (-0.92, 1.47, 0.55), vol=0.8)
if NIGHT and not BRO:
    T.box("Telefoon_scherm", (-0.62, 1.52, 0.566), (0.066, 0.14, 0.002), T.glow("telefoonscherm", (0.45, 0.65, 1.0), 6), bevel=0, ol=0)
    T.point_light("Telefoon_gloed", (-0.62, 1.4, 0.75), color=(0.35, 0.55, 1.0), energy=25, radius=0.2)

# ---------------------------------------------------------------------------
# Bureau met laptop, schoolboeken, stoel met hoodie
# ---------------------------------------------------------------------------
T.use_collection(T.collection("Bureau"))
DX, DY = 1.76, 0.25
I.table("Bureau", (DX, DY, 0), size=(1.35, 0.62, 0.75), color=(0.92, 0.90, 0.86), rot=90)
if BRO:
    # origami op het bureau: papier, vier kraanvogels en de eerste, mislukte ('een zielige duif')
    from lib import huis as HU  # noqa: E402
    HU.papierstapels("Origamipapier", (DX + 0.1, DY - 0.2, 0.75), n=3)
    for k, (x, y, r) in enumerate(((0.12, 0.3, -80), (0.22, 0.42, -110), (0.05, 0.48, -60), (0.18, 0.18, -95))):
        HU.kraanvogel(f"Kraanvogel_{k + 1}", (DX + x, DY + y, 0.75), (k * 3) % 8, rot=(0, 0, r))
    HU.kraanvogel("Kraanvogel_zielige_duif", (DX - 0.12, DY + 0.12, 0.75), 5, rot=(0, 0, -150), droevig=True)
    dl = [T.cyl("Bureaulamp_voet", (0, 0, 0), 0.07, 0.02, T.toon("bureaulamp", (0.95, 0.35, 0.15)), seg=16, ol=0),
          T.cyl("Bureaulamp_arm", (0, 0, 0.02), 0.01, 0.38, T.toon("bureaulamp", (0.95, 0.35, 0.15)), rot=(0, -20, 0), seg=8, ol=0),
          T.cyl("Bureaulamp_kap", (-0.1, 0, 0.32), 0.08, 0.1, T.toon("bureaulamp", (0.95, 0.35, 0.15)), r2=0.03, rot=(0, 160, 0), seg=16, ol=0, cap=False)]
    T.merge("Bureaulamp", dl, ol=0.005).location = (DX + 0.2, DY - 0.5, 0.75)
    T.point_light("Bureaulamp_licht", (DX + 0.1, DY - 0.45, 1.0), color=(1.0, 0.72, 0.42), energy=35, radius=0.06)
else:
    lap = [T.box("Laptop_onder", (0, 0, 0), (0.34, 0.24, 0.018), T.toon("laptop", (0.72, 0.74, 0.78)), bevel=0.006, ol=0),
           T.box("Laptop_scherm", (0, 0.12, 0.0), (0.34, 0.012, 0.23), T.toon("laptop", (0.72, 0.74, 0.78)), rot=(-15, 0, 0), bevel=0.006, ol=0)]
    lap_o = T.merge("Laptop", lap, ol=0.005)
    lap_o.location = (DX + 0.05, DY + 0.05, 0.75)
    lap_o.rotation_euler.z = math.radians(-90)
    scr = T.box("Laptop_beeld", (0, 0.112, 0.012), (0.31, 0.003, 0.2), T.glow("laptopscherm", (0.55, 0.75, 1.0), 2.0) if NIGHT else T.toon("laptopbeeld", (0.20, 0.35, 0.60)), rot=(-15, 0, 0), bevel=0, ol=0)
    scr.parent = lap_o
    I.books("Schoolboeken_stapel", (DX + 0.02, DY - 0.42, 0.75), n=5, rot=8, seed=1)
    I.books("Schoolboek_open", (DX - 0.05, DY + 0.5, 0.75), n=1, rot=-20, seed=3)
T.cyl("Pennenbak", (DX + 0.15, DY + 0.45, 0.75), 0.04, 0.1, T.toon("pennenbak", (0.15, 0.6, 0.35)), seg=12, ol=0.005)
chair = I.chair("Bureaustoel", (DX - 0.62, DY - 0.05, 0), rot=-90, color=(0.18, 0.20, 0.26), office=True)
HOOD = T.toon("pyjama_dino", (0.30, 0.70, 0.35)) if BRO else T.toon("hoodie_oranje", (0.88, 0.30, 0.05))
hood = [T.box("Hoodie_rug", (0, 0.03, 0.62), (0.5, 0.06, 0.42), HOOD, bevel=0.03, ol=0),
        T.box("Hoodie_over", (0, -0.03, 0.96), (0.52, 0.16, 0.08), HOOD, bevel=0.04, ol=0),
        T.box("Hoodie_mouw_l", (-0.27, 0.0, 0.52), (0.1, 0.12, 0.48), HOOD, rot=(0, 8, 0), bevel=0.04, ol=0),
        T.box("Hoodie_mouw_r", (0.27, 0.0, 0.52), (0.1, 0.12, 0.48), HOOD, rot=(0, -8, 0), bevel=0.04, ol=0),
        T.sphere("Hoodie_capuchon", (0, -0.1, 1.0), 0.14, HOOD, scale=(1.2, 0.9, 0.6), seg=14, ol=0)]
hood_o = T.merge("Hoodie", hood, ol=0.008)
hood_o.parent = chair
hood_o.location = (0, 0.22, 0)

# wandplank met boeken en globe boven het bureau
shelf = T.box("Wandplank", (W / 2 - 0.13, DY, 1.55), (0.24, 1.1, 0.03), T.toon("plank", (0.95, 0.93, 0.9)), bevel=0.005, ol=0.006)
I.books("Plankboeken", (W / 2 - 0.13, DY - 0.45, 1.58), n=9, rot=90, flat=False, seed=2)
T.sphere("Globe", (W / 2 - 0.15, DY + 0.38, 1.72), 0.11, T.toon("globe", (0.25, 0.55, 0.9)), seg=16, ol=0.005)
T.cyl("Globe_voet", (W / 2 - 0.15, DY + 0.38, 1.58), 0.05, 0.04, P.m("zwart"), seg=10, ol=0.004)

# ---------------------------------------------------------------------------
# Ruimteposter, commode met plant, sneakers
# ---------------------------------------------------------------------------
T.use_collection(T.collection("Decoratie"))
pz, py = 1.6, 0.85
import random  # noqa: E402
rnd = random.Random(7)
if BRO:
    # dinoposter: groene brontosaurus op geel
    DG = T.toon("poster_dino", (0.20, 0.62, 0.25))
    poster = [T.box("Poster_vlak", (0, 0, 0), (0.012, 0.62, 0.86), T.toon("poster_dino_achter", (0.98, 0.80, 0.25)), bevel=0, base=False, ol=0),
              T.sphere("Dino_lijf", (0.012, 0.02, -0.08), 0.16, DG, scale=(0.05, 1.2, 0.7), seg=20, ol=0),
              T.cyl("Dino_nek", (0.012, -0.12, -0.02), 0.04, 0.28, DG, rot=(30, 0, 0), seg=10, ol=0),
              T.sphere("Dino_kop", (0.012, -0.27, 0.24), 0.06, DG, scale=(0.05, 1.3, 0.9), seg=12, ol=0),
              T.cyl("Dino_staart", (0.012, 0.18, -0.12), 0.05, 0.25, DG, r2=0.005, rot=(-75, 0, 0), seg=10, ol=0)]
    for k, y in enumerate((-0.1, -0.02, 0.08, 0.16)):
        poster.append(T.cyl(f"Dino_poot{k}", (0.012, y, -0.27), 0.028, 0.14, DG, seg=8, ol=0))
    pst = T.merge("Dinoposter", poster, ol=0.004)
    T.text("Poster_tekst", "ROAR!", (0.02, 0, -0.4), 0.09, T.toon("poster_rood", (0.85, 0.12, 0.1)), rot=(90, 0, 90), extrude=0.002).parent = pst
else:
    poster = [T.box("Poster_vlak", (0, 0, 0), (0.012, 0.62, 0.86), T.toon("poster_ruimte", (0.05, 0.06, 0.20)), bevel=0, base=False, ol=0),
              T.sphere("Poster_planeet", (0.012, 0.05, 0.05), 0.17, T.toon("poster_planeet", (0.95, 0.55, 0.20)), scale=(0.05, 1, 1), seg=20, ol=0),
              T.torus("Poster_ring", (0.016, 0.05, 0.05), 0.26, 0.012, T.toon("poster_ring", (0.98, 0.85, 0.5)), rot=(0, 90, 0), seg=40, seg2=6, ol=0)]
    for k in range(18):
        poster.append(T.sphere(f"Poster_ster{k}", (0.012, rnd.uniform(-0.28, 0.28), rnd.uniform(-0.4, 0.4)), 0.008, P.m("wit"), scale=(0.3, 1, 1), seg=6, ol=0))
    pst = T.merge("Ruimteposter", poster, ol=0.004)
    T.text("Poster_tekst", "SPACE", (0.02, 0, -0.38), 0.09, P.m("wit"), rot=(90, 0, 90), extrude=0.002).parent = pst
pst.location = (-W / 2 + 0.01, py, pz)  # tegen de linkerwand, kijkt de kamer in (+x)

com = [T.box("Commode_body", (0, 0, 0), (0.5, 0.95, 0.85), T.toon("commode", (0.95, 0.85, 0.62)), bevel=0.02, ol=0)]
for k in range(3):
    com.append(T.box(f"Commode_la{k}", (0.255, 0, 0.1 + k * 0.25), (0.01, 0.85, 0.2), T.toon("commode_la", (0.9, 0.78, 0.52)), bevel=0.005, ol=0))
    com.append(T.sphere(f"Commode_knop{k}", (0.27, 0, 0.2 + k * 0.25), 0.02, P.m("metaal"), seg=8, ol=0))
T.merge("Commode", com, ol=0.01).location = (-W / 2 + 0.27, -1.2, 0)
T.cyl("Plantpot", (-W / 2 + 0.27, -1.0, 0.85), 0.09, 0.16, T.toon("pot", (0.80, 0.40, 0.25)), r2=0.07, seg=14, ol=0.005)
for k in range(5):
    a = k * 72
    T.sphere(f"Plantblad{k}", (-W / 2 + 0.27 + 0.07 * math.cos(math.radians(a)), -1.0 + 0.07 * math.sin(math.radians(a)), 1.08), 0.08, P.m("boomblad2"), scale=(0.6, 0.6, 1.4), seg=10, ol=0.004, rot=(20 * math.cos(math.radians(a)), 20 * math.sin(math.radians(a)), 0))
T.box("Lijstje", (-W / 2 + 0.3, -1.45, 0.85), (0.04, 0.16, 0.2), T.toon("lijstje", (0.25, 0.25, 0.3)), rot=(0, -8, 0), bevel=0.005, ol=0.004)


def sneaker(name, loc, rot):
    s = [T.box(name + "_zool", (0, 0, 0), (0.29, 0.11, 0.035), P.m("wit"), bevel=0.015, ol=0),
         T.box(name + "_body", (-0.03, 0, 0.03), (0.22, 0.1, 0.07), T.toon("sneaker_rood", (0.85, 0.12, 0.12)), bevel=0.03, ol=0),
         T.box(name + "_hiel", (-0.1, 0, 0.03), (0.08, 0.1, 0.11), T.toon("sneaker_rood", (0.85, 0.12, 0.12)), bevel=0.03, ol=0),
         T.box(name + "_neus", (0.1, 0, 0.03), (0.08, 0.1, 0.04), P.m("wit"), bevel=0.02, ol=0)]
    o = T.merge(name, s, ol=0.005)
    o.location = loc
    o.rotation_euler.z = math.radians(rot)
    return o


sneaker("Sneaker_links", (-0.75, -0.45, 0), 30)
sneaker("Sneaker_rechts", (-0.55, -0.62, 0), -70)

# ---------------------------------------------------------------------------
# Buiten: tuin, boom en buurhuis (zichtbaar door het raam; kamer is op de 1e verdieping)
# ---------------------------------------------------------------------------
T.use_collection(T.collection("Buiten"))
P.ground("Tuin", (200, 200), (0.24, 0.50, 0.18), z=-3.0)
P.tree("Boom_tuin", (-3.0, 7.0, -3.0), h=8.5, r=2.4, seed=2)
P.tree("Boom_tuin2", (-4.5, 11, -3.0), h=7.5, r=2.6, seed=5)
T.box("Buurhuis", (1.0, 15, -3.0), (9, 7, 6.2), T.toon("baksteen", (0.70, 0.36, 0.25)), bevel=0.05, ol=0.03)
roof = T.mesh_from("Buurhuis_dak", [(-4.8, -3.8, 0), (4.8, -3.8, 0), (4.8, 3.8, 0), (-4.8, 3.8, 0), (-4.8, 0, 3), (4.8, 0, 3)],
                   [(0, 1, 5, 4), (3, 2, 5, 4)[::-1], (0, 4, 3), (1, 2, 5)], T.toon("dakpan", (0.35, 0.18, 0.15)), ol=0.03)
roof.location = (1.0, 15, 3.2)
for k, x in enumerate((-2.0, 1.0, 4.0)):
    T.box(f"Buurhuis_raam{k}", (x, 11.48, 0.3), (1.0, 0.05, 1.2), T.glow("raam_buur", (1.0, 0.8, 0.45), 2) if NIGHT else T.toon("raam_buiten", (0.55, 0.72, 0.85)), bevel=0, ol=0.01)
P.hedge("Schutting", (0, 4.5, -3.0), (12, 0.12, 1.8), color="hout")

# ---------------------------------------------------------------------------
# Licht
# ---------------------------------------------------------------------------
T.use_collection(None)
if BRO:
    T.area_light("Maanlicht_raam", (0.9, 2.2, 1.6), (0.0, 0.0, 0.3), size=(1.4, 1.2), color=(0.45, 0.55, 1.0), energy=10)
    T.point_light("Plafondlamp_licht", (0, 0, H - 0.9), color=(1.0, 0.8, 0.55), energy=60, radius=0.1)
elif NIGHT:
    T.area_light("Maanlicht_raam", (0.9, 2.2, 1.6), (0.0, 0.0, 0.3), size=(1.4, 1.2), color=(0.45, 0.55, 1.0), energy=20)
else:
    T.area_light("Ochtendlicht_raam", (0.9, 1.6, 1.6), (-0.6, -0.5, 0.5), size=(1.4, 1.2), color=(1.0, 0.75, 0.45), energy=50)
    T.area_light("Vullicht", (0.5, -3.0, 2.2), (0, 0.5, 1.0), size=(3, 2), color=(0.75, 0.80, 1.0), energy=40)

if BRO:
    T.character((-0.35, -1.25, 0), rot_z=10)
elif DAG2:
    T.character((-0.2, -1.0, 0), rot_z=-30)
else:
    T.character((0.35, -0.55, 0), rot_z=-15)

cams = [
    T.camera("CAM_01_wide_kamer", (0.9, -3.3, 1.55), (-0.6, 0.6, 0.85), lens=20),
    T.camera("CAM_02_bed", (0.2, -0.9, 1.15), (-1.45, 0.95, 0.75), lens=26),
    T.camera("CAM_03_bureau", (1.0, -1.35, 1.4), (1.8, 0.35, 0.95), lens=24),
    T.camera("CAM_04_naar_raam", (-1.0, -1.4, 1.3), (0.9, 1.9, 1.5), lens=24),
]
if BRO:
    cams.append(T.camera("CAM_05_origami_bureau", (DX - 0.45, DY + 0.95, 1.3), (DX + 0.1, DY + 0.2, 0.78), lens=30))
if DAG2:
    cams.append(T.camera("CAM_05_wekker_glas", (-0.55, 0.85, 0.85), (-0.75, 1.55, 0.6), lens=40))
blend, renders = T.finish(OUT, ("kamer_broertje" if BRO else "slaapkamer_" + MOOD), cams)
print("KLAAR", blend, renders)
