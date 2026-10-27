"""SH2c · tijd stopt · badkamer, jaar 3: in de spiegel zie je dat jij ouder wordt (stoppelbaard). Niemand anders.

    blender -b -P anim/shorts/sh2c_badkamer.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from short import *  # noqa: E402,F401

S = Short("sh2", "c", "badkamer", "binnen", lines=(6,))
l6 = S.L[6]
T0, END = S.t0, S.t1

SX = -0.55
SPOT = V(SX + 0.02, 0.42, 0)
MIRROR = S.obj("Grote_spiegel")
held = S.actor("hoofdpersonage", SPOT, 180)

# stoppelbaard: puntjes op zijn kaak (stralen op het gezicht)
S.beat(held, 0.0, "staan", face="neutraal", look=(0, 0))


def jaw(u, v):
    if v > -0.05 or (u * u) / 0.09 + ((v + 0.05) ** 2) / 0.1 > 1:
        return False
    return not (abs(u) < 0.07 and v > -0.15)


pts = face_points(S, held, 0.0, (0, 1, 0), jaw, step=0.014)
beard = P.points_mesh("Stoppels", pts, 0.009, S.mat("stoppels", (0.18, 0.12, 0.08)), seg=6)
attach_keep(beard, held, "head", 0.0)
print("stoppels:", len(pts))

S.counter("YEAR 3", l6[0] + 0.05, None, sub="YOU: 3 YEARS OLDER")
S.card("", T0, END, dim=0.1, bg=(0.35, 0.5, 0.95), fin=0, fout=0)
S.ambience("sfx_binnen_sfeer", T0, END, vol=0.05)

HANDS = SPOT + V(0, 0.36, 1.02)
S.beat(held, T0, "staan", face="verdrietig", face_amt=0.4, look=(0, 0.1), mouth=0.0)
S.beat(held, l6[0] + 1.3, "staan", face="nerveus", face_amt=0.6, look=(0, 0), mouth=0.0, body={"head": (-4, 0, 0)})
S.reach(held, l6[0] + 1.6, "R", S.head(held, 0.0) + V(0.06, 0.3, -0.3))
S.reach(held, l6[0] + 2.4, "R", S.head(held, 0.0) + V(-0.04, 0.3, -0.3))
S.reach(held, l6[0] + 3.0, "R", None, 0.0)
S.beat(held, l6[0] + 3.0, "staan", face="verdrietig", face_amt=1.0, look=(0, -0.3), mouth=0.0, body={"head": (10, 0, 0)})
S.reach(held, l6[1] - 0.9, "L", HANDS + V(-0.2, 0, 0))
S.reach(held, l6[1] - 0.9, "R", HANDS + V(0.2, 0, 0))
S.beat(held, l6[1] - 0.6, "staan", face="verdrietig", face_amt=1.0, look=(0, -0.8), mouth=0.0,
       body={"head": (24, 0, 0), "chest": (12, 0, 0)})
S.hold(held, END)

# camera: van achter hem, dan 'door de spiegel' (spiegel even onzichtbaar voor de camera), dan weer achter
HC = S.head(held, 0.0)
MS = l6[0] + 0.8
for t, on in ((0, True), (MS, False), (l6[1] - 1.1, True)):
    MIRROR.visible_camera = on
    MIRROR.keyframe_insert("visible_camera", frame=F(t))
constant(MIRROR, "visible")
S.cam(T0, ((0.5, -1.0, 1.75), (SX, 1.1, 1.4), 24), ((0.4, -0.85, 1.72), (SX, 1.1, 1.4), 26))
S.cam(MS, ((SX + 0.06, 1.24, 1.5), HC + V(0, 0, -0.05), 30), ((SX + 0.05, 1.24, 1.48), HC + V(0, 0, -0.06), 36))
S.cam(l6[1] - 1.1, ((SX + 0.55, -0.35, 1.7), HC + V(0, 0.4, -0.25), 30), ((SX + 0.5, -0.3, 1.72), HC + V(0, 0.4, -0.3), 32))

S.done()
