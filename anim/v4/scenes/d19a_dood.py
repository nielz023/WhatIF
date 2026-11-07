"""D19a · Vijf miljard jaar: de rode reus (script scène 19a). Dode aarde, rode zon.
19a  WIDE LOW trage push 4 s: de rode zon vult de lucht, de grond barst open en gloeit.
     VO: "Scientists think the Sun will swell up to two hundred times its size."

    python3 anim/v4/scenes/d19a_dood.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v4 import *  # noqa: E402,F401,F403

S = Scene4("d19a", "heuvel", "dood", exposure=0.1)
sh = S.cuts([4.7])
END = sh[-1][1]
S.hide("Personage_marker", "Character_marker")

SUN = V(0.0, 2600.0, 260.0)
held = S.actor("hoofdpersonage_rafels", (0.0, -1.2, 0.0), 180)
S.beat(held, 0.0, "staan", face="neutraal", face_amt=0.5, at=SUN)
S.beat(held, 2.5, "staan", face="verdrietig", face_amt=0.3, at=SUN)
S.hold(held, END)
for t in frange(0.2, END, 0.6):                            # gloeiende as die opwaait
    S.puff(V(1.5, 2.0, 0.1), t, n=2, r=(0.2, 0.5), grow=1.8, dur=1.4, color=(0.12, 0.10, 0.10), rise=1.5, spread=2.0)

S.cam(0.0, (V(0.8, -6.5, 0.35), V(0, 20, 5), 20), (V(0.7, -5.6, 0.38), V(0, 20, 5.5), 20))

S.year(5000000000, t0=0.0, big=True)
S.jump(0.0)
S.say("D19-01", at=0.2)
S.ambience("sfx_zon_gebrul", 0.0, END, vol=0.12)
S.music("subbas", 0.0, END, vol=0.14, fade_in=0.4, fade_out=0.0)
S.finish(length=END, tail=0.0)
