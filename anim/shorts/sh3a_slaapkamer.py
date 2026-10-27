"""SH3a · What if you could see 1 year into the future? · slaapkamer (nacht): zijn ogen flitsen wit... en hij ziet
morgen.

    blender -b -P anim/shorts/sh3a_slaapkamer.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from short import *  # noqa: E402,F401

S = Short("sh3", "a", "slaapkamer", "nacht", lines=(1,))
l1 = S.L[1]
END = S.t1
BED = V(-1.52, 1.25, 0.6)
for n in ("Telefoon", "Telefoon_scherm", "Laptop"):
    o = S.obj(n)
    if o:
        o.hide_render = True
lap = S.obj("Laptop")
if lap:
    for o in lap.children_recursive:
        o.hide_render = True

held = S.actor("hoofdpersonage", BED, 0)
SIT, _ = sit(held, seat_top=0.0, lean=-8, spread=0.12)
FL = l1[0] + 0.9                                # de flits
eye_glow(held, [(0, 0), (FL - 0.05, 0), (FL + 0.1, 1), (FL + 1.2, 1), (FL + 1.8, 0.65), (END, 0.8)])
lamp = T.point_light("Oog_gloed", tuple(BED + V(0, -0.45, 1.05)), color=(0.8, 0.9, 1.0), energy=0, radius=0.05)
for t, e in ((0, 0), (FL - 0.05, 0), (FL + 0.1, 40), (FL + 1.2, 25), (END, 30)):
    lamp.data.energy = e
    lamp.data.keyframe_insert("energy", frame=F(t))

S.music_all("ruimte_koor", vol=0.2)
S.sfx("sfx_visioen", FL - 0.1, 0.55)
S.card("", FL, FL + 0.25, dim=0.85, bg=(1, 1, 1), fin=1, fout=5)
S.card("", END - 0.3, END, dim=1.0, bg=(1, 1, 1), fin=7, fout=0)
S.sfx("sfx_whoosh", END - 0.3, 0.3)

S.beat(held, 0.0, **SIT, pose="ontspannen", face="neutraal", look=(0, -0.2), mouth=0.0)
S.beat(held, FL - 0.2, **SIT, pose="ontspannen", face="neutraal", look=(0, 0), mouth=0.0, body={"head": (-4, 0, 0)})
S.beat(held, FL + 0.05, **SIT, pose="schrik", amount=0.8, face="geschrokken", face_amt=1.0, look=(0, 0), mouth=0.5,
       body={"head": (-12, 0, 0), "chest": (-6, 0, 0)})
S.beat(held, FL + 1.4, **SIT, pose="handen_hoofd", amount=0.8, face="verbaasd", face_amt=1.0, look=(0, 0), mouth=0.3)
S.beat(held, END - 0.6, **SIT, pose="ontspannen", face="verbaasd", face_amt=1.0, look=(0, 0.1), mouth=0.2)
S.hold(held, END)

S.cam(0.0, ((0.1, -1.0, 1.45), (-1.52, 1.1, 1.0), 26), ((-0.05, -0.8, 1.42), (-1.52, 1.1, 1.05), 28))
S.cam(FL - 0.1, S.shot(held, FL, "mcu", az=8, lens=32, h=-0.05), S.shot(held, END, "cu", az=4, lens=44, h=-0.05),
      shake=lambda t: 1.2 * max(0, 1 - (t - FL) / 0.6))

S.done()
