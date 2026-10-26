"""S16a · Dag 15 · voor het huis: drie zwarte auto's. 'Don't worry. We just want to run a few tests.'

    blender -b -P anim/scenes/s16a_suvs.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from scene import *  # noqa: E402,F401

S = Scene("s16a", "straat", "suvs")

STEP2 = V(-1.4, 12.62, 0.30)
SCI_AT = V(-1.4, 11.25, 0.0)
mama = S.actor("mama", STEP2, 0, energy=1.0)
held = S.actor("hoofdpersonage", V(-0.82, 12.78, 0.30), -18)
sci = S.actor("wetenschapper", SCI_AT, 180, energy=1.1)
agents = [S.actor("officier", V(x, y, 0.12), heading((x, y), (-1.4, 12.6)), energy=0.6, label=f"agent_{k}")
          for k, (x, y) in enumerate(((-0.4, 5.6), (1.3, 5.4)))]

# ---------------------------------------------------------------- tijdlijn
S.hud(15, "32,768x STRONGER", t0=0.4)
S.music("drone", 0.0, 60, vol=0.28, fade_in=0.8, fade_out=0.6)
S.ambience("sfx_straat_sfeer", 0.0, 60, vol=0.08)
l1 = S.say("S16-01", gap=0.6)
CARS = l1[0] + 1.7
l2 = S.say("S16-02", who=sci, gap=0.5, gain=1.15)
S.wait(1.0)
END = S.t
S.sfx("sfx_suvs", 0.0, 0.3)

# ---------------------------------------------------------------- acteren
S.beat(mama, 0.0, "staan", face="nerveus", face_amt=0.6, at=S.head(sci, 0))
S.beat(mama, l2[0] + 0.5, "armen_over", amount=0.6, face="twijfel", face_amt=0.8, at=S.head(sci, 0))
S.hold(mama, END)
S.beat(held, 0.0, "staan", face="nerveus", face_amt=0.7, at=V(0.5, 3.2, 1.0))
S.beat(held, l2[0] + 0.3, "staan", face="nerveus", face_amt=0.8, at=S.head(sci, 0), body={"chest": (0, 0, 8)})
S.hold(held, END)
S.beat(sci, 0.0, "staan", face="blij", face_amt=0.6, at=S.head(mama, 0), arms=HOLD_FRONT_L)
S.beat(sci, l2[0] + 0.1, "handen_zij", amount=0.4, face="lach", face_amt=0.6, at=S.head(mama, 0))
S.beat(sci, l2[0] + 1.4, "staan", face="blij", face_amt=0.8, at=S.head(held, 0), arms=HOLD_FRONT_L)
S.hold(sci, END)
for a in agents:
    S.beat(a, 0.0, "armen_over", face="neutraal", face_amt=0.8, at=S.head(held, 0))
    S.hold(a, END)

# ---------------------------------------------------------------- camera
S.cam(0.0, ((1.2, 12.5, 4.0), (1.0, 2.5, 0.8), 26), ((1.0, 12.4, 3.9), (0.6, 2.8, 0.9), 30))
S.cam(CARS + 0.6, ((-14.0, -2.0, 2.0), (2.0, 6.0, 1.6), 26), ((-13.0, -1.6, 2.0), (1.0, 6.5, 1.6), 28))
S.cam(l2[0] - 0.2, ((1.4, 10.8, 1.5), (-1.25, 12.0, 1.35), 30))
S.cam(l2[0] + 1.0, ((-0.4, 12.35, 1.55), S.head(sci, 0) + V(0, 0, -0.1), 34), ((-0.42, 12.3, 1.55), S.head(sci, 0) + V(0, 0, -0.1), 38))

S.finish(length=END)
