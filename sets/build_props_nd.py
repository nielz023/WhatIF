"""Props (video 4, Never Die): overzicht in de glans-studio + close-ups van opa's zakhorloge.

Varianten:
    horloge   het zakhorloge in vier toestanden: dicht, open (gravure), gebarsten glas + gloeiende wijzers, met rijp
    overzicht alle andere props: horlogedoosje, gezinsfoto (nieuw / vergeeld / verbleekt), politiepenning, rolstoel,
              bloemen, snoepzak, peperbakje, kwallenbak, grazer, vliegende auto

Gebruik:
    python3 sets/build_props_nd.py <variant> [uitvoermap] [foto.png]
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402,F401
from lib import toon as T  # noqa: E402
from lib import nooitdood as ND  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
VAR = args[0] if args else "horloge"
OUT = args[1] if len(args) > 1 else "/mnt/project-files/videos/nooit-dood/sets/00_props"
FOTO = args[2] if len(args) > 2 else "/mnt/project-files/videos/nooit-dood/sets/00_props/gezinsfoto_14e_verjaardag.png"
if not os.path.exists(FOTO):
    FOTO = None

mood = dict(T.MOODS["binnen"], sky_top=(0.04, 0.06, 0.14), sky_horizon=(0.07, 0.10, 0.20), ground_glow=(0.05, 0.06, 0.1),
            ambient=(0.12, 0.14, 0.22), sun_strength=0.0, fog_max=0.0, bloom=0.6)
T.new_scene("Props_" + VAR, mood, samples=48)
T.use_collection(T.collection("Studio"))
T.plane("Studio_vloer", (0, 0, 0), (40, 40), T.toon("studio_vloer_nachtblauw", (0.06, 0.08, 0.16)))
T.area_light("Hoofdlicht", (-1.5, -2.5, 3.0), (0, 0, 0), size=(2, 2), color=(1.0, 0.90, 0.80), energy=420)
T.area_light("Randlicht_oranje", (2.5, 1.5, 1.2), (0, 0, 0.1), size=(1, 1), color=(1.0, 0.6, 0.24), energy=160)
T.area_light("Randlicht_blauw", (-2.5, 1.8, 1.0), (0, 0, 0.1), size=(1, 1), color=(0.24, 0.55, 1.0), energy=180)
T.use_collection(T.collection("Props"))

if VAR == "horloge":
    ND.zakhorloge("Zakhorloge_dicht", (-0.19, 0, 0.012), rot=(0, 0, 20), open_=0.0)
    ND.zakhorloge("Zakhorloge_open", (-0.05, 0, 0.012), rot=(0, 0, -10), open_=1.0, tijd=(10, 10, 32), gravure_gloed=0.0)
    ND.zakhorloge("Zakhorloge_gebarsten", (0.09, 0, 0.012), rot=(0, 0, 5), open_=1.0, barst=True, lume=2.5, tijd=(11, 58, 45))
    ND.zakhorloge("Zakhorloge_rijp", (0.23, 0, 0.012), rot=(0, 0, -20), open_=0.0, rijp=True, ketting=False)
    ND.horlogedoosje("Horlogedoosje", (-0.08, 0.17, 0), rot_z=-15, open_=1.0)
    cams = [T.camera("CAM_ALLE_VIER", (0.02, -0.46, 0.40), (0.02, 0.04, 0.0), lens=40),
            T.camera("CAM_GRAVURE", (-0.10, -0.04, 0.12), (-0.10, 0.005, 0.012), lens=55),
            T.camera("CAM_WIJZERPLAAT", (-0.05, -0.05, 0.12), (-0.05, 0.0, 0.01), lens=70),
            T.camera("CAM_GEBARSTEN", (0.09, -0.06, 0.12), (0.09, 0.0, 0.01), lens=70)]
else:
    ND.horlogedoosje("Horlogedoosje", (-1.6, 0.0, 0), rot_z=-15, open_=1.0)
    ND.zakhorloge("Zakhorloge_in_doosje", (-1.6, 0.0, 0.033), rot=(0, 0, -15), open_=0.0, ketting=False)
    ND.oude_foto("Gezinsfoto_nieuw", (-1.0, 0.0, 0.002), rot=(0, 0, 8), image=FOTO)
    ND.oude_foto("Gezinsfoto_vergeeld", (-0.8, 0.15, 0.002), rot=(0, 0, -6), image=FOTO, vergeling=0.55, kreuk=0.3)
    ND.oude_foto("Gezinsfoto_verbleekt", (-0.6, 0.0, 0.004), rot=(0, 0, 12), image=FOTO, vergeling=0.7, verbleking=0.85, kreuk=1.0)
    ND.politiepenning("Politiepenning", (-0.25, -0.05, 0.001), rot=(0, 0, 10))
    ND.rolstoel("Rolstoel", (0.6, 0.6, 0), rot_z=-30)
    ND.bloemen("Bloemen", (0.05, 0.3, 0), rot_z=40, seed=2)
    ND.snoepzak("Snoepzak", (-0.35, 0.35, 0), rot_z=10)
    ND.peperbakje("Peperbakje", (0.0, -0.25, 0), rot_z=-10)
    ND.kwallenbak("Kwallenbak", (-0.5, 0.75, 0), rot_z=10)
    ND.grazer("Grazer", (-2.8, 3.8, 0), rot_z=-150, schaal=0.45)
    ND.vliegende_auto("Vliegende_auto", (2.8, 4.6, 0.6), rot_z=-30)
    cams = [T.camera("CAM_OVERZICHT", (0.2, -3.6, 2.2), (0.2, 0.9, 0.2), lens=35),
            T.camera("CAM_FOTO_PENNING", (-0.65, -0.55, 0.55), (-0.6, 0.05, 0.0), lens=50),
            T.camera("CAM_KWAL", (-0.45, 0.25, 0.22), (-0.5, 0.75, 0.16), lens=50)]
blend, renders = T.finish(OUT, "props_" + VAR, cams)
print("KLAAR", blend, renders)
