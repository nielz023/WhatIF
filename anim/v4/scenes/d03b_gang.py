"""D03b · Over de gang op zijn sokken (script scène 3d2, 3e). Overloop, ochtend.
3d2 MEDIUM 4,6 s: hij glijdt grijnzend op zijn sokken over de gang naar de trap en slaat met zijn hand tegen de
    trappaal: kraak. Hij schudt zijn hand uit.  VO: "Because forever is a very, very long time to feel things."
3e  DETAIL 2,4 s: zijn hand, de rode plek op zijn knokkels.  VO: "Remember that."  SFX: tik.

    python3 anim/v4/scenes/d03b_gang.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v4 import *  # noqa: E402,F401,F403

S = Scene4("d03b", "overloop", "ochtend", exposure=0.25)
sh = S.cuts([4.6, 2.4])
END = sh[-1][1]
t_e = sh[1][0]

POST = V(-0.60, -0.76, 0.95)                         # bovenkant van de trappaal
START = V(2.2, -0.35, 0.0)
STOP = V(-0.15, -0.38, 0.0)
held = S.actor("hoofdpersonage_kind", START, -90)    # kijkt naar -x (de trap)
# aanloop: twee passen, dan glijden (voeten stil, lichaam schuin achterover, armen uit)
S.walk(held, 0.0, 0.8, [START, START + V(-0.9, 0, 0)], stride=0.5, arms=1.0)
S.beat(held, 0.4, "staan", face="lach", face_amt=0.9, feet="keep", at=POST + V(-2, 0, 0.3))
SLIDE = arms(arm("L", (0.95, 0.10, 0.10), (0.95, 0.20, 0.15)), arm("R", (0.95, 0.10, 0.10), (0.95, 0.20, 0.15)))
for t, p in ((0.8, START + V(-0.9, 0, 0)), (1.6, START + V(-1.75, 0, 0)), (2.25, STOP)):
    S.place(held, t, p, -90)
S.beat(held, 0.85, "staan", arms=SLIDE, face="lach", face_amt=1.0, crouch=(0.10, -8),
       feet=((0, 0.18, 0.0), (0, -0.12, 0.0)), at=POST + V(-2, 0, 0.3))
S.beat(held, 1.7, "staan", arms=SLIDE, face="grijns", face_amt=1.0, crouch=(0.12, -10),
       feet=((0, 0.20, 0.0), (0, -0.14, 0.0)), at=POST + V(-2, 0, 0.3))
# hij remt bij de paal: linkerhand klapt tegen de paal (paal ligt links van hem)
T_HIT = 2.3
S.beat(held, T_HIT - 0.1, "staan", face="grijns", face_amt=0.8, crouch=(0.08, 6), feet=((0, 0.06, 0), (0, -0.06, 0)),
       at=POST)
S.reach(held, 0.0, "L", None, 0.0)
S.reach(held, T_HIT - 0.25, "L", None, 0.0)
S.reach(held, T_HIT, "L", POST + V(0.06, 0.06, -0.12))
S.reach(held, T_HIT + 0.25, "L", POST + V(0.08, 0.10, -0.14))
S.reach(held, T_HIT + 0.45, "L", None, 0.0)
S.beat(held, T_HIT + 0.05, "staan", face="inspanning", face_amt=1.0, crouch=(0.06, 10), feet=((0, 0.06, 0), (0, -0.06, 0)),
       at=POST)
# hand uitschudden (voor zijn borst, nooit bij zijn hoofd)
SHAKE_A = arm("L", (0.30, 0.55, -0.75), (0.10, 0.85, 0.40))
SHAKE_B = arm("L", (0.35, 0.50, -0.75), (0.35, 0.80, 0.15))
for k, t in enumerate(frange(T_HIT + 0.5, t_e + 0.05, 0.13)):
    S.beat(held, t, "staan", arms=SHAKE_A if k % 2 else SHAKE_B, face="inspanning" if k < 5 else "twijfel",
           face_amt=0.8, crouch=(0.04, 4), feet=((0, 0.06, 0), (0, -0.06, 0)), at=S.head(held) + V(-0.4, -0.6, -0.5))
# 3e: hij bekijkt zijn knokkels (hand voor zijn borst, handrug naar boven)
LOOKH = arm("L", (0.25, 0.55, -0.75), (-0.30, 0.75, 0.55))
S.beat(held, t_e, "staan", arms=LOOKH, face="twijfel", face_amt=0.7, feet=((0, 0.06, 0), (0, -0.06, 0)),
       look=(0.3, -0.7), body={"head": (10, 0, 0)})
S.hold(held, END)
# rode plek op zijn knokkels, trekt weg in 3e
plek = T.sphere("Knokkel_plek", (0, 0, 0), 0.02, S.mat("knokkel_rood", (0.85, 0.2, 0.25), 0.0), scale=(1.4, 1.0, 0.4), seg=12, ol=0)
plek.parent = held.rig
plek.parent_type = "BONE"
plek.parent_bone = "hand.L"
plek.matrix_parent_inverse = Matrix.Identity(4)
plek.location = (0.0, -0.01, 0.03)
for t, s in ((0.0, 0.001), (T_HIT, 0.001), (T_HIT + 0.04, 1.0), (t_e + 0.6, 1.0), (t_e + 1.6, 0.001)):
    key(plek, t, scale=s)

# ---------------------------------------------------------------- camera's
# 3d2 MEDIUM: camera beweegt mee langs de gang (vóór hem, aan de kant van de muren), houdt hem van voren in beeld
def track(t):
    M = S._root_matrix(held, max(0.0, min(t, T_HIT)))
    p = M.translation
    return p + V(-2.0, 0.6, 1.3), p + V(0.0, 0.0, 1.0), 26
S.cam(0.0, None, fn=track)
# 3e (half)close: hij bekijkt zijn knokkels; de rode plek trekt weg
S.cam(t_e, S.shot(held, t_e + 0.8, size=1.15, az=-10, lens=35, h=-0.30), S.shot(held, t_e + 0.8, size=1.0, az=-8, lens=35, h=-0.28))

# ---------------------------------------------------------------- HUD, stem en geluid
S.year(2026, t0=0.0, tick=False)
S.say("D03-05", at=0.2)
S.sfx("sfx_hout_klop", T_HIT, 0.5)
S.sfx("sfx_knokkels", T_HIT + 0.05, 0.35)
S.say("D03-06", at=t_e + 0.15)
S.tick(t_e + 1.9, 0.6)
S.ambience("sfx_binnen_sfeer", 0.0, END, vol=0.08)
S.music("speels", 0.0, t_e + 0.2, vol=0.2, fade_in=0.2, fade_out=0.6)
S.finish(length=END, tail=0.0)
