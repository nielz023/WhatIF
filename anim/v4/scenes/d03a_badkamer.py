"""D03a · De spiegel (script scène 3c, 3d). Badkamer, ochtend.
3c MEDIUM 4,1 s: hij kijkt in de spiegel; de camera is 'de spiegel' (vlak voor het glas, schuin voor hem).
   Hij voelt aan zijn kin, knippert, trekt een gek gezicht.  VO: "Rule three. You never, ever get older."
3d CLOSE 5,1 s: hij grijnst nog, hij weet niet wat er komt.
   VO: "Sounds amazing, right? One more thing. You'll still feel everything."

    python3 anim/v4/scenes/d03a_badkamer.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v4 import *  # noqa: E402,F401,F403

S = Scene4("d03a", "badkamer", "binnen", exposure=0.25)
sh = S.cuts([4.1, 5.1])
END = sh[-1][1]
t_d = sh[1][0]

AT = V(-0.55, -0.05, 0.0)
held = S.actor("hoofdpersonage_kind", AT, 180)          # kijkt naar +y, naar de spiegel
MIRROR = V(-0.55, 1.2, 1.25)
HC = S.headpos(held, 0.0)
CHIN = arm("R", (0.25, 0.70, -0.65), (-0.40, 0.55, 0.75))  # hand onder zijn kin, ~0,4 m voor het hoofdcentrum
S.beat(held, 0.0, "staan", face="neutraal", face_amt=0.4, at=HC + V(0, 1.0, 0.0))
S.beat(held, 0.6, "staan", arms=CHIN, face="twijfel", face_amt=0.6, at=HC + V(0, 1.0, 0.0), body={"head": (-6, 0, 8)})
S.beat(held, 1.5, "staan", arms=CHIN, face="twijfel", face_amt=0.8, at=HC + V(0, 1.0, 0.0), body={"head": (-6, 0, -8)})
A.blink_at(held, F(1.2))
# gek gezicht: wangen bol, ogen scheel-wijd, mond open
S.beat(held, 2.4, "staan", face="schreeuw", face_amt=0.6, at=HC + V(0, 1.0, 0.0), body={"head": (0, 0, 14)},
       ogen_wijd=0.9, mond_grijns=0.5)
S.beat(held, 3.2, "staan", face="lach", face_amt=1.0, at=HC + V(0, 1.0, 0.0), body={"head": (-4, 0, -6)})
# 3d: hij draait iets naar de camera en grijnst breed, wijst nog even naar zichzelf
S.teleport(held, t_d, AT + V(0, 0.35, 0), 0)           # 3d: hij heeft zich omgedraaid en grijnst naar de kijker
S.beat(held, t_d, "staan", face="grijns", face_amt=0.9, at=HC + V(0.2, -1.0, 0.0))
S.beat(held, t_d + 1.4, "schouders_op", amount=0.6, face="zelfverzekerd", face_amt=1.0, at=HC + V(0.2, -1.0, 0.1))
S.beat(held, t_d + 3.0, "staan", face="grijns", face_amt=1.0, at=HC + V(0.1, -1.0, 0.0), body={"head": (-4, 0, 6)})
A.blink_at(held, F(t_d + 2.4))
S.hold(held, END)

# ---------------------------------------------------------------- camera's
H1 = S.headpos(held, 1.5)
# 3c: 'de spiegel' kijkt naar hem (camera vlak voor het glas, iets opzij zodat het niet star frontaal is)
S.cam(0.0, (V(-0.36, 1.12, H1.z + 0.10), H1 + V(0, 0, -0.30), 24), (V(-0.40, 1.10, H1.z + 0.08), H1 + V(0, 0, -0.28), 25))
S.hide("Grote_spiegel")              # het glas zit anders tussen de camera en zijn gezicht
# 3d CLOSE van schuin opzij (tussen wastafel en douche), trage push-in
H2 = S.headpos(held, t_d + 2.0)
S.cam(t_d, S.shot(held, t_d + 2.0, size=1.1, az=15, lens=24), S.shot(held, t_d + 2.0, size=0.95, az=12, lens=24))

# ---------------------------------------------------------------- HUD, stem en geluid
S.year(2026, t0=0.0, tick=False)
S.say("D03-03", at=0.15)
S.say("D03-04", at=t_d + 0.15)
S.ambience("sfx_binnen_sfeer", 0.0, END, vol=0.08)
S.music("speels", 0.0, END, vol=0.2, fade_in=0.2)
S.finish(length=END, tail=0.0)
