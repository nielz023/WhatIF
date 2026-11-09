"""Set (video 3, No Rules): het strand met strandwacht, vlaggen en het bord NO SWIMMING BEYOND THE FLAGS.

Varianten (zelfde plekken, zodat 19d-19e het spiegelbeeld van 3c-3d is):
    middag   scène 3c-3d: vol strand, opa en oma op strandstoelen, strandwacht op zijn stoel.
    jaar5    scène 19d-19e: weer vol, maar met zonnepanelen op de strandtent, fietsenrekken
             op de boulevard en een handgeschilderd bord terug op dezelfde plek.
    leeg     reserve (dag 2-6): leeg strand, omgewaaide parasol, bord scheef.
    nacht    originele short OR7 (maan 2x dichterbij): leeg strand 's nachts, maanlicht vanaf zee, verlichte flats.

De zee ligt aan de -y kant, de boulevard aan de +y kant.

Gebruik:
    python3 sets/build_strand.py <variant> [uitvoermap]
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
VAR = args[0] if args else "middag"
OUT = args[1] if len(args) > 1 else "/mnt/project-files/videos/geen-regels/sets/03_strand"

mood = dict(T.MOODS["dag"])
mood.update(sun_rot=(40, 0, 160), sky_horizon=(0.62, 0.82, 1.0), lit_tint=(1.0, 0.97, 0.90), fog_start=90.0, fog_end=900.0,
                fog_max=0.35, exposure=-0.35)
if VAR == "leeg":
    mood = dict(T.MOODS["bewolkt"])
if VAR == "nacht":
    mood = dict(T.MOODS["nacht"])
    mood.update(sun_rot=(60, 0, 0), sun_strength=0.5, sun_color=(0.75, 0.82, 1.0), fog_start=60.0, fog_end=700.0, fog_max=0.5)
T.new_scene("Strand_" + VAR, mood, samples=32)
rnd = random.Random(19)

# ---------------------------------------------------------------------------
# Zand, zee, duinen, boulevard
# ---------------------------------------------------------------------------
T.use_collection(T.collection("Strand"))
zand = T.toon("zand_strand", (0.93, 0.78, 0.52))
nat = T.toon("zand_nat", (0.78, 0.66, 0.48))
P.ground("Zand", (500, 300), (0.93, 0.78, 0.52), z=-0.02)
T.plane("Natte_strook", (0, -21, -0.005), (500, 6), nat)
T.plane("Zee", (0, -150, 0.05), (600, 250), T.toon("water_zee", (0.04, 0.42, 0.68)))
T.plane("Branding", (0, -24.5, 0.06), (500, 1.4), T.toon("schuim_branding", (0.92, 0.96, 0.98)))
for i in range(6):  # golfjes
    T.box(f"Golf_{i}", (rnd.uniform(-60, 60), -30 - i * 8, 0.05), (rnd.uniform(8, 20), 0.6, 0.12),
          T.toon("schuim_branding", (0.92, 0.96, 0.98)), bevel=0.05, ol=0)
for i in range(14):  # duinen met helmgras
    x = -90 + i * 14
    T.sphere(f"Duin_{i}", (x, 34 + rnd.uniform(-2, 2), -2.5), 9.0, zand, scale=(1.0, 0.5, 0.45), seg=20, ol=0)
    for k in range(8):
        T.cyl(f"Helmgras_{i}_{k}", (x + rnd.uniform(-6, 6), 32 + rnd.uniform(-2, 2), rnd.uniform(0.6, 1.4)), 0.12, 0.6,
              T.toon("blad_helmgras", (0.55, 0.62, 0.32)), r2=0.0, seg=6, ol=0)
T.box("Boulevard", (0, 40, 0), (300, 7, 1.6), T.toon("stoep_boulevard", (0.75, 0.72, 0.68)), bevel=0.05, ol=0)
for i in range(8):
    S.building(f"Boulevardflat_{i}", (-70 + i * 20, 44, 0), w=17, d=10, floors=rnd.randint(4, 8),
               color=[(0.95, 0.92, 0.85), (0.70, 0.82, 0.90), (0.98, 0.85, 0.70)][i % 3], lit=0.5 if VAR == "nacht" else 0.0, seed=60 + i,
               glass_col=(0.45, 0.65, 0.85))
# strandtent
tent = T.toon("hout_strandtent", (0.78, 0.60, 0.40))
T.box("Strandtent", (-24, 14, 0), (10, 6, 3.2), tent, bevel=0.05, ol=0)
T.box("Strandtent_dak", (-24, 13.6, 3.2), (11, 7.2, 0.3), T.toon("dak_strandtent", (0.20, 0.45, 0.72)), bevel=0.04, ol=0)
T.box("Strandtent_terras", (-24, 9.0, 0), (12, 4.0, 0.25), tent, bevel=0.03, ol=0)
S.label("Strandtent_naam", "BEACH BAR", (-24, 10.95, 2.5), 0.6, (1, 1, 1), extrude=0.03)

# ---------------------------------------------------------------------------
# Strandwacht, vlaggen, het bord
# ---------------------------------------------------------------------------
T.use_collection(T.collection("Strandwacht"))
S.strandwachtstoel("Strandwachtstoel", (6, -8, 0), rot_z=0)
S.vlag("Vlag_links", (-6, -19.5, 0), color=(0.95, 0.85, 0.1))
S.vlag("Vlag_rechts", (18, -19.5, 0), color=(0.95, 0.85, 0.1))
leeg = VAR in ("leeg", "nacht")
txt = ["NO SWIMMING", "BEYOND THE FLAGS"]
bord = S.sign("Bord_NO_SWIMMING", txt, (1.0, -14.5, 0), rot_z=200, w=1.5, h=0.7, bg=(0.88, 0.12, 0.10) if VAR != "jaar5" else (0.95, 0.92, 0.80),
              fg=(1, 1, 1) if VAR != "jaar5" else (0.12, 0.25, 0.65), post_h=1.3, marker=(VAR == "jaar5"))
if leeg:
    bord.rotation_euler.y = math.radians(14)

# ---------------------------------------------------------------------------
# Badgasten (handdoeken, parasols, stoelen) + plek van opa en oma
# ---------------------------------------------------------------------------
T.use_collection(T.collection("Badgasten"))
cols = [(0.95, 0.35, 0.2), (0.2, 0.55, 0.95), (0.98, 0.8, 0.2), (0.4, 0.8, 0.5), (0.9, 0.4, 0.7), (0.95, 0.95, 0.95)]
pcol = [("rood", "wit"), ("blauw", "wit"), ("geel", "wit"), ("roze", "wit")]
n = 3 if leeg else 30
for i in range(n):
    x = rnd.uniform(-22, 26)
    y = rnd.uniform(-13, 7)
    if abs(x - 6) < 3.5 and abs(y + 8) < 3.5:
        continue
    if abs(x + 4) < 3 and abs(y + 2) < 3:
        continue
    S.handdoek(f"Handdoek_{i}", (x, y, 0.005), rot_z=rnd.uniform(-20, 20), color=cols[i % 6])
    if i % 2 == 0:
        S.parasol(f"Parasol_{i}", (x + 0.9, y + 0.6, 0), colors=pcol[i % 4], tilt=rnd.uniform(-10, 10))
if leeg:
    pr = S.parasol("Parasol_omgewaaid", (8, -3, 0.25), colors=("rood", "wit"))
    pr.rotation_euler = (math.radians(95), 0, math.radians(30))
# opa en oma (scène 3c/19e): twee strandstoelen, strandtas, krant
T.use_collection(T.collection("Opa en oma"))
S.strandstoel("Strandstoel_opa", (-4.6, -2.0, 0), rot_z=-5, color=(0.15, 0.50, 0.90))
S.strandstoel("Strandstoel_oma", (-3.4, -2.1, 0), rot_z=5, color=(0.95, 0.45, 0.55))
S.parasol("Parasol_opa_oma", (-4.0, -1.0, 0), colors=("blauw", "wit"), tilt=-6)
T.box("Strandtas", (-2.7, -1.7, 0), (0.45, 0.22, 0.35), T.toon("stof_strandtas", (0.95, 0.75, 0.30)), bevel=0.05, ol=0)
S.pillendoosje("Pillendoosje_opa", (-2.7, -1.7, 0.35), rot_z=10)
T.cyl("Zonnebrand_oma", (-3.08, -1.8, 0.0), 0.04, 0.17, T.toon("plastic_zonnebrand", (0.98, 0.55, 0.15)), seg=12, ol=0)
S.handdoek("Handdoek_opa_oma", (-4.0, -2.6, 0.005), rot_z=90, color=(0.2, 0.55, 0.95))

if VAR == "jaar5":
    T.use_collection(T.collection("Jaar 5"))
    for i in range(4):
        S.zonnepaneel(f"Zonnepaneel_strandtent_{i}", (-28 + i * 2.6, 15.0, 3.5), w=1.0, d=1.6, tilt=20, legs=False)
    for i in range(8):
        S.fiets2(f"Fiets_boulevard_{i}", (-12 + i * 0.9, 37.8, 1.6), rot=90, color=cols[i % 6])
    S.sign("Bord_BIKES_ONLY", ["BIKES ONLY"], (-16, 37.6, 1.6), rot_z=180, w=1.0, h=0.35, bg=(0.15, 0.45, 0.25), post_h=1.4)

T.use_collection(None)
T.character((1.8, -12.5, 0), rot_z=180)
cams = [
    T.camera("CAM_01_strand_wide", (-9, 7, 2.3), (3, -10, 1.2), lens=26),
    T.camera("CAM_02_strandwacht", (2.5, -18, 1.4), (6, -8, 2.4), lens=30),
    T.camera("CAM_03_opa_oma", (-4.0, -6.5, 1.0), (-4.0, -2.0, 0.7), lens=35),
    T.camera("CAM_04_pillendoosje", (-2.3, -2.3, 0.75), (-2.7, -1.7, 0.38), lens=50),
]
blend, renders = T.finish(OUT, "strand_" + VAR, cams)
print("KLAAR", blend, renders)
