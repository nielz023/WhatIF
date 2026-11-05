"""Sets (video 4, Never Die): de ruimte tot het einde van alles.

Varianten:
    sterren     scène 1e-1f, 20a-20d: sterrenhemel met sterrenstelsels; duizenden sterren in één object die je
                één voor één kunt uitzetten (materiaal "Sterrenveld_mat", node "Sterren uit" 0 -> 1), plus het
                laatste rode sterretje "Laatste_ster" (materiaal "Laatste_ster_gloed", Emission Strength -> 0).
                Sterrenstelsels "Stelsel_N" kun je laten wegdrijven (location keyframen).
    aarde       scène 1d: hij zweeft door de ruimte zonder pak, de aarde klein achter hem.
    rode_reus   scène 19a2, 19g: de rode reus vult de lucht, de aarde als klein zwart bolletje ervoor; daarna
                zweeft hij in de ruimte, achter hem een rode bol en geen aarde meer (Aarde_silhouet verbergen).
    zwarte_gaten scène 20d2: in het zwart alleen zwarte gaten als dunne gloeiende ringen (materialen
                "Zwart_gat_N_ring", Emission Strength -> 0 = verdampt).
    donker      scène 20e-22c: totaal zwart; een heel zwakke blauwe rand op zijn silhouet (lamp "Blauwe_rand"),
                opa's horloge met gloeiende wijzers in zijn handen (materiaal "Zakhorloge_lume"), en heel ver weg
                één warm lichtpuntje dat op de tik aan en uit gaat (materiaal "Lichtpuntje_gloed").

Gebruik:
    python3 sets/build_ruimte_nd.py <variant> [uitvoermap]
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402
from lib import toon as T  # noqa: E402
from lib import stad as S  # noqa: E402
from lib import nooitdood as ND  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
VAR = args[0] if args else "sterren"
OUT = args[1] if len(args) > 1 else f"/mnt/project-files/videos/nooit-dood/sets/03_ruimte_{VAR}"
rnd = random.Random(100)

ZWART = dict(sky_top=(0.0, 0.0, 0.0), sky_horizon=(0.0, 0.0, 0.0), ground_glow=(0.0, 0.0, 0.0),
             sun_color=(1.0, 0.96, 0.9), sun_strength=0.0, sun_rot=(60, 0, 30), ambient=(0.004, 0.005, 0.008),
             shadow_tint=(0.2, 0.2, 0.3), lit_tint=(1, 1, 1), fog_color=(0, 0, 0), fog_start=1e5, fog_end=1e6, fog_max=0.0,
             sun_disc=None, bloom=0.9, exposure=-0.2)
mood = dict(ZWART)
if VAR == "aarde":
    mood.update(sun_strength=1.3, sun_rot=(60, 0, -120), ambient=(0.01, 0.012, 0.02))
elif VAR == "rode_reus":
    mood.update(sun_strength=1.6, sun_color=(1.0, 0.32, 0.12), sun_rot=(90, 0, 180), ambient=(0.02, 0.005, 0.003), bloom=1.2)
elif VAR == "sterren":
    mood.update(ambient=(0.01, 0.012, 0.02))
T.new_scene("Ruimte_" + VAR, mood, samples=32)

HELD = (0, 0, 0)    # hij zweeft rond de oorsprong
T.use_collection(T.collection("Ruimte"))
if VAR in ("sterren", "aarde", "rode_reus"):
    ND.sterrenveld("Sterrenveld", n=5000 if VAR == "sterren" else 3000, radius=1400)
if VAR == "sterren":
    for k in range(7):
        a = rnd.uniform(0, 2 * math.pi)
        e = rnd.uniform(-0.3, 0.6)
        d = Vector((math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), math.sin(e)))
        ND.sterrenstelsel(f"Stelsel_{k}", tuple(d * rnd.uniform(700, 1100)), r=rnd.uniform(40, 110),
                          kleur=[(0.85, 0.75, 1.0), (1.0, 0.85, 0.7), (0.7, 0.85, 1.0)][k % 3], seed=k,
                          rot=(rnd.uniform(0, 90), rnd.uniform(0, 90), rnd.uniform(0, 90)))
    # het laatste rode sterretje, net boven en voor hem (1f, 20c)
    ls = T.sphere("Laatste_ster", (0.6, -14, 3.2), 0.07, ND.pbr("Laatste_ster_gloed", (1.0, 0.25, 0.12), emit=(1.0, 0.25, 0.1),
                                                               strength=60.0), seg=16, ol=0)
    ls.visible_shadow = False
    T.point_light("Laatste_ster_licht", (0.6, -14, 3.2), color=(1.0, 0.28, 0.12), energy=900, radius=0.05)
elif VAR == "aarde":
    aarde = T.sphere("Aarde", (60, 260, -40), 45, T.toon("water_oceaan_aarde", (0.03, 0.18, 0.62)), seg=64, ol=0)
    # continenten als groene/bruine vlekken op de bol
    cont = []
    for k in range(18):
        a, e = rnd.uniform(0, 6.28), rnd.uniform(-1.2, 1.2)
        n = Vector((math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), math.sin(e)))
        cont.append(T.sphere(f"Continent_{k}", tuple(Vector((60, 260, -40)) + n * 44.3), rnd.uniform(6, 14),
                             T.toon("gras_continent" if k % 3 else "zand_continent", (0.20, 0.45, 0.16) if k % 3 else (0.62, 0.50, 0.30)),
                             scale=(1, 1, 0.12), seg=16, ol=0, rot=(0, 0, 0)))
        cont[-1].rotation_euler = n.to_track_quat("Z", "Y").to_euler()
    T.merge("Aarde_continenten", cont, ol=0)
    wolk = T.sphere("Aarde_wolken", (60, 260, -40), 45.8, ND.pbr("wolken_aarde", (1, 1, 1), rough=0.9, alpha=0.12), seg=64, ol=0)
    atm = T.sphere("Aarde_atmosfeer", (60, 260, -40), 47.5, ND.pbr("atmosfeer_aarde", (0.3, 0.6, 1.0), emit=(0.3, 0.6, 1.0),
                                                                  strength=0.35, alpha=0.06), seg=64, ol=0)
    atm.visible_shadow = False
elif VAR == "rode_reus":
    zon = T.sphere("Rode_reus", (0, 1000, 0), 440,   # binnen het sterrenveld (r 1400), zelfde schijngrootte
                     ND.pbr("Rode_reus_gloed", (1.0, 0.18, 0.04), emit=(1.0, 0.16, 0.03),
                                                          strength=1.6), seg=96, ol=0)
    zon.visible_shadow = False
    T.sphere("Rode_reus_corona", (0, 1015, 0), 490, ND.pbr("Rode_reus_corona", (1.0, 0.35, 0.1), emit=(1.0, 0.25, 0.05),
                                                            strength=0.6, alpha=0.12), seg=64, ol=0).visible_shadow = False
    T.sphere("Aarde_silhouet", (-6, 260, 4), 7.0, T.toon("aarde_verkoold", (0.02, 0.015, 0.012)), seg=48, ol=0)
elif VAR == "zwarte_gaten":
    for k in range(5):
        a = rnd.uniform(-1.2, 1.2)
        ND.zwart_gat(f"Zwart_gat_{k}", (math.sin(a) * rnd.uniform(80, 200), rnd.uniform(150, 400), rnd.uniform(-40, 80)),
                     r=rnd.uniform(4, 12), rot=(rnd.uniform(50, 80), rnd.uniform(-20, 20), rnd.uniform(0, 90)), gloed=10.0)
elif VAR == "donker":
    lp = T.sphere("Lichtpuntje", (-160, 420, 18), 0.6, ND.pbr("Lichtpuntje_gloed", (1.0, 0.75, 0.4), emit=(1.0, 0.72, 0.38),
                                                             strength=40.0), seg=16, ol=0)
    lp.visible_shadow = False
    lp["uitleg"] = "Emission Strength op de tik keyframen (0 / 40); location dichterbij = het komt dichterbij (21i2)"
    # opa's horloge voor zijn borst, open, met gloeiende wijzers
    ND.zakhorloge("Zakhorloge", (0.12, -0.32, 1.0), rot=(70, 0, 10), open_=1.0, lume=3.0, ketting=True)
    T.point_light("Horloge_gloed", (0.12, -0.36, 1.02), color=(0.75, 1.0, 0.6), energy=0.35, radius=0.02)

# hij, zwevend
T.use_collection(None)
held = T.character(HELD, rot_z=180 if VAR == "aarde" else 0)   # 0 = gezicht naar -Y (naar de camera)
if held:
    held.rotation_euler.x = math.radians(12)
if VAR == "donker" and held:
    held["held"] = False   # geen oranje/blauwe glans-randlichten: alleen de zwakke blauwe rand hieronder
if VAR == "donker":
    T.area_light("Blauwe_rand", (1.2, 1.4, 1.6), (0, 0, 1.2), size=(0.6, 0.6), color=(0.1, 0.3, 1.0), energy=6)
    rl = bpy.data.objects["Blauwe_rand"]
    rl.visible_camera = False

if VAR == "sterren":
    cams = [T.camera("CAM_20a_HEMEL", (0.35, 1.1, 1.1), (-2, -20, 9), lens=20),
            T.camera("CAM_1f_20c_CLOSE", (0.1, -2.3, 1.5), (0.0, 0.0, 1.4), lens=45)]
elif VAR == "aarde":
    cams = [T.camera("CAM_1d_WIJD", (-3.5, -6.5, 1.6), (6, 60, -6), lens=28)]
elif VAR == "rode_reus":
    cams = [T.camera("CAM_19a2_HOOG", (-12, -320, 60), (0, 1000, 0), lens=24),
            T.camera("CAM_19g_ZWEVEN", (2.5, -4.8, 1.8), (0, 0, 1.0), lens=28)]
elif VAR == "zwarte_gaten":
    cams = [T.camera("CAM_20d2_WIJD", (0, -6, 1.5), (0, 300, 10), lens=24)]
else:
    cams = [T.camera("CAM_21b_CLOSE", (0.2, -2.1, 1.3), (0.05, -0.2, 1.15), lens=40),
            T.camera("CAM_21h_WIJD", (1.5, -3.5, 1.6), (-160, 420, 18), lens=30)]
blend, renders = T.finish(OUT, "ruimte_" + VAR, cams)
print("KLAAR", blend, renders)
