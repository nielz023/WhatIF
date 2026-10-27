"""SH7b · teleport-kopieën · keuken: ineens staat hij in de keuken. Hij kan teleporteren!

    blender -b -P anim/shorts/sh7b_keuken.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from short import *  # noqa: E402,F401

S = Short("sh7", "b", "keuken", "ochtend", lines=(1,), t0=1.0, t1=5.8)
l1, l2 = S.L[1], S.L[2]
T0, END = S.t0, S.t1
for n in ("Krant", "Ontbijt_broertje"):
    o = S.obj(n)
    if o:
        o.hide_render = True
HP = V(1.1, 0.55, 0)
held = S.actor("hoofdpersonage", HP, 0)
tele_fx(S, HP, T0 + 0.02, sound=False)
S.counter("JUMPS: 1", T0 + 0.2, None, color=(0.6, 0.85, 1.0, 1))
S.beat(held, T0, "schrik", amount=0.8, face="geschrokken", face_amt=1.0, look=(0, 0), mouth=0.5)
S.beat(held, T0 + 0.9, "staan", face="verbaasd", face_amt=1.0, look=(-0.8, 0.2), mouth=0.3, body={"head": (0, 0, 35)})
S.beat(held, T0 + 1.8, "staan", face="verbaasd", face_amt=1.0, look=(0.8, 0.2), mouth=0.3, body={"head": (0, 0, -35)})
S.beat(held, l1[1] - 0.7, "handen_hoofd", face="verbaasd", face_amt=1.0, look=(0, 0), mouth=0.4)
S.beat(held, l2[0] + 0.3, "juichen", face="lach", face_amt=1.0, look=(0, 0.2), mouth=0.6)
S.beat(held, END - 0.5, "vuisten", face="grijns", face_amt=1.0, look=(0, 0), mouth=0.0)
show(held.rig, 0, END - 0.1)
tele_fx(S, HP, END - 0.1)
S.cam(T0, ((1.6, -1.7, 1.35), (1.05, 0.55, 1.05), 26), ((1.55, -1.55, 1.35), (1.05, 0.55, 1.1), 28))
S.cam(l1[1] - 0.9, S.shot(held, l1[1] - 0.6, "mcu", az=8, lens=32), S.shot(held, END, "mcu", az=4, lens=36))
S.done()
