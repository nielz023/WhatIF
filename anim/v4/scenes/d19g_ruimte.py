"""D19g · Zweven in de ruimte (script scène 19g-19h). Rode reus, geen aarde meer.
19g  WIDE trage roll 5 s (hier 2 shots): stilte; hij zweeft in de ruimte zonder pak, langzaam draaiend.
     VO: "There's no air out here. You can't breathe. And you still... can't... die."
19h  CLOSE 3 s: zijn mond gaat open alsof hij naar adem hapt. Niets.  VO: "You'll still feel everything. Remember?"

    python3 anim/v4/scenes/d19g_ruimte.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v4 import *  # noqa: E402,F401,F403

S = Scene4("d19g", "ruimte_nd", "rode_reus", exposure=0.1)
sh = S.cuts([3.4, 3.3, 3.0])
END = sh[-1][1]
t_g2, t_h = (s[0] for s in sh[1:])
S.hide("Personage_marker", "Character_marker", "Aarde_silhouet")

HIP = V(0.0, 0.0, 1.0)
held = S.actor("hoofdpersonage_rafels", HIP, 0)
hb = Body(S, held, HIP, 0)
S.qc_skip.add(held.name)
hb.key(0.0, HIP, tilt=-12, roll=-8, yaw=-20)
hb.key(t_h, HIP + V(0, 0, 0.1), tilt=-6, roll=10, yaw=15)
hb.key(END, HIP + V(0, 0, 0.12), tilt=-5, roll=12, yaw=18)
FLOAT = arms(arm("L", (0.75, 0.10, -0.35), (0.80, 0.25, -0.20)), arm("R", (0.75, 0.10, -0.35), (0.80, 0.25, -0.20)))
LEGS = dict(feet=((0.16, 0.10, 0.12), (-0.14, -0.05, 0.05)))
S.beat(held, 0.0, "staan", arms=FLOAT, face="neutraal", face_amt=0.5, look=(0.0, 0.0), **LEGS)
S.beat(held, t_g2, "staan", arms=FLOAT, face="verdrietig", face_amt=0.4, **LEGS)
S.beat(held, t_h + 0.4, "staan", arms=FLOAT, face="bang", face_amt=0.6, mouth=0.9, **LEGS)          # hapt naar adem
S.beat(held, t_h + 1.2, "staan", arms=FLOAT, face="bang", face_amt=0.5, mouth=0.2, **LEGS)
S.beat(held, t_h + 1.8, "staan", arms=FLOAT, face="bang", face_amt=0.6, mouth=0.8, **LEGS)
S.beat(held, t_h + 2.6, "staan", arms=FLOAT, face="verdrietig", face_amt=0.5, mouth=0.1, **LEGS)
S.hold(held, END)
HD = S.headpos(held, t_h + 0.5)

S.cam(0.0, (V(2.5, -4.8, 1.8), V(0, 0, 1.0), 28), (V(2.1, -4.6, 1.5), V(0, 0, 1.05), 28))
S.cam(t_g2, (V(-3.2, -3.4, 0.4), V(0, 0, 1.2), 26), (V(-3.0, -3.2, 0.6), V(0, 0, 1.2), 26))
S.cam(t_h, (HD + V(0.35, -1.3, -0.05), HD, 38), (HD + V(0.3, -1.12, -0.05), HD, 38))

S.no_hud.append((0.0, END))
S.say("D19-04", at=0.25)
S.say("D19-05", at=t_h + 0.3)
S.music("drone", 0.0, END, vol=0.08, fade_in=1.0, fade_out=0.6)
S.finish(length=END, tail=0.0)
