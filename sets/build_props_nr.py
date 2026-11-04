"""Props van video 3 (No Rules) bij elkaar op één vloer, in de glans-look (overzicht en losse bibliotheek).

Alles komt uit lib/stad.py, zodat de animatie dezelfde functies in elke set kan gebruiken.
Gebruik:
    python3 sets/build_props_nr.py [uitvoermap]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402,F401
from lib import toon as T  # noqa: E402
from lib import props as P  # noqa: E402
from lib import stad as S  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
OUT = args[0] if args else "/mnt/project-files/videos/geen-regels/sets/00_props"

mood = dict(T.MOODS["binnen"])
mood.update(sky_top=(0.04, 0.07, 0.20), sky_horizon=(0.10, 0.18, 0.42), ambient=(0.30, 0.32, 0.42), sun_strength=0.9,
            sun_rot=(50, 0, 30), fog_max=0.0, bloom=0.4)
T.new_scene("Props_no_rules", mood, samples=48)
T.use_collection(T.collection("Vloer"))
T.plane("Studiovloer", (0, 3, 0), (60, 40), T.toon("studio_vloer_blauw", (0.12, 0.16, 0.32)))

T.use_collection(T.collection("Props"))
# rij 1 (voor): kleine props
S.pillendoosje("Pillendoosje_opa", (-2.4, -1.0, 0.0), rot_z=10, open_=("SAT",))
S.house_rules("HOUSE_RULES", (-1.5, -1.0, 0.31), rot=(0, 0, 0))
S.house_rules("HOUSE_RULES_vergeeld", (-1.15, -1.0, 0.31), rot=(0, 0, 0), extra="5. EVERYONE GETS A VOTE.", yellowed=True)
S.kroon("Kroon_karton", (-0.45, -1.0, 0.0))
S.zaklamp("Zaklamp_agent", (0.25, -1.0, 0.03), rot=(0, 90, 20), on=True)
S.batterijen("Batterijen", (0.8, -1.0, 0.0), n=6)
S.medicijndoos("Medicijndoos", (1.3, -1.0, 0.0), rot_z=-10)
S.kaars("Kaars", (1.7, -1.0, 0.0), lit=True)
S.stripboeken("Stripboeken", (2.2, -1.0, 0.0), n=6)
S.jerrycan_("Jerrycan_water", (2.9, -1.0, 0.0), rot_z=-20)
# rij 2: borden, fietsen, kar
S.sign("Bord_KEEP_OFF_THE_GRASS", ["KEEP OFF", "THE GRASS"], (-3.6, 1.0, 0), rot_z=10, w=0.8, h=0.45)
S.fiets2("Fiets_vriend_rood", (-1.9, 1.2, 0), rot=-5, color=(0.85, 0.12, 0.10), sticker=True)
S.fiets2("Fiets_held_lamp_jerrycan", (0.3, 1.2, 0), rot=-5, color=(0.15, 0.35, 0.75), lamp_on=True, jerrycan=True)
S.winkelkar("Winkelkar", (2.4, 1.2, 0), rot=-30)
S.sign("Bord_NO_SWIMMING", ["NO SWIMMING", "BEYOND THE FLAGS"], (3.7, 1.0, 0), rot_z=-10, w=1.5, h=0.7, bg=(0.88, 0.12, 0.10), post_h=1.3)
# rij 3: grote props
S.slagboom("Slagboom", (-4.2, 4.0, 0), rot_z=0)
S.vuurkorf("Vuurkorf", (-0.9, 4.0, 0), lit=True)
S.tankstation_bord("Prijsbord_tankstation", (0.9, 4.2, 0), price="1.89")
S.regelbord("Regelbord_klein", (3.4, 4.4, 0), 0, w=2.4, h=1.6, title="OUR RULES", size=0.13,
            rules=["1. NOBODY GOES HUNGRY.", "2. SHARE THE WATER.", "3. HELP YOUR NEIGHBOUR."])
S.troon("Troon_winkelkarren", (6.2, 4.4, 0), rot_z=-20)

T.use_collection(None)
T.character((-5.6, 1.6, 0), rot_z=20)
T.area_light("Studio_key", (-4, -6, 6), (0, 2, 0.5), size=(4, 4), color=(1.0, 0.88, 0.72), energy=2500)
T.area_light("Studio_rim", (6, 9, 4), (0, 2, 0.5), size=(4, 4), color=(0.5, 0.65, 1.0), energy=1500)
cams = [T.camera("CAM_01_props_overzicht", (0.6, -9.5, 4.2), (0.6, 2.0, 0.6), lens=30),
        T.camera("CAM_02_kleine_props", (0.2, -3.4, 0.9), (0.2, -1.0, 0.1), lens=35),
        T.camera("CAM_03_fietsen", (-0.8, -2.6, 1.0), (-0.8, 1.2, 0.6), lens=30)]
blend, renders = T.finish(OUT, "props_no_rules", cams)
print("KLAAR", blend, renders)
