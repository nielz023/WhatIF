"""Branding voor het kanaal "Way Too Far": rendert het hoofdpersonage voor logo en banner.

Rendert twee losse figuren met een doorzichtige achtergrond (PNG met alfa):
- logo_held.png:   schouders en hoofd, geschrokken, handen aan zijn hoofd (vierkant)
- banner_held.png: hele figuur, geschrokken, kijkt omhoog naar wat er komt (staand)

    blender -b -P branding/render_branding.py -- [uitmap]

Daarna zet branding/compose_branding.py er tekst en achtergrond bij.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(REPO, "sets"))
sys.path.insert(0, os.path.join(REPO, "anim", "lib"))
import bpy  # noqa: E402
from lib import toon as T  # noqa: E402
import rig as R  # noqa: E402
import acting as A  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = os.path.abspath(argv[0] if argv else os.path.join(REPO, "out", "branding"))
os.makedirs(OUT, exist_ok=True)

mood = dict(T.MOODS["dag"])
mood.update(sun_rot=(50, 0, -30), ambient=(0.55, 0.55, 0.62))
sc = T.new_scene("Branding", mood, res=(1600, 1600), samples=64)
sc.render.film_transparent = True

held = R.load("hoofdpersonage", loc=(0, 0, 0), rot_z=0)
T.area_light("Randlicht", (1.6, 1.4, 2.4), (0, 0, 1.2), size=(1.5, 1.5), color=(1.0, 0.75, 0.45), energy=420)
T.area_light("Vullicht", (-2.0, -2.5, 1.6), (0, 0, 1.2), size=(2, 2), color=(0.8, 0.88, 1.0), energy=260)


def shoot(name, frame, cam_loc, target, lens, res):
    sc.frame_set(frame)
    cam = T.camera("Cam_" + name, cam_loc, target, lens=lens)
    sc.camera = cam
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = os.path.join(OUT, name + ".png")
    bpy.ops.render.render(write_still=True)
    print("RENDER", sc.render.filepath)


# frame 1: logo, handen aan het hoofd, wijd open ogen
A.pose(held, 1, "handen_hoofd", extra={"head": (-6, 0, 4)})
A.expr(held, 1, "geschrokken", look=(0.0, 0.1))
A.key_prop(held.rig, "mond_open", 0.75, 1)
A.key_prop(held.rig, "knipper", 0.0, 1)
# frame 10: banner, deinst terug en kijkt geschrokken naar de tekst rechts van hem
A.pose(held, 10, "schrik", extra={"spine": (-8, 0, 0), "head": (-4, 18, 0)})
A.expr(held, 10, "geschrokken", look=(0.5, 0.1))
A.key_prop(held.rig, "mond_open", 0.7, 10)
A.key_prop(held.rig, "knipper", 0.0, 10)

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "branding.blend"))

only = argv[1].split(",") if len(argv) > 1 else ("logo_held", "banner_held")
if "logo_held" in only:
    shoot("logo_held", 1, (0.35, -3.0, 1.30), (0, 0, 1.42), 80, (1600, 1600))
if "banner_held" in only:
    shoot("banner_held", 10, (1.0, -4.0, 1.0), (0, 0, 1.0), 62, (1200, 1600))
