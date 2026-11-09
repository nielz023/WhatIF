"""OR5a · What if you turned invisible? · slaapkamer (ochtend), regel 1-2.

1  hook: je lichaam flikkert: het wordt doorzichtig als glas en komt weer terug.
2  SECOND 1: je houdt je handen voor je gezicht. Ze vervagen, vanaf je vingertoppen.

    python3 anim/shorts/or5a_slaapkamer.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orshort import *  # noqa: E402,F401,F403

S = ORShort("or5", "a", "slaapkamer", "ochtend", lines=(1, 2))
L = S.L
T0, END = S.t0, S.t1
W = lambda n, i: L[n][0] + S.words[f"OR5-{n:02d}"][i]["s"]

P = V(0.2, -0.6, 0)
held = S.actor("hoofdpersonage", P, 20)            # naar de camera (min y), iets gedraaid
HEAD = S.head(held, 0.0)

# hook: van je borst uit even helemaal glas, dan terug
flick = bpy.data.objects.new("Onzichtbaar_flikker", None)
T._link(flick)
attach(flick, held, "chest")
for t, s in ((0.0, 0.001), (0.25, 0.001), (0.55, 2.5), (0.62, 0.001), (0.8, 0.001), (1.0, 2.5), (1.35, 2.5), (1.5, 0.001)):
    key(flick, t, scale=s)
for fc in A._fcurves(flick):
    for kp in fc.keyframe_points:
        kp.interpolation = "LINEAR"
# regel 2: vanaf beide handen, langzaam
r2 = L[2][0]
hl = spreader(S, held, "Onzichtbaar_L", W(2, 3), L[2][1] + 0.2, r1=0.2, bone="hand.L")
hr = spreader(S, held, "Onzichtbaar_R", W(2, 3) + 0.08, L[2][1] + 0.2, r1=0.2, bone="hand.R")
material_spread(held, [("glas", flick), ("glas", hl), ("glas", hr)])
S.sfx("sfx_glitch", 0.5, 0.3)
S.sfx("sfx_glitch", 0.95, 0.3)
S.sfx("sfx_visioen", W(2, 3), 0.3)

S.beat(held, 0.0, "staan", face="verbaasd", face_amt=0.8, look=(0, -0.6), body={"head": (18, 0, 0)})
S.beat(held, 0.6, "schrik", face="geschrokken", face_amt=1.0, look=(0, -0.6), body={"head": (16, 0, 0)})
S.beat(held, L[1][1], "schrik", face="geschrokken", face_amt=0.8, look=(0, 0.0))
# handen voor je gezicht, handpalmen naar je toe
S.reach(held, 0.0, "L", None, 0.0)
S.reach(held, 0.0, "R", None, 0.0)
S.reach(held, r2, "L", None, 0.0)
S.reach(held, r2, "R", None, 0.0)
FRONT = V(math.sin(math.radians(20)), -math.cos(math.radians(20)), 0)       # waar je naartoe kijkt
SIDE = V(-FRONT.y, FRONT.x, 0)
HL = HEAD + FRONT * 0.42 + SIDE * 0.14 + V(0, 0, -0.18)
HR = HEAD + FRONT * 0.42 - SIDE * 0.14 + V(0, 0, -0.18)
S.reach(held, r2 + 0.45, "L", HL)
S.reach(held, r2 + 0.45, "R", HR)
S.reach(held, L[2][1], "L", HL + V(0, 0, 0.03))
S.reach(held, L[2][1], "R", HR + V(0, 0, 0.03))
S.reach(held, END, "L", HL + V(0, 0, 0.04))
S.reach(held, END, "R", HR + V(0, 0, 0.04))
S.beat(held, r2 + 0.45, "staan", face="verbaasd", face_amt=0.8, look=(0, -0.5), body={"head": (16, 0, 0)})
S.beat(held, W(2, 4), "staan", face="geschrokken", face_amt=1.0, look=(0, -0.5), body={"head": (18, 0, 0)})
S.beat(held, END, "staan", face="geschrokken", face_amt=1.0, look=(0, -0.5), body={"head": (18, 0, 0)})

S.counter("SECOND 1", r2, END)
S.music_all("m_spanning_puls", vol=0.22)
S.ambience("sfx_binnen_sfeer", 0.0, END, vol=0.05)

# camera's: hook wijd genoeg om het hele lichaam te zien; regel 2 over je schouder op je handen
S.cam(0.0, ((P.x + 0.8, P.y - 2.6, 1.2), (P.x, P.y, 0.95), 26), ((P.x + 0.7, P.y - 2.3, 1.2), (P.x, P.y, 1.0), 28))
S.cam(r2, ((HEAD.x + 0.35 + FRONT.x * 1.05, HEAD.y + FRONT.y * 1.05, HEAD.z - 0.05), tuple((HL + HR) / 2 * 0.6 + HEAD * 0.4), 26),
      ((HEAD.x + 0.3 + FRONT.x * 0.9, HEAD.y + FRONT.y * 0.9, HEAD.z - 0.05), tuple((HL + HR) / 2 * 0.65 + HEAD * 0.35), 30))
S.done()
